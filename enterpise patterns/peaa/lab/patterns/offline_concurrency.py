"""Offline concurrency: locks across user sessions, not OS threads.

أقفال بين جلسات المستخدمين على نفس البيانات، مش خيوط داخل العملية.
"""

from __future__ import annotations

from peaa.lab.lease_app.db import fresh
from peaa.lab.registry import register


class Conflict(RuntimeError):
    pass


class Locked(RuntimeError):
    pass


def save_with_version(conn, lease_id: int, status: str, expected_version: int) -> None:
    cur = conn.execute(
        """
        UPDATE leases
        SET status = ?, version = version + 1
        WHERE id = ? AND version = ?
        """,
        (status, lease_id, expected_version),
    )
    if cur.rowcount != 1:
        raise Conflict(f"lease {lease_id} version {expected_version} lost")
    conn.commit()


@register("optimistic_offline_lock")
def demo_optimistic() -> None:
    conn = fresh()
    version_a = conn.execute("SELECT version FROM leases WHERE id = 1").fetchone()["version"]
    version_b = version_a
    save_with_version(conn, 1, "billed", version_a)
    try:
        save_with_version(conn, 1, "returned", version_b)
    except Conflict as exc:
        print("optimistic_offline_lock", exc)


def acquire(conn, owner: str, lease_id: int) -> None:
    row = conn.execute(
        "SELECT owner FROM offline_locks WHERE aggregate = 'lease' AND aggregate_id = ?",
        (lease_id,),
    ).fetchone()
    if row and row["owner"] != owner:
        raise Locked(f"held by {row['owner']}")
    conn.execute(
        """
        INSERT INTO offline_locks (aggregate, aggregate_id, owner, expires_at)
        VALUES ('lease', ?, ?, '2099-01-01')
        ON CONFLICT(aggregate, aggregate_id) DO UPDATE SET owner = excluded.owner
        """,
        (lease_id, owner),
    )
    conn.commit()


@register("pessimistic_offline_lock")
def demo_pessimistic() -> None:
    conn = fresh()
    acquire(conn, "session-a", 1)
    try:
        acquire(conn, "session-b", 1)
    except Locked as exc:
        print("pessimistic_offline_lock", exc)


@register("coarse_grained_lock")
def demo_coarse() -> None:
    """Lock the lease root; lines ride along. قفل الأب يغطي البنود."""
    conn = fresh()
    acquire(conn, "session-a", 1)
    lines = conn.execute("SELECT id FROM lease_lines WHERE lease_id = 1").fetchall()
    print("coarse_grained_lock root held, lines covered", [r["id"] for r in lines])


class ImplicitLeaseEditor:
    """The mapper takes the lock so the caller does not. القفل داخل المابر."""

    def __init__(self, conn, owner: str) -> None:
        self.conn = conn
        self.owner = owner

    def change_status(self, lease_id: int, status: str) -> None:
        acquire(self.conn, self.owner, lease_id)
        version = self.conn.execute("SELECT version FROM leases WHERE id = ?", (lease_id,)).fetchone()["version"]
        save_with_version(self.conn, lease_id, status, version)


@register("implicit_lock")
def demo_implicit() -> None:
    conn = fresh()
    ImplicitLeaseEditor(conn, "session-a").change_status(1, "billed")
    owner = conn.execute("SELECT owner FROM offline_locks WHERE aggregate_id = 1").fetchone()["owner"]
    status = conn.execute("SELECT status FROM leases WHERE id = 1").fetchone()["status"]
    print("implicit_lock", owner, status)
