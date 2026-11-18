#!/usr/bin/env python3
"""Cron script (daily 09:00) for the daily-summary skill. Prints a JSON digest of the last 24h of anomaly runs."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "noc-tools" / "scripts"))
import noclib as n  # noqa: E402


def digest(runs: list[dict], findings: list[dict]) -> dict:
    groups: dict = defaultdict(lambda: {"count": 0, "first": None, "last": None, "kinds": set(), "worst_ratio": None})
    for f in findings:
        g = groups[(f["check"], f["series"])]
        g["count"] += 1
        g["first"] = g["first"] or f["at"]
        g["last"] = f["at"]
        g["kinds"].add(f["kind"])
        r = f.get("ratio")
        if r is not None and (g["worst_ratio"] is None or abs(r - 1) > abs(g["worst_ratio"] - 1)):
            g["worst_ratio"] = r
    errors: dict = defaultdict(int)
    for r in runs:
        for e in r.get("errors", []):
            errors[e.split(":")[0]] += 1
    top = sorted(groups.items(), key=lambda kv: -kv[1]["count"])
    return {"period": "last 24h", "runs": len(runs), "runs_with_errors": sum(1 for r in runs if r.get("errors")),
            "findings_total": len(findings), "distinct_series": len(groups),
            "series": [{"check": c, "series": s, **{**g, "kinds": sorted(g["kinds"])}} for (c, s), g in top[:30]],
            "errors": dict(errors)}


def main() -> int:
    since = n.now() - timedelta(hours=24)
    print(json.dumps(digest(n.read_jsonl("anomaly_runs.jsonl", since), n.read_jsonl("anomalies.jsonl", since)),
                     ensure_ascii=False))
    for f in ("anomaly_runs.jsonl", "anomalies.jsonl"):
        n.prune_jsonl(f, keep_days=7)
    return 0


if __name__ == "__main__":
    sys.exit(main())
