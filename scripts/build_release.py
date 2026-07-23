#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE_VERSION = '8.5.0-s1.3'


def fail(message):
    print(f'FAIL: {message}')
    return False


def pass_msg(message):
    print(f'PASS: {message}')
    return True


def clean_generated_temp_files():
    for cache_dir in ROOT.rglob('__pycache__'):
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir)
    for pattern in ('*.pyc', '*.pyo'):
        for path in ROOT.rglob(pattern):
            if path.is_file():
                path.unlink()
    for cache_dir in (ROOT / '.pytest_cache', ROOT / '.ruff_cache'):
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
    pass_msg('Cleaned generated temporary files')


def run_updater():
    subprocess.run([sys.executable, str(ROOT / 'scripts' / 'update_data.py')], check=True)
    pass_msg('Updater completed and live.json regenerated')


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def validate_release_files():
    ok = True
    index_text = (ROOT / 'index.html').read_text(encoding='utf-8')
    sw_text = (ROOT / 'service-worker.js').read_text(encoding='utf-8')
    manifest = load_json(ROOT / 'manifest.json')
    live = load_json(ROOT / 'data' / 'live.json')

    if RELEASE_VERSION in index_text and manifest.get('name', '').endswith(RELEASE_VERSION):
        pass_msg('Version is updated in index.html and manifest.json')
    else:
        ok = fail('Version mismatch in index.html or manifest.json') and ok

    if f"CACHE_VERSION = '{RELEASE_VERSION}'" in sw_text:
        pass_msg('Service worker cache version matches release')
    else:
        ok = fail('Service worker cache version mismatch') and ok

    if live.get('appVersion') == RELEASE_VERSION:
        pass_msg('live.json appVersion matches release')
    else:
        ok = fail('live.json appVersion mismatch') and ok

    required_assets = ['bitcoin-compass-base.png', 'bitcoin-compass-needle.png', 'data/live.json']
    for asset in required_assets:
        if (ROOT / asset).exists():
            pass_msg(f'Asset exists: {asset}')
        else:
            ok = fail(f'Missing required asset: {asset}') and ok

    required_controls = ['id="sideRefresh"', 'id="topRefresh"', 'id="settingsRefresh"', 'id="mobileMenuBtn"', 'id="detailMenuBtn"']
    for marker in required_controls:
        if marker in index_text:
            pass_msg(f'UI control exists: {marker}')
        else:
            ok = fail(f'Missing required UI control: {marker}') and ok

    return ok


def main():
    try:
        clean_generated_temp_files()
        run_updater()
    except subprocess.CalledProcessError as exc:
        print(f'FAIL: updater failed with exit code {exc.returncode}')
        return 1

    if not validate_release_files():
        return 1

    print('PASS: build_release completed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
