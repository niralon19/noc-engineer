# Security

> **REQUIRES FROM NIR: P1, P2, A2, H3 (docs/OPEN-QUESTIONS.md). Before implementing/filling run `python3 scripts/open_items.py --file docs/security.md`; if BLOCKED, ask Nir. Never invent.**

Read-only by default. Blocked: restart, scale, block IP, firewall changes. Jira writes limited to comment/create (+ status per policy) with audit.
SOUL.md is not a permission mechanism: enforce permissions in `noc-mcp/security/`.

> LLM/DEVELOPER: expand with: per-system service accounts, secrets handling (.env / approved secret manager, never in skills or logs), rate limits, timeouts, result-size caps, prompt-injection handling for Jira/logs/alert annotations, audit format, test vs production separation. Keep the repo private.
