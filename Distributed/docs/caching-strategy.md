# Caching strategy

**Status: Extension Phase 5.** Product get and list stay cache-aside. This page describes that path, the 30 second TTL, and what a Redis error does. It does not add a second cache or a write-through path. The React Native client at `mobile/react-native-app` reads products through that same HTTP API. It does not add a cache.

The sentences below come from the order-service code. The tests in this phase use `FakeRedis`. They do not open a Redis server, and this page does not record a live Redis result.

Replica count, probes, and the Service that shares this cache are [kubernetes.md](kubernetes.md). How the suites are laid out is [testing.md](testing.md). JWT, roles, and the fail-closed limits are [security.md](security.md). Scrape, dashboards, and alerts are [observability.md](observability.md).

## Cache-aside

`GetProduct` and `ListProducts` in `services/order-service/src/order_service/application/use_cases/catalog.py` ask `ProductCatalogCache` first (`services/order-service/src/order_service/infrastructure/redis/catalog_cache.py`). Orders are not cached. The price copied onto an order line is read from the product row in `order_db`.

| Result | What Redis did | What the use case does |
| --- | --- | --- |
| Hit | A stored JSON value parses as a product or a list page | Return that value. `order_db` is not read |
| Miss | The key is absent, or the payload does not parse | Read `order_db`, then `SET` the JSON |
| Error | `RedisUnavailable`: Redis is down, or the command fails before the timeout | Return no cached value. The use case reads `order_db`. A fill that then fails is skipped |

The caller treats an error the same way it treats a miss: the response comes from Postgres. The series are different. An error increments `product_cache_errors_total`. A miss increments `product_cache_misses_total`.

Keys:

| Key | Value |
| --- | --- |
| `catalog:product:{product_id}` | One product JSON document |
| `catalog:list:{limit}:{offset}` | A JSON list of those documents |

The TTL is `product_cache_ttl_seconds` in `services/order-service/src/order_service/infrastructure/settings.py`. The default is 30 seconds. `SET` passes that TTL (`ex` on the Redis client). When the key expires, the next get or list is a miss and reads `order_db` again.

Every order-service API replica uses this same Redis. There is no per-pod product cache.

Login, register, and order create do not use this fallback. Those routes fail closed when Redis is down. The budgets and the 15 second order-create lock are in [security.md](security.md). The lock key is not a product-cache key.

## Invalidation

`CreateProduct` and `UpdateProduct` call `invalidate` after `commit`. `invalidate` deletes that product key and every key under `catalog:list:`.

Redis and Postgres are not one atomic update. The product row commits in `order_db`. The delete is a later Redis command. A crash after the commit and before the delete leaves the previous key in place until the 30 second TTL. A get during that window returns the cached document.

A reader that loaded the old row before the delete can `SET` that old document after the delete. The TTL is the backstop. The delete is not a lock around the fill.

The order service is both the writer and the cache client, and Redis is shared by its replicas. Invalidation stays in that process after commit. This phase does not add a RabbitMQ consumer whose job is to delete the key. Exchanges and retries are [rabbitmq.md](rabbitmq.md).

## Concurrent misses

A get or list that finds no key does not take a lock before reading `order_db`. Two callers can both miss, both read Postgres, and both `SET`. Each `SET` stores one complete JSON document. The later `SET` is the value Redis keeps. There is no single-flight lock. The order-create lock does not cover this path.

## Metrics

Product get and list record one sample per cache read. The names are:

| Series | Type | Labels |
| --- | --- | --- |
| `product_cache_hits_total` | counter | `operation` (`get` or `list`) |
| `product_cache_misses_total` | counter | `operation` |
| `product_cache_errors_total` | counter | `operation` |
| `product_cache_duration_seconds` | histogram | `operation`, `result` (`hit`, `miss`, or `error`) |

`result` on the histogram is the same outcome as the counter. Duration is the time to classify that cache read, including a payload that does not parse. It is not the Postgres query.

The label values are those words. An account id, a product id, and a token are not labels.

The order-service process exposes them on `/metrics`. The existing Prometheus scrape of `order-service:8000` collects them. No second Prometheus was added.

Grafana already provisions `deploy/observability/grafana/dashboards/`. Two of those boards query the new series:

- Dependencies (`dependencies.json`): product-cache hits, misses, errors, and duration p95. The Redis keyspace hit ratio panel on that board still queries `redis_keyspace_hits_total` and `redis_keyspace_misses_total` from the Redis exporter. That ratio is the server keyspace.
- Platform overview (`platform-overview.json`): the same four product-cache queries. The Redis exporter stat on that board remains `up{job="redis"}`.

## Tests

`services/order-service/tests/unit/test_cache_behavior.py` uses `FakeRedis`. The file does not skip when Redis is down.

| Test | What it holds |
| --- | --- |
| `test_stale_product_is_served_when_the_delete_has_not_happened` | After the Postgres price changes, a key that is still present is the value get returns, until something deletes it or the TTL ends |
| `test_redis_down_falls_through_to_postgres` | A cache error on get and on list reads the in-memory product row and records `error`, not `miss` |
| `test_concurrent_misses_both_fill_and_the_last_write_wins` | Two overlapping misses both read the repository and both fill. The stored value is one of those complete documents. `set_if_absent` is not used |
| `test_successful_catalog_change_deletes_the_product_key` | `invalidate` runs only after a successful commit, and then the product key and the list key are gone. A refused commit leaves the key |

`services/order-service/tests/unit/test_redis_cache.py` already covers a hit, a delete after update, a late fill that puts an old price back, and a Redis error on get. Those tests use the same fake.
