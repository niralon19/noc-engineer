#!/usr/bin/env python3
"""Make Hermes cron match cron/jobs.yaml. Idempotent; runs on every pod start (deploy/start.sh).

Each job is created as <name>--<hash of its definition>. Unchanged -> left alone. Changed -> the new version is
created first, then older versions are removed. Jobs deleted from jobs.yaml are removed too (only ones we created).
Uses HERMES_HOME from the environment. --soft: never fail (a cron problem must not stop the gateway).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
VERSIONED = re.compile(r"\b([a-z0-9][a-z0-9-]*?)--([0-9a-f]{8})\b")


def create_args(job: dict, deliver: str, scripts_dir: Path) -> list[str]:
    args = ["cron", "create", job["schedule"], job["prompt"].strip()]
    for s in job.get("skills", []):
        args += ["--skill", s]
    if job.get("script"):
        args += ["--script", str(scripts_dir / job["script"])]
    return args + ["--deliver", job.get("deliver") or deliver]


def versioned_name(name: str, args: list[str]) -> str:
    return f"{name}--{hashlib.sha256(json.dumps(args).encode()).hexdigest()[:8]}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--jobs", default=str(HERE / "jobs.yaml"))
    ap.add_argument("--hermes-bin", default=os.environ.get("HERMES_BIN", "hermes"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--soft", action="store_true")
    a = ap.parse_args(argv)

    home = Path(os.environ.get("HERMES_HOME") or Path.home() / ".hermes")
    spec = yaml.safe_load(Path(a.jobs).read_text())
    hermes = shlex.split(a.hermes_bin)

    def run(*args: str) -> int:
        if a.dry_run:
            print("DRY-RUN:", " ".join(shlex.quote(x) for x in hermes + list(args)))
            return 0
        r = subprocess.run(hermes + list(args), capture_output=True, text=True, timeout=120)
        if r.returncode:
            print(f"  hermes {' '.join(args[:2])} failed: {r.stderr.strip()[:200]}", file=sys.stderr)
        return r.returncode

    existing: dict[str, list[str]] = {}
    if not a.dry_run:
        listing = subprocess.run(hermes + ["cron", "list"], capture_output=True, text=True, timeout=60).stdout
        for m in VERSIONED.finditer(listing):
            if m.group(0) not in existing.setdefault(m.group(1), []):
                existing[m.group(1)].append(m.group(0))

    failed = 0
    declared = {j["name"] for j in spec["jobs"]}
    for job in spec["jobs"]:
        args = create_args(job, spec.get("deliver", "local"), home / "scripts")
        name = versioned_name(job["name"], args)
        current = existing.get(job["name"], [])
        if name in current:
            print(f"SAME {job['name']}")
            continue
        if run(*args, "--name", name):
            failed += 1
            print(f"FAIL {job['name']} (previous version kept)")
            continue
        for old in current:
            if old != name:
                run("cron", "remove", old)
        print(f"OK   {job['name']} -> {name}")

    managed = home / ".managed-cron"
    if managed.exists():
        for old_name in managed.read_text().split():
            if old_name not in declared:
                for v in existing.get(old_name, []):
                    if not run("cron", "remove", v):
                        print(f"GONE {v}")
    if not a.dry_run:
        home.mkdir(parents=True, exist_ok=True)
        managed.write_text("\n".join(sorted(declared)) + "\n")
    return 0 if (a.soft or not failed) else 1


if __name__ == "__main__":
    sys.exit(main())
