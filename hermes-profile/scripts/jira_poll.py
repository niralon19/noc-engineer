"""No-agent cron script: jira_poll.

FOR THE LLM / DEVELOPER OPENING THIS FILE
Hermes runs this script on schedule (hermes cron create --no-agent --script) and delivers its STDOUT verbatim. No LLM is involved.
What to implement:
  - Poll Jira with a persisted cursor (event-ingestion/jira_poller.py), dedupe, forward new events to Hermes.
  - Print a short human-readable result to stdout ONLY when something needs attention; verify with Nir/Hermes docs how an empty stdout is handled before relying on silence.
  - Exit non-zero on failure (so it is visible), never hang (default no-agent timeout is ~120 s).
  - Read config/secrets from environment (.env); never print secrets.
  - Reuse code from anomaly-engine/, event-ingestion/, noc-mcp/clients/ instead of duplicating logic.
"""
import sys


def main() -> int:
    raise NotImplementedError


if __name__ == "__main__":
    sys.exit(main())
