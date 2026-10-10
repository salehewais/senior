# Endpoints

Send `Authorization: Bearer <access_token>` on every route marked **token**. Public pages do not need a token to load. Their data calls still do.

The longer contract, including error codes and request bodies, is [api.md](api.md).

## Pages

| Method | URL | Service | Auth |
| --- | --- | --- | --- |
| GET | http://127.0.0.1:8080/ | React storefront | Public page |
| GET | http://127.0.0.1:8080/reporting | Django | Public page. Report data needs an admin or manager token. |
| GET | http://127.0.0.1:8080/notifications | Flask | Public page. The delivery list needs an admin or manager token. |

## Auth (FastAPI)

| Method | URL | Auth | Effect |
| --- | --- | --- | --- |
| POST | http://127.0.0.1:8080/api/v1/auth/register | Public | Create a customer. A `role` field in the body is ignored. |
| POST | http://127.0.0.1:8080/api/v1/auth/login | Public | Return an access token and a refresh token. |
| POST | http://127.0.0.1:8080/api/v1/auth/refresh | Refresh token in the body | Rotate the refresh token and return a new pair. |
| POST | http://127.0.0.1:8080/api/v1/auth/logout | Refresh token in the body | Revoke that refresh token. Returns 204. |

## Products (FastAPI)

| Method | URL | Auth | Effect |
| --- | --- | --- | --- |
| GET | http://127.0.0.1:8080/api/v1/products | Token | List the catalog. Query: `limit`, `offset`. |
| GET | http://127.0.0.1:8080/api/v1/products/{id} | Token | One product. |
| POST | http://127.0.0.1:8080/api/v1/products | Admin | Create a product. |
| PATCH | http://127.0.0.1:8080/api/v1/products/{id} | Admin, Manager | Update name, price, or active flag. |

## Customers (FastAPI)

| Method | URL | Auth | Effect |
| --- | --- | --- | --- |
| GET | http://127.0.0.1:8080/api/v1/customers/me | Customer | Own profile. |
| PATCH | http://127.0.0.1:8080/api/v1/customers/me | Customer | Update display name. |
| GET | http://127.0.0.1:8080/api/v1/customers | Admin, Manager | List customers. |
| GET | http://127.0.0.1:8080/api/v1/customers/{id} | Admin, Manager, or that customer | One profile. |

## Orders (FastAPI)

| Method | URL | Auth | Effect |
| --- | --- | --- | --- |
| POST | http://127.0.0.1:8080/api/v1/orders | Customer | Create a `PENDING` order. Body is `items` of `product_id` and `quantity`. The server sets the price. |
| GET | http://127.0.0.1:8080/api/v1/orders | Token | Customer sees their own orders. Admin and Manager see all. Query: `limit`, `cursor`. |
| GET | http://127.0.0.1:8080/api/v1/orders/{id} | Owner, Admin, Manager | One order. |
| POST | http://127.0.0.1:8080/api/v1/orders/{id}/confirm | Owner, Admin, Manager | `PENDING` to `CONFIRMED`. |
| POST | http://127.0.0.1:8080/api/v1/orders/{id}/cancel | Owner, Admin, Manager | `PENDING` to `CANCELLED`. Body: `{"reason": "customer_request"}` or `staff_request`. |

## Reports (Django)

| Method | URL | Auth | Effect |
| --- | --- | --- | --- |
| GET | http://127.0.0.1:8080/api/v1/reports/orders/summary | Admin, Manager | Counts and totals by status. |
| GET | http://127.0.0.1:8080/api/v1/reports/orders | Admin, Manager | Projected orders. |
| GET | http://127.0.0.1:8080/api/v1/reports/inventory | Admin, Manager | Projected stock. |
| GET | http://127.0.0.1:8080/api/v1/reports/revenue | Admin, Manager | Payment totals from the reporting database. |

## Notifications (Flask)

| Method | URL | Auth | Effect |
| --- | --- | --- | --- |
| GET | http://127.0.0.1:8080/api/v1/notifications | Admin, Manager | List mock deliveries. |
| POST | http://127.0.0.1:8080/api/v1/device-tokens | Token | Register a device token. Body: `token`, `platform`. |
| GET | http://127.0.0.1:8080/api/v1/device-tokens | Token | List the caller's device tokens. |
| DELETE | http://127.0.0.1:8080/api/v1/device-tokens/{id} | Token | Remove one of the caller's device tokens. Returns 204. |

## Not on the public gateway

These exist on the order-service pod only. Traefik does not route them, so they have no `http://127.0.0.1:8080` URL. Fulfillment calls need the header `X-Internal-Token`.

| Method | Path | Effect |
| --- | --- | --- |
| GET | `/health/live` | Process is up. Does not check the database. |
| GET | `/health/ready` | Database accepts a query. |
| POST | `/api/v1/internal/orders/{id}/processing` | `CONFIRMED` to `PROCESSING`. |
| POST | `/api/v1/internal/orders/{id}/shipped` | `PROCESSING` to `SHIPPED`. |
| POST | `/api/v1/internal/orders/{id}/delivered` | `SHIPPED` to `DELIVERED`. |

Django and Flask also expose `/health/live`, `/health/ready`, and `/metrics` on their own pods. The gateway does not publish those paths.
