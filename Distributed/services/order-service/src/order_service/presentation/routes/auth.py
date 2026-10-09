"""Public auth routes. Do not log the body: it contains a password or a refresh secret."""

import uuid

from fastapi import APIRouter, Request, Response

from order_service.application.use_cases.auth import LoginAccount, LogoutSession, RefreshSession, RegisterAccount
from order_service.presentation.client_address import client_ip
from order_service.presentation.dependencies import UnitOfWorkDep
from order_service.presentation.schemas import LoginBody, RefreshTokenBody, RegisterBody, TokenResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _services(request: Request) -> tuple[object, object, object, object]:
    return (
        request.app.state.clock,
        request.app.state.password_hasher,
        request.app.state.token_issuer,
        request.app.state.refresh_tokens,
    )


def _ids(request: Request) -> tuple[uuid.UUID, uuid.UUID]:
    return request.state.correlation_id, request.state.request_id


@router.post("/register", status_code=201)
def register(body: RegisterBody, request: Request, uow: UnitOfWorkDep) -> TokenResponse:
    request.app.state.rate_limiter.consume_register(ip=client_ip(request))
    clock, passwords, tokens, refresh_tokens = _services(request)
    correlation_id, causation_id = _ids(request)
    pair = RegisterAccount(clock, passwords, tokens, refresh_tokens).execute(
        uow,
        email=body.email,
        display_name=body.display_name,
        password=body.password,
        correlation_id=correlation_id,
        causation_id=causation_id,
    )
    return TokenResponse(
        access_token=pair.access_token,
        refresh_token=pair.refresh_token,
        expires_in=pair.expires_in,
    )


@router.post("/login")
def login(body: LoginBody, request: Request, uow: UnitOfWorkDep) -> TokenResponse:
    request.app.state.rate_limiter.consume_login(ip=client_ip(request), email=body.email)
    clock, passwords, tokens, refresh_tokens = _services(request)
    pair = LoginAccount(clock, passwords, tokens, refresh_tokens).execute(
        uow,
        email=body.email,
        password=body.password,
    )
    return TokenResponse(
        access_token=pair.access_token,
        refresh_token=pair.refresh_token,
        expires_in=pair.expires_in,
    )


@router.post("/refresh")
def refresh(body: RefreshTokenBody, request: Request, uow: UnitOfWorkDep) -> TokenResponse:
    clock, _passwords, tokens, refresh_tokens = _services(request)
    pair = RefreshSession(clock, tokens, refresh_tokens).execute(uow, refresh_token=body.refresh_token)
    return TokenResponse(
        access_token=pair.access_token,
        refresh_token=pair.refresh_token,
        expires_in=pair.expires_in,
    )


@router.post("/logout", status_code=204)
def logout(body: RefreshTokenBody, request: Request, uow: UnitOfWorkDep) -> Response:
    clock, _passwords, _tokens, refresh_tokens = _services(request)
    LogoutSession(clock, refresh_tokens).execute(uow, refresh_token=body.refresh_token)
    return Response(status_code=204)
