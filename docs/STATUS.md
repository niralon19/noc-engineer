# STATUS: where the project is now

> Every agent/developer: read this after CLAUDE.md, and UPDATE it at the end of your work (tick boxes, move items, add the date).
> Last update: 2026-11-15

## Done (in this repo)
- [x] Hermes profile: SOUL.md, 18 skills (6 route, 3 domain, 9 supporting), `config.yaml` (Kimi K3 custom provider, API server :8642, MCP url, tools.include)
- [x] Investigation contract: `Investigation.validate()` (hop, evidence, ruled_out, next_check), data-based fingerprint
- [x] noc-mcp: 18 config-driven tools (pipeline, rules, changes, servers, kafka, monitoring, history, Jira + gated comment, health); stdio + HTTP; offline tests
- [x] Cron: `install-cron.sh` (profile-aware, skips stub scripts), prompts for oncall-report and proactive-review
- [x] Deployment: k8s Hermes (gateway, PVC, Service/Route, profile init container) + noc-mcp pod + NetworkPolicy + Argo Application; `day0-check.sh`
- [x] Web app chat example (`examples/web-app/`), Hebrew docs (guide, what-is-Hermes)
- [x] Ask-Nir mechanism: `docs/OPEN-QUESTIONS.md` (60 questions) + `docs/skeleton-files.yaml` (every skeleton file -> blocking questions, tagged `REQUIRES FROM NIR`) + `scripts/open_items.py` scanner + mandatory protocol in CLAUDE.md; runtime: tools/health name the question ID, SOUL tells Hermes to ask instead of guessing
- [x] E2E fixes 2026-11-15: skill frontmatter is strict YAML (13 skills would not have loaded); cron upgrade is create-then-retire with versioned names (a failed create keeps the old job); noc-mcp HTTP requires a bearer token (fail-closed) + /healthz; every tool call is audited (reads, errors, denied writes); config.yaml seeded on first deploy and merged safely (`merge_config.py`, backup, placeholders never overwrite real values)
- [x] Tests passing (`python3 -m pytest -q tests`)

## Waiting for Nir at work (blocks real investigations)
Full, current list with question IDs: `python3 scripts/open_items.py` / `docs/OPEN-QUESTIONS.md`. Summary:
- [ ] Make the repo private / move to the org git
- [ ] `noc-mcp/config/backends.yaml`: URLs, secrets via env, server/Kafka PromQL templates, rules API paths, maintenance source
- [ ] `noc-mcp/config/pipeline.yaml`: real hops, `in_query`/`out_query` per hop, hermeticity/coupling KPI queries, then `verified: true`
- [ ] `rule-paths.yaml` (if the rules system has no rule -> path API)
- [ ] Hermes: image, HERMES_HOME path, Kimi endpoint + model id, Secrets, Slack app tokens
- [ ] Verify Hermes CLI flags on the installed version (`cron create`, `gateway run`, `mcp test`)
- [ ] "Environment knowledge" sections in the skills

## Next (in order)
1. Day 0: `day0-check.sh` READY; 3 resolved alerts via `hermes chat`, compare with CrewAI
2. `evals/`: 20–30 resolved alerts with known root cause + runner that scores hop/rule correctness, time, tool calls  <- buildable now
3. Grafana -> Hermes -> `validate()` -> Slack bridge (`event-ingestion/grafana_webhook.py`) for shadow mode  <- buildable now
4. Hermes self-monitoring (latency, tool errors, tokens per investigation)
5. Shadow mode 2–4 weeks, then switch Jira ownership from CrewAI
6. Routes: customer-ticket, config-change, web app; then anomaly engine + proactive-review; then the other cron scripts

## Not implemented yet (stubs on purpose)
- noc-mcp network / enrichment / data-quality / platform tools (contract names only)
- `anomaly-engine/`, `event-ingestion/`, `reporting/`, cron scripts in `hermes-profile/scripts/`
- History in org Postgres (JSONL for now)

## Success criteria (shadow mode exit)
- Correct hop for >= 80% of the evaluation set; correct rule/instance for >= 70%
- No CONFIRMED conclusion that is wrong; every conclusion cites evidence and passes `validate()`
- Median investigation < 5 min; tool errors handled as missing_data, never as "healthy"
- Better than CrewAI on the same alerts at locating the problem (the reason this project exists)
