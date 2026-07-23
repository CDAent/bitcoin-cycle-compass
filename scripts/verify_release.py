#!/usr/bin/env python3
import argparse
import json
import re
import sqlite3
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE_VERSION = '8.5.2'
DEFAULT_RELEASE_DIR = ROOT / 'dist' / 'release'


def parse_args():
    parser = argparse.ArgumentParser(description='Verify staged release output.')
    parser.add_argument('--release-dir', default=str(DEFAULT_RELEASE_DIR), help='Staged release directory')
    return parser.parse_args()


def read_text(path):
    return path.read_text(encoding='utf-8')


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def check(condition, label, failures):
    if condition:
        print(f'PASS: {label}')
    else:
        print(f'FAIL: {label}')
        failures.append(label)


def verify_db_bootstrap(failures):
    scripts_dir = ROOT / 'scripts'
    import sys

    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))

    from db_schema import init_db  # noqa: E402
    from snapshot_service import snapshot, upsert_snapshot  # noqa: E402

    with tempfile.TemporaryDirectory(prefix='bcc-db-bootstrap-') as tmp:
        db_path = Path(tmp) / 'data' / 'history.db'
        conn = init_db(db_path)
        conn.close()
        check(db_path.exists(), 'runtime history database is auto-created from scratch', failures)
        conn = sqlite3.connect(db_path)
        tables = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        }
        required = {'schema_version', 'btc_daily', 'market_snapshots', 'build_metadata'}
        check(required.issubset(tables), 'required schema tables are created', failures)
        conn.close()

        conn = init_db(db_path)
        upsert_snapshot(conn, '2026-01-01', {'btc_usd': 100000.0, 'btc_quality_status': 'live'})
        conn.commit()
        conn.close()
        round_trip = snapshot('2026-01-01', db_path)
        check(round_trip is not None and round_trip.get('btc_usd') == 100000.0, 'snapshot write/read succeeds on auto-created DB', failures)


def main():
    args = parse_args()
    release_dir = Path(args.release_dir).resolve()
    failures = []

    check(release_dir.exists(), f'release directory exists ({release_dir})', failures)
    if failures:
        print('\nSUMMARY:')
        print(f'FAIL ({len(failures)} checks failed)')
        return 1

    index_text = read_text(release_dir / 'index.html')
    sw_text = read_text(release_dir / 'service-worker.js')
    manifest = read_json(release_dir / 'manifest.json')
    live = read_json(release_dir / 'data' / 'live.json')

    check(f'v{RELEASE_VERSION}' in index_text, 'staged index.html visible version matches release', failures)
    check(manifest.get('name', '').endswith(RELEASE_VERSION), 'staged manifest version matches release', failures)
    check(live.get('appVersion') == RELEASE_VERSION, 'staged live.json appVersion matches release', failures)
    check(live.get('buildMeta', {}).get('appVersion') == RELEASE_VERSION, 'staged build metadata version matches release', failures)
    check(f"CACHE_VERSION = '{RELEASE_VERSION}'" in sw_text, 'staged service-worker cache version matches release', failures)

    check(isinstance(live, dict), 'staged live.json exists and parses', failures)
    check(bool(live.get('historyDaily')), 'staged historyDaily is populated', failures)
    check(bool(live.get('historyWeekly')), 'staged historyWeekly is populated', failures)
    check(bool(live.get('reports')) and bool(live.get('reports', {}).get('sections')), 'staged reports payload exists', failures)
    check((release_dir / 'data' / 'history.db').exists(), 'staged runtime history database exists', failures)

    for marker, label in [
        ('id="sideRefresh"', 'refresh buttons exist (sidebar)'),
        ('id="topRefresh"', 'refresh buttons exist (desktop header)'),
        ('id="settingsRefresh"', 'refresh button exists in Settings'),
        ('id="mobileHeaderRefresh"', 'refresh button exists in mobile header'),
        ('id="mobileHeaderLogo"', 'mobile logo exists'),
        ('id="mobileSharedHeader"', 'shared mobile header exists'),
        ('id="mobileMenuBtn"', 'hamburger open button exists'),
        ('id="mobileDrawerClose"', 'hamburger close button exists'),
        ('data-view="history"', 'History view exists'),
        ('reports:()=>', 'Reports view route exists'),
        ('data-view="news"', 'Market News view exists'),
        ('data-view="alerts"', 'Alerts view exists'),
        ('data-view="settings"', 'Settings view exists'),
        ('data-view="about"', 'About and Glossary view exists'),
        ('id="settingsSupportCard"', 'Feedback & Support widget exists in Settings'),
    ]:
        check(marker in index_text, label, failures)
    check('data-view="reports"' not in index_text, 'Reports is hidden from visible navigation', failures)

    ids = re.findall(r'id="([^"]+)"', index_text)
    duplicate_ids = [item for item, count in Counter(ids).items() if count > 1]
    check(not duplicate_ids, 'no duplicate IDs (including currency selectors)', failures)
    check('id="detailClose"' not in index_text, 'no per-page close X button remains', failures)

    obsolete_hits = []
    obsolete_pattern = re.compile(r'8\.5\.(?:0(?:-s1(?:\.3)?)?|1)')
    for path in [release_dir / 'index.html', release_dir / 'manifest.json', release_dir / 'service-worker.js', release_dir / 'data' / 'live.json']:
        text = read_text(path)
        if obsolete_pattern.search(text):
            obsolete_hits.append(str(path))
    check(not obsolete_hits, 'no obsolete hardcoded version remains in staged files', failures)

    lower_index = index_text.lower()
    full_page_placeholder = (
        'coming soon' in lower_index and
        ('<h1>coming soon' in lower_index or '<title>coming soon' in lower_index)
    )
    check(not full_page_placeholder, 'no forbidden Coming Soon full-page placeholder remains', failures)

    verify_db_bootstrap(failures)

    print('\nSUMMARY:')
    if failures:
        print(f'FAIL ({len(failures)} checks failed)')
        for item in failures:
            print(f' - {item}')
        return 1

    print('PASS (all checks passed)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
