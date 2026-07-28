# Release Checklist
## Bitcoin Cycle Compass — Version 8.7 · Sprint 0

Step-by-step checklist for preparing, building, validating, deploying, and tagging a release. Complete all steps in order. A release is not done until a git tag has been pushed and GitHub Actions has confirmed deployment.

---

## Phase 1 — Version Bump

Update the version string in all four files. All four must match exactly (format: `X.Y.Z`).

- [ ] `index.html` — update `APP_VERSION` constant (line ~406) and `<title>` tag (line ~8)
- [ ] `service-worker.js` — update `CACHE_VERSION` constant (line 1)
- [ ] `manifest.json` — update `name` field (`"Bitcoin Cycle Compass Version X.Y.Z"`) and `short_name` field
- [ ] `scripts/update_data.py` — update `_APP_VERSION` constant (line ~333)
- [ ] `scripts/update_data.py` — update `_SPRINT` constant (line ~334) if the sprint number has changed

**Verify all four match:**
```bash
grep "APP_VERSION\|CACHE_VERSION\|_APP_VERSION" index.html service-worker.js scripts/update_data.py
grep '"name"' manifest.json
```

---

## Phase 2 — Change Log

- [ ] Open `docs/Change_Log.md`
- [ ] Add a new version section (e.g. `## [X.Y.Z] — YYYY-MM`) under `[Unreleased]`
- [ ] Move all `[Unreleased]` entries into the new version section
- [ ] Add the release date
- [ ] Leave `[Unreleased]` empty and ready for the next cycle

---

## Phase 3 — Local Build and Test

Run all checks locally before pushing. Fix any failures before proceeding.

```bash
# 1. Run the full test suite
python3 -m pytest tests/ -q

# 2. Compile all scripts (catches syntax errors)
python3 -m py_compile scripts/*.py

# 3. Build staged release
python3 scripts/build_release.py --stage-dir dist/release

# 4. Verify staged release (version strings, required files, UI markers)
python3 scripts/verify_release.py --release-dir dist/release
```

- [ ] All pytest tests pass
- [ ] `py_compile` passes with no errors
- [ ] `build_release.py` completes successfully
- [ ] `verify_release.py` reports all checks passed
- [ ] `dist/release/data/live.json` is present and parseable
- [ ] `dist/release/index.html` contains the correct version string

---

## Phase 4 — Commit and Push

- [ ] Stage and commit the version bump changes:
  ```bash
  git add index.html service-worker.js manifest.json scripts/update_data.py docs/Change_Log.md
  git commit -m "chore: bump version to vX.Y.Z"
  ```
- [ ] Push to `main`:
  ```bash
  git push origin main
  ```
- [ ] Monitor GitHub Actions (`pages-release.yml`) — confirm all steps pass:
  - Clean tree check ✓
  - Tests ✓
  - Compile scripts ✓
  - Build staged release ✓
  - Verify staged release ✓
  - Upload Pages artifact ✓
  - Deploy to GitHub Pages ✓

---

## Phase 5 — Release Tag

Use `scripts/release.py` to create a guarded annotated git tag. This script enforces:
- Branch must be `main`
- HEAD must match `origin/main`
- Tag name must match the version in `manifest.json`
- Tag must not already exist
- Runs full build, verify, pytest, and py_compile checks

```bash
python3 scripts/release.py --tag vX.Y.Z --message "Bitcoin Cycle Compass vX.Y.Z"
```

- [ ] `release.py` completes with `PASS: created and pushed tag vX.Y.Z`
- [ ] Confirm tag is visible on GitHub: `git tag -l | tail -5`
- [ ] `release-tag-guard.yml` workflow passes on GitHub Actions (validates tag points to `origin/main` HEAD)

---

## Phase 6 — Post-Release Verification

- [ ] Visit the live GitHub Pages URL and confirm the version shown in the footer matches the release version
- [ ] Confirm `live.json` was refreshed (check "Last updated" timestamp in the sidebar)
- [ ] Confirm the app loads, dashboard renders, and at least one data card shows a value
- [ ] Confirm service worker is at the new cache version (check DevTools → Application → Service Workers)
- [ ] Clean up the local staged build:
  ```bash
  rm -rf dist/
  ```

---

## Phase 7 — Documentation Update (if needed)

If this release includes structural changes:

- [ ] Update `docs/Architecture_Map.md` if the folder structure changed
- [ ] Update `docs/Component_Register.md` if new components were added
- [ ] Update `docs/Page_Register.md` if new views were added
- [ ] Update `docs/Service_Register.md` if new services were added
- [ ] Update `docs/API_Register.md` if new external APIs were added
- [ ] Update `docs/Theme_Guide.md` if new design tokens were added
- [ ] Update `docs/Feature_Locator.md` if significant new functions were added
- [ ] Update `docs/Technical_Debt.md` — mark resolved items; add any new debt identified

---

## Quick Reference

| Check | Command |
|---|---|
| Run all tests | `python3 -m pytest tests/ -q` |
| Compile scripts | `python3 -m py_compile scripts/*.py` |
| Build staged release | `python3 scripts/build_release.py --stage-dir dist/release` |
| Verify staged release | `python3 scripts/verify_release.py --release-dir dist/release` |
| Create and push tag | `python3 scripts/release.py --tag vX.Y.Z` |
| Check version strings | `grep "APP_VERSION\|CACHE_VERSION\|_APP_VERSION" index.html service-worker.js scripts/update_data.py` |
| Check local tags | `git tag -l \| tail -10` |
| Clean staged build | `rm -rf dist/` |

---

## Notes

- `sync_manifest_versions()` in `update_data.py` automatically keeps `manifest.json` in sync during a build. However, manually updating it during a version bump ensures it is correct before the build runs.
- Never push directly to `main` without running Phase 3 first. The CI pipeline will gate deployment, but local validation catches issues faster.
- Do not create a tag manually with `git tag` — always use `release.py` to enforce the guardrails.
- `history.db` and `dist/` are gitignored and must never be committed.
