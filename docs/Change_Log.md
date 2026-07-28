# Change Log
## Bitcoin Cycle Compass

All notable changes to this project are documented here.

This file follows the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.  
Version numbers follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

> Changes in development that have not yet been released.

---

## [8.7.0] — 2025-07 (Sprint 0 — Architecture & Documentation)

### Added
- `/docs/Architecture_Map.md` — High-level application architecture, folder structure, and connection tree
- `/docs/Component_Register.md` — Registry of every major UI and service component
- `/docs/Data_Flow.md` — End-to-end data flow documentation including server pipeline, client pipeline, and score computation
- `/docs/Theme_Guide.md` — Complete design token reference: colours, typography, spacing, icons, and market regime colour mapping
- `/docs/Page_Register.md` — Register of every page and view with routes, components, services, and data sources
- `/docs/Service_Register.md` — Register of every service with functions, dependencies, and return values
- `/docs/API_Register.md` — Complete documentation of all 14 external APIs and the internal `live.json` endpoint
- `/docs/Developer_Handbook.md` — Project vision, architecture overview, coding standards, naming conventions, deployment workflow, and release process
- `/docs/Technical_Debt.md` — Known issues, deferred work, and architecture improvement register
- `/docs/Change_Log.md` — This file

### Changed
- No application code changes in this sprint (documentation only)

---

## [8.6.1] — Prior Release

### Summary
- Service worker cache version aligned with app version
- Minor stability improvements to build pipeline
- `verify_release.py` improvements for version string consistency checks

---

## [8.6.0] — Prior Release

### Added
- V2 database schema: `market_snapshots` table for unified per-day market data snapshots
- `snapshot_service.py` — CRUD service for market_snapshots with query, upsert, range, nearest, and compare functions
- `build_metadata` table for key/value build context storage
- `import_history.py` — bulk history import utility
- `backfill_history.py` — backfill utility for historical data gaps

### Changed
- Database schema version incremented from V1 to V2
- `update_data.py` now calls `upsert_snapshot()` to write a unified daily snapshot on each run

---

## [8.5.0] — Prior Release

### Added
- Compass Ai Analyst — deterministic evidence-based market analysis
- External research endpoint support (optional user-configured private API)
- `compassResearchEndpoint`, `compassExternalResearch`, `compassEvidenceOnly`, `compassAnalystProfile` localStorage keys

### Changed
- Reports view expanded with analyst integration

---

## [8.4.0] — Prior Release

### Added
- Capital Allocation dashboard card — 9-asset model (BTC, Gold, Cash, Equities, AI, EM, RE, Bonds, AltCoin)
- Traditional market proxies via Stooq (GLD, SPY, QQQ, EEM, VNQ, AGG, SHV)
- `btcPrevRegimeScore` localStorage key for regime change detection

---

## [8.3.0] — Prior Release

### Added
- ETF demand proxy score — computed from 6 ETF tickers (IBIT, FBTC, ARKB, BITB, GBTC, BTC) via Yahoo Finance
- ETF flow detail view with 30-day net flow chart

### Changed
- Macro composite score updated to incorporate ETF proxy

---

## [8.2.0] — Prior Release

### Added
- Alert system (`ALERT_DEFINITIONS`) — configurable thresholds for Fear & Greed, macro score, ETF flows, stablecoin supply
- `btcAlertConfig` localStorage key for user alert preferences
- Alert badge on Dashboard nav item

---

## [8.1.0] — Prior Release

### Added
- PWA manifest and service worker
- Offline support (cache-first for images, network-first for data)
- Install prompt support

---

## [8.0.0] — Prior Release

### Added
- V1 database schema: 9 tables — `btc_daily`, `fear_greed`, `etf_flows`, `stablecoin_market_cap`, `scores`, `market_regime`, `capital_allocation`, `market_data`, `schema_version`
- `db_schema.py` — schema definitions and migration framework
- `history_service.py` — `btc_daily` query functions for daily and weekly history
- GitHub Actions CI/CD pipeline (`pages-release.yml`)
- `build_release.py` — staged release builder
- `verify_release.py` — release validation script

---

## [7.x] — Earlier Versions

### Summary
- Initial Python data pipeline development
- Single-file frontend established
- Core signal set: price, Fear & Greed, macro, on-chain
- Basic dark theme and dashboard layout

---

_For the full project history, see the git log and GitHub release tags._

---

## Release Checklist

Use this checklist when preparing a new release:

- [ ] Update version string in `index.html` (`APP_VERSION`)
- [ ] Update version string in `service-worker.js` (`CACHE_VERSION`)
- [ ] Update version string in `manifest.json` (`name`, `short_name`)
- [ ] Update version string in `scripts/update_data.py` (`_APP_VERSION`)
- [ ] Add entry to this Change Log under `[Unreleased]` section
- [ ] Move `[Unreleased]` entries to the new version section with the release date
- [ ] Run `python3 scripts/build_release.py` locally
- [ ] Run `python3 scripts/verify_release.py --release-dir dist/release`
- [ ] Confirm all tests pass (`python3 -m pytest tests/ -q`)
- [ ] Push to `main` and confirm GitHub Actions deployment succeeds
- [ ] Optionally create a git tag with `python3 scripts/create_release_tag.py`
