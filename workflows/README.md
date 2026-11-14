# Workflows (design specs)

These YAML files describe flows that our own Python code (event-ingestion/, anomaly-engine/, reporting/) implements. **Hermes does not read them.** In Hermes terms: methodology lives in skills, schedules in `hermes cron`, tools in MCP. `event-schema.json` is the contract between our Python producers and the agent bridge.
