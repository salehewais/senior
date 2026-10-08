# ADR-012: Why an API gateway, and why Traefik

**Status: Phase 0 design; not implemented.** Accepted for this learning project.

## Context

The browser must talk to more than one backend (order service and reporting) and must not learn their internal addresses. Every service would otherwise repeat CORS, request IDs, a coarse rate limit, and a JWT presence check. Those are edge concerns. Order rules are not.

We need the same idea on Compose and, later, on kind. The gateway has to be small enough to run beside a classroom cluster.

## Decision

Put **Traefik** in front of the storefront and the APIs.

Traefik will:

- Route `/api/v1/reports` to reporting and the rest of `/api/v1` to the order service.
- Serve or route the React app.
- Set `X-Correlation-Id`.
- Enforce CORS for the storefront origin.
- Check JWT signatures on protected routes and strip client-supplied identity headers.
- Apply a coarse in-memory rate limit.

Traefik will not contain order logic, and it will not be the only JWT check. Services verify tokens again.

Why Traefik rather than nginx:

- On Compose it can discover routes from container labels. On Kubernetes it is a native ingress controller with Middleware resources for headers, rate limits, and forwarding. One product covers both phases.
- kind does not ship an ingress we are forced to keep. Installing Traefik makes the gateway visible. k3s would have handed us Traefik already, which is convenient and a worse lesson (see [ADR-008](ADR-008-why-kubernetes.md)).
- The configuration we care about (routes, middleware) stays declarative. We do not need a large nginx template language to start.

Services still verify JWTs because a pod IP on the docker network is reachable if someone misplaces a port. The gateway is a policy checkpoint, not a magic barrier.

## Alternatives

| Alternative | Why it lost |
| --- | --- |
| No gateway, browser calls each service | CORS and auth logic fork. Internal hostnames leak into the frontend. A new service means a frontend change just to find it. |
| nginx | A production-proven reverse proxy, and a good choice if the team already operates it. Route and header behavior would be a config file we must rewrite into an ingress annotation or a second config when we reach kind. We would rather carry one gateway concept across both runtimes. If Traefik's middleware model becomes a burden, nginx remains the documented fallback; switching is an ADR update, not a quiet compose edit. |
| Envoy or a full service mesh | More power (retries, mTLS, traffic splitting) than three services need. The mesh would become the project. |
| Kong or a heavy API platform | Plugins and a database for the gateway. We would operate a product to route four prefixes. |
| Application-only middleware, no edge | Correct as a duplicate check, incomplete as the only door. The public entry would be whichever service we remembered to expose. |

## Consequences

- Traefik's in-memory rate limit is per replica. Shared login limits stay in Redis behind the order service ([ADR-007](ADR-007-why-redis.md)). Do not "fix" a bypass by claiming the gateway limit is global.
- JWT verification at the edge needs the public key mounted into Traefik. Rotation means updating that mount and the services together. Document the overlap when rotation exists. Phase 0 only reserves the requirement.
- A misrouted prefix silently sends report traffic to FastAPI, which will 404. Route tests belong in the Compose journey.
- The gateway is a single process in the learning setup. When it is down, public traffic is down, and data is fine. Run it on purpose in the gateway drill in [../failure-scenarios.md](../failure-scenarios.md).
- Internal routes (fulfillment milestones) must not be added to the public router. A review check is part of the decision, because Traefik will happily expose whatever is labeled.
- We accept Traefik-specific Middleware CRDs later. They do not port line-for-line to nginx. That lock-in is small and acknowledged.

## What happens without this decision

Each service grows a slightly different CORS list and a slightly different idea of a correlation id. The React app imports two base URLs and, eventually, a database password someone put in a frontend env file because it was "easier to query reports directly." The gateway exists so that shortcut has nowhere public to attach.
