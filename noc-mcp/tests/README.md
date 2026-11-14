# noc-mcp tests
LLM/DEVELOPER: unit-test each tool with mocked backends (no network). Add a replay suite: feed resolved historical alerts with known root cause and measure the correctness of conclusions (docs/investigation-flow.md). Test failure paths: backend timeout, empty result, oversized result, permission denied.
