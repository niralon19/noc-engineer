from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ["sre-observability", "network-engineering", "incident-investigation",
          "devops-operations", "itsm-coordination", "data-quality", "enrichment-quality"]
CRON = {"data-quality-scan.yaml", "enrichment-audit.yaml", "anomaly-baseline.yaml",
        "jira-polling.yaml", "noc-daily-report.yaml", "housekeeping.yaml"}


def test_required_directories_exist():
    for name in ["hermes-profile", "noc-mcp", "anomaly-engine", "event-ingestion",
                 "reporting", "deployment", "docs", "workflows", "tests"]:
        assert (ROOT / name).is_dir(), name


def test_profile_files_exist():
    assert (ROOT / "hermes-profile" / "SOUL.md").exists()
    assert (ROOT / "hermes-profile" / "config.yaml").exists()


def test_all_seven_skills_exist():
    for s in SKILLS:
        assert (ROOT / "hermes-profile" / "skills" / s / "SKILL.md").exists(), s


def test_skill_frontmatter_name_matches_directory():
    for s in SKILLS:
        head = (ROOT / "hermes-profile" / "skills" / s / "SKILL.md").read_text().splitlines()
        assert head[0] == "---" and f"name: {s}" in head[:4], s


def test_six_cron_jobs_defined_via_hermes_cli_script():
    script = (ROOT / "deployment" / "cron" / "install-cron.sh").read_text()
    for name in ["data-quality-scan", "enrichment-audit", "anomaly-baseline",
                 "jira-polling-backup", "housekeeping", "noc-daily-report"]:
        assert name in script, name
    assert "hermes\" cron create" in script or '"$HERMES" cron create' in script
    assert not list((ROOT / "deployment" / "cron").glob("*.yaml"))  # Hermes does not read cron YAML


def test_noscript_scripts_and_prompt_exist():
    for s in ["data_quality_scan", "enrichment_audit", "anomaly_baseline", "jira_poll", "housekeeping"]:
        assert (ROOT / "hermes-profile" / "scripts" / f"{s}.py").exists(), s
    assert (ROOT / "deployment" / "cron" / "prompts" / "noc-daily-report.md").exists()


def test_mcp_config_uses_hermes_shape():
    text = (ROOT / "hermes-profile" / "config.yaml").read_text()
    assert "mcp_servers:" in text and "tools:" in text and "include:" in text
