# Security

**Status: Phase 2 implements accounts, argon2id password hashes, RS256 access tokens, and hashed refresh tokens in the order service. Phase 9 adds Redis login, register, and order-create limits that fail closed when Redis is down. Phase 10 adds the Traefik gateway: storefront CORS, a coarse in-memory per-IP limit, correlation IDs, and an RS256 signature check on protected routes. KMS and refresh-token family revocation are not implemented.**

This is the threat model for a learning system that still refuses to trust the browser. It is not a penetration test and not a production sign-off.

## Assets

- Accounts and password hashes in `order_db`
- Order contents and customer email
- The signing key for access tokens
- Broker credentials that can publish events
- Database roles that can write each service's tables

Redis contents are rebuildable. They are still not a place to put tokens.

## Identity

Roles are `customer`, `admin`, and `manager`. They live on the `accounts` row. Login loads the role from that row and puts it in the access token. The token is signed with RS256. The private key stays with the order service. The gateway and the reporting service get the public key only.

Why RS256: a shared HMAC secret would have to be copied into every verifier, and any one of them could mint tokens. A public key lets Traefik and Django check signatures without the ability to issue them.

Access token lifetime: 15 minutes. Refresh token lifetime: 7 days, rotated on every refresh, stored as a hash in `order_db`. Logout deletes or revokes that hash. An access token remains valid until it expires; that is the usual JWT trade-off. Fifteen minutes bounds the damage of a stolen access token. We do not build a synchronous denylist of every access token in Phase 0.

> **Learning simplification.** Key pair mounted from a local file generated outside git. No KMS.
> **Production would require.** Key storage in a KMS or vault, rotation with overlapping public keys, and a way to revoke refresh-token families after theft.

### Do not trust the client

- Ignore `role` in JSON bodies.
- The gateway strips inbound `X-User-Id` and `X-User-Role` (and similar, including `X-Internal-Token`). It does not copy the verified subject or role onto a new header. The services already derive identity from the JWT, and a header they do not read must not become a second source of truth.
- Services still verify the JWT signature. A request that reaches a published port and bypasses the gateway must not become admin because a header said so. The order service does not emit browser CORS; the gateway does. Skipping Traefik does not skip the Bearer check.
- Prices, totals, and status strings from the client are not written onto the order. The server computes them or rejects them.
- Internal fulfillment routes use a service credential, not a customer token, and are not on the public ingress. Phase 2 compares `X-Internal-Token` to `INTERNAL_SERVICE_TOKEN` in constant time and returns 503 if that variable is unset. A long-lived shared header is a learning stand-in. Production would use a private network plus a rotated credential or mTLS.

What happens if we trust a client role: any customer sends `"role": "admin"` and reads every order. Detection after the fact is an audit of who fetched `/customers`. Recovery is to revoke refresh tokens and fix the check. The design avoids needing that incident.

Authorization sits in the application use case, not only in the router. The domain still rejects illegal transitions even if an admin asks. Admin is not a bypass of the state machine.

## Gateway duties

- TLS is the production requirement at the public door. Local Compose may use HTTP. That is a simplification, and it means tokens travel in the clear on localhost. Do not point that HTTP port at a shared network and call it fine.
- CORS allows the storefront origin, not `*`, once credentials or tokens are in play. A reflection of any origin is a bug.
- Coarse rate limit per IP at Traefik.
- Login, register, and order-create limits in the order service, backed by Redis, failing closed (503) if Redis is down so those routes cannot be sprayed without a limit during a cache outage. Catalog reads fall through to Postgres.
- Request body size limits so a huge payload cannot pin a worker.

## Data handling

- Passwords hashed with a slow hash (argon2id or bcrypt). No reversible encryption of passwords.
- Events carry email and display name where the catalog says so. They do not carry password hashes, refresh tokens, or card data.
- Payment calls send card data only if a later phase truly must; the preferred shape is a provider token or a test double that never sees a PAN. Phase 16 should use a fake provider in learning, not live card numbers.
- Logs omit authorization headers and request bodies on auth routes.
- Errors returned to clients omit SQL and stack traces.

## Network

| Path | Who can open it |
| --- | --- |
| Gateway HTTP | The developer on the laptop, later the ingress |
| Postgres, Redis, RabbitMQ | Services on the internal network. Not the public internet. |
| Odoo UI | Private port for learning, not the storefront origin |
| Internal fulfillment HTTP | Odoo module to order service, not the browser |
| Metrics | Internal scrape network. Not the public gateway. |

Database roles cannot log into another database. That is the enforcement behind [database.md](database.md). Documentation alone will not stop a DSN typo; grants will.

## Secrets

No passwords, JWT private keys, or broker credentials are committed. Examples use variable names. If a secret lands in git, the response is to rotate it, not only to delete the file in a later commit.

## What this phase does not do

No OAuth authorization-server build, no OIDC federation with Odoo, no mTLS mesh, no web application firewall. Odoo staff login stays Odoo's own session for the ERP UI. Unifying those identities is a later product decision, not a hidden Phase 0 requirement.

Customer accounts and ERP users are different. A storefront JWT does not log you into Odoo.

## Related documents

- [api.md](api.md)
- [ADR-012](adr/ADR-012-why-api-gateway.md)
- [ADR-007](adr/ADR-007-why-redis.md)
