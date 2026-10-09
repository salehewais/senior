import logging
from collections.abc import Callable

from fastapi import FastAPI
from prometheus_client import make_asgi_app

from order_service.application.clock import Clock, SystemClock
from order_service.application.ports import AccessTokenIssuer, PasswordHasher, RefreshTokenCodec
from order_service.application.rate_limit import RateLimitPolicy
from order_service.application.unit_of_work import UnitOfWork
from order_service.infrastructure.database.engine import make_engine, make_session_factory
from order_service.infrastructure.database.unit_of_work import SqlUnitOfWork
from order_service.infrastructure.redis.catalog_cache import ProductCatalogCache
from order_service.infrastructure.redis.client import RedisClient
from order_service.infrastructure.redis.commands import RedisCommands
from order_service.infrastructure.redis.limiter import RedisRateLimiter
from order_service.infrastructure.redis.order_lock import RedisOrderLock
from order_service.infrastructure.security.keys import load_signing_keys
from order_service.infrastructure.security.passwords import Argon2PasswordHasher
from order_service.infrastructure.security.refresh_tokens import Sha256RefreshTokens
from order_service.infrastructure.security.tokens import RsaAccessTokenIssuer
from order_service.infrastructure.settings import get_settings
from order_service.observability.jsonlog import configure_logging
from order_service.observability.metrics import bind_database_engine
from order_service.observability.tracing import configure_tracing, instrument_fastapi
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
    redis_commands: RedisCommands | object = _UNSET,
    rate_limit_policy: RateLimitPolicy | None = None,
) -> FastAPI:
    """HTTP adapter. Business rules live in use cases, not in these routes.

    Pass uow_factory and token_issuer in tests to avoid Postgres and committed keys.
    The handler writes the business row and the outbox row, then returns.
    It does not open RabbitMQ. A separate publisher process does that.
    """

    app = FastAPI(
        title="Order service",
        version="0.9.0",
        description=(
            "Phase 9 order service. Product reads may come from Redis and are filled from "
            "order_db on a miss. Login, register, and order-create limits live in Redis and "
            "fail closed when it is down. Orders, the outbox, and refresh-token hashes stay "
            "in order_db. saga_status stays null until the saga."
        ),
    )
    settings = None
    if uow_factory is None or token_issuer is _UNSET or internal_service_token is _UNSET or redis_commands is _UNSET:
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

    app.state.uow_factory = uow_factory
    app.state.engine = engine
    app.state.clock = clock or SystemClock()
    app.state.password_hasher = password_hasher or Argon2PasswordHasher()
    app.state.token_issuer = token_issuer
    app.state.refresh_tokens = refresh_tokens or Sha256RefreshTokens()
    app.state.internal_service_token = internal_service_token
    if redis_commands is _UNSET:
        assert settings is not None
        redis_commands = RedisClient(
            settings.redis_url,
            connect_timeout=settings.redis_socket_connect_timeout_seconds,
            socket_timeout=settings.redis_socket_timeout_seconds,
        )
        policy = rate_limit_policy or RateLimitPolicy(
            login_per_minute=settings.login_rate_limit,
            register_per_minute=settings.register_rate_limit,
            order_create_per_minute=settings.order_create_rate_limit,
            window_seconds=settings.rate_limit_window_seconds,
        )
        cache_ttl = settings.product_cache_ttl_seconds
        lock_ttl = settings.order_create_lock_ttl_seconds
    else:
        policy = rate_limit_policy or RateLimitPolicy()
        cache_ttl = 30
        lock_ttl = 15
    app.state.product_cache = ProductCatalogCache(redis_commands, ttl_seconds=cache_ttl)
    app.state.rate_limiter = RedisRateLimiter(redis_commands, policy)
    app.state.order_guard = RedisOrderLock(redis_commands, ttl_seconds=lock_ttl)
    configure_logging("order-service")
    bind_database_engine(engine)
    configure_tracing("order-service", engine)
    install_middleware(app)
    # Browser CORS is Traefik's allow-list (Phase 10). This process does not add
    # Access-Control-Allow-Origin, so a response that already passed the gateway
    # does not grow a second copy of that header. A client that dials a published
    # port and skips Traefik still has to present a Bearer token; the route
    # dependencies verify the signature. A matching Origin is not a credential.
    install_error_handlers(app)
    app.mount("/metrics", make_asgi_app())
    instrument_fastapi(app)
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(products_router)
    app.include_router(customers_router)
    app.include_router(orders_router)
    app.include_router(internal)
    logger.debug("order service application created")
    return app


app = create_app()
