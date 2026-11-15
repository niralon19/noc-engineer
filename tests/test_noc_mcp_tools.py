"""Offline tests for noc-mcp tools: a fake HTTP layer stands in for Prometheus, ECK, Argo, Kubernetes, Grafana,
the rules system and Jira."""
import json
import sys
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlparse

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "noc-mcp"))

from context import Context, set_context  # noqa: E402
from schemas.common import ToolError, iso, now  # noqa: E402
from tools import changes, health, investigation, jira, kafka, monitoring, pipeline, rules, servers  # noqa: E402,F401
from tools._base import REGISTRY  # noqa: E402

NOW = now()


class FakeHttp:
    def __init__(self, routes):
        self.routes, self.calls = routes, []

    def request(self, method, url, **kw):
        self.calls.append((method, url, kw))
        for (m, frag), handler in self.routes.items():
            if m == method and frag in url:
                return handler(url, kw) if callable(handler) else handler
        raise ToolError("not_found", f"no fake route for {method} {urlparse(url).path}")

    def get(self, url, **kw):
        return self.request("GET", url, **kw)

    def post(self, url, **kw):
        return self.request("POST", url, **kw)


def prom_vector(values_by_instance):
    return {"status": "success", "data": {"resultType": "vector", "result": [
        {"metric": {"instance": i}, "value": [NOW.timestamp(), str(v)]} for i, v in values_by_instance.items()]}}


PIPELINE = {"verified": False, "hops": [
    {"id": "kafka_ingest", "per_rule": False,
     "in_query": 'sum by (instance) (increase(produced{instance=~"{instances}"}[{range}]))',
     "out_query": 'sum by (instance) (increase(consumed{instance=~"{instances}"}[{range}]))',
     "lag_query": "TBD"},
    {"id": "rule_matching", "per_rule": True, "in_query": 'sum(increase(seen{rule="{rule_id}"}[{range}]))', "matched_query": "TBD"},
    {"id": "server_nic", "in_query": "TBD", "out_query": "TBD"},
], "kpis": {"hermeticity": {"definition": "matched/expected", "query": 'hermeticity{rule="{rule_id}"}'},
            "coupling": {"definition": "coupled/eligible", "query": "TBD"}}}


def ctx_with(routes, **settings):
    base = {"prometheus": {"url": "http://prom", "local_retention_hours": 24}, "thanos": {"url": "http://thanos"},
            "security": {"allow_writes": "false"}}
    base.update(settings)
    c = Context(base, PIPELINE, FakeHttp(routes))
    set_context(c)
    return c


@pytest.fixture(autouse=True)
def _reset():
    yield
    set_context(None)


# ---------- pipeline
def test_hop_counts_detects_divergence_and_marks_missing_measures():
    def prom(url, kw):
        q, t = kw["params"]["query"], float(kw["params"]["time"])
        current = abs(t - NOW.timestamp()) < 3600
        if "produced" in q:
            return prom_vector({"srv1": 1000, "srv2": 1000})
        return prom_vector({"srv1": 500 if current else 990, "srv2": 1000 if current else 995})
    ctx_with({("GET", "/api/v1/query"): prom})
    r = pipeline.get_hop_counts("kafka_ingest", instances=["srv1", "srv2"], start="-30m", end="now")
    assert r["ok"], r
    d = r["data"]
    assert d["measures"]["out"]["by_instance"] == {"instance=srv1": 500.0, "instance=srv2": 1000.0}
    assert d["derived"]["out_in_ratio"]["current"] == 0.75
    assert any("diverges" in h for h in d["derived"]["hints"])
    assert "not instrumented at this hop: lag" in r["notes"]
    assert 'instance=~"srv1|srv2"' in d["measures"]["in"]["query"] and "[1800s]" in d["measures"]["in"]["query"]


def test_hop_counts_uses_thanos_for_old_baselines():
    c = ctx_with({("GET", "/api/v1/query"): prom_vector({"a": 1})})
    pipeline.get_hop_counts("kafka_ingest", compare="7d")
    hosts = {urlparse(u).netloc for _, u, _ in c.http.calls}
    assert hosts == {"prom", "thanos"}


def test_hop_not_instrumented_and_rule_required():
    ctx_with({})
    r = pipeline.get_hop_counts("server_nic")
    assert not r["ok"] and r["error"]["code"] == "hop_not_instrumented"
    r = pipeline.get_hop_counts("rule_matching")
    assert r["error"]["code"] == "bad_argument" and "rule_id" in r["error"]["message"]
    assert pipeline.get_hop_counts("nowhere")["error"]["code"] == "bad_argument"


def test_pipeline_map_reports_instrumentation():
    ctx_with({})
    d = pipeline.get_pipeline_map()["data"]
    assert d["hops"][0]["instrumented"] == ["in", "out"] and d["kpis"]["coupling"]["instrumented"] is False


# ---------- rules
RULES_CFG = {"base_url": "http://rules", "get_rule_path": "/api/rules/{rule_id}",
             "changes_path": "/api/rules/{rule_id}/history?from={start}&to={end}", "global_changes_path": "TBD",
             "changes_list_field": "items", "change_fields": {"time": "changedAt", "author": "by", "summary": "desc"},
             "rule_path_path": "TBD", "rule_paths_file": None}


def test_rule_changes_maps_fields_and_notes_missing_global():
    ctx_with({("GET", "/api/rules/R1/history"): {"items": [{"changedAt": "2026-11-14T10:00:00Z", "by": "dana", "desc": "scope +10.0.0.0/8"}]}},
             rules=RULES_CFG)
    r = rules.get_rule_changes("R1", start="-6h")
    assert r["ok"] and r["data"]["rule_changes"][0]["author"] == "dana"
    assert any("global" in n for n in r["notes"])


def test_rule_path_from_static_file(tmp_path):
    f = tmp_path / "rule-paths.yaml"
    f.write_text(yaml.safe_dump({"rules": {"CUST-A-*": {"servers": ["s1", "s2"], "argo_apps": ["proc"]}}}))
    ctx_with({}, rules=RULES_CFG | {"rule_paths_file": str(f)})
    assert rules.get_rule_path("CUST-A-17")["data"]["path"]["servers"] == ["s1", "s2"]
    assert rules.get_rule_path("OTHER")["error"]["code"] == "not_found"


def test_rule_kpis_skips_tbd_and_returns_baselines():
    ctx_with({("GET", "/api/v1/query_range"): {"status": "success", "data": {"result": [
                {"metric": {}, "values": [[NOW.timestamp() - 60, "0.99"], [NOW.timestamp(), "0.80"]]}]}},
              ("GET", "/api/v1/query"): prom_vector({"x": 0.8})})
    r = rules.get_rule_kpis("R1")
    assert r["ok"] and r["data"]["kpis"]["hermeticity"]["window_value"] == 0.8
    assert "coupling: query TBD in pipeline.yaml" in r["notes"]


# ---------- changes
def test_argo_history_filters_window_and_uses_rule_path(tmp_path):
    f = tmp_path / "rp.yaml"
    f.write_text(yaml.safe_dump({"rules": {"R1": {"argo_apps": ["proc"]}}}))
    app = {"status": {"history": [{"deployedAt": iso(NOW - timedelta(hours=1)), "revision": "abc", "id": 5},
                                  {"deployedAt": iso(NOW - timedelta(days=3)), "revision": "old", "id": 4}],
                      "sync": {"status": "Synced"}, "health": {"status": "Healthy"},
                      "operationState": {"phase": "Succeeded", "finishedAt": iso(NOW - timedelta(hours=1))}}}
    ctx_with({("GET", "/api/v1/applications/proc"): app}, argocd={"url": "http://argo"},
             rules=RULES_CFG | {"rule_paths_file": str(f)})
    r = changes.get_argo_sync_history(rule_id="R1")
    assert [d["revision"] for d in r["data"]["apps"][0]["deploys_in_window"]] == ["abc"]


def test_deployment_history_filters_by_service_and_time():
    def rs(name, owner, age_h):
        return {"metadata": {"name": name, "namespace": "ns", "creationTimestamp": iso(NOW - timedelta(hours=age_h)),
                             "ownerReferences": [{"kind": "Deployment", "name": owner}],
                             "annotations": {"deployment.kubernetes.io/revision": "7"}},
                "spec": {"template": {"spec": {"containers": [{"image": "reg/proc:1.2"}]}}}, "status": {"readyReplicas": 2}}
    ctx_with({("GET", "/apis/apps/v1/namespaces/ns/replicasets"): {"items": [rs("a", "enricher", 2), rs("b", "enricher", 50), rs("c", "other", 1)]}},
             kubernetes={"clusters": {"openshift": {"api_url": "http://k8s", "token": "t"}}})
    r = changes.get_deployment_history("openshift", namespace="ns", service="enricher")
    assert [x["images"] for x in r["data"]["rollouts"]] == [["reg/proc:1.2"]]
    assert changes.get_deployment_history("nope")["error"]["code"] == "bad_argument"


def test_maintenance_from_grafana_silences_matches_server():
    sil = [{"startsAt": iso(NOW - timedelta(hours=2)), "endsAt": iso(NOW + timedelta(hours=1)), "comment": "kernel upgrade",
            "matchers": [{"name": "instance", "value": "srv[12]", "isRegex": True}], "status": {"state": "active"}},
           {"startsAt": iso(NOW - timedelta(days=5)), "endsAt": iso(NOW - timedelta(days=4)), "matchers": []}]
    ctx_with({("GET", "/silences"): sil}, maintenance={"source": "grafana_silences", "grafana_url": "http://graf"})
    r = changes.get_maintenance_windows(servers=["srv1"])
    assert [w["comment"] for w in r["data"]["windows"]] == ["kernel upgrade"]
    assert changes.get_maintenance_windows(servers=["srv9"])["data"]["windows"] == []


# ---------- servers / kafka / monitoring
def test_server_drops_requires_config_and_scopes_instances():
    ctx_with({("GET", "/api/v1/query"): prom_vector({"srv1": 120})}, server_queries={"rx_drops": 'x{instance=~"{instances}"}[{range}]', "cpu": "TBD"})
    r = servers.get_server_drops(["srv1"])
    assert r["data"]["measures"]["rx_drops"]["by_server"] == {"instance=srv1": 120.0} and "cpu" in r["notes"][0]
    ctx_with({}, server_queries={"rx_drops": "TBD"})
    assert servers.get_server_drops(["srv1"])["error"]["code"] == "not_configured"


def test_consumer_lag_trend():
    series = {"status": "success", "data": {"result": [
        {"metric": {"topic": "t", "partition": "3"}, "values": [[1, "100"], [2, "5000"]]},
        {"metric": {"topic": "t", "partition": "1"}, "values": [[1, "10"], [2, "10"]]}]}}
    ctx_with({("GET", "/api/v1/query_range"): series}, kafka_queries={"consumer_lag_by_partition": 'lag{group="{group}"}'})
    d = kafka.get_consumer_lag("grp")["data"]
    assert d["top_partitions"][0]["partition"] == "3" and d["top_partitions"][0]["trend"] == "growing" and d["summary"]["growing"] == 1


def test_query_logs_groups_with_first_seen():
    body = {"hits": {"total": {"value": 2}, "hits": [{"_index": "logs", "_source": {"@timestamp": "t1", "message": "x" * 500, "svc": "a"}}]},
            "aggregations": {"by": {"buckets": [{"key": "ConnTimeout", "doc_count": 42, "first_seen": {"value_as_string": "t0"}}]}}}
    c = ctx_with({("POST", "/logs/_search"): body}, elasticsearch={"url": "http://es", "default_index": "logs"})
    d = monitoring.query_logs("level:error", group_by="error.type", size=500)["data"]
    assert d["groups"][0] == {"value": "ConnTimeout", "count": 42, "first_seen": "t0"} and len(d["hits"][0]["message"]) == 300
    assert c.http.calls[0][2]["json"]["size"] == 50


def test_backend_timeout_is_retryable_error():
    def boom(url, kw):
        raise ToolError("backend_timeout", "timeout calling prom", retryable=True)
    ctx_with({("GET", "/api/v1/query_range"): boom})
    r = monitoring.query_metrics("up")
    assert r["ok"] is False and r["error"]["retryable"] is True


# ---------- history + jira
def test_history_search(tmp_path):
    from history import History
    c = ctx_with({}, history={"path": str(tmp_path / "h.jsonl")})
    h = History(c)
    h.save({"investigation_id": "I1", "fingerprint": "fp1", "status": "CONFIRMED", "headline": "lag on p3",
            "suspected_location": {"hop": "kafka_ingest", "rule_id": "R1"}})
    h.save({"investigation_id": "I2", "fingerprint": "fp2", "suspected_location": {"hop": "server_nic"}})
    assert [i["investigation_id"] for i in investigation.search_investigations(rule_id="R1")["data"]["investigations"]] == ["I1"]
    assert investigation.search_investigations(hop="server_nic")["data"]["count"] == 1


GOOD = {"investigation_id": "INV-1", "fingerprint": "abcdef0123456789xyz", "source": "grafana_alert", "status": "CONFIRMED",
        "headline": "Hermeticity drop on R1 caused by consumer lag on partition 3 since 14:05",
        "suspected_location": {"hop": "kafka_ingest", "rule_id": "R1", "component": "topic-x", "instances": ["p3"]},
        "onset_time": "2026-11-14T14:05:00Z",
        "candidates": [{"location": {"hop": "kafka_ingest"}, "verdict": "confirmed", "evidence_for": ["e1"]}],
        "evidence": [{"ref": "e1", "tool": "get_consumer_lag", "query": "lag", "time_range": {"start": "a", "end": "b"},
                      "observation": "lag grew 100 -> 5000 on p3"}],
        "ruled_out": {"server_nic": "no drops on any server"}}


def jira_ctx(allow=True):
    posted = []
    routes = {("GET", "/comment"): lambda u, kw: {"comments": [{"body": b} for b in posted]},
              ("POST", "/comment"): lambda u, kw: posted.append(kw["json"]["body"]) or {"id": "1"}}
    ctx_with(routes, jira={"url": "http://jira", "token": "t"}, security={"allow_writes": str(allow).lower()})
    return posted


def test_comment_blocked_when_writes_disabled():
    jira_ctx(allow=False)
    assert jira.add_investigation_comment("NOC-1", GOOD)["error"]["code"] == "permission_denied"


def test_comment_rejects_invalid_investigation():
    jira_ctx()
    bad = dict(GOOD, ruled_out={}, suspected_location={"hop": "made_up_hop"})
    r = jira.add_investigation_comment("NOC-1", bad)
    assert r["error"]["code"] == "validation_failed" and "ruled_out" in r["error"]["message"]


def test_comment_posts_once_with_marker(tmp_path):
    posted = jira_ctx()
    from context import get_context
    get_context().settings["security"]["audit_log"] = str(tmp_path / "audit.jsonl")
    r1 = jira.add_investigation_comment("NOC-1", GOOD)
    r2 = jira.add_investigation_comment("NOC-1", GOOD)
    assert r1["data"]["posted"] is True and r2["data"]["posted"] is False and len(posted) == 1
    assert "Ruled out:" in posted[0] and "[noc-engineer:abcdef0123456789:INV-1]" in posted[0]
    lines = [json.loads(l) for l in (tmp_path / "audit.jsonl").read_text().splitlines()]
    outcomes = [l["outcome"] for l in lines]
    assert outcomes == ["posted", "ok", "skipped:duplicate", "ok"]      # policy record + per-call record for each call
    assert all(l["tool"] == "add_investigation_comment" for l in lines)
    assert "token" not in json.dumps(lines[0])


# ---------- server wiring
def test_every_tool_in_hermes_include_is_implemented():
    cfg = yaml.safe_load((ROOT / "hermes-profile" / "config.yaml").read_text())
    include = set(cfg["mcp_servers"]["noc_mcp"]["tools"]["include"])
    assert include <= set(REGISTRY), include - set(REGISTRY)


def test_mcp_server_lists_tools():
    import asyncio
    import server
    tools = asyncio.run(server.build().list_tools())
    names = {t.name for t in tools}
    assert names == set(REGISTRY) and len(names) >= 18


def test_not_configured_names_the_question_and_health_lists_it():
    from tools import health
    ctx_with({}, server_queries={"rx_drops": "TBD"}, elasticsearch={"url": "http://es"})
    r = servers.get_server_drops(["s1"])
    assert r["error"]["code"] == "not_configured" and "G2" in r["error"]["message"]
    assert "G4" in monitoring.query_logs("x")["error"]["message"]
    ask = health.noc_mcp_health()["data"]["ask_team"]
    assert any(a.startswith("E1") for a in ask) and any(a.startswith("H1") for a in ask)


def test_every_tool_call_is_audited_including_reads_and_failures(tmp_path):
    log = tmp_path / "audit.jsonl"
    ctx_with({("GET", "/api/v1/query"): prom_vector({"a": 1})}, security={"allow_writes": "false", "audit_log": str(log)},
             server_queries={"rx_drops": "x"})
    servers.get_server_drops(["srv1"])
    pipeline.get_hop_counts("server_nic")                         # error path
    jira.add_investigation_comment("NOC-1", GOOD)                 # denied write
    recs = [json.loads(l) for l in log.read_text().splitlines()]
    assert [(r["tool"], r["outcome"]) for r in recs] == [
        ("get_server_drops", "ok"), ("get_hop_counts", "error:hop_not_instrumented"),
        ("add_investigation_comment", "error:permission_denied")]
    assert recs[2]["args"]["_write"] is True and recs[2]["investigation"]["id"] == "INV-1"


def test_http_transport_requires_bearer_token():
    import os
    import socket
    import subprocess
    import time
    import urllib.request
    s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
    env = {**os.environ, "NOC_MCP_TOKEN": "s3cret"}
    srv = ROOT / "noc-mcp" / "server.py"
    no_token = subprocess.run(["python3", str(srv), "--http", "--port", str(port)], capture_output=True, text=True,
                              env={k: v for k, v in env.items() if k != "NOC_MCP_TOKEN"}, timeout=20)
    assert no_token.returncode != 0 and "NOC_MCP_TOKEN" in no_token.stderr
    p = subprocess.Popen(["python3", str(srv), "--http", "--host", "127.0.0.1", "--port", str(port)], env=env,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(50):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/healthz", timeout=1); break
            except Exception:
                time.sleep(0.2)
        body = b'{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"t","version":"1"}}}'
        def call(token):
            req = urllib.request.Request(f"http://127.0.0.1:{port}/mcp", data=body, method="POST",
                                         headers={"content-type": "application/json", "accept": "application/json, text/event-stream",
                                                  **({"authorization": f"Bearer {token}"} if token else {})})
            try:
                return urllib.request.urlopen(req, timeout=5).status
            except urllib.error.HTTPError as e:
                return e.code
        assert call(None) == 401 and call("wrong") == 401 and call("s3cret") == 200
    finally:
        p.terminate(); p.wait(timeout=10)
