"""Base patterns used across the leasing labs. أنماط أساس تتكرر في التصميم."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from peaa.lab.lease_app.db import fresh
from peaa.lab.lease_app.money import Money
from peaa.lab.registry import register


class RateGateway:
    """Wraps an awkward outside API. يغلّف واجهة خارجية مزعجة."""

    def monthly_rate_cents(self, asset_name: str) -> int:
        table = {"Flatbed": 50000, "Warehouse lift": 20000}
        return table[asset_name]


@register("gateway")
def demo_gateway() -> None:
    print("gateway", RateGateway().monthly_rate_cents("Flatbed"))


@register("mapper")
def demo_mapper() -> None:
    row = {"id": 1, "status": "active"}
    domain = {"lease_id": row["id"], "state": row["status"]}
    print("mapper", domain)


@dataclass
class DomainObject:
    """Layer supertype. أب مشترك لكل كائنات النطاق."""

    id: int | None = None


@dataclass
class NamedLease(DomainObject):
    status: str = "draft"


@register("layer_supertype")
def demo_layer_supertype() -> None:
    lease = NamedLease(id=1, status="active")
    print("layer_supertype", isinstance(lease, DomainObject), lease.id, lease.status)


class BillingPort(ABC):
    @abstractmethod
    def charge(self, lease_id: int, amount: Money) -> str:
        raise NotImplementedError


class SqliteBilling(BillingPort):
    def __init__(self, conn) -> None:
        self.conn = conn

    def charge(self, lease_id: int, amount: Money) -> str:
        self.conn.execute(
            "INSERT INTO invoices (lease_id, amount_cents, currency) VALUES (?, ?, ?)",
            (lease_id, amount.cents, amount.currency),
        )
        self.conn.commit()
        return "stored"


@register("separated_interface")
def demo_separated_interface() -> None:
    port: BillingPort = SqliteBilling(fresh())
    print("separated_interface", port.charge(1, Money(90000)))


class Registry:
    """Service locator. مكان واحد تلاقي منه البوابات — استخدمه بحذر."""

    def __init__(self) -> None:
        self._services: dict[str, object] = {}

    def put(self, name: str, service: object) -> None:
        self._services[name] = service

    def get(self, name: str) -> object:
        return self._services[name]


@register("registry")
def demo_registry() -> None:
    reg = Registry()
    reg.put("rates", RateGateway())
    print("registry", reg.get("rates").monthly_rate_cents("Warehouse lift"))  # type: ignore[attr-defined]


@dataclass(frozen=True)
class DateRange:
    start: str
    end: str

    def includes(self, day: str) -> bool:
        return self.start <= day <= self.end


@register("value_object")
def demo_value_object() -> None:
    a = DateRange("2026-01-01", "2026-01-31")
    b = DateRange("2026-01-01", "2026-01-31")
    print("value_object", a == b, a.includes("2026-01-15"))


@register("money")
def demo_money() -> None:
    total = Money(50000) + Money(20000) * 2
    print("money", total)
    try:
        _ = Money(1, "EUR") + Money(1, "USD")
    except ValueError as exc:
        print("money rejected", exc)


class MissingCustomer:
    """Special case instead of None. حالة خاصة بدل None."""

    id = None
    name = "Unknown customer"

    def label(self) -> str:
        return self.name


@register("special_case")
def demo_special_case() -> None:
    conn = fresh()
    row = conn.execute("SELECT name FROM customers WHERE id = 999").fetchone()
    customer = MissingCustomer() if row is None else row
    print("special_case", customer.label())


class BillingPlugin(ABC):
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError


class ProratePlugin(BillingPlugin):
    def name(self) -> str:
        return "prorate"


class FlatPlugin(BillingPlugin):
    def name(self) -> str:
        return "flat"


PLUGINS: dict[str, type[BillingPlugin]] = {
    "prorate": ProratePlugin,
    "flat": FlatPlugin,
}


@register("plugin")
def demo_plugin() -> None:
    chosen = PLUGINS["prorate"]()
    print("plugin", chosen.name())


class BillingStub(BillingPort):
    def __init__(self) -> None:
        self.calls: list[tuple[int, int]] = []

    def charge(self, lease_id: int, amount: Money) -> str:
        self.calls.append((lease_id, amount.cents))
        return "stub-ok"


@register("service_stub")
def demo_service_stub() -> None:
    stub = BillingStub()
    print("service_stub", stub.charge(1, Money(90000)), stub.calls)


@register("record_set")
def demo_record_set() -> None:
    conn = fresh()
    record_set = [
        dict(r)
        for r in conn.execute(
            "SELECT asset_id, quantity FROM lease_lines WHERE lease_id = 1"
        ).fetchall()
    ]
    quantity = sum(row["quantity"] for row in record_set)
    print("record_set", record_set, "qty", quantity)
