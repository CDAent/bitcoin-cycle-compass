#!/usr/bin/env python3
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE_VERSION = '8.5.2'


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


def main():
    failures = []
    index_text = read_text(ROOT / 'index.html')
    sw_text = read_text(ROOT / 'service-worker.js')
    manifest = read_json(ROOT / 'manifest.json')
    live = read_json(ROOT / 'data' / 'live.json')

    check(f'v{RELEASE_VERSION}' in index_text, 'index.html visible version matches release', failures)
    check(manifest.get('name', '').endswith(RELEASE_VERSION), 'manifest version matches release', failures)
    check(live.get('appVersion') == RELEASE_VERSION, 'live.json appVersion matches release', failures)
    check(live.get('buildMeta', {}).get('appVersion') == RELEASE_VERSION, 'build metadata version matches release', failures)
    check(f"CACHE_VERSION = '{RELEASE_VERSION}'" in sw_text, 'service-worker cache version matches release', failures)

    check(isinstance(live, dict), 'live.json exists and parses', failures)
    check(bool(live.get('historyDaily')), 'historyDaily is populated', failures)
    check(bool(live.get('historyWeekly')), 'historyWeekly is populated', failures)
    check(bool(live.get('reports')) and bool(live.get('reports', {}).get('sections')), 'reports payload exists', failures)

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
    for path in [ROOT / 'index.html', ROOT / 'manifest.json', ROOT / 'service-worker.js', ROOT / 'data' / 'live.json']:
        text = read_text(path)
        if obsolete_pattern.search(text):
            obsolete_hits.append(str(path))
    check(not obsolete_hits, 'no obsolete hardcoded version remains', failures)

    lower_index = index_text.lower()
    full_page_placeholder = (
        'coming soon' in lower_index and
        ('<h1>coming soon' in lower_index or '<title>coming soon' in lower_index)
    )
    check(not full_page_placeholder, 'no forbidden Coming Soon full-page placeholder remains', failures)

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
