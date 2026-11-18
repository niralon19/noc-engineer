#!/bin/sh
# Pod entrypoint. Same as `hermes profile update`: replace the distribution-owned files in HERMES_HOME
# (config.yaml only on first start), schedule any cron job from cron/*.json that is not there yet, run the gateway.
set -eu
: "${HERMES_HOME:?HERMES_HOME must be set}"
SRC=/opt/noc-engineer
mkdir -p "$HERMES_HOME"
for p in SOUL.md distribution.yaml skills scripts cron; do
  rm -rf "${HERMES_HOME:?}/$p"
  cp -r "$SRC/$p" "$HERMES_HOME/$p"
done
[ -f "$HERMES_HOME/config.yaml" ] || cp "$SRC/config.yaml" "$HERMES_HOME/config.yaml"

python3 - <<'EOF'
import glob, json, subprocess
existing = subprocess.run(["hermes", "cron", "list"], capture_output=True, text=True).stdout
for f in sorted(glob.glob("/opt/noc-engineer/cron/*.json")):
    j = json.load(open(f))
    if j["name"] in existing:
        continue
    cmd = ["hermes", "cron", "create", j["schedule"], j["prompt"], "--name", j["name"], "--deliver", j["deliver"]]
    for s in j.get("skills", []):
        cmd += ["--skill", s]
    if j.get("script"):
        cmd += ["--script", j["script"]]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(("scheduled " if r.returncode == 0 else "FAILED ") + j["name"], r.stderr.strip()[:200])
EOF

exec hermes gateway run
