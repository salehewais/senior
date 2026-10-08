from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Request

from order_service.application.actor import Actor
from order_service.application.ports import InvalidAccessToken
from order_service.application.unit_of_work import UnitOfWork
from order_service.domain.exceptions import DependencyUnavailableError, UnauthenticatedError
from order_service.infrastructure.security.service_token import service_token_matches


def get_uow(request: Request) -> Iterator[UnitOfWork]:
    uow: UnitOfWork = request.app.state.uow_factory()
    try:
        yield uow
    finally:
        uow.close()


def get_actor(request: Request) -> Actor:
    """Verify the access token here. Use cases still receive the actor and check the role."""

    issuer = request.app.state.token_issuer
    if issuer is None:
        raise DependencyUnavailableError("Token signing keys are not configured.")
    header = request.headers.get("authorization", "")
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise UnauthenticatedError("Authentication is required.")
    try:
        return issuer.parse(token.strip(), now=request.app.state.clock.now())
    except InvalidAccessToken:
        raise UnauthenticatedError("Authentication is required.") from None


def require_internal_token(request: Request) -> None:
    """Customer JWTs are not a credential for fulfillment. Phase 8 replaces this header.

    If INTERNAL_SERVICE_TOKEN is unset the route fails closed with 503. A long-lived
    shared header is a learning stand-in. Production would use a private network plus
    a rotated credential or mTLS.
    """

    expected = request.app.state.internal_service_token
    if not expected:
        raise DependencyUnavailableError("Internal fulfillment is not configured.")
    presented = request.headers.get("x-internal-token", "")
    if not service_token_matches(presented, expected):
        raise UnauthenticatedError("Authentication is required.")


UnitOfWorkDep = Annotated[UnitOfWork, Depends(get_uow)]
ActorDep = Annotated[Actor, Depends(get_actor)]
InternalDep = Annotated[None, Depends(require_internal_token)]
