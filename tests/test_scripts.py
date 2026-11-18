import json
from datetime import timedelta

import anomaly_digest
import anomaly_scan
import grafana_poll
import jira_poll

CHECK = {"name": "c", "min_ratio": 0.5, "max_ratio": 2.0, "min_baseline": 10}


def s(inst, v):
    return {"labels": {"instance": inst}, "value": v}


def test_evaluate_drop_spike_disappeared_and_floor():
    cur = [s("a", 20), s("b", 300), s("d", 1)]
    base = [s("a", 100), s("b", 100), s("c", 100), s("d", 2)]
    res = {f["series"]: f["kind"] for f in anomaly_scan.evaluate(CHECK, cur, base)}
    assert res == {"instance=a": "drop", "instance=b": "spike", "instance=c": "disappeared"}


def test_evaluate_within_band_is_quiet():
    assert anomaly_scan.evaluate(CHECK, [s("a", 90)], [s("a", 100)]) == []


def _prom(now_val, week_val, env):
    def handler(m, url, params, body):
        old = float(params["time"]) < (env.now() - timedelta(days=1)).timestamp()
        v = week_val if old else now_val
        return {"status": "success", "data": {"result": [{"metric": {"instance": "s1"}, "value": [0, str(v)]}]}}
    return handler


def test_anomaly_scan_reports_then_cools_down(env, fake, capsys):
    fake({"/api/v1/query": _prom(10, 100, env)})
    anomaly_scan.main()
    first = json.loads(capsys.readouterr().out)
    assert first["new_findings"][0]["kind"] == "drop"
    anomaly_scan.main()
    assert capsys.readouterr().out == ""                       # same finding inside cooldown -> nothing -> [SILENT]
    assert len(env.read_jsonl("anomalies.jsonl")) == 2         # but both runs are recorded for the digest


def test_anomaly_scan_unconfigured_is_silent_but_recorded(env, capsys):
    env.section("anomaly")["checks"][0]["query"] = "TBD"
    anomaly_scan.main()
    assert capsys.readouterr().out == ""
    assert "no anomaly checks configured" in env.read_jsonl("anomaly_runs.jsonl")[0]["errors"][0]


def test_digest_groups_series():
    t = "2026-01-01T00:00:00Z"
    findings = [{"check": "c", "series": "x", "kind": "drop", "ratio": 0.4, "at": t},
                {"check": "c", "series": "x", "kind": "drop", "ratio": 0.1, "at": t}]
    d = anomaly_digest.digest([{"errors": []}, {"errors": ["c: backend_unreachable: x"]}], findings)
    assert d["runs"] == 2 and d["runs_with_errors"] == 1 and d["distinct_series"] == 1
    assert d["series"][0]["count"] == 2 and d["series"][0]["worst_ratio"] == 0.1


def test_grafana_poll_only_new(env, fake, capsys):
    alert = {"fingerprint": "f1", "startsAt": "t1", "labels": {"alertname": "Loss", "instance": "s1"}, "annotations": {}}
    fake({"/alerts": lambda *a: [alert]})
    grafana_poll.main()
    assert json.loads(capsys.readouterr().out)["new_alerts"][0]["alertname"] == "Loss"
    grafana_poll.main()
    assert capsys.readouterr().out == ""


def test_jira_poll_changed_and_skips_own_comment(env, fake, capsys):
    issue = {"key": "CUST-1", "fields": {"summary": "loss", "updated": "u1", "comment": {"comments": []}}}
    f = fake({"/search": lambda *a: {"issues": [issue]}})
    jira_poll.main()
    assert json.loads(capsys.readouterr().out)["tickets"][0]["key"] == "CUST-1"
    assert "project = CUST" in f.calls[0][3]["jql"]
    jira_poll.main()
    assert capsys.readouterr().out == ""                       # unchanged
    issue["fields"]["updated"] = "u2"
    issue["fields"]["comment"]["comments"] = [{"body": "... [noc-engineer:fp:i1]"}]
    jira_poll.main()
    assert capsys.readouterr().out == ""                       # only our own comment changed it
