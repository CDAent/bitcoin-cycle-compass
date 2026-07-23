import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from db_schema import init_db  # noqa: E402
from snapshot_service import snapshot, upsert_snapshot  # noqa: E402
import release as release_script  # noqa: E402


def _git(*args):
    return subprocess.run(
        ['git', *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def test_gitignore_covers_runtime_database_files():
    content = (ROOT / '.gitignore').read_text(encoding='utf-8')
    for marker in [
        'data/history.db',
        'data/history.db-wal',
        'data/history.db-shm',
        'data/history.db-journal',
    ]:
        assert marker in content


def test_history_database_is_not_tracked():
    tracked = _git('ls-files', 'data/history.db')
    assert tracked == ''


def test_db_bootstrap_creates_schema_and_roundtrip(tmp_path):
    db_path = tmp_path / 'data' / 'history.db'
    conn = init_db(db_path)
    conn.close()
    assert db_path.exists()

    conn = sqlite3.connect(db_path)
    tables = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    }
    conn.close()
    assert {'schema_version', 'btc_daily', 'market_snapshots', 'build_metadata'}.issubset(tables)

    conn = init_db(db_path)
    upsert_snapshot(conn, '2026-02-01', {'btc_usd': 101000.0, 'btc_quality_status': 'live'})
    conn.commit()
    conn.close()
    row = snapshot('2026-02-01', db_path)
    assert row is not None
    assert row['btc_usd'] == 101000.0


def test_existing_database_data_is_preserved(tmp_path):
    db_path = tmp_path / 'data' / 'history.db'
    conn = init_db(db_path)
    conn.execute("INSERT OR IGNORE INTO btc_daily (date, price_usd, source) VALUES ('2026-01-01', 99000, 'test')")
    conn.commit()
    conn.close()

    conn = init_db(db_path)
    value = conn.execute("SELECT price_usd FROM btc_daily WHERE date='2026-01-01'").fetchone()[0]
    conn.close()
    assert value == 99000


def test_build_and_verify_use_staged_output_and_keep_source_clean():
    baseline = _git('status', '--porcelain', '--untracked-files=no')

    subprocess.run(
        [sys.executable, 'scripts/build_release.py', '--stage-dir', 'dist/release', '--allow-dirty-start'],
        cwd=ROOT,
        check=True,
    )
    assert _git('status', '--porcelain', '--untracked-files=no') == baseline

    staged_live = ROOT / 'dist' / 'release' / 'data' / 'live.json'
    assert staged_live.exists()
    payload = json.loads(staged_live.read_text(encoding='utf-8'))
    assert payload.get('historyDaily')
    assert payload.get('historyWeekly')
    assert payload.get('reports', {}).get('sections')

    subprocess.run([sys.executable, 'scripts/verify_release.py', '--release-dir', 'dist/release'], cwd=ROOT, check=True)
    assert _git('status', '--porcelain', '--untracked-files=no') == baseline


def test_release_guard_fails_for_dirty_tree(monkeypatch):
    monkeypatch.setattr(release_script, 'tracked_status', lambda: ' M index.html')
    with pytest.raises(SystemExit):
        release_script.ensure_clean_repo('Before release')


def test_tests_do_not_reference_committed_runtime_history_db():
    needle = 'data/' 'history.db'
    for path in (ROOT / 'tests').glob('*.py'):
        if path.name == 'test_runtime_artifact_separation.py':
            continue
        assert needle not in path.read_text(encoding='utf-8')
