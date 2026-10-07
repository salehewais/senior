"""Distribution patterns. واجهة بعيدة وكائن نقل بيانات."""

from __future__ import annotations

from dataclasses import dataclass

from peaa.lab.lease_app.db import fresh
from peaa.lab.lease_app.money import Money
from peaa.lab.patterns.domain_logic import load_domain_lease
from peaa.lab.registry import register


@dataclass(frozen=True)
class LeaseSummary:
    lease_id: int
    status: str
    amount_cents: int
    currency: str


class RemoteLeaseFacade:
    """One coarse call instead of many fine-grained remote calls."""

    def __init__(self, conn) -> None:
        self.conn = conn

    def bill_and_summarize(self, lease_id: int) -> LeaseSummary:
        total = load_domain_lease(self.conn, lease_id).monthly_total()
        row = self.conn.execute("SELECT status FROM leases WHERE id = ?", (lease_id,)).fetchone()
        self.conn.execute(
            "INSERT INTO invoices (lease_id, amount_cents, currency) VALUES (?, ?, ?)",
            (lease_id, total.cents, total.currency),
        )
        self.conn.commit()
        return LeaseSummary(lease_id, row["status"], total.cents, total.currency)


@register("remote_facade")
def demo_remote_facade() -> None:
    summary = RemoteLeaseFacade(fresh()).bill_and_summarize(1)
    print("remote_facade", summary)


@register("dto")
def demo_dto() -> None:
    """A flat object for the wire, not the domain graph. كائن مسطّح للنقل."""
    conn = fresh()
    total: Money = load_domain_lease(conn, 1).monthly_total()
    dto = LeaseSummary(1, "active", total.cents, total.currency)
    print("dto", dto)
