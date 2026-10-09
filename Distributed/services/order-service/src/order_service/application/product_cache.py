"""Catalog read cache. Orders are not cached. The charged price is read from the product row."""

from __future__ import annotations

import uuid
from typing import Protocol

from order_service.application.dto import ProductView


class ProductCache(Protocol):
    def get_product(self, product_id: uuid.UUID) -> ProductView | None: ...

    def put_product(self, view: ProductView) -> None: ...

    def get_list(self, *, limit: int, offset: int) -> list[ProductView] | None: ...

    def put_list(self, views: list[ProductView], *, limit: int, offset: int) -> None: ...

    def invalidate(self, product_id: uuid.UUID) -> None: ...
