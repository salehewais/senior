from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models import TraceRequest, TraceResponse
from app.runner import run_trace

app = FastAPI(title="Python visualizer")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, bool]:
    return {"ok": True}


@app.post("/api/trace", response_model=TraceResponse)
def trace(body: TraceRequest) -> TraceResponse:
    return TraceResponse.model_validate(run_trace(body.code, body.stdin))
