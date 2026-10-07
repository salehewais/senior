"""Rate limit, bulkhead, and monitor. تحديد المعدل والعزل والمراقب."""

from __future__ import annotations

import queue
import threading

from peaa.lab.registry import register


class TokenBucket:
    """Virtual-clock token bucket. دلو رموز بساعة افتراضية."""

    def __init__(self, rate: float, capacity: float) -> None:
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.now = 0.0

    def advance(self, dt: float) -> None:
        self.now += dt
        self.tokens = min(self.capacity, self.tokens + dt * self.rate)

    def allow(self) -> bool:
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


@register("rate_limiter")
def demo_rate_limiter() -> None:
    bucket = TokenBucket(rate=1, capacity=3)
    decisions = [bucket.allow() for _ in range(5)]
    bucket.advance(2)
    decisions.append(bucket.allow())
    print("rate_limiter", decisions)


@register("bulkhead")
def demo_bulkhead() -> None:
    """A full notifications queue does not block billing. طابور الإشعارات الممتلئ لا يوقف الفوترة."""
    billing: queue.Queue[str] = queue.Queue(maxsize=2)
    notifications: queue.Queue[str] = queue.Queue(maxsize=1)
    notifications.put("mail-1")
    billing.put("invoice-1")
    billing.put("invoice-2")
    notify_blocked = False
    try:
        notifications.put_nowait("mail-2")
    except queue.Full:
        notify_blocked = True
    print("bulkhead billing", billing.qsize(), "notify_blocked", notify_blocked)


class BalanceMonitor:
    """Synchronized methods plus a condition. دوال متزامنة وشرط انتظار."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._cv = threading.Condition(self._lock)
        self._cents = 0

    def deposit(self, cents: int) -> None:
        with self._cv:
            self._cents += cents
            self._cv.notify_all()

    def withdraw(self, cents: int) -> None:
        with self._cv:
            while self._cents < cents:
                self._cv.wait()
            self._cents -= cents

    @property
    def cents(self) -> int:
        with self._lock:
            return self._cents


@register("monitor_object")
def demo_monitor() -> None:
    monitor = BalanceMonitor()

    def take() -> None:
        monitor.withdraw(40)

    worker = threading.Thread(target=take)
    worker.start()
    monitor.deposit(50)
    worker.join()
    print("monitor_object", monitor.cents)
