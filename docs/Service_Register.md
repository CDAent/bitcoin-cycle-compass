# Service Register
## Bitcoin Cycle Compass — Version 8.7 · Sprint 0

Services in Bitcoin Cycle Compass are Python scripts in the `scripts/` directory. They run server-side in GitHub Actions. There are no runtime backend services — all processing happens at build/update time.

---

## 1. Data Updater (`update_data.py`)

| Field | Value |
|---|---|
| **Purpose** | Primary data orchestrator. Fetches all external APIs, computes composite scores, writes `data/live.json` and upserts all tables in `data/history.db`. |
| **Location** | `scripts/update_data.py` |
| **Called By** | GitHub Actions `pages-release.yml`, `build_release.py`, manual execution |
| **Dependencies** | `db_schema.py`, `history_service.py`, `snapshot_service.py`, `import_history.py` (all optional via try/import) |

### Functions

| Function | Purpose | Returns |
|---|---|---|
| `price_sources()` | Fetches BTC/USD from Coinbase, Kraken, Bitstamp, CoinGecko. Applies trimmed average with median outlier rejection (±2.5%). | `(avg_usd, detail_list, cg24h_change)` |
| `fx()` | Fetches USD→AUD exchange rate from Frankfurter API. | `float` (usdAud rate) |
| `fear()` | Fetches last 2 Fear & Greed readings from Alternative.me. Computes 24h change. | `dict` (value, label, change24h) |
| `stablecoins()` | Fetches stablecoin market cap chart from DeFiLlama. Computes 1d/7d/30d changes. | `dict` (marketCapUsd, change1d, change7d, change30d) |
| `fred(series)` | Fetches a FRED CSV series by ID. | `list` of `(date, value)` tuples |
| `macro()` | Calls `fred()` for 5 series (WALCL, M2SL, DGS10, DTWEXBGS, VIXCLS). Computes weighted macro_score. | `dict` (per-series objects + score) |
| `chain()` | Fetches 3 Blockchain.info chart series. Computes onchain_score. | `dict` (score, metrics dict) |
| `stooq(symbol)` | Fetches daily CSV from Stooq for a given symbol. Returns last close and 20-day change. | `dict` (last, change20d) |
| `etf_demand_proxy()` | Fetches 6 Bitcoin ETF tickers from Yahoo Finance. Computes dollar-volume-weighted return and volume ratio. Returns proxy score and label. | `dict` (status, score, label, return1d, volumeVs20d, aggregateDollarVolumeUsd, funds) |
| `etf_flow(previous)` | Scrapes Farside ETF flow table. Combines flow_score with proxy_score. Handles stale data. | `dict` (status, source, daily/5d/20d flows, flowScore, proxy, score, scoreSource, dailyAvailable, errors) |
| `_parse_farside(url)` | HTML parser for Farside ETF flow table. Extracts date + USD millions rows. | `list` of `{date, usdMillions}` |
| `_yahoo_etf(ticker)` | Fetches 1-month daily history for one ETF ticker from Yahoo Finance. | `dict` (ticker, close, return1d, volume, volumeVs20d, dollarVolumeUsd) |
| `btc_daily_history_four_years()` | Fetches 4 years of BTC-USD daily data from Yahoo Finance. | `list` of `{day, usd}` (last 1465 rows) |
| `daily_btc_history()` | Thin wrapper for `btc_daily_history_four_years()`. | `list` of `{day, usd}` |
| `weekly_btc_history()` | Aggregates daily rows into Monday-anchored weekly buckets. | `list` of `{week, usd}` (last 208 weeks) |
| `article_significance(title, source)` | Rule-based news scorer. Assigns score, star rating (1–5), impact label, tags, and why-text. | `dict` (impactScore, stars, impact, tags, why) |
| `news()` | Queries Google News RSS for 3 search queries. Deduplicates and applies `article_significance()`. | `list` of article dicts (max 20) |
| `events()` | Returns hardcoded list of official economic calendar links. | `list` of `{tag, title, source, url}` |
| `reports_payload(scores, trends, etf, macro, onchain)` | Builds 3-section executive report summary. | `dict` (status, sections[]) |
| `sync_manifest_versions(manifest_path)` | Reads `manifest.json` and updates name/short_name to match `_APP_VERSION` if changed. | None |
| `_git_commit()` | Returns the short HEAD git commit hash. | `str` |
| `save_daily_to_db(conn, today, ...)` | Upserts all V1 SQLite tables (btc_daily, fear_greed, etf_flows, stablecoin_market_cap, scores, capital_allocation, market_data). | None |
| `write_full_snapshot(conn, today, now_utc, ...)` | Upserts a complete `market_snapshots` row for today (V2 schema). | None |
| `get(url, timeout)` | HTTP GET via urllib. Returns decoded string. | `str` |
| `jget(url)` | HTTP GET parsed as JSON. | `dict` |
| `safe(fn, default)` | Calls `fn()`, returns `default` on any exception. | Any |
| `clamp(x, a, b)` | Clamps x to [a, b]. | `number` |
| `pct(a, b)` | Percentage change from b to a. | `float` |

### Command-Line Arguments

| Argument | Default | Purpose |
|---|---|---|
| `--output` | `data/live.json` | Output path for the JSON file |
| `--db-path` | `data/history.db` | SQLite database path |
| `--manifest-path` | `manifest.json` | Manifest path for version sync |

---

## 2. Schema Manager (`db_schema.py`)

| Field | Value |
|---|---|
| **Purpose** | Manages the SQLite database schema using `CREATE TABLE IF NOT EXISTS` plus a `schema_version` migration table. Safe to call multiple times — never destroys existing data. |
| **Location** | `scripts/db_schema.py` |
| **Called By** | `update_data.py`, `history_service.py`, `snapshot_service.py` |
| **Dependencies** | Python `sqlite3` |

### Functions

| Function | Purpose | Returns |
|---|---|---|
| `init_db(db_path)` | Opens (or creates) the database, applies all pending migrations, returns an open connection. | `sqlite3.Connection` |
| `get_connection(db_path)` | Opens the database with WAL mode, foreign keys enabled, and `row_factory = sqlite3.Row`. | `sqlite3.Connection` |
| `get_schema_version(conn)` | Returns the current schema version integer (0 if not initialised). | `int` |
| `apply_migrations(conn)` | Applies V1 and V2 migration scripts in order. Idempotent. | None |

### Schema Versions

| Version | Tables Added |
|---|---|
| V1 (Sprint 1) | `schema_version`, `btc_daily`, `fear_greed`, `etf_flows`, `stablecoin_market_cap`, `scores`, `market_regime`, `capital_allocation`, `market_data` |
| V2 (Sprint 2A) | `market_snapshots` (unified daily row with all fields), `build_metadata` (key/value) |

---

## 3. History Service (`history_service.py`)

| Field | Value |
|---|---|
| **Purpose** | Queries the `btc_daily` table and returns JSON-serialisable daily or weekly price history for specified date ranges. |
| **Location** | `scripts/history_service.py` |
| **Called By** | `update_data.py` (to populate `historyDaily` and `historyWeekly` in `live.json`) |
| **Dependencies** | `db_schema.py` |

### Functions

| Function | Purpose | Parameters | Returns |
|---|---|---|---|
| `get_daily_history(db_path, days)` | Returns up to `days` daily rows from `btc_daily`. | `db_path=None`, `days=1465` | `list` of `{day, usd, aud}` |
| `get_weekly_history(db_path, weeks)` | Returns up to `weeks` Monday-anchored weekly rows. | `db_path=None`, `weeks=208` | `list` of `{week, usd, aud}` |
| `query_range(range_key, db_path)` | Returns rows for a named range key with resolution metadata. | `range_key: '7d'|'1m'|'3m'|'6m'|'1y'|'2y'|'4y'` | `dict` (rows, resolution) |
| `_daily_rows(conn, days)` | Internal: queries `btc_daily` for the last N days. | `conn, days` | `list` of dicts |
| `_weekly_rows(conn, weeks)` | Internal: aggregates daily into weekly buckets, returns last N weeks. | `conn, weeks` | `list` of dicts |

### Supported Range Keys

| Key | Resolution | Count |
|---|---|---|
| `7d` | Daily | 7 days |
| `1m` | Daily | 31 days |
| `3m` | Daily | 92 days |
| `6m` | Daily | 184 days |
| `1y` | Weekly | 52 weeks |
| `2y` | Weekly | 104 weeks |
| `4y` | Weekly | 208 weeks |

---

## 4. Snapshot Service (`snapshot_service.py`)

| Field | Value |
|---|---|
| **Purpose** | CRUD and comparison operations on the `market_snapshots` table (V2 schema). Also manages `build_metadata`. |
| **Location** | `scripts/snapshot_service.py` |
| **Called By** | `update_data.py` (`upsert_snapshot`, `set_build_metadata`, `get_build_metadata`) |
| **Dependencies** | `db_schema.py` |

### Functions

| Function | Purpose | Parameters | Returns |
|---|---|---|---|
| `latest_snapshot(db_path)` | Returns the most recent `market_snapshots` row. | `db_path=None` | `dict` or `None` |
| `snapshot(date, db_path)` | Returns the row for an exact date string. | `date='YYYY-MM-DD'`, `db_path=None` | `dict` or `None` |
| `nearest_snapshot(date, db_path)` | Returns the row closest to the given date by calendar distance (ties go earlier). | `date='YYYY-MM-DD'`, `db_path=None` | `dict` or `None` |
| `range_query(start, end, db_path)` | Returns all rows between start and end inclusive, ordered by date. | `start, end: 'YYYY-MM-DD'`, `db_path=None` | `list` of dicts |
| `compare_snapshots(date1, date2, db_path)` | Returns a diff object comparing two snapshots: changes (from/to/delta) and missing fields. | `date1, date2: 'YYYY-MM-DD'`, `db_path=None` | `dict` (date1, date2, snapshot1, snapshot2, changes, missing) |
| `upsert_snapshot(conn, date, fields, now_utc)` | Inserts or replaces a `market_snapshots` row. Missing columns default to NULL. | `conn, date, fields: dict`, `now_utc=None` | None |
| `set_build_metadata(conn, meta_dict)` | Upserts key/value pairs into `build_metadata`. | `conn, meta_dict: dict` | None |
| `get_build_metadata(db_path)` | Returns `build_metadata` as a `{key: value}` dict. | `db_path=None` | `dict` |

---

## 5. Import History (`import_history.py`)

| Field | Value |
|---|---|
| **Purpose** | Bulk import of historical BTC price data into the `btc_daily` table. Used for initial database population and gap-filling. |
| **Location** | `scripts/import_history.py` |
| **Called By** | `update_data.py` (imported as a module), manual execution |
| **Dependencies** | `db_schema.py` |

---

## 6. Backfill History (`backfill_history.py`)

| Field | Value |
|---|---|
| **Purpose** | Utility for backfilling historical data gaps. Fetches missing daily records from external sources and inserts them into the database. |
| **Location** | `scripts/backfill_history.py` |
| **Called By** | Manual execution only |
| **Dependencies** | `db_schema.py`, `import_history.py` |

---

## 7. Build Release (`build_release.py`)

| Field | Value |
|---|---|
| **Purpose** | Staged release builder. Copies all static files to `dist/release/`, runs `update_data.py` in that context to generate fresh `live.json` and `history.db`, then validates the output. Never mutates tracked source files. |
| **Location** | `scripts/build_release.py` |
| **Called By** | GitHub Actions `pages-release.yml` |
| **Dependencies** | `update_data.py`, `verify_release.py` (called separately after) |

### Functions

| Function | Purpose | Returns |
|---|---|---|
| `tracked_status()` | Returns `git status --porcelain` output. | `str` |
| `ensure_tracked_clean(label)` | Raises `RuntimeError` if tracked tree is dirty. | None |
| `clean_generated_temp_files()` | Removes `__pycache__`, `.pyc`, `.pyo`, `.pytest_cache`, `.ruff_cache`. | None |
| `prepare_stage_dir(stage_dir)` | Creates staging directory and copies all static files. | None |
| `run_updater_in_stage(stage_dir)` | Runs `update_data.py` with staging paths. | `(stage_live_path, stage_db_path)` |
| `validate_release_files(stage_dir)` | Checks version strings, required assets, required UI controls. | `bool` (all pass) |
| `main()` | Orchestrates the full build. Exit code 0 on success. | `int` |

---

## 8. Verify Release (`verify_release.py`)

| Field | Value |
|---|---|
| **Purpose** | Post-build release artefact verification. Confirms all required files exist, version strings are consistent, and required UI markers are present in the staged `index.html`. |
| **Location** | `scripts/verify_release.py` |
| **Called By** | GitHub Actions `pages-release.yml` (after `build_release.py`) |
| **Dependencies** | None (reads staged files directly) |

---

## 9. Release Orchestrator (`release.py`)

| Field | Value |
|---|---|
| **Purpose** | Top-level release coordination helper. Orchestrates the sequence of build, verify, and tag operations for a formal release. |
| **Location** | `scripts/release.py` |
| **Called By** | Manual execution by developer |
| **Dependencies** | `build_release.py`, `verify_release.py`, `create_release_tag.py` |

---

## 10. Tag Creator (`create_release_tag.py`)

| Field | Value |
|---|---|
| **Purpose** | Creates a git tag for the current release version after a successful build and verification. Enforces tag naming conventions. |
| **Location** | `scripts/create_release_tag.py` |
| **Called By** | `release.py`, manual execution |
| **Dependencies** | Python `subprocess` (git commands) |

---

## 11. Service Worker (Client-Side Cache Service)

| Field | Value |
|---|---|
| **Purpose** | PWA caching service. Controls which resources are fetched from network vs served from cache, ensuring the app works offline with the last known data. |
| **Location** | `service-worker.js` |
| **Called By** | Browser via `navigator.serviceWorker.register('./service-worker.js')` in `index.html` |
| **Dependencies** | Cache API, Fetch API |

### Cache Strategy

| Resource Type | Strategy | Behaviour |
|---|---|---|
| `index.html`, `live.json`, `manifest.json` | **Network-first** | Always try network; cache on success; serve cache on network failure |
| `*.png` (stable images) | **Cache-first** | Serve from cache if present; fetch and cache if missing |
| All other same-origin requests | **Network with cache fallback** | Try network; serve cache if network fails |

### Constants

| Constant | Value |
|---|---|
| `CACHE_VERSION` | `'8.6.1'` |
| `CACHE_NAME` | `btc-cycle-compass-8.6.1` |
| `STABLE_ASSETS` | `['./bitcoin-compass-base.png', './bitcoin-compass-needle.png']` |

### Lifecycle

| Event | Action |
|---|---|
| `install` | `skipWaiting()` + pre-cache stable images |
| `activate` | Delete all old caches + `clients.claim()` |
| `fetch` | Route by URL pattern to appropriate strategy |

---

## 12. Browser-Side Data Services (Client JavaScript)

These are not Python scripts but constitute the client-side service layer:

| Function | Purpose | Called By |
|---|---|---|
| `refreshLiveData()` | Fetches `data/live.json`, enriches, renders. Auto-repeats every 15 minutes. | Initialisation, refresh buttons |
| `browserFallback()` | Direct browser API calls to 7 external endpoints when `live.json` is unavailable. Constructs minimal DATA object. | `refreshLiveData()` on failure |
| `enrichMissingFeeds(data)` | Patches ETF proxy, events, and news if any are missing from the payload. | `refreshLiveData()` after successful fetch |
| `ensureEtfIndication(data)` | Derives a market-based ETF proxy score from BTC, fear, and stablecoin data when no live proxy is available. | `enrichMissingFeeds()` |
| `fetchBrowserNews()` | Tries rss2json.com (Google News RSS, AU+US) then GDELT to fetch fresh news from the browser. | `enrichMissingFeeds()` |
| `buildCompassAnalysis(question, data)` | Deterministic AI analyst engine. Reads all DATA fields and constructs a structured evidence-based analysis response. | `views.analyst()` |
| `runExternalResearch(question, data)` | POSTs to a user-configured external research endpoint with context and a structured source policy. | `views.analyst()` (optional) |
| `renderAlertsPanel(container)` | Reads alert config, reads live values, renders alert cards with triggered state. | `views.alerts()` |
| `renderHistoryRange(range)` | Selects correct data series, renders SVG chart (line or candlestick), renders records table. | `views.history()`, range buttons |
