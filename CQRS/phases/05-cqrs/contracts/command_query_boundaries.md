# Command / Query boundaries

## Commands (writes)

| Allowed | System | Notes |
|---------|--------|-------|
| Create/post/cancel moves, POS orders, payments | Odoo → **PRIMARY** | Only write path for accounting facts |
| Enqueue report jobs | Odoo or reporting API → job store | No AML mutation |
| Emit outbox events | Same TX as Odoo write (optional) | Payload only |

**Forbidden:** Report workers or ETL writing into `account_move` / `account_move_line` on primary.

## Queries (reads)

| Lane | Allowed sources | Forbidden |
|------|-----------------|-----------|
| Exact | PRIMARY (rare) or **REPLICA** Odoo schema, lag-gated | Reporting facts without proven parity |
| Analytical | `reporting.aml_daily` / `fact_*` / warehouse | Wide AML scans on primary |

## Sync

| Path | Owner |
|------|-------|
| Phase 2 refresh jobs | Reporting platform |
| Phase 3 ETL | Reporting platform |
| Phase 4 event consumers | Reporting platform |
| Nightly reconcile + alerts | Shared on-call |

## Acceptance

- [ ] Every `report_code` listed in `config/report_routing.yaml`
- [ ] Exact codes never target `REPORTING_DSN` unless parity waiver signed
- [ ] Analytical codes never target `PRIMARY_DSN`
