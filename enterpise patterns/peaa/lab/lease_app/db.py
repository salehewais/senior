"""In-memory leasing schema shared by the labs. مخطط عقد التأجير في الذاكرة."""

from __future__ import annotations

import sqlite3

SCHEMA = """
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE assets (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    kind TEXT NOT NULL,
    monthly_rate_cents INTEGER NOT NULL,
    currency TEXT NOT NULL DEFAULT 'USD',
    axle_count INTEGER,
    lift_height_cm INTEGER
);
CREATE TABLE leases (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 0,
    terms_json TEXT
);
CREATE TABLE lease_lines (
    id INTEGER PRIMARY KEY,
    lease_id INTEGER NOT NULL,
    asset_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL
);
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY,
    lease_id INTEGER NOT NULL,
    amount_cents INTEGER NOT NULL,
    currency TEXT NOT NULL
);
CREATE TABLE offline_locks (
    aggregate TEXT NOT NULL,
    aggregate_id INTEGER NOT NULL,
    owner TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    PRIMARY KEY (aggregate, aggregate_id)
);
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    payload TEXT NOT NULL
);
"""


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def seed(conn: sqlite3.Connection) -> None:
    conn.executemany(
        "INSERT INTO customers (id, name) VALUES (?, ?)",
        [(1, "Noura"), (2, "Hadi")],
    )
    conn.executemany(
        """
        INSERT INTO assets
            (id, name, kind, monthly_rate_cents, currency, axle_count, lift_height_cm)
        VALUES (?, ?, ?, ?, 'USD', ?, ?)
        """,
        [
            (1, "Flatbed", "truck", 50000, 3, None),
            (2, "Warehouse lift", "forklift", 20000, None, 450),
        ],
    )
    conn.execute(
        "INSERT INTO leases (id, customer_id, status, version, terms_json) VALUES (1, 1, 'active', 0, ?)",
        ('{"early_return": "prorate"}',),
    )
    conn.executemany(
        "INSERT INTO lease_lines (id, lease_id, asset_id, quantity) VALUES (?, 1, ?, ?)",
        [(1, 1, 1), (2, 2, 2)],
    )
    conn.commit()


def fresh() -> sqlite3.Connection:
    conn = connect()
    seed(conn)
    return conn
