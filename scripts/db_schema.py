"""
SQLite schema management for Bitcoin Cycle Compass v8.4 historical data layer.

Uses CREATE TABLE IF NOT EXISTS + schema_version table for safe migrations.
An existing database is never destroyed — only additive changes are applied.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / 'data' / 'history.db'

CURRENT_VERSION = 1

# All tables use CREATE TABLE IF NOT EXISTS so reruns are safe.
_SCHEMA_V1 = """
CREATE TABLE IF NOT EXISTS schema_version (
    version    INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

-- Daily BTC price in USD and AUD.
CREATE TABLE IF NOT EXISTS btc_daily (
    date       TEXT PRIMARY KEY,   -- YYYY-MM-DD (UTC)
    price_usd  REAL NOT NULL,
    price_aud  REAL,
    source     TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

-- Daily Fear & Greed index.
CREATE TABLE IF NOT EXISTS fear_greed (
    date       TEXT PRIMARY KEY,
    value      INTEGER NOT NULL,   -- 0–100
    label      TEXT,
    change_24h REAL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

-- Daily Bitcoin ETF flows.
CREATE TABLE IF NOT EXISTS etf_flows (
    date                    TEXT PRIMARY KEY,
    daily_usd_millions      REAL,
    five_day_usd_millions   REAL,
    twenty_day_usd_millions REAL,
    flow_score              INTEGER,
    combined_score          INTEGER,
    source                  TEXT,
    created_at              TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

-- Daily stablecoin market cap.
CREATE TABLE IF NOT EXISTS stablecoin_market_cap (
    date           TEXT PRIMARY KEY,
    market_cap_usd REAL,
    change_1d      REAL,
    change_7d      REAL,
    change_30d     REAL,
    created_at     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

-- Daily composite scores.
CREATE TABLE IF NOT EXISTS scores (
    date              TEXT PRIMARY KEY,
    opportunity_score INTEGER,
    research_score    INTEGER,
    macro_score       INTEGER,
    onchain_score     INTEGER,
    btc_score         INTEGER,
    fear_greed_value  INTEGER,
    created_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

-- Daily market regime classification.
CREATE TABLE IF NOT EXISTS market_regime (
    date       TEXT PRIMARY KEY,
    label      TEXT NOT NULL,   -- Bull, Transition, Bear
    confidence INTEGER,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

-- Daily capital allocation percentages (0–100 each).
CREATE TABLE IF NOT EXISTS capital_allocation (
    date             TEXT PRIMARY KEY,
    cash_bills       INTEGER,
    govt_bonds       INTEGER,
    global_equities  INTEGER,
    ai_technology    INTEGER,
    emerging_markets INTEGER,
    bitcoin          INTEGER,
    stablecoins      INTEGER,
    gold             INTEGER,
    silver           INTEGER,
    created_at       TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

-- Daily macro market data (Gold, S&P 500, NASDAQ, DXY, US 10Y yield).
CREATE TABLE IF NOT EXISTS market_data (
    date              TEXT PRIMARY KEY,
    gold_price        REAL,
    gold_change_20d   REAL,
    sp500_price       REAL,
    sp500_change_20d  REAL,
    nasdaq_price      REAL,
    nasdaq_change_20d REAL,
    dxy_value         REAL,
    dxy_change_20d    REAL,
    us_10y_yield      REAL,
    us_10y_change_20d REAL,
    created_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);
"""


def get_connection(db_path=None):
    """Return an open sqlite3 connection with WAL mode and row_factory."""
    path = Path(db_path or DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def get_schema_version(conn):
    """Return the current schema version number (0 if not yet initialised)."""
    try:
        row = conn.execute(
            "SELECT MAX(version) AS v FROM schema_version"
        ).fetchone()
        return row['v'] if row and row['v'] is not None else 0
    except sqlite3.OperationalError:
        return 0


def apply_migrations(conn):
    """Apply any pending migrations. Safe to call multiple times."""
    version = get_schema_version(conn)
    if version < 1:
        conn.executescript(_SCHEMA_V1)
        conn.execute(
            "INSERT OR IGNORE INTO schema_version (version) VALUES (1)"
        )
        conn.commit()


def init_db(db_path=None):
    """Open (or create) the database, apply migrations, and return the connection."""
    conn = get_connection(db_path)
    apply_migrations(conn)
    return conn
