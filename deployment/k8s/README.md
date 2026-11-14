# Deploying Hermes on OpenShift/Rancher with Argo CD (GitOps)

> LLM/DEVELOPER: skeleton. VERIFY with Nir: Hermes container image and tag, the HERMES_HOME path inside it, how the gateway is started, which cluster/namespace, storage class, and how secrets are provided (sealed secrets / vault / external secrets). Do not guess.

- `kustomization.yaml` builds a ConfigMap from `hermes-profile/` (SOUL.md, skills, scripts) so the profile is versioned and deployed by Argo, not copied by hand.
- An init container copies the ConfigMap into the persistent HERMES_HOME (PVC) on every start, deleting only repo-managed skills (see `profile-manifest.txt` logic in sync-profile.sh), so Hermes memory/sessions/cron jobs survive.
- `config.yaml` is NOT overwritten: it lives on the PVC and is changed with `hermes config set` (or a dedicated merge job).
- Runs as non-root (OpenShift restricted SCC). Egress only to: Kimi endpoint, MCP server, Slack (Socket Mode, outbound WebSocket), Jira.
- One process (`hermes gateway run`) serves Slack, cron and the API server (port 8642, `/health`). Service + Route expose the API to the web app backend only; never to browsers directly.
- Secret `hermes-noc-engineer-env` holds the values from `deployment/.env.example` (OPENAI_API_KEY, API_SERVER_KEY, SLACK_*, backends).
- After first deploy: exec into the pod and run `deployment/cron/install-cron.sh` once.

## Commands
```bash
python3 deployment/k8s/gen_kustomization.py      # after adding/removing skills or scripts (a test checks it is fresh)
kubectl kustomize deployment/k8s                 # render locally before committing
```
