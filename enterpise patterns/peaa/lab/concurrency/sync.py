"""Synchronization patterns. أنماط المزامنة بين الخيوط."""

from __future__ import annotations

import threading

from peaa.lab.registry import register


class RWLock:
    """Many readers or one writer. قرّاء متعددون أو كاتب واحد."""

    def __init__(self) -> None:
        self._cond = threading.Condition()
        self._readers = 0
        self._writer = False

    def acquire_read(self) -> None:
        with self._cond:
            while self._writer:
                self._cond.wait()
            self._readers += 1

    def release_read(self) -> None:
        with self._cond:
            self._readers -= 1
            if self._readers == 0:
                self._cond.notify_all()

    def acquire_write(self) -> None:
        with self._cond:
            while self._writer or self._readers:
                self._cond.wait()
            self._writer = True

    def release_write(self) -> None:
        with self._cond:
            self._writer = False
            self._cond.notify_all()


@register("rwlock")
def demo_rwlock() -> None:
    lock = RWLock()
    seen: list[str] = []

    def reader(name: str) -> None:
        lock.acquire_read()
        try:
            seen.append(f"read:{name}")
        finally:
            lock.release_read()

    def writer() -> None:
        lock.acquire_write()
        try:
            seen.append("write")
        finally:
            lock.release_write()

    threads = [
        threading.Thread(target=reader, args=("a",)),
        threading.Thread(target=reader, args=("b",)),
        threading.Thread(target=writer),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    print("rwlock", seen)


@register("lock_splitting")
def demo_lock_splitting() -> None:
    billing = {"n": 0, "lock": threading.Lock()}
    notify = {"n": 0, "lock": threading.Lock()}

    def bump(box: dict, times: int) -> None:
        for _ in range(times):
            with box["lock"]:
                box["n"] += 1

    threads = [
        threading.Thread(target=bump, args=(billing, 100)),
        threading.Thread(target=bump, args=(notify, 100)),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    print("lock_splitting", billing["n"], notify["n"])


class StripedLocks:
    def __init__(self, stripes: int = 8) -> None:
        self._locks = [threading.Lock() for _ in range(stripes)]

    def lock_for(self, key: str) -> threading.Lock:
        return self._locks[hash(key) % len(self._locks)]


@register("striped_locking")
def demo_striped() -> None:
    stripes = StripedLocks(4)
    totals = {"lease-1": 0, "lease-2": 0}
    guard = threading.Lock()

    def add(key: str, amount: int) -> None:
        with stripes.lock_for(key):
            with guard:
                totals[key] += amount

    threads = [
        threading.Thread(target=add, args=("lease-1", 10)),
        threading.Thread(target=add, args=("lease-1", 5)),
        threading.Thread(target=add, args=("lease-2", 7)),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    print("striped_locking", totals)


@register("guarded_suspension")
def demo_guarded() -> None:
    cond = threading.Condition()
    ready = {"value": False}
    result: list[str] = []

    def wait_for_bill() -> None:
        with cond:
            while not ready["value"]:
                cond.wait()
            result.append("ran")

    def publish() -> None:
        with cond:
            ready["value"] = True
            cond.notify_all()

    waiter = threading.Thread(target=wait_for_bill)
    waiter.start()
    publish()
    waiter.join()
    print("guarded_suspension", result)


@register("barrier")
def demo_barrier() -> None:
    barrier = threading.Barrier(3)
    phases: list[str] = []
    lock = threading.Lock()

    def worker(name: str) -> None:
        with lock:
            phases.append(f"arrive:{name}")
        barrier.wait()
        with lock:
            phases.append(f"go:{name}")

    threads = [threading.Thread(target=worker, args=(str(i),)) for i in range(3)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    first_go = phases.index("go:0") if "go:0" in phases else phases.index(next(p for p in phases if p.startswith("go:")))
    arrives_before = all(item.startswith("arrive:") for item in phases[:3])
    print("barrier ordered", arrives_before, "events", len(phases), "sample", phases[first_go])
