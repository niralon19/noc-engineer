#!/usr/bin/env bash
# Create/refresh the NOC cron jobs in Hermes via `hermes cron create`. Idempotent: remove by name, then create.
#
# Usage:
#   deployment/cron/install-cron.sh [--profile noc-engineer] [--deliver slack] [--dry-run] [--all] [job ...]
#   no job names  -> installs agent jobs + only those script jobs whose script is implemented
#   --all         -> installs every job, even if its script still raises NotImplementedError
#   job names     -> installs only those (e.g. `oncall-report`)
#   --list-jobs   -> prints the known job names and exits
#
# Run INSIDE the Hermes pod/host, after the gateway is running and the profile was synced.
# First run `hermes cron create --help` and confirm the flags used below exist in your version.
set -euo pipefail

PROFILE="${PROFILE:-noc-engineer}"
HERMES_BIN="${HERMES_BIN:-hermes}"
DELIVER="${NOC_DELIVER:-slack}"      # slack -> SLACK_HOME_CHANNEL; VERIFY syntax with --help
DRY_RUN=0; ALL=0; SELECTED=()
while [ $# -gt 0 ]; do
  case "$1" in
    --profile) PROFILE="$2"; shift 2;;
    --deliver) DELIVER="$2"; shift 2;;
    --dry-run) DRY_RUN=1; shift;;
    --all) ALL=1; shift;;
    --list-jobs) echo "data-quality-scan enrichment-audit anomaly-baseline jira-polling-backup housekeeping proactive-review oncall-report"; exit 0;;
    -h|--help) sed -n '2,12p' "$0"; exit 0;;
    -*) echo "unknown option $1" >&2; exit 2;;
    *) SELECTED+=("$1"); shift;;
  esac
done

HOME_DIR="${HERMES_HOME:-$HOME/.hermes/profiles/$PROFILE}"
SCRIPTS="$HOME_DIR/scripts"
HERE="$(cd "$(dirname "$0")" && pwd)"

hermes() {  # always target the profile
  if [ "$DRY_RUN" = 1 ]; then printf 'DRY-RUN: hermes -p %q' "$PROFILE"; printf ' %q' "$@"; echo; return 0; fi
  "$HERMES_BIN" -p "$PROFILE" "$@"
}
wanted() {  # is job $1 selected?
  [ ${#SELECTED[@]} -eq 0 ] && return 0
  local s; for s in "${SELECTED[@]}"; do [ "$s" = "$1" ] && return 0; done; return 1
}
implemented() {  # script exists and is not a stub
  local f="$SCRIPTS/$1"
  [ -f "$f" ] || f="$HERE/../../hermes-profile/scripts/$1"
  [ -f "$f" ] && ! grep -q "raise NotImplementedError" "$f"
}
skip() { echo "SKIP $1: $2"; }

job_script() { # name schedule script
  wanted "$1" || return 0
  if [ "$ALL" = 0 ] && ! implemented "$3"; then skip "$1" "script $3 not implemented yet (use --all or name the job to force)"; [ ${#SELECTED[@]} -eq 0 ] && return 0; fi
  hermes cron remove "$1" >/dev/null 2>&1 || true
  hermes cron create "$2" --name "$1" --no-agent --script "$SCRIPTS/$3" --deliver "$DELIVER"
  echo "OK   $1"
}
job_agent() { # name schedule prompt_file script(or -) skills...
  local name="$1" sched="$2" prompt="$3" script="$4"; shift 4
  wanted "$name" || return 0
  if [ "$script" != "-" ] && [ "$ALL" = 0 ] && ! implemented "$script"; then
    skip "$name" "input script $script not implemented yet"; [ ${#SELECTED[@]} -eq 0 ] && return 0
  fi
  local extra=(); local s; for s in "$@"; do extra+=(--skill "$s"); done
  if [ "$script" != "-" ]; then extra+=(--script "$SCRIPTS/$script"); fi   # script stdout becomes agent context
  hermes cron remove "$name" >/dev/null 2>&1 || true
  hermes cron create "$sched" "$(cat "$HERE/prompts/$prompt")" --name "$name" "${extra[@]}" --deliver "$DELIVER"
  echo "OK   $name"
}

echo "profile=$PROFILE deliver=$DELIVER scripts=$SCRIPTS"
echo "NOTE: schedules are meant as Asia/Jerusalem. Container time now: $(date '+%H:%M %Z'). If it is UTC, confirm how Hermes interprets cron times."

job_script data-quality-scan    "*/15 * * * *" data_quality_scan.py
job_script enrichment-audit     "*/30 * * * *" enrichment_audit.py
job_script anomaly-baseline     "0 * * * *"    anomaly_baseline.py
job_script jira-polling-backup  "*/2 * * * *"  jira_poll.py
job_script housekeeping         "0 2 * * *"    housekeeping.py
job_agent  proactive-review     "*/15 * * * *" proactive-review.md anomaly_scan.py proactive-review change-correlation pipeline-walk observability-queries
job_agent  oncall-report        "0 7 * * *"    oncall-report.md    -               oncall-report jira-operations observability-queries

hermes cron list
echo "Test a job now: hermes -p $PROFILE cron run <name>"
