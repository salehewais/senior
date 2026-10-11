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
import dis
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
    last_locals: dict[int, dict[str, str]] = {}
    arg_index = _ArgIndex(source, call)

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
                params = _entry_params(fr)
                frame_locals = _snapshot_locals(fr)
                caller_locals = _caller_snapshot(fr)
                open_ids.append(node_id)
                last_locals[node_id] = frame_locals
                if parent is not None:
                    last_locals[parent] = caller_locals
                call_event: dict[str, Any] = {
                    "type": "call",
                    "id": node_id,
                    "parent": parent,
                    "name": func_name,
                    "args": args,
                    "depth": len(open_ids) - 1,
                    "params": params,
                    "argExprs": arg_index.exprs_for(fr),
                    "locals": frame_locals,
                    "callerLocals": caller_locals,
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
                    last_locals[node_id] = snapshot
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
                frame_locals = _snapshot_locals(fr)
                caller_locals = _caller_snapshot(fr)
                last_locals[node_id] = frame_locals
                parent = open_ids[-1] if open_ids else None
                if parent is not None:
                    last_locals[parent] = caller_locals
                return_event: dict[str, Any] = {
                    "type": "return",
                    "id": node_id,
                    "value": "raised" if failed else _safe_repr(value),
                    "error": failed,
                    "locals": frame_locals,
                    "callerLocals": caller_locals,
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
            parent = open_ids[-1] if open_ids else None
            return_event = {
                "type": "return",
                "id": node_id,
                "value": "raised",
                "error": True,
                "locals": last_locals.get(node_id, {}),
                "callerLocals": last_locals.get(parent, {}) if parent is not None else {},
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


_CALL_OPS = {"CALL", "CALL_FUNCTION", "CALL_FUNCTION_KW", "CALL_FUNCTION_EX", "CALL_KW"}


class _ArgIndex:
    """Call nodes from one run, used to recover argument source text.

    The starting call is parsed too, but its text lives outside the editor,
    so those expressions stay empty.
    """

    def __init__(self, source: str, call: str) -> None:
        self.source = source
        self.calls = _call_nodes(source)
        try:
            ast.parse(call, filename="<call>", mode="eval")
        except SyntaxError:
            pass
        self._instructions: dict[int, list[dis.Instruction]] = {}

    def exprs_for(self, frame: types.FrameType) -> list[str]:
        names = _param_names(frame.f_code)
        empty = [""] * len(names)
        caller = frame.f_back
        if caller is None or getattr(caller.f_code, "co_filename", None) != "<user>":
            return empty
        node = self._match_call(caller)
        if node is None:
            return empty
        try:
            return _align_arg_exprs(frame.f_code, node, self.source)
        except Exception:
            return empty

    def _match_call(self, caller: types.FrameType) -> ast.Call | None:
        position = self._call_position(caller)
        if position is None:
            return None
        lineno, col, end_lineno, end_col = position
        matches = [
            node
            for node in self.calls
            if _span_contains(node, lineno, col, end_lineno, end_col)
        ]
        if not matches:
            return None
        matches.sort(key=_span_area)
        if len(matches) > 1 and _span_area(matches[0]) == _span_area(matches[1]):
            return None
        return matches[0]

    def _call_position(
        self, caller: types.FrameType
    ) -> tuple[int, int, int, int] | None:
        # f_lasti sits just past the CALL, often inside its inline cache.
        # The latest CALL at or before that offset is the one that entered us,
        # which separates fib(n - 1) from fib(n - 2) on the same line.
        code = caller.f_code
        cached = self._instructions.get(id(code))
        if cached is None:
            cached = [inst for inst in dis.get_instructions(code) if inst.opname in _CALL_OPS]
            self._instructions[id(code)] = cached
        chosen: dis.Instruction | None = None
        for inst in cached:
            if inst.offset <= caller.f_lasti:
                chosen = inst
            else:
                break
        if chosen is None or chosen.positions is None:
            return None
        pos = chosen.positions
        lineno, col = pos.lineno, pos.col_offset
        end_lineno, end_col = pos.end_lineno, pos.end_col_offset
        if lineno is None or col is None or end_lineno is None or end_col is None:
            return None
        return (lineno, col, end_lineno, end_col)


def _call_nodes(source: str) -> list[ast.Call]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    return [node for node in ast.walk(tree) if isinstance(node, ast.Call)]


def _span_contains(
    node: ast.AST, lineno: int, col: int, end_lineno: int, end_col: int
) -> bool:
    if node.lineno is None or node.end_lineno is None or node.end_col_offset is None:
        return False
    start = (node.lineno, node.col_offset)
    end = (node.end_lineno, node.end_col_offset)
    return start <= (lineno, col) and (end_lineno, end_col) <= end


def _span_area(node: ast.AST) -> tuple[int, int]:
    end_line = node.end_lineno if node.end_lineno is not None else node.lineno or 0
    end_col = node.end_col_offset if node.end_col_offset is not None else node.col_offset
    start_line = node.lineno or 0
    return (end_line - start_line, end_col - node.col_offset)


def _param_names(code: types.CodeType) -> list[str]:
    names = list(code.co_varnames[: code.co_argcount + code.co_kwonlyargcount])
    index = code.co_argcount + code.co_kwonlyargcount
    if code.co_flags & inspect.CO_VARARGS:
        names.append(code.co_varnames[index])
        index += 1
    if code.co_flags & inspect.CO_VARKEYWORDS:
        names.append(code.co_varnames[index])
    return names


def _entry_params(frame: types.FrameType) -> dict[str, str]:
    loc = frame.f_locals
    params: dict[str, str] = {}
    for name in _param_names(frame.f_code):
        params[name] = _safe_repr(loc[name]) if name in loc else "?"
    return params


def _align_arg_exprs(code: types.CodeType, node: ast.Call, source: str) -> list[str]:
    names = _param_names(code)
    exprs = {name: "" for name in names}
    pos_names = list(code.co_varnames[: code.co_argcount])
    vararg: str | None = None
    varkw: str | None = None
    index = code.co_argcount + code.co_kwonlyargcount
    if code.co_flags & inspect.CO_VARARGS:
        vararg = code.co_varnames[index]
        index += 1
    if code.co_flags & inspect.CO_VARKEYWORDS:
        varkw = code.co_varnames[index]

    positional = 0
    seen_star = False
    extra: list[str] = []
    for arg in node.args:
        text = ast.get_source_segment(source, arg) or ""
        if isinstance(arg, ast.Starred):
            seen_star = True
            if vararg and not exprs[vararg]:
                exprs[vararg] = text
            continue
        if seen_star:
            return [""] * len(names)
        if positional < len(pos_names):
            exprs[pos_names[positional]] = text
            positional += 1
        else:
            extra.append(text)
    if vararg and extra and not exprs[vararg]:
        exprs[vararg] = ", ".join(extra)

    extra_kw: list[str] = []
    for keyword in node.keywords:
        text = ast.get_source_segment(source, keyword.value) or ""
        if keyword.arg is None:
            if varkw:
                exprs[varkw] = text
            continue
        if keyword.arg in exprs and keyword.arg != vararg:
            exprs[keyword.arg] = text
        else:
            extra_kw.append(f"{keyword.arg}={text}" if text else keyword.arg)
    if varkw and extra_kw and not exprs[varkw]:
        exprs[varkw] = ", ".join(extra_kw)
    return [exprs[name] for name in names]


def _caller_snapshot(frame: types.FrameType) -> dict[str, str]:
    caller = frame.f_back
    if caller is None or getattr(caller.f_code, "co_filename", None) != "<user>":
        return {}
    if caller.f_code.co_name == "<module>":
        return {}
    return _snapshot_locals(caller)


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
