"""Process entrypoint for the HTTP API."""

from __future__ import annotations

from notification_service.config import http_port
from notification_service.factory import create_app


def main() -> None:
    app = create_app()
    app.run(host="0.0.0.0", port=http_port(), threaded=True)


if __name__ == "__main__":
    main()
