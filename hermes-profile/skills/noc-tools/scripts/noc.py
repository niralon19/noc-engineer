#!/usr/bin/env python3
"""noc: the agent's read-only tools for metrics, logs, Grafana and Jira. Prints one JSON object.

  noc.py health
  noc.py metrics "<promql>" [--start -1h] [--end now] [--step 60]
  noc.py metrics-at "<promql>" [--at -7d]
  noc.py logs "<query_string>" [--index I] [--start -1h] [--end now] [--size 20] [--group-by field]
  noc.py grafana-alerts
  noc.py jira-get KEY
  noc.py jira-search "<jql>" [--limit 10]
  noc.py jira-comment KEY --file investigation.json      (the ONLY write; gated, validated, deduplicated)

Output: {"ok": bool, "source": ..., "data": ..., "error": {"code", "message"}}.
error.code "not_configured" means missing configuration: say so and ask, never treat it as "healthy".
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import noclib as n  # noqa: E402
from investigation import render, validate  # noqa: E402

MAX_OUT = 20_000


def out(ok: bool, source: str, data=None, error=None, **extra) -> dict:
    res = {"ok": ok, "source": source, "data": data, "error": error, **extra}
    text = json.dumps(res, default=str)
    if len(text) > MAX_OUT:
        res["data"] = {"_truncated_preview": json.dumps(data, default=str)[: MAX_OUT // 2]}
        res["truncated"] = True
        res["note"] = "result too large: aggregate the query or narrow the window"
    return res


def cmd_health(a) -> dict:
    checks = {"prometheus": ("prometheus", "url"), "elasticsearch": ("elasticsearch", "url"),
              "grafana": ("grafana", "url"), "jira": ("jira", "url"), "jira_customer_jql": ("jira", "customer_jql")}
    status = {k: ("configured" if not n.is_tbd(n.section(s).get(f)) else "not_configured") for k, (s, f) in checks.items()}
    checks_cfg = (n.section("anomaly").get("checks") or [])
    status["anomaly_checks"] = f"{sum(1 for c in checks_cfg if not n.is_tbd(c.get('query')))}/{len(checks_cfg)} configured"
    status["jira_comment"] = "enabled" if n.section("jira").get("allow_comment") in (True, "true", "1") else "disabled"
    return out(True, "noc", status)


def _summ(series: list[dict], cap: int) -> list[dict]:
    res = []
    for s in series[:cap]:
        vals = [v for _, v in s["values"] if v is not None]
        res.append({"labels": s["labels"], "points": len(s["values"]),
                    "first": s["values"][0] if s["values"] else None, "last": s["values"][-1] if s["values"] else None,
                    "min": min(vals, default=None), "max": max(vals, default=None),
                    "values": s["values"][:: max(1, len(s["values"]) // 30)]})
    return res


def cmd_metrics(a) -> dict:
    s, e = n.window(a.start, a.end)
    series = n.prom_range(a.promql, s, e, a.step)
    cap = int(n.section("prometheus").get("max_series", 50))
    return out(True, "prometheus", {"query": a.promql, "series": _summ(series, cap)},
               time_range={"start": n.iso(s), "end": n.iso(e)}, truncated=len(series) > cap,
               note=f"{len(series)} series, showing {cap}: aggregate (sum by / topk)" if len(series) > cap else None)


def cmd_metrics_at(a) -> dict:
    at = n.parse_time(a.at, n.now())
    return out(True, "prometheus", {"query": a.promql, "at": n.iso(at), "result": n.prom_instant(a.promql, at)[:50]})


def cmd_logs(a) -> dict:
    es = n.section("elasticsearch")
    idx = a.index or es.get("default_index")
    if n.is_tbd(idx):
        raise n.NocError("not_configured", "elasticsearch.default_index is not configured (or pass --index)")
    s, e = n.window(a.start, a.end)
    size = max(0, min(a.size, int(es.get("max_hits", 50))))
    body = n.es_search(idx, a.query, s, e, size, a.group_by) or {}
    ts = es.get("timestamp_field", "@timestamp")
    hits = []
    for h in (body.get("hits") or {}).get("hits", []):
        src = h.get("_source") or {}
        hits.append({"ts": src.get(ts), "message": str(src.get("message") or src.get("log") or "")[:300],
                     "fields": {k: v for k, v in src.items() if k not in ("message", "log") and not isinstance(v, (dict, list))}})
    total = (body.get("hits") or {}).get("total")
    data = {"index": idx, "query": a.query, "total": total.get("value") if isinstance(total, dict) else total, "hits": hits}
    if a.group_by:
        data["groups"] = [{"value": b["key"], "count": b["doc_count"], "first_seen": (b.get("first_seen") or {}).get("value_as_string")}
                          for b in (body.get("aggregations") or {}).get("by", {}).get("buckets", [])]
    return out(True, "eck", data, time_range={"start": n.iso(s), "end": n.iso(e)})


def cmd_grafana_alerts(a) -> dict:
    alerts = [{"name": x.get("labels", {}).get("alertname"), "labels": x.get("labels"), "annotations": x.get("annotations"),
               "startsAt": x.get("startsAt"), "state": (x.get("status") or {}).get("state")} for x in n.grafana_alerts()]
    return out(True, "grafana", {"count": len(alerts), "alerts": alerts[:50]})


def cmd_jira_get(a) -> dict:
    b = n.jira_issue(a.key)
    f = b.get("fields", {})
    return out(True, "jira", {"key": b.get("key"), "summary": f.get("summary"), "status": (f.get("status") or {}).get("name"),
                              "priority": (f.get("priority") or {}).get("name"),
                              "assignee": (f.get("assignee") or {}).get("displayName"), "labels": f.get("labels"),
                              "created": f.get("created"), "updated": f.get("updated"),
                              "description": (f.get("description") or "")[:2000]})


def cmd_jira_search(a) -> dict:
    limit = max(1, min(a.limit, int(n.section("jira").get("max_results", 20))))
    b = n.jira_search(a.jql, limit)
    return out(True, "jira", {"total": b.get("total"), "issues": [
        {"key": i["key"], "summary": i["fields"].get("summary"), "status": (i["fields"].get("status") or {}).get("name"),
         "updated": i["fields"].get("updated"), "labels": i["fields"].get("labels")} for i in b.get("issues", [])]})


def cmd_jira_comment(a) -> dict:
    j = n.section("jira")
    if j.get("allow_comment") not in (True, "true", "1"):
        raise n.NocError("permission_denied", "Jira comments are disabled (jira.allow_comment=false). Return the result instead.")
    inv = json.loads(Path(a.file).read_text())
    hops = set(n.section("pipeline").get("hops") or []) - {"TBD"}
    errors = validate(inv, hops or None)
    if errors:
        raise n.NocError("validation_failed", "fix the investigation before publishing: " + "; ".join(errors))
    marker = f"[{j.get('comment_marker', 'noc-engineer')}:{inv['fingerprint']}:{inv['investigation_id']}]"
    if any(marker in (c.get("body") or "") for c in n.jira_comments(a.key)):
        return out(True, "jira", {"key": a.key, "posted": False, "reason": "already posted"})
    n.jira_add_comment(a.key, render(inv, marker))
    n.append_jsonl("audit.jsonl", {"at": n.iso(n.now()), "action": "jira_comment", "key": a.key,
                                   "investigation_id": inv["investigation_id"], "status": inv["status"]})
    return out(True, "jira", {"key": a.key, "posted": True, "marker": marker})


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="noc.py", description="NOC read-only tools")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("health").set_defaults(fn=cmd_health)
    p = sub.add_parser("metrics"); p.add_argument("promql"); p.add_argument("--start"); p.add_argument("--end")
    p.add_argument("--step", type=int); p.set_defaults(fn=cmd_metrics)
    p = sub.add_parser("metrics-at"); p.add_argument("promql"); p.add_argument("--at"); p.set_defaults(fn=cmd_metrics_at)
    p = sub.add_parser("logs"); p.add_argument("query"); p.add_argument("--index"); p.add_argument("--start")
    p.add_argument("--end"); p.add_argument("--size", type=int, default=20); p.add_argument("--group-by")
    p.set_defaults(fn=cmd_logs)
    sub.add_parser("grafana-alerts").set_defaults(fn=cmd_grafana_alerts)
    p = sub.add_parser("jira-get"); p.add_argument("key"); p.set_defaults(fn=cmd_jira_get)
    p = sub.add_parser("jira-search"); p.add_argument("jql"); p.add_argument("--limit", type=int, default=10)
    p.set_defaults(fn=cmd_jira_search)
    p = sub.add_parser("jira-comment"); p.add_argument("key"); p.add_argument("--file", required=True)
    p.set_defaults(fn=cmd_jira_comment)
    return ap


TIME_FLAGS = ("--start", "--end", "--at")


def _join_negative_times(argv: list[str]) -> list[str]:
    """Allow `--start -1h` (argparse would read -1h as a flag)."""
    res, i = [], 0
    while i < len(argv):
        if argv[i] in TIME_FLAGS and i + 1 < len(argv) and argv[i + 1].startswith("-"):
            res.append(f"{argv[i]}={argv[i + 1]}")
            i += 2
        else:
            res.append(argv[i])
            i += 1
    return res


def main(argv=None) -> int:
    a = parser().parse_args(_join_negative_times(list(sys.argv[1:] if argv is None else argv)))
    try:
        res = a.fn(a)
    except n.NocError as e:
        res = out(False, a.cmd, error={"code": e.code, "message": e.message})
    except Exception as e:  # noqa: BLE001
        res = out(False, a.cmd, error={"code": "internal_error", "message": f"{type(e).__name__}: {e}"[:300]})
    print(json.dumps({k: v for k, v in res.items() if v is not None}, default=str, ensure_ascii=False))
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
