import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "hermes-profile"
SKILLS = sorted(p.parent.name for p in (PROFILE / "skills").glob("*/SKILL.md"))


def frontmatter(path: Path) -> dict:
    m = re.match(r"^---\n(.*?)\n---\n", path.read_text(), re.S)
    assert m, f"{path} has no frontmatter"
    return yaml.safe_load(m.group(1))


def test_skills_have_valid_frontmatter():
    assert len(SKILLS) == 7
    for name in SKILLS:
        fm = frontmatter(PROFILE / "skills" / name / "SKILL.md")
        assert fm["name"] == name and len(fm["description"]) > 20


def test_soul_routes_to_every_skill():
    soul = (PROFILE / "SOUL.md").read_text()
    assert all(f"`{s}`" in soul for s in SKILLS)


def test_cron_jobs_reference_real_skills_and_scripts():
    spec = yaml.safe_load((ROOT / "cron" / "jobs.yaml").read_text())
    for job in spec["jobs"]:
        assert set(job["skills"]) <= set(SKILLS), job["name"]
        assert (PROFILE / "scripts" / job["script"]).exists()
        assert "[SILENT]" in job["prompt"] or job["name"] == "daily-summary"


def test_config_files_parse():
    for f in [PROFILE / "noc.yaml", PROFILE / "config.yaml", ROOT / "deploy" / "argocd.yaml"]:
        yaml.safe_load(f.read_text())
    assert len(list(yaml.safe_load_all((ROOT / "deploy" / "k8s.yaml").read_text()))) == 2


def test_no_mcp_left():
    text = " ".join(p.read_text() for p in PROFILE.rglob("*") if p.is_file() and p.suffix in (".md", ".py", ".yaml"))
    assert "mcp_servers" not in text and "noc-mcp" not in text
