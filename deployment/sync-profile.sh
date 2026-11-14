#!/usr/bin/env bash
# Copy the version-controlled profile into the real Hermes profile. Copy, never symlink
# (a bare symlink can make Hermes silently use the default profile).
# config.yaml is NOT overwritten: merge the mcp_servers block yourself (see hermes-profile/config.yaml).
# VERIFY the profile path for your Docker image / host before first use.
set -euo pipefail
PROFILE="${PROFILE:-noc-engineer}"
HERMES="${HERMES_BIN:-hermes}"
SRC="$(cd "$(dirname "$0")/../hermes-profile" && pwd)"
DEST="${HERMES_HOME:-$HOME/.hermes/profiles/$PROFILE}"

[ -d "$DEST" ] || "$HERMES" profile create "$PROFILE"
mkdir -p "$DEST/skills" "$DEST/scripts"
cp "$SRC/SOUL.md" "$DEST/SOUL.md"
cp -a "$SRC/skills/." "$DEST/skills/"     # no --delete: keeps skills Hermes created itself
cp -a "$SRC/scripts/." "$DEST/scripts/"
echo "Synced SOUL.md, skills/, scripts/ -> $DEST"
echo "Next: merge mcp_servers from hermes-profile/config.yaml, then: hermes config check && hermes mcp test noc_mcp && deployment/cron/install-cron.sh"
