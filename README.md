# noc-engineer — Hermes NOC Engineer

Single Hermes agent (profile `noc-engineer`) that replaces the CrewAI pipeline (`crew-network`). Model: Kimi K3 via an OpenAI-compatible endpoint. Read-only by default.

## Routes
| Route | Entry | Skills |
|---|---|---|
| New alert | Grafana webhook (existing router + dedup forwards to Hermes) | `alert-investigation` + domain |
| Customer/team Jira ticket | Jira webhook + polling | `customer-ticket` + domain |
| Team question | Web chat / Slack | `user-question` |
| Early detection | cron `proactive-review` (anomaly engine script -> agent) | `proactive-review` |
| On-call morning report | cron `oncall-report` 07:00 | `oncall-report` |

Domain skills: `traffic-hermetic`, `coupling`, `coatr`. Supporting skills: `observability-queries`, `network-engineering`, `openshift-operations`, `jira-operations`. Every investigation must locate the problem (`suspected_location`, `onset_time`, `ruled_out`, `next_check`); see `noc-mcp/schemas/investigation.py`.

## Architecture
- **Hermes = brain**, **Skills = methodology**, **MCP = tool access**. One agent, seven skills, one MCP layer. No multi-agent, no CrewAI as a permanent layer.
- The Python anomaly engine does deterministic/statistical detection outside the LLM path and emits normalized events. Hermes does correlation, explanation and RCA.
- Jira enters via webhook plus bounded polling. Web chat is primary; Slack is for notifications.
- PostgreSQL/RabbitMQ are **optional** (`--profile optional`) and not needed to start.

## Repository map
| Path | Purpose |
|---|---|
| `hermes-profile/` | Version-controlled mirror of `HERMES_HOME`: `SOUL.md`, `config.yaml` fragment, `skills/<name>/SKILL.md`, `scripts/` (no-agent cron) |
| `noc-mcp/` | MCP server code, tool contract (`config/`), result schemas |
| `anomaly-engine/` | Deterministic detection (`anomaly_engine.py`, rules, baselines) |
| `event-ingestion/` | Grafana/Jira webhooks and polling (reuse the existing Grafana→Jira agent) |
| `reporting/` | Daily NOC report |
| `workflows/` | Design specs for our Python code (NOT read by Hermes) + event schema |
| `deployment/` | `sync-profile.sh`, `cron/install-cron.sh` + prompts, `.env.example`, compose, optional Postgres schema |
| `docs/` | Architecture, tools contract, investigation flow, security, runbooks |
| `tests/` | Architecture contracts and anomaly-engine tests (`pytest tests`) |

## Hermes-native vs ours
Hermes reads only: `SOUL.md`, `skills/`, `config.yaml` (MCP block), `scripts/` and cron jobs created through its CLI. Everything else in the repo is our own code or design spec. Full table: `docs/hermes-mapping.md`.

## Deploying the profile
```bash
deployment/sync-profile.sh          # copies SOUL.md, skills/, scripts/ (never a symlink)
# merge mcp_servers from hermes-profile/config.yaml, then:
hermes config check && hermes mcp test noc_mcp
deployment/cron/install-cron.sh     # creates the 6 jobs via `hermes cron create`
```
Change live settings with `hermes config set`; do not overwrite the live `config.yaml`.

## Cron
7 jobs: 5 deterministic no-agent scripts, `proactive-review` (every 15 min) and `oncall-report` (07:00). Details: `deployment/cron/README.md`.

## Start order
0. Connect Kimi K3 + the existing FastMCP server to Hermes; one real alert end to end.
1. `alert-investigation` + one domain skill; compare with what CrewAI wrote in Jira for the same alert.
2. Shadow mode on 20–30 resolved alerts: Hermes writes only to a Slack channel/log, CrewAI keeps owning Jira.
3. Switch ownership; add `customer-ticket`, `user-question`.
4. `proactive-review` + `oncall-report`.
5. Hardening (permissions, failure tests, idempotency). See `docs/migration-from-crewai.md`.

## Optional services
```bash
cp deployment/.env.example deployment/.env   # replace all passwords
docker compose -f deployment/docker-compose.yml --profile optional up -d
```

## Status
Scaffold with explicit contracts, not production-ready. MCP tool names/schemas, Jira workflow, Slack, Hermes version, Prometheus limits and secrets management must come from the environment owner. Keep this repository **private**; never commit internal addresses, topology, logs or credentials.
