"""Run one pattern demo or every demo.

Usage (from the ``enterpise patterns`` directory):

    python -m peaa.lab.run_demo domain_model
    python -m peaa.lab.run_demo --all
"""

from __future__ import annotations

import argparse
import sys

from peaa.lab.registry import DEMOS


def _load() -> None:
    import peaa.lab.concurrency.execution  # noqa: F401
    import peaa.lab.concurrency.resilience  # noqa: F401
    import peaa.lab.concurrency.sync  # noqa: F401
    import peaa.lab.concurrency.workers  # noqa: F401
    import peaa.lab.lease_app.story  # noqa: F401
    import peaa.lab.patterns.base_patterns  # noqa: F401
    import peaa.lab.patterns.data_source  # noqa: F401
    import peaa.lab.patterns.distribution  # noqa: F401
    import peaa.lab.patterns.domain_logic  # noqa: F401
    import peaa.lab.patterns.offline_concurrency  # noqa: F401
    import peaa.lab.patterns.or_behavioral  # noqa: F401
    import peaa.lab.patterns.or_metadata  # noqa: F401
    import peaa.lab.patterns.or_structural  # noqa: F401
    import peaa.lab.patterns.session_state  # noqa: F401
    import peaa.lab.patterns.web_presentation  # noqa: F401


def main(argv: list[str] | None = None) -> int:
    _load()
    parser = argparse.ArgumentParser(description="Run a PEAA or concurrency lab")
    parser.add_argument("name", nargs="?", help="demo name")
    parser.add_argument("--all", action="store_true", help="run every demo")
    parser.add_argument("--list", action="store_true", help="list demo names")
    args = parser.parse_args(argv)
    if args.list:
        for name in sorted(DEMOS):
            print(name)
        return 0
    if args.all:
        failed = 0
        for name in sorted(DEMOS):
            try:
                print(f"--- {name}")
                DEMOS[name]()
            except Exception as exc:  # noqa: BLE001 — report and continue
                failed += 1
                print(f"FAIL {name}: {exc}", file=sys.stderr)
        print(f"ran {len(DEMOS)} demos, failed {failed}")
        return 1 if failed else 0
    if not args.name:
        parser.error("pass a demo name, --list, or --all")
    try:
        DEMOS[args.name]()
    except KeyError:
        print(f"unknown demo {args.name}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
