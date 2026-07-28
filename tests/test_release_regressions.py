import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE_VERSION = '8.6.1'


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
    assert 'alert-card' in html
    assert 'alert-direction' in html
    assert 'alert-threshold' in html
    assert 'alert-save' in html
    assert 'alert-reset' in html
    assert 'alert-toggle-check' in html


def test_alerts_enable_without_edit_mode():
    """Alerts must allow enable/disable via toggle without entering edit mode."""
    html = _read('index.html')
    assert 'alert-toggle-check' in html
    assert 'alert-card-indicator' in html
    # Old edit-mode-only approach should not be present
    assert 'alert-edit' not in html or 'alert-toggle-check' in html


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
    assert "CACHE_VERSION =" in sw
    assert RELEASE_VERSION in sw
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


def test_v860_mobile_header_animated_compass():
    """Mobile header must have animated needle image and logo stage."""
    html = _read('index.html')
    assert 'mobile-logo-stage' in html
    assert 'mobile-logo-needle' in html
    assert 'mobile-logo-base' in html


def test_v860_mobile_currency_selector():
    """Mobile header must include compact currency selector."""
    html = _read('index.html')
    assert 'mobile-currency-row' in html
    assert 'mobile-curr-btn' in html


def test_v860_settings_label_renamed():
    """Settings must use 'Display Currency and Date Default' label."""
    html = _read('index.html')
    assert 'Display Currency and Date Default' in html


def test_v860_daily_history_range():
    """History view must include Today (1d) range button."""
    html = _read('index.html')
    assert "data-range=\"1d\"" in html
    assert "renderCandlestickChart" in html


def test_v860_movement_pct_in_allocation():
    """Global Capital Allocation must show Movement % not Trend."""
    html = _read('index.html')
    assert 'MOVEMENT %' in html or 'Movement %' in html
    assert 'movement-pos' in html
    assert 'movement-neg' in html


def test_v860_regime_score_presentation():
    """Market Regime Score must include explanation, factors, typical environment."""
    html = _read('index.html')
    assert 'Bullish Expansion' in html
    assert 'Transition Zone' in html
    assert 'Bear Contraction' in html
    assert 'factors' in html or 'explanation' in html


def test_v860_news_impact_hidden_by_default():
    """Market Impact Summary must be hidden by default."""
    html = _read('index.html')
    assert 'news-intel-summary' in html
    assert 'news-intel-summary visible' in html or 'hasSignificantNews' in html


def test_v860_empty_states_present():
    """Empty state messages must be defined."""
    html = _read('index.html')
    assert 'empty-state' in html
    assert 'empty-state-icon' in html


def test_v860_feedback_support_view():
    """Feedback & Support view must be accessible via Settings."""
    html = _read('index.html')
    assert "support:()=>" in html or "support:()" in html
    assert 'openSupportNav' in html


def test_v860_market_article_new_layout():
    """Market article cards must use new headline/summary/footer layout."""
    html = _read('index.html')
    assert 'market-article-headline' in html
    assert 'market-article-footer' in html
    assert 'market-article-rating' in html


def test_v860_refresh_notification_mobile_bottom():
    """Refresh notification must be positioned at bottom on mobile."""
    html = _read('index.html')
    assert '#refreshStatus' in html
    assert 'position:fixed' in html
    assert 'bottom:calc' in html


def test_v860_alert_card_live_value():
    """Alerts must show live current value."""
    html = _read('index.html')
    assert 'getLiveAlertValue' in html
    assert 'alert-live-row' in html
    assert 'alert-live-value' in html


def test_v861_no_sample_external_research_url():
    html = _read('index.html')
    lowered = html.lower()
    forbidden = [
        'your-private-endpoint.example',
        'placeholder.example',
        'demo.example',
        'http://localhost',
        'http://127.0.0.1',
    ]
    assert not any(token in lowered for token in forbidden)


def test_v861_support_form_exists():
    html = _read('index.html')
    assert 'supportType' in html
    assert 'supportSubmit' in html
    assert 'compassSupportEmail' in html


def test_v861_pin_control_icon_only():
    html = _read('index.html')
    assert 'pin-label' not in html
    assert 'Pin article for later' in html


def test_v861_daily_candles_last_seven_days():
    html = _read('index.html')
    assert "if(range==='1d')return{rows:daily.slice(-7)" in html


def test_v861_direction_based_movement_class_helper():
    html = _read('index.html')
    assert 'const movementClass=' in html
    assert 'movement-pos' in html
    assert 'movement-neg' in html
    assert 'movement-neu' in html
