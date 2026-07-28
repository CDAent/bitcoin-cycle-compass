# Page Register
## Bitcoin Cycle Compass — Version 8.7 · Sprint 0

All "pages" in Bitcoin Cycle Compass are views rendered within a single `index.html` document. The default view is the Dashboard (card grid). All other views are rendered inside the `#detailPanel` overlay by the `openDetail(view)` function.

There is no URL router — view state is held in the `ACTIVE_VIEW` JavaScript variable.

---

## 1. Dashboard

| Field | Value |
|---|---|
| **Purpose** | Primary overview page. Shows 13 cards covering live BTC price, market snapshot, research confidence, market regime, bottom/peak probability models, Fear & Greed gauge, stablecoin supply, ETF flow, capital allocation, regime scores, smart money summary, events, and news. |
| **Route** | Default view (no `openDetail` call — `closeDetail()` is called when navigating here) |
| **Main Component** | `render()` function in `index.html` |
| **Child Components** | BTC Live Price Card, Today's Snapshot Card, Compass AI Research Card, Market Regime Card, Bottom Probability Card, Next Peak Probability Card, Fear & Greed Card, Stablecoin Supply Card, ETF Flow & Demand Card, Global Capital Allocation Card, Market Regime Scores Card, Smart Money Summary Card, Major Market Events Card, Market News Card |
| **Services Used** | `refreshLiveData()`, `enrichMissingFeeds()`, `browserFallback()` |
| **Data Sources** | `data/live.json` (`DATA.btc`, `DATA.fx`, `DATA.fearGreed`, `DATA.stablecoins`, `DATA.etf`, `DATA.macro`, `DATA.onchain`, `DATA.liquidityScores`, `DATA.liquidityTrends`, `DATA.news`, `DATA.events`) |
| **LocalStorage Read** | `btcCurrency`, `btcPrevRegimeScore` |
| **LocalStorage Write** | `btcCompassWeeklyHistory`, `btcPrevRegimeScore` |
| **Future Enhancements** | Personalised card ordering; user-selectable metric widgets; collapsible cards; notification badge on nav when alerts trigger |

---

## 2. Markets & Forecasts

| Field | Value |
|---|---|
| **Purpose** | Detailed view of live Bitcoin price data across multiple exchanges, next-bottom scenario model with three probability bands, and next-peak scenario model with three bands. |
| **Route** | `openDetail('markets')` — triggered by "Markets & Forecasts" nav item or clicking the BTC Price, Fear & Greed, or Summary cards |
| **Main Component** | `views.markets()` inside `openDetail()` |
| **Child Components** | `tableRows()` helper; source metadata badges |
| **Services Used** | None — all data from existing `DATA` global |
| **Data Sources** | `DATA.btc` (price, sources, change24h), `DATA.fx`, Dashboard DOM elements for forecast values (reads from already-rendered card elements) |
| **Notable Behaviour** | Bottom and peak values are read back from the DOM (from `render()` output), not recalculated here |
| **Future Enhancements** | Live chart of Bitcoin vs the forecast model ranges; configurable reference cycle high; historical model accuracy tracking |

---

## 3. Global Liquidity

| Field | Value |
|---|---|
| **Purpose** | Full breakdown of estimated capital allocation across 9 asset classes + Other; stablecoin liquidity (4 timeframes); confirmed ETF net flows (daily, 5-session, 20-session); ETF demand proxy details; individual ETF fund participation. |
| **Route** | `openDetail('liquidity')` — triggered by nav item or clicking Stablecoin, ETF, or Capital Allocation cards |
| **Main Component** | `views.liquidity()` inside `openDetail()` |
| **Child Components** | `liquidityShares()`, `trendInfo()`, `selectedCompactUsd()`, `tableRows()` |
| **Services Used** | None — all data from existing `DATA` global |
| **Data Sources** | `DATA.liquidityScores`, `DATA.liquidityTrends`, `DATA.stablecoins`, `DATA.etf` (flows + proxy + fund list) |
| **Future Enhancements** | Historical liquidity trend chart; stablecoin breakdown by issuer; ETF fund comparison chart; real audited AUM data integration |

---

## 4. On-Chain Metrics

| Field | Value |
|---|---|
| **Purpose** | Network composite health score and individual metric cards for hash rate, transaction count, and mempool size — each with latest value and 30-day change. |
| **Route** | `openDetail('onchain')` — triggered by "On-Chain Metrics" nav item |
| **Main Component** | `views.onchain()` inside `openDetail()` |
| **Child Components** | `tableRows()`, `cls()` |
| **Services Used** | None — all data from existing `DATA` global |
| **Data Sources** | `DATA.onchain` (score, metrics: hash-rate, n-transactions, mempool-size) |
| **Future Enhancements** | More on-chain metrics (MVRV, SOPR, NVT); chart of on-chain score over time; exchange flow tracking; long-term holder data |

---

## 5. Macro Economy

| Field | Value |
|---|---|
| **Purpose** | Macro tailwind composite score and five individual FRED series cards: Federal Reserve assets (WALCL), US M2 money supply (M2SL), US 10-year yield (DGS10), Broad US dollar index (DTWEXBGS), and VIX volatility (VIXCLS). Each shows latest value, observation date, and approximate 20-period change. |
| **Route** | `openDetail('macro')` — triggered by "Macro Economy" nav item or clicking Market Regime Scores card |
| **Main Component** | `views.macro()` inside `openDetail()` |
| **Child Components** | `tableRows()`, `cls()` |
| **Services Used** | None — all data from existing `DATA` global |
| **Data Sources** | `DATA.macro` (score plus WALCL, M2SL, DGS10, DTWEXBGS, VIXCLS objects) |
| **Future Enhancements** | International central bank series (ECB, RBA, BoJ); yield curve; PCE / CPI integration; credit spreads; earnings composite |

---

## 6. Market News & Events

| Field | Value |
|---|---|
| **Purpose** | Full article list with headlines, summaries, star ratings (global significance), impact classification (Bullish/Bearish/Neutral), affected market tags, and source/time metadata. Impact summary banner for high-significance stories. Official economic event calendar links. Pinned articles section with persistent local storage. |
| **Route** | `openDetail('news')` — triggered by "News & Events" nav item or clicking Events or News cards |
| **Main Component** | `views.news()` inside `openDetail()` |
| **Child Components** | `sortedNews()`, `marketArticleHtml()`, `pinnedArticlesHtml()`, `bindPinButtons()`, `marketImpactSummary()`, `starText()`, `starLabel()`, `escapeHtml()`, `safeUrl()`, `relativeTime()` |
| **Services Used** | `fetchBrowserNews()` (if `DATA.news` is empty at load) |
| **Data Sources** | `DATA.news` (articles from Google News RSS, scored by `article_significance()`), `DATA.events` (official calendar links), `localStorage.btcCompassPinnedArticles` |
| **Future Enhancements** | Live news filtering by tag/impact; notification for high-impact stories; direct RSS feed configuration; news sentiment trend over time |

---

## 7. History & Trends

| Field | Value |
|---|---|
| **Purpose** | Interactive Bitcoin price history with 8 timeframe views (Today, 1 Week, 1 Month, 3 Months, 6 Months, 1 Year, 2 Years, 4 Years). Line chart for longer timeframes; candlestick chart for short-term daily view. Scrollable historic records table with percentage change arrows. |
| **Route** | `openDetail('history')` — triggered by "History & Trends" nav item |
| **Main Component** | `views.history()` inside `openDetail()` |
| **Child Components** | `renderHistoryRange()`, `renderCandlestickChart()`, `historySeriesFor()`, `formatAppDate()`, `tableRows()` |
| **Services Used** | None at render time — data loaded during `refreshLiveData()` |
| **Data Sources** | `DATA.historyWeekly` (from `live.json`, 208 weeks), `DATA.historyDaily` (from `live.json`, 4 years daily), `localStorage.btcCompassWeeklyHistory` (locally saved snapshots merged with remote) |
| **LocalStorage Read/Write** | `btcCompassWeeklyHistory` (merged and stored by `saveSnapshot()`) |
| **Future Enhancements** | Overlaying research score or regime on the price chart; volume chart; on-chain overlay; export to CSV; comparison of two timeframe periods |

---

## 8. Compass Ai Analyst

| Field | Value |
|---|---|
| **Purpose** | Evidence-based AI analyst answering free-text questions about the Bitcoin cycle, capital allocation, macro, and institutional demand. Uses a deterministic internal model (no external LLM unless the user configures an optional private endpoint). Answers are structured into: Verified Facts, Market Interpretation, Supporting Evidence, Risks & Counterarguments, What Would Change This View, and Confidence & Evidence Quality. |
| **Route** | `openDetail('analyst')` — triggered by "Compass Ai Analyst" nav item |
| **Main Component** | `views.analyst()` inside `openDetail()` |
| **Child Components** | `buildCompassAnalysis()`, `renderAnalystAnswer()`, `appendAnalystMessage()`, `runExternalResearch()`, `buildEvidenceRegister()`, `evidenceQuality()`, `profileLanguage()`, `liquidityShares()`, `trendInfo()` |
| **Services Used** | `runExternalResearch()` — optional POST to user-configured private endpoint |
| **Data Sources** | `DATA` global (btc, fearGreed, stablecoins, etf, liquidityScores, liquidityTrends, macro, researchScore, opportunityScore, regime), `window.__weeklyHistory` (merged local + remote weekly), `localStorage` (profile, externalResearch flag, evidenceOnly flag, compassResearchEndpoint) |
| **External Config** | `localStorage.compassResearchEndpoint` — optional private research API URL (must be user-configured in Settings) |
| **Future Enhancements** | First-class LLM integration with evidence grounding; conversation history persistence; comparison mode (two dates); custom question templates; deeper historical context |

---

## 9. Alerts

| Field | Value |
|---|---|
| **Purpose** | Configurable threshold alerts for 9 metrics: Bitcoin price, 24h change %, Fear & Greed, opportunity score, research score, ETF flow, stablecoin 7d flow, macro score, on-chain score. Each alert shows live current value, triggered/OK status, and controls to enable/set threshold/direction. Local storage only — no push notifications in this release. |
| **Route** | `openDetail('alerts')` — triggered by "Alerts" nav item |
| **Main Component** | `views.alerts()` → `renderAlertsPanel()` |
| **Child Components** | `ALERT_DEFINITIONS`, `loadAlertConfig()`, `saveAlertConfig()`, `getLiveAlertValue()`, `formatLiveAlertValue()`, `checkAlertTriggered()`, `validateAlertInput()` |
| **Services Used** | None |
| **Data Sources** | `DATA` global (live values via `getLiveAlertValue()`), `localStorage.btcAlertConfig` |
| **Future Enhancements** | Browser push notification delivery; email/webhook integration; alert history log; multi-condition compound alerts |

---

## 10. Settings

| Field | Value |
|---|---|
| **Purpose** | User configuration panel with 7 setting cards: refresh trigger, display currency, external research endpoint URL, diagnostics/cache clear, support destination email, navigation to Feedback & Support, and local data reset. |
| **Route** | `openDetail('settings')` — triggered by "Settings" nav item |
| **Main Component** | `views.settings()` inside `openDetail()` |
| **Child Components** | `refreshLiveData()`, `clearCacheAndReload()`, `isValidResearchEndpoint()`, currency buttons |
| **Services Used** | `refreshLiveData()`, `clearCacheAndReload()` (unregisters service worker, clears caches, reloads) |
| **Data Sources** | `localStorage` keys: `compassResearchEndpoint`, `compassSupportEmail`, `btcCurrency` |
| **Future Enhancements** | Theme customisation (accent colour); data export; notification preferences; timezone selection; user account for cross-device sync |

---

## 11. About & Glossary

| Field | Value |
|---|---|
| **Purpose** | Static reference page covering: how to read the dashboard (workflow steps), colour guide, segment glossary with icons (Dashboard, Market Analysis, Capital & Liquidity, Data & Infrastructure sections), probability confidence guide, source and update cadence table, sources overview, methodology notes, important disclaimer, and build metadata. |
| **Route** | `openDetail('about')` — triggered by "About & Glossary" nav item |
| **Main Component** | `views.about()` inside `openDetail()` |
| **Child Components** | `tableRows()`, glossary cards with `tone-pos/neu/neg/gold` icon classes |
| **Services Used** | None |
| **Data Sources** | `DATA.buildMeta`, `APP_VERSION` constant |
| **Future Enhancements** | Searchable glossary; video walkthrough integration; release notes section; FAQ accordion |

---

## 12. Feedback & Support

| Field | Value |
|---|---|
| **Purpose** | Structured feedback form with three report types: Bug Report (title, description, steps, expected/actual behaviour, priority), Feature Request (title, improvement, benefit), and General Feedback (subject, comments). Optional diagnostics block. Opens a pre-filled `mailto:` draft. Draft auto-saved to `localStorage`. |
| **Route** | `openDetail('support')` — triggered by "Feedback & Support" nav link in Settings, or via `openSupportNav` button click event |
| **Main Component** | `views.support()` inside `openDetail()` |
| **Child Components** | `tableRows()`, form fields rendered dynamically by `typeSel.onchange` |
| **Services Used** | None (opens `mailto:` in user's email client) |
| **Data Sources** | `localStorage.compassSupportEmail`, `localStorage.compassSupportDraft`, `DATA.buildMeta`, `APP_VERSION`, `navigator.userAgent`, `navigator.platform` |
| **Future Enhancements** | Direct in-app form submission (requires backend); GitHub Issues integration; support ticket tracking |

---

## 13. Reports (Internal)

| Field | Value |
|---|---|
| **Purpose** | Internal executive report view showing snapshot generation time, version, and 3 report sections (Cycle Posture, Liquidity Focus, Trend Watch) derived from the latest data. |
| **Route** | `openDetail('reports')` — not in the primary navigation; accessible via direct `data-view="reports"` links or programmatic calls |
| **Main Component** | `views.reports()` inside `openDetail()` |
| **Child Components** | `tableRows()` |
| **Services Used** | None |
| **Data Sources** | `DATA.reports` (sections array), `DATA.buildMeta`, `DATA.generatedAt`, `DATA.appVersion` |
| **Future Enhancements** | Promote to primary navigation; PDF export; scheduled email delivery; historical report archive |
