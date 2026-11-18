# Instructions for coding agents

- This repo is a Hermes profile distribution: the root is the profile (`distribution.yaml`, `SOUL.md`, `config.yaml`, `skills/`, `scripts/`, `cron/`). Keep it flat. No MCP, no extra layers.
- Talk to Nir in Hebrew, bottom line first. Code, comments and SKILL/SOUL files in English.
- Never invent environment facts (metric names, PromQL, hosts, JQL, channels). Leave `TBD` and list it under "To fill" in README.
- Deterministic work (polling, comparisons, dedup) is Python in `scripts/`. The agent explains and locates.
- Read-only. The only write is `noc.py jira-comment`.
- SOUL.md and SKILL.md go into the model prompt: no developer notes in them.
- Secrets never in git. Tests: `python3 -m pytest -q tests` (offline, fake HTTP).
