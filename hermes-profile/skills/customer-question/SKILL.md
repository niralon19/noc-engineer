---
name: customer-question
description: "Answer questions from the team or customers in Slack about their servers, rules, loss, load or alerts."
---

# Questions in Slack

Typical: "Is there loss on my server?", "Why did rule X stop matching?", "Was there maintenance last night?"

1. Identify what is asked about: server, rule, customer, time window. If one essential fact is missing, ask one short question.
2. Load `noc-environment`; query with `noc-tools`. Compare with last week or the window before.
3. Answer:
   - first line: the direct answer (yes / no / where)
   - 2-4 lines of evidence with numbers and time window
   - what you could not check, if anything
4. Never paste raw JSON or internal hostnames the asker did not mention. Never promise changes; you are read-only.
