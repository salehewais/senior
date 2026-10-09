"""Tiny upstream for the gateway live check. It records which headers arrived."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:  # noqa: N802
        self._respond()

    def do_POST(self) -> None:  # noqa: N802
        self._respond()

    def do_PATCH(self) -> None:  # noqa: N802
        self._respond()

    def _respond(self) -> None:
        body = json.dumps(
            {
                "upstream": os.environ.get("UPSTREAM_NAME", "unknown"),
                "path": self.path.split("?", 1)[0],
                "x-user-role": self.headers.get("X-User-Role"),
                "x-user-id": self.headers.get("X-User-Id"),
                "x-internal-token": self.headers.get("X-Internal-Token"),
                "authorization_present": self.headers.get("Authorization") is not None,
                "x-correlation-id": self.headers.get("X-Correlation-Id"),
            }
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("X-Upstream-Name", os.environ.get("UPSTREAM_NAME", "unknown"))
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: object) -> None:
        super().log_message("%s", args[0] if args else fmt)


def main() -> None:
    port = int(os.environ.get("PORT", "8000"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
