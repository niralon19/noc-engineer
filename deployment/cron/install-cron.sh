#!/usr/bin/env bash
# REQUIRES FROM NIR: B4, B5, D2 (docs/OPEN-QUESTIONS.md). Before implementing/filling run `python3 scripts/open_items.py --file deployment/cron/install-cron.sh`; if BLOCKED, ask Nir. Never invent.
# Create/refresh the NOC cron jobs in Hermes via `hermes cron create`.
# Safe upgrade: every job is named <job>--<hash of its definition>. The new version is CREATED FIRST; only if that
# succeeds are older versions of the same job removed. Unchanged jobs are left alone. A failed create keeps the old job.
#
# Usage:
#   deployment/cron/install-cron.sh [--profile noc-engineer] [--deliver slack] [--dry-run] [--all] [job ...]
#   no job names  -> installs agent jobs + only those script jobs whose script is implemented
#   --all         -> installs every job, even if its script still raises NotImplementedError
#   job names     -> installs only those (e.g. `oncall-report`)
#   --list-jobs   -> prints the known job names and exits
# Job names in Hermes look like `oncall-report--1a2b3c4d`; `hermes -p <profile> cron list` shows them.
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

EXISTING=""
refresh_existing() {  # names of jobs currently in Hermes (VERIFY: parsing assumes names appear verbatim in `cron list`)
  if [ "$DRY_RUN" = 1 ]; then EXISTING=""; return 0; fi
  EXISTING="$("$HERMES_BIN" -p "$PROFILE" cron list 2>/dev/null | grep -oE '[a-z0-9-]+--[0-9a-f]{8}' | sort -u || true)"
}
defhash() { printf '%s' "$*" | sha256sum | cut -c1-8; }

# install_job <job> <create args...>: create <job>--<hash> first, then remove older versions of <job>.
install_job() {
  local job="$1"; shift
  local versioned="$job--$(defhash "$@")"
  if printf '%s\n' "$EXISTING" | grep -qx "$versioned"; then echo "SAME $job ($versioned unchanged)"; return 0; fi
  if ! hermes cron create "$@" --name "$versioned"; then
    echo "FAIL $job: create failed; previous version left running" >&2; FAILED=$((FAILED+1)); return 0
  fi
  local old
  for old in $(printf '%s\n' "$EXISTING" | grep -E "^$job--[0-9a-f]{8}$" | grep -vx "$versioned" || true); do
    hermes cron remove "$old" >/dev/null 2>&1 && echo "     retired $old" || echo "WARN could not remove $old (remove it manually)" >&2
  done
  if [ "$DRY_RUN" = 1 ]; then echo "     (dry-run: would retire older versions of $job after a successful create)"; fi
  echo "OK   $job -> $versioned"
}
FAILED=0

job_script() { # name schedule script
  wanted "$1" || return 0
  if [ "$ALL" = 0 ] && ! implemented "$3"; then skip "$1" "script $3 not implemented yet (use --all or name the job to force)"; [ ${#SELECTED[@]} -eq 0 ] && return 0; fi
  install_job "$1" "$2" --no-agent --script "$SCRIPTS/$3" --deliver "$DELIVER"
}
job_agent() { # name schedule prompt_file script(or -) skills...
  local name="$1" sched="$2" prompt="$3" script="$4"; shift 4
  wanted "$name" || return 0
  if [ "$script" != "-" ] && [ "$ALL" = 0 ] && ! implemented "$script"; then
    skip "$name" "input script $script not implemented yet"; [ ${#SELECTED[@]} -eq 0 ] && return 0
  fi
  local extra=(); local s; for s in "$@"; do extra+=(--skill "$s"); done
  if [ "$script" != "-" ]; then extra+=(--script "$SCRIPTS/$script"); fi   # script stdout becomes agent context
  install_job "$name" "$sched" "$(cat "$HERE/prompts/$prompt")" "${extra[@]}" --deliver "$DELIVER"
}

echo "profile=$PROFILE deliver=$DELIVER scripts=$SCRIPTS"
refresh_existing
echo "NOTE: schedules are meant as Asia/Jerusalem. Container time now: $(date '+%H:%M %Z'). If it is UTC, confirm how Hermes interprets cron times."

job_script data-quality-scan    "*/15 * * * *" data_quality_scan.py
job_script enrichment-audit     "*/30 * * * *" enrichment_audit.py
job_script anomaly-baseline     "0 * * * *"    anomaly_baseline.py
job_script jira-polling-backup  "*/2 * * * *"  jira_poll.py
job_script housekeeping         "0 2 * * *"    housekeeping.py
job_agent  proactive-review     "*/15 * * * *" proactive-review.md anomaly_scan.py proactive-review change-correlation pipeline-walk observability-queries
job_agent  oncall-report        "0 7 * * *"    oncall-report.md    -               oncall-report jira-operations observability-queries

hermes cron list
echo "Test a job now: hermes -p $PROFILE cron run <job--hash from the list>"
[ "$FAILED" -eq 0 ] || { echo "$FAILED job(s) failed to install; old versions kept" >&2; exit 1; }
