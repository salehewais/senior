# PEAA study labs

Runnable Python for the enterprise-patterns guide. Pattern names follow the book table of contents. The code is a minimal leasing example (one active lease, monthly total USD 900.00), not a port of the book and not a production app.

Part 3 under `lab/concurrency/` is an add-on about threads and tasks. It is not the same problem as offline locks in `lab/patterns/offline_concurrency.py`.

## Run

From this directory (`enterpise patterns`):

```bash
python3 -m peaa.extract_outline
python3 -m peaa.build_guide
python3 -m peaa.lab.run_demo --list
python3 -m peaa.lab.run_demo domain_model
python3 -m peaa.lab.run_demo --all
```

Labs use the standard library (Python 3.10+). `requirements.txt` is only for optional PyMuPDF bookmark extraction; without it, `extract_outline.py` uses `pdftotext`.

## Where a demo lives

| Area | Module |
|------|--------|
| Part 1 walkthrough | `lab/lease_app/story.py` |
| Domain logic | `lab/patterns/domain_logic.py` |
| Data source | `lab/patterns/data_source.py` |
| OR behavior | `lab/patterns/or_behavioral.py` |
| OR structure | `lab/patterns/or_structural.py` |
| Metadata | `lab/patterns/or_metadata.py` |
| Web | `lab/patterns/web_presentation.py` |
| Distribution | `lab/patterns/distribution.py` |
| Offline locks | `lab/patterns/offline_concurrency.py` |
| Session state | `lab/patterns/session_state.py` |
| Base patterns | `lab/patterns/base_patterns.py` |
| Pools and tasks | `lab/concurrency/workers.py` |
| Sync | `lab/concurrency/sync.py` |
| Reactor-style execution | `lab/concurrency/execution.py` |
| Rate limit, bulkhead, monitor | `lab/concurrency/resilience.py` |

`python3 -m peaa.lab.run_demo --list` prints every name. The HTML guide repeats the name next to each section.
