"""
History service for Bitcoin Cycle Compass v8.4.

Queries the SQLite historical data layer and returns JSON-serialisable
dicts for the daily / weekly range views used by the History & Trends page.

Supported range keys
--------------------
  7d   – last 7 days, daily resolution
  1m   – last 31 days, daily resolution
  3m   – last 92 days, daily resolution
  6m   – last 184 days, daily resolution
  1y   – last 52 weeks, weekly resolution
  2y   – last 104 weeks, weekly resolution
  4y   – last 208 weeks, weekly resolution
"""
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

# Allow running from any working directory.
sys.path.insert(0, str(Path(__file__).parent))
from db_schema import DB_PATH, init_db  # noqa: E402

_RANGES = {
    '7d':  ('daily',  7),
    '1m':  ('daily',  31),
    '3m':  ('daily',  92),
    '6m':  ('daily',  184),
    '1y':  ('weekly', 52),
    '2y':  ('weekly', 104),
    '4y':  ('weekly', 208),
}


def _daily_rows(conn, days):
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    rows = conn.execute(
        "SELECT date AS day, price_usd AS usd, price_aud AS aud "
        "FROM btc_daily WHERE date >= ? ORDER BY date",
        (cutoff,),
    ).fetchall()
    return [dict(r) for r in rows]


def _weekly_rows(conn, weeks):
    """Aggregate daily rows into ISO Monday-anchored weekly buckets."""
    all_rows = conn.execute(
        "SELECT date AS day, price_usd AS usd, price_aud AS aud "
        "FROM btc_daily ORDER BY date"
    ).fetchall()
    week_map = {}
    for r in all_rows:
        d = datetime.strptime(r['day'], '%Y-%m-%d')
        monday = (d - timedelta(days=d.weekday())).strftime('%Y-%m-%d')
        # Keep the last price seen for each week (most recent day in week).
        week_map[monday] = {'week': monday, 'usd': r['usd'], 'aud': r['aud']}
    sorted_weeks = sorted(week_map.values(), key=lambda x: x['week'])
    return sorted_weeks[-weeks:]


def query_range(range_key, db_path=None):
    """
    Return history records for the given range key.

    Returns a dict with:
      rows        – list of record dicts
      resolution  – 'Daily' or 'Weekly'
    """
    if range_key not in _RANGES:
        raise ValueError(
            f"Unknown range key: {range_key!r}. Valid keys: {sorted(_RANGES)}"
        )
    resolution_type, count = _RANGES[range_key]
    conn = init_db(db_path)
    try:
        if resolution_type == 'daily':
            rows = _daily_rows(conn, count)
            return {'rows': rows, 'resolution': 'Daily'}
        else:
            rows = _weekly_rows(conn, count)
            return {'rows': rows, 'resolution': 'Weekly'}
    finally:
        conn.close()


def get_daily_history(db_path=None, days=1465):
    """Return up to *days* daily BTC price rows from the database."""
    conn = init_db(db_path)
    try:
        return _daily_rows(conn, days)
    finally:
        conn.close()


def get_weekly_history(db_path=None, weeks=208):
    """Return up to *weeks* weekly BTC price rows from the database."""
    conn = init_db(db_path)
    try:
        return _weekly_rows(conn, weeks)
    finally:
        conn.close()
