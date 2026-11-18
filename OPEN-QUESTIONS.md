# Open questions (Nir)

| ID | Question | Where it goes |
|---|---|---|
| Q1 | Kimi K3 endpoint URL and exact model id | `hermes-profile/config.yaml` |
| Q2 | Hermes image and version in the cluster; do `hermes cron create --script/--skill/--deliver/--name` match that version | `deploy/k8s.yaml`, `cron/reconcile_cron.py` |
| Q3 | PromQL for each anomaly check (port in, port out, rule rate, more?) and the thresholds | `noc.yaml` `anomaly.checks` |
| Q4 | ECK index pattern for application logs | `noc.yaml` `elasticsearch.default_index` |
| Q5 | JQL for customer tickets the agent should handle | `noc.yaml` `jira.customer_jql` |
| Q6 | Hop ids of the data path, the metric per hop, known failure patterns | `noc.yaml` `pipeline.hops`, `skills/noc-environment` |
| Q7 | Slack: team channel ID, allowed member IDs (team + which customers) | Secret `hermes-noc-env` |
| Q8 | Namespace and registry for the deployment | `deploy/k8s.yaml`, `deploy/argocd.yaml` |
