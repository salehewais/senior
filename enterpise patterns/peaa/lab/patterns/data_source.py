"""Data-source architectural patterns. أنماط مصدر البيانات."""

from __future__ import annotations

from dataclasses import dataclass

from peaa.lab.lease_app.db import fresh
from peaa.lab.lease_app.money import Money
from peaa.lab.registry import register


class LeaseTableGateway:
    """SQL for the leases table lives here only. كل SQL للجدول في بوابة واحدة."""

    def __init__(self, conn) -> None:
        self.conn = conn

    def find(self, lease_id: int):
        return self.conn.execute("SELECT * FROM leases WHERE id = ?", (lease_id,)).fetchone()

    def set_status(self, lease_id: int, status: str) -> None:
        self.conn.execute("UPDATE leases SET status = ? WHERE id = ?", (status, lease_id))
        self.conn.commit()


@register("table_data_gateway")
def demo_table_data_gateway() -> None:
    conn = fresh()
    gateway = LeaseTableGateway(conn)
    gateway.set_status(1, "billed")
    print("table_data_gateway", gateway.find(1)["status"])


class LeaseRow:
    """One instance per row. كائن لكل صف ويعرف يحدّث نفسه."""

    def __init__(self, conn, row) -> None:
        self.conn = conn
        self.id = row["id"]
        self.status = row["status"]

    def update(self) -> None:
        self.conn.execute("UPDATE leases SET status = ? WHERE id = ?", (self.status, self.id))
        self.conn.commit()


@register("row_data_gateway")
def demo_row_data_gateway() -> None:
    conn = fresh()
    row = LeaseRow(conn, conn.execute("SELECT * FROM leases WHERE id = 1").fetchone())
    row.status = "returned"
    row.update()
    print("row_data_gateway", row.status)


@dataclass
class ActiveLease:
    """Domain object that also saves itself. كائن نطاق يحفظ نفسه."""

    conn: object
    id: int
    customer_id: int
    status: str

    def monthly_total(self) -> Money:
        rows = self.conn.execute(
            """
            SELECT a.monthly_rate_cents, l.quantity
            FROM lease_lines l JOIN assets a ON a.id = l.asset_id
            WHERE l.lease_id = ?
            """,
            (self.id,),
        )
        return Money(sum(r["monthly_rate_cents"] * r["quantity"] for r in rows))

    def save(self) -> None:
        self.conn.execute("UPDATE leases SET status = ? WHERE id = ?", (self.status, self.id))
        self.conn.commit()


@register("active_record")
def demo_active_record() -> None:
    conn = fresh()
    raw = conn.execute("SELECT * FROM leases WHERE id = 1").fetchone()
    lease = ActiveLease(conn, raw["id"], raw["customer_id"], raw["status"])
    lease.status = "active"
    lease.save()
    print("active_record", lease.monthly_total(), lease.status)


@dataclass
class DomainLease:
    id: int
    customer_id: int
    status: str

    def can_bill(self) -> bool:
        return self.status == "active"


class LeaseMapper:
    """Maps rows to a domain object that knows nothing about SQL."""

    def __init__(self, conn) -> None:
        self.conn = conn

    def find(self, lease_id: int) -> DomainLease:
        row = self.conn.execute("SELECT * FROM leases WHERE id = ?", (lease_id,)).fetchone()
        return DomainLease(row["id"], row["customer_id"], row["status"])

    def update(self, lease: DomainLease) -> None:
        self.conn.execute(
            "UPDATE leases SET status = ?, customer_id = ? WHERE id = ?",
            (lease.status, lease.customer_id, lease.id),
        )
        self.conn.commit()


@register("data_mapper")
def demo_data_mapper() -> None:
    conn = fresh()
    mapper = LeaseMapper(conn)
    lease = mapper.find(1)
    print("data_mapper loaded", lease.can_bill(), type(lease).__name__)
    lease.status = "closed"
    mapper.update(lease)
    print("data_mapper saved", mapper.find(1).status)
