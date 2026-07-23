#!/usr/bin/env python3
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE_VERSION = '8.5.2'
DEFAULT_STAGE_DIR = ROOT / 'dist' / 'release'
STATIC_FILES = [
    'index.html',
    'manifest.json',
    'service-worker.js',
    'bitcoin-compass-base.png',
    'bitcoin-compass-needle.png',
]


def fail(message):
    print(f'FAIL: {message}')
    return False


def pass_msg(message):
    print(f'PASS: {message}')
    return True


def parse_args():
    parser = argparse.ArgumentParser(description='Build a staged release without mutating tracked source files.')
    parser.add_argument('--stage-dir', default=str(DEFAULT_STAGE_DIR), help='Output staging directory')
    parser.add_argument('--allow-dirty-start', action='store_true', help='Skip clean-tree check before build')
    return parser.parse_args()


def tracked_status():
    result = subprocess.run(
        ['git', 'status', '--porcelain', '--untracked-files=no'],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def ensure_tracked_clean(label):
    status = tracked_status()
    if status:
        print(status)
        raise RuntimeError(f'{label}: tracked working tree is not clean')


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


def prepare_stage_dir(stage_dir):
    if stage_dir.exists():
        shutil.rmtree(stage_dir)
    (stage_dir / 'data').mkdir(parents=True, exist_ok=True)
    for rel in STATIC_FILES:
        src = ROOT / rel
        dest = stage_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    pass_msg(f'Staging directory prepared at {stage_dir}')


def run_updater_in_stage(stage_dir):
    stage_live = stage_dir / 'data' / 'live.json'
    stage_db = stage_dir / 'data' / 'history.db'
    stage_manifest = stage_dir / 'manifest.json'
    cmd = [
        sys.executable,
        str(ROOT / 'scripts' / 'update_data.py'),
        '--output',
        str(stage_live),
        '--db-path',
        str(stage_db),
        '--manifest-path',
        str(stage_manifest),
    ]
    subprocess.run(cmd, check=True, cwd=ROOT)
    pass_msg('Updater completed and staged live.json regenerated')
    return stage_live, stage_db


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def validate_release_files(stage_dir):
    ok = True
    index_text = (stage_dir / 'index.html').read_text(encoding='utf-8')
    sw_text = (stage_dir / 'service-worker.js').read_text(encoding='utf-8')
    manifest = load_json(stage_dir / 'manifest.json')
    live = load_json(stage_dir / 'data' / 'live.json')

    if RELEASE_VERSION in index_text and manifest.get('name', '').endswith(RELEASE_VERSION):
        pass_msg('Version is updated in staged index.html and manifest.json')
    else:
        ok = fail('Version mismatch in staged index.html or manifest.json') and ok

    if f"CACHE_VERSION = '{RELEASE_VERSION}'" in sw_text:
        pass_msg('Staged service worker cache version matches release')
    else:
        ok = fail('Staged service worker cache version mismatch') and ok

    if live.get('appVersion') == RELEASE_VERSION:
        pass_msg('Staged live.json appVersion matches release')
    else:
        ok = fail('Staged live.json appVersion mismatch') and ok

    required_assets = ['bitcoin-compass-base.png', 'bitcoin-compass-needle.png', 'data/live.json', 'data/history.db']
    for asset in required_assets:
        if (stage_dir / asset).exists():
            pass_msg(f'Staged asset exists: {asset}')
        else:
            ok = fail(f'Missing staged asset: {asset}') and ok

    required_controls = [
        'id="sideRefresh"',
        'id="topRefresh"',
        'id="settingsRefresh"',
        'id="mobileHeaderRefresh"',
        'id="mobileMenuBtn"',
        'id="mobileSharedHeader"',
    ]
    for marker in required_controls:
        if marker in index_text:
            pass_msg(f'Staged UI control exists: {marker}')
        else:
            ok = fail(f'Missing staged UI control: {marker}') and ok
    return ok


def main():
    args = parse_args()
    stage_dir = Path(args.stage_dir).resolve()
    try:
        baseline_status = tracked_status()
        if not args.allow_dirty_start:
            ensure_tracked_clean('Before build')
        clean_generated_temp_files()
        prepare_stage_dir(stage_dir)
        run_updater_in_stage(stage_dir)
        if not validate_release_files(stage_dir):
            return 1
        after_status = tracked_status()
        if args.allow_dirty_start:
            if after_status != baseline_status:
                print(after_status)
                print('--- baseline ---')
                print(baseline_status)
                raise RuntimeError('After build: tracked working tree changed unexpectedly')
        else:
            ensure_tracked_clean('After build')
    except subprocess.CalledProcessError as exc:
        print(f'FAIL: command failed with exit code {exc.returncode}')
        return 1
    except RuntimeError as exc:
        print(f'FAIL: {exc}')
        return 1

    print(f'PASS: build_release completed (stage: {stage_dir})')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
