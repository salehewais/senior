"""Alertmanager webhook sink. Writes one JSON line per alert to stdout.

No email, no secret, and no call out of this process. docker logs is the record.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length) if length else b""
        try:
            body = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            body = {}
        alerts = body.get("alerts", []) if isinstance(body, dict) else []
        for alert in alerts:
            if not isinstance(alert, dict):
                continue
            labels = alert.get("labels") if isinstance(alert.get("labels"), dict) else {}
            annotations = alert.get("annotations") if isinstance(alert.get("annotations"), dict) else {}
            print(
                json.dumps(
                    {
                        "status": alert.get("status"),
                        "alertname": labels.get("alertname"),
                        "severity": labels.get("severity"),
                        "summary": annotations.get("summary"),
                        "description": annotations.get("description"),
                    }
                ),
                flush=True,
            )
        self.send_response(204)
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
