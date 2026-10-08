#!/usr/bin/env python3
"""
11 — CQRS (Command Query Responsibility Segregation)
----------------------------------------------------
Commands mutate the write model; queries read a separate read model.
CQRS alone is not performance magic — it enables specialized read paths.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from _demo_data import banner


@dataclass
class WriteModel:
    """Odoo-like transactional store."""

    lines: list[dict] = field(default_factory=list)

    def handle_post_invoice(self, invoice_id: int, branch_id: int, amount: float) -> dict:
        line = {
            "invoice_id": invoice_id,
            "branch_id": branch_id,
            "amount": amount,
            "state": "posted",
        }
        self.lines.append(line)
        return line  # command result


@dataclass
class ReadModel:
    branch_totals: dict[int, float] = field(default_factory=dict)

    def project(self, line: dict) -> None:
        b = line["branch_id"]
        self.branch_totals[b] = self.branch_totals.get(b, 0.0) + line["amount"]

    def query_branch_kpi(self, branch_id: int) -> float:
        return self.branch_totals.get(branch_id, 0.0)


class App:
    def __init__(self) -> None:
        self.write = WriteModel()
        self.read = ReadModel()

    def command_post_invoice(self, invoice_id: int, branch_id: int, amount: float) -> None:
        line = self.write.handle_post_invoice(invoice_id, branch_id, amount)
        # naive sync projection (events come in example 12+)
        self.read.project(line)

    def query_kpi(self, branch_id: int) -> float:
        return self.read.query_branch_kpi(branch_id)


def main() -> None:
    banner("11 CQRS — commands write, queries read a different model")
    app = App()
    app.command_post_invoice(1001, branch_id=1, amount=500)
    app.command_post_invoice(1002, branch_id=1, amount=250)
    app.command_post_invoice(1003, branch_id=2, amount=800)

    print(f"write model lines: {len(app.write.lines)}")
    print(f"query KPI branch 1 (read model): {app.query_kpi(1):,.2f}")
    print(f"query KPI branch 2 (read model): {app.query_kpi(2):,.2f}")
    print("\nTrade-off: extra model to maintain; performance needs aggregation/replica too.")


if __name__ == "__main__":
    main()
