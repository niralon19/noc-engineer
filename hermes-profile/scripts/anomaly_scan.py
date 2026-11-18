#!/usr/bin/env python3
"""Cron script (every 5 min) for the anomaly-scan skill. Deterministic: no LLM here.

For every check in noc.yaml `anomaly.checks`: run the PromQL now and at the same time last week, compare per series.
A series is a finding when now/last_week is outside [min_ratio, max_ratio] (or it disappeared / appeared).
Prints NEW findings as JSON (one object). Prints NOTHING when there is nothing new, so the agent answers [SILENT].
Every run is recorded in data/noc/anomaly_runs.jsonl and every finding in data/noc/anomalies.jsonl (daily summary).
"""
from __future__ import annotations

import json
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "noc-tools" / "scripts"))
import noclib as n  # noqa: E402


def evaluate(check: dict, current: list[dict], baseline: list[dict]) -> list[dict]:
    """Compare two instant vectors series by series. Pure function (tested)."""
    lo, hi = float(check.get("min_ratio", 0.5)), float(check.get("max_ratio", 2.0))
    floor = float(check.get("min_baseline", 0))
    base = {n.series_key(s["labels"]): s["value"] for s in baseline}
    cur = {n.series_key(s["labels"]): s["value"] for s in current}
    findings = []
    for key in sorted(set(base) | set(cur)):
        b, c = base.get(key), cur.get(key)
        if b is None and c is None:
            continue
        if b is not None and b < floor and (c is None or c < floor):
            continue                                   # too small to matter
        if c is None:
            kind, ratio = "disappeared", 0.0
        elif b is None or b == 0:
            if c is not None and c >= max(floor, 1e-9) and check.get("alert_on_new", False):
                kind, ratio = "appeared", None
            else:
                continue
        else:
            ratio = c / b
            if lo <= ratio <= hi:
                continue
            kind = "drop" if ratio < lo else "spike"
        findings.append({"check": check["name"], "series": key, "kind": kind, "now": c, "last_week": b,
                         "ratio": None if ratio is None else round(ratio, 3)})
    return findings


def main() -> int:
    cfg = n.section("anomaly")
    checks = [c for c in cfg.get("checks") or [] if not n.is_tbd(c.get("query"))]
    run = {"at": n.iso(n.now()), "checks": len(checks), "errors": [], "findings": 0, "new": 0}
    if not checks:
        run["errors"].append("no anomaly checks configured (noc.yaml anomaly.checks)")
        n.append_jsonl("anomaly_runs.jsonl", run)
        return 0
    cooldown = timedelta(minutes=int(cfg.get("cooldown_minutes", 60)))
    baseline_offset = n.parse_time(cfg.get("baseline", "-7d"), n.now()) - n.now()
    state = n.load_state("anomaly_state.json")
    new = []
    t = n.now()
    for check in checks:
        try:
            cur = n.prom_instant(check["query"], t)
            base = n.prom_instant(check["query"], t + baseline_offset)
        except n.NocError as e:
            run["errors"].append(f"{check['name']}: {e.code}: {e.message}"[:300])
            continue
        for f in evaluate(check, cur, base):
            run["findings"] += 1
            f["at"] = n.iso(t)
            f["fingerprint"] = n.fingerprint("anomaly", f["check"], f["series"], f["kind"])
            n.append_jsonl("anomalies.jsonl", f)
            last = state.get(f["fingerprint"])
            if last and n.parse_time(last, t) > t - cooldown:
                continue
            state[f["fingerprint"]] = n.iso(t)
            new.append(f)
    run["new"] = len(new)
    state = {k: v for k, v in state.items() if n.parse_time(v, t) > t - timedelta(days=2)}
    n.save_state("anomaly_state.json", state)
    n.append_jsonl("anomaly_runs.jsonl", run)
    if new:
        print(json.dumps({"window": "now vs same time last week", "new_findings": new[:20],
                          "more": max(0, len(new) - 20), "errors": run["errors"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
