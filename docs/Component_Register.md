# Component Register
## Bitcoin Cycle Compass — Version 8.7 · Sprint 0

All components are implemented as JavaScript functions or HTML sections within `index.html`. There are no separate component files — the entire frontend is a single document.

---

## Dashboard Cards (HTML Sections)

### BTC Live Price Card

| Field | Value |
|---|---|
| **Component Name** | BTC Live Price Card |
| **Purpose** | Displays the live Bitcoin price in the selected currency, secondary price, 24h change, exchange sources, FX rate, and last-updated time |
| **Location** | `index.html` — `.card.c-price` section, line ~358 |
| **Element IDs** | `btcPrice`, `btcSecondary`, `btcChange`, `priceSources`, `fxLabel`, `priceUpdated` |
| **Updated By** | `render()` |
| **Data Source** | `DATA.btc`, `DATA.fx` |
| **Related CSS** | `.c-price`, `.live-price`, `.price-top`, `.price-secondary`, `.change24`, `.sources`, `.source`, `.price-foot` |
| **Opens Detail** | `data-open="markets"` |

---

### Today's Snapshot Card

| Field | Value |
|---|---|
| **Component Name** | Today's Snapshot Card |
| **Purpose** | Counts positive, neutral, and negative signals across all inputs; displays overall market signal (Risk On / Risk Off / Mixed) with animal emoji |
| **Location** | `index.html` — `.card.c-snapshot` section |
| **Element IDs** | `positiveCount`, `neutralCount`, `negativeCount`, `overallText`, `overallAnimal` |
| **Updated By** | `render()` |
| **Data Source** | Computed from `DATA.btc`, `DATA.stablecoins`, `DATA.macro`, `DATA.onchain`, `DATA.fearGreed`, `DATA.etf` |
| **Related CSS** | `.c-snapshot`, `.signal-counts`, `.overall`, `.animal`, `.pos`, `.neu`, `.neg` |

---

### Compass AI Research Card

| Field | Value |
|---|---|
| **Component Name** | Compass AI Research Card |
| **Purpose** | Shows the AI research score as a horizontal gradient meter (Weak → Confident) with a sliding marker |
| **Location** | `index.html` — `.card.c-research` section |
| **Element IDs** | `researchMarker`, `researchLabel`, `confidence` |
| **Updated By** | `render()` |
| **Data Source** | Computed `research` score from `render()` (weighted composite of btcLiquidity, macro, onchain, fear, stableScore) |
| **Related CSS** | `.c-research`, `.research-meter`, `.research-scale`, `.research-track`, `.research-marker`, `.research-reading` |

---

### Market Regime Card

| Field | Value |
|---|---|
| **Component Name** | Market Regime Card |
| **Purpose** | Displays the current market regime (Bullish Expansion / Transition Zone / Bear Contraction) with animal emoji, supporting points, and score |
| **Location** | `index.html` — `.card.c-regime` section |
| **Element IDs** | `regimeAnimal`, `regimeTitle`, `regimePoints`, `regimeScore` |
| **Updated By** | `render()`, calls `regimeFromScore()` |
| **Data Source** | Computed `regimeScore` from `render()` |
| **Related CSS** | `.c-regime`, `.regime-wrap`, `.regime-title`, `.regime-points`, `.regime-score` |
| **Dependencies** | `regimeFromScore()`, `normalizeMarketState()`, `marketStateClass()`, `movementClass()` |

---

### Bottom Probability Card

| Field | Value |
|---|---|
| **Component Name** | Bottom Probability Card |
| **Purpose** | Shows estimated bottom probability %, price range, and three scenario estimates (Severe/Base/Shallow) |
| **Location** | `index.html` — `.card.c-bottom` section |
| **Element IDs** | `bottomProbability`, `bottomPrice`, `bottomSevere`, `bottomBase`, `bottomShallow` |
| **Updated By** | `render()` |
| **Data Source** | Computed from BTC price vs cycle high, fear, macro |
| **Related CSS** | `.c-bottom`, `.probability`, `.forecast-range`, `.scenario-mini` |

---

### Next Peak Probability Card

| Field | Value |
|---|---|
| **Component Name** | Next Peak Probability Card |
| **Purpose** | Shows estimated next-cycle-peak confidence % and three price scenario ranges (Conservative/Base/Strong) |
| **Location** | `index.html` — `.card.c-peak` section |
| **Element IDs** | `peakProbability`, `peakPrice`, `peakConservative`, `peakBase`, `peakStrong` |
| **Updated By** | `render()` |
| **Data Source** | Computed from `research`, `regimeScore`, and bottom estimates |
| **Related CSS** | `.c-peak`, `.probability`, `.forecast-range`, `.scenario-mini` |

---

### Fear & Greed Card

| Field | Value |
|---|---|
| **Component Name** | Fear & Greed Card |
| **Purpose** | Semi-circular gauge showing the Alternative.me Fear & Greed Index value and animated needle |
| **Location** | `index.html` — `.card.c-fear` section |
| **Element IDs** | `fearNeedle`, `fearValue`, `fearLabel`, `fearYesterday` |
| **Updated By** | `render()` |
| **Data Source** | `DATA.fearGreed` |
| **Related CSS** | `.c-fear`, `.gauge`, `.gauge-ring`, `.gauge-cover`, `.needle`, `.gauge-value`, `.gauge-label` |
| **Opens Detail** | `data-open="markets"` |

---

### Stablecoin Supply Card

| Field | Value |
|---|---|
| **Component Name** | Stablecoin Supply Card |
| **Purpose** | Shows total stablecoin market cap with 24h/7d/30d percentage changes and a liquidity direction label |
| **Location** | `index.html` — `.card.c-stable` section |
| **Element IDs** | `stableCap`, `stable1d`, `stable7d`, `stable30d`, `stableLabel` |
| **Updated By** | `render()` |
| **Data Source** | `DATA.stablecoins` |
| **Related CSS** | `.c-stable`, `.stable-value` |
| **Opens Detail** | `data-open="liquidity"` |

---

### Bitcoin ETF Flow & Demand Card

| Field | Value |
|---|---|
| **Component Name** | ETF Flow & Demand Card |
| **Purpose** | Displays confirmed ETF daily flow, direction, demand label, proxy trading activity, and flow status |
| **Location** | `index.html` — `.card.c-etf` section |
| **Element IDs** | `etfValue`, `etfDirection`, `etfLabel`, `etfProxy`, `etfStatus` |
| **Updated By** | `render()` |
| **Data Source** | `DATA.etf` |
| **Related CSS** | `.c-etf`, `.etf-value`, `.etf-demand-label` |
| **Opens Detail** | `data-open="liquidity"` |

---

### Global Capital Allocation Card

| Field | Value |
|---|---|
| **Component Name** | Global Capital Allocation Card |
| **Purpose** | Ranked table of 9 asset categories + Other, showing estimated allocation share % and trend direction |
| **Location** | `index.html` — `.card.c-liquidity` section |
| **Element IDs** | `liquidityRows` |
| **Updated By** | `render()`, calls `liquidityShares()` |
| **Data Source** | `DATA.liquidityScores`, `DATA.liquidityTrends` |
| **Related CSS** | `.c-liquidity`, `.rank-head`, `.rank-row`, `.asset-dot`, `.asset-name-wrap`, `.score-pill`, `.trend-up/down/flat` |
| **Dependencies** | `liquidityShares()`, `movementClass()`, `movementArrow()` |
| **Opens Detail** | `data-open="liquidity"` |

---

### Market Regime Scores Card

| Field | Value |
|---|---|
| **Component Name** | Market Regime Scores Card |
| **Purpose** | Shows 5 regime scoring components (Liquidity Momentum, Institutional Buying, Risk Appetite, Macro Tailwind, Cycle Confidence) each as a score with market-state pill and arrow |
| **Location** | `index.html` — `.card.c-regscores` section |
| **Element IDs** | `regimeRows` |
| **Updated By** | `render()` |
| **Data Source** | Computed scores: `btcLiquidity`, `etfScore`, `fear`, `macro`, `research`, `onchain` |
| **Related CSS** | `.c-regscores`, `.reg-row`, `.score-pill`, market-state classes |
| **Dependencies** | `normalizeMarketState()`, `marketStateClass()`, `marketStateArrow()` |
| **Opens Detail** | `data-open="macro"` |

---

### Smart Money Summary Card

| Field | Value |
|---|---|
| **Component Name** | Smart Money Summary Card |
| **Purpose** | 24-hour summary of up to 7 key signals as bullet points (BTC price, stablecoin, macro, on-chain, sentiment, ETF) |
| **Location** | `index.html` — `.card.c-summary` section |
| **Element IDs** | `summaryList` |
| **Updated By** | `render()` |
| **Data Source** | `DATA.btc`, `DATA.stablecoins`, `DATA.macro`, `DATA.onchain`, `DATA.fearGreed`, `DATA.etf` |
| **Related CSS** | `.c-summary`, `.summary-list`, `.summary-item`, `.bullet` |
| **Opens Detail** | `data-open="markets"` |

---

### Major Market Events Card

| Field | Value |
|---|---|
| **Component Name** | Major Market Events Card |
| **Purpose** | Displays up to 4 recent and upcoming market events with tags (UPCOMING/LIVE/RECENT) |
| **Location** | `index.html` — `.card.c-events` section |
| **Element IDs** | `eventsList` |
| **Updated By** | `render()` |
| **Data Source** | `DATA.events` |
| **Related CSS** | `.c-events`, `.events`, `.event`, `.event-tag`, `.event-title` |
| **Opens Detail** | `data-open="news"` |

---

### Market News Card

| Field | Value |
|---|---|
| **Component Name** | Market News Card |
| **Purpose** | Shows the 5 most recent news headlines with star ratings and relative timestamps |
| **Location** | `index.html` — `.card.c-news` section |
| **Element IDs** | `newsList` |
| **Updated By** | `render()` |
| **Data Source** | `DATA.news` |
| **Related CSS** | `.c-news`, `.news-list`, `.news-item`, `.market-stars`, `.stars-filled`, `.stars-empty` |
| **Dependencies** | `sortedNews()`, `starText()`, `starLabel()`, `relativeTime()`, `safeUrl()`, `escapeHtml()` |
| **Opens Detail** | `data-open="news"` |

---

## Navigation Components

### Desktop Sidebar

| Field | Value |
|---|---|
| **Component Name** | Desktop Sidebar |
| **Purpose** | Fixed-left navigation with animated compass logo, section buttons, refresh button, version stamp, and last-updated time |
| **Location** | `index.html` — `<aside class="sidebar">` |
| **Element IDs** | `logoWrap`, `sideRefresh`, `sideVersion`, `sideTimestamp` |
| **Related CSS** | `.sidebar`, `.logo-wrap`, `.logo-stage`, `.logo`, `.logo-needle`, `.nav`, `.nav-item`, `.side-bottom`, `.side-refresh`, `.side-stamp` |
| **Behaviour** | Hidden below 820px breakpoint (replaced by mobile drawer) |

---

### Mobile Shared Header

| Field | Value |
|---|---|
| **Component Name** | Mobile Shared Header |
| **Purpose** | Fixed top header on mobile: compass logo, page title, refresh button, hamburger menu |
| **Location** | `index.html` — `<header id="mobileSharedHeader">` |
| **Element IDs** | `mobileSharedHeader`, `mobileHeaderLogo`, `mobileHeaderTitle`, `mobileHeaderRefresh`, `mobileMenuBtn` |
| **Related CSS** | `.mobile-shared-header`, `.mobile-header-logo`, `.mobile-logo-stage`, `.mobile-logo-base`, `.mobile-logo-needle`, `.mobile-header-title`, `.mobile-menu-btn`, `.refresh-btn` |
| **Behaviour** | Only visible below 820px breakpoint |

---

### Mobile Currency Row

| Field | Value |
|---|---|
| **Component Name** | Mobile Currency Row |
| **Purpose** | AUD / USD currency toggle row displayed below the mobile header |
| **Location** | `index.html` — `<div id="mobileCurrencyRow">` |
| **Element IDs** | `mobileCurrencyRow`, `mobileAudBtn`, `mobileUsdBtn` |
| **Related CSS** | `.mobile-currency-row`, `.mobile-curr-btn` |
| **Dependencies** | `setCur()` |

---

### Mobile Navigation Drawer

| Field | Value |
|---|---|
| **Component Name** | Mobile Navigation Drawer |
| **Purpose** | Off-canvas slide-in navigation drawer with full section list and close button |
| **Location** | `index.html` — `<aside id="mobileDrawer">` and `<div id="mobileNavOverlay">` |
| **Element IDs** | `mobileDrawer`, `mobileNavOverlay`, `mobileDrawerClose` |
| **Related CSS** | `.mobile-drawer`, `.mobile-nav-overlay`, `.mobile-drawer-head`, `.mobile-drawer-nav`, `.mobile-nav-item`, `.mobile-drawer-close` |
| **Dependencies** | `toggleMobileDrawer()` |

---

### Desktop Top Bar

| Field | Value |
|---|---|
| **Component Name** | Desktop Top Bar |
| **Purpose** | Shows app title, refresh button, AUD/USD currency toggle, and live-data indicator dot |
| **Location** | `index.html` — `<div class="topbar">` |
| **Element IDs** | `topRefresh`, `audBtn`, `usdBtn` |
| **Related CSS** | `.topbar`, `.title`, `.toptools`, `.toggle`, `.currency-label`, `.live-dot` |

---

## Detail Panel Components

### Detail Panel Shell

| Field | Value |
|---|---|
| **Component Name** | Detail Panel Shell |
| **Purpose** | Full-screen overlay panel that renders when a nav item or card is clicked |
| **Location** | `index.html` — `<section id="detailPanel">` |
| **Element IDs** | `detailPanel`, `detailTitle`, `detailBody` |
| **Related CSS** | `.detail-panel`, `.detail-head`, `.detail-kicker`, `.detail-grid`, `.detail-card`, `.detail-table`, `.detail-link` |
| **Dependencies** | `openDetail()`, `closeDetail()` |

---

### Markets & Forecasts View

| Field | Value |
|---|---|
| **Component Name** | Markets & Forecasts Detail View |
| **Purpose** | Shows live BTC index, next bottom model, and next peak model with scenario tables; source metadata |
| **Location** | `openDetail()` → `views.markets` in `index.html` |
| **Data Source** | `DATA.btc`, `DATA.fx`, dashboard DOM elements for forecast values |
| **Related CSS** | `.detail-grid`, `.detail-card`, `.source-meta`, `.meta-badge`, `.method-note` |

---

### Global Liquidity View

| Field | Value |
|---|---|
| **Component Name** | Global Liquidity Detail View |
| **Purpose** | Full allocation detail table, stablecoin liquidity, confirmed ETF flows, ETF demand proxy, individual ETF participation |
| **Location** | `openDetail()` → `views.liquidity` in `index.html` |
| **Data Source** | `DATA.liquidityScores`, `DATA.liquidityTrends`, `DATA.stablecoins`, `DATA.etf` |
| **Dependencies** | `liquidityShares()`, `trendInfo()`, `movementClass()`, `selectedCompactUsd()` |
| **Related CSS** | `.detail-grid`, `.allocation-detail-row`, `.allocation-detail-value`, `.allocation-detail-trend` |

---

### On-Chain Metrics View

| Field | Value |
|---|---|
| **Component Name** | On-Chain Metrics Detail View |
| **Purpose** | Network composite score and individual metric cards (hash rate, transactions, mempool) |
| **Location** | `openDetail()` → `views.onchain` in `index.html` |
| **Data Source** | `DATA.onchain` |
| **Related CSS** | `.detail-grid`, `.detail-card`, `.big-score`, `.method-note`, `.source-meta`, `.section-note` |

---

### Macro Economy View

| Field | Value |
|---|---|
| **Component Name** | Macro Economy Detail View |
| **Purpose** | Macro tailwind composite score and five FRED series cards (Fed assets, M2, 10Y yield, DXY, VIX) |
| **Location** | `openDetail()` → `views.macro` in `index.html` |
| **Data Source** | `DATA.macro` |
| **Related CSS** | `.detail-grid`, `.detail-card`, `.big-score` |

---

### Market News & Events View

| Field | Value |
|---|---|
| **Component Name** | Market News & Events Detail View |
| **Purpose** | Full article list with headlines, summaries, source, star ratings, impact tags; official event calendar links; pinned articles section |
| **Location** | `openDetail()` → `views.news` in `index.html` |
| **Element IDs** | `pinnedArticles` |
| **Data Source** | `DATA.news`, `DATA.events`, `localStorage.btcCompassPinnedArticles` |
| **Dependencies** | `sortedNews()`, `marketArticleHtml()`, `pinnedArticlesHtml()`, `bindPinButtons()`, `marketImpactSummary()` |
| **Related CSS** | `.market-article`, `.market-article-headline`, `.market-article-summary`, `.market-article-footer`, `.market-article-source`, `.market-article-rating`, `.market-stars`, `.stars-filled`, `.stars-empty`, `.market-impact`, `.market-tags`, `.market-tag`, `.pin-btn`, `.pinned-section`, `.news-intel-summary` |

---

### History & Trends View

| Field | Value |
|---|---|
| **Component Name** | History & Trends Detail View |
| **Purpose** | Interactive SVG price chart with timeframe selector (1d–4y), candlestick or line mode, and historic records table |
| **Location** | `openDetail()` → `views.history` in `index.html` |
| **Element IDs** | `historyChart`, `historyRecords`, `historyResolution`, `historyTimeframe` |
| **Data Source** | `DATA.historyWeekly`, `DATA.historyDaily`, `localStorage.btcCompassWeeklyHistory` (merged) |
| **Dependencies** | `renderHistoryRange()`, `renderCandlestickChart()`, `historySeriesFor()`, `formatAppDate()` |
| **Related CSS** | `.history-controls`, `.range-btn`, `.history-chart`, `.history-axis`, `.history-line`, `.history-grid`, `.candle-up`, `.candle-down`, `.history-table`, `.move-arrow-up`, `.move-arrow-down`, `.history-header`, `.history-legend`, `.history-reserved-grid` |

---

### Compass Ai Analyst View

| Field | Value |
|---|---|
| **Component Name** | Compass Ai Analyst Detail View |
| **Purpose** | Free-text question interface with quick prompts; deterministic evidence-based analysis (no external LLM); optional external research endpoint integration; analyst emphasis profiles |
| **Location** | `openDetail()` → `views.analyst` in `index.html` |
| **Element IDs** | `analystMessages`, `analystInput`, `analystSend`, `externalResearch`, `evidenceOnly`, `researchStatus`, `analystProfile` |
| **Data Source** | `DATA` global, `localStorage` settings |
| **Dependencies** | `buildCompassAnalysis()`, `renderAnalystAnswer()`, `appendAnalystMessage()`, `runExternalResearch()`, `buildEvidenceRegister()`, `evidenceQuality()`, `profileLanguage()` |
| **Related CSS** | `.analyst-shell`, `.analyst-chat`, `.analyst-messages`, `.analyst-msg`, `.analyst-input-row`, `.analyst-input`, `.analyst-send`, `.quick-prompts`, `.quick-prompt`, `.analyst-note`, `.analyst-research-row`, `.analyst-check`, `.analyst-profile`, `.analyst-select`, `.answer-card`, `.answer-section`, `.evidence-toggle`, `.evidence-panel`, `.evidence-row`, `.reliability-box`, `.fact-badge`, `.evidence-mode` |
| **External Config** | `localStorage.compassResearchEndpoint` — optional private research API |

---

### Alerts View

| Field | Value |
|---|---|
| **Component Name** | Alerts Detail View |
| **Purpose** | Configurable threshold alerts for 9 metrics; local storage only; no push notifications in this version |
| **Location** | `openDetail()` → `views.alerts` in `index.html` |
| **Element IDs** | `alertListBody` |
| **Data Source** | `localStorage.btcAlertConfig`, live values via `getLiveAlertValue()` |
| **Dependencies** | `renderAlertsPanel()`, `loadAlertConfig()`, `saveAlertConfig()`, `getLiveAlertValue()`, `formatLiveAlertValue()`, `checkAlertTriggered()`, `validateAlertInput()`, `ALERT_DEFINITIONS` constant |
| **Related CSS** | `.alert-status-card`, `.alert-dot`, `.alert-card`, `.alert-card-header`, `.alert-card-body`, `.alert-field`, `.alert-live-row`, `.alert-live-comparison`, `.alert-card-actions`, `.btn-sm`, `.alert-error` |

---

### Settings View

| Field | Value |
|---|---|
| **Component Name** | Settings Detail View |
| **Purpose** | Refresh controls, currency selection, external research endpoint config, diagnostics/cache clear, support email config, local data reset |
| **Location** | `openDetail()` → `views.settings` in `index.html` |
| **Element IDs** | `settingsRefresh`, `researchEndpoint`, `saveResearchEndpoint`, `endpointStatus`, `clearCacheReload`, `supportEmail`, `saveSupportEmail`, `supportEmailStatus` |
| **Data Source** | `localStorage` |
| **Dependencies** | `refreshLiveData()`, `clearCacheAndReload()`, `isValidResearchEndpoint()` |
| **Related CSS** | `.settings-grid`, `.settings-card`, `.settings-content`, `.settings-actions`, `.settings-input`, `.primary-btn`, `.currency-btn` |

---

### Feedback & Support View

| Field | Value |
|---|---|
| **Component Name** | Feedback & Support Detail View |
| **Purpose** | Structured bug/feature/general feedback form that opens a pre-filled email draft via `mailto:`; diagnostics inclusion option |
| **Location** | `openDetail()` → `views.support` in `index.html` |
| **Element IDs** | `supportType`, `supportFields`, `supportSubmit`, `supportStatus`, `includeDiagnostics` |
| **Data Source** | `localStorage.compassSupportEmail`, `localStorage.compassSupportDraft` |
| **Related CSS** | `.support-section`, `.support-channel`, `.support-form`, `.support-row`, `.support-actions`, `.support-status`, `.support-diagnostics`, `.support-check`, `.support-destination` |

---

### About & Glossary View

| Field | Value |
|---|---|
| **Component Name** | About & Glossary Detail View |
| **Purpose** | Dashboard reading guide, colour legend, segment glossary (with icons), probability guide, source cadence table, methodology notes, build metadata |
| **Location** | `openDetail()` → `views.about` in `index.html` |
| **Data Source** | `DATA.buildMeta`, `APP_VERSION` constant |
| **Related CSS** | `.glossary-section-title`, `.glossary-card`, `.glossary-icon`, `.glossary-content`, `.glossary-grid`, `.glossary-row`, `.workflow-steps`, `.cadence-table`, `.colour-swatch`, `.source-meta`, `.meta-badge`, `.section-note`, `.method-note` |

---

## JavaScript Service Components (Python Scripts)

### Data Updater

| Field | Value |
|---|---|
| **Component Name** | Data Updater |
| **Location** | `scripts/update_data.py` |
| **Purpose** | Fetches all external APIs, scores signals, writes `data/live.json` and `data/history.db` |
| **Exports** | `data/live.json` (JSON), `data/history.db` (SQLite) |
| **Dependencies** | `db_schema.py`, `history_service.py`, `snapshot_service.py`, `import_history.py` |
| **Called By** | GitHub Actions `pages-release.yml`, `build_release.py` |

---

### Schema Manager

| Field | Value |
|---|---|
| **Component Name** | Schema Manager |
| **Location** | `scripts/db_schema.py` |
| **Purpose** | Creates and migrates the SQLite database schema (v1 → v2) |
| **Exports** | `init_db()`, `get_connection()`, `apply_migrations()`, `get_schema_version()` |
| **Dependencies** | Python `sqlite3` |
| **Called By** | `update_data.py`, `history_service.py`, `snapshot_service.py` |

---

### History Service

| Field | Value |
|---|---|
| **Component Name** | History Service |
| **Location** | `scripts/history_service.py` |
| **Purpose** | Queries the `btc_daily` table for daily/weekly price history in specified date ranges |
| **Exports** | `get_daily_history()`, `get_weekly_history()`, `query_range()` |
| **Dependencies** | `db_schema.py` |
| **Called By** | `update_data.py` |

---

### Snapshot Service

| Field | Value |
|---|---|
| **Component Name** | Snapshot Service |
| **Location** | `scripts/snapshot_service.py` |
| **Purpose** | CRUD operations on `market_snapshots` — insert, query latest, query by date, range query, compare two snapshots, write build metadata |
| **Exports** | `latest_snapshot()`, `snapshot()`, `nearest_snapshot()`, `range_query()`, `compare_snapshots()`, `upsert_snapshot()`, `set_build_metadata()`, `get_build_metadata()` |
| **Dependencies** | `db_schema.py` |
| **Called By** | `update_data.py` |

---

### Build Release

| Field | Value |
|---|---|
| **Component Name** | Build Release |
| **Location** | `scripts/build_release.py` |
| **Purpose** | Copies static files to a staging directory, runs the updater in that directory, validates the result |
| **Exports** | None (CLI tool, exit code 0/1) |
| **Dependencies** | `update_data.py`, `verify_release.py` |
| **Called By** | GitHub Actions `pages-release.yml` |

---

### Service Worker

| Field | Value |
|---|---|
| **Component Name** | Service Worker |
| **Location** | `service-worker.js` |
| **Purpose** | Controls PWA caching: network-first for `index.html`, `live.json`, `manifest.json`; cache-first for images; standard network for everything else |
| **Exports** | None (browser registration via `navigator.serviceWorker.register()`) |
| **Dependencies** | Cache API, Fetch API |
| **Called By** | `index.html` via `navigator.serviceWorker.register('./service-worker.js')` |

---

## LocalStorage State Components

| Key | Purpose | Used By |
|---|---|---|
| `btcCurrency` | Selected display currency (AUD/USD) | `setCur()`, `render()`, all money formatters |
| `btcAlertConfig` | Alert threshold configurations | `renderAlertsPanel()`, `loadAlertConfig()`, `saveAlertConfig()` |
| `btcCompassPinnedArticles` | User-pinned news articles | `getPinnedArticles()`, `togglePinnedArticle()`, `pinnedArticlesHtml()` |
| `btcCompassWeeklyHistory` | Locally stored weekly snapshots | `saveSnapshot()`, `views.history` |
| `btcPrevRegimeScore` | Previous regime score for delta calculation | `render()`, `regimeFromScore()` |
| `compassResearchEndpoint` | External research API URL | `runExternalResearch()`, `views.analyst` |
| `compassExternalResearch` | External research enabled flag | `views.analyst` |
| `compassEvidenceOnly` | Evidence-Based Mode flag | `views.analyst`, `runExternalResearch()` |
| `compassAnalystProfile` | Analyst emphasis (conservative/balanced/opportunistic) | `buildCompassAnalysis()`, `profileLanguage()` |
| `compassSupportEmail` | Support form destination email | `views.support`, `views.settings` |
| `compassSupportDraft` | Support form draft persistence | `views.support` |
