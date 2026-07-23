#!/usr/bin/env python3
import argparse
import subprocess
import sys


def run(cmd, check=True):
    return subprocess.run(cmd, check=check, text=True, capture_output=True)


def out(cmd):
    return run(cmd).stdout.strip()


def fail(message):
    print(f'FAIL: {message}')
    raise SystemExit(1)


def ensure_clean_repo():
    status = out(['git', 'status', '--porcelain'])
    if status:
        fail('Working tree is not clean. Commit/stash changes before tagging.')


def ensure_on_main():
    branch = out(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    if branch != 'main':
        fail(f'Current branch is "{branch}". Switch to "main" before tagging.')


def ensure_at_origin_main_head():
    run(['git', 'fetch', 'origin', 'main'])
    local = out(['git', 'rev-parse', 'HEAD'])
    remote = out(['git', 'rev-parse', 'origin/main'])
    if local != remote:
        fail('HEAD does not match origin/main. Pull/rebase before tagging.')


def ensure_tag_not_exists(tag):
    existing = run(['git', 'tag', '-l', tag]).stdout.strip()
    if existing:
        fail(f'Tag "{tag}" already exists.')


def run_release_checks():
    commands = [
        [sys.executable, 'scripts/build_release.py'],
        [sys.executable, 'scripts/verify_release.py'],
        [sys.executable, '-m', 'pytest', 'tests/', '-q'],
        [sys.executable, '-m', 'py_compile', 'scripts/backfill_history.py', 'scripts/build_release.py',
         'scripts/create_release_tag.py', 'scripts/db_schema.py', 'scripts/history_service.py',
         'scripts/import_history.py', 'scripts/snapshot_service.py', 'scripts/update_data.py', 'scripts/verify_release.py'],
    ]
    for cmd in commands:
        print(f'Running: {" ".join(cmd)}')
        run(cmd)


def create_and_push_tag(tag, message):
    run(['git', 'tag', '-a', tag, '-m', message])
    run(['git', 'push', 'origin', tag])
    print(f'PASS: created and pushed tag {tag}')


def main():
    parser = argparse.ArgumentParser(description='Create a guarded release tag from main.')
    parser.add_argument('--tag', required=True, help='Tag name, e.g. v8.5.2')
    parser.add_argument('--message', default='Bitcoin Cycle Compass Release', help='Annotated tag message')
    args = parser.parse_args()

    ensure_clean_repo()
    ensure_on_main()
    ensure_at_origin_main_head()
    ensure_tag_not_exists(args.tag)
    run_release_checks()
    create_and_push_tag(args.tag, args.message)


if __name__ == '__main__':
    main()
