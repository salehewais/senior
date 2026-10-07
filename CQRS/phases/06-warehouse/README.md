# Phase 6 — Warehouse / OLAP

Only when Phase 2–4 are insufficient for cross-domain BI, long history, or external BI tools.

## Artifacts

| Path | Purpose |
|------|---------|
| `sql/01_star_schema.sql` | Warehouse star for finance/sales facts |
| `elt/load_from_reporting_db.py` | ELT from Reporting DB → warehouse |
| `semantic_layer.md` | Notes for BI/OLAP tools |

Exact statutory delivery stays on Odoo replica — not warehouse-only.
