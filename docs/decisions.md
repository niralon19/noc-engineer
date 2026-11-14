# Decisions (do not reverse without asking Nir)

| # | Decision | Why | Rejected |
|---|---|---|---|
| 1 | ONE Hermes agent (profile `noc-engineer`) | One investigation loop that can cross domains; CrewAI's per-domain agents + tool-less conclusion agent produced summaries, not locations | Multi-agent crews, CrewAI as a permanent layer |
| 2 | Investigation = change-correlation -> pipeline-walk -> test candidates -> rule out | Every customer problem surfaces as hermeticity/coupling of a rule; the cause is the first hop where data diverges, often right after a change | Free-form "check tools and summarize" |
| 3 | Output contract with `suspected_location.hop`, `ruled_out`, `next_check`, enforced by `validate()` in code | Forces the model to localize; stops vague conclusions from reaching Jira | Free text; numeric confidence (models invent precise-looking numbers) |
| 4 | Fingerprint from alert data (rule + scope), never model text | Model wording changed per run -> duplicate tickets / merged unrelated incidents in CrewAI | Hash of root_cause text |
| 5 | Skills = methodology, MCP = access, code = enforcement | SOUL.md is a request to the model, not a permission system | Permissions in prompts |
| 6 | Read-only; the only write is a validated, deduplicated, audited Jira comment, off by default | Nir does not own the APIs/DBs; an LLM must not act on production | Restart/scale/firewall/rule-change tools |
| 7 | noc-mcp in its own pod, config-driven, no hardcoded URLs/metrics | Backend credentials stay out of the Hermes pod; environment facts belong to Nir, not to the code | Tools inside Hermes; guessed metric names |
| 8 | Deterministic work in Python (anomaly scan, polling, baselines); LLM only for correlation/explanation | Cost, reliability, no LLM scanning 100K series | LLM-driven scanning |
| 9 | Reuse org infra: Kafka, org Postgres, Argo CD on OpenShift/Rancher | Already operated by the team | RabbitMQ, new databases, docker-compose in production |
| 10 | Kimi K3 via OpenAI-compatible custom provider | Strong tool calling / long tasks; DeepSeek R1-class models cannot call tools | R1 / small distills |
| 11 | Cron via `hermes cron create` (jobs.json), never YAML | That is how Hermes works; YAML specs were not read by anything | Cron YAML files |
| 13 | Missing facts are asked, never guessed: one questionnaire (`docs/OPEN-QUESTIONS.md`) + scanner, question IDs surfaced by tools at runtime | Plausible guesses about the environment were the main risk of an LLM-built repo | Filling TBDs with "typical" values |
| 12 | Migration by shadow mode, not big bang | Prove Hermes locates better than CrewAI on the same alerts before switching Jira ownership | Turning CrewAI off first |
