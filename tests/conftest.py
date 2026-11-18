import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "noc-tools" / "scripts"))
sys.path.insert(0, str(ROOT / "scripts"))

import noclib  # noqa: E402


class FakeHttp:
    """Routes requests by URL substring to handlers: {substr: fn(method, url, params, body) -> response}."""

    def __init__(self, routes):
        self.routes, self.calls = routes, []

    def request(self, method, url, params=None, body=None, headers=None):
        self.calls.append((method, url, params, body))
        for k, fn in self.routes.items():
            if k in url:
                return fn(method, url, params, body)
        raise AssertionError(f"unexpected call {method} {url}")


BASE_CFG = {
    "prometheus": {"url": "http://prom", "max_series": 50},
    "elasticsearch": {"url": "http://es", "default_index": "logs-*", "max_hits": 50},
    "grafana": {"url": "http://grafana", "token": "t"},
    "jira": {"url": "http://jira", "token": "t", "customer_jql": "project = CUST", "comment_marker": "noc-engineer",
             "allow_comment": "false"},
    "anomaly": {"baseline": "-7d", "cooldown_minutes": 60, "checks": [
        {"name": "port_in_rate", "query": "sum by (instance) (rate(rx[5m]))", "min_ratio": 0.5, "max_ratio": 2.0}]},
}


@pytest.fixture
def env(tmp_path, monkeypatch):
    import copy
    monkeypatch.setattr(noclib, "HERMES_HOME", tmp_path)
    noclib.set_config(copy.deepcopy(BASE_CFG))
    yield noclib
    noclib.set_config(None)


@pytest.fixture
def fake(monkeypatch):
    def install(routes):
        f = FakeHttp(routes)
        monkeypatch.setattr(noclib, "HTTP", f)
        return f
    return install
