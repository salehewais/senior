"""Child process: run user code under sys.settrace and print one JSON object."""

from __future__ import annotations

import builtins
import io
import json
import os
import signal
import sys
import time
from typing import Any

from app.encode import Encoder

EVENTS = ("line", "call", "return", "exception")
MAX_STDOUT = 12_000
RECURSION_LIMIT = 128


class StepLimit(BaseException):
    pass


class TimeoutStop(BaseException):
    pass


def make_input(data: str, stdout_buf: io.StringIO):
    lines = data.splitlines()
    index = 0

    def _input(prompt: str = "") -> str:
        nonlocal index
        if prompt:
            stdout_buf.write(str(prompt))
        if index >= len(lines):
            raise EOFError("EOF when reading a line")
        line = lines[index]
        index += 1
        return line

    return _input


def _bindings(mapping: dict[str, Any], encoder: Encoder) -> list[dict[str, Any]]:
    bindings = []
    try:
        items = list(mapping.items())
    except Exception:
        return bindings
    for name, value in items:
        if not isinstance(name, str) or name.startswith("__"):
            continue
        bindings.append({"name": name, "value": encoder.encode(value)})
    return bindings


def _exception_info(arg: Any) -> dict[str, str] | None:
    if arg is None:
        return None
    if isinstance(arg, BaseException):
        return {"type": type(arg).__name__, "message": str(arg)}
    if isinstance(arg, tuple) and len(arg) >= 2:
        exc_type, exc_value = arg[0], arg[1]
        if isinstance(exc_value, BaseException):
            return {"type": type(exc_value).__name__, "message": str(exc_value)}
        name = getattr(exc_type, "__name__", None) or "Exception"
        return {"type": str(name), "message": str(exc_value)}
    return {"type": "Exception", "message": str(arg)}


def _frame_line(frame) -> int:
    line = frame.f_lineno
    if isinstance(line, int) and line > 0:
        return line
    first = frame.f_code.co_firstlineno
    if isinstance(first, int) and first > 0:
        return first
    return 1


def _snapshot(frame, event: str, arg: Any, filename: str, stdout_buf: io.StringIO) -> dict[str, Any]:
    encoder = Encoder()
    frames = []
    current = frame
    while current is not None:
        code_file = current.f_code.co_filename
        if os.path.abspath(code_file) == filename:
            frames.append(current)
        current = current.f_back
    frames.reverse()

    stack = []
    for item in frames:
        stack.append(
            {
                "func": item.f_code.co_name,
                "line": _frame_line(item),
                "locals": _bindings(item.f_locals, encoder),
            }
        )

    step: dict[str, Any] = {
        "line": _frame_line(frame),
        "event": event,
        "func": frame.f_code.co_name,
        "stdout": stdout_buf.getvalue()[:MAX_STDOUT],
        "exception": _exception_info(arg) if event == "exception" else None,
        "stack": stack,
        "globals": _bindings(frame.f_globals, encoder),
        "heap": encoder.heap,
    }
    if event == "return" and frame.f_code.co_name != "<module>":
        step["return_value"] = encoder.encode(arg)
    return step


def trace_source(
    source: str,
    filename: str,
    user_stdin: str,
    max_steps: int,
    timeout: float,
) -> dict[str, Any]:
    filename = os.path.abspath(filename)
    try:
        compiled = compile(source, filename, "exec")
    except SyntaxError as exc:
        return {
            "steps": [],
            "stopped": None,
            "error": {
                "type": "SyntaxError",
                "message": exc.msg or str(exc),
                "line": exc.lineno,
            },
        }

    stdout_buf = io.StringIO()
    steps: list[dict[str, Any]] = []
    state: dict[str, Any] = {"stopped": None, "tripped": False, "busy": False, "unwind_frame": None}
    deadline = time.monotonic() + timeout
    old_stdout = sys.stdout
    old_input = builtins.input
    previous_handler = signal.getsignal(signal.SIGALRM)
    previous_recursion = sys.getrecursionlimit()

    def stop(reason: str) -> None:
        state["tripped"] = True
        state["stopped"] = reason

    def on_alarm(_signum, _frame) -> None:
        stop("timeout")
        raise TimeoutStop()

    def tracer(frame, event, arg):
        if os.path.abspath(frame.f_code.co_filename) != filename:
            return None
        if state["tripped"]:
            return None
        if state["busy"]:
            return tracer
        if len(steps) >= max_steps:
            stop("step_limit")
            raise StepLimit()
        if time.monotonic() >= deadline:
            stop("timeout")
            raise TimeoutStop()
        if event == "return" and state["unwind_frame"] == id(frame):
            # A return with no value follows an exception leaving this frame.
            state["unwind_frame"] = None
            return tracer
        if event == "line":
            state["unwind_frame"] = None
        if event in EVENTS:
            if event == "exception":
                state["unwind_frame"] = id(frame)
            state["busy"] = True
            try:
                steps.append(_snapshot(frame, event, arg, filename, stdout_buf))
            except (StepLimit, TimeoutStop):
                raise
            except Exception:
                # A snapshot must not hide the user's program.
                pass
            finally:
                state["busy"] = False
        return tracer

    user_globals = {"__name__": "__main__", "__file__": filename}
    builtins.input = make_input(user_stdin, stdout_buf)
    sys.stdout = stdout_buf
    sys.setrecursionlimit(RECURSION_LIMIT)
    signal.signal(signal.SIGALRM, on_alarm)
    signal.setitimer(signal.ITIMER_REAL, max(timeout, 0.1))
    sys.settrace(tracer)
    caught: Exception | None = None
    try:
        exec(compiled, user_globals)
    except (StepLimit, TimeoutStop):
        pass
    except Exception as exc:
        caught = exc
    finally:
        sys.settrace(None)
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous_handler)
        sys.stdout = old_stdout
        builtins.input = old_input
        sys.setrecursionlimit(previous_recursion)

    if caught is not None and not any(step.get("exception") for step in steps):
        line = None
        traceback = caught.__traceback__
        error_frame = None
        while traceback is not None:
            if os.path.abspath(traceback.tb_frame.f_code.co_filename) == filename:
                line = traceback.tb_lineno
                error_frame = traceback.tb_frame
            traceback = traceback.tb_next
        if error_frame is not None and len(steps) < max_steps:
            try:
                step = _snapshot(error_frame, "exception", caught, filename, stdout_buf)
                step["line"] = line or step["line"]
                step["exception"] = {
                    "type": type(caught).__name__,
                    "message": str(caught),
                }
                steps.append(step)
            except Exception:
                pass

    return {"steps": steps, "stopped": state["stopped"], "error": None}


def main() -> None:
    try:
        filename = os.path.abspath(sys.argv[1])
        max_steps = int(sys.argv[2]) if len(sys.argv) > 2 else 300
        timeout = float(sys.argv[3]) if len(sys.argv) > 3 else 1.7
        user_stdin = sys.stdin.read()
        source = open(filename, encoding="utf-8").read()
        result = trace_source(source, filename, user_stdin, max_steps, timeout)
    except Exception as exc:
        result = {
            "steps": [],
            "stopped": None,
            "error": {
                "type": type(exc).__name__,
                "message": str(exc),
                "line": None,
            },
        }
    sys.__stdout__.write(json.dumps(result))
    sys.__stdout__.write("\n")
    sys.__stdout__.flush()


if __name__ == "__main__":
    main()
