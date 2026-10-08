#!/usr/bin/env python3
"""
15 — Archiving
--------------
Move cold history out of the hot working set. In accounting this is NOT
`DELETE FROM account_move_line` — keep legal/audit/ZATCA reconstructibility.
"""

from __future__ import annotations

from _demo_data import banner, make_lines


def main() -> None:
    banner("15 Archiving — hot vs cold (never naive DELETE on AML)")
    lines = make_lines(20_000)
    hot_years = {2025, 2026}
    hot = [l for l in lines if l.move_date.year in hot_years]
    cold = [l for l in lines if l.move_date.year not in hot_years]

    # Cold storage keeps data — we do not destroy it
    archive = {"storage": "cold_s3_or_archive_db", "rows": cold}

    print(f"total rows: {len(lines):,}")
    print(f"hot transactional set ({hot_years}): {len(hot):,}")
    print(f"archived historical rows: {len(archive['rows']):,} in {archive['storage']}")
    print("Exact reports for old years read archive/reporting history — not DELETED.")
    print("\nTrade-off: legal retention first; Odoo dependencies make AML deletes dangerous.")


if __name__ == "__main__":
    main()
