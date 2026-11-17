#!/usr/bin/env python3
"""Reconcile Hermes cron jobs with deployment/cron/jobs.yaml (declarative, idempotent, safe).

Runs on every pod start (init container `reconcile-cron`) and by hand via install-cron.sh.
- Each job is installed as <name>--<hash of its definition>; unchanged jobs are left alone (SAME).
- Changed jobs: the new version is CREATED FIRST; older versions are retired only after that succeeds.
- Jobs removed from jobs.yaml are pruned (only jobs this reconciler created, tracked in .repo-managed-cron).
- Jobs whose script is still a stub (raise NotImplementedError) are skipped.
- --soft: never exit non-zero (so a cron problem cannot block the gateway from starting); status is written to
  $HERMES_HOME/.cron-reconcile-status.json and checked by deployment/day0-check.sh.
UNVERIFIED (B4): `hermes cron create/list/remove` flags and whether they work while the gateway is not running.
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
import time
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO_SCRIPTS = HERE.parents[1] / "hermes-profile" / "scripts"
VERSIONED = re.compile(r"\b([a-z0-9][a-z0-9-]*?)--([0-9a-f]{8})\b")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("jobs_filter", nargs="*", help="only these job names")
    ap.add_argument("--jobs", default=str(HERE / "jobs.yaml"))
    ap.add_argument("--prompts-dir", default=str(HERE / "prompts"))
    ap.add_argument("--profile", default=os.environ.get("PROFILE", "noc-engineer"),
                    help="hermes -p <profile>; pass '' when HERMES_HOME already points at the profile")
    ap.add_argument("--home", default=os.environ.get("HERMES_HOME", ""))
    ap.add_argument("--hermes-bin", default=os.environ.get("HERMES_BIN", "hermes"))
    ap.add_argument("--deliver", default=os.environ.get("NOC_DELIVER"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--all", action="store_true", help="install stub-script jobs too")
    ap.add_argument("--no-prune", action="store_true")
    ap.add_argument("--soft", action="store_true", help="exit 0 even on failures (init container)")
    ap.add_argument("--list-jobs", action="store_true")
    return ap.parse_args()


class Hermes:
    def __init__(self, a: argparse.Namespace):
        self.base = shlex.split(a.hermes_bin) + (["-p", a.profile] if a.profile else [])
        self.dry = a.dry_run

    def run(self, *args: str) -> subprocess.CompletedProcess:
        cmd = self.base + list(args)
        if self.dry:
            print("DRY-RUN: " + " ".join(shlex.quote(c) for c in cmd))
            return subprocess.CompletedProcess(cmd, 0, "", "")
        return subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    def existing(self) -> dict[str, list[str]]:
        if self.dry:
            return {}
        out = subprocess.run(self.base + ["cron", "list"], capture_output=True, text=True, timeout=60).stdout
        found: dict[str, list[str]] = {}
        for m in VERSIONED.finditer(out):
            found.setdefault(m.group(1), [])
            if m.group(0) not in found[m.group(1)]:
                found[m.group(1)].append(m.group(0))
        return found


def implemented(script: str, scripts_dir: Path) -> bool:
    for d in (scripts_dir, REPO_SCRIPTS):
        p = d / script
        if p.exists():
            return "raise NotImplementedError" not in p.read_text()
    return False


def create_args(job: dict, deliver: str, scripts_dir: Path, prompts_dir: Path) -> list[str]:
    args = ["cron", "create", job["schedule"]]
    if job["mode"] == "agent":
        args.append((prompts_dir / job["prompt"]).read_text().strip())
    extra: list[str] = []
    if job["mode"] == "script":
        extra += ["--no-agent", "--script", str(scripts_dir / job["script"])]
    else:
        for s in job.get("skills", []):
            extra += ["--skill", s]
        if job.get("script"):
            extra += ["--script", str(scripts_dir / job["script"])]
    return args + extra + ["--deliver", job.get("deliver") or deliver]


def main() -> int:
    a = parse_args()
    spec = yaml.safe_load(Path(a.jobs).read_text())
    jobs = spec["jobs"]
    if a.list_jobs:
        print(" ".join(j["name"] for j in jobs))
        return 0
    home = Path(a.home) if a.home else Path.home() / ".hermes" / "profiles" / (a.profile or "default")
    scripts_dir, prompts_dir = home / "scripts", Path(a.prompts_dir)
    deliver = a.deliver or spec.get("deliver", "local")
    hermes = Hermes(a)
    existing = hermes.existing()
    wanted = [j for j in jobs if not a.jobs_filter or j["name"] in a.jobs_filter]
    status = {"at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "ok": [], "same": [], "skipped": [], "failed": [], "pruned": []}
    print(f"profile={a.profile or '(HERMES_HOME)'} home={home} deliver={deliver}")
    print(f"NOTE: schedules are meant as Asia/Jerusalem. Container time: {time.strftime('%H:%M %Z')}.")

    for job in wanted:
        name = job["name"]
        script = job.get("script")
        if script and not a.all and not implemented(script, scripts_dir) and not a.jobs_filter:
            print(f"SKIP {name}: script {script} not implemented yet (use --all or name the job to force)")
            status["skipped"].append(name)
            continue
        args = create_args(job, deliver, scripts_dir, prompts_dir)
        versioned = f"{name}--{hashlib.sha256(json.dumps(args).encode()).hexdigest()[:8]}"
        current = existing.get(name, [])
        if versioned in current:
            print(f"SAME {name} ({versioned} unchanged)")
            status["same"].append(name)
            continue
        r = hermes.run(*args, "--name", versioned)
        if r.returncode != 0:
            print(f"FAIL {name}: create failed; previous version left running. {r.stderr.strip()[:200]}", file=sys.stderr)
            status["failed"].append(name)
            continue
        for old in current:
            if old != versioned:
                ok = hermes.run("cron", "remove", old).returncode == 0
                print(f"     retired {old}" if ok else f"WARN could not remove {old} (remove it manually)")
        print(f"OK   {name} -> {versioned}")
        status["ok"].append(name)

    # prune jobs we created earlier that are no longer declared
    managed_file = home / ".repo-managed-cron"
    declared = {j["name"] for j in jobs}
    if not a.no_prune and not a.jobs_filter and managed_file.exists():
        for old_name in managed_file.read_text().split():
            if old_name not in declared:
                for v in existing.get(old_name, []):
                    if hermes.run("cron", "remove", v).returncode == 0:
                        print(f"PRUNE {v} (no longer in jobs.yaml)")
                        status["pruned"].append(v)
    if not a.dry_run and not a.jobs_filter:
        home.mkdir(parents=True, exist_ok=True)
        managed_file.write_text("\n".join(sorted(declared)) + "\n")
        (home / ".cron-reconcile-status.json").write_text(json.dumps(status, indent=2))

    if not a.dry_run:
        hermes.run("cron", "list")
    if status["failed"]:
        print(f"{len(status['failed'])} job(s) failed to install; old versions kept", file=sys.stderr)
        return 0 if a.soft else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
