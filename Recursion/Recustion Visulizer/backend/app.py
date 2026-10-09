"""API for the recursion-tree visualizer."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.examples import EXAMPLES
from backend.tracer import run_trace

app = FastAPI(title="Recursion Tree")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TraceRequest(BaseModel):
    source: str = Field(max_length=100_000)
    call: str = Field(max_length=500)
    debug: bool = False


@app.get("/api/examples")
def examples() -> list[dict[str, str]]:
    return EXAMPLES


@app.post("/api/trace")
def trace(body: TraceRequest) -> dict:
    return run_trace(body.source, body.call, body.debug)


DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if DIST.is_dir():
    app.mount("/", StaticFiles(directory=DIST, html=True), name="ui")
