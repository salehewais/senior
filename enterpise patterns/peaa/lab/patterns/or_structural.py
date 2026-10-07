"""Object-relational structural patterns. أنماط شكل الربط بين الكائن والجدول."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from peaa.lab.lease_app.db import connect, fresh
from peaa.lab.lease_app.money import Money
from peaa.lab.registry import register


@dataclass
class Identified:
    id: int | None


@register("identity_field")
def demo_identity_field() -> None:
    """Primary key stored on the object. المفتاح الأساسي حقل على الكائن."""
    conn = fresh()
    row = conn.execute("SELECT id, status FROM leases WHERE id = 1").fetchone()
    lease = Identified(id=row["id"])
    print("identity_field", lease.id, row["status"])


@dataclass
class CustomerRef:
    id: int
    name: str


@dataclass
class LeaseWithCustomer:
    id: int
    customer: CustomerRef


@register("foreign_key_mapping")
def demo_foreign_key_mapping() -> None:
    conn = fresh()
    row = conn.execute(
        """
        SELECT l.id AS lease_id, c.id AS customer_id, c.name
        FROM leases l JOIN customers c ON c.id = l.customer_id
        WHERE l.id = 1
        """
    ).fetchone()
    lease = LeaseWithCustomer(row["lease_id"], CustomerRef(row["customer_id"], row["name"]))
    print("foreign_key_mapping", lease.id, lease.customer.name)


@register("association_table_mapping")
def demo_association_table() -> None:
    """Many-to-many via a link table. علاقة متعدد-لمتعدد عبر جدول وسيط."""
    conn = fresh()
    conn.executescript(
        """
        CREATE TABLE inspectors (id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE lease_inspectors (
            lease_id INTEGER,
            inspector_id INTEGER,
            PRIMARY KEY (lease_id, inspector_id)
        );
        INSERT INTO inspectors VALUES (1, 'Lina'), (2, 'Omar');
        INSERT INTO lease_inspectors VALUES (1, 1), (1, 2);
        """
    )
    names = conn.execute(
        """
        SELECT i.name FROM lease_inspectors li
        JOIN inspectors i ON i.id = li.inspector_id
        WHERE li.lease_id = 1
        """
    ).fetchall()
    print("association_table_mapping", [r["name"] for r in names])


@dataclass
class Line:
    asset_id: int
    quantity: int


@dataclass
class LeaseGraph:
    id: int
    lines: list[Line] = field(default_factory=list)


@register("dependent_mapping")
def demo_dependent_mapping() -> None:
    """Lines are saved only with their lease. البنود تتحفظ مع الأب."""
    conn = fresh()
    lease = LeaseGraph(1, [Line(1, 1), Line(2, 3)])
    conn.execute("DELETE FROM lease_lines WHERE lease_id = ?", (lease.id,))
    for index, line in enumerate(lease.lines, start=1):
        conn.execute(
            "INSERT INTO lease_lines (id, lease_id, asset_id, quantity) VALUES (?, ?, ?, ?)",
            (index, lease.id, line.asset_id, line.quantity),
        )
    conn.commit()
    qty = conn.execute(
        "SELECT SUM(quantity) AS q FROM lease_lines WHERE lease_id = 1"
    ).fetchone()["q"]
    print("dependent_mapping quantity", qty)


@register("embedded_value")
def demo_embedded_value() -> None:
    """Money is two columns, one value object. المال عمودين وكائن واحد."""
    conn = fresh()
    conn.execute(
        "INSERT INTO invoices (lease_id, amount_cents, currency) VALUES (1, 90000, 'USD')"
    )
    row = conn.execute("SELECT amount_cents, currency FROM invoices").fetchone()
    print("embedded_value", Money(row["amount_cents"], row["currency"]))


@register("serialized_lob")
def demo_serialized_lob() -> None:
    conn = fresh()
    raw = conn.execute("SELECT terms_json FROM leases WHERE id = 1").fetchone()["terms_json"]
    terms = json.loads(raw)
    terms["grace_days"] = 5
    conn.execute("UPDATE leases SET terms_json = ? WHERE id = 1", (json.dumps(terms),))
    conn.commit()
    print("serialized_lob", json.loads(conn.execute("SELECT terms_json FROM leases WHERE id = 1").fetchone()["terms_json"]))


def _sti_load(conn, asset_id: int) -> dict:
    row = conn.execute("SELECT * FROM assets WHERE id = ?", (asset_id,)).fetchone()
    data = {"id": row["id"], "name": row["name"], "kind": row["kind"]}
    if row["kind"] == "truck":
        data["axles"] = row["axle_count"]
    else:
        data["lift_cm"] = row["lift_height_cm"]
    return data


@register("single_table_inheritance")
def demo_sti() -> None:
    conn = fresh()
    print("single_table_inheritance", _sti_load(conn, 1), _sti_load(conn, 2))


@register("class_table_inheritance")
def demo_cti() -> None:
    conn = connect()
    conn.executescript(
        """
        CREATE TABLE asset_base (id INTEGER PRIMARY KEY, name TEXT, kind TEXT);
        CREATE TABLE trucks (id INTEGER PRIMARY KEY, axle_count INTEGER);
        CREATE TABLE forklifts (id INTEGER PRIMARY KEY, lift_height_cm INTEGER);
        INSERT INTO asset_base VALUES (1, 'Flatbed', 'truck');
        INSERT INTO trucks VALUES (1, 3);
        INSERT INTO asset_base VALUES (2, 'Lift', 'forklift');
        INSERT INTO forklifts VALUES (2, 450);
        """
    )
    truck = conn.execute(
        """
        SELECT b.name, t.axle_count FROM asset_base b
        JOIN trucks t ON t.id = b.id WHERE b.id = 1
        """
    ).fetchone()
    print("class_table_inheritance", truck["name"], truck["axle_count"])


@register("concrete_table_inheritance")
def demo_concrete() -> None:
    conn = connect()
    conn.executescript(
        """
        CREATE TABLE truck_assets (
            id INTEGER PRIMARY KEY, name TEXT, monthly_rate_cents INTEGER, axle_count INTEGER
        );
        CREATE TABLE forklift_assets (
            id INTEGER PRIMARY KEY, name TEXT, monthly_rate_cents INTEGER, lift_height_cm INTEGER
        );
        INSERT INTO truck_assets VALUES (1, 'Flatbed', 50000, 3);
        INSERT INTO forklift_assets VALUES (2, 'Lift', 20000, 450);
        """
    )
    trucks = conn.execute("SELECT name, axle_count FROM truck_assets").fetchall()
    print("concrete_table_inheritance", [(r["name"], r["axle_count"]) for r in trucks])


class TruckMapper:
    def load(self, conn, asset_id: int) -> dict:
        row = conn.execute("SELECT * FROM assets WHERE id = ? AND kind = 'truck'", (asset_id,)).fetchone()
        return {"type": "truck", "name": row["name"], "axles": row["axle_count"]}


class ForkliftMapper:
    def load(self, conn, asset_id: int) -> dict:
        row = conn.execute(
            "SELECT * FROM assets WHERE id = ? AND kind = 'forklift'", (asset_id,)
        ).fetchone()
        return {"type": "forklift", "name": row["name"], "lift_cm": row["lift_height_cm"]}


class AssetMapper:
    """Chooses a concrete mapper from the discriminator. يختار المابر حسب النوع."""

    def __init__(self) -> None:
        self._by_kind = {"truck": TruckMapper(), "forklift": ForkliftMapper()}

    def load(self, conn, asset_id: int) -> dict:
        kind = conn.execute("SELECT kind FROM assets WHERE id = ?", (asset_id,)).fetchone()["kind"]
        return self._by_kind[kind].load(conn, asset_id)


@register("inheritance_mappers")
def demo_inheritance_mappers() -> None:
    conn = fresh()
    mapper = AssetMapper()
    print("inheritance_mappers", mapper.load(conn, 1), mapper.load(conn, 2))
