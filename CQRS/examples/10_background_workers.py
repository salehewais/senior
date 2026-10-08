#!/usr/bin/env python3
"""
10 — Background Workers
-----------------------
Pool of workers consuming a queue with a concurrency cap (protects DB).
"""

from __future__ import annotations

import queue
import threading
import time

from _demo_data import banner, make_lines

LINES = make_lines(10_000)


def run_report(job: int) -> None:
    total = sum(l.balance for l in LINES if l.branch_id == (job % 5) + 1)
    time.sleep(0.1)
    print(f"  worker={threading.current_thread().name} finished job#{job} total={total:,.2f}")


def worker_loop(name: str, q: queue.Queue) -> None:
    while True:
        job = q.get()
        if job is None:
            q.task_done()
            break
        run_report(job)
        q.task_done()


def main() -> None:
    banner("10 Background Workers — capped concurrency for 50+ users")
    q: queue.Queue = queue.Queue()
    n_workers = 3  # concurrency cap (not 50 parallel AML scans)
    threads = [
        threading.Thread(target=worker_loop, args=(f"w{i}", q), name=f"w{i}", daemon=True)
        for i in range(n_workers)
    ]
    for t in threads:
        t.start()

    for job in range(1, 9):
        q.put(job)  # 8 report requests from users

    q.join()
    for _ in threads:
        q.put(None)
    for t in threads:
        t.join()
    print(f"\nProcessed 8 jobs with only {n_workers} concurrent workers.")
    print("Trade-off: queue backlog if demand >> capacity — show status to users.")


if __name__ == "__main__":
    main()
