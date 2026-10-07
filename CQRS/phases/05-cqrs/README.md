# Phase 5 — Explicit CQRS boundaries

Formalize command vs query ownership. No new performance magic — governance over Phase 3–4.

## Artifacts

| Path | Purpose |
|------|---------|
| `contracts/command_query_boundaries.md` | What may write / what may read |
| `config/report_routing.yaml` | Map report_code → lane → DSN / dataset |

Wire Phase 1 workers and Analytical apps to honor `report_routing.yaml`.
