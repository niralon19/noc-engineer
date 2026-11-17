# noc-engineer — Hermes NOC Engineer

Single Hermes agent (profile `noc-engineer`) that replaces the CrewAI pipeline (`crew-network`). Model: Kimi K3 via an OpenAI-compatible endpoint. Read-only by default.

## How it thinks
Every customer problem surfaces as a **rule's hermeticity or coupling** degrading, but the cause can be any hop of a long path (servers -> NIC -> capture app -> Kafka -> K8s processing -> internal enrichment -> rule matching -> Postgres/ECK -> output), a change (rule/config, Argo, rollout), maintenance, loss or load. Each investigation: **what changed -> walk the path to the first diverging hop -> test candidates there -> rule out**. The hops are defined in `noc-mcp/config/pipeline.yaml` / `docs/pipeline-map.md` (filled at work).

## Routes
| Route | Entry | Skills |
|---|---|---|
| New alert | Grafana webhook (existing router + dedup forwards to Hermes) | `alert-investigation` |
| Customer/team Jira ticket | Jira webhook + polling | `customer-ticket` |
| Rule/config change request | Jira / chat | `config-change` (review before, verify after) |
| Team question | Web chat / Slack | `user-question` |
| Early detection | cron `proactive-review` (rule-centric anomaly script -> agent) | `proactive-review` |
| On-call morning report | cron `oncall-report` 07:00 | `oncall-report` |

Domain skills: `traffic-hermetic` (hermeticity), `coupling`, `coatr` (app/DB).
Supporting skills: `change-correlation`, `pipeline-walk`, `capture-servers`, `kafka-pipeline`, `platform-operations` (Rancher, OpenShift, Argo, Postgres, ECK), `network-engineering`, `enrichment-quality`, `observability-queries`, `jira-operations`.
Every investigation must locate the problem (`suspected_location.hop`, `rule_id`, `onset_time`, `ruled_out`, `next_check`) and pass `Investigation.validate()`.

## Architecture
- **Hermes = brain**, **Skills = methodology**, **MCP = tool access**. One agent, one MCP layer (Nir's FastMCP server). No multi-agent, no CrewAI as a permanent layer.
- The Python anomaly engine is rule-centric (hermeticity/coupling per rule vs baseline, hop divergence) and deterministic. Hermes correlates and explains.
- Uses existing infrastructure: Kafka for events, org Postgres for investigation history. No RabbitMQ.
- Production deploy: OpenShift/Rancher via Argo CD (`deployment/k8s`, `deployment/argocd`). `docker-compose.yml` is local dev only.
- Entry points: Slack (Socket Mode), the web app via the API server (`examples/web-app/`), CLI. What Hermes is and how users reach it (Hebrew): `docs/מה-זה-הרמס.md`.
- Hebrew guide to every folder and file: `docs/מדריך-הפרויקט.md`.

## Repository map
| Path | Purpose |
|---|---|
| `hermes-profile/` | Version-controlled mirror of `HERMES_HOME`: `SOUL.md`, `config.yaml` fragment, `skills/<name>/SKILL.md`, `scripts/` (no-agent cron) |
| `noc-mcp/` | MCP server with 18 implemented, config-driven investigation tools (`noc-mcp/README.md`), pipeline map, investigation schema, fingerprint, write gate |
| `anomaly-engine/` | Deterministic detection (`anomaly_engine.py`, rules, baselines) |
| `event-ingestion/` | Grafana/Jira webhooks and polling (reuse the existing Grafana→Jira agent) |
| `reporting/` | Daily NOC report |
| `workflows/` | Design specs for our Python code (NOT read by Hermes) + event schema |
| `deployment/` | `k8s/` + `argocd/` (production), `sync-profile.sh`, `cron/install-cron.sh` + prompts, `.env.example`, local compose |
| `docs/` | Architecture, tools contract, investigation flow, security, runbooks |
| `tests/` | Architecture contracts and anomaly-engine tests (`pytest tests`) |

## Hermes-native vs ours
Hermes reads only: `SOUL.md`, `skills/`, `config.yaml` (MCP block), `scripts/` and cron jobs created through its CLI. Everything else in the repo is our own code or design spec. Full table: `docs/hermes-mapping.md`.

## Getting started (at work)
```bash
# production: Argo CD syncs deployment/k8s (init container unpacks the profile into the PVC)
python3 deployment/k8s/gen_kustomization.py           # after adding/removing skills or scripts
# inside the pod (or a host with Hermes; dev alternative: deployment/sync-profile.sh --profile noc-engineer)
deployment/day0-check.sh --profile noc-engineer       # CLI, profile, config, model, MCP, API, Slack, cron
deployment/cron/install-cron.sh oncall-report         # first cron job
hermes -p noc-engineer cron run oncall-report         # test it now
```
Change live settings with `hermes config set`; do not overwrite the live `config.yaml`.

## Cron
7 jobs declared in `deployment/cron/jobs.yaml` and applied automatically on every pod start (init container `reconcile-cron`); manual: `install-cron.sh`. Details: `deployment/cron/README.md`.

## Start order
0. Connect Kimi K3 + the existing FastMCP server to Hermes; one real alert end to end.
1. `alert-investigation` + one domain skill; compare with what CrewAI wrote in Jira for the same alert.
2. Shadow mode on 20–30 resolved alerts: Hermes writes only to a Slack channel/log, CrewAI keeps owning Jira.
3. Switch ownership; add `customer-ticket`, `user-question`.
4. `proactive-review` + `oncall-report`.
5. Hardening (permissions, failure tests, idempotency). See `docs/migration-from-crewai.md`.

## Local dev
```bash
cp deployment/.env.example deployment/.env
docker compose -f deployment/docker-compose.yml --profile optional up -d   # local Postgres only
```

## Status
See `docs/STATUS.md` (done / waiting for environment data / next / success criteria) and `docs/decisions.md`. Keep this repository **private**; never commit internal addresses, topology, logs or credentials.
