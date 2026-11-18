# Instructions for coding agents

- This is a plain Hermes profile. Read `README.md` first. Keep it flat: SOUL.md, skills, scripts, cron, deploy. No MCP, no extra layers.
- Talk to Nir in Hebrew, bottom line first. Code, comments and SKILL/SOUL files in English.
- Never invent environment facts (metric names, PromQL, hosts, JQL, channels, Hermes flags). Leave `TBD` and add a row to `OPEN-QUESTIONS.md`.
- Deterministic work (polling, comparisons, dedup) is Python in `hermes-profile/scripts`. The agent explains and locates.
- Read-only. The only write is `noc.py jira-comment`.
- SOUL.md and SKILL.md go into the model prompt: no developer notes in them.
- Secrets never in git. Tests: `python3 -m pytest -q tests` (offline, fake HTTP).
