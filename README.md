# noc-engineer

A Hermes Agent profile for the NOC. One agent, five jobs, all plain Hermes: skills + cron + Slack gateway.

| Job | Trigger | Skill |
|---|---|---|
| Anomalies (metric now vs same time last week) -> team channel | cron every 5 min, `anomaly_scan.py` | `anomaly-scan` |
| Daily anomaly summary -> team channel | cron 09:00, `anomaly_digest.py` | `daily-summary` |
| Questions from the team / customers | Slack message | `customer-question` |
| New Grafana alerts -> where is the problem | cron every 2 min, `grafana_poll.py` | `grafana-alert` |
| Customer Jira tickets -> comment with the location | cron every 5 min, `jira_poll.py` | `jira-ticket` |

Shared: `noc-tools` (read-only CLI for Prometheus, ECK, Grafana, Jira) and `noc-environment` (data path + method).

```
hermes-profile/           -> copied into $HERMES_HOME
  SOUL.md  config.yaml  noc.yaml  .env.example
  skills/<name>/SKILL.md  (noc-tools/scripts/ = the tools)
  scripts/                cron scripts: deterministic, stdout is the agent's input, empty = [SILENT]
cron/jobs.yaml            the 4 cron jobs; reconcile_cron.py applies them with `hermes cron create`
deploy/                   Dockerfile (Hermes image + profile), start.sh, k8s.yaml, argocd.yaml
tests/
```

## Run locally
```bash
export HERMES_HOME=~/.hermes/profiles/noc-engineer
mkdir -p $HERMES_HOME && cp -r hermes-profile/* $HERMES_HOME/ && cp hermes-profile/.env.example $HERMES_HOME/.env
# fill .env and noc.yaml, then:
python3 $HERMES_HOME/skills/noc-tools/scripts/noc.py health
python3 cron/reconcile_cron.py --dry-run
hermes gateway run
```

## Deploy
`docker build -f deploy/Dockerfile --build-arg HERMES_IMAGE=<hermes image> -t <registry>/noc-engineer .`, create Secret `hermes-noc-env`, apply `deploy/argocd.yaml`.

## Safety
Read-only. The only write is a validated, deduplicated Jira comment, off unless `NOC_JIRA_ALLOW_COMMENT=true`.
The agent has a shell, so the real guard is the credentials: give it read-only tokens (Prometheus, ECK, Grafana viewer) and a Jira user that can only comment.

Missing facts: [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md). Tests: `python3 -m pytest -q tests`.
