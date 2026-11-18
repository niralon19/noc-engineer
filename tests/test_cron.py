import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cron"))
import reconcile_cron  # noqa: E402

FAKE = '''#!/usr/bin/env python3
import json, sys, pathlib
db = pathlib.Path(sys.argv[0]).with_suffix(".json")
jobs = json.loads(db.read_text()) if db.exists() else {}
a = sys.argv[1:]
if a[:2] == ["cron", "list"]:
    print("\\n".join(jobs))
elif a[:2] == ["cron", "create"]:
    jobs[a[a.index("--name") + 1]] = a
elif a[:2] == ["cron", "remove"]:
    jobs.pop(a[2], None)
db.write_text(json.dumps(jobs))
'''


def setup(tmp_path, monkeypatch):
    fake = tmp_path / "hermes"
    fake.write_text(FAKE)
    fake.chmod(0o755)
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "home"))
    spec = yaml.safe_load((ROOT / "cron" / "jobs.yaml").read_text())
    jobs = tmp_path / "jobs.yaml"
    jobs.write_text(yaml.safe_dump(spec))
    return fake, jobs, spec, lambda: json.loads(fake.with_suffix(".json").read_text())


def test_create_same_change_prune(tmp_path, monkeypatch):
    fake, jobs, spec, state = setup(tmp_path, monkeypatch)
    args = ["--jobs", str(jobs), "--hermes-bin", str(fake)]
    assert reconcile_cron.main(args) == 0
    first = state()
    assert len(first) == 4 and all("--" in k for k in first)
    assert reconcile_cron.main(args) == 0 and state() == first            # idempotent

    spec["jobs"][0]["schedule"] = "*/10 * * * *"
    del spec["jobs"][3]
    jobs.write_text(yaml.safe_dump(spec))
    assert reconcile_cron.main(args) == 0
    names = list(state())
    assert len(names) == 3 and not any(n.startswith("jira-tickets--") for n in names)
    assert sum(n.startswith("anomaly-scan--") for n in names) == 1
    assert next(v for k, v in state().items() if k.startswith("anomaly-scan--"))[2] == "*/10 * * * *"


def test_create_args_shape(tmp_path):
    job = {"name": "x", "schedule": "0 9 * * *", "prompt": "p", "skills": ["a", "b"], "script": "s.py"}
    args = reconcile_cron.create_args(job, "slack", tmp_path)
    assert args[:4] == ["cron", "create", "0 9 * * *", "p"]
    assert ["--skill", "a", "--skill", "b", "--script", str(tmp_path / "s.py"), "--deliver", "slack"] == args[4:]
