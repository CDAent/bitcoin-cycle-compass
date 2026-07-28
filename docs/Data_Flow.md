# Data Flow
## Bitcoin Cycle Compass — Version 8.7 · Sprint 0

---

## 1. Overview

Data in Bitcoin Cycle Compass flows through two independent pipelines:

1. **Server-side Pipeline** — Python scripts running in GitHub Actions fetch external APIs, compute scores, and write static artefacts (`live.json`, `history.db`).
2. **Client-side Pipeline** — The browser fetches `data/live.json`, processes it through JavaScript functions, and renders the UI.

These two pipelines share no runtime connection. The only handoff is the static `data/live.json` file served by GitHub Pages.

---

## 2. Top-Level Data Flow

```
EXTERNAL APIs
     │
     │  HTTP (urllib, scheduled GH Actions)
     ▼
update_data.py
     │
     ├──► data/live.json   ──────────────────────────► Browser fetch (refreshLiveData)
     │                                                       │
     └──► data/history.db  (SQLite, not published)           ▼
                                                        DATA global object
                                                             │
                                                        render() + openDetail(view)
                                                             │
                                                        DOM updates
                                                             │
                                                      User sees dashboard
```

---

## 3. Server-Side Pipeline (Python / GitHub Actions)

### 3.1 Trigger

The pipeline runs on:
- Push to `main` branch (via `pages-release.yml`)
- `workflow_dispatch` (manual trigger)
- Scheduled runs (configured separately, not shown in repository)

### 3.2 Step-by-Step Flow

```
GitHub Actions: pages-release.yml
│
├── [1] Checkout source
├── [2] Setup Python 3.11
├── [3] Clean __pycache__, dist/
├── [4] Confirm tracked tree is clean
├── [5] Run pytest tests/
├── [6] Compile scripts (py_compile)
├── [7] scripts/build_release.py --stage-dir dist/release
│       │
│       ├── [7a] Copy static files → dist/release/
│       │        index.html, manifest.json, service-worker.js, *.png
│       │
│       └── [7b] Run update_data.py --output dist/release/data/live.json
│                                    --db-path dist/release/data/history.db
│                │
│                ├── price_sources()    → Coinbase, Kraken, Bitstamp, CoinGecko
│                │                       Trimmed average / median outlier rejection
│                │
│                ├── fx()              → Frankfurter API (USD → AUD)
│                │
│                ├── fear()            → Alternative.me (last 2 readings)
│                │
│                ├── stablecoins()     → DeFiLlama (30-day chart, 1d/7d/30d changes)
│                │
│                ├── macro()           → FRED CSV (WALCL, M2SL, DGS10, DTWEXBGS, VIXCLS)
│                │                       Computes macro_score from 5 series
│                │
│                ├── chain()           → Blockchain.info (hash-rate, n-transactions, mempool)
│                │                       Computes onchain_score
│                │
│                ├── stooq()           → Stooq CSV (gold, equities, AI proxy)
│                │
│                ├── etf_flow()        → Farside HTML scraper (ETF net flows table)
│                │                       + etf_demand_proxy() → Yahoo Finance (6 ETF tickers)
│                │
│                ├── btc_daily_history_four_years()
│                │                    → Yahoo Finance BTC-USD (4y, 1d interval)
│                │
│                ├── weekly_btc_history()
│                │                    → Aggregates daily into Monday-anchored weeks
│                │
│                ├── news()            → Google News RSS (3 search queries)
│                │                       + article_significance() scoring
│                │
│                ├── events()          → Hardcoded official calendar links
│                │
│                ├── reports_payload() → Summary sections from scores
│                │
│                ├── sync_manifest_versions() → Updates manifest.json in staging
│                │
│                ├── save_daily_to_db()    → SQLite: upsert all V1 tables
│                │
│                ├── write_full_snapshot() → SQLite: upsert market_snapshots (V2)
│                │
│                └── writes data/live.json (all fields assembled)
│
├── [8] scripts/verify_release.py --release-dir dist/release
│       Checks: version strings, required UI controls, required assets
│
├── [9] Confirm tracked tree unchanged
│
├── [10] Upload dist/release as GitHub Pages artefact
│
└── [11] deploy: Deploy to GitHub Pages
```

### 3.3 Score Computation (Server-Side)

Scores are computed in `update_data.py` using weighted composites:

**Macro Score**
```
macro_score = 50
  + clamp(WALCL.change20 × 3, -10, 10)
  + clamp(M2SL.change20 × 4, -10, 10)
  - clamp(DTWEXBGS.change20 × 3, -8, 8)
  - clamp(DGS10.change20 × 1.5, -8, 8)
  - clamp((VIX - 20) × 0.8, -10, 15)
→ clamped to [0, 100]
```

**On-Chain Score**
```
onchain_score = 50
  + clamp(hash-rate.change30d × 0.5, -12, 12)
  + clamp(n-transactions.change30d × 0.4, -12, 12)
  - clamp(mempool-size.change30d × 0.1, -6, 6)
→ clamped to [0, 100]
```

**ETF Flow Score**
```
flow_score = clamp(50 + dailyFlow / 15)
etf_combined = clamp(flow_score × 0.72 + proxy_score × 0.28)
```

**ETF Proxy Score**
```
proxy_score = clamp(50 + weighted_return × 5 + (volume_ratio - 1) × 12)
where weighted_return = dollar-volume-weighted return across 6 ETFs
```

---

## 4. live.json Structure

The output of `update_data.py` is a single JSON file read by the browser:

```json
{
  "generatedAt":     "ISO timestamp",
  "status":          "Live scheduled research snapshot",
  "appVersion":      "8.6.1",
  "buildMeta": {
    "appVersion":    "...",
    "sprint":        "...",
    "gitCommit":     "...",
    "buildDate":     "..."
  },
  "btc": {
    "usd":           number,
    "aud":           number,
    "change24h":     number,
    "method":        "trimmed average / median check",
    "sources":       [{ "name": string, "usd": number }, ...]
  },
  "fx": {
    "usdAud":        number,
    "audUsd":        number
  },
  "fearGreed": {
    "value":         number (0–100),
    "label":         string,
    "change24h":     number
  },
  "stablecoins": {
    "marketCapUsd":  number,
    "change1d":      number (%),
    "change7d":      number (%),
    "change30d":     number (%)
  },
  "etf": {
    "status":        "live" | "stale" | "unavailable",
    "source":        "Farside",
    "sourceUrl":     string,
    "dailyUsdMillions": number | null,
    "date":          "YYYY-MM-DD",
    "fiveDayUsdMillions":   number,
    "twentyDayUsdMillions": number,
    "flowScore":     number,
    "proxy": {
      "status":      "live proxy",
      "score":       number,
      "label":       string,
      "return1d":    number,
      "volumeVs20d": number,
      "aggregateDollarVolumeUsd": number,
      "funds":       [{ "ticker", "close", "return1d", "volume", "volumeVs20d", "dollarVolumeUsd" }, ...]
    },
    "score":         number,
    "scoreSource":   string,
    "dailyAvailable": boolean
  },
  "macro": {
    "WALCL":  { "value": number, "date": "YYYY-MM-DD", "change20": number },
    "M2SL":   { "value": number, "date": "YYYY-MM-DD", "change20": number },
    "DGS10":  { "value": number, "date": "YYYY-MM-DD", "change20": number },
    "DTWEXBGS": { "value": number, "date": "YYYY-MM-DD", "change20": number },
    "VIXCLS": { "value": number, "date": "YYYY-MM-DD", "change20": number },
    "score":  number
  },
  "onchain": {
    "score":   number,
    "metrics": {
      "hash-rate":       { "latest": number, "change30d": number },
      "n-transactions":  { "latest": number, "change30d": number },
      "mempool-size":    { "latest": number, "change30d": number }
    }
  },
  "liquidityScores": {
    "Cash & short-term bills":       number,
    "Government bonds & fixed income": number,
    "Global equities":               number,
    "AI technology":                 number,
    "Emerging markets":              number,
    "Bitcoin":                       number,
    "Stablecoins":                   number,
    "Gold":                          number,
    "Silver":                        number
  },
  "liquidityTrends": {
    "Cash & short-term bills":       number (%),
    "Government bonds & fixed income": number (%),
    "Global equities":               number (%),
    "AI technology":                 number (%),
    "Emerging markets":              number (%),
    "Bitcoin":                       number (%),
    "Stablecoins":                   number (%),
    "Gold":                          number (%),
    "Silver":                        number (%),
    "Other":                         number
  },
  "historyWeekly": [{ "week": "YYYY-MM-DD", "usd": number, "aud": number }, ...],
  "historyDaily":  [{ "day":  "YYYY-MM-DD", "usd": number, "aud": number }, ...],
  "news":   [{ "title", "url", "source", "date", "impactScore", "stars", "impact", "tags", "why" }, ...],
  "events": [{ "tag", "title", "source", "url" }, ...],
  "reports": {
    "status":   "available",
    "sections": [{ "title": string, "summary": string }, ...]
  },
  "proxies": {
    "gold":     { "change20d": number },
    "silver":   { "change20d": number },
    "equities": { "change20d": number },
    "ai":       { "change20d": number },
    "emerging": { "change20d": number },
    "bonds":    { "change20d": number },
    "cash":     { "change20d": number }
  }
}
```

---

## 5. Client-Side Pipeline (Browser)

### 5.1 Initialisation Sequence

```
Browser loads index.html
       │
       ├── [1] HTML parsed, inline <style> applied
       ├── [2] Inline <script> parsed
       │       Global constants defined (APP_VERSION, ALERT_DEFINITIONS)
       │       CUR restored from localStorage
       │
       ├── [3] setCur(CUR) — syncs currency buttons
       ├── [4] setMobileHeaderTitle('dashboard')
       ├── [5] refreshLiveData() called immediately
       │       │
       │       ├── Fetch data/live.json?v=timestamp (cache-busted)
       │       │   Success → DATA = await enrichMissingFeeds(json)
       │       │           → render()
       │       │   Failure → browserFallback()
       │       │               → fetch Coinbase, Kraken, Bitstamp, CoinGecko,
       │       │                  Frankfurter, Alternative.me, DeFiLlama directly
       │       │               → construct minimal DATA object
       │       │               → enrichMissingFeeds()
       │       │               → render()
       │       │
       │       └── setInterval(refreshLiveData, 15 × 60 × 1000) — auto-refresh
       │
       ├── [6] Event listeners bound:
       │       nav-item clicks → openDetail(view)
       │       currency-btn clicks → setCur(currency)
       │       data-open card clicks → openDetail(openTarget)
       │       mobileMenuBtn → toggleMobileDrawer()
       │       Escape key → toggleMobileDrawer(false)
       │
       └── [7] Service worker registered (./service-worker.js)
```

### 5.2 render() — Dashboard Paint

`render()` is called after every successful data fetch. It reads from the `DATA` global and updates all dashboard card DOM elements:

```
render(DATA)
  │
  ├── [Currency conversion]
  │     conv = CUR === 'AUD' ? DATA.fx.usdAud : 1
  │     p = DATA.btc.usd × conv
  │
  ├── [Score computation]
  │     stableScore   = clamp(50 + stablecoins.change7d × 8)
  │     btcLiquidity  = DATA.liquidityScores.Bitcoin ?? computed
  │     research      = 0.24×btcLiquidity + 0.20×macro + 0.18×onchain + 0.18×fear + 0.20×stableScore
  │     regimeScore   = 0.28×macro + 0.22×btcLiquidity + 0.18×fear + 0.16×onchain + 0.16×etfScore
  │
  ├── [Bottom/Peak model]
  │     high = 126200 × conv  (hardcoded reference cycle high)
  │     baseBottom = high × 0.34
  │     bottomProb = clamp(45 + drawdownContrib + sentimentContrib + macroContrib, 20, 88)
  │     peakProb   = clamp(18 + (research - 50) × 0.28 + (regimeScore - 50) × 0.18, 10, 55)
  │
  ├── [Regime classification]
  │     regimeFromScore(regimeScore, prevScore)
  │     → { title, animal, cls, lines, explanation, factors, typical, moveText }
  │
  ├── [DOM updates — Cards]
  │     BTC Price: btcPrice, btcSecondary, btcChange, priceSources, fxLabel
  │     Snapshot:  positiveCount, neutralCount, negativeCount, overallText, overallAnimal
  │     Research:  researchMarker.style.left, researchLabel, confidence
  │     Regime:    regimeAnimal, regimeTitle, regimePoints, regimeScore
  │     Bottom:    bottomProbability, bottomPrice, bottomSevere, bottomBase, bottomShallow
  │     Peak:      peakProbability, peakPrice, peakConservative, peakBase, peakStrong
  │     Fear:      fearNeedle.style.transform, fearValue, fearLabel, fearYesterday
  │     Stable:    stableCap, stable1d, stable7d, stable30d, stableLabel
  │     ETF:       etfValue, etfDirection, etfLabel, etfProxy, etfStatus
  │     Liquidity: liquidityRows (liquidityShares() → HTML)
  │     RegScores: regimeRows (5 metrics → HTML)
  │     Summary:   summaryList (signal bullets → HTML)
  │     News:      newsList (5 headlines → HTML)
  │     Events:    eventsList (4 events → HTML)
  │
  ├── [localStorage]
  │     saveSnapshot(d, research, regimeScore, bottomProb, peakProb)
  │     localStorage.setItem('btcPrevRegimeScore', regimeScore)
  │
  └── [Footer / version stamps]
        sideTimestamp, priceUpdated, footerStatus, sideVersion, footerVersion, document.title
```

### 5.3 openDetail(view) — Detail Panel Flow

```
openDetail('markets' | 'liquidity' | 'onchain' | 'macro' | 'news' |
           'history' | 'analyst' | 'alerts' | 'settings' | 'support' | 'about')
  │
  ├── Set ACTIVE_VIEW = view
  ├── Update all .nav-item active states
  ├── Show #detailPanel (hidden = false)
  ├── Call views[view]()
  │   └── Writes HTML to #detailBody
  │       Uses DATA global (already loaded by render())
  │
  └── Scroll to top
```

### 5.4 Data Enrichment (enrichMissingFeeds)

After fetching `live.json`, the browser patches any missing or unavailable feeds:

```
enrichMissingFeeds(data)
  │
  ├── ensureEtfIndication(data)
  │     If no live ETF proxy: derive score from BTC change, fear, stablecoin
  │
  ├── If data.events is empty: use FALLBACK_EVENTS (hardcoded official calendars)
  │
  └── If data.news is empty:
        fetchBrowserNews()
          ├── Try: rss2json.com → Google News RSS (AU locale)
          ├── Try: rss2json.com → Google News RSS (US locale)
          └── Try: GDELT API (last 3 days)
        If still empty: use 3 hardcoded Google News search links
```

### 5.5 Compass Ai Analyst Data Flow

The analyst is fully deterministic — there is no external LLM call unless the user configures an optional research endpoint.

```
User types question → ask()
  │
  ├── appendAnalystMessage('user', question)
  │
  ├── buildCompassAnalysis(question, DATA)
  │     Reads: DATA.btc, DATA.fearGreed, DATA.stablecoins, DATA.etf,
  │             DATA.liquidityScores, DATA.liquidityTrends, DATA.macro,
  │             DATA.researchScore, DATA.opportunityScore, DATA.regime,
  │             window.__weeklyHistory (merged local + remote weekly data)
  │     Computes: facts[], support[], counter[], interpretation, changeView[], confidence{}
  │     Calls: liquidityShares(), buildEvidenceRegister(), evidenceQuality(),
  │             profileLanguage(), trendInfo()
  │     Returns: analysis object
  │
  ├── renderAnalystAnswer(analysis)
  │     Renders structured answer card into #analystMessages
  │
  └── [If external research enabled]
        runExternalResearch(question, DATA)
          POST → user-configured endpoint
          Body: { question, context, evidenceOnly, sourcePolicy, responseSchema }
          Response: { answer, sources[], conflicts[], excludedClaims[] }
          Renders result as external-result message bubble
```

### 5.6 Alert Data Flow

```
renderAlertsPanel()
  │
  ├── loadAlertConfig() from localStorage
  │
  ├── For each ALERT_DEFINITION:
  │     getLiveAlertValue(key) → reads from DATA global
  │     checkAlertTriggered(item, config, liveValue)
  │     Renders alert card with live value, triggered status, controls
  │
  ├── On toggle/save:
  │     validateAlertInput() → saveAlertConfig() → localStorage
  │
  └── (No push notifications — visual only in this release)
```

### 5.7 History Data Flow

```
openDetail('history')
  │
  ├── DATA.historyWeekly (from live.json) — remote data
  ├── localStorage.btcCompassWeeklyHistory — locally stored snapshots
  ├── Merge: deduplicate by week, sort, cap at 208 weeks
  │     → window.__weeklyHistory
  │
  ├── DATA.historyDaily (from live.json) — 4 years daily
  │
  ├── renderHistoryRange('4y')  (default)
  │     historySeriesFor(range) → selects daily or weekly rows
  │     If mode === 'candlestick': renderCandlestickChart() → inline SVG
  │     If mode === 'line':        inline SVG polyline path
  │     tableRows(records) → HTML table with movement arrows
  │
  └── range buttons → re-call renderHistoryRange(range)
```

### 5.8 Service Worker Cache Flow

```
Browser requests resource
  │
  ├── URL matches index.html / live.json / manifest.json?
  │     → Network-first: try network, cache on success, serve cache on fail
  │
  ├── URL matches *.png (stable image)?
  │     → Cache-first: serve from cache if available, else fetch and cache
  │
  └── All other same-origin requests?
        → Network with cache fallback
```

---

## 6. Data Flow Summary Diagram

```
Dashboard (Browser)
      │
      │  [user opens dashboard / auto-refresh every 15 min]
      ▼
refreshLiveData()
      │
      │  fetch('data/live.json?v=timestamp', {cache:'no-store'})
      ▼
GitHub Pages (static file server)
      │
      │  serves data/live.json (written by update_data.py)
      ▼
enrichMissingFeeds(json)
      │  ├── ensureEtfIndication()   fills ETF proxy if absent
      │  ├── FALLBACK_EVENTS         if no events
      │  └── fetchBrowserNews()      if no news
      ▼
DATA = enriched payload
      │
      ├──► render()
      │      Paints all 13 dashboard cards
      │      Computes research, regime, bottom, peak scores in browser
      │      Saves snapshot to localStorage
      │
      └──► [User navigates to a section]
             openDetail(view)
               │
               ├── markets    → live BTC + forecast model
               ├── liquidity  → capital allocation + stablecoins + ETF
               ├── onchain    → network score + metrics
               ├── macro      → macro score + FRED series
               ├── news       → article cards + event links + pinned
               ├── history    → SVG chart + records table
               ├── analyst    → buildCompassAnalysis() → evidence answer
               │                 [optional] runExternalResearch()
               ├── alerts     → renderAlertsPanel() → threshold cards
               ├── settings   → settings cards
               ├── support    → feedback form → mailto:
               └── about      → glossary + methodology + build meta
```
