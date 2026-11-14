# Scheduled jobs (Hermes-native)

Hermes does **not** read cron YAML. Jobs are created with `hermes cron create` (or `/cron add`, or by asking Hermes) and stored by Hermes in `$HERMES_HOME/cron/jobs.json`. Do not hand-edit that JSON. Docs: https://hermes-agent.nousresearch.com/docs/user-guide/features/cron

`install-cron.sh` recreates the six jobs idempotently (remove by name, then create).

| Job | Schedule | Mode | What runs |
|---|---|---|---|
| data-quality-scan | `*/15 * * * *` | no-agent script | `hermes-profile/scripts/data_quality_scan.py` |
| enrichment-audit | `*/30 * * * *` | no-agent script | `scripts/enrichment_audit.py` |
| anomaly-baseline | `0 * * * *` | no-agent script | `scripts/anomaly_baseline.py` |
| jira-polling-backup | `*/2 * * * *` | no-agent script | `scripts/jira_poll.py` |
| noc-daily-report | `0 7 * * *` | agent (skills attached) | `prompts/noc-daily-report.md` |
| housekeeping | `0 2 * * *` | no-agent script | `scripts/housekeeping.py` |

Rules from the Hermes docs:
- No-agent mode runs a script and delivers its stdout verbatim; no LLM, no tokens. Use it for every deterministic check.
- Agent jobs start a fresh session each run: the prompt must be self-contained; keep procedures in skills (`--skill`, repeatable).
- The gateway daemon must be running for jobs to fire.
- Test one job with `hermes cron run <name>` before relying on the schedule.
- Run each job in exactly one scheduler. Verify the timezone Hermes uses for cron expressions (ask Nir / `hermes cron --help`); Asia/Jerusalem is the intent.
