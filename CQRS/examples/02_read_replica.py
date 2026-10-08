#!/usr/bin/env python3
"""
02 — Read Replica
-----------------
Idea: Primary handles writes; replica handles heavy report SELECTs.
Isolation of workload — replica still has the same ~200M rows.
"""

from __future__ import annotations

import copy
import time

from _demo_data import banner, make_lines


class FakeDB:
    def __init__(self, name: str, lines):
        self.name = name
        self.lines = lines
        self.write_count = 0
        self.read_count = 0

    def write(self, line) -> None:
        self.write_count += 1
        self.lines.append(line)

    def sum_balance(self) -> float:
        self.read_count += 1
        # simulate heavy read
        time.sleep(0.02)
        return sum(l.balance for l in self.lines)


def replicate(primary: FakeDB) -> FakeDB:
    """Physical replica ≈ copy of data (same row count)."""
    return FakeDB("replica", copy.deepcopy(primary.lines))


def main() -> None:
    banner("02 Read Replica — reports off primary, same data volume")
    primary = FakeDB("primary", make_lines(5_000))
    replica = replicate(primary)

    # POS write hits primary only
    from _demo_data import MoveLine
    from datetime import date

    primary.write(
        MoveLine(999999, date(2026, 1, 1), 1, 1, 1000, 100.0, 0.0)
    )
    print(f"primary rows={len(primary.lines)} writes={primary.write_count}")
    print(f"replica rows={len(replica.lines)} (lag: new write not applied yet)")

    # Heavy report on replica — primary.read_count stays 0
    bal = replica.sum_balance()
    print(f"report on {replica.name}: balance={bal:,.2f} reads={replica.read_count}")
    print(f"primary reads still={primary.read_count} (POS protected)")
    print("\nTrade-off: protects writes, but a bad SELECT on replica is still heavy.")


if __name__ == "__main__":
    main()
