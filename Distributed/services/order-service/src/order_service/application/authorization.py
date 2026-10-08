"""Role and ownership checks. The domain state machine is a separate gate and still runs."""

from __future__ import annotations

from order_service.application.actor import Actor
from order_service.domain.entities.order import Order
from order_service.domain.exceptions import ForbiddenError
from order_service.domain.roles import Role

_STAFF = (Role.ADMIN, Role.MANAGER)


def require_role(actor: Actor, *allowed: Role) -> None:
    if actor.role not in allowed:
        raise ForbiddenError("You do not have access to this resource.")


def can_view_order(actor: Actor, order: Order) -> bool:
    if actor.role in _STAFF:
        return True
    return actor.role == Role.CUSTOMER and actor.account_id == order.customer_id.value


def cancel_reason_for(actor: Actor, requested: str) -> str:
    """A customer may only cancel as themselves. Staff may record a staff reason.

    The check happens before the state machine so a disallowed reason is 403, not a
    domain validation error the client could satisfy by trying another string they
    are not allowed to use.
    """

    if actor.role == Role.CUSTOMER:
        if requested != "customer_request":
            raise ForbiddenError("That cancel reason is not allowed for your role.")
        return "customer_request"
    if actor.role in _STAFF:
        return requested
    raise ForbiddenError("You do not have access to this resource.")
