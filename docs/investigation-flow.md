# Investigation flow

> **REQUIRES FROM NIR: J1 (docs/OPEN-QUESTIONS.md). Before implementing/filling run `python3 scripts/open_items.py --file docs/investigation-flow.md`; if BLOCKED, ask Nir. Never invent.**

> LLM/DEVELOPER: describe: alert -> context -> skills -> MCP evidence -> baseline/trend/related incidents -> conclusion -> Jira (dedup) -> report. Define the investigation JSON (`noc-mcp/schemas/investigation.py`), the 4 categorical statuses with explicit criteria for each, and the evaluation procedure on historical resolved alerts (precision, false positives, time to conclusion).
