"""Flask notification service. Owns notification_db and does not open order_db."""

from notification_service.factory import create_app

__all__ = ["create_app"]
