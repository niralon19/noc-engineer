#!/usr/bin/env bash
# REQUIRES FROM NIR: B4, B5, D2 (docs/OPEN-QUESTIONS.md). Before implementing/filling run `python3 scripts/open_items.py --file deployment/cron/install-cron.sh`; if BLOCKED, ask Nir. Never invent.
# Manual entry point for the cron reconciler. The jobs are declared in deployment/cron/jobs.yaml.
# In Kubernetes this runs automatically on every pod start (init container `reconcile-cron`).
#
# Usage: deployment/cron/install-cron.sh [--profile noc-engineer] [--dry-run] [--all] [--soft] [job ...]
#   no job names -> reconcile all jobs (skip stub scripts, prune jobs removed from jobs.yaml)
#   job names    -> only those jobs (forces stubs too); --list-jobs prints the declared names
set -euo pipefail
exec python3 "$(cd "$(dirname "$0")" && pwd)/reconcile_cron.py" "$@"
