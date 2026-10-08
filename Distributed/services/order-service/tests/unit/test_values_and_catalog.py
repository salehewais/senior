from pathlib import Path

import pytest

from order_service.domain.entities.catalog import Customer, Product
from order_service.domain.entities.inventory_snapshot import InventorySnapshot
from order_service.domain.exceptions import DomainValidationError
from order_service.domain.ids import ProductId, uuid7
from order_service.domain.value_objects import Money, Quantity

NOW_IMPORTS = (
    "fastapi",
    "sqlalchemy",
    "psycopg",
    "alembic",
    "redis",
    "pika",
)


def test_domain_package_does_not_import_frameworks() -> None:
    root = Path(__file__).resolve().parents[2] / "src" / "order_service" / "domain"
    for path in root.rglob("*.py"):
        text = path.read_text()
        for banned in NOW_IMPORTS:
            assert banned not in text, f"{path.name} mentions {banned}"


def test_money_rejects_floats_and_negative_amounts() -> None:
    with pytest.raises(DomainValidationError):
        Money(1.5, "USD")  # type: ignore[arg-type]
    with pytest.raises(DomainValidationError):
        Money(True, "USD")  # type: ignore[arg-type]
    with pytest.raises(DomainValidationError):
        Money(-1, "USD")
    with pytest.raises(DomainValidationError):
        Money(100, "usd")
    assert Money(1999, "USD").as_dict() == {"amount_minor": 1999, "currency": "USD"}


def test_line_quantity_must_be_positive_and_stock_may_be_zero() -> None:
    with pytest.raises(DomainValidationError):
        Quantity.of_line(0)
    assert Quantity.of_stock(0).value == 0
    with pytest.raises(DomainValidationError):
        Quantity.of_stock(-1)


def test_uuid7_sets_the_version_nibble() -> None:
    assert uuid7().version == 7


def test_product_update_is_a_new_snapshot_version() -> None:
    import uuid
    from datetime import UTC, datetime

    product = Product.create(
        sku=" mug-01 ",
        name="Mug",
        unit_price=Money(1500, "USD"),
        now=datetime(2026, 10, 8, tzinfo=UTC),
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    assert product.sku == "mug-01"
    assert product.pending_events()[0].event_type == "ProductCreated"
    product.update(
        name="Large mug",
        unit_price=None,
        active=False,
        now=datetime(2026, 10, 8, 1, tzinfo=UTC),
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    updated = product.pending_events()[-1]
    assert updated.event_type == "ProductUpdated"
    assert updated.aggregate_version == 2
    assert updated.active is False


def test_customer_registration_is_customer_updated_version_one() -> None:
    import uuid
    from datetime import UTC, datetime

    customer = Customer.create(
        email="Ada@Example.com",
        display_name="Ada",
        now=datetime(2026, 10, 8, tzinfo=UTC),
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    event = customer.pending_events()[0]
    assert event.event_type == "CustomerUpdated"
    assert event.aggregate_version == 1
    assert event.email == "ada@example.com"


def test_inventory_snapshot_ignores_an_older_version() -> None:
    product_id = ProductId.generate()
    current = InventorySnapshot(
        product_id=product_id,
        sku="MUG-01",
        on_hand=Quantity.of_stock(5),
        reserved=Quantity.of_stock(1),
        warehouse_code="MAIN",
        source_version=3,
    )
    stale = InventorySnapshot(
        product_id=product_id,
        sku="MUG-01",
        on_hand=Quantity.of_stock(9),
        reserved=Quantity.of_stock(0),
        warehouse_code="MAIN",
        source_version=2,
    )
    newer = InventorySnapshot(
        product_id=product_id,
        sku="MUG-01",
        on_hand=Quantity.of_stock(4),
        reserved=Quantity.of_stock(2),
        warehouse_code="MAIN",
        source_version=4,
    )
    assert current.apply(stale) is False
    assert current.on_hand.value == 5
    assert current.apply(newer) is True
    assert current.on_hand.value == 4
    assert current.source_version == 4
