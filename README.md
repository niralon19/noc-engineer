# noc-engineer

A Hermes Agent [profile distribution](https://hermes-agent.nousresearch.com/docs/user-guide/profile-distributions): the repo root is the profile.

| Job | Trigger | Skill |
|---|---|---|
| Anomalies (metric now vs same time last week) -> team channel | `cron/anomaly-scan.json`, every 5 min | `anomaly-scan` |
| Daily anomaly summary -> team channel | `cron/daily-summary.json`, 09:00 | `daily-summary` |
| Questions from the team / customers | Slack message | `customer-question` |
| New Grafana alerts -> where the problem is | `cron/grafana-alerts.json`, every 2 min | `grafana-alert` |
| Customer Jira tickets -> comment with the location | `cron/jira-tickets.json`, every 5 min | `jira-ticket` |

Shared skills: `noc-tools` (read-only CLI for Prometheus, ECK, Grafana, Jira; settings in `assets/noc.yaml`) and `noc-environment` (data path + how to locate a problem).
`scripts/` are the cron scripts: deterministic, their stdout is the agent's input, empty output = `[SILENT]` (no message).

```
distribution.yaml  SOUL.md  config.yaml
skills/<name>/SKILL.md
scripts/           cron scripts
cron/*.json        cron jobs
deploy/            Dockerfile + start.sh + k8s.yaml
tests/
```

## Install
```bash
hermes profile install github.com/niralon19/noc-engineer --alias
# fill ~/.hermes/profiles/noc-engineer/.env with the vars it lists, then schedule cron (same as cron/*.json):
noc-engineer cron create "*/5 * * * *" "Follow the anomaly-scan skill on the script output above. If it is empty, answer exactly [SILENT]." --name anomaly-scan --script anomaly_scan.py --skill anomaly-scan --skill noc-tools --skill noc-environment --deliver slack
noc-engineer cron create "0 9 * * *" "Follow the daily-summary skill on the digest above and write the 09:00 message for the team." --name daily-summary --script anomaly_digest.py --skill daily-summary --skill noc-tools --deliver slack
noc-engineer cron create "*/2 * * * *" "Follow the grafana-alert skill on the new alerts above. If there are none, answer exactly [SILENT]." --name grafana-alerts --script grafana_poll.py --skill grafana-alert --skill noc-tools --skill noc-environment --deliver slack
noc-engineer cron create "*/5 * * * *" "Follow the jira-ticket skill on the tickets above. If there are none, answer exactly [SILENT]." --name jira-tickets --script jira_poll.py --skill jira-ticket --skill noc-tools --skill noc-environment --deliver slack
noc-engineer gateway run
```
Kubernetes: build `deploy/Dockerfile`, create Secret `hermes-noc-env`, apply `deploy/k8s.yaml`. The pod syncs the profile and schedules the cron jobs on start.

## To fill
- `config.yaml`: Kimi K3 endpoint and model id
- `skills/noc-tools/assets/noc.yaml`: anomaly PromQL per check, ECK index, customer JQL, pipeline hop ids
- `skills/noc-environment/SKILL.md`: hops, metric per hop, known failure patterns
- `deploy/k8s.yaml`: image and namespace

## Safety
Read-only. The only write is a validated, deduplicated Jira comment, off unless `NOC_JIRA_ALLOW_COMMENT=true`.
The agent has a shell, so give it read-only tokens and a Jira user that can only comment.

Tests: `python3 -m pytest -q tests`
