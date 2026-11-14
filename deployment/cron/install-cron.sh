#!/usr/bin/env bash
# Recreate the NOC cron jobs in Hermes. Idempotent (remove by name, then create).
# VERIFY flags against your Hermes version first: `hermes cron create --help`.
# Run as the user that owns the Hermes profile; set HERMES_HOME/profile as needed (e.g. `noc-engineer cron ...` wrapper).
set -euo pipefail
HERMES="${HERMES_BIN:-hermes}"
SCRIPTS="${HERMES_HOME:-$HOME/.hermes}/scripts"
DELIVER="${NOC_DELIVER:-local}"          # local | slack:<channel> | ... (see Hermes --deliver docs)
HERE="$(cd "$(dirname "$0")" && pwd)"

job_script() { # name schedule script
  "$HERMES" cron remove "$1" 2>/dev/null || true
  "$HERMES" cron create "$2" --name "$1" --no-agent --script "$SCRIPTS/$3" --deliver "$DELIVER"
}
job_agent() { # name schedule prompt_file skills...
  local name="$1" sched="$2" prompt="$3"; shift 3
  local skill_args=(); for s in "$@"; do skill_args+=(--skill "$s"); done
  "$HERMES" cron remove "$name" 2>/dev/null || true
  "$HERMES" cron create "$sched" "$(cat "$HERE/prompts/$prompt")" --name "$name" "${skill_args[@]}" --deliver "$DELIVER"
}

job_script data-quality-scan    "*/15 * * * *" data_quality_scan.py
job_script enrichment-audit     "*/30 * * * *" enrichment_audit.py
job_script anomaly-baseline     "0 * * * *"    anomaly_baseline.py
job_script jira-polling-backup  "*/2 * * * *"  jira_poll.py
job_script housekeeping         "0 2 * * *"    housekeeping.py
job_agent  noc-daily-report     "0 7 * * *"    noc-daily-report.md sre-observability incident-investigation itsm-coordination

"$HERMES" cron list
