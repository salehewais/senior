"""The direct TCP peer.

Phase 10's gateway is not the only way to reach this process: the learning
port 8000 is still published, so a client could spoof X-Forwarded-For on that
port and walk around the per-IP budget. The header stays untrusted until the
upstream port is no longer public.
"""

from fastapi import Request


def client_ip(request: Request) -> str:
    peer = request.client
    if peer is None or not peer.host:
        return "unknown"
    return peer.host
