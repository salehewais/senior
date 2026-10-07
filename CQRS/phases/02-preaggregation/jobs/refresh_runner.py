#!/usr/bin/env python3
"""Run Phase 2 nightly window or incremental refresh against REPLICA_DSN."""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date, timedelta
from pathlib import Path

try:
    import psycopg2
except ImportError:
    print("Install psycopg2-binary", file=sys.stderr)
    sys.exit(1)


def load_env() -> None:
    cfg = Path(__file__).resolve().parents[2] / "shared" / "config.env"
    if not cfg.exists():
        return
    for line in cfg.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


DATASETS = {
    "aml_daily": {
        "nightly_fn": "reporting.refresh_aml_daily_window",
        "incremental_fn": "reporting.refresh_aml_daily_incremental",
        "window_env": "AML_DAILY_WINDOW_DAYS",
        "default_days": 7,
    },
    "sales_daily": {
        "nightly_fn": "reporting.refresh_sales_daily_window",
        "incremental_fn": None,  # add when needed
        "window_env": "SALES_DAILY_WINDOW_DAYS",
        "default_days": 7,
    },
}


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=DATASETS.keys(), required=True)
    parser.add_argument("--mode", choices=("nightly", "incremental"), required=True)
    args = parser.parse_args()

    dsn = os.environ.get("REPLICA_DSN")
    if not dsn:
        print("REPLICA_DSN required", file=sys.stderr)
        sys.exit(1)

    meta = DATASETS[args.dataset]
    with psycopg2.connect(dsn) as conn:
        conn.autocommit = False
        with conn.cursor() as cur:
            if args.mode == "nightly":
                days = int(os.environ.get(meta["window_env"], meta["default_days"]))
                end = date.today() + timedelta(days=1)
                start = end - timedelta(days=days)
                cur.execute(
                    f"SELECT {meta['nightly_fn']}(%s::date, %s::date)",
                    (start, end),
                )
            else:
                fn = meta["incremental_fn"]
                if not fn:
                    print(f"incremental not implemented for {args.dataset}", file=sys.stderr)
                    sys.exit(2)
                cur.execute(f"SELECT {fn}()")
        conn.commit()
    print(f"ok dataset={args.dataset} mode={args.mode}")


if __name__ == "__main__":
    main()
