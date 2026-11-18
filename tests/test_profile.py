import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = sorted(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md"))


def frontmatter(path: Path) -> dict:
    m = re.match(r"^---\n(.*?)\n---\n", path.read_text(), re.S)
    assert m, f"{path} has no frontmatter"
    return yaml.safe_load(m.group(1))


def test_distribution_manifest():
    d = yaml.safe_load((ROOT / "distribution.yaml").read_text())
    assert d["name"] == "noc-engineer"
    assert all({"name", "description", "required"} <= set(e) for e in d["env_requires"])
    for p in d["distribution_owned"]:
        assert (ROOT / p.rstrip("/")).exists(), p


def test_skills_have_valid_frontmatter():
    assert len(SKILLS) == 7
    for name in SKILLS:
        fm = frontmatter(ROOT / "skills" / name / "SKILL.md")
        assert fm["name"] == name and len(fm["description"]) > 20


def test_soul_routes_to_every_skill():
    soul = (ROOT / "SOUL.md").read_text()
    assert all(f"`{s}`" in soul for s in SKILLS)


def test_cron_jobs_reference_real_skills_and_scripts():
    jobs = [json.loads(p.read_text()) for p in sorted((ROOT / "cron").glob("*.json"))]
    assert len(jobs) == 4
    for job in jobs:
        assert set(job["skills"]) <= set(SKILLS), job["name"]
        assert (ROOT / "scripts" / job["script"]).exists()
        assert job["name"] in (ROOT / "README.md").read_text()
        assert "[SILENT]" in job["prompt"] or job["name"] == "daily-summary"


def test_config_files_parse():
    yaml.safe_load((ROOT / "config.yaml").read_text())
    yaml.safe_load((ROOT / "skills" / "noc-tools" / "assets" / "noc.yaml").read_text())
    assert len(list(yaml.safe_load_all((ROOT / "deploy" / "k8s.yaml").read_text()))) == 2


def test_prompt_files_have_no_dev_notes():
    for f in [ROOT / "SOUL.md", *(ROOT / "skills").glob("*/SKILL.md")]:
        assert "TODO" not in f.read_text() and "mcp" not in f.read_text().lower(), f
