import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE_VERSION = '8.5.2'


def _read(path):
    return (ROOT / path).read_text(encoding='utf-8')


def _json(path):
    return json.loads(_read(path))


def test_refresh_controls_exist():
    html = _read('index.html')
    assert 'id="sideRefresh"' in html
    assert 'id="topRefresh"' in html
    assert 'id="mobileHeaderRefresh"' in html
    assert 'id="settingsRefresh"' in html


def test_mobile_logo_and_hamburger_exist():
    html = _read('index.html')
    assert 'id="mobileHeaderLogo"' in html
    assert 'id="mobileSharedHeader"' in html
    assert 'id="mobileMenuBtn"' in html
    assert 'id="mobileDrawerClose"' in html
    assert 'id="detailClose"' not in html


def test_feedback_support_is_settings_widget_not_nav_view_and_reports_hidden():
    html = _read('index.html')
    assert 'id="settingsSupportCard"' in html
    assert 'data-view="support"' not in html
    assert 'data-view="reports"' not in html
    assert 'reports:()=>{' in html


def test_market_news_has_larger_widget_than_events():
    html = _read('index.html')
    assert '.c-news{grid-column:span 8}' in html
    assert '.c-events{grid-column:span 4}' in html
    assert '.events{display:grid;grid-template-columns:1fr;' in html


def test_alert_threshold_controls_exist():
    html = _read('index.html')
    assert "const ALERT_STORAGE_KEY='btcAlertConfig'" in html
    assert 'alert-threshold-row' in html
    assert 'alert-direction' in html
    assert 'alert-threshold' in html
    assert 'alert-save' in html
    assert 'alert-edit' in html
    assert 'alert-disable' in html
    assert 'alert-reset' in html


def test_no_duplicate_currency_selector_ids():
    html = _read('index.html')
    ids = re.findall(r'id="([^"]+)"', html)
    duplicates = {item for item in ids if ids.count(item) > 1}
    assert not duplicates


def test_version_metadata_consistent():
    html = _read('index.html')
    sw = _read('service-worker.js')
    manifest = _json('manifest.json')
    live = _json('data/live.json')
    assert f'v{RELEASE_VERSION}' in html
    assert manifest['name'].endswith(RELEASE_VERSION)
    assert f"CACHE_VERSION = '{RELEASE_VERSION}'" in sw
    assert live.get('appVersion') == RELEASE_VERSION
    assert live.get('buildMeta', {}).get('appVersion') == RELEASE_VERSION


def test_live_json_and_payloads_present():
    live = _json('data/live.json')
    assert isinstance(live, dict)
    assert len(live.get('historyDaily') or []) > 0
    assert len(live.get('historyWeekly') or []) > 0
    assert len((live.get('reports') or {}).get('sections') or []) > 0


def test_service_worker_removes_old_caches():
    sw = _read('service-worker.js')
    assert 'caches.keys()' in sw
    assert 'caches.delete' in sw
    assert 'self.skipWaiting()' in sw
    assert 'clients.claim()' in sw


def test_mobile_header_is_shared_logic():
    html = _read('index.html')
    assert "function setMobileHeaderTitle(view)" in html
    assert '.topbar{display:none}' in html
    assert '.detail-head{display:none}' in html
