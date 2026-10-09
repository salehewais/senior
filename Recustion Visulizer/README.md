# Recursion Tree

A local visualizer for Python recursion. Write a normal function, give it a starting call such as `fib(5)`, and step through the call tree. The function can have any name. Helpers and constants in the same file are allowed. A function defined inside the one you call is traced with it; other helpers are not.

## Run

From this directory:

```bash
./run.sh
```

That builds the page and starts the app at http://127.0.0.1:8000.

To work on the page with live reload, use two terminals instead:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app:app --reload --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173. Load an example, press Run, then play or step. Ctrl+Enter also runs.

To serve the built UI from the API instead:

```bash
cd frontend && npm run build
uvicorn backend.app:app --port 8000
```

Then open http://127.0.0.1:8000.

## How a run works

The starting call has to be a direct call such as `fib(5)` or `knapsack(0, 12)`. The API compiles your file, runs it in a subprocess, and follows that function with `sys.settrace`. Each call and return becomes an event. The page plays the events in order and lays the visible nodes out as a tidy tree.

A run stops after 2 seconds or 400 recorded calls, so a runaway recursion cannot hang the app. Code you run executes on this machine.
