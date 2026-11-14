# Deploying Hermes on OpenShift/Rancher with Argo CD (GitOps)

> LLM/DEVELOPER: skeleton. VERIFY with Nir: Hermes container image and tag, the HERMES_HOME path inside it, how the gateway is started, which cluster/namespace, storage class, and how secrets are provided (sealed secrets / vault / external secrets). Do not guess.

- `kustomization.yaml` builds a ConfigMap from `hermes-profile/` (SOUL.md, skills, scripts) so the profile is versioned and deployed by Argo, not copied by hand.
- An init container copies the ConfigMap into the persistent HERMES_HOME (PVC) on every start, deleting only repo-managed skills (see `profile-manifest.txt` logic in sync-profile.sh), so Hermes memory/sessions/cron jobs survive.
- `config.yaml` is NOT overwritten: it lives on the PVC and is changed with `hermes config set` (or a dedicated merge job).
- Runs as non-root (OpenShift restricted SCC). Egress only to: Kimi endpoint, MCP server, Slack, Jira.
- After first deploy: exec into the pod and run `deployment/cron/install-cron.sh` once.
