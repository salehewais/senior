#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ ! -x .venv/bin/uvicorn ]]; then
  echo "Missing .venv. From this directory run:" >&2
  echo "  python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2
  exit 1
fi

if [[ ! -d frontend/node_modules ]]; then
  echo "Missing frontend/node_modules. From the frontend directory run: npm install" >&2
  exit 1
fi

echo "Building the page..."
npm run build --prefix frontend

echo "Open http://127.0.0.1:8000"
exec .venv/bin/uvicorn backend.app:app --port 8000
