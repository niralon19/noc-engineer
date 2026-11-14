# Authoring guide (developer-only; NOT loaded by Hermes)

`SOUL.md` and `skills/*/SKILL.md` go into the model prompt. Keep them short, imperative, English, and free of developer notes.

## Skill layout
- Route skills (procedure): alert-investigation, customer-ticket, user-question, proactive-review, oncall-report. The investigation protocol and output contract live ONLY in alert-investigation; others reference it.
- Supporting skills (cross-cutting layers): observability-queries, network-engineering, openshift-operations, jira-operations, enrichment-quality. Keep them generic to the layer; alert-specific logic goes in domain skills.
- Domain skills (knowledge): traffic-hermetic, coupling, coatr. Port the domain logic from the CrewAI agents/tools. Fill "Environment knowledge" only with facts from Nir/the team (metric meaning, normal ranges, known causes, owners). Delete the HTML comment once filled.
- Keep tool names in skills equal to the names exposed by the MCP server (and listed in config.yaml tools.include).
- Change a skill only after a real investigation shows what went wrong; add that case to the evaluation set.

## config.yaml
Add the `mcp_servers` entry for the MCP server and a tool allow-list (start ~8 read-only tools + Jira comment/create). Verify exact keys against the installed Hermes version (`hermes config check`).
