#!/usr/bin/env python3
"""
09 — Asynchronous Processing
----------------------------
User enqueues a report and gets a job_id immediately; work finishes in background.
Async ≠ faster SQL — it only frees the HTTP/UI thread.
"""

from __future__ import annotations

import queue
import threading
import time
import uuid

from _demo_data import banner, make_lines

JOBS: dict[str, dict] = {}
Q: queue.Queue = queue.Queue()


def worker() -> None:
    lines = make_lines(15_000)
    while True:
        job_id = Q.get()
        if job_id is None:
            break
        JOBS[job_id]["status"] = "running"
        time.sleep(0.4)  # heavy report
        total = sum(l.balance for l in lines if l.branch_id == JOBS[job_id]["branch"])
        JOBS[job_id].update(status="done", result=total)
        Q.task_done()


def request_report(branch: int) -> str:
    job_id = str(uuid.uuid4())[:8]
    JOBS[job_id] = {"status": "queued", "branch": branch, "result": None}
    Q.put(job_id)
    return job_id  # return immediately to user


def main() -> None:
    banner("09 Async Processing — enqueue, don't block the user")
    t = threading.Thread(target=worker, daemon=True)
    t.start()

    t0 = time.perf_counter()
    job_id = request_report(branch=3)
    enqueue_ms = (time.perf_counter() - t0) * 1000
    print(f"user got job_id={job_id} in {enqueue_ms:.1f}ms (UI free)")

    while JOBS[job_id]["status"] != "done":
        print(f"  …polling status={JOBS[job_id]['status']}")
        time.sleep(0.15)

    print(f"notification: report ready result={JOBS[job_id]['result']:,.2f}")
    Q.put(None)
    t.join()
    print("\nTrade-off: better UX / isolation; query duration may stay 60s.")


if __name__ == "__main__":
    main()
