"""Growing lease walkthrough for Part 1. قصة الإيجار تكبر مع فصول السرد."""

from __future__ import annotations

from peaa.lab.lease_app.db import fresh
from peaa.lab.patterns.distribution import RemoteLeaseFacade
from peaa.lab.patterns.domain_logic import BillingService, LeaseTable, load_domain_lease
from peaa.lab.patterns.offline_concurrency import save_with_version
from peaa.lab.registry import register


@register("layering")
def demo_layering() -> None:
    """Presentation asks a service; the service uses the domain; SQL stays below."""
    conn = fresh()
    total = BillingService(conn).bill(1)
    print("presentation shows", total)
    print("invoice rows", conn.execute("SELECT COUNT(*) AS n FROM invoices").fetchone()["n"])


@register("organizing_domain")
def demo_organizing() -> None:
    conn = fresh()
    model_total = load_domain_lease(conn, 1).monthly_total()
    rows = conn.execute(
        """
        SELECT a.monthly_rate_cents, l.quantity
        FROM lease_lines l JOIN assets a ON a.id = l.asset_id
        WHERE l.lease_id = 1
        """
    ).fetchall()
    table_total = LeaseTable([dict(r) for r in rows]).monthly_total()
    print("organizing_domain model", model_total, "table", table_total)


@register("mapping_preview")
def demo_mapping() -> None:
    from peaa.lab.patterns.data_source import LeaseMapper

    conn = fresh()
    lease = LeaseMapper(conn).find(1)
    print("mapping_preview", lease.id, lease.can_bill())


@register("web_preview")
def demo_web() -> None:
    conn = fresh()
    lease = conn.execute("SELECT id, status FROM leases WHERE id = 1").fetchone()
    print(f"web_preview view: Lease #{lease['id']} is {lease['status']}")


@register("offline_preview")
def demo_offline_preview() -> None:
    conn = fresh()
    version = conn.execute("SELECT version FROM leases WHERE id = 1").fetchone()["version"]
    save_with_version(conn, 1, "billed", version)
    print("offline_preview version", conn.execute("SELECT version FROM leases WHERE id = 1").fetchone()["version"])
    print("see Part 3 for threads:", "part3-concurrency")


@register("session_preview")
def demo_session_preview() -> None:
    stateless = {"path": "/leases/1"}
    stateful = {"session": "sess-7", "wizard": "confirm"}
    print("session_preview stateless", stateless, "stateful", stateful)


@register("distribution_preview")
def demo_distribution_preview() -> None:
    summary = RemoteLeaseFacade(fresh()).bill_and_summarize(1)
    print("distribution_preview one call", summary.lease_id, summary.amount_cents)


@register("together")
def demo_together() -> None:
    """Domain, then mapper-style read, then one service bill. المسار كامل."""
    conn = fresh()
    lease = load_domain_lease(conn, 1)
    print("domain", lease.monthly_total())
    print("billed", BillingService(conn).bill(1))
