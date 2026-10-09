from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = (
        "postgresql+psycopg://order_service:order_service@localhost:5432/order_db"
    )
    # A request must not wait forever on a quiet network or a stuck query.
    db_connect_timeout_seconds: int = 5
    db_statement_timeout_ms: int = 10000
    # PEM text or file paths. Both empty means auth routes answer 503 instead of signing.
    jwt_private_key_pem: str = ""
    jwt_public_key_pem: str = ""
    jwt_private_key_path: str = ""
    jwt_public_key_path: str = ""
    # Empty means internal fulfillment routes answer 503 instead of accepting any caller.
    internal_service_token: str = ""
    # Local placeholder, same standard as the Postgres password. Not a shared credential.
    rabbitmq_url: str = "amqp://order_service:order_service@127.0.0.1:5672/%2F"
    # Connect, declare, publish confirm, and consumer socket calls stop after this.
    rabbitmq_timeout_seconds: float = 5.0
    # Outbox publisher process. The API does not use these to talk to RabbitMQ.
    outbox_poll_interval_seconds: float = 1.0
    outbox_batch_size: int = 100
    # Broker confirms that failed. After this many, the row is status=failed and is not retried.
    # Same count as the consumer retry budget. A failed outbox row is not a consumer DLQ message.
    outbox_max_attempts: int = 5
    # Local placeholder. No password: the Compose port is bound to 127.0.0.1 only.
    redis_url: str = "redis://127.0.0.1:6379/0"
    # A hung Redis must fail the command. None would block the request until the socket dies.
    redis_socket_connect_timeout_seconds: float = 1.0
    redis_socket_timeout_seconds: float = 1.0
    # Short on purpose. A stale fill after invalidation lives only this long.
    product_cache_ttl_seconds: int = 30
    # Laptop demo. Shared across API processes because the counters live in Redis.
    login_rate_limit: int = 5
    register_rate_limit: int = 5
    order_create_rate_limit: int = 10
    rate_limit_window_seconds: int = 60
    # In-flight duplicate suppressor only. After this, a retry can create another order.
    order_create_lock_ttl_seconds: int = 15
    # Retention CronJob. Terminal orders older than this many days, in committed batches.
    order_retention_days: int = 365
    order_retention_batch_size: int = 100
    order_retention_max_batches: int = 20


@lru_cache
def get_settings() -> Settings:
    return Settings()
