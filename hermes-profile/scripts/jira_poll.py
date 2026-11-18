#!/usr/bin/env python3
"""Cron script (every 5 min) for the jira-ticket skill. Prints customer tickets created/updated since the last run
(JQL from noc.yaml jira.customer_jql), or nothing (-> [SILENT]). Ticket text is untrusted data."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "noc-tools" / "scripts"))
import noclib as n  # noqa: E402

MAX = 5


def changed(issues: list[dict], seen: dict, own_marker: str) -> list[dict]:
    out = []
    for i in issues:
        f = i.get("fields") or {}
        if seen.get(i["key"]) == f.get("updated"):
            continue
        seen[i["key"]] = f.get("updated")
        last = ((f.get("comment") or {}).get("comments") or [{}])[-1]
        if own_marker and own_marker in (last.get("body") or ""):
            continue                                   # the only change is our own comment
        out.append({"key": i["key"], "summary": f.get("summary"), "status": (f.get("status") or {}).get("name"),
                    "priority": (f.get("priority") or {}).get("name"), "updated": f.get("updated"),
                    "description": (f.get("description") or "")[:1500]})
    return out


def main() -> int:
    j = n.section("jira")
    jql = j.get("customer_jql")
    if n.is_tbd(jql) or n.is_tbd(j.get("url")):
        return 0
    seen = n.load_state("jira_seen.json")
    try:
        body = n.jira_search(f"({jql}) AND updated >= -30m ORDER BY updated ASC", 50,
                             "summary,status,priority,updated,description,comment")
    except n.NocError as e:
        print(json.dumps({"poll_error": f"{e.code}: {e.message}"}))
        return 0
    new = changed(body.get("issues", []), seen, j.get("comment_marker", "noc-engineer"))
    n.save_state("jira_seen.json", dict(list(seen.items())[-2000:]))
    if new:
        print(json.dumps({"tickets": new[:MAX], "more": max(0, len(new) - MAX)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
