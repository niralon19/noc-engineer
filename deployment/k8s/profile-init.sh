#!/bin/sh
# Init container: unpack the hermes-profile ConfigMap (flattened keys) into the persistent HERMES_HOME.
# Keys: SOUL.md, skills__<name>__SKILL.md, scripts__<file>. config.yaml is NOT touched (lives on the PVC).
# Removes skills this repo deployed before but no longer ships; keeps skills Hermes created itself.
set -eu
SRC="${PROFILE_SRC:-/profile-src}"
DEST="${HERMES_HOME:?set HERMES_HOME}"
mkdir -p "$DEST/skills" "$DEST/scripts"
cp "$SRC/SOUL.md" "$DEST/SOUL.md"
NEW_MANIFEST="$DEST/.repo-managed-skills.new"
: > "$NEW_MANIFEST"
for f in "$SRC"/skills__*__SKILL.md; do
  [ -e "$f" ] || continue
  name=$(basename "$f"); name=${name#skills__}; name=${name%__SKILL.md}
  mkdir -p "$DEST/skills/$name"; cp "$f" "$DEST/skills/$name/SKILL.md"
  echo "$name" >> "$NEW_MANIFEST"
done
if [ -f "$DEST/.repo-managed-skills" ]; then
  while IFS= read -r old; do
    [ -n "$old" ] || continue
    grep -qx "$old" "$NEW_MANIFEST" || { rm -rf "$DEST/skills/$old"; echo "removed stale skill: $old"; }
  done < "$DEST/.repo-managed-skills"
fi
mv "$NEW_MANIFEST" "$DEST/.repo-managed-skills"
for f in "$SRC"/scripts__*; do
  [ -e "$f" ] || continue
  name=$(basename "$f"); cp "$f" "$DEST/scripts/${name#scripts__}"
done
echo "profile synced into $DEST: $(wc -l < "$DEST/.repo-managed-skills") skills"
