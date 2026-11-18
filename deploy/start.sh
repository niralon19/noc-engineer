#!/bin/sh
# Pod entrypoint: copy the profile from the image into the persistent HERMES_HOME, apply cron, start the gateway.
# Overwritten on every start: SOUL.md, noc.yaml, our skills, scripts. Seeded once: config.yaml. Kept: memories,
# sessions, .env, skills Hermes created itself.
set -eu
: "${HERMES_HOME:?HERMES_HOME must be set}"
SRC=/opt/noc/hermes-profile
mkdir -p "$HERMES_HOME/skills" "$HERMES_HOME/scripts"
cp "$SRC/SOUL.md" "$SRC/noc.yaml" "$HERMES_HOME/"
[ -f "$HERMES_HOME/config.yaml" ] || cp "$SRC/config.yaml" "$HERMES_HOME/config.yaml"
for d in "$SRC"/skills/*/; do
  name=$(basename "$d")
  rm -rf "$HERMES_HOME/skills/$name"
  cp -r "$d" "$HERMES_HOME/skills/$name"
done
cp "$SRC"/scripts/*.py "$HERMES_HOME/scripts/"
python3 /opt/noc/cron/reconcile_cron.py --soft
exec hermes gateway run
