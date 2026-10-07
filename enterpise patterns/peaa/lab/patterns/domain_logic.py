"""Domain logic patterns. أنماط منطق النطاق على نفس عقد التأجير."""

from __future__ import annotations

from dataclasses import dataclass, field

from peaa.lab.lease_app.db import fresh
from peaa.lab.lease_app.money import Money
from peaa.lab.registry import register


def _lines(conn, lease_id: int):
    return conn.execute(
        """
        SELECT a.name, a.monthly_rate_cents, a.currency, l.quantity
        FROM lease_lines l
        JOIN assets a ON a.id = l.asset_id
        WHERE l.lease_id = ?
        """,
        (lease_id,),
    ).fetchall()


@register("transaction_script")
def demo_transaction_script() -> None:
    """One procedure bills a lease. إجراء واحد يحسب الفاتورة ويحفظها."""
    conn = fresh()
    total = 0
    currency = "USD"
    for row in _lines(conn, 1):
        total += row["monthly_rate_cents"] * row["quantity"]
        currency = row["currency"]
    conn.execute(
        "INSERT INTO invoices (lease_id, amount_cents, currency) VALUES (1, ?, ?)",
        (total, currency),
    )
    conn.commit()
    print("transaction_script", Money(total, currency))


@dataclass
class Asset:
    name: str
    monthly_rate: Money


@dataclass
class LeaseLine:
    asset: Asset
    quantity: int

    def charge(self) -> Money:
        return self.asset.monthly_rate * self.quantity


@dataclass
class Lease:
    lines: list[LeaseLine] = field(default_factory=list)

    def monthly_total(self) -> Money:
        total = Money(0)
        for line in self.lines:
            total += line.charge()
        return total


def load_domain_lease(conn, lease_id: int) -> Lease:
    lease = Lease()
    for row in _lines(conn, lease_id):
        lease.lines.append(
            LeaseLine(
                Asset(row["name"], Money(row["monthly_rate_cents"], row["currency"])),
                row["quantity"],
            )
        )
    return lease


@register("domain_model")
def demo_domain_model() -> None:
    """Rules live on Lease, not in the query. القواعد على الكائن."""
    conn = fresh()
    lease = load_domain_lease(conn, 1)
    print("domain_model", lease.monthly_total())


class LeaseTable:
    """Table Module: one class, many rows. كلاس واحد يشتغل على مجموعة صفوف."""

    def __init__(self, rows: list[dict]) -> None:
        self.rows = rows

    def monthly_total(self) -> Money:
        cents = sum(r["monthly_rate_cents"] * r["quantity"] for r in self.rows)
        return Money(cents)


@register("table_module")
def demo_table_module() -> None:
    conn = fresh()
    rows = [dict(r) for r in _lines(conn, 1)]
    print("table_module", LeaseTable(rows).monthly_total())


class BillingService:
    """Application service around the domain model. خدمة تطبيق تنسّق الفوترة."""

    def __init__(self, conn) -> None:
        self.conn = conn

    def bill(self, lease_id: int) -> Money:
        total = load_domain_lease(self.conn, lease_id).monthly_total()
        self.conn.execute(
            "INSERT INTO invoices (lease_id, amount_cents, currency) VALUES (?, ?, ?)",
            (lease_id, total.cents, total.currency),
        )
        self.conn.commit()
        return total


@register("service_layer")
def demo_service_layer() -> None:
    conn = fresh()
    print("service_layer", BillingService(conn).bill(1))
