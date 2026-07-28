# Technical Debt Register
## Bitcoin Cycle Compass — Version 8.7 · Sprint 0

This register tracks known issues, architectural limitations, and deferred improvements. It is a living document and should be updated when new debt is identified or when existing debt is resolved.

**Status values**: `open` · `in-progress` · `resolved` · `accepted` (won't fix)

---

## 1. Known Issues

### TD-001 — Monolithic index.html

| Field | Value |
|---|---|
| **Category** | Architecture |
| **Severity** | High |
| **Status** | Open |
| **Sprint** | Deferred — requires significant refactor |

**Description**  
The entire frontend — all HTML structure, all CSS (≈ 330 lines), all JavaScript (≈ 530 lines) — lives in a single `index.html` file (148KB). There is no build step, no bundler, and no module system.

**Impact**  
- The file is difficult to navigate
- No code splitting or lazy loading possible
- Changes to CSS risk unintended side effects on unrelated sections
- No IDE-level component isolation or scoped linting
- Duplication of logic between Python computation and JS re-computation

**Resolution Path**  
Extract CSS to a dedicated `styles.css`. Extract JS to `app.js` or multiple ES modules. Introduce a lightweight build step (Vite or esbuild) that outputs a single-file release for GitHub Pages compatibility.

---

### TD-002 — No URL Router

| Field | Value |
|---|---|
| **Category** | Architecture |
| **Severity** | Medium |
| **Status** | Open |
| **Sprint** | Deferred |

**Description**  
Navigation between views is managed entirely by JavaScript state (`ACTIVE_VIEW`). There are no URL changes when the user switches between the Dashboard, History, Reports, or detail panels.

**Impact**  
- Browser Back button does not work for in-app navigation
- Cannot deep-link to a specific view
- Cannot share a URL that opens a specific detail panel
- No integration with browser history API

**Resolution Path**  
Implement a hash-based or History API router (`window.location.hash` or `history.pushState`) that reflects the current view in the URL.

---

### TD-003 — Hardcoded Cycle High Reference

| Field | Value |
|---|---|
| **Category** | Data accuracy |
| **Severity** | Medium |
| **Status** | Open |
| **Sprint** | Deferred |

**Description**  
The bottom and peak probability models in `render()` use a hardcoded reference cycle high of `$126,200` USD.

```js
const CYCLE_HIGH_REF = 126200;
```

**Impact**  
- When the actual cycle high becomes known, this constant will be incorrect
- Probabilities will diverge from reality if BTC meaningfully exceeds or undershoots the reference
- No mechanism for the user to configure this value without editing the source

**Resolution Path**  
Make `CYCLE_HIGH_REF` a user-configurable setting stored in `localStorage`. Provide a settings panel to adjust it. Alternatively, derive it dynamically from the 4-year price history when the actual cycle high is confirmed.

---

### TD-004 — history.db Not Published to Browser

| Field | Value |
|---|---|
| **Category** | Feature limitation |
| **Severity** | Medium |
| **Status** | Accepted |

**Description**  
The SQLite database (`history.db`) is a build-time artefact only. The browser never has access to it. All history delivered to the browser comes through the `historyDaily` and `historyWeekly` arrays in `live.json`, which are limited by the size of the JSON payload.

**Impact**  
- Cannot query arbitrary date ranges from the browser
- All historical analysis must be pre-computed server-side
- The History page is limited to whatever is pre-included in `live.json`

**Resolution Path**  
Options: (a) Publish `history.db` as a binary and use `sql.js` in the browser — large download; (b) Generate a set of pre-computed JSON fragments indexed by time period; (c) Accept current limitation as appropriate for a single-user static app.

---

### TD-005 — No Push Notifications for Alerts

| Field | Value |
|---|---|
| **Category** | Feature limitation |
| **Severity** | Low |
| **Status** | Open |

**Description**  
The alert system (`ALERT_DEFINITIONS`) evaluates conditions and displays in-page alerts. There is no push notification mechanism to alert the user when conditions change while they are not looking at the app.

**Impact**  
- User must visit the app to see alerts
- Critical signals (e.g. Fear & Greed entering extreme levels) may be missed

**Resolution Path**  
Implement Web Push notifications using a push service (e.g. OneSignal, Firebase, or a lightweight self-hosted push relay). Requires a service worker push handler and a subscription mechanism.

---

### TD-006 — External Research Requires Private Server

| Field | Value |
|---|---|
| **Category** | Feature dependency |
| **Severity** | Low |
| **Status** | Accepted |

**Description**  
The Compass Ai Analyst's evidence-ranked research mode requires the user to run and configure a private API endpoint. The application does not provide this service.

**Impact**  
- The research feature is non-functional for users without a private endpoint configured
- The deterministic local analyst mode works without it, but the external research mode is a dependency on infrastructure the user must self-provision

**Resolution Path**  
Accept as a conscious design decision — the external research feature is explicitly optional and the application is fully functional without it.

---

### TD-007 — No Offline-First Data Architecture

| Field | Value |
|---|---|
| **Category** | Architecture |
| **Severity** | Low |
| **Status** | Open |

**Description**  
The service worker is network-first for data files. When offline, the app displays stale data from cache without clear indication of how stale it is. The build timestamp in `live.json` is shown, but the UX could be clearer.

**Impact**  
- Users may act on data hours or days old without realising
- PWA offline experience is functional but not optimal

**Resolution Path**  
Add a staleness banner that computes `now - live.json build time` and warns the user if data is more than a configured threshold (e.g. 4 hours) old.

---

## 2. Future Improvements

### TD-010 — Split JavaScript into ES Modules

| Field | Value |
|---|---|
| **Category** | Architecture |
| **Severity** | High |
| **Status** | Open |
| **Sprint** | Target: Sprint 2 or later |

Separate the inline JS into ES module files:
- `app.js` — bootstrap and state
- `data.js` — fetch and enrichment
- `render.js` — render and DOM update
- `analyst.js` — Compass Ai Analyst
- `alerts.js` — alert evaluation and UI
- `history.js` — history and trends

Use a bundler (Vite/esbuild) to concatenate back to a single file for the GitHub Pages deployment.

---

### TD-011 — Extract CSS to a Dedicated File

| Field | Value |
|---|---|
| **Category** | Architecture |
| **Severity** | Medium |
| **Status** | Open |
| **Sprint** | Target: Sprint 2 or later |

Move the `<style>` block from `index.html` to `styles.css`. This enables:
- CSS linting (Stylelint)
- Better IDE support
- Easier review of theme changes
- Potential for CSS modules if components are separated

---

### TD-012 — Configurable Score Weights

| Field | Value |
|---|---|
| **Category** | Feature |
| **Severity** | Medium |
| **Status** | Open |
| **Sprint** | Target: Sprint 3 or later |

The weighted composite score uses hardcoded weights in `update_data.py` and in the browser `render()` function. Future work could expose these as user-configurable values with a settings panel.

---

### TD-013 — Paginated News Loading

| Field | Value |
|---|---|
| **Category** | Performance |
| **Severity** | Low |
| **Status** | Open |

Currently up to 20 news articles are fetched and included in `live.json`. The News section renders all of them at once. Future work could lazy-load additional articles on scroll.

---

### TD-014 — Duplicated Score Computation

| Field | Value |
|---|---|
| **Category** | Architecture |
| **Severity** | Medium |
| **Status** | Open |

The weighted composite score computation exists in two places:
1. `update_data.py` (Python) — produces the server-side score stored in `live.json`
2. `render()` in `index.html` (JavaScript) — re-derives the research score, regime score, bottom score, and peak score from raw DATA fields

If the weighting logic diverges between Python and JS, the UI will display scores inconsistent with the stored values. A single source of truth would reduce this risk.

**Resolution Path**  
Compute all scores server-side in Python and publish them to `live.json`. The JS render function reads stored scores and does not re-derive them.

---

## 3. Deferred Work

### TD-020 — Reports Page Not Integrated into Primary Navigation

| Field | Value |
|---|---|
| **Category** | UX |
| **Severity** | Low |
| **Status** | Open |

The Reports view exists in the codebase but does not appear in the primary nav for all screen sizes. It is accessible via the data-view attribute but may not be immediately discoverable.

---

### TD-021 — Alert Notification Persistence

| Field | Value |
|---|---|
| **Category** | Feature |
| **Severity** | Low |
| **Status** | Open |

Alert state is computed from current data on each render. There is no persistent history of which alerts fired and when. Future work could log alert events to `localStorage` with timestamps.

---

### TD-022 — ETF Farside Scraper Fragility

| Field | Value |
|---|---|
| **Category** | Data reliability |
| **Severity** | Medium |
| **Status** | Open |

The ETF flow data from Farside is obtained by HTML scraping. If Farside changes their page structure, the scraper will silently fail and ETF flow data will be absent from `live.json`. The staleness detection (> 4 days = stale) provides a partial guard.

**Resolution Path**  
Add automated assertions on the scraped structure. Add a fallback ETF flow data source. Alert (in `live.json`) when ETF flow data has not been successfully scraped for > 2 consecutive runs.

---

### TD-023 — FRED API Cadence Mismatch

| Field | Value |
|---|---|
| **Category** | Data quality |
| **Severity** | Low |
| **Status** | Accepted |

Some FRED series (e.g. `M2SL`) are monthly, while others (e.g. `DGS10`) are daily. The macro composite score normalises across these, but the monthly data is effectively stale for most of the month.

---

## 4. Performance Improvements

### TD-030 — Single Large JSON Payload

| Field | Value |
|---|---|
| **Category** | Performance |
| **Severity** | Low |
| **Status** | Open |

`live.json` is a single monolithic file. As more data is added (history, news, snapshots), the file will grow. The browser must download and parse the entire file on every refresh.

**Resolution Path**  
Split into a small core payload (`live-core.json`) loaded immediately, and supplementary payloads (`live-news.json`, `live-history.json`, `live-analyst.json`) loaded lazily.

---

### TD-031 — Service Worker Cache Invalidation

| Field | Value |
|---|---|
| **Category** | Performance |
| **Severity** | Low |
| **Status** | Open |

The service worker's `CACHE_VERSION` must be manually incremented with each release to force cache refresh. If it is forgotten, users may see stale HTML/JS/CSS after a deployment.

**Resolution Path**  
Automate the `CACHE_VERSION` bump as part of `build_release.py` — derive it from the app version string or a build timestamp.

---

## 5. Architecture Improvements

### TD-040 — No Router / Single Page Architecture

Covered in `TD-002`. An architecture improvement that would involve adding a hash or history router without introducing a framework.

---

### TD-041 — Tighter Python/JS Contract

Currently there is no formal schema for `live.json`. If a Python change drops a field that JS assumes is present, the browser silently shows `'Unavailable'`. The contract between the pipeline and the frontend is informal.

**Resolution Path**  
Introduce a JSON Schema for `live.json`. Validate it in `verify_release.py`. This creates a machine-verifiable contract between the Python output and JS input.

---

### TD-042 — No Integration Tests for Browser UI

`test_mobile_navigation_playwright.py` covers basic navigation. There are no integration tests for:
- Dashboard card rendering with mocked `live.json`
- Detail view content
- Alert rendering
- Analyst output

**Resolution Path**  
Expand Playwright test suite to cover the main user journeys.
