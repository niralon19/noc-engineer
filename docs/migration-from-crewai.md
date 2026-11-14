# Migration from CrewAI (`crew-network`) to Hermes

> LLM/DEVELOPER: the current CrewAI code lives in Nir's WORK repository, not on GitHub (the public `niralon19/crew-network` is an old January 2026 snapshot with stub tools). Do the mapping inside the work repo; do NOT copy work code, hostnames, metric names or credentials into this repository. Ask Nir when a mapping is unclear.

## Why migrate
CrewAI works end to end, but conclusions do not say where the problem is: they are a collection of tool outputs. Causes found in the old design:
1. Domain agents ran tools once and reported; no hypothesis/rule-out loop.
2. The conclusion agent had no tools: it summarized summaries and could not verify.
3. Routing sent each alert to ONE domain, so cross-domain causes were missed.
4. The output schema had no location, onset, or ruled-out fields, so nothing forced the model to localize.
5. Dedup fingerprint hashed the model-written root_cause: reworded causes created duplicate tickets; different "unknown" incidents merged.

Hermes fixes this only together with: one agent in an investigation loop (`alert-investigation` protocol), a contract that requires `suspected_location`/`ruled_out`/`next_check` (`Investigation.validate()`), and a data-based fingerprint.

## Mapping
| CrewAI component | Hermes / this repo | Action |
|---|---|---|
| `router.py` (deterministic by alert type) | `event-ingestion/grafana_webhook.py` | Keep logic; it now picks the domain skill hint and forwards to Hermes instead of a crew |
| `models.Alert` | `workflows/event-schema.json` | Keep fields; add entity + rule for fingerprint |
| Traffic / Coupling / COATR agents (role, goal, backstory) | skills `traffic-hermetic`, `coupling`, `coatr` | Move the domain know-how (what to check, in which order, known causes) into the skill. Drop role-play text |
| Domain tools (`check_traffic`, `check_ratios`, `analyze_logs`, `run_sql`, real versions) | tools in the existing FastMCP server | Expose as MCP tools, read-only, structured output with query + time range. Add names to `tools.include` |
| `tasks.py` prompts | `alert-investigation` skill | Replaced by the protocol; no "run tools and summarize" prompt |
| Conclusion agent | removed | The same agent that investigates concludes; contract enforced by `Investigation.validate()` |
| `policy.should_open_jira` | MCP server Jira tool policy (code) | Enforce in code, not prompt. Map the old rule onto status/priority |
| `jira/client.py`, `formatter.py`, `publisher.py` | MCP Jira tools (`search_issues`, `add_investigation_comment`, `create_followup_task`) | Reuse client; formatter renders the new contract (headline, location, ruled out, next check) |
| `memory/fingerprint.py` | `noc-mcp/schemas/fingerprint.py` | Fixed: fingerprint from alert data only |
| `memory/dedup.py`, `store.py`, `ttl.py` (SQLite) | ingestion dedup + `search_investigations` backend | Keep SQLite at first; pgvector knowledge base later if search needs it |
| `main.handle_alert` | Hermes session triggered by ingestion | Verify how a webhook starts a Hermes session (gateway webhook / API) on Nir's version |
| pgvector Incident KB (planned) | backend of `search_investigations` | After shadow mode, if similarity search proves useful |

## Rollout
1. **Day 0:** Hermes + Kimi K3 + existing FastMCP; one real alert manually (`hermes chat`), check tool calls and that the output passes `validate()`.
2. **Side by side on history:** pick 20–30 resolved alerts with a known root cause, including tickets where CrewAI's conclusion was vague. Score: located correctly? time to conclusion? false locations?
3. **Shadow mode (2–4 weeks):** ingestion sends each live alert to both; CrewAI keeps creating Jira, Hermes posts only to a Slack channel. Compare daily.
4. **Switch:** Hermes owns Jira comments/creation; CrewAI off. Keep its code until one month without regressions.
5. Add routes: customer tickets, user questions, proactive review, on-call report.

## Open questions for Nir
- Exact list of current tools and which are already FastMCP.
- How the alert reaches CrewAI today (webhook format, router location).
- Jira project/issue types used for AI tickets; who may create vs comment.
- Slack channel for shadow mode and for the on-call report.
- Kimi K3 endpoint and serving stack; is reasoning_effort configurable through Hermes provider settings?
