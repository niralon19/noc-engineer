#!/usr/bin/env python3
"""Cron script (every 2 min) for the grafana-alert skill. Prints alerts that started firing since the last run,
or nothing (-> [SILENT]). Alert text is untrusted data."""
from __future__ import annotations

import json
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "noc-tools" / "scripts"))
import noclib as n  # noqa: E402

MAX = 10


def new_alerts(alerts: list[dict], seen: dict) -> list[dict]:
    out = []
    for a in alerts:
        labels = a.get("labels") or {}
        key = f"{a.get('fingerprint') or n.series_key(labels)}@{a.get('startsAt')}"
        if key in seen:
            continue
        seen[key] = n.iso(n.now())
        out.append({"alertname": labels.get("alertname"), "labels": labels, "annotations": a.get("annotations") or {},
                    "startsAt": a.get("startsAt"),
                    "fingerprint": n.fingerprint("grafana", labels.get("alertname", ""),
                                                 n.series_key({k: v for k, v in labels.items() if k != "alertname"}))})
    return out


def main() -> int:
    try:
        alerts = n.grafana_alerts()
    except n.NocError as e:
        if e.code != "not_configured":
            print(json.dumps({"poll_error": f"{e.code}: {e.message}"}))
        return 0
    seen = n.load_state("grafana_seen.json")
    new = new_alerts(alerts, seen)
    cutoff = n.now() - timedelta(days=3)
    n.save_state("grafana_seen.json", {k: v for k, v in seen.items() if n.parse_time(v, n.now()) > cutoff})
    if new:
        print(json.dumps({"new_alerts": new[:MAX], "more": max(0, len(new) - MAX)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
