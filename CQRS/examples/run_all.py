#!/usr/bin/env python3
"""Run every example script in order (01→22)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = sorted(ROOT.glob("[0-9][0-9]_*.py"))


def main() -> int:
    failed = []
    for script in SCRIPTS:
        print(f"\n>>> running {script.name}")
        proc = subprocess.run([sys.executable, str(script)], cwd=ROOT)
        if proc.returncode != 0:
            failed.append(script.name)
    if failed:
        print("FAILED:", ", ".join(failed))
        return 1
    print(f"\nAll {len(SCRIPTS)} examples OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
