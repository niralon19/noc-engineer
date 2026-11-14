# What Hermes reads vs what our code reads

Verified against the Hermes docs (links below). "Ask Nir" items are not verified for his version.

| Repo path | Deployed to | Who reads it | Notes |
|---|---|---|---|
| `hermes-profile/SOUL.md` | `$HERMES_HOME/SOUL.md` | **Hermes** (slot #1 of the system prompt) | Prompt text: no developer notes |
| `hermes-profile/skills/<name>/SKILL.md` | `$HERMES_HOME/skills/` | **Hermes** (loaded on demand; attachable to cron via `--skill`) | Frontmatter `name`, `description` |
| `hermes-profile/config.yaml` | merged into `$HERMES_HOME/config.yaml` | **Hermes** | `model` (provider custom, base_url, default), `gateway.api_server` (8642), `mcp_servers`. |
| `hermes-profile/scripts/*.py` | `$HERMES_HOME/scripts/` | **Hermes cron** (no-agent mode) | stdout delivered verbatim, no LLM |
| `deployment/cron/install-cron.sh` | run once | **Hermes CLI** (`hermes cron create`) | Jobs are stored by Hermes in `cron/jobs.json`; never hand-edit |
| `deployment/cron/prompts/*.md` | read by install script | Hermes (as job prompt) | Self-contained: each run is a fresh session |
| `deployment/.env.example` | `.env` | Hermes (secrets) + our code | Secrets only |
| `noc-mcp/` | MCP server | Hermes connects to it as an MCP server | Tools appear as `mcp_noc_mcp_<tool>` |
| `noc-mcp/config/tool-contracts.yaml`, `anomaly-engine/config/*`, `deployment/config/*`, `workflows/*.yaml`, `workflows/event-schema.json` | - | **our Python code only** | Not Hermes files |
| `deployment/k8s/`, `deployment/argocd/` | cluster | Argo CD | Hermes Deployment + PVC + profile ConfigMap (skeleton, TBD values) |
| `noc-mcp/config/pipeline.yaml` | - | our code | Pipeline hops and KPI definitions |
| `deployment/docker-compose.yml` | - | Docker | Local dev Postgres only |

## Entry points
- Slack gateway (Socket Mode): `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`, `SLACK_ALLOWED_USERS`, `SLACK_HOME_CHANNEL` in `.env`.
- API server (OpenAI-compatible, port 8642): `/v1/chat/completions`, `/health`; `API_SERVER_KEY` required; `X-Hermes-Session-Id`, `X-Hermes-Session-Key`, `Idempotency-Key` headers. Web app integration: `examples/web-app/`.
- CLI: `hermes -p noc-engineer chat`.

## Not yet verified (ask Nir / test)
- Exact `hermes cron create` flags for no-agent scripts and delivery targets on his version.
- Timezone used for cron expressions.
- How an external webhook (Grafana/Jira intake) triggers a Hermes session (gateway webhook vs API).
- The profile path inside his Docker image.

## Sources
- Profiles / layout: https://mer.vin/2026/05/hermes-agent-dot-hermes-folder-layout-soul-secrets-memory-skills/ , https://blakecrosley.com/guides/hermes
- Cron: https://hermes-agent.nousresearch.com/docs/user-guide/features/cron , https://hermes-agent.nousresearch.com/docs/developer-guide/cron-internals
- MCP: https://hermes-agent.nousresearch.com/docs/reference/mcp-config-reference , https://hermes-agent.nousresearch.com/docs/guides/use-mcp-with-hermes
- API server: https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server
- Slack: https://hermes-agent.nousresearch.com/docs/user-guide/messaging/slack
