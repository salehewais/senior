"""One fulfillment call. A 409 is not a retry storm and not an invented transition."""

from __future__ import annotations

from email.message import Message
from urllib.error import HTTPError

import pytest

from commerce_erp.clients.fulfillment import MilestoneResult, MissingToken, post_milestone

ORDER_ID = "018f1c2a-1111-7c11-8a22-222222222222"


class _Response:
    def __init__(self, status: int) -> None:
        self.status = status

    def __enter__(self) -> _Response:
        return self

    def __exit__(self, *args: object) -> bool:
        return False

    def getcode(self) -> int:
        return self.status


class _Opener:
    def __init__(self, *, status: int = 200, error: Exception | None = None) -> None:
        self.status = status
        self.error = error
        self.calls: list[tuple[object, float]] = []

    def __call__(self, request, timeout: float):
        self.calls.append((request, timeout))
        if self.error is not None:
            raise self.error
        return _Response(self.status)


def test_processing_sends_internal_token_once() -> None:
    opener = _Opener()
    result = post_milestone(
        order_service_url="http://127.0.0.1:8000",
        token="local-placeholder",
        order_id=ORDER_ID,
        milestone="processing",
        timeout=5,
        opener=opener,
    )

    assert result.result is MilestoneResult.ACCEPTED
    assert result.http_status == 200
    assert len(opener.calls) == 1
    request, timeout = opener.calls[0]
    assert timeout == 5
    assert request.get_header("X-internal-token") == "local-placeholder"
    assert request.full_url.endswith(f"/api/v1/internal/orders/{ORDER_ID}/processing")


def test_conflict_is_not_retried() -> None:
    opener = _Opener(error=HTTPError("http://orders", 409, "conflict", Message(), None))
    result = post_milestone(
        order_service_url="http://127.0.0.1:8000",
        token="local-placeholder",
        order_id=ORDER_ID,
        milestone="shipped",
        tracking_reference="TRK-100",
        timeout=5,
        opener=opener,
    )

    assert result.result is MilestoneResult.NOT_READY
    assert result.http_status == 409
    assert len(opener.calls) == 1


def test_missing_token_does_not_call() -> None:
    opener = _Opener()
    with pytest.raises(MissingToken):
        post_milestone(
            order_service_url="http://127.0.0.1:8000",
            token="",
            order_id=ORDER_ID,
            milestone="delivered",
            timeout=5,
            opener=opener,
        )
    assert opener.calls == []
