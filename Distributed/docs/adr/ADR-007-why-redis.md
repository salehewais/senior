# ADR-007: Why Redis

**Status: Phase 0 design; not implemented.** Accepted for this learning project.

## Context

Product reads will be more frequent than catalog writes. Several API replicas, when they exist, need a shared counter for login and order-create limits. Traefik's built-in rate limit is per process, so it cannot be the only limit once two gateway or API replicas are running.

We already have Postgres. Putting hot, rebuildable keys there works and adds write traffic and vacuum cost for data we are allowed to lose.

## Decision

Use Redis for:

- A TTL cache of product read models in the order service.
- Shared rate-limit counters for login and order creation.

Redis is not the source of truth. Orders, outbox rows, refresh-token hashes, HTTP idempotency keys, and processed event IDs stay in Postgres.

If Redis is down, product reads fall through to `order_db`. Auth and order-create limits fail closed with 503 so an outage does not become an unlimited credential-stuffing window.

The coarse per-IP limit at Traefik stays in memory as a cheap shield in front of a single replica. It is not the shared budget.

## Alternatives

| Alternative | Why it lost |
| --- | --- |
| Cache only in process memory | Correct and simple for one replica. Wrong as soon as two replicas should see one login budget, and cold on every deploy. |
| Postgres for counters | Durable in a way we do not need, and it puts abuse traffic onto the same database as orders. |
| Redis as a primary store for carts or orders | A flush or an eviction policy then deletes sales. The "cache" label would be a lie. |
| No cache and no shared limit | Honest for the first laptop demo. The moment Phase 18 starts a second replica, login limits silently multiply by the replica count. Deciding the tool now stops that surprise. |

## Consequences

- Every cached product can be stale until the TTL or until a `ProductUpdated` invalidates the key. The order line still copies the price at create time from the database, not from a cache value the client sent. Implementers should read the price from `order_db` inside the create transaction even if the HTTP GET was cached. The cache is for reads, not for the price that will be charged.
- Fail-closed limits make Redis a dependency of login. That is intentional and narrower than making Redis a dependency of every GET.
- Redis data is excluded from backups. A restore runbook that loads a Redis dump is a bug.
- One more process to run in Compose. The lesson is worth the process only if nobody promotes it to a system of record. This ADR is the thing to quote in review when that patch appears.
- Rate-limit algorithms (fixed window versus sliding window) can wait until implementation. The storage decision should not wait, because it changes the failure mode.

## What happens without this decision

Either every replica has its own limit, and the real budget is N times what you configured, or every product read hits Postgres, which is fine at classroom volume and teaches nothing about a hot key. We take Redis so the failure mode ("it is gone, reads still work, login pauses") is explicit.
