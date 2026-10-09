"""Trace one Python function and record call / return events.

The starting call names the function to follow, for example ``fib(5)`` or
``subset_sum(0, 5)``. Functions defined inside that function are followed too,
so a nested recursive helper shows up in the tree. Other calls, including the
standard library and helpers defined beside it, are ignored. The user source
runs in a short-lived subprocess with a timeout and a cap on how many calls
are recorded. When debug is requested, each executed line of a followed
function is recorded too, with a snapshot of its local variables.
"""

from __future__ import annotations

import ast
import inspect
import io
import json
import os
import select
import subprocess
import sys
import threading
import time
import traceback
import types
from pathlib import Path
from typing import Any

MAX_CALLS = 400
MAX_LINES = 2500
TIMEOUT_SECONDS = 2.0
_WORKER = Path(__file__).resolve()


class _CallLimit(BaseException):
    """Stops user code once the recorded-call cap is hit.

    This inherits from BaseException so a function that catches Exception
    cannot swallow the cap and keep recursing.
    """


def run_trace(source: str, call: str, debug: bool = False) -> dict[str, Any]:
    """Validate ``call``, run ``source`` in a subprocess, and return events."""
    try:
        target = function_name(call)
    except ValueError as exc:
        return _empty(error=str(exc))

    if len(source) > 100_000:
        return _empty(error="The source is too long.", target=target)
    if not source.strip():
        return _empty(error="The editor is empty.", target=target)
    try:
        compile(source, "<user>", "exec")
    except SyntaxError as exc:
        line = exc.lineno or 1
        return _empty(error=f"Syntax error on line {line}: {exc.msg}.", target=target)

    return _run_subprocess(source, call.strip(), target, debug)


def function_name(call: str) -> str:
    """Return the function name from a simple call, or raise ValueError."""
    text = call.strip()
    if not text:
        raise ValueError("Enter a starting call, such as fib(5).")
    try:
        tree = ast.parse(text, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"The starting call could not be parsed: {exc.msg}.") from exc

    node = tree.body
    if not isinstance(node, ast.Call):
        raise ValueError("The starting call has to be a function call, such as fib(5).")
    if not isinstance(node.func, ast.Name):
        raise ValueError("The starting call has to name a function directly, such as fib(5).")
    if any(isinstance(arg, ast.Starred) for arg in node.args):
        raise ValueError(
            "Arguments in the starting call have to be literals or names, such as fib(5) or knapsack(0, 12)."
        )
    for arg in node.args:
        _validate_expr(arg)
    for keyword in node.keywords:
        if keyword.arg is None:
            raise ValueError(
                "Arguments in the starting call have to be literals or names, such as fib(5) or knapsack(0, 12)."
            )
        _validate_expr(keyword.value)
    return node.func.id


def _validate_expr(node: ast.AST) -> None:
    if isinstance(node, ast.Constant):
        return
    if isinstance(node, ast.Name):
        return
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub, ast.Not)):
        _validate_expr(node.operand)
        return
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        for elt in node.elts:
            if isinstance(elt, ast.Starred):
                break
            _validate_expr(elt)
        else:
            return
    if isinstance(node, ast.Dict):
        for key, value in zip(node.keys, node.values):
            if key is None:
                break
            _validate_expr(key)
            _validate_expr(value)
        else:
            return
    raise ValueError(
        "Arguments in the starting call have to be literals or names, such as fib(5) or knapsack(0, 12)."
    )


def _empty(*, error: str | None, target: str | None = None, timed_out: bool = False) -> dict[str, Any]:
    return {
        "events": [],
        "result": None,
        "error": error,
        "truncated": False,
        "timed_out": timed_out,
        "target": target,
    }


def _run_subprocess(source: str, call: str, target: str, debug: bool = False) -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"
    payload = json.dumps(
        {
            "source": source,
            "call": call,
            "max_calls": MAX_CALLS,
            "max_lines": MAX_LINES,
            "debug": bool(debug),
        }
    ).encode("utf-8")

    proc = subprocess.Popen(
        [sys.executable, "-u", str(_WORKER)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        bufsize=0,
    )
    assert proc.stdin is not None and proc.stdout is not None and proc.stderr is not None
    proc.stdin.write(payload)
    proc.stdin.close()

    stderr_parts: list[bytes] = []

    def _drain_stderr() -> None:
        stderr_parts.append(proc.stderr.read())

    drain = threading.Thread(target=_drain_stderr, daemon=True)
    drain.start()

    events: list[dict[str, Any]] = []
    done: dict[str, Any] | None = None
    timed_out = False
    deadline = time.monotonic() + TIMEOUT_SECONDS
    fd = proc.stdout.fileno()
    os.set_blocking(fd, False)
    pending = b""

    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            timed_out = True
            break
        if proc.poll() is not None:
            # The process exited. Read whatever is left, without waiting past the deadline.
            readable, _, _ = select.select([fd], [], [], min(remaining, 0.05))
            if not readable:
                break
        else:
            readable, _, _ = select.select([fd], [], [], min(remaining, 0.2))
            if not readable:
                continue
        try:
            chunk = os.read(fd, 65536)
        except BlockingIOError:
            continue
        if not chunk:
            break
        pending += chunk
        while b"\n" in pending:
            line, pending = pending.split(b"\n", 1)
            message = _decode_message(line)
            if message is None:
                continue
            if message.get("type") == "event":
                event = message.get("event")
                if isinstance(event, dict):
                    events.append(event)
            elif message.get("type") == "done":
                done = message

    if timed_out or proc.poll() is None and done is None:
        # A finished process has poll() != None. Kill only if it is still going
        # or the deadline passed before a done message.
        if proc.poll() is None:
            timed_out = True
            proc.kill()

    try:
        proc.wait(timeout=1)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=1)
    drain.join(timeout=1)

    stderr = b"".join(stderr_parts).decode("utf-8", errors="replace").strip()
    if done is None:
        error = None
        if not timed_out:
            error = "The run ended before it finished."
            if stderr:
                tail = stderr[-500:]
                error = f"{error} {tail}"
        return {
            "events": events,
            "result": None,
            "error": error,
            "truncated": False,
            "timed_out": timed_out,
            "target": target,
        }

    return {
        "events": events,
        "result": done.get("result"),
        "error": done.get("error"),
        "truncated": bool(done.get("truncated")),
        "timed_out": False,
        "target": target,
    }


def _decode_message(line: bytes) -> dict[str, Any] | None:
    text = line.decode("utf-8", errors="replace").strip()
    if not text:
        return None
    try:
        message = json.loads(text)
    except json.JSONDecodeError:
        return None
    if isinstance(message, dict):
        return message
    return None


def _worker_main() -> None:
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8"))
        source = payload["source"]
        call = payload["call"]
        max_calls = int(payload.get("max_calls", MAX_CALLS))
        max_lines = int(payload.get("max_lines", MAX_LINES))
        debug = bool(payload.get("debug", False))
    except Exception as exc:  # noqa: BLE001 - report any bad payload to the parent
        _emit({"type": "done", "result": None, "error": f"Bad request: {exc}", "truncated": False})
        return
    try:
        _execute(source, call, max_calls, debug, max_lines)
    except Exception:
        traceback.print_exc(file=sys.__stderr__)
        _emit({"type": "done", "result": None, "error": "The tracer crashed.", "truncated": False})


def _execute(source: str, call: str, max_calls: int, debug: bool = False, max_lines: int = MAX_LINES) -> None:
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()

    try:
        target = function_name(call)
    except ValueError as exc:
        _emit({"type": "done", "result": None, "error": str(exc), "truncated": False})
        return

    namespace: dict[str, Any] = {"__name__": "__main__"}
    try:
        exec(compile(source, "<user>", "exec"), namespace)
    except SyntaxError as exc:
        line = exc.lineno or 1
        _emit(
            {
                "type": "done",
                "result": None,
                "error": f"Syntax error on line {line}: {exc.msg}.",
                "truncated": False,
            }
        )
        return
    except Exception as exc:
        _emit(
            {
                "type": "done",
                "result": None,
                "error": _format_exc(exc),
                "truncated": False,
            }
        )
        return

    func = namespace.get(target)
    code = getattr(func, "__code__", None)
    if not callable(func) or code is None or getattr(code, "co_filename", None) != "<user>":
        if func is None:
            message = f"{target} is not defined in this file."
        elif not callable(func):
            message = f"{target} is not a function."
        else:
            message = f"{target} is not a Python function defined in this file."
        _emit({"type": "done", "result": None, "error": message, "truncated": False})
        return

    open_ids: list[int] = []
    next_id = 1
    call_count = 0
    line_count = 0
    truncated = False
    error: str | None = None
    result: Any = None
    last_lines: dict[int, int] = {}

    def tracer(frame: types.FrameType, event: str, arg: object):  # noqa: ANN202
        nonlocal next_id, call_count, line_count, truncated
        if event != "call" or not _follows(frame.f_code, code):
            return None

        func_name = frame.f_code.co_name
        state: dict[str, Any] = {"id": None, "raising": False, "locals": {}}

        def local(fr: types.FrameType, ev: str, value: object):  # noqa: ANN202
            nonlocal next_id, call_count, line_count, truncated
            if state["id"] is None and ev in ("line", "return"):
                if call_count >= max_calls:
                    truncated = True
                    raise _CallLimit()
                call_count += 1
                node_id = next_id
                next_id += 1
                state["id"] = node_id
                parent = open_ids[-1] if open_ids else None
                try:
                    args = _format_args(fr)
                except Exception:
                    args = ["?"]
                open_ids.append(node_id)
                call_event: dict[str, Any] = {
                    "type": "call",
                    "id": node_id,
                    "parent": parent,
                    "name": func_name,
                    "args": args,
                    "depth": len(open_ids) - 1,
                }
                if debug:
                    call_event["line"] = fr.f_lineno
                    last_lines[node_id] = fr.f_lineno
                _emit({"type": "event", "event": call_event})
            # A propagating exception still produces a return event whose
            # value is None. An exception that the function catches is
            # followed by another line, so the flag is cleared first.
            if ev == "exception":
                state["raising"] = True
            elif ev == "line":
                state["raising"] = False
                if debug and state["id"] is not None:
                    if line_count >= max_lines:
                        truncated = True
                        raise _CallLimit()
                    line_count += 1
                    node_id = int(state["id"])
                    lineno = fr.f_lineno
                    last_lines[node_id] = lineno
                    snapshot = _snapshot_locals(fr)
                    previous = state["locals"]
                    changed = [name for name, text in snapshot.items() if previous.get(name) != text]
                    state["locals"] = snapshot
                    _emit(
                        {
                            "type": "event",
                            "event": {
                                "type": "line",
                                "id": node_id,
                                "line": lineno,
                                "locals": snapshot,
                                "changed": changed,
                            },
                        }
                    )
            elif ev == "return" and state["id"] is not None:
                node_id = int(state["id"])
                if open_ids and open_ids[-1] == node_id:
                    open_ids.pop()
                failed = bool(state["raising"])
                return_event: dict[str, Any] = {
                    "type": "return",
                    "id": node_id,
                    "value": "raised" if failed else _safe_repr(value),
                    "error": failed,
                }
                if debug:
                    return_event["line"] = fr.f_lineno
                    last_lines[node_id] = fr.f_lineno
                _emit({"type": "event", "event": return_event})
            return local

        return local

    try:
        call_code = compile(call, "<call>", "eval")
    except SyntaxError as exc:
        _emit(
            {
                "type": "done",
                "result": None,
                "error": f"The starting call could not be parsed: {exc.msg}.",
                "truncated": False,
            }
        )
        return

    sys.settrace(tracer)
    try:
        result = eval(call_code, namespace)
    except _CallLimit:
        truncated = True
    except Exception as exc:
        error = _format_exc(exc)
    except BaseException as exc:
        error = _format_exc(exc)
    finally:
        sys.settrace(None)

    if error:
        while open_ids:
            node_id = open_ids.pop()
            return_event = {
                "type": "return",
                "id": node_id,
                "value": "raised",
                "error": True,
            }
            if debug and node_id in last_lines:
                return_event["line"] = last_lines[node_id]
            _emit({"type": "event", "event": return_event})

    _emit(
        {
            "type": "done",
            "result": None if error or truncated else _safe_repr(result),
            "error": error,
            "truncated": truncated,
        }
    )


def _follows(frame_code: types.CodeType, target_code: types.CodeType) -> bool:
    """True for the called function and functions defined inside it."""
    if frame_code is target_code:
        return True
    if getattr(frame_code, "co_filename", None) != "<user>":
        return False
    qualname = getattr(frame_code, "co_qualname", "")
    prefix = getattr(target_code, "co_qualname", target_code.co_name) + ".<locals>."
    return qualname.startswith(prefix)


def _snapshot_locals(frame: types.FrameType) -> dict[str, str]:
    loc = frame.f_locals
    names = list(frame.f_code.co_varnames)
    for name in loc:
        if name not in names:
            names.append(name)
    snapshot: dict[str, str] = {}
    for name in names:
        if name not in loc or _is_user_function(loc[name]):
            continue
        snapshot[name] = _safe_repr(loc[name])
    return snapshot


def _is_user_function(value: object) -> bool:
    code = getattr(value, "__code__", None)
    return getattr(code, "co_filename", None) == "<user>"


def _format_args(frame: types.FrameType) -> list[str]:
    code = frame.f_code
    loc = frame.f_locals
    parts: list[str] = []
    for name in code.co_varnames[: code.co_argcount]:
        parts.append(_safe_repr(loc[name]) if name in loc else "?")
    kw_end = code.co_argcount + code.co_kwonlyargcount
    for name in code.co_varnames[code.co_argcount : kw_end]:
        if name in loc:
            parts.append(f"{name}={_safe_repr(loc[name])}")
    index = kw_end
    if code.co_flags & inspect.CO_VARARGS:
        for item in loc.get(code.co_varnames[index], ()):
            parts.append(_safe_repr(item))
        index += 1
    if code.co_flags & inspect.CO_VARKEYWORDS:
        mapping = loc.get(code.co_varnames[index], {})
        if isinstance(mapping, dict):
            for key, value in mapping.items():
                parts.append(f"{key}={_safe_repr(value)}")
    return parts


def _safe_repr(value: object, limit: int = 80) -> str:
    try:
        text = repr(value)
    except Exception:
        return "<unrepresentable>"
    if len(text) > limit:
        return text[: limit - 1] + "…"
    return text


def _format_exc(exc: BaseException) -> str:
    text = f"{type(exc).__name__}: {exc}"
    if len(text) > 400:
        return text[:399] + "…"
    return text


def _emit(message: dict[str, Any]) -> None:
    sys.__stdout__.write(json.dumps(message, ensure_ascii=False) + "\n")
    sys.__stdout__.flush()


if __name__ == "__main__":
    _worker_main()
