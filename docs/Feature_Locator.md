# Feature Locator
## Bitcoin Cycle Compass — Version 8.7 · Sprint 0

Quick-reference guide to find any feature, function, constant, or section in the codebase. All line numbers refer to the **current version** of the file and may shift as code is added.

---

## How to Use This Document

| Column | Meaning |
|---|---|
| **Feature / Symbol** | The function name, constant, CSS class, or HTML element ID |
| **File** | The file it lives in (path relative to repo root) |
| **Line** | Starting line number |
| **Notes** | Brief description of what it does |

---

## 1. index.html — CSS Design Tokens & Colour System

| Feature / Symbol | File | Line | Notes |
|---|---|---|---|
| `:root` CSS custom properties | `index.html` | 10 | All colour tokens (`--bg`, `--gold`, `--green`, etc.), spacing, and radius variables |
| Base layout (`*`, `html`, `body`) | `index.html` | 11 | Box-sizing reset, background radial gradient, font stack |
| `.app` / `.sidebar` grid | `index.html` | 12 | Two-column app shell: 220px sidebar + fluid main content |
| `.nav` / `.nav-item` / `.nav-item.active` | `index.html` | 12 | Sidebar nav link styles, gold left-border on active |
| `.main` / `.topbar` / `.toggle` | `index.html` | 13 | Main content wrapper, top bar with currency toggle |
| `.dashboard` 12-column grid | `index.html` | 14 | 12-col responsive CSS grid for dashboard cards |
| `.card` base style | `index.html` | 14 | Gradient card background, border, border-radius, box-shadow |
| `.c-snapshot` through `.c-news` grid spans | `index.html` | 14 | `grid-column: span N` for all 13 dashboard cards |
| `.signal-counts` / `.pos` / `.neu` / `.neg` | `index.html` | 15 | Snapshot card layout; green/amber/red utility colour classes |
| `.market-state-*` classes | `index.html` | 15 | Five market-state colour classes: bullish, slightly-bullish, neutral, slightly-bearish, bearish |
| `.big-score` / `.score-denom` | `index.html` | 15 | Large score display (52px font) for research card |
| `.research-meter` / `.research-track` / `.research-marker` | `index.html` | 15 | Gradient slider for research score visualisation |
| `.regime-wrap` / `.regime-score` | `index.html` | 15 | Market regime card layout |
| `.probability` / `.forecast-range` / `.forecast-price` | `index.html` | 15 | Bottom/peak probability number display |
| `.gauge` / `.gauge-ring` / `.needle` | `index.html` | 17 | Fear & Greed semicircle gauge |
| `.stable-value` / `.etf-value` | `index.html` | 18 | Stablecoin and ETF large-value display |
| `.rank-head` / `.rank-row` / `.asset-dot` | `index.html` | 18 | Capital Allocation table layout |
| `.score-pill` | `index.html` | 18 | Coloured pill badge for scores and market state labels |
| `.allocation-detail-row` | `index.html` | 19 | Detail view allocation table row layout |
| `.history-controls` / `.range-btn` / `.history-chart` | `index.html` | 35 | History view chart wrapper and range button row |
| `.candle-up` / `.candle-down` / `.candle-wick` | `index.html` | 37 | Candlestick chart fill and stroke colours |
| `.move-arrow-up` / `.move-arrow-down` | `index.html` | 39 | History table movement arrow colours |
| `.analyst-shell` / `.analyst-chat` / `.analyst-messages` | `index.html` | 40 | Compass Ai Analyst two-column layout |
| `.analyst-msg.user` / `.analyst-msg.ai` | `index.html` | 40 | Chat bubble styles; gold left-border on AI messages |
| `.market-article` / `.market-article-headline` | `index.html` | 23 | News article card layout |
| `.market-stars` / `.stars-filled` / `.stars-empty` | `index.html` | 24 | Star rating display (gold filled, grey empty) |
| `.pin-btn` / `.pin-btn.pinned` | `index.html` | 27–30 | Article pin button — highlighted gold when pinned |
| 1180px responsive breakpoint | `index.html` | 70 | Sidebar narrows, cards reflow to 4-column spans |
| 820px mobile breakpoint | `index.html` | 73 | Sidebar becomes horizontal scroll nav, cards go full-width |

---

## 2. index.html — HTML Structure

| Feature / Symbol | File | Line | Notes |
|---|---|---|---|
| `.app` root element | `index.html` | 333 | Two-column app shell wrapper |
| `<aside class="sidebar">` / `.logo-wrap` | `index.html` | 334–335 | Desktop sidebar: logo, compass needle, nav items |
| `<nav class="nav">` — desktop nav items | `index.html` | 336–348 | All 13 `data-view` nav buttons (dashboard through support) |
| `.side-bottom` / `#sideRefresh` | `index.html` | 349–351 | Sidebar refresh button and build-info stamp |
| `#mobileSharedHeader` | `index.html` | 352 | Mobile sticky header: logo, title, refresh button, menu toggle |
| `#refreshStatus` | `index.html` | 355 | Refresh status message box (hidden by default) |
| `.main` — dashboard cards (`.c-*`) | `index.html` | 356–376 | All 13 dashboard card elements with element IDs |
| `#detailPanel` / `#detailBody` | `index.html` | 377–380 | Detail view overlay panel — hidden until nav item clicked |
| `#mobileNavOverlay` | `index.html` | 383 | Dark overlay behind mobile drawer |
| `#mobileDrawer` — mobile nav items | `index.html` | 384–399 | Mobile drawer with all 13 `data-view` buttons |
| `<script>` block start | `index.html` | 400 | All JavaScript begins here |

---

## 3. index.html — JavaScript Constants & Global State

| Feature / Symbol | File | Line | Notes |
|---|---|---|---|
| `APP_VERSION` | `index.html` | 406 | Version string — must match `service-worker.js`, `manifest.json`, `update_data.py` |
| `MOBILE_TITLES` | `index.html` | 407 | Display title for each view key, used by mobile header |
| `ALERT_STORAGE_KEY` | `index.html` | 408 | `localStorage` key for alert configuration (`'btcAlertConfig'`) |
| `ALERT_DEFINITIONS` | `index.html` | 409–419 | Array of 9 alert definitions with keys, labels, units, bounds, and defaults |
| `DATA` | `index.html` | 420 | Global — holds the parsed `live.json` payload |
| `CUR` | `index.html` | 420 | Global — current display currency (`'AUD'` or `'USD'`), persisted to `localStorage` |
| `ACTIVE_VIEW` | `index.html` | 420 | Global — current active view key (e.g. `'dashboard'`, `'analyst'`) |
| `FALLBACK_EVENTS` | `index.html` | 845 | Hardcoded fallback event links used when `d.events` is absent |

---

## 4. index.html — Utility Functions

| Feature / Symbol | File | Line | Notes |
|---|---|---|---|
| `showLoading(text)` | `index.html` | 402 | Shows loading overlay with optional text |
| `hideLoading()` | `index.html` | 403 | Hides loading overlay |
| `animateCurrentView()` | `index.html` | 404 | Triggers view panel slide-in animation |
| `setRefreshMessage(text, type)` | `index.html` | 421 | Updates the `#refreshStatus` message box |
| `setRefreshButtons({loading, label})` | `index.html` | 422 | Disables/enables all `.js-refresh-btn` elements |
| `clearCacheAndReload()` | `index.html` | 423 | Unregisters service workers, clears cache storage, reloads |
| `money(v, d)` | `index.html` | 424 | Formats number as AUD or USD using `Intl.NumberFormat` |
| `formatAppDate(value)` | `index.html` | 424 | Formats ISO date as DD/MM/YY (AUD) or MM/DD/YY (USD) |
| `usd(v)` | `index.html` | 425 | Formats number as USD with no decimal places |
| `compactMoney(v, c)` | `index.html` | 426 | Compact currency (e.g. `$1.2B`) for large values |
| `fxRate()` | `index.html` | 427 | Returns AUD/USD multiplier from `DATA.fx.usdAud` |
| `selectedFromUsd(v)` | `index.html` | 428 | Converts USD value to selected currency |
| `selectedCompactUsd(v)` | `index.html` | 429 | Compact currency conversion from USD |
| `setMobileHeaderTitle(view)` | `index.html` | 430 | Updates `#mobileHeaderTitle` text from `MOBILE_TITLES` |
| `keepActiveNavVisible(view)` | `index.html` | 431 | Scrolls active nav item into view on mobile horizontal nav |
| `setCur(c)` | `index.html` | 432 | Sets currency, persists to `localStorage`, re-renders |
| `setClass(el, v)` | `index.html` | 434 | Replaces `pos`/`neu`/`neg` class on an element based on score |
| `toggleMobileDrawer(force)` | `index.html` | 435 | Opens/closes mobile navigation drawer with focus trap |
| `scoreLabel(v)` | `index.html` | 437 | Maps score 0–100 to `CONFIDENT` / `POSITIVE` / `BALANCED` / `WEAK` |
| `liquidityShares(scores)` | `index.html` | 438 | Converts raw liquidity score object to percentage allocation array |
| `pctText(v)` | `index.html` | 453 | Formats percentage with sign (e.g. `+1.23%`) |
| `regimeFromScore(v, prevScore)` | `index.html` | 454 | Maps regime score to `{title, animal, cls, lines, explanation, factors, typical, moveText}` |
| `normalizeMarketState(value, label)` | `index.html` | 420 | Normalises market state strings and numeric scores to canonical keys |
| `marketStateClass(state)` | `index.html` | 420 | Maps state key to CSS class (e.g. `'market-state-bullish'`) |
| `marketStateArrow(state)` | `index.html` | 420 | Maps state key to arrow character (`▲`, `➜`, `▼`) |
| `movementClass(v)` / `movementArrow(v)` / `trendInfo(v)` | `index.html` | 420 | Movement direction utilities for trend arrows and CSS classes |
| `escapeHtml(v)` | `index.html` | 456 | Escapes `&`, `<`, `>`, `'`, `"` — **must be used on all external strings** |
| `safeUrl(v)` | `index.html` | 457 | Validates URLs — returns `'#'` for non-`http(s)` or malformed URLs |
| `isValidResearchEndpoint(url)` | `index.html` | 458 | Validates private research endpoint (must be production, not localhost) |
| `relativeTime(v)` | `index.html` | 459 | Returns human-readable relative time (`now`, `5m`, `2h`, `3d`) |
| `formatArticleTime(v)` | `index.html` | 460 | Formats article date as locale-appropriate datetime string |

---

## 5. index.html — News & Article Functions

| Feature / Symbol | File | Line | Notes |
|---|---|---|---|
| `starText(n)` | `index.html` | 461 | Renders filled/empty star HTML for article significance rating |
| `starLabel(n)` | `index.html` | 465 | Maps star count to impact label (e.g. `'Critical Global Impact'`) |
| `sortedNews(items)` | `index.html` | 467 | Returns news items sorted newest-first by `date` |
| `marketArticleHtml(n, fromPinned)` | `index.html` | 468 | Renders a full article card HTML string with stars, tags, pin button |
| `marketImpactSummary(items)` | `index.html` | 486 | Returns bullet summary of top ≥4-star articles |
| `articleKey(n)` | `index.html` | 487 | Derives a stable unique key for an article (for pin storage) |
| `getPinnedArticles()` | `index.html` | 493 | Reads pinned articles array from `localStorage` |
| `savePinnedArticles(items)` | `index.html` | 499 | Writes pinned articles array to `localStorage` |
| `isPinnedArticle(n)` | `index.html` | 508 | Returns `true` if article is currently pinned |
| `togglePinnedArticle(n)` | `index.html` | 512 | Pins or unpins an article and saves to `localStorage` |
| `refreshPinnedUI()` | `index.html` | 518 | Re-renders the pinned articles list in the News detail view |
| `bindPinButtons()` | `index.html` | 531 | Attaches pin-button click handlers after news HTML is rendered |
| `pinnedArticlesHtml()` | `index.html` | 544 | Renders the pinned articles section HTML |

---

## 6. index.html — Snapshot, Alerts & Score Utilities

| Feature / Symbol | File | Line | Notes |
|---|---|---|---|
| `saveSnapshot(d, research, regime, bottom, peak)` | `index.html` | 551 | Saves weekly price/score snapshot to `localStorage` (rolling 208 weeks) |
| `tableRows(rows)` | `index.html` | 552 | Renders a `<table><tbody>` from `[[label, value], ...]` pairs |
| `defaultAlertConfig()` | `index.html` | 553 | Returns default alert configuration from `ALERT_DEFINITIONS` |
| `loadAlertConfig()` | `index.html` | 554 | Reads and validates alert config from `localStorage` |
| `saveAlertConfig(cfg)` | `index.html` | 555 | Persists alert config to `localStorage` |
| `validateAlertInput(item, enabled, rawValue)` | `index.html` | 556 | Validates alert threshold input — returns error string or `''` |
| `getLiveAlertValue(key)` | `index.html` | 557 | Extracts current live value for an alert key from `DATA` |
| `formatLiveAlertValue(item, val)` | `index.html` | 571 | Formats a live alert value for display |
| `checkAlertTriggered(item, row, val)` | `index.html` | 577 | Returns `true` if alert threshold condition is currently met |
| `renderAlertsPanel(container)` | `index.html` | 582 | Renders the full Alerts detail view into a container element |

---

## 7. index.html — History & Charting

| Feature / Symbol | File | Line | Notes |
|---|---|---|---|
| `historySeriesFor(range)` | `index.html` | 667 | Returns the appropriate data rows and resolution label for a range key (`'1d'` through `'4y'`) |
| `renderCandlestickChart(chartEl, rows, fxConvert)` | `index.html` | 678 | Renders an SVG candlestick chart into a container element |
| `renderHistoryRange(range)` | `index.html` | 680 | Orchestrates chart + table rendering for the selected history range |

---

## 8. index.html — Compass Ai Analyst

| Feature / Symbol | File | Line | Notes |
|---|---|---|---|
| `appendAnalystMessage(type, text)` | `index.html` | 684 | Appends a chat bubble to `#analystMessages` and scrolls to bottom |
| `percentile(values, current)` | `index.html` | 685 | Returns percentile rank of `current` within `values` array |
| `evidenceSource(name, type, rating, value, date, url)` | `index.html` | 686 | Constructs an evidence source record object |
| `buildEvidenceRegister(d)` | `index.html` | 687 | Builds the full evidence register from `DATA` for analyst context |
| `evidenceQuality(evidence)` | `index.html` | 698 | Scores overall evidence quality and returns quality label |
| `profileLanguage(profile)` | `index.html` | 702 | Returns tone/language descriptor for analyst profile (`conservative`, `balanced`, `opportunistic`) |
| `buildCompassAnalysis(question, d)` | `index.html` | 707 | Deterministic local analyst — generates structured answer with facts, interpretation, risks, uncertainty |
| `renderAnalystAnswer(a)` | `index.html` | 742 | Renders a structured analyst answer object as HTML into the chat |
| `runExternalResearch(question, d)` | `index.html` | 749 | Calls user-configured private research endpoint; appends result to chat |

---

## 9. index.html — Navigation, Views & Render

| Feature / Symbol | File | Line | Notes |
|---|---|---|---|
| `openDetail(view)` | `index.html` | 765 | Main view dispatcher — sets `ACTIVE_VIEW`, updates nav, renders selected view into `#detailBody` |
| `views.markets` | `index.html` | 767 | Markets & Forecasts detail view |
| `views.liquidity` | `index.html` | 768 | Global Liquidity detail view (allocation, stablecoins, ETF flows, proxy) |
| `views.onchain` | `index.html` | 769 | On-Chain Metrics detail view (score + per-metric cards) |
| `views.macro` | `index.html` | 770 | Macro Economy detail view (FRED series tables) |
| `views.news` | `index.html` | 771 | Market News & Events detail view (articles, events, pinned) |
| `views.history` | `index.html` | 772 | History & Trends detail view (candlestick chart, range buttons, table) |
| `views.reports` | `index.html` | 773 | Reports detail view (summary sections from `live.json`) |
| `views.analyst` | `index.html` | 774 | Compass Ai Analyst detail view (chat, quick prompts, profile, research toggle) |
| `views.alerts` | `index.html` | 775 | Alerts detail view (delegates to `renderAlertsPanel`) |
| `views.settings` | `index.html` | 776 | Settings detail view (currency, research endpoint, cache clear, reset) |
| `views.support` | `index.html` | 778 | Feedback & Support detail view (bug/feature/general form, email draft) |
| `views.about` | `index.html` | 779 | About & Glossary detail view |
| `closeDetail()` | `index.html` | 814 | Returns to dashboard, hides `#detailPanel`, sets Dashboard nav active |
| `render()` | `index.html` | 816 | Core render function — populates all 13 dashboard cards from `DATA` |

---

## 10. index.html — Data Fetching & Fallback

| Feature / Symbol | File | Line | Notes |
|---|---|---|---|
| `getJson(url)` | `index.html` | 844 | Fetch wrapper — `cache: 'no-store'`, throws on non-OK status |
| `ensureEtfIndication(d)` | `index.html` | 851 | Synthesises a market-proxy ETF score if `d.etf.proxy` is absent |
| `fetchBrowserNews()` | `index.html` | 862 | Fetches news from rss2json.com (AU then US locale), then GDELT as last resort |
| `enrichMissingFeeds(d)` | `index.html` | 885 | Fills empty `news`/`events` fields in `d` by calling `fetchBrowserNews()` |
| `browserFallback()` | `index.html` | 891 | Full browser-side fallback — calls 7 APIs via `Promise.allSettled`, returns synthetic `DATA` object |
| `refreshLiveData(manual)` | `index.html` | 913 | Main data refresh entry point — fetches `live.json`, falls back to `browserFallback()`, calls `render()` |

---

## 11. scripts/update_data.py — Python Data Pipeline

| Feature / Symbol | File | Line | Notes |
|---|---|---|---|
| `ROOT` / `OUT` constants | `scripts/update_data.py` | 7–8 | Repo root path; `data/live.json` output path |
| `get(url, timeout)` | `scripts/update_data.py` | 29 | HTTP GET wrapper returning response text |
| `jget(url)` | `scripts/update_data.py` | 32 | HTTP GET returning parsed JSON |
| `clamp(x, a, b)` | `scripts/update_data.py` | 33 | Clamps value to `[a, b]` range |
| `pct(a, b)` | `scripts/update_data.py` | 34 | Percentage change `(a/b - 1) * 100` |
| `safe(fn, default)` | `scripts/update_data.py` | 36 | Exception-safe wrapper — returns `default` on any error |
| `price_sources()` | `scripts/update_data.py` | 40 | Fetches BTC price from Coinbase, Kraken, Bitstamp, CoinGecko; returns median-filtered average |
| `fx()` | `scripts/update_data.py` | 60 | Fetches USD/AUD rate from Frankfurter API |
| `fear()` | `scripts/update_data.py` | 64 | Fetches Fear & Greed Index from Alternative.me |
| `stablecoins()` | `scripts/update_data.py` | 69 | Fetches stablecoin supply chart from DeFiLlama; computes 1d/7d/30d changes |
| `fred(series)` | `scripts/update_data.py` | 81 | Fetches a single FRED time series CSV; returns latest value + 20-period change |
| `macro()` | `scripts/update_data.py` | 90 | Fetches all 5 FRED series; computes macro composite score |
| `chain()` | `scripts/update_data.py` | 105 | Fetches 3 Blockchain.info on-chain metrics; computes on-chain composite score |
| `stooq(symbol)` | `scripts/update_data.py` | 115 | Fetches daily CSV from Stooq for a traditional market proxy symbol |
| `_TableParser` | `scripts/update_data.py` | 131 | HTML parser for Farside ETF flow table |
| `_parse_farside(url)` | `scripts/update_data.py` | 146 | Scrapes Farside ETF flow page; returns `{date, usdMillions}` list |
| `_yahoo_etf(ticker)` | `scripts/update_data.py` | 163 | Fetches 1-month daily OHLCV for one ETF ticker from Yahoo Finance |
| `etf_demand_proxy()` | `scripts/update_data.py` | 174 | Computes ETF demand proxy score from 6 ETF tickers |
| `etf_flow(previous)` | `scripts/update_data.py` | 188 | Fetches ETF net flow from Farside; computes 5-day and 20-day totals |
| `btc_daily_history_four_years()` | `scripts/update_data.py` | 254 | Fetches 4 years of daily BTC/USD history from Yahoo Finance |
| `daily_btc_history()` | `scripts/update_data.py` | 270 | Queries `btc_daily` for daily history records |
| `weekly_btc_history()` | `scripts/update_data.py` | 273 | Queries `btc_daily` for weekly history records |
| `article_significance(title, source)` | `scripts/update_data.py` | 282 | Rule-based news significance scorer — returns 1–5 star rating |
| `news()` | `scripts/update_data.py` | 307 | Fetches 3 Google News RSS feeds; scores articles; returns top 20 |
| `events()` | `scripts/update_data.py` | 325 | Returns list of curated official event calendar links |
| `_APP_VERSION` | `scripts/update_data.py` | 333 | Version string — must match `APP_VERSION` in `index.html` |
| `_SPRINT` | `scripts/update_data.py` | 334 | Sprint number written into `live.json` build metadata |
| `reports_payload(scores, trends, etf, macro, onchain)` | `scripts/update_data.py` | 337 | Builds the `reports` section of `live.json` |
| `sync_manifest_versions(manifest_path)` | `scripts/update_data.py` | 363 | Updates `manifest.json` to match `_APP_VERSION` |
| `_git_commit()` | `scripts/update_data.py` | 386 | Returns current git commit hash for build metadata |
| `save_daily_to_db(conn, ...)` | `scripts/update_data.py` | 398 | Upserts today's metrics row into V1 SQLite tables |
| `write_full_snapshot(conn, ...)` | `scripts/update_data.py` | 494 | Builds and writes the complete `live.json` payload; also upserts V2 snapshot |
| `_db_history(db_path)` | `scripts/update_data.py` | 610 | Returns `(historyDaily, historyWeekly)` tuple for `live.json` |
| `parse_args()` / `main()` | `scripts/update_data.py` | 633/641 | CLI argument parser and main entry point |

---

## 12. scripts/db_schema.py — SQLite Schema

| Feature / Symbol | File | Line | Notes |
|---|---|---|---|
| `CURRENT_VERSION` | `scripts/db_schema.py` | 12 | Current schema version (2) — increment when adding migrations |
| `_SCHEMA_V1` | `scripts/db_schema.py` | 17 | V1 schema: 9 tables — `btc_daily`, `fear_greed`, `etf_flows`, `stablecoin_market_cap`, `scores`, `market_regime`, `capital_allocation`, `market_data`, `schema_version` |
| `_SCHEMA_V2` | `scripts/db_schema.py` | 107 | V2 additions: `market_snapshots` (unified row per day) + `build_metadata` (key/value) |
| `get_connection(db_path)` | `scripts/db_schema.py` | 218 | Returns a `sqlite3.Connection` with WAL mode and row factory |
| `get_schema_version(conn)` | `scripts/db_schema.py` | 229 | Returns integer schema version from `schema_version` table |
| `apply_migrations(conn)` | `scripts/db_schema.py` | 240 | Runs outstanding migrations to bring schema to `CURRENT_VERSION` |
| `init_db(db_path)` | `scripts/db_schema.py` | 254 | Creates DB file, applies V1 schema, runs migrations, returns connection |

---

## 13. scripts/history_service.py — Price History Queries

| Feature / Symbol | File | Line | Notes |
|---|---|---|---|
| `_daily_rows(conn, days)` | `scripts/history_service.py` | 36 | Internal — fetches last N daily rows from `btc_daily` |
| `_weekly_rows(conn, weeks)` | `scripts/history_service.py` | 46 | Internal — aggregates weekly OHLCV from `btc_daily` |
| `query_range(range_key, db_path)` | `scripts/history_service.py` | 62 | Returns rows for a named range (`'4y'`, `'1y'`, etc.) |
| `get_daily_history(db_path, days)` | `scripts/history_service.py` | 87 | Returns up to 1465 daily rows for `historyDaily` in `live.json` |
| `get_weekly_history(db_path, weeks)` | `scripts/history_service.py` | 96 | Returns up to 208 weekly rows for `historyWeekly` in `live.json` |

---

## 14. scripts/snapshot_service.py — V2 Snapshot CRUD

| Feature / Symbol | File | Line | Notes |
|---|---|---|---|
| `_row_to_dict(row)` | `scripts/snapshot_service.py` | 22 | Converts a sqlite3 `Row` to a plain dict |
| `latest_snapshot(db_path)` | `scripts/snapshot_service.py` | 29 | Returns the most recent `market_snapshots` row |
| `snapshot(date, db_path)` | `scripts/snapshot_service.py` | 41 | Returns the snapshot for a specific ISO date |
| `nearest_snapshot(date, db_path)` | `scripts/snapshot_service.py` | 53 | Returns the closest snapshot to a given date |
| `range_query(start, end, db_path)` | `scripts/snapshot_service.py` | 81 | Returns all snapshots between two ISO dates |
| `compare_snapshots(date1, date2, db_path)` | `scripts/snapshot_service.py` | 97 | Returns side-by-side comparison of two snapshot dates |
| `upsert_snapshot(conn, date, fields, now_utc)` | `scripts/snapshot_service.py` | 143 | Inserts or replaces a snapshot row for a given date |
| `set_build_metadata(conn, meta_dict)` | `scripts/snapshot_service.py` | 162 | Writes key/value pairs to `build_metadata` table |
| `get_build_metadata(db_path)` | `scripts/snapshot_service.py` | 176 | Reads all `build_metadata` key/value pairs as a dict |

---

## 15. scripts/build_release.py — Staged Release Builder

| Feature / Symbol | File | Line | Notes |
|---|---|---|---|
| `STATIC_FILES` | `scripts/build_release.py` | 12 | List of files copied from repo root to `dist/release/` |
| `fail(message)` | `scripts/build_release.py` | 21 | Prints failure message and exits with code 1 |
| `ensure_tracked_clean(label)` | `scripts/build_release.py` | 49 | Asserts no uncommitted changes to tracked files |
| `clean_generated_temp_files()` | `scripts/build_release.py` | 56 | Removes `__pycache__`, `.pyc`, and `dist/` before build |
| `prepare_stage_dir(stage_dir)` | `scripts/build_release.py` | 70 | Creates `dist/release/` and copies `STATIC_FILES` into it |
| `run_updater_in_stage(stage_dir)` | `scripts/build_release.py` | 82 | Runs `update_data.py` with `--out` pointed at staging dir |
| `validate_release_files(stage_dir)` | `scripts/build_release.py` | 105 | Verifies all required assets exist and `live.json` is parseable |
| `main()` | `scripts/build_release.py` | 150 | Orchestrates the full staged build sequence |

---

## 16. scripts/verify_release.py — Release Validation

| Feature / Symbol | File | Line | Notes |
|---|---|---|---|
| `check(condition, label, failures)` | `scripts/verify_release.py` | 29 | Appends `label` to `failures` if `condition` is `False` |
| `verify_db_bootstrap(failures)` | `scripts/verify_release.py` | 37 | Confirms `history.db` can be initialised and queried in staging dir |
| `main()` | `scripts/verify_release.py` | 69 | Runs all checks; prints pass/fail; exits non-zero on any failure |

---

## 17. service-worker.js — PWA Cache Strategy

| Feature / Symbol | File | Line | Notes |
|---|---|---|---|
| `CACHE_VERSION` | `service-worker.js` | 1 | Cache name prefix — must match app version; increment to bust caches |
| `isNetworkFirst(url)` | `service-worker.js` | 8 | Returns `true` for `live.json` and `manifest.json` — always fetched fresh |
| `isStableImage(url)` | `service-worker.js` | 17 | Returns `true` for `.png` assets — served cache-first |
| `install` event listener | `service-worker.js` | 24 | Pre-caches core shell assets on install |
| `activate` event listener | `service-worker.js` | 31 | Deletes stale caches on activation |
| `fetch` event listener | `service-worker.js` | 41 | Routes requests: network-first for data/manifest, cache-first for images, stale-while-revalidate for everything else |

---

## 18. localStorage Keys — Quick Reference

| Key | Set By | Read By | Purpose |
|---|---|---|---|
| `btcCurrency` | `setCur()` L432 | `CUR` init L420, `setCur()` | Selected display currency (`'AUD'` or `'USD'`) |
| `btcAlertConfig` | `saveAlertConfig()` L555 | `loadAlertConfig()` L554 | User-configured alert thresholds |
| `btcCompassPinnedArticles` | `savePinnedArticles()` L499 | `getPinnedArticles()` L493 | Pinned news article objects |
| `btcCompassWeeklyHistory` | `saveSnapshot()` L551 | `views.history` L772 | Rolling 208-week local price/score history |
| `btcPrevRegimeScore` | `render()` L816 | `regimeFromScore()` L454 | Previous regime score for week-on-week change |
| `compassResearchEndpoint` | `views.settings` L776 | `runExternalResearch()` L749 | User's private research API URL |
| `compassExternalResearch` | `views.analyst` L774 | `views.analyst` L774 | Boolean — enable external research calls |
| `compassEvidenceOnly` | `views.analyst` L774 | `buildCompassAnalysis()` L707 | Boolean — evidence-based mode |
| `compassAnalystProfile` | `views.analyst` L774 | `buildCompassAnalysis()` L707 | Analyst emphasis (`'conservative'`, `'balanced'`, `'opportunistic'`) |
| `compassSupportEmail` | `views.settings` L776 | `views.support` L778 | Support destination email address |
| `compassSupportDraft` | `views.support` L778 | `views.support` L778 | Auto-saved support form draft |
