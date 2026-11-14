#!/usr/bin/env bash
# Recreate the NOC cron jobs in Hermes. Idempotent (remove by name, then create).
# VERIFY flags against your Hermes version first: `hermes cron create --help`.
# Run as the user that owns the Hermes profile; set HERMES_HOME/profile as needed (e.g. `noc-engineer cron ...` wrapper).
set -euo pipefail
HERMES="${HERMES_BIN:-hermes}"
SCRIPTS="${HERMES_HOME:-$HOME/.hermes}/scripts"
DELIVER="${NOC_DELIVER:-local}"          # local | slack:<channel> | ... (see Hermes --deliver docs); set to the on-call/team channel
HERE="$(cd "$(dirname "$0")" && pwd)"

job_script() { # name schedule script
  "$HERMES" cron remove "$1" 2>/dev/null || true
  "$HERMES" cron create "$2" --name "$1" --no-agent --script "$SCRIPTS/$3" --deliver "$DELIVER"
}
job_agent() { # name schedule prompt_file script(or -) skills...
  local name="$1" sched="$2" prompt="$3" script="$4"; shift 4
  local extra=(); for s in "$@"; do extra+=(--skill "$s"); done
  [ "$script" != "-" ] && extra+=(--script "$SCRIPTS/$script")   # script stdout is given to the agent as context
  "$HERMES" cron remove "$name" 2>/dev/null || true
  "$HERMES" cron create "$sched" "$(cat "$HERE/prompts/$prompt")" --name "$name" "${extra[@]}" --deliver "$DELIVER"
}

job_script data-quality-scan    "*/15 * * * *" data_quality_scan.py
job_script enrichment-audit     "*/30 * * * *" enrichment_audit.py
job_script anomaly-baseline     "0 * * * *"    anomaly_baseline.py
job_script jira-polling-backup  "*/2 * * * *"  jira_poll.py
job_script housekeeping         "0 2 * * *"    housekeeping.py
job_agent  proactive-review     "*/15 * * * *" proactive-review.md anomaly_scan.py proactive-review alert-investigation traffic-hermetic coupling coatr
job_agent  oncall-report        "0 7 * * *"    oncall-report.md    -               oncall-report

"$HERMES" cron list
