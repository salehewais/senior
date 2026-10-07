"""Metadata mapping, query object, repository. ميتاداتا واستعلام ومستودع."""

from __future__ import annotations

from peaa.lab.lease_app.db import fresh
from peaa.lab.registry import register

LEASE_META = {
    "table": "leases",
    "fields": {
        "id": "id",
        "customer_id": "customer_id",
        "status": "status",
    },
}


class MetaMapper:
    def __init__(self, conn, meta: dict) -> None:
        self.conn = conn
        self.meta = meta

    def find(self, row_id: int) -> dict:
        cols = ", ".join(self.meta["fields"].values())
        row = self.conn.execute(
            f"SELECT {cols} FROM {self.meta['table']} WHERE id = ?",
            (row_id,),
        ).fetchone()
        return {attr: row[column] for attr, column in self.meta["fields"].items()}


@register("metadata_mapping")
def demo_metadata_mapping() -> None:
    conn = fresh()
    print("metadata_mapping", MetaMapper(conn, LEASE_META).find(1))


class Query:
    """Criteria that compile to SQL. شروط تتحول لاستعلام."""

    def __init__(self, table: str) -> None:
        self.table = table
        self._where: list[tuple[str, object]] = []

    def eq(self, column: str, value: object) -> Query:
        if column not in {"status", "customer_id", "id"}:
            raise ValueError(column)
        self._where.append((column, value))
        return self

    def sql(self) -> tuple[str, list]:
        clause = " AND ".join(f"{col} = ?" for col, _ in self._where) or "1=1"
        params = [value for _, value in self._where]
        return f"SELECT id, status FROM {self.table} WHERE {clause}", params


@register("query_object")
def demo_query_object() -> None:
    conn = fresh()
    sql, params = Query("leases").eq("status", "active").sql()
    rows = conn.execute(sql, params).fetchall()
    print("query_object", [(r["id"], r["status"]) for r in rows])


class LeaseRepository:
    """Collection-like access. وصول يشبه مجموعة مش استعلام مبعثر."""

    def __init__(self, conn) -> None:
        self.conn = conn

    def active(self) -> list[dict]:
        rows = self.conn.execute("SELECT id, status FROM leases WHERE status = 'active'").fetchall()
        return [dict(r) for r in rows]

    def get(self, lease_id: int) -> dict:
        return dict(self.conn.execute("SELECT id, status FROM leases WHERE id = ?", (lease_id,)).fetchone())


@register("repository")
def demo_repository() -> None:
    conn = fresh()
    repo = LeaseRepository(conn)
    print("repository", repo.active(), repo.get(1)["status"])
