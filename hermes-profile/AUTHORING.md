# Authoring guide (developer-only; NOT loaded by Hermes)

`SOUL.md` and `skills/*/SKILL.md` go into the model prompt. Keep them short, imperative, English, and free of developer notes.

## Filling a SKILL.md
Replace each `TODO` with concrete content:
- **When to use:** trigger conditions (alert types, keywords, data domains).
- **Tools to call:** exact tool names from `noc-mcp/config/tool-contracts.yaml` (verified via MCP discovery), in order.
- **Order of checks:** numbered steps; check the time window before and after the event.
- **Required data:** inputs the skill needs before starting; ask/state what is missing.
- **Cross-referencing:** which independent sources must agree before concluding.
- **Failure modes:** tool down, stale data, missing samples -> say so, do not invent.
- **Verification:** what must be true to call a conclusion CONFIRMED.
- **Output:** the standard investigation result (`noc-mcp/schemas/investigation.py`).
Write the skill ONLY after a real investigation shows what the agent got wrong; start with sre-observability, incident-investigation, itsm-coordination.

## config.yaml
Add the `mcp_servers` entry for the MCP server and a tool allow-list (start ~8 read-only tools + Jira comment/create). Verify exact keys against the installed Hermes version (`hermes config check`).
