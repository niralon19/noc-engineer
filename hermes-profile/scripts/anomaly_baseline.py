"""No-agent cron script: anomaly_baseline.

REQUIRES FROM NIR: K3, E3, E4 (docs/OPEN-QUESTIONS.md). Before implementing/filling run `python3 scripts/open_items.py --file hermes-profile/scripts/anomaly_baseline.py`; if BLOCKED, ask Nir. Never invent.

FOR THE LLM / DEVELOPER OPENING THIS FILE
Hermes runs this script on schedule (hermes cron create --no-agent --script) and delivers its STDOUT verbatim. No LLM is involved.
What to implement:
  - Recompute hourly baselines (anomaly-engine/baselines.py) and persist them.
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
