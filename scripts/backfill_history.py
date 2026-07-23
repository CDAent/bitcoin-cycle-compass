"""
Backfill four-year historical market snapshots into market_snapshots.

Sources used (all free, no API key required):
  BTC-USD        -- Yahoo Finance (already in btc_daily from Sprint 1)
  Fear & Greed   -- alternative.me historical API (1465 days)
  Gold (GLD)     -- Yahoo Finance
  S&P 500 (SPY)  -- Yahoo Finance
  NASDAQ (QQQ)   -- Yahoo Finance
  DXY            -- Yahoo Finance (DX-Y.NYB)
  US 10Y yield   -- Yahoo Finance (^TNX)
  AUD/USD        -- Yahoo Finance (AUDUSD=X)
  Stablecoins    -- stablecoins.llama.fi (weekly resolution)

Metrics NOT backfilled (not historically available):
  ETF flows            -- only from Jan 2024 ETF launch
  Opportunity score    -- dynamic model, no historical API
  Research score       -- dynamic model
  Capital allocation   -- dynamic model
  Market regime        -- dynamic model

Usage:
    python scripts/backfill_history.py
    python scripts/backfill_history.py --dry-run
    python scripts/backfill_history.py --db path/to/history.db
"""
import argparse, json, sys, urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from db_schema import DB_PATH, init_db          # noqa: E402
from snapshot_service import upsert_snapshot    # noqa: E402

APP_VERSION = '8.5.0-s1.3'
SPRINT = '1.3'
UA = {'User-Agent': 'BitcoinCycleCompass/8.5 (+GitHub Pages)', 'Accept': '*/*'}


def _get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode('utf-8', 'replace')


def _jget(url, timeout=30):
    return json.loads(_get(url, timeout))


def _safe(fn, label=''):
    try:
        return fn()
    except Exception as e:
        print(f'  WARNING [{label}]: {e}', file=sys.stderr)
        return None


def _ts_to_date(ts):
    return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime('%Y-%m-%d')


# ---------------------------------------------------------------------------
# Fetchers
# ---------------------------------------------------------------------------

def fetch_yahoo(ticker, years=4):
    """Return {date: close} for a Yahoo Finance ticker."""
    url = (f'https://query1.finance.yahoo.com/v8/finance/chart/'
           f'{ticker}?range={years}y&interval=1d&events=history')
    d = _jget(url)
    result = d['chart']['result'][0]
    timestamps = result.get('timestamp', [])
    closes = result['indicators']['quote'][0].get('close', [])
    out = {}
    for ts, c in zip(timestamps, closes):
        if c is not None:
            out[_ts_to_date(ts)] = round(float(c), 6)
    return out


def fetch_fear_greed(limit=1465):
    """Return {date: {'value': int, 'label': str}} from alternative.me."""
    url = f'https://api.alternative.me/fng/?limit={limit}&format=json'
    data = _jget(url).get('data', [])
    out = {}
    for row in data:
        d = _ts_to_date(row['timestamp'])
        out[d] = {'value': int(row['value']), 'label': row['value_classification']}
    return out


def fetch_stablecoins():
    """Return {date: market_cap_usd} from llama.fi (daily resolution)."""
    url = 'https://stablecoins.llama.fi/stablecoincharts/all'
    data = _jget(url)
    out = {}
    for row in data:
        cap = row.get('totalCirculatingUSD', {}).get('peggedUSD')
        if cap:
            d = _ts_to_date(row['date'])
            out[d] = float(cap)
    return out


# ---------------------------------------------------------------------------
# Main backfill
# ---------------------------------------------------------------------------

def backfill(db_path=None, dry_run=False, verbose=True):
    now_utc = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    if verbose:
        print('Fetching historical data sources...')

    btc_data    = _safe(lambda: fetch_yahoo('BTC-USD'),   'BTC-USD')     or {}
    gld_data    = _safe(lambda: fetch_yahoo('GLD'),        'GLD')         or {}
    spy_data    = _safe(lambda: fetch_yahoo('SPY'),        'SPY')         or {}
    qqq_data    = _safe(lambda: fetch_yahoo('QQQ'),        'QQQ')         or {}
    dxy_data    = _safe(lambda: fetch_yahoo('DX-Y.NYB'),   'DX-Y.NYB')   or {}
    us10y_data  = _safe(lambda: fetch_yahoo('^TNX'),       '^TNX')        or {}
    audusd_data = _safe(lambda: fetch_yahoo('AUDUSD=X'),   'AUDUSD=X')   or {}
    fg_data     = _safe(fetch_fear_greed,                   'fear_greed') or {}
    stable_data = _safe(fetch_stablecoins,                  'stablecoins') or {}

    if verbose:
        print(f'  BTC: {len(btc_data)} days')
        print(f'  Gold (GLD): {len(gld_data)} days')
        print(f'  S&P 500 (SPY): {len(spy_data)} days')
        print(f'  NASDAQ (QQQ): {len(qqq_data)} days')
        print(f'  DXY: {len(dxy_data)} days')
        print(f'  US 10Y: {len(us10y_data)} days')
        print(f'  AUD/USD: {len(audusd_data)} days')
        print(f'  Fear & Greed: {len(fg_data)} days')
        print(f'  Stablecoins: {len(stable_data)} days')

    # Union of all dates that have any data.
    all_dates = sorted(
        set(btc_data) | set(gld_data) | set(spy_data) | set(qqq_data)
        | set(dxy_data) | set(us10y_data) | set(audusd_data) | set(fg_data)
    )

    if verbose:
        print(f'Building {len(all_dates)} snapshot rows...')

    if dry_run:
        print(f'Dry run: would write {len(all_dates)} rows. Exiting.')
        return len(all_dates)

    conn = init_db(db_path)
    inserted = updated = 0
    for date in all_dates:
        existing = conn.execute(
            "SELECT 1 FROM market_snapshots WHERE date=?", (date,)
        ).fetchone()

        fg = fg_data.get(date, {})
        fields = {
            # Bitcoin
            'btc_usd':               btc_data.get(date),
            'btc_aud':               (
                round(btc_data[date] / audusd_data[date], 2)
                if date in btc_data and date in audusd_data and audusd_data[date]
                else None
            ),
            'btc_source':            'yahoo_finance' if date in btc_data else None,
            'btc_fetched_at':        now_utc if date in btc_data else None,
            'btc_verified':          1 if date in btc_data else 0,
            'btc_quality_status':    'live' if date in btc_data else 'unavailable',
            # Sentiment
            'fear_greed_value':      fg.get('value'),
            'fear_greed_label':      fg.get('label'),
            'fear_greed_source':     'alternative.me' if fg else None,
            'fear_greed_fetched_at': now_utc if fg else None,
            'fear_greed_quality':    'live' if fg else 'unavailable',
            # Stablecoins (nearest available date)
            'stablecoin_market_cap_usd': stable_data.get(date),
            'stablecoin_source':         'llama.fi' if date in stable_data else None,
            'stablecoin_fetched_at':     now_utc if date in stable_data else None,
            'stablecoin_quality':        'live' if date in stable_data else 'unavailable',
            # Traditional markets
            'gold_price':            gld_data.get(date),
            'gold_source':           'yahoo_finance/GLD' if date in gld_data else None,
            'gold_fetched_at':       now_utc if date in gld_data else None,
            'gold_quality':          'live' if date in gld_data else 'unavailable',
            'sp500_price':           spy_data.get(date),
            'sp500_source':          'yahoo_finance/SPY' if date in spy_data else None,
            'sp500_fetched_at':      now_utc if date in spy_data else None,
            'sp500_quality':         'live' if date in spy_data else 'unavailable',
            'nasdaq_price':          qqq_data.get(date),
            'nasdaq_source':         'yahoo_finance/QQQ' if date in qqq_data else None,
            'nasdaq_fetched_at':     now_utc if date in qqq_data else None,
            'nasdaq_quality':        'live' if date in qqq_data else 'unavailable',
            'dxy_value':             dxy_data.get(date),
            'dxy_source':            'yahoo_finance/DX-Y.NYB' if date in dxy_data else None,
            'dxy_fetched_at':        now_utc if date in dxy_data else None,
            'dxy_quality':           'live' if date in dxy_data else 'unavailable',
            'us_10y_yield':          us10y_data.get(date),
            'us_10y_source':         'yahoo_finance/^TNX' if date in us10y_data else None,
            'us_10y_fetched_at':     now_utc if date in us10y_data else None,
            'us_10y_quality':        'live' if date in us10y_data else 'unavailable',
            'aud_usd':               audusd_data.get(date),
            'aud_usd_source':        'yahoo_finance/AUDUSD=X' if date in audusd_data else None,
            'aud_usd_fetched_at':    now_utc if date in audusd_data else None,
            'aud_usd_quality':       'live' if date in audusd_data else 'unavailable',
            # Scores/regime/allocation: not backfillable
            'scores_quality':        'unavailable',
            'updater_version':       APP_VERSION,
            'sprint':                SPRINT,
        }

        upsert_snapshot(conn, date, fields, now_utc)
        if existing:
            updated += 1
        else:
            inserted += 1

    conn.commit()
    conn.close()

    if verbose:
        print(f'  Inserted: {inserted}, Updated: {updated}')
    return inserted + updated


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Backfill historical market snapshots.')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--db', default=None)
    args = parser.parse_args()
    backfill(db_path=args.db, dry_run=args.dry_run)
