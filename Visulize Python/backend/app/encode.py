"""Turn a Python value into an inline value plus a heap map for one step."""

from __future__ import annotations

import math
import types
from typing import Any

MAX_DEPTH = 8
MAX_ITEMS = 40
MAX_HEAP = 60
MAX_STR = 240
MAX_REPR = 200


def safe_repr(value: Any) -> str:
    try:
        text = repr(value)
    except Exception:
        text = "<unrepresentable>"
    if len(text) > MAX_REPR:
        return text[:MAX_REPR] + "…"
    return text


def _clip(text: str) -> str:
    if len(text) > MAX_STR:
        return text[:MAX_STR] + "…"
    return text


class Encoder:
    def __init__(self) -> None:
        self.heap: dict[str, dict[str, Any]] = {}
        self._ids: dict[int, int] = {}
        self._next_id = 1

    def encode(self, value: Any, depth: int = 0) -> dict[str, Any]:
        try:
            return self._encode(value, depth)
        except Exception:
            return {
                "kind": "unknown",
                "type": type(value).__name__,
                "repr": safe_repr(value),
            }

    def _encode(self, value: Any, depth: int) -> dict[str, Any]:
        if value is None:
            return {"kind": "none"}
        if isinstance(value, bool):
            return {"kind": "bool", "v": value}
        if isinstance(value, int):
            return {"kind": "int", "v": value}
        if isinstance(value, float):
            if math.isnan(value) or math.isinf(value):
                return {"kind": "float", "v": None, "repr": str(value)}
            return {"kind": "float", "v": value}
        if isinstance(value, str):
            return {"kind": "str", "v": _clip(value)}

        return self._heap_object(value, depth)

    def _heap_object(self, value: Any, depth: int) -> dict[str, Any]:
        identity = id(value)
        existing = self._ids.get(identity)
        if existing is not None:
            return {"kind": "ref", "id": existing}

        if depth > MAX_DEPTH or len(self.heap) >= MAX_HEAP:
            return {
                "kind": "unknown",
                "type": type(value).__name__,
                "repr": safe_repr(value),
            }

        heap_id = self._next_id
        self._next_id += 1
        self._ids[identity] = heap_id
        key = str(heap_id)
        # Reserve the slot before walking children so cycles point back here.
        self.heap[key] = {"kind": "unknown", "type": type(value).__name__, "repr": ""}

        if isinstance(value, list):
            self.heap[key] = {
                "kind": "list",
                "items": self._items(value, depth),
                "truncated": len(value) > MAX_ITEMS,
            }
        elif isinstance(value, tuple):
            self.heap[key] = {
                "kind": "tuple",
                "items": self._items(value, depth),
                "truncated": len(value) > MAX_ITEMS,
            }
        elif isinstance(value, (set, frozenset)):
            sample = list(value)[:MAX_ITEMS]
            self.heap[key] = {
                "kind": "set" if isinstance(value, set) else "frozenset",
                "items": [self.encode(item, depth + 1) for item in sample],
                "truncated": len(value) > MAX_ITEMS,
            }
        elif isinstance(value, dict):
            pairs = []
            for index, (item_key, item_value) in enumerate(value.items()):
                if index >= MAX_ITEMS:
                    break
                pairs.append(
                    {
                        "key": self.encode(item_key, depth + 1),
                        "value": self.encode(item_value, depth + 1),
                    }
                )
            self.heap[key] = {
                "kind": "dict",
                "items": pairs,
                "truncated": len(value) > MAX_ITEMS,
            }
        elif isinstance(value, types.FunctionType):
            self.heap[key] = self._describe_function(value, depth)
        elif isinstance(value, types.MethodType):
            func = getattr(value, "__func__", None)
            self.heap[key] = self._describe_function(func, depth) if func is not None else {
                "kind": "function",
                "name": safe_repr(value),
                "params": [],
            }
        elif isinstance(value, types.BuiltinFunctionType):
            self.heap[key] = {
                "kind": "function",
                "name": getattr(value, "__name__", "builtin"),
                "params": [],
            }
        elif isinstance(value, type):
            bases = [
                base.__name__
                for base in value.__bases__
                if isinstance(base, type) and base is not object
            ]
            self.heap[key] = {
                "kind": "class",
                "name": value.__name__,
                "bases": bases,
                "attrs": self._class_attrs(value.__dict__, depth),
            }
        elif isinstance(value, types.ModuleType):
            del self.heap[key]
            self._ids.pop(identity, None)
            self._next_id -= 1
            return {"kind": "unknown", "type": "module", "repr": value.__name__}
        elif hasattr(value, "__dict__") and isinstance(getattr(value, "__dict__"), dict):
            self.heap[key] = {
                "kind": "instance",
                "type": type(value).__name__,
                "attrs": self._attrs(value.__dict__, depth),
                "class_ref": self.encode(type(value), depth + 1),
            }
        else:
            self.heap[key] = {
                "kind": "unknown",
                "type": type(value).__name__,
                "repr": safe_repr(value),
            }

        return {"kind": "ref", "id": heap_id}

    def _describe_function(self, func: Any, depth: int) -> dict[str, Any]:
        name = getattr(func, "__name__", "function")
        code = getattr(func, "__code__", None)
        params: list[str] = []
        closure: list[dict[str, Any]] = []
        if code is not None:
            params = [str(item) for item in code.co_varnames[: code.co_argcount]]
            cells = getattr(func, "__closure__", None) or ()
            for cell_name, cell in zip(code.co_freevars, cells):
                try:
                    content = cell.cell_contents
                except ValueError:
                    continue
                closure.append({"name": str(cell_name), "value": self.encode(content, depth + 1)})
        described: dict[str, Any] = {"kind": "function", "name": name, "params": params}
        if closure:
            described["closure"] = closure
        return described

    def _items(self, value: list | tuple, depth: int) -> list[dict[str, Any]]:
        return [self.encode(item, depth + 1) for item in list(value)[:MAX_ITEMS]]

    def _attrs(self, mapping: dict, depth: int) -> list[dict[str, Any]]:
        return self._named_attrs(mapping, depth, keep_dunder_methods=False)

    def _class_attrs(self, mapping: dict, depth: int) -> list[dict[str, Any]]:
        return self._named_attrs(mapping, depth, keep_dunder_methods=True)

    def _named_attrs(self, mapping: dict, depth: int, keep_dunder_methods: bool) -> list[dict[str, Any]]:
        attrs = []
        for name, child in mapping.items():
            if not isinstance(name, str):
                continue
            if name.startswith("__"):
                is_method = isinstance(child, (types.FunctionType, classmethod, staticmethod))
                if not (keep_dunder_methods and is_method):
                    continue
            attrs.append({"name": name, "value": self.encode(child, depth + 1)})
            if len(attrs) >= MAX_ITEMS:
                break
        return attrs
