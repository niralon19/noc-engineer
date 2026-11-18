---
name: noc-tools
description: "Read-only NOC tools: Prometheus metrics, ECK logs, Grafana alerts, Jira. Load before querying any NOC data."
metadata:
  hermes:
    requires_toolsets: [terminal]
required_environment_variables:
  - {name: PROMETHEUS_URL, prompt: "Prometheus / Thanos Query URL"}
  - {name: PROMETHEUS_TOKEN, prompt: "Prometheus read-only token (optional)"}
  - {name: ECK_URL, prompt: "Elasticsearch URL"}
  - {name: ECK_USER, prompt: "Elasticsearch read-only user"}
  - {name: ECK_PASSWORD, prompt: "Elasticsearch password"}
  - {name: GRAFANA_URL, prompt: "Grafana URL"}
  - {name: GRAFANA_TOKEN, prompt: "Grafana viewer token"}
  - {name: JIRA_URL, prompt: "Jira URL"}
  - {name: JIRA_USER, prompt: "Jira user"}
  - {name: JIRA_TOKEN, prompt: "Jira token"}
  - {name: NOC_JIRA_ALLOW_COMMENT, prompt: "Allow Jira comments (true/false)"}
---

# NOC tools

Run with the terminal tool. Every command prints one JSON object: `ok`, `data`, `error{code,message}`.

```bash
python3 ${HERMES_SKILL_DIR}/scripts/noc.py health                              # what is configured
python3 ${HERMES_SKILL_DIR}/scripts/noc.py metrics '<promql>' --start -1h --end now
python3 ${HERMES_SKILL_DIR}/scripts/noc.py metrics-at '<promql>' --at -7d     # instant value at a time
python3 ${HERMES_SKILL_DIR}/scripts/noc.py logs '<query_string>' --start -1h --size 20 --group-by <field>
python3 ${HERMES_SKILL_DIR}/scripts/noc.py grafana-alerts
python3 ${HERMES_SKILL_DIR}/scripts/noc.py jira-get KEY
python3 ${HERMES_SKILL_DIR}/scripts/noc.py jira-search '<jql>' --limit 10
python3 ${HERMES_SKILL_DIR}/scripts/noc.py jira-comment KEY --file /tmp/inv.json
```

Times: ISO-8601, `now`, `-30m`, `-2h`, `-7d`.

## Rules
- Use only these commands for NOC data. Do not call the backends with curl.
- PromQL: always aggregate (`sum by (...)`, `topk`); use `rate()`/`increase()` on counters. Results are capped at 50 series.
- Compare with a baseline: the same query `--start -7d` / `metrics-at --at -7d`, and the window before the event.
- Logs: use `--group-by` with an error/signature field to find the FIRST new error after onset.
- `error.code = not_configured` means missing configuration, not "healthy". Say what is missing.
- `jira-comment` is the only write. It refuses unless enabled, validates the investigation JSON and skips duplicates.

## Investigation JSON (for jira-comment)
```json
{"investigation_id": "<unique>", "fingerprint": "<from the alert/ticket data>",
 "status": "CONFIRMED | HIGH_CONFIDENCE | INCONCLUSIVE | INVESTIGATION_INCOMPLETE",
 "headline": "<symptom> at <location> since <onset>",
 "suspected_location": {"hop": "", "rule_id": "", "component": "", "instances": []},
 "onset_time": "", "evidence": [{"ref": "e1", "tool": "noc.py metrics", "query": "", "observation": ""}],
 "candidates": [{"location": {"hop": ""}, "verdict": "confirmed|supported|ruled_out|unknown", "evidence_for": ["e1"]}],
 "ruled_out": {"<alternative>": "<why>"}, "next_check": "", "missing_data": [], "recommended_actions": []}
```
CONFIRMED needs a confirmed candidate citing evidence and `ruled_out`. Anything below CONFIRMED needs `next_check`.
