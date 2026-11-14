# noc-engineer — Hermes NOC Engineer

Single primary Hermes agent (profile `noc-engineer`) for on-prem NOC investigation, early anomaly detection, Jira coordination and a daily report. Runs in Docker, read-only by default.

## Architecture
- **Hermes = brain**, **Skills = methodology**, **MCP = tool access**. One agent, seven skills, one MCP layer. No multi-agent, no CrewAI as a permanent layer.
- The Python anomaly engine does deterministic/statistical detection outside the LLM path and emits normalized events. Hermes does correlation, explanation and RCA.
- Jira enters via webhook plus bounded polling. Web chat is primary; Slack is for notifications.
- PostgreSQL/RabbitMQ are **optional** (`--profile optional`) and not needed to start.

## Repository map
| Path | Purpose |
|---|---|
| `hermes-profile/` | Version-controlled mirror of `HERMES_HOME`: `SOUL.md`, `config.yaml`, `skills/<name>/SKILL.md` |
| `noc-mcp/` | MCP server code, tool contracts and allowlist (`config/`), result schemas |
| `anomaly-engine/` | Deterministic detection (`anomaly_engine.py`, rules, baselines) |
| `event-ingestion/` | Grafana/Jira webhooks and polling (reuse the existing Grafana→Jira agent) |
| `reporting/` | Daily NOC report |
| `workflows/` | Declarative specs: incident lifecycle, Jira intake, event schema |
| `deployment/` | Compose, `.env.example`, cron job specs, example settings, optional Postgres schema |
| `docs/` | Architecture, tools contract, investigation flow, security, runbooks |
| `tests/` | Architecture contracts and anomaly-engine tests (`pytest tests`) |

## Deploying the profile
`hermes-profile/` is the source of truth; sync its contents into the real `HERMES_HOME` (usually `~/.hermes/profiles/noc-engineer/`) with a script. Do not use a bare symlink (Hermes may silently fall back to the default profile). Change settings with `hermes config set`, not by hand-editing `config.yaml` on the live host. Verify the path in your Docker image.

## Cron
Job specs live in `deployment/cron/` (data-quality `*/15`, enrichment `*/30`, baseline `0 *`, Jira polling `*/2`, daily report `0 7`, housekeeping `0 2`; timezone `Asia/Jerusalem`). They are specs, not enabled schedules. Register each in exactly one scheduler. Deterministic checks run as plain Python, not through the LLM.

## Start order
0. **Day 0:** test the local LLM on a synthetic multi-step tool-calling investigation. If it fails, nothing else matters.
1. Profile + `SOUL.md` + 3 core skills (observability, investigation, ITSM) + MCP with ~8 read-only tools; one real investigation.
2. Evaluation set: 20–30 resolved historical alerts with known root cause.
3. Webhook/polling intake, dedup, history.
4. Proactive monitoring (anomaly engine), data quality, enrichment.
5. Cron, daily report, SLA tracking.
6. Hardening: permissions, failure tests, idempotency, Hermes-vs-CrewAI comparison.

## Optional services
```bash
cp deployment/.env.example deployment/.env   # replace all passwords
docker compose -f deployment/docker-compose.yml --profile optional up -d
```

## Status
Scaffold with explicit contracts, not production-ready. MCP tool names/schemas, Jira workflow, Slack, Hermes version, Prometheus limits and secrets management must come from the environment owner. Keep this repository **private**; never commit internal addresses, topology, logs or credentials.
