"""Worker and task patterns. إدارة الخيوط والمهام."""

from __future__ import annotations

import heapq
import queue
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from peaa.lab.registry import register


@register("thread_pool")
def demo_thread_pool() -> None:
    """Fixed workers versus ThreadPoolExecutor. مجموعة ثابتة مقابل المنفّذ الجاهز."""
    log: list[tuple[str, int]] = []
    lock = threading.Lock()
    jobs: queue.Queue[int | None] = queue.Queue()

    def worker() -> None:
        while True:
            item = jobs.get()
            try:
                if item is None:
                    return
                with lock:
                    log.append((threading.current_thread().name, item))
            finally:
                jobs.task_done()

    threads = [threading.Thread(target=worker, name=f"w{i}") for i in range(3)]
    for thread in threads:
        thread.start()
    for number in range(6):
        jobs.put(number)
    jobs.join()
    for _ in threads:
        jobs.put(None)
    for thread in threads:
        thread.join()

    with ThreadPoolExecutor(max_workers=3) as pool:
        squares = list(pool.map(lambda n: n * n, range(6)))
    print("thread_pool hand", log)
    print("thread_pool executor", squares)


@register("producer_consumer")
def demo_producer_consumer() -> None:
    """Bounded queue applies backpressure. طابور محدود يبطّئ المنتج."""
    buffer: queue.Queue[int | None] = queue.Queue(maxsize=2)
    consumed: list[int] = []

    def producer() -> None:
        for number in range(5):
            buffer.put(number)
        buffer.put(None)

    def consumer() -> None:
        while True:
            item = buffer.get()
            if item is None:
                return
            consumed.append(item)

    threads = [threading.Thread(target=producer), threading.Thread(target=consumer)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    print("producer_consumer", consumed, "capacity", buffer.maxsize)


@register("active_object")
def demo_active_object() -> None:
    """Calls are queued onto one private thread. الاستدعاءات تدخل طابور خيط خاص."""

    class ActiveBiller:
        def __init__(self) -> None:
            self._queue: queue.Queue = queue.Queue()
            self._thread = threading.Thread(target=self._run, name="active-biller")
            self._thread.start()

        def _run(self) -> None:
            while True:
                message = self._queue.get()
                if message is None:
                    return
                method, arg, box = message
                box.put(method(arg))

        def bill(self, cents: int) -> int:
            box: queue.Queue[int] = queue.Queue()
            self._queue.put((lambda value: value + 1000, cents, box))
            return box.get()

        def stop(self) -> None:
            self._queue.put(None)
            self._thread.join()

    biller = ActiveBiller()
    print("active_object", biller.bill(50000), biller.bill(20000))
    biller.stop()


@register("future_promise")
def demo_future() -> None:
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(lambda n: n * 10, i) for i in range(4)]
        done = [future.result() for future in as_completed(futures)]
    print("future_promise", sorted(done))


@register("scheduler")
def demo_scheduler() -> None:
    """Due times sit on a heap. المواعيد على كومة."""
    clock = {"t": 0.0}
    pending: list[tuple[float, int, str]] = []
    ran: list[str] = []

    def schedule(delay: float, name: str) -> None:
        heapq.heappush(pending, (clock["t"] + delay, len(ran) + len(pending), name))

    schedule(0, "bill-lease-1")
    schedule(5, "remind")
    schedule(0, "notify")
    while pending and pending[0][0] <= 0:
        _due, _seq, name = heapq.heappop(pending)
        ran.append(name)
    clock["t"] = 5
    while pending and pending[0][0] <= clock["t"]:
        _due, _seq, name = heapq.heappop(pending)
        ran.append(name)
    print("scheduler", ran)
