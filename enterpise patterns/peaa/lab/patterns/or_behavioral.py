"""Object-relational behavioral patterns. أنماط سلوك الربط بين الكائن والجدول."""

from __future__ import annotations

from dataclasses import dataclass, field

from peaa.lab.lease_app.db import fresh
from peaa.lab.registry import register


class UnitOfWork:
    """Tracks new, dirty, and deleted objects, then writes them in one commit."""

    def __init__(self, conn) -> None:
        self.conn = conn
        self.new: list[tuple] = []
        self.dirty: list[tuple] = []
        self.deleted: list[int] = []

    def register_new(self, lease_id: int, customer_id: int, status: str) -> None:
        self.new.append((lease_id, customer_id, status))

    def register_dirty(self, lease_id: int, status: str) -> None:
        self.dirty.append((lease_id, status))

    def register_deleted(self, lease_id: int) -> None:
        self.deleted.append(lease_id)

    def commit(self) -> None:
        for lease_id, customer_id, status in self.new:
            self.conn.execute(
                "INSERT INTO leases (id, customer_id, status, version) VALUES (?, ?, ?, 0)",
                (lease_id, customer_id, status),
            )
        for lease_id, status in self.dirty:
            self.conn.execute("UPDATE leases SET status = ? WHERE id = ?", (status, lease_id))
        for lease_id in self.deleted:
            self.conn.execute("DELETE FROM leases WHERE id = ?", (lease_id,))
        self.conn.commit()
        self.new.clear()
        self.dirty.clear()
        self.deleted.clear()


@register("unit_of_work")
def demo_unit_of_work() -> None:
    conn = fresh()
    uow = UnitOfWork(conn)
    uow.register_dirty(1, "billed")
    uow.register_new(9, 2, "draft")
    uow.commit()
    rows = conn.execute("SELECT id, status FROM leases ORDER BY id").fetchall()
    print("unit_of_work", [(r["id"], r["status"]) for r in rows])


class IdentityMap:
    """One in-memory object per database id. كائن واحد في الذاكرة لكل مفتاح."""

    def __init__(self, conn) -> None:
        self.conn = conn
        self._cache: dict[int, dict] = {}

    def get(self, lease_id: int) -> dict:
        if lease_id not in self._cache:
            row = self.conn.execute("SELECT * FROM leases WHERE id = ?", (lease_id,)).fetchone()
            self._cache[lease_id] = dict(row)
        return self._cache[lease_id]


@register("identity_map")
def demo_identity_map() -> None:
    conn = fresh()
    ident = IdentityMap(conn)
    first = ident.get(1)
    second = ident.get(1)
    first["status"] = "touched"
    print("identity_map same object", first is second, second["status"])


@dataclass
class LazyLease:
    """Lines load on first touch. البنود تتحمل عند أول استخدام."""

    conn: object
    lease_id: int
    _lines: list | None = field(default=None, repr=False)

    @property
    def lines(self) -> list:
        if self._lines is None:
            self._lines = self.conn.execute(
                "SELECT asset_id, quantity FROM lease_lines WHERE lease_id = ?",
                (self.lease_id,),
            ).fetchall()
            print("lazy_load fetched", len(self._lines), "lines")
        return list(self._lines)


@register("lazy_load")
def demo_lazy_load() -> None:
    conn = fresh()
    lease = LazyLease(conn, 1)
    print("lazy_load before touch", lease._lines)
    print("lazy_load lines", [(r["asset_id"], r["quantity"]) for r in lease.lines])
    _ = lease.lines
