# Python visualizer

Paste Python, optionally paste stdin, and step through what each line did: the highlighted line, the call stack, globals, and heap objects. Two names that point at the same list share one heap id.

A child Python process runs the tracer. The API process does not execute the pasted code. Limits are about 2 seconds, 300 steps, and a lowered recursion limit. Hitting a limit still returns the steps collected so far.

## Run

From `backend/`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

From `frontend/`:

```bash
npm install
npm run dev
```

The Vite dev server proxies `/api` to `http://127.0.0.1:8000`.

## Trace contract

`POST /api/trace` accepts `{"code": "...", "stdin": ""}` and returns:

```json
{
  "steps": [
    {
      "line": 3,
      "event": "line",
      "func": "<module>",
      "stdout": "hi\n",
      "exception": null,
      "stack": [
        {"func": "add", "line": 2, "locals": [{"name": "x", "value": {"kind": "int", "v": 1}}]}
      ],
      "globals": [{"name": "nums", "value": {"kind": "ref", "id": 1}}],
      "heap": {
        "1": {"kind": "list", "items": [{"kind": "int", "v": 10}, {"kind": "int", "v": 20}]}
      }
    }
  ],
  "stopped": null
}
```

- Primitives (`None`, `bool`, `int`, `float`, `str`) are inlined.
- Containers and user objects go on the heap and are referenced by id. The same Python object always gets the same id inside one step, so aliasing is visible.
- `event` is `line`, `call`, `return`, or `exception`.
- `stopped` is `null`, `"step_limit"`, or `"timeout"`.
- Syntax errors use HTTP 200 with `{"steps": [], "error": {"type": "SyntaxError", "message": "...", "line": 1}}`.
