"""Logs, metrics, and traces for the order service.

Prometheus labels stay low-cardinality. Request and message ids belong in
logs and spans, not in metric labels.
"""
