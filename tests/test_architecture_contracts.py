from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def test_primary_profile_exists():
    assert (ROOT / "profile" / "noc-engineer.yaml").exists()

def test_required_architecture_directories_exist():
    for name in ["profile", "skills", "mcp", "workflows", "cron", "config", "memory", "tests"]:
        assert (ROOT / name).is_dir()

def test_all_seven_skills_exist():
    assert len(list((ROOT / "skills").glob("*/SKILL.md"))) == 7

def test_six_scheduled_jobs_exist():
    expected = {"data-quality-scan.yaml", "enrichment-audit.yaml", "anomaly-baseline.yaml", "jira-polling.yaml", "noc-daily-report.yaml", "housekeeping.yaml"}
    assert expected.issubset({p.name for p in (ROOT / "cron").glob("*.yaml")})
