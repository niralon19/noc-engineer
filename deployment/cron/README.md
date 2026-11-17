# Scheduled jobs (Hermes-native, declared in git)

Hermes stores jobs it creates with `hermes cron create` in `$HERMES_HOME/cron/jobs.json` (never hand-edit).
We declare the desired jobs in **`jobs.yaml`** and a reconciler applies them:

- **Automatically:** init container `reconcile-cron` in `deployment/k8s/hermes.yaml` runs on every pod start.
  Edit `jobs.yaml` / a prompt -> commit -> Argo sync -> ConfigMap hash changes -> pod restarts -> jobs updated.
- **Manually:** `deployment/cron/install-cron.sh [--profile P] [--dry-run] [--all] [job ...]`.

Reconciler rules (`reconcile_cron.py`):
- Job name in Hermes = `<name>--<hash of its definition>`. Unchanged -> `SAME` (nothing touched).
- Changed -> new version **created first**, old versions retired only after success. Failed create keeps the old job.
- Removed from `jobs.yaml` -> pruned (only jobs the reconciler created, tracked in `.repo-managed-cron`).
- Script still a stub (`raise NotImplementedError`) -> `SKIP`; it is installed automatically once implemented.
- In the init container it runs with `--soft`: cron problems never block the gateway; the result is in
  `$HERMES_HOME/.cron-reconcile-status.json` and reported by `deployment/day0-check.sh`.

| Job | Schedule | Mode | Runs |
|---|---|---|---|
| data-quality-scan | `*/15 * * * *` | script (no LLM) | `data_quality_scan.py` |
| enrichment-audit | `*/30 * * * *` | script | `enrichment_audit.py` |
| anomaly-baseline | `5 * * * *` | script | `anomaly_baseline.py` (4-week median -> Postgres) |
| jira-polling-backup | `*/2 * * * *` | script | `jira_poll.py` |
| housekeeping | `0 2 * * *` | script | `housekeeping.py` |
| proactive-review | `*/5 * * * *` | agent + `anomaly_scan.py` output | answers `[SILENT]` when there are no findings |
| oncall-report | `0 7 * * *` | agent | morning report to the on-call channel |

UNVERIFIED (B4/B5): exact `hermes cron` flags, whether the CLI works before the gateway starts (init container), cron timezone.
If the CLI needs a running gateway, move the same command to a `postStart` hook or a sidecar; the reconciler does not change.
