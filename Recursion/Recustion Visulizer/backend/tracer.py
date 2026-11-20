"""Trace one Python function and record call / return events.

The starting call names the function to follow, for example ``fib(5)`` or
``subset_sum(0, 5)``. Functions defined inside that function are followed too,
so a nested recursive helper shows up in the tree. Methods of the same class
are followed as well, so a recursive helper called on ``self`` shows up.
Other calls, including the standard library and helpers defined beside it,
are ignored. The user source
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
    if isinstance(func, types.MethodType):
        func = func.__func__
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
    last_loops: dict[int, list[dict[str, Any]] | None] = {}
    arg_index = _ArgIndex(source, call)
    loop_index = _build_loop_index(source)

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
                frame_loops = _loop_snapshot(fr, loop_index)
                caller_loops = _caller_loop_snapshot(fr, loop_index)
                open_ids.append(node_id)
                last_locals[node_id] = frame_locals
                last_loops[node_id] = frame_loops
                if parent is not None:
                    last_locals[parent] = caller_locals
                    last_loops[parent] = caller_loops
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
                    "loops": frame_loops,
                    "callerLoops": caller_loops,
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
                    frame_loops = _loop_snapshot(fr, loop_index)
                    last_loops[node_id] = frame_loops
                    _emit(
                        {
                            "type": "event",
                            "event": {
                                "type": "line",
                                "id": node_id,
                                "line": lineno,
                                "locals": snapshot,
                                "changed": changed,
                                "loops": frame_loops,
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
                frame_loops = _loop_snapshot(fr, loop_index)
                caller_loops = _caller_loop_snapshot(fr, loop_index)
                last_locals[node_id] = frame_locals
                last_loops[node_id] = frame_loops
                parent = open_ids[-1] if open_ids else None
                if parent is not None:
                    last_locals[parent] = caller_locals
                    last_loops[parent] = caller_loops
                return_event: dict[str, Any] = {
                    "type": "return",
                    "id": node_id,
                    "value": "raised" if failed else _safe_repr(value),
                    "error": failed,
                    "locals": frame_locals,
                    "callerLocals": caller_locals,
                    "loops": frame_loops,
                    "callerLoops": caller_loops,
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
                "loops": last_loops.get(node_id),
                "callerLoops": last_loops.get(parent) if parent is not None else None,
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
    """True for the called function, functions inside it, and methods of its class."""
    if frame_code is target_code:
        return True
    if getattr(frame_code, "co_filename", None) != "<user>":
        return False
    qualname = getattr(frame_code, "co_qualname", "") or frame_code.co_name
    target_qual = getattr(target_code, "co_qualname", "") or target_code.co_name
    if qualname.startswith(target_qual + ".<locals>."):
        return True
    target_class = _class_name(target_qual)
    return target_class is not None and target_class == _class_name(qualname)


def _class_name(qualname: str) -> str | None:
    """Return the class that owns a method, ignoring functions nested inside it."""
    owner = qualname.split(".<locals>.", 1)[0]
    if "." not in owner:
        return None
    return owner.split(".", 1)[0]


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


def _caller_loop_snapshot(
    frame: types.FrameType, loop_index: dict[int, list[dict[str, Any]]]
) -> list[dict[str, Any]] | None:
    caller = frame.f_back
    if caller is None or getattr(caller.f_code, "co_filename", None) != "<user>":
        return None
    if caller.f_code.co_name == "<module>":
        return None
    return _loop_snapshot(caller, loop_index)


def _build_loop_index(source: str) -> dict[int, list[dict[str, Any]]]:
    """Map each function's co_firstlineno to the loops in its body."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {}

    index: dict[int, list[dict[str, Any]]] = {}

    def collect(body: list[ast.stmt]) -> list[dict[str, Any]]:
        loops: list[dict[str, Any]] = []
        for stmt in body:
            if isinstance(stmt, ast.For):
                loops.append(_for_loop_info(stmt))
                loops.extend(collect(stmt.body))
                loops.extend(collect(stmt.orelse))
            elif isinstance(stmt, ast.While):
                loops.append(_while_loop_info(stmt, source))
                loops.extend(collect(stmt.body))
                loops.extend(collect(stmt.orelse))
            elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            else:
                for child_body in _compound_bodies(stmt):
                    loops.extend(collect(child_body))
        return loops

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            index[node.lineno] = collect(node.body)
    return index


def _compound_bodies(stmt: ast.stmt) -> list[list[ast.stmt]]:
    bodies: list[list[ast.stmt]] = []
    if isinstance(stmt, ast.If):
        bodies.append(stmt.body)
        bodies.append(stmt.orelse)
    elif isinstance(stmt, (ast.With, ast.AsyncWith)):
        bodies.append(stmt.body)
    elif isinstance(stmt, ast.Try):
        bodies.append(stmt.body)
        for handler in stmt.handlers:
            bodies.append(handler.body)
        bodies.append(stmt.orelse)
        bodies.append(stmt.finalbody)
    elif isinstance(stmt, ast.Match):
        for case in stmt.cases:
            bodies.append(case.body)
    return bodies


def _for_bound_names(target: ast.AST) -> list[str]:
    """Names bound by a for-loop target, in source order."""
    names: list[str] = []

    def walk(node: ast.AST) -> None:
        if isinstance(node, ast.Name):
            names.append(node.id)
        elif isinstance(node, (ast.Tuple, ast.List)):
            for elt in node.elts:
                walk(elt)
        elif isinstance(node, ast.Starred):
            walk(node.value)

    walk(target)
    return names


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    return None


def _enumerate_start(call: ast.Call) -> dict[str, Any] | None:
    """Start index for enumerate(iterable) or enumerate(iterable, start)."""
    if len(call.args) >= 2:
        return _bound_expr(call.args[1])
    for keyword in call.keywords:
        if keyword.arg == "start":
            return _bound_expr(keyword.value)
    return {"kind": "const", "value": 0}


def _len_bound(node: ast.AST) -> dict[str, Any] | None:
    """len(expr) when expr is a local name we can resolve."""
    if isinstance(node, ast.Name):
        return {"kind": "len", "name": node.id}
    return None


def _add_bounds(
    left: dict[str, Any] | None, right: dict[str, Any] | None
) -> dict[str, Any] | None:
    if left is None or right is None:
        return None
    if left == {"kind": "const", "value": 0}:
        return right
    return {"kind": "binop", "op": "Add", "left": left, "right": right}


def _for_loop_info(node: ast.For) -> dict[str, Any]:
    bound_names = _for_bound_names(node.target)
    target: str | None = None
    value_targets: list[str] = []
    start_expr: dict[str, Any] | None = None
    end_expr: dict[str, Any] | None = None

    iter_node = node.iter
    if isinstance(iter_node, ast.Call) and _call_name(iter_node.func) == "range":
        # for i in range(...) — classic indexed loop
        if bound_names:
            target = bound_names[0]
            value_targets = bound_names[1:]
        args = iter_node.args
        if len(args) == 1:
            start_expr = {"kind": "const", "value": 0}
            end_expr = _bound_expr(args[0])
        elif len(args) >= 2:
            start_expr = _bound_expr(args[0])
            end_expr = _bound_expr(args[1])
    elif isinstance(iter_node, ast.Call) and _call_name(iter_node.func) == "enumerate":
        # for i, x in enumerate(xs[, start]) — first name is the index
        if bound_names:
            target = bound_names[0]
            value_targets = bound_names[1:]
        start_expr = _enumerate_start(iter_node)
        if iter_node.args:
            end_expr = _add_bounds(start_expr, _len_bound(iter_node.args[0]))
    else:
        # for x in xs / for a, b in pairs — no numeric index in locals
        value_targets = bound_names
        if isinstance(iter_node, ast.Name):
            start_expr = {"kind": "const", "value": 0}
            end_expr = _len_bound(iter_node)

    return {
        "kind": "for",
        "start_line": node.lineno,
        "end_line": node.end_lineno if node.end_lineno is not None else node.lineno,
        "target": target,
        "value_targets": value_targets,
        "start_expr": start_expr,
        "end_expr": end_expr,
        "condition": None,
    }


def _while_loop_info(node: ast.While, source: str) -> dict[str, Any]:
    condition = ast.get_source_segment(source, node.test)
    if condition is None:
        try:
            condition = ast.unparse(node.test)
        except Exception:
            condition = None
    return {
        "kind": "while",
        "start_line": node.lineno,
        "end_line": node.end_lineno if node.end_lineno is not None else node.lineno,
        "target": None,
        "start_expr": None,
        "end_expr": None,
        "condition": condition,
        "condition_expr": _condition_expr(node.test),
    }


_MISSING = object()

_BOUND_BINOPS = {
    ast.Add: "Add",
    ast.Sub: "Sub",
    ast.Mult: "Mult",
    ast.FloorDiv: "FloorDiv",
    ast.Mod: "Mod",
}

_BOUND_UNARY = {
    ast.UAdd: "UAdd",
    ast.USub: "USub",
}

_CONDITION_UNARY = {
    **_BOUND_UNARY,
    ast.Not: "Not",
}

_COMPARE_OPS = {
    ast.Eq: "Eq",
    ast.NotEq: "NotEq",
    ast.Lt: "Lt",
    ast.LtE: "LtE",
    ast.Gt: "Gt",
    ast.GtE: "GtE",
    ast.Is: "Is",
    ast.IsNot: "IsNot",
    ast.In: "In",
    ast.NotIn: "NotIn",
}

_EVAL_BINOPS = {
    "Add": lambda a, b: a + b,
    "Sub": lambda a, b: a - b,
    "Mult": lambda a, b: a * b,
    "FloorDiv": lambda a, b: a // b,
    "Mod": lambda a, b: a % b,
}

_EVAL_UNARY = {
    "UAdd": lambda a: +a,
    "USub": lambda a: -a,
    "Not": lambda a: not a,
}

_EVAL_COMPARE = {
    "Eq": lambda a, b: a == b,
    "NotEq": lambda a, b: a != b,
    "Lt": lambda a, b: a < b,
    "LtE": lambda a, b: a <= b,
    "Gt": lambda a, b: a > b,
    "GtE": lambda a, b: a >= b,
    "Is": lambda a, b: a is b,
    "IsNot": lambda a, b: a is not b,
    "In": lambda a, b: a in b,
    "NotIn": lambda a, b: a not in b,
}


def _bound_expr(node: ast.AST) -> dict[str, Any] | None:
    """Serialize a safe arithmetic bound expression, or None if unsupported."""
    if isinstance(node, ast.Constant):
        return {"kind": "const", "value": node.value}
    if isinstance(node, ast.Name):
        return {"kind": "name", "name": node.id}
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "len"
        and len(node.args) == 1
        and isinstance(node.args[0], ast.Name)
    ):
        return {"kind": "len", "name": node.args[0].id}
    if isinstance(node, ast.UnaryOp):
        op = _BOUND_UNARY.get(type(node.op))
        if op is None:
            return None
        operand = _bound_expr(node.operand)
        if operand is None:
            return None
        return {"kind": "unary", "op": op, "operand": operand}
    if isinstance(node, ast.BinOp):
        op = _BOUND_BINOPS.get(type(node.op))
        if op is None:
            return None
        left = _bound_expr(node.left)
        right = _bound_expr(node.right)
        if left is None or right is None:
            return None
        return {"kind": "binop", "op": op, "left": left, "right": right}
    return None


def _condition_expr(node: ast.AST) -> dict[str, Any] | None:
    """Serialize a safe while-test expression, or None if unsupported."""
    base = _bound_expr(node)
    if base is not None:
        return base
    if isinstance(node, ast.UnaryOp):
        op = _CONDITION_UNARY.get(type(node.op))
        if op is None:
            return None
        operand = _condition_expr(node.operand)
        if operand is None:
            return None
        return {"kind": "unary", "op": op, "operand": operand}
    if isinstance(node, ast.BoolOp):
        if isinstance(node.op, ast.And):
            op_name = "And"
        elif isinstance(node.op, ast.Or):
            op_name = "Or"
        else:
            return None
        values: list[dict[str, Any]] = []
        for value in node.values:
            tree = _condition_expr(value)
            if tree is None:
                return None
            values.append(tree)
        return {"kind": "boolop", "op": op_name, "values": values}
    if isinstance(node, ast.Compare):
        left = _condition_expr(node.left)
        if left is None:
            return None
        ops: list[str] = []
        comparators: list[dict[str, Any]] = []
        for op_node, comparator in zip(node.ops, node.comparators):
            op_name = _COMPARE_OPS.get(type(op_node))
            if op_name is None:
                return None
            tree = _condition_expr(comparator)
            if tree is None:
                return None
            ops.append(op_name)
            comparators.append(tree)
        return {"kind": "compare", "left": left, "ops": ops, "comparators": comparators}
    return None


def _eval_expr(expr: dict[str, Any] | None, loc: dict[str, Any]) -> object:
    """Evaluate a serialized expression against locals, or return _MISSING."""
    if expr is None:
        return _MISSING
    kind = expr.get("kind")
    try:
        if kind == "const":
            return expr.get("value")
        if kind == "name":
            name = expr.get("name")
            if isinstance(name, str) and name in loc:
                return loc[name]
            return _MISSING
        if kind == "len":
            name = expr.get("name")
            if isinstance(name, str) and name in loc:
                return len(loc[name])
            return _MISSING
        if kind == "unary":
            op = expr.get("op")
            fn = _EVAL_UNARY.get(op) if isinstance(op, str) else None
            if fn is None:
                return _MISSING
            operand = _eval_expr(expr.get("operand"), loc)
            if operand is _MISSING:
                return _MISSING
            return fn(operand)
        if kind == "binop":
            op = expr.get("op")
            fn = _EVAL_BINOPS.get(op) if isinstance(op, str) else None
            if fn is None:
                return _MISSING
            left = _eval_expr(expr.get("left"), loc)
            right = _eval_expr(expr.get("right"), loc)
            if left is _MISSING or right is _MISSING:
                return _MISSING
            return fn(left, right)
        if kind == "boolop":
            values = expr.get("values")
            if not isinstance(values, list) or not values:
                return _MISSING
            op = expr.get("op")
            if op == "And":
                result: object = True
                for value in values:
                    result = _eval_expr(value, loc)
                    if result is _MISSING:
                        return _MISSING
                    if not result:
                        return result
                return result
            if op == "Or":
                result = False
                for value in values:
                    result = _eval_expr(value, loc)
                    if result is _MISSING:
                        return _MISSING
                    if result:
                        return result
                return result
            return _MISSING
        if kind == "compare":
            left = _eval_expr(expr.get("left"), loc)
            if left is _MISSING:
                return _MISSING
            ops = expr.get("ops")
            comparators = expr.get("comparators")
            if not isinstance(ops, list) or not isinstance(comparators, list):
                return _MISSING
            if len(ops) != len(comparators) or not ops:
                return _MISSING
            current = left
            for op_name, comparator_expr in zip(ops, comparators):
                fn = _EVAL_COMPARE.get(op_name) if isinstance(op_name, str) else None
                if fn is None:
                    return _MISSING
                right = _eval_expr(comparator_expr, loc)
                if right is _MISSING:
                    return _MISSING
                if not fn(current, right):
                    return False
                current = right
            return True
    except Exception:
        return _MISSING
    return _MISSING


def _resolve_bound(expr: dict[str, Any] | None, loc: dict[str, Any]) -> str | None:
    value = _eval_expr(expr, loc)
    if value is _MISSING:
        return None
    return _safe_repr(value)


def _resolve_loop_index(loop: dict[str, Any], loc: dict[str, Any]) -> str | None:
    target = loop.get("target")
    if isinstance(target, str) and target in loc:
        return _safe_repr(loc[target])
    return None


def _resolve_loop_value(loop: dict[str, Any], loc: dict[str, Any]) -> str | None:
    """Current non-index loop bindings, e.g. ``num`` in ``for i, num in enumerate``."""
    names = loop.get("value_targets") or []
    if not isinstance(names, list) or not names:
        return None
    parts: list[str] = []
    for name in names:
        if isinstance(name, str) and name in loc:
            parts.append(
                f"{name}={_safe_repr(loc[name])}" if len(names) > 1 else _safe_repr(loc[name])
            )
    return ", ".join(parts) if parts else None


def _loop_snapshot(
    frame: types.FrameType, loop_index: dict[int, list[dict[str, Any]]]
) -> list[dict[str, Any]] | None:
    loops = loop_index.get(frame.f_code.co_firstlineno)
    if not loops:
        return None
    lineno = frame.f_lineno
    containing = [loop for loop in loops if loop["start_line"] <= lineno <= loop["end_line"]]
    if not containing:
        return None
    # Outer → inner: larger span first, then earlier start_line.
    containing.sort(
        key=lambda loop: (-(loop["end_line"] - loop["start_line"]), loop["start_line"]),
    )
    loc = frame.f_locals
    frames: list[dict[str, Any]] = []
    for loop in containing:
        if loop["kind"] == "for":
            index = _resolve_loop_index(loop, loc)
            value = _resolve_loop_value(loop, loc)
            frames.append(
                {
                    "kind": "for",
                    "start": _resolve_bound(loop["start_expr"], loc),
                    "end": _resolve_bound(loop["end_expr"], loc),
                    "index": index,
                    "value": value,
                    "condition": None,
                }
            )
        else:
            condition_value: str | None = None
            value = _eval_expr(loop.get("condition_expr"), loc)
            if value is not _MISSING:
                condition_value = _safe_repr(value)
            frames.append(
                {
                    "kind": "while",
                    "start": None,
                    "end": None,
                    "index": None,
                    "value": None,
                    "condition": loop.get("condition"),
                    "conditionValue": condition_value,
                }
            )
    return frames


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
