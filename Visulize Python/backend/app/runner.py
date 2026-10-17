"""Run the tracer in a child process. This module never executes user code."""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
MAX_STEPS = 300
TIMEOUT_SEC = 2.0
MAX_CODE_CHARS = 100_000


def _parse_stdout(out: bytes) -> dict[str, Any] | None:
    text = out.decode(errors="replace").strip()
    if not text:
        return None
    line = text.splitlines()[-1]
    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict) or "steps" not in data:
        return None
    return data


def _kill(proc: subprocess.Popen) -> None:
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        proc.kill()
    try:
        proc.wait(timeout=1)
    except subprocess.TimeoutExpired:
        proc.kill()


def run_trace(
    code: str,
    stdin: str = "",
    *,
    max_steps: int = MAX_STEPS,
    timeout: float = TIMEOUT_SEC,
) -> dict[str, Any]:
    if len(code) > MAX_CODE_CHARS:
        return {
            "steps": [],
            "stopped": None,
            "error": {
                "type": "ValueError",
                "message": "Code is too long to visualize",
                "line": None,
            },
        }

    fd, path = tempfile.mkstemp(suffix=".py", prefix="viz-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(code)
        child_timeout = max(0.2, timeout - 0.3)
        proc = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "app.tracer",
                path,
                str(max_steps),
                str(child_timeout),
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(BACKEND_ROOT),
            start_new_session=True,
        )
        try:
            out, err = proc.communicate(stdin.encode(), timeout=timeout)
        except subprocess.TimeoutExpired:
            _kill(proc)
            out, err = proc.communicate()
            parsed = _parse_stdout(out)
            if parsed is not None:
                parsed["stopped"] = parsed.get("stopped") or "timeout"
                return parsed
            return {"steps": [], "stopped": "timeout", "error": None}

        parsed = _parse_stdout(out)
        if parsed is None:
            message = err.decode(errors="replace").strip() or "The tracer produced no result"
            return {
                "steps": [],
                "stopped": None,
                "error": {
                    "type": "RuntimeError",
                    "message": message[-1500:],
                    "line": None,
                },
            }
        return parsed
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass
