"""
Shared schema pieces.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - ToolResult envelope (dataclass or pydantic): ok, data, error{code,message,retryable}, source, queried_at, time_range{start,end}, truncated
  - TimeRange, Pagination helpers
  - Helper to build error results from exceptions

All tools/* import from here.

Acceptance: unit tests in the matching tests/ folder pass with mocked backends; no network in tests.
"""
