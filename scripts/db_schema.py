"""
SQLite schema management for Bitcoin Cycle Compass v8.4 historical data layer.

Uses CREATE TABLE IF NOT EXISTS + schema_version table for safe migrations.
An existing database is never destroyed -- only additive changes are applied.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / 'data' / 'history.db'

CURRENT_VERSION = 2

# ---------------------------------------------------------------------------
# V1 - Sprint 1 tables (unchanged after release)
# ---------------------------------------------------------------------------
_SCHEMA_V1 = """
CREATE TABLE IF NOT EXISTS schema_version (
    version    INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);
CREATE TABLE IF NOT EXISTS btc_daily (
    date       TEXT PRIMARY KEY,
    price_usd  REAL NOT NULL,
    price_aud  REAL,
    source     TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);
CREATE TABLE IF NOT EXISTS fear_greed (
    date       TEXT PRIMARY KEY,
    value      INTEGER NOT NULL,
    label      TEXT,
    change_24h REAL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);
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
CREATE TABLE IF NOT EXISTS stablecoin_market_cap (
    date           TEXT PRIMARY KEY,
    market_cap_usd REAL,
    change_1d      REAL,
    change_7d      REAL,
    change_30d     REAL,
    created_at     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);
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
CREATE TABLE IF NOT EXISTS market_regime (
    date       TEXT PRIMARY KEY,
    label      TEXT NOT NULL,
    confidence INTEGER,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);
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

# ---------------------------------------------------------------------------
# V2 - Sprint 2A: unified market_snapshots table + build_metadata
#
# market_snapshots: one row per day, every required metric.
# NULL = genuinely unavailable (never silently substituted with zero).
# Each metric group has source, fetched_at, verified, quality_status columns.
# ---------------------------------------------------------------------------
_SCHEMA_V2 = """
CREATE TABLE IF NOT EXISTS market_snapshots (
    date                        TEXT PRIMARY KEY,

    -- Bitcoin
    btc_usd                     REAL,
    btc_aud                     REAL,
    btc_change_24h              REAL,
    btc_source                  TEXT,
    btc_fetched_at              TEXT,
    btc_verified                INTEGER DEFAULT 0,
    btc_quality_status          TEXT,

    -- Sentiment
    fear_greed_value            INTEGER,
    fear_greed_label            TEXT,
    fear_greed_source           TEXT,
    fear_greed_fetched_at       TEXT,
    fear_greed_quality          TEXT,

    -- ETF Flows
    etf_daily_usd_millions      REAL,
    etf_cumulative_usd_millions REAL,
    etf_flow_score              INTEGER,
    etf_source                  TEXT,
    etf_fetched_at              TEXT,
    etf_quality                 TEXT,

    -- Stablecoins
    stablecoin_market_cap_usd   REAL,
    stablecoin_change_7d        REAL,
    stablecoin_source           TEXT,
    stablecoin_fetched_at       TEXT,
    stablecoin_quality          TEXT,

    -- Scores (NULL when not computed)
    opportunity_score           INTEGER,
    research_score              INTEGER,
    macro_score                 INTEGER,
    onchain_score               INTEGER,
    btc_score                   INTEGER,
    scores_source               TEXT DEFAULT 'compass_model',
    scores_quality              TEXT,

    -- Market Regime
    market_regime               TEXT,
    market_regime_confidence    INTEGER,
    regime_source               TEXT DEFAULT 'compass_model',

    -- Capital Allocation (percentages, NULL when not computed)
    alloc_cash_bills            INTEGER,
    alloc_govt_bonds            INTEGER,
    alloc_global_equities       INTEGER,
    alloc_ai_technology         INTEGER,
    alloc_emerging_markets      INTEGER,
    alloc_bitcoin               INTEGER,
    alloc_stablecoins           INTEGER,
    alloc_gold                  INTEGER,
    alloc_silver                INTEGER,

    -- Gold
    gold_price                  REAL,
    gold_source                 TEXT,
    gold_fetched_at             TEXT,
    gold_quality                TEXT,

    -- S&P 500
    sp500_price                 REAL,
    sp500_source                TEXT,
    sp500_fetched_at            TEXT,
    sp500_quality               TEXT,

    -- NASDAQ
    nasdaq_price                REAL,
    nasdaq_source               TEXT,
    nasdaq_fetched_at           TEXT,
    nasdaq_quality              TEXT,

    -- DXY
    dxy_value                   REAL,
    dxy_source                  TEXT,
    dxy_fetched_at              TEXT,
    dxy_quality                 TEXT,

    -- US 10-Year Treasury Yield
    us_10y_yield                REAL,
    us_10y_source               TEXT,
    us_10y_fetched_at           TEXT,
    us_10y_quality              TEXT,

    -- AUD/USD
    aud_usd                     REAL,
    aud_usd_source              TEXT,
    aud_usd_fetched_at          TEXT,
    aud_usd_quality             TEXT,

    -- Audit
    created_at                  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    updated_at                  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    updater_version             TEXT,
    sprint                      TEXT
);

CREATE TABLE IF NOT EXISTS build_metadata (
    key        TEXT PRIMARY KEY,
    value      TEXT,
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
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
        conn.execute("INSERT OR IGNORE INTO schema_version (version) VALUES (1)")
        conn.commit()
        version = 1
    if version < 2:
        conn.executescript(_SCHEMA_V2)
        conn.execute("INSERT OR IGNORE INTO schema_version (version) VALUES (2)")
        conn.commit()


def init_db(db_path=None):
    """Open (or create) the database, apply migrations, and return the connection."""
    conn = get_connection(db_path)
    apply_migrations(conn)
    return conn
