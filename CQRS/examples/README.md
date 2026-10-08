# Python examples — all 22 solutions

Each script is a **small teaching demo** (stdlib only) of one idea from the reporting-scale map.  
Not production Odoo code — analogies you can run locally to feel the trade-off.

## Run one

```bash
cd examples
python3 06_pre_aggregation.py
```

## Run all

```bash
cd examples
python3 run_all.py
```

## Index

| # | File | Topic |
|---|------|--------|
| 1 | `01_partitioning.py` | Partition pruning vs full scan |
| 2 | `02_read_replica.py` | Primary writes / replica reads |
| 3 | `03_separate_reporting_server.py` | Report process ≠ Odoo web process |
| 4 | `04_reporting_db.py` | Facts/dims in SQLite “reporting DB” |
| 5 | `05_read_model.py` | Projection optimized for queries |
| 6 | `06_pre_aggregation.py` | Highest ROI — pay once, read many |
| 7 | `07_materialized_view.py` | Stored result + REFRESH |
| 8 | `08_cache.py` | Identical params → cache hit |
| 9 | `09_async_processing.py` | Enqueue job_id; don’t block UI |
| 10 | `10_background_workers.py` | Worker pool + concurrency cap |
| 11 | `11_cqrs.py` | Command vs Query models |
| 12 | `12_event_driven.py` | InvoicePosted → update summary |
| 13 | `13_cqrs_plus_events.py` | CQRS + async projection |
| 14 | `14_eventual_consistency.py` | Write now / read catches up |
| 15 | `15_archiving.py` | Hot/cold — not DELETE AML |
| 16 | `16_data_warehouse.py` | Star schema ETL for BI |
| 17 | `17_olap.py` | Cube slice / rollup |
| 18 | `18_resource_isolation.py` | Separate process pools |
| 19 | `19_connection_control.py` | Semaphore = connection cap |
| 20 | `20_async_plus_preaggregation.py` | Worker maintains summary |
| 21 | `21_replica_plus_reporting_model.py` | Exact vs Analytical routing |
| 22 | `22_full_stack.py` | Mini end-to-end analytical stack |

Shared fake AML generator: `_demo_data.py`.

Interactive HTML guide: [`../learn.html`](../learn.html).
