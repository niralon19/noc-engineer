#!/usr/bin/env bash
# Day 0: verify Hermes is ready before anything else. Read-only; runs every check and prints PASS/FAIL/WARN.
# Usage: deployment/day0-check.sh [--profile noc-engineer] [--api http://localhost:8642]
# Needs API_SERVER_KEY in the environment for the API checks.
set -uo pipefail
PROFILE="noc-engineer"; API="${HERMES_API:-http://localhost:8642}"; HERMES_BIN="${HERMES_BIN:-hermes}"
while [ $# -gt 0 ]; do case "$1" in --profile) PROFILE="$2"; shift 2;; --api) API="$2"; shift 2;; *) shift;; esac; done
H() { "$HERMES_BIN" -p "$PROFILE" "$@"; }
HOME_DIR="${HERMES_HOME:-$HOME/.hermes/profiles/$PROFILE}"
fails=0
check() { # label, command...
  local label="$1"; shift
  if out=$("$@" 2>&1); then echo "PASS  $label"; else echo "FAIL  $label"; echo "$out" | tail -5 | sed 's/^/      /'; fails=$((fails+1)); fi
}
warn() { echo "WARN  $1"; }

echo "== Hermes $( "$HERMES_BIN" --version 2>/dev/null || echo '?') | profile=$PROFILE | home=$HOME_DIR"
check "hermes CLI available"            "$HERMES_BIN" --version
check "profile exists (SOUL.md)"        test -f "$HOME_DIR/SOUL.md"
check "skills deployed (>=18)"          bash -c "[ \$(ls -1d '$HOME_DIR'/skills/*/ 2>/dev/null | wc -l) -ge 18 ]"
check "config valid"                    H config check
check "model configured (custom)"       bash -c "grep -q 'provider: custom' '$HOME_DIR/config.yaml' && ! grep -q REPLACE '$HOME_DIR/config.yaml'"
check "MCP server reachable + tools"    H mcp test noc_mcp
check "API /health"                     curl -fsS --max-time 5 "$API/health"
if [ -n "${API_SERVER_KEY:-}" ]; then
  check "API auth + model listed"       bash -c "curl -fsS --max-time 10 -H 'Authorization: Bearer $API_SERVER_KEY' '$API/v1/models' | grep -q ."
  check "model answers (1 short call)"  bash -c "curl -fsS --max-time 120 -H 'Authorization: Bearer $API_SERVER_KEY' -H 'Content-Type: application/json' \
      -d '{\"model\":\"$PROFILE\",\"messages\":[{\"role\":\"user\",\"content\":\"Reply with the single word OK. Do not call tools.\"}]}' \
      '$API/v1/chat/completions' | grep -qi ok"
else
  warn "API_SERVER_KEY not set: skipped authenticated API checks"
fi
for v in SLACK_BOT_TOKEN SLACK_APP_TOKEN SLACK_ALLOWED_USERS SLACK_HOME_CHANNEL; do
  [ -n "${!v:-}" ] || grep -q "^$v=." "$HOME_DIR/.env" 2>/dev/null || warn "$v not set (Slack will not work / cron output has no channel)"
done
check "cron list"                       H cron list
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[ -f "$REPO_ROOT/scripts/open_items.py" ] && echo "== $(python3 "$REPO_ROOT/scripts/open_items.py" --brief 2>/dev/null) (see docs/OPEN-QUESTIONS.md)"
echo "== container time: $(date '+%Y-%m-%d %H:%M %Z') (cron schedules assume Asia/Jerusalem)"

echo
if [ $fails -eq 0 ]; then
  echo "READY. Next: a real investigation:"
  echo "  hermes -p $PROFILE chat   ->  'Investigate alert <paste a real resolved alert>. Follow alert-investigation.'"
  echo "  then: deployment/cron/install-cron.sh --profile $PROFILE oncall-report && hermes -p $PROFILE cron run oncall-report"
else
  echo "$fails check(s) failed. Fix them before installing cron or opening it to the team."
fi
exit $fails
