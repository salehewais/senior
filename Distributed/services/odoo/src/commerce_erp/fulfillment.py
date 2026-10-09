"""Ask the order service to move a confirmed order through fulfillment.

One HTTP call, with a timeout. A 409 means the previous milestone is not
applied yet. The caller retries later. This function does not loop, and it
does not publish OrderShipped or any other order-status event.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

MILESTONES = ("processing", "shipped", "delivered")


class MilestoneResult(Enum):
    ACCEPTED = "accepted"
    NOT_READY = "not_ready"
    REJECTED = "rejected"
    UNAVAILABLE = "unavailable"


class MissingToken(Exception):
    """INTERNAL_SERVICE_TOKEN is unset. Do not call the order service."""


@dataclass(frozen=True, slots=True)
class FulfillmentResponse:
    result: MilestoneResult
    http_status: int


def post_milestone(
    *,
    order_service_url: str,
    token: str,
    order_id: str,
    milestone: str,
    tracking_reference: str | None = None,
    timeout: float,
    opener=urlopen,
) -> FulfillmentResponse:
    """POST one milestone. ``opener`` is urllib.request.urlopen, or a test double."""

    if timeout <= 0:
        raise ValueError("order service timeout must be greater than zero")
    if not token:
        raise MissingToken("INTERNAL_SERVICE_TOKEN is unset")
    if milestone not in MILESTONES:
        raise ValueError(f"Unknown milestone {milestone}")
    url = f"{order_service_url.rstrip('/')}/api/v1/internal/orders/{order_id}/{milestone}"
    body: dict[str, str] = {}
    if milestone == "shipped" and tracking_reference:
        body["tracking_reference"] = tracking_reference
    request = Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Internal-Token": token,
        },
        method="POST",
    )
    try:
        with opener(request, timeout=timeout) as response:
            status = getattr(response, "status", None) or response.getcode()
    except HTTPError as exc:
        if exc.code == 409:
            return FulfillmentResponse(MilestoneResult.NOT_READY, exc.code)
        if exc.code >= 500:
            return FulfillmentResponse(MilestoneResult.UNAVAILABLE, exc.code)
        return FulfillmentResponse(MilestoneResult.REJECTED, exc.code)
    except (TimeoutError, URLError, OSError):
        return FulfillmentResponse(MilestoneResult.UNAVAILABLE, 0)
    if 200 <= status < 300:
        return FulfillmentResponse(MilestoneResult.ACCEPTED, status)
    return FulfillmentResponse(MilestoneResult.REJECTED, status)
