import json

import noc


def run(capsys, *argv):
    code = noc.main(list(argv))
    return code, json.loads(capsys.readouterr().out)


def test_health_reports_configuration(env, capsys):
    env.section("jira")["customer_jql"] = "TBD"
    code, res = run(capsys, "health")
    assert code == 0
    assert res["data"]["prometheus"] == "configured"
    assert res["data"]["jira_customer_jql"] == "not_configured"
    assert res["data"]["anomaly_checks"] == "1/1 configured"
    assert res["data"]["jira_comment"] == "disabled"


def test_not_configured_is_an_error_not_healthy(env, capsys):
    env.section("prometheus")["url"] = "TBD"
    code, res = run(capsys, "metrics", "up")
    assert code == 1 and res["error"]["code"] == "not_configured"


def test_metrics_range_is_summarised(env, fake, capsys):
    series = [{"metric": {"instance": f"s{i}"}, "values": [[1, "1"], [2, "3"]]} for i in range(3)]
    fake({"/api/v1/query_range": lambda *a: {"status": "success", "data": {"result": series}}})
    code, res = run(capsys, "metrics", "sum by (instance) (x)", "--start", "-1h")
    assert code == 0
    s = res["data"]["series"][0]
    assert (s["min"], s["max"], s["points"]) == (1.0, 3.0, 2)


def test_logs_group_by_first_seen(env, fake, capsys):
    body = {"hits": {"total": {"value": 1}, "hits": [{"_source": {"@timestamp": "t", "message": "boom", "pod": "p1"}}]},
            "aggregations": {"by": {"buckets": [{"key": "E1", "doc_count": 4, "first_seen": {"value_as_string": "t0"}}]}}}
    f = fake({"/_search": lambda *a: body})
    code, res = run(capsys, "logs", "level:error", "--group-by", "error.code")
    assert code == 0 and res["data"]["groups"][0] == {"value": "E1", "count": 4, "first_seen": "t0"}
    assert "aggs" in f.calls[0][3]


GOOD = {"investigation_id": "i1", "fingerprint": "fp1", "status": "HIGH_CONFIDENCE", "headline": "loss at capture since 10:00",
        "suspected_location": {"hop": "capture_app", "instances": ["s1"]},
        "evidence": [{"ref": "e1", "tool": "noc.py metrics", "query": "q", "observation": "drops x10"}],
        "candidates": [{"location": {"hop": "capture_app"}, "verdict": "supported", "evidence_for": ["e1"]}],
        "next_check": "check NIC ring buffer"}


def test_jira_comment_disabled_by_default(env, tmp_path, capsys):
    p = tmp_path / "inv.json"
    p.write_text(json.dumps(GOOD))
    code, res = run(capsys, "jira-comment", "CUST-1", "--file", str(p))
    assert code == 1 and res["error"]["code"] == "permission_denied"


def test_jira_comment_validated_posted_once(env, fake, tmp_path, capsys):
    env.section("jira")["allow_comment"] = "true"
    posted = []
    fake({"/comment": lambda m, u, p, b: posted.append(b["body"]) if m == "POST" else {"comments": [{"body": x} for x in posted]}})
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({**GOOD, "status": "CONFIRMED"}))
    code, res = run(capsys, "jira-comment", "CUST-1", "--file", str(bad))
    assert code == 1 and res["error"]["code"] == "validation_failed" and not posted

    good = tmp_path / "good.json"
    good.write_text(json.dumps(GOOD))
    assert run(capsys, "jira-comment", "CUST-1", "--file", str(good))[1]["data"]["posted"] is True
    assert run(capsys, "jira-comment", "CUST-1", "--file", str(good))[1]["data"]["posted"] is False
    assert len(posted) == 1 and "[noc-engineer:fp1:i1]" in posted[0]


def test_known_hops_enforced(env, fake, tmp_path, capsys):
    env.section("jira")["allow_comment"] = "true"
    env.config()["pipeline"] = {"hops": ["kafka_ingest"]}
    p = tmp_path / "inv.json"
    p.write_text(json.dumps(GOOD))
    code, res = run(capsys, "jira-comment", "CUST-1", "--file", str(p))
    assert code == 1 and "unknown hop" in res["error"]["message"]
