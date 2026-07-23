#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd, check=True):
    return subprocess.run(cmd, cwd=ROOT, check=check, text=True, capture_output=True)


def out(cmd):
    return run(cmd).stdout.strip()


def fail(message):
    print(f'FAIL: {message}')
    raise SystemExit(1)


def tracked_status():
    return out(['git', 'status', '--porcelain', '--untracked-files=no'])


def ensure_clean_repo(label):
    status = tracked_status()
    if status:
        print(status)
        fail(f'{label}: tracked working tree is not clean')


def ensure_on_main():
    branch = out(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    if branch != 'main':
        fail(f'Current branch is "{branch}". Switch to "main" before release.')


def ensure_at_origin_main_head():
    run(['git', 'fetch', 'origin', 'main'])
    local = out(['git', 'rev-parse', 'HEAD'])
    remote = out(['git', 'rev-parse', 'origin/main'])
    if local != remote:
        fail('HEAD does not match origin/main. Pull/rebase before release.')


def app_version():
    manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
    name = manifest.get('name', '')
    match = re.search(r'(\d+\.\d+\.\d+(?:-[A-Za-z0-9\.-]+)?)$', name)
    if not match:
        fail('Could not determine app version from manifest.json')
    return match.group(1)


def ensure_tag_not_exists(tag):
    if run(['git', 'tag', '-l', tag]).stdout.strip():
        fail(f'Tag "{tag}" already exists.')


def run_release_checks():
    commands = [
        [sys.executable, 'scripts/build_release.py', '--stage-dir', 'dist/release'],
        [sys.executable, 'scripts/verify_release.py', '--release-dir', 'dist/release'],
        [sys.executable, '-m', 'pytest', 'tests/', '-q'],
        [sys.executable, '-m', 'py_compile', 'scripts/backfill_history.py', 'scripts/build_release.py',
         'scripts/create_release_tag.py', 'scripts/db_schema.py', 'scripts/history_service.py',
         'scripts/import_history.py', 'scripts/release.py', 'scripts/snapshot_service.py', 'scripts/update_data.py', 'scripts/verify_release.py'],
    ]
    for cmd in commands:
        print(f'Running: {" ".join(cmd)}')
        subprocess.run(cmd, cwd=ROOT, check=True)


def create_and_push_tag(tag, message):
    run(['git', 'tag', '-a', tag, '-m', message])
    tag_commit = out(['git', 'rev-list', '-n', '1', tag])
    origin_main = out(['git', 'rev-parse', 'origin/main'])
    if tag_commit != origin_main:
        fail(f'Tag {tag} does not point to origin/main (tag={tag_commit}, origin/main={origin_main})')
    run(['git', 'push', 'origin', tag])
    print(f'PASS: created and pushed tag {tag}')


def main():
    parser = argparse.ArgumentParser(description='Guarded release entrypoint from main branch.')
    parser.add_argument('--tag', required=True, help='Tag name, e.g. v8.5.2')
    parser.add_argument('--message', default='Bitcoin Cycle Compass Release', help='Annotated tag message')
    args = parser.parse_args()

    ensure_clean_repo('Before release')
    ensure_on_main()
    ensure_at_origin_main_head()
    version = app_version()
    expected_tag = f'v{version}'
    if args.tag != expected_tag:
        fail(f'Tag {args.tag} does not match application version ({expected_tag}).')
    ensure_tag_not_exists(args.tag)

    run_release_checks()
    ensure_clean_repo('After build and verification')
    ensure_at_origin_main_head()
    create_and_push_tag(args.tag, args.message)


if __name__ == '__main__':
    main()
