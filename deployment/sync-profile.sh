#!/usr/bin/env bash
# Copy the version-controlled profile into the real Hermes profile. Copy, never symlink
# (a bare symlink can make Hermes silently use the default profile).
# config.yaml: seeded when missing; when present, managed keys are merged only with --apply-config (backup kept).
# VERIFY the profile path for your Docker image / host before first use.
set -euo pipefail
PROFILE="${PROFILE:-noc-engineer}"
APPLY_CONFIG=""
while [ $# -gt 0 ]; do case "$1" in --profile) PROFILE="$2"; shift 2;; --apply-config) APPLY_CONFIG="--apply"; shift;; *) shift;; esac; done
HERMES="${HERMES_BIN:-hermes}"
SRC="$(cd "$(dirname "$0")/../hermes-profile" && pwd)"
DEST="${HERMES_HOME:-$HOME/.hermes/profiles/$PROFILE}"

[ -d "$DEST" ] || "$HERMES" profile create "$PROFILE"   # VERIFY: `hermes profile --help`
mkdir -p "$DEST/skills" "$DEST/scripts"
cp "$SRC/SOUL.md" "$DEST/SOUL.md"
# Remove skills that THIS repo deployed before but no longer has (renamed/deleted),
# while keeping skills Hermes created itself. The manifest records what the repo owns.
MANIFEST="$DEST/.repo-managed-skills"
if [ -f "$MANIFEST" ]; then
  while IFS= read -r old; do
    [ -n "$old" ] && [ ! -d "$SRC/skills/$old" ] && rm -rf "$DEST/skills/$old" && echo "removed stale skill: $old"
  done < "$MANIFEST"
fi
cp -a "$SRC/skills/." "$DEST/skills/"
( cd "$SRC/skills" && ls -1d */ | sed 's#/$##' ) > "$MANIFEST"
cp -a "$SRC/scripts/." "$DEST/scripts/"
find "$DEST/scripts" -name "__pycache__" -prune -exec rm -rf {} +
echo "Synced SOUL.md, skills/, scripts/ -> $DEST"
# config.yaml: seed if missing; otherwise show (or with --apply-config, apply) a merge of the managed keys only.
python3 "$(dirname "$0")/merge_config.py" "$SRC/config.yaml" "$DEST/config.yaml" ${APPLY_CONFIG:-$( [ -f "$DEST/config.yaml" ] || echo --apply )}
echo "Next: fill model/MCP values in $DEST/config.yaml (or re-run with --apply-config), then: deployment/day0-check.sh --profile $PROFILE"
