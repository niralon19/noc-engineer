---
name: user-question
description: Answer a question from a team member in chat or Slack about alerts, metrics, incidents, Jira or the environment.
---

# User question

- Answer from live data via tools, not from memory, when the question is about current state. Cite the query and time window.
- Read-only: never create or change Jira issues or anything else from a question unless the user explicitly asks and the action is allowed in this session.
- If the question is really "why is X broken", switch to investigation: Follow the investigation protocol and output contract from the `alert-investigation` skill.
- If the question is ambiguous (which service, which time range), ask one short question before running heavy queries.
- Keep answers short: bottom line first, then evidence.
