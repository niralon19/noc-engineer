import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTE_SKILLS = ["alert-investigation", "customer-ticket", "config-change", "user-question", "proactive-review", "oncall-report"]
DOMAIN_SKILLS = ["traffic-hermetic", "coupling", "coatr"]
SUPPORT_SKILLS = ["change-correlation", "pipeline-walk", "capture-servers", "kafka-pipeline", "platform-operations",
                  "network-engineering", "enrichment-quality", "observability-queries", "jira-operations"]
SKILLS = ROUTE_SKILLS + DOMAIN_SKILLS + SUPPORT_SKILLS
CRON = {"data-quality-scan.yaml", "enrichment-audit.yaml", "anomaly-baseline.yaml",
        "jira-polling.yaml", "noc-daily-report.yaml", "housekeeping.yaml"}


def test_required_directories_exist():
    for name in ["hermes-profile", "noc-mcp", "anomaly-engine", "event-ingestion",
                 "reporting", "deployment", "docs", "workflows", "tests"]:
        assert (ROOT / name).is_dir(), name


def test_profile_files_exist():
    assert (ROOT / "hermes-profile" / "SOUL.md").exists()
    assert (ROOT / "hermes-profile" / "config.yaml").exists()


def test_route_and_domain_skills_exist():
    found = {p.parent.name for p in (ROOT / "hermes-profile" / "skills").glob("*/SKILL.md")}
    assert found == set(SKILLS), found ^ set(SKILLS)


def test_soul_routes_to_every_skill():
    soul = (ROOT / "hermes-profile" / "SOUL.md").read_text()
    for s in SKILLS:
        assert f"`{s}`" in soul, s


def test_skill_frontmatter_name_matches_directory():
    for s in SKILLS:
        head = (ROOT / "hermes-profile" / "skills" / s / "SKILL.md").read_text().splitlines()
        assert head[0] == "---" and f"name: {s}" in head[:4], s


def test_six_cron_jobs_defined_via_hermes_cli_script():
    script = (ROOT / "deployment" / "cron" / "install-cron.sh").read_text()
    for name in ["data-quality-scan", "enrichment-audit", "anomaly-baseline",
                 "jira-polling-backup", "housekeeping", "proactive-review", "oncall-report"]:
        assert name in script, name
    assert "hermes cron create" in script
    assert not list((ROOT / "deployment" / "cron").glob("*.yaml"))  # Hermes does not read cron YAML


def test_noscript_scripts_and_prompt_exist():
    for s in ["data_quality_scan", "enrichment_audit", "anomaly_baseline", "jira_poll", "housekeeping", "anomaly_scan"]:
        assert (ROOT / "hermes-profile" / "scripts" / f"{s}.py").exists(), s
    for pr in ["oncall-report.md", "proactive-review.md"]:
        assert (ROOT / "deployment" / "cron" / "prompts" / pr).exists(), pr


def test_cron_skills_exist():
    import re
    script = (ROOT / "deployment" / "cron" / "install-cron.sh").read_text()
    for line in re.findall(r"^job_agent .*$", script, re.M):
        for s in __import__("shlex").split(line)[5:]:
            assert s in SKILLS, s


def test_mcp_config_uses_hermes_shape():
    text = (ROOT / "hermes-profile" / "config.yaml").read_text()
    assert "mcp_servers:" in text and "tools:" in text and "include:" in text


def test_config_include_matches_contract():
    import yaml
    inc = yaml.safe_load((ROOT / "hermes-profile" / "config.yaml").read_text())["mcp_servers"]["noc_mcp"]["tools"]["include"]
    contract = yaml.safe_load((ROOT / "noc-mcp" / "config" / "tool-contracts.yaml").read_text())["domains"]
    known = {t for tools in contract.values() for t in tools}
    assert set(inc) <= known, set(inc) - known


def test_skills_reference_only_contract_tools():
    import re
    import yaml
    contract = yaml.safe_load((ROOT / "noc-mcp" / "config" / "tool-contracts.yaml").read_text())["domains"]
    known = {t for tools in contract.values() for t in tools}
    for p in (ROOT / "hermes-profile" / "skills").glob("*/SKILL.md"):
        for name in re.findall(r"`((?:get|search|find|query|add|create|validate|compare|lookup|resolve|check|inspect|audit|link)_[a-z_]+)`", p.read_text()):
            assert name in known, (p.parent.name, name)


def test_sync_profile_removes_stale_repo_skills(tmp_path):
    import shutil
    import subprocess
    fake = tmp_path / "bin"; fake.mkdir()
    (fake / "hermes").write_text("#!/usr/bin/env bash\nexit 0\n"); (fake / "hermes").chmod(0o755)
    home = tmp_path / "home"
    env = {"PATH": "/usr/bin:/bin", "HERMES_BIN": str(fake / "hermes"), "HERMES_HOME": str(home)}
    script = ROOT / "deployment" / "sync-profile.sh"
    subprocess.run(["bash", str(script)], check=True, env=env, capture_output=True)
    (home / "skills" / "agent-made").mkdir()            # skill Hermes created itself
    (home / ".repo-managed-skills").write_text("old-repo-skill\n" + (home / ".repo-managed-skills").read_text())
    (home / "skills" / "old-repo-skill").mkdir()
    subprocess.run(["bash", str(script)], check=True, env=env, capture_output=True)
    assert not (home / "skills" / "old-repo-skill").exists()
    assert (home / "skills" / "agent-made").exists()
    assert {p.name for p in (home / "skills").iterdir()} >= set(SKILLS)


def test_hermes_runtime_requirements_present():
    import yaml
    cfg = yaml.safe_load((ROOT / "hermes-profile" / "config.yaml").read_text())
    assert cfg["model"]["provider"] == "custom" and cfg["model"]["base_url"].endswith("/v1")
    api = cfg["gateway"]["api_server"]
    assert api["enabled"] is True and api["port"] == 8642 and "key" not in api   # key only in .env
    env = (ROOT / "deployment" / ".env.example").read_text()
    for var in ["OPENAI_API_KEY", "API_SERVER_KEY", "SLACK_BOT_TOKEN", "SLACK_APP_TOKEN", "SLACK_ALLOWED_USERS", "SLACK_HOME_CHANNEL"]:
        assert f"{var}=" in env, var
    k8s = list(yaml.safe_load_all((ROOT / "deployment" / "k8s" / "hermes.yaml").read_text()))
    dep = next(d for d in k8s if d["kind"] == "Deployment")
    assert dep["spec"]["replicas"] == 1
    assert {d["kind"] for d in k8s} >= {"Service", "Route", "PersistentVolumeClaim"}


def _run(cmd, **env):
    import os
    import subprocess
    return subprocess.run(cmd, capture_output=True, text=True, env={**os.environ, **env})


def test_install_cron_default_skips_stub_scripts_and_targets_profile():
    r = _run(["bash", str(ROOT / "deployment" / "cron" / "install-cron.sh"), "--dry-run", "--profile", "noc-engineer"])
    assert r.returncode == 0, r.stderr
    created = [l for l in r.stdout.splitlines() if " cron create " in l]
    assert all("hermes -p noc-engineer cron create" in l for l in created)
    assert "OK   oncall-report" in r.stdout and "SKIP data-quality-scan" in r.stdout


def test_install_cron_all_and_single_job():
    script = str(ROOT / "deployment" / "cron" / "install-cron.sh")
    assert _run(["bash", script, "--dry-run", "--all"]).stdout.count("OK   ") == 7
    one = _run(["bash", script, "--dry-run", "proactive-review"]).stdout
    assert "OK   proactive-review" in one and "oncall-report" not in one.replace("cron list", "")


def test_kustomization_is_fresh():
    r = _run(["python3", str(ROOT / "deployment" / "k8s" / "gen_kustomization.py"), "--check"])
    assert r.returncode == 0, r.stderr


def test_profile_init_unflattens_and_prunes(tmp_path):
    import shutil
    src, home = tmp_path / "src", tmp_path / "home"
    src.mkdir(); (home / "skills" / "old").mkdir(parents=True); (home / "skills" / "agent-made").mkdir()
    (home / ".repo-managed-skills").write_text("old\n")
    shutil.copy(ROOT / "hermes-profile" / "SOUL.md", src / "SOUL.md")
    for p in (ROOT / "hermes-profile" / "skills").glob("*/SKILL.md"):
        shutil.copy(p, src / f"skills__{p.parent.name}__SKILL.md")
    r = _run(["sh", str(ROOT / "deployment" / "k8s" / "profile-init.sh")], PROFILE_SRC=str(src), HERMES_HOME=str(home))
    assert r.returncode == 0, r.stderr
    names = {p.name for p in (home / "skills").iterdir()}
    assert "old" not in names and "agent-made" in names and set(SKILLS) <= names


def test_orientation_docs_present():
    claude = (ROOT / "CLAUDE.md").read_text()
    assert "## North star" in claude and "docs/STATUS.md" in claude and "docs/decisions.md" in claude
    assert (ROOT / "CLAUDE.md").read_text() == (ROOT / "AGENTS.md").read_text()
    assert "SUPERSEDED" in (ROOT / "docs" / "project-map.he.md").read_text()[:200]


def test_open_items_scanner_and_questionnaire_agree():
    import subprocess
    r = subprocess.run(["python3", str(ROOT / "scripts" / "open_items.py"), "--json"], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    items = json.loads(r.stdout)
    assert items and all(i["question"] != "(missing from OPEN-QUESTIONS.md)" for i in items)
    ids = {i["id"] for i in items}
    assert {"B2", "E1", "E2", "F1"} <= ids          # known open facts are reported with evidence
    assert any(i["evidence"] for i in items if i["id"] == "E2")


def test_claude_md_has_ask_protocol_and_soul_asks():
    claude = (ROOT / "CLAUDE.md").read_text()
    assert "scripts/open_items.py" in claude and "Never invent" in claude
    assert "## When information is missing" in (ROOT / "hermes-profile" / "SOUL.md").read_text()
