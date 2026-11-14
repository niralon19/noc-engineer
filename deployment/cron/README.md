# Scheduled jobs (Hermes-native)

Hermes does **not** read cron YAML. Jobs are created with `hermes cron create` (or `/cron add`, or by asking Hermes) and stored by Hermes in `$HERMES_HOME/cron/jobs.json`. Do not hand-edit that JSON. Docs: https://hermes-agent.nousresearch.com/docs/user-guide/features/cron

`install-cron.sh` creates/refreshes jobs idempotently (remove by name, then create), always with `-p <profile>`.

```bash
deployment/cron/install-cron.sh --dry-run                 # see what would run
deployment/cron/install-cron.sh                           # agent jobs + script jobs whose script is implemented
deployment/cron/install-cron.sh oncall-report             # one job
deployment/cron/install-cron.sh --all                     # everything, even stub scripts
hermes -p noc-engineer cron run oncall-report             # run now to test
hermes -p noc-engineer cron list | remove <name>
```
Script jobs are skipped automatically while their script still raises NotImplementedError, so nothing fails every few minutes.

| Job | Schedule | Mode | What runs |
|---|---|---|---|
| data-quality-scan | `*/15 * * * *` | no-agent script | `hermes-profile/scripts/data_quality_scan.py` |
| enrichment-audit | `*/30 * * * *` | no-agent script | `scripts/enrichment_audit.py` |
| anomaly-baseline | `0 * * * *` | no-agent script | `scripts/anomaly_baseline.py` |
| jira-polling-backup | `*/2 * * * *` | no-agent script | `scripts/jira_poll.py` |
| housekeeping | `0 2 * * *` | no-agent script | `scripts/housekeeping.py` |
| proactive-review | `*/15 * * * *` | agent + `--script anomaly_scan.py` | `prompts/proactive-review.md`; answers `[SILENT]` when there are no findings |
| oncall-report | `0 7 * * *` | agent | `prompts/oncall-report.md`, skill `oncall-report`, delivered to the on-call channel |

Rules from the Hermes docs:
- No-agent mode runs a script and delivers its stdout verbatim; no LLM, no tokens. Use it for every deterministic check.
- Agent jobs start a fresh session each run: the prompt must be self-contained; keep procedures in skills (`--skill`, repeatable).
- The gateway daemon must be running for jobs to fire.
- Test one job with `hermes cron run <name>` before relying on the schedule.
- Run each job in exactly one scheduler. Verify the timezone Hermes uses for cron expressions (ask Nir / `hermes cron --help`); Asia/Jerusalem is the intent.
