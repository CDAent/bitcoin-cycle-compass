import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import update_data  # noqa: E402


def _proxy():
    return {
        'status': 'live proxy',
        'score': 55,
        'label': 'Positive demand',
        'return1d': 1.2,
        'volumeVs20d': 1.1,
        'funds': [],
    }


def test_etf_daily_positive(monkeypatch):
    monkeypatch.setattr(update_data, 'etf_demand_proxy', _proxy)
    monkeypatch.setattr(update_data, '_parse_farside', lambda url: [{'date': '2026-07-24', 'usdMillions': 25.0}])
    out = update_data.etf_flow({})
    assert out['status'] == 'live'
    assert out['dailyUsdMillions'] == 25.0


def test_etf_daily_negative(monkeypatch):
    monkeypatch.setattr(update_data, 'etf_demand_proxy', _proxy)
    monkeypatch.setattr(update_data, '_parse_farside', lambda url: [{'date': '2026-07-24', 'usdMillions': -12.5}])
    out = update_data.etf_flow({})
    assert out['status'] == 'live'
    assert out['dailyUsdMillions'] == -12.5


def test_etf_daily_genuine_zero(monkeypatch):
    monkeypatch.setattr(update_data, 'etf_demand_proxy', _proxy)
    monkeypatch.setattr(update_data, '_parse_farside', lambda url: [{'date': '2026-07-24', 'usdMillions': 0.0}])
    out = update_data.etf_flow({})
    assert out['status'] == 'live'
    assert out['dailyUsdMillions'] == 0.0


def test_etf_missing_source_value(monkeypatch):
    monkeypatch.setattr(update_data, 'etf_demand_proxy', _proxy)
    monkeypatch.setattr(update_data, '_parse_farside', lambda url: [])
    out = update_data.etf_flow({})
    assert out['status'] == 'unavailable'
    assert out['dailyUsdMillions'] is None


def test_etf_parsing_failure(monkeypatch):
    monkeypatch.setattr(update_data, 'etf_demand_proxy', _proxy)
    def _fail(url):
        raise RuntimeError('parse failed')
    monkeypatch.setattr(update_data, '_parse_farside', _fail)
    out = update_data.etf_flow({})
    assert out['status'] == 'unavailable'
    assert out['dailyUsdMillions'] is None
    assert out['errors']


def test_etf_stale_data(monkeypatch):
    monkeypatch.setattr(update_data, 'etf_demand_proxy', _proxy)
    monkeypatch.setattr(update_data, '_parse_farside', lambda url: [{'date': '2024-01-01', 'usdMillions': 10.0}])
    out = update_data.etf_flow({'dailyUsdMillions': 42.0, 'date': '2026-07-20'})
    assert out['status'] == 'stale'
    assert out['dailyUsdMillions'] is None
    assert out['dailyAvailable'] is False


def test_etf_failure_does_not_overwrite_last_valid(monkeypatch):
    monkeypatch.setattr(update_data, 'etf_demand_proxy', _proxy)
    def _fail(url):
        raise RuntimeError('upstream down')
    monkeypatch.setattr(update_data, '_parse_farside', _fail)
    prev = {'status': 'live', 'dailyUsdMillions': 123.4, 'date': '2026-07-23'}
    out = update_data.etf_flow(prev)
    assert out['dailyUsdMillions'] is None
    assert out['lastValidDailyUsdMillions'] == 123.4
    assert out['lastValidDate'] == '2026-07-23'
