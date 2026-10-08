import logging
from collections.abc import Callable

from fastapi import FastAPI

from order_service.application.clock import Clock, SystemClock
from order_service.application.ports import AccessTokenIssuer, PasswordHasher, RefreshTokenCodec
from order_service.application.publishing import EventPublisher
from order_service.application.unit_of_work import UnitOfWork
from order_service.infrastructure.database.engine import make_engine, make_session_factory
from order_service.infrastructure.database.unit_of_work import SqlUnitOfWork
from order_service.infrastructure.messaging.publisher import PikaEventPublisher
from order_service.infrastructure.security.keys import load_signing_keys
from order_service.infrastructure.security.passwords import Argon2PasswordHasher
from order_service.infrastructure.security.refresh_tokens import Sha256RefreshTokens
from order_service.infrastructure.security.tokens import RsaAccessTokenIssuer
from order_service.infrastructure.settings import get_settings
from order_service.presentation.cors import install_local_frontend_cors
from order_service.presentation.errors import install_error_handlers, install_middleware
from order_service.presentation.routes.auth import router as auth_router
from order_service.presentation.routes.customers import router as customers_router
from order_service.presentation.routes.health import router as health_router
from order_service.presentation.routes.orders import internal
from order_service.presentation.routes.orders import router as orders_router
from order_service.presentation.routes.products import router as products_router

logger = logging.getLogger("order_service")

_UNSET = object()


def create_app(
    *,
    uow_factory: Callable[[], UnitOfWork] | None = None,
    clock: Clock | None = None,
    engine=None,
    password_hasher: PasswordHasher | None = None,
    token_issuer: AccessTokenIssuer | None | object = _UNSET,
    refresh_tokens: RefreshTokenCodec | None = None,
    internal_service_token: str | None | object = _UNSET,
    event_publisher: EventPublisher | None | object = _UNSET,
) -> FastAPI:
    """HTTP adapter. Business rules live in use cases, not in these routes.

    Pass uow_factory and token_issuer in tests to avoid Postgres and committed keys.
    Pass event_publisher=None in tests so they do not open RabbitMQ.
    The default factory opens order_db, loads the RS256 key pair, and publishes
    with pika after commit. That publish is not the outbox.
    """

    app = FastAPI(
        title="Order service",
        version="0.4.0",
        description=(
            "Phase 4 order service. Access tokens are RS256. After order_db commits, "
            "domain events are published to the commerce.events exchange. "
            "A broker failure does not roll the sale back, and the event can be lost until the outbox. "
            "saga_status stays null until the saga."
        ),
    )
    settings = None
    if uow_factory is None or token_issuer is _UNSET or internal_service_token is _UNSET:
        settings = get_settings()
    if uow_factory is None:
        assert settings is not None
        engine = make_engine(settings)
        sessions = make_session_factory(engine)

        def uow_factory() -> UnitOfWork:
            return SqlUnitOfWork(sessions())

    if token_issuer is _UNSET:
        assert settings is not None
        loaded = load_signing_keys(settings)
        token_issuer = None if loaded is None else RsaAccessTokenIssuer(loaded[0], loaded[1])
    if internal_service_token is _UNSET:
        assert settings is not None
        internal_service_token = settings.internal_service_token.strip() or None
    elif isinstance(internal_service_token, str):
        internal_service_token = internal_service_token.strip() or None
    if event_publisher is _UNSET:
        if settings is None:
            settings = get_settings()
        event_publisher = PikaEventPublisher(settings)

    app.state.uow_factory = uow_factory
    app.state.engine = engine
    app.state.clock = clock or SystemClock()
    app.state.password_hasher = password_hasher or Argon2PasswordHasher()
    app.state.token_issuer = token_issuer
    app.state.refresh_tokens = refresh_tokens or Sha256RefreshTokens()
    app.state.internal_service_token = internal_service_token
    app.state.event_publisher = event_publisher
    install_middleware(app)
    # Added after the correlation middleware so this wrapper is outermost and can
    # answer browser preflight before a route runs. Traefik replaces it in Phase 10.
    install_local_frontend_cors(app)
    install_error_handlers(app)
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(products_router)
    app.include_router(customers_router)
    app.include_router(orders_router)
    app.include_router(internal)
    logger.debug("order service application created")
    return app


app = create_app()
