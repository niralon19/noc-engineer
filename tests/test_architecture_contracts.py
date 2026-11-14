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
    assert "hermes\" cron create" in script or '"$HERMES" cron create' in script
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
