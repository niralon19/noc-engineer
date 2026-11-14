"""Script feeding the `proactive-review` agent cron job (every 15 min).

FOR THE LLM / DEVELOPER OPENING THIS FILE
Hermes runs this script before the agent and passes its STDOUT to the agent as context.
What to implement:
  - Run anomaly-engine/detection.py over the last 15 minutes (bounded batches; ~100K series).
  - Print NO_FINDINGS when nothing was detected (the prompt tells the agent to answer [SILENT]).
  - Otherwise print a compact JSON list of findings: entity, metric, deviation, baseline, onset, rule_id, event_id.
  - Deduplicate against findings already reported (persist event_ids), so the agent sees each finding once.
  - Exit non-zero on failure; never hang. No LLM calls here.
Note: the agent still wakes every 15 min even when it answers [SILENT]. If token cost matters, verify with Nir
whether his Hermes version skips the agent on empty script output, or lower the frequency.
"""
import sys


def main() -> int:
    raise NotImplementedError


if __name__ == "__main__":
    sys.exit(main())
