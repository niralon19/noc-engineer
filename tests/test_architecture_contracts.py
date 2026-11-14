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


def test_six_scheduled_jobs_exist():
    assert CRON.issubset({p.name for p in (ROOT / "deployment" / "cron").glob("*.yaml")})
