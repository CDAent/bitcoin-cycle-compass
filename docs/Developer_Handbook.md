# Developer Handbook
## Bitcoin Cycle Compass — Version 8.7 · Sprint 0

---

## 1. Project Vision

Bitcoin Cycle Compass is a personal financial intelligence tool that helps the owner track the Bitcoin market cycle using a multi-signal dashboard. The goal is to present a clear, evidence-based view of where Bitcoin sits in its market cycle by combining:

- Live price across multiple exchanges
- Macro liquidity conditions (Fed assets, M2, rates, DXY, VIX)
- On-chain network health (hash rate, transactions, mempool)
- Institutional demand (ETF net flows and ETF demand proxy)
- Stablecoin liquidity (supply changes as a risk-appetite proxy)
- Market sentiment (Fear & Greed Index)
- Capital allocation model (where liquidity is flowing across 9 asset classes)
- News significance (scored by likely global financial impact)
- Compass AI Analyst (deterministic evidence-based analysis)

The product is designed for a single user on GitHub Pages. It is a static site with no backend, no database at runtime, and no external accounts required to use it.

---

## 2. Architecture Overview

### What this application is

- A **Progressive Web App (PWA)** served as a static site from GitHub Pages
- A **single HTML file** (`index.html`) containing all CSS and JavaScript
- Powered by a **Python data pipeline** that runs in GitHub Actions
- Data is delivered as a **static JSON file** (`data/live.json`)

### What this application is not

- It is not a Node.js application
- It is not a React/Vue/Angular application
- It has no server-side runtime at request time
- It has no user accounts, authentication, or database accessible at runtime

### Core components

| Component | Technology | Location |
|---|---|---|
| Frontend | Vanilla HTML + CSS + JS | `index.html` |
| Data pipeline | Python 3.11 | `scripts/` |
| Data store (build-time) | SQLite | `data/history.db` (not committed) |
| Data payload (runtime) | JSON | `data/live.json` |
| PWA shell | Service Worker | `service-worker.js` |
| PWA manifest | JSON | `manifest.json` |
| CI/CD | GitHub Actions | `.github/workflows/` |

For a full architectural diagram, see [`Architecture_Map.md`](Architecture_Map.md).

---

## 3. Folder Conventions

```
bitcoin-cycle-compass/
├── index.html            # All frontend (HTML + CSS + JS)
├── service-worker.js     # PWA cache strategy
├── manifest.json         # PWA metadata
├── *.png                 # Compass images
├── data/
│   ├── live.json         # Generated output (committed on each run)
│   └── history.db        # SQLite (NOT committed — runtime artefact)
├── scripts/              # Python data pipeline
│   ├── update_data.py    # Main updater (run this to refresh data)
│   ├── db_schema.py      # Schema and migrations
│   ├── history_service.py
│   ├── snapshot_service.py
│   ├── import_history.py
│   ├── backfill_history.py
│   ├── build_release.py
│   ├── verify_release.py
│   ├── release.py
│   └── create_release_tag.py
├── tests/                # Pytest test suite
├── docs/                 # Architecture documentation (this folder)
└── .github/workflows/    # CI/CD pipelines
```

### Rules

- `history.db` and `dist/` are gitignored — never commit them
- `data/live.json` is committed — it is the static data payload
- Do not create files outside the documented structure without updating this handbook
- Do not add a `node_modules/` or `package.json` — the project is pure Python + vanilla JS
- Python scripts belong in `scripts/`; tests belong in `tests/`

---

## 4. Coding Standards

### Python

- **Version**: Python 3.11 (as specified in `pages-release.yml`)
- **Style**: Follow PEP 8. Function and variable names use `snake_case`.
- **Imports**: Standard library only where possible. No third-party packages are installed in CI.
- **Error handling**: Use `safe(fn, default)` for all external API calls. Never let a single source failure abort the updater.
- **Type annotations**: Not currently enforced, but encouraged for new functions.
- **Docstrings**: Module-level docstrings are required for service files. Function docstrings for public functions.
- **Constants**: Module-level constants in `UPPER_SNAKE_CASE` (e.g. `_APP_VERSION`, `ROOT`, `OUT`).

### JavaScript

- **Standard**: ES2020+ (native browser support, no transpilation)
- **Style**: Minified in the script block. New logic added to the script block should be written clearly first, then minified before commit if adding to the inline block.
- **Error handling**: Wrap all DOM access in null checks (`if(el)...`). Wrap all `localStorage` access in try/catch.
- **Security**: Always run user-sourced strings through `escapeHtml()` before inserting into the DOM. Always run URLs through `safeUrl()` before using in `href` attributes.
- **No external libraries**: Do not add CDN links or npm packages. All JS is inline.

### HTML

- One `<style>` block; one `<script>` block. Keep this structure.
- All semantic elements: `<aside>`, `<main>`, `<header>`, `<section>`, `<nav>`, `<button>`.
- All interactive elements accessible: `aria-label`, `aria-expanded`, `aria-live`, `aria-pressed`.
- Minimum touch target: `44px` height/width on mobile.

---

## 5. Naming Standards

### Python

| Pattern | Convention |
|---|---|
| Functions | `snake_case` |
| Constants | `UPPER_SNAKE_CASE` or `_UPPER_SNAKE_CASE` (private) |
| Classes | `PascalCase` |
| Arguments | `snake_case` |
| Database columns | `snake_case` |
| SQLite tables | `snake_case` |

### JavaScript

| Pattern | Convention |
|---|---|
| Functions | `camelCase` |
| Constants | `UPPER_SNAKE_CASE` (e.g. `APP_VERSION`, `ALERT_DEFINITIONS`) |
| State variables | `camelCase` (e.g. `DATA`, `CUR`, `ACTIVE_VIEW`) |
| CSS IDs | `camelCase` (e.g. `btcPrice`, `fearNeedle`, `detailPanel`) |
| CSS classes | `kebab-case` (e.g. `.market-article`, `.score-pill`) |
| CSS tokens | `--kebab-case` (e.g. `--green`, `--card-radius`) |

### Files

| Pattern | Convention |
|---|---|
| Python scripts | `snake_case.py` |
| Docs | `PascalCase.md` |
| HTML/JS/CSS | `kebab-case.html/.js` |
| Images | `kebab-case.png` |

---

## 6. Component Rules

### Adding a new Dashboard Card

1. Add the HTML section to the dashboard grid in `index.html` with the correct `c-` grid class and a `data-open` attribute if it should link to a detail view.
2. Assign element IDs to all dynamic parts.
3. Update `render()` to populate those elements from the `DATA` global.
4. Add the corresponding CSS class with `grid-column: span N` and adjust the responsive breakpoints.
5. Document the new card in `Component_Register.md`.

### Adding a new Detail View

1. Add a `data-view="<name>"` button to both the desktop nav and the mobile drawer nav.
2. Add the view name to the `MOBILE_TITLES` constant.
3. Add a `views.<name>: () => {...}` function inside `openDetail()`.
4. Document the view in `Page_Register.md`.

### Modifying a Python Service

1. All external API calls must use `safe(fn, default)` wrappers.
2. Any new table or column must be added as a migration script in `db_schema.py` (increment `CURRENT_VERSION`).
3. Never delete existing tables or columns in migrations — only add.
4. Update `update_data.py` to write the new field to `live.json`.
5. Update `Service_Register.md`.

### Modifying live.json

Any field added to `live.json` must:
- Have a corresponding null/default fallback in the JS render path (never assume a field exists)
- Be documented in `Data_Flow.md` section 4

---

## 7. Testing Strategy

Tests are located in `tests/` and run via `pytest`.

| Test File | What It Covers |
|---|---|
| `test_history_db.py` | SQLite schema creation, V1/V2 migrations, `btc_daily` and `market_snapshots` inserts and queries |
| `test_snapshot_service.py` | `snapshot_service.py` public API: latest, by date, nearest, range, compare, upsert, build metadata |
| `test_etf_flow_integrity.py` | ETF flow field validation, staleness detection, proxy score logic |
| `test_release_regressions.py` | `live.json` structure, version string consistency across `index.html`, `service-worker.js`, `manifest.json`, `live.json` |
| `test_runtime_artifact_separation.py` | Ensures `history.db`, `dist/`, and other runtime artefacts are not tracked in git |
| `test_mobile_navigation_playwright.py` | Browser-based UI tests: mobile navigation, section switching, refresh behaviour |

### Running tests locally

```bash
python3 -m pytest tests/ -q
```

### Test rules

- Write a test for every new Python service function.
- Tests must pass in a clean environment with no external network access (mock or skip network calls).
- Do not commit a change that breaks existing tests without updating those tests.
- The CI pipeline gates every deployment on `pytest tests/` passing.

---

## 8. Deployment Workflow

### Standard Deployment (push to `main`)

```
Developer pushes to main
        │
        ▼
GitHub Actions: pages-release.yml
  [1] Checkout
  [2] Setup Python 3.11
  [3] Clean __pycache__ / dist/
  [4] Verify clean tree
  [5] Run tests (pytest tests/ -q)
  [6] Compile scripts (py_compile scripts/*.py)
  [7] Build staged release (build_release.py)
        → Copy static files → dist/release/
        → Run update_data.py (fetch all APIs, write live.json + history.db)
  [8] Verify staged release (verify_release.py)
        → Check version strings
        → Check required assets exist
        → Check required UI elements present
  [9] Verify clean tree (post-build)
  [10] Upload dist/release as Pages artifact
  [11] Deploy to GitHub Pages
```

**Important**: The updater runs during deployment. This means each deployment also refreshes `data/live.json` with the latest market data.

### Manual Data Refresh

Data can also be refreshed without a code push via `workflow_dispatch` on `pages-release.yml`.

### Local Development

```bash
# Fetch all data locally (writes data/live.json and data/history.db)
python3 scripts/update_data.py

# Serve the app locally (any static file server)
python3 -m http.server 8000
# Then open http://localhost:8000

# Run tests
python3 -m pytest tests/ -q
```

---

## 9. Branch Strategy

| Branch | Purpose |
|---|---|
| `main` | Production branch. Every push triggers a full build, verify, and deployment to GitHub Pages. Must always be deployable. |
| Feature branches | All work-in-progress. Named `feature/<description>`, `fix/<description>`, or `sprint-<N>-<description>`. |
| Worktrees | Used for sprint work. Named `<repo>.worktrees/<sprint-name>`. |

### Rules

- Never push broken Python or JavaScript directly to `main`.
- All new work should be in a branch or worktree.
- Merge to `main` only when CI passes locally.
- The `release-tag-guard.yml` workflow prevents unauthorized release tags.

---

## 10. Release Process

A release is defined by a consistent version string across four files:

| File | Field |
|---|---|
| `index.html` | `APP_VERSION` constant and `<title>` |
| `service-worker.js` | `CACHE_VERSION` constant |
| `manifest.json` | `name` and `short_name` |
| `scripts/update_data.py` | `_APP_VERSION` constant and `_SPRINT` constant |

### Steps to cut a release

1. Update the version string in all four files (format: `X.Y.Z`). Update `_SPRINT` in `update_data.py` if the sprint number has changed.
2. Confirm all tests pass: `python3 -m pytest tests/ -q`
3. Run `python3 scripts/build_release.py --stage-dir dist/release` locally to validate the staged build.
4. Run `python3 scripts/verify_release.py --release-dir dist/release` to confirm version consistency and required assets.
5. Commit the version bump.
6. Push to `main`.
7. Monitor GitHub Actions to confirm deployment.
8. To create an annotated git tag: `python3 scripts/release.py --tag vX.Y.Z`
   - This enforces: branch is `main`, HEAD is at `origin/main`, tag matches version in `manifest.json`, tag is unique, full build/verify/test cycle passes.

See [`Release_Checklist.md`](Release_Checklist.md) for the step-by-step checklist.

### `sync_manifest_versions()`

The `update_data.py` script automatically keeps `manifest.json` in sync with `_APP_VERSION` during the build. Manual sync is not required if this function is called.

---

## 11. Documentation Standards

### When to update docs

| Change | Documents to update |
|---|---|
| New dashboard card | `Component_Register.md`, `Architecture_Map.md` (if structural) |
| New detail view / page | `Page_Register.md`, `Component_Register.md` |
| New Python service or function | `Service_Register.md` |
| New external API | `API_Register.md` |
| New CSS token or colour | `Theme_Guide.md` |
| New data field in `live.json` | `Data_Flow.md` |
| Architecture change | `Architecture_Map.md` |
| Technical debt identified | `Technical_Debt.md` |
| Release | `Change_Log.md` |

### Documentation location

All docs live in `/docs/`. File names use `PascalCase.md`.

| File | Contents |
|---|---|
| `Architecture_Map.md` | High-level architecture, folder structure, connection tree |
| `Component_Register.md` | Every component with purpose, location, imports, CSS |
| `Data_Flow.md` | End-to-end data flow diagrams |
| `Theme_Guide.md` | Design tokens, colours, typography |
| `Page_Register.md` | Every page/view with services and data sources |
| `Service_Register.md` | Every service with functions and returns |
| `API_Register.md` | Every external API and internal endpoint |
| `Developer_Handbook.md` | This file — standards and workflow |
| `Technical_Debt.md` | Known issues and deferred work |
| `Change_Log.md` | Release history |

### Style

- Use tables for structured information (component properties, API fields)
- Use code blocks for file paths, function signatures, and example JSON
- Use ASCII diagrams for data flows and architecture (consistent with other docs)
- Keep prose concise — these are reference documents, not tutorials
