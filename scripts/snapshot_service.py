"""
Snapshot service for Bitcoin Cycle Compass v8.5 Sprint 1.

Queries the market_snapshots table and returns JSON-serialisable dicts.

API
---
latest_snapshot(db_path)           -- most recent row
snapshot(date, db_path)            -- exact date match or None
nearest_snapshot(date, db_path)    -- closest date by calendar distance
range_query(start, end, db_path)   -- all rows between start and end inclusive
compare_snapshots(date1, date2, db_path) -- side-by-side diff dict
"""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from db_schema import DB_PATH, init_db   # noqa: E402


def _row_to_dict(row):
    """Convert a sqlite3.Row to a plain dict, stripping None values only for output."""
    if row is None:
        return None
    return dict(row)


def latest_snapshot(db_path=None):
    """Return the most recent market_snapshots row as a dict, or None."""
    conn = init_db(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM market_snapshots ORDER BY date DESC LIMIT 1"
        ).fetchone()
        return _row_to_dict(row)
    finally:
        conn.close()


def snapshot(date, db_path=None):
    """Return the market_snapshots row for an exact date string (YYYY-MM-DD), or None."""
    conn = init_db(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM market_snapshots WHERE date = ?", (date,)
        ).fetchone()
        return _row_to_dict(row)
    finally:
        conn.close()


def nearest_snapshot(date, db_path=None):
    """
    Return the market_snapshots row whose date is closest to *date*.

    Ties are broken by returning the earlier of the two equidistant rows.
    Returns None if the table is empty.
    """
    conn = init_db(db_path)
    try:
        # SQLite: ABS(JULIANDAY(date) - JULIANDAY(?)) finds calendar distance.
        row = conn.execute(
            """
            SELECT *, ABS(JULIANDAY(date) - JULIANDAY(?)) AS dist
            FROM market_snapshots
            ORDER BY dist ASC, date ASC
            LIMIT 1
            """,
            (date,),
        ).fetchone()
        if row is None:
            return None
        d = dict(row)
        d.pop('dist', None)
        return d
    finally:
        conn.close()


def range_query(start, end, db_path=None):
    """
    Return all market_snapshots rows between *start* and *end* inclusive
    (both YYYY-MM-DD strings), ordered ascending by date.
    """
    conn = init_db(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM market_snapshots WHERE date BETWEEN ? AND ? ORDER BY date",
            (start, end),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        conn.close()


def compare_snapshots(date1, date2, db_path=None):
    """
    Return a dict comparing two snapshots.

    Structure:
        {
          'date1': YYYY-MM-DD,
          'date2': YYYY-MM-DD,
          'snapshot1': {...},
          'snapshot2': {...},
          'changes': {field: {'from': v1, 'to': v2, 'delta': v2-v1 or None}},
          'missing': [field, ...]   # fields NULL in both snapshots
        }
    Returns None for a date if that snapshot does not exist.
    """
    s1 = snapshot(date1, db_path)
    s2 = snapshot(date2, db_path)
    changes = {}
    missing = []
    if s1 and s2:
        all_keys = set(s1) | set(s2)
        skip = {'date', 'created_at', 'updated_at'}
        for k in sorted(all_keys - skip):
            v1 = s1.get(k)
            v2 = s2.get(k)
            if v1 is None and v2 is None:
                missing.append(k)
                continue
            if v1 != v2:
                try:
                    delta = round(float(v2) - float(v1), 6) if (
                        v1 is not None and v2 is not None
                    ) else None
                except (TypeError, ValueError):
                    delta = None
                changes[k] = {'from': v1, 'to': v2, 'delta': delta}
    return {
        'date1': date1,
        'date2': date2,
        'snapshot1': s1,
        'snapshot2': s2,
        'changes': changes,
        'missing': missing,
    }


def upsert_snapshot(conn, date, fields, now_utc=None):
    """
    Insert or replace a market_snapshots row for *date*.

    *fields* is a dict of column->value pairs. Missing columns default to NULL.
    A second call for the same date always updates (no silent duplicate).
    """
    if now_utc is None:
        now_utc = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    fields['date'] = date
    fields['updated_at'] = now_utc
    cols = ', '.join(fields.keys())
    placeholders = ', '.join(['?' for _ in fields])
    conn.execute(
        f"INSERT OR REPLACE INTO market_snapshots ({cols}) VALUES ({placeholders})",
        list(fields.values()),
    )


def set_build_metadata(conn, meta_dict):
    """
    Upsert key/value pairs into build_metadata.

    *meta_dict* should contain: appVersion, sprint, gitCommit, buildDate,
    databaseVersion, lastSuccessfulUpdate.
    """
    for key, value in meta_dict.items():
        conn.execute(
            "INSERT OR REPLACE INTO build_metadata (key, value) VALUES (?, ?)",
            (str(key), str(value) if value is not None else None),
        )


def get_build_metadata(db_path=None):
    """Return build_metadata as a plain dict {key: value}."""
    conn = init_db(db_path)
    try:
        rows = conn.execute("SELECT key, value FROM build_metadata").fetchall()
        return {r['key']: r['value'] for r in rows}
    finally:
        conn.close()
