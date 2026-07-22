"""
Import four-year BTC daily history from Yahoo Finance into SQLite.

Safe to run multiple times — INSERT OR IGNORE prevents duplicates.
Usage:
    python scripts/import_history.py
    python scripts/import_history.py --dry-run
"""
import argparse
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# Allow imports from scripts/ regardless of working directory.
sys.path.insert(0, str(Path(__file__).parent))
from db_schema import DB_PATH, init_db  # noqa: E402

_UA = {
    'User-Agent': 'BitcoinCycleCompass/8.4 (+GitHub Pages)',
    'Accept': 'application/json,*/*',
}
_VALID_PRICE_RANGE = (1_000, 2_000_000)   # USD sanity bounds


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_row(row):
    """
    Validate a single price row dict with 'date' and 'price_usd' keys.

    Raises ValueError for invalid data; returns True when valid.
    """
    date_str = row.get('date')
    if not date_str:
        raise ValueError(f"Missing date: {row!r}")
    # Strict format check.
    try:
        datetime.strptime(str(date_str), '%Y-%m-%d')
    except ValueError:
        raise ValueError(f"Invalid date format (expected YYYY-MM-DD): {date_str!r}")

    price = row.get('price_usd')
    if price is None:
        raise ValueError(f"Missing price_usd: {row!r}")
    try:
        price = float(price)
    except (TypeError, ValueError):
        raise ValueError(f"Non-numeric price_usd: {price!r}")
    lo, hi = _VALID_PRICE_RANGE
    if not (lo < price < hi):
        raise ValueError(
            f"price_usd {price} outside valid range ({lo}, {hi})"
        )
    return True


# ---------------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------------

def fetch_yahoo_btc(years=4):
    """
    Fetch up to *years* years of daily BTC-USD closes from Yahoo Finance.

    Returns a list of {'date': 'YYYY-MM-DD', 'price_usd': float} dicts
    sorted ascending by date, capped at 1465 rows.
    """
    url = (
        f'https://query1.finance.yahoo.com/v8/finance/chart/'
        f'BTC-USD?range={years}y&interval=1d&events=history'
    )
    req = urllib.request.Request(url, headers=_UA)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode('utf-8'))

    result = data['chart']['result'][0]
    timestamps = result.get('timestamp', [])
    closes = (
        result.get('indicators', {})
              .get('quote', [{}])[0]
              .get('close', [])
    )
    rows = []
    for ts, close in zip(timestamps, closes):
        if close is None:
            continue
        day = datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime('%Y-%m-%d')
        rows.append({'date': day, 'price_usd': round(float(close), 2)})

    rows.sort(key=lambda x: x['date'])
    return rows[-1465:]   # last four years of trading days


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------

def import_history(db_path=None, dry_run=False, verbose=True):
    """
    Fetch four-year BTC history and insert new rows into the database.

    Rows that already exist are skipped (INSERT OR IGNORE).
    Returns the number of newly inserted rows.
    """
    if verbose:
        print('Fetching BTC daily history from Yahoo Finance…')
    raw_rows = fetch_yahoo_btc()
    if verbose:
        print(f'  Received {len(raw_rows)} rows from API')

    valid, rejected = [], []
    for row in raw_rows:
        try:
            validate_row(row)
            valid.append(row)
        except ValueError as exc:
            rejected.append((row, str(exc)))
            if verbose:
                print(f'  SKIPPED invalid row: {exc}')

    if verbose and rejected:
        print(f'  Rejected {len(rejected)} row(s) — see above for details')

    if dry_run:
        if verbose:
            print(f'Dry run: would import {len(valid)} valid rows '
                  f'(skipping {len(rejected)} invalid)')
        return len(valid)

    conn = init_db(db_path)
    inserted = skipped = 0
    try:
        for row in valid:
            cur = conn.execute(
                "INSERT OR IGNORE INTO btc_daily (date, price_usd, source) "
                "VALUES (?, ?, 'yahoo_finance')",
                (row['date'], row['price_usd']),
            )
            if cur.rowcount > 0:
                inserted += 1
            else:
                skipped += 1
        conn.commit()
    finally:
        conn.close()

    if verbose:
        print(f'  Inserted: {inserted} new rows, '
              f'already present: {skipped} rows')
    return inserted


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Import four-year BTC history into SQLite.'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Fetch and validate without writing to the database.'
    )
    parser.add_argument(
        '--db', default=None,
        help='Override database path (default: data/history.db).'
    )
    args = parser.parse_args()
    import_history(db_path=args.db, dry_run=args.dry_run)
