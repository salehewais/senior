"""Web presentation patterns without a framework. أنماط العرض من غير إطار."""

from __future__ import annotations

import json
from string import Template

from peaa.lab.lease_app.db import fresh
from peaa.lab.registry import register


def _lease(conn):
    return dict(conn.execute("SELECT id, status, customer_id FROM leases WHERE id = 1").fetchone())


@register("mvc")
def demo_mvc() -> None:
    conn = fresh()
    model = _lease(conn)

    def view(lease: dict) -> str:
        return f"Lease #{lease['id']} is {lease['status']}"

    def controller(action: str) -> str:
        if action == "show":
            return view(model)
        raise KeyError(action)

    print("mvc", controller("show"))


@register("page_controller")
def demo_page_controller() -> None:
    """One function per page. دالة لكل صفحة."""
    conn = fresh()

    def show_lease_page() -> str:
        lease = _lease(conn)
        return f"<page>lease {lease['id']}</page>"

    print("page_controller", show_lease_page())


@register("front_controller")
def demo_front_controller() -> None:
    conn = fresh()

    def show(_request):
        return f"show:{_lease(conn)['status']}"

    def bill(_request):
        return "bill:queued"

    routes = {"GET /lease": show, "POST /lease/bill": bill}

    def front(path: str) -> str:
        handler = routes[path]
        return handler({})

    print("front_controller", front("GET /lease"), front("POST /lease/bill"))


@register("template_view")
def demo_template_view() -> None:
    conn = fresh()
    lease = _lease(conn)
    html = Template("Lease $id ($status)").substitute(id=lease["id"], status=lease["status"])
    print("template_view", html)


@register("transform_view")
def demo_transform_view() -> None:
    conn = fresh()
    lease = _lease(conn)

    def to_document(row: dict) -> dict:
        return {"leaseId": row["id"], "state": row["status"]}

    print("transform_view", json.dumps(to_document(lease)))


@register("two_step_view")
def demo_two_step_view() -> None:
    conn = fresh()
    lease = _lease(conn)
    logical = {"title": f"Lease {lease['id']}", "fields": [("status", lease["status"])]}

    def render_text(screen: dict) -> str:
        lines = [screen["title"]]
        lines += [f"{name}: {value}" for name, value in screen["fields"]]
        return "\n".join(lines)

    print("two_step_view")
    print(render_text(logical))


@register("application_controller")
def demo_application_controller() -> None:
    """Wizard flow for returning an asset. مسار خطوات إرجاع الأصل."""
    flow = {
        "start": "choose_asset",
        "choose_asset": "confirm",
        "confirm": "done",
    }
    step = "start"
    seen = [step]
    while step != "done":
        step = flow[step]
        seen.append(step)
    print("application_controller", " -> ".join(seen))
