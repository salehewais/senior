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


@lru_cache
def get_settings() -> Settings:
    return Settings()
