"""Execution patterns: stealing, reactor, proactor, leader/followers.

أنماط تنفيذ: سرقة عمل، مفاعل، إكمال، قائد وتابعين.
"""

from __future__ import annotations

import asyncio
import collections
import selectors
import socket
import threading

from peaa.lab.registry import register


@register("work_stealing")
def demo_work_stealing() -> None:
    deques = [collections.deque(["bill-1", "bill-2", "bill-3"]), collections.deque()]
    done: list[str] = []

    def steal_into(thief: int, victim: int) -> None:
        if deques[victim]:
            deques[thief].append(deques[victim].pop())

    steal_into(1, 0)
    while deques[0]:
        done.append(deques[0].popleft())
    while deques[1]:
        done.append("stolen:" + deques[1].popleft())
    print("work_stealing", done)


@register("reactor")
def demo_reactor() -> None:
    """One thread demultiplexes ready sockets. خيط واحد يوزّع الجاهز."""
    selector = selectors.DefaultSelector()
    left, right = socket.socketpair()
    left.setblocking(False)
    seen: list[bytes] = []

    def on_read() -> None:
        seen.append(left.recv(64))

    selector.register(left, selectors.EVENT_READ, on_read)
    right.sendall(b"lease-bill")
    for key, _mask in selector.select(timeout=1):
        key.data()
    selector.close()
    left.close()
    right.close()
    print("reactor", seen)


@register("proactor")
def demo_proactor() -> None:
    """Completion handler runs when the future finishes. المعالج يشتغل عند الاكتمال."""

    async def main() -> None:
        loop = asyncio.get_running_loop()
        future: asyncio.Future[str] = loop.create_future()
        seen: list[str] = []

        def on_done(done: asyncio.Future[str]) -> None:
            seen.append(done.result())

        future.add_done_callback(on_done)
        future.set_result("invoice-ready")
        await asyncio.sleep(0)
        print("proactor", seen)

    asyncio.run(main())


@register("leader_followers")
def demo_leader_followers() -> None:
    """The leader takes a job, then promotes the next follower before handling it."""
    cond = threading.Condition()
    pending: collections.deque[int] = collections.deque()
    waiting: list[str] = []
    leader = {"name": None}
    closed = {"value": False}
    processed: list[tuple[str, int]] = []

    def promote() -> None:
        if waiting:
            leader["name"] = waiting.pop(0)
        else:
            leader["name"] = None
        cond.notify_all()

    def loop(name: str) -> None:
        while True:
            with cond:
                if leader["name"] is None and name not in waiting:
                    leader["name"] = name
                elif leader["name"] != name:
                    waiting.append(name)
                    while leader["name"] != name and not closed["value"]:
                        cond.wait()
                    if closed["value"] and leader["name"] != name:
                        return
                while not pending and not closed["value"]:
                    cond.wait()
                if not pending and closed["value"]:
                    promote()
                    return
                job = pending.popleft()
                if name in waiting:
                    waiting.remove(name)
                promote()
            processed.append((name, job))

    threads = [threading.Thread(target=loop, args=(f"f{i}",)) for i in range(3)]
    for thread in threads:
        thread.start()
    with cond:
        pending.extend([10, 20, 30, 40])
        cond.notify_all()
    for thread in threads:
        thread.join(timeout=0.2)
    with cond:
        closed["value"] = True
        cond.notify_all()
    for thread in threads:
        thread.join(timeout=1)
    print("leader_followers", processed)
