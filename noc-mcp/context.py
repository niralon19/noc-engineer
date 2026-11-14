"""Runtime context: settings + HTTP. Tests swap it with set_context().

Settings come from config/backends.yaml (path: NOC_MCP_CONFIG), with ${ENV_VAR} substitution so secrets
stay in the environment. The pipeline map comes from config/pipeline.yaml (NOC_MCP_PIPELINE).
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml

from clients.http import Http

HERE = Path(__file__).resolve().parent
_ENV = re.compile(r"\$\{([A-Z0-9_]+)(?::-([^}]*))?\}")


def _subst(obj: Any) -> Any:
    if isinstance(obj, str):
        return _ENV.sub(lambda m: os.environ.get(m.group(1), m.group(2) or ""), obj)
    if isinstance(obj, list):
        return [_subst(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _subst(v) for k, v in obj.items()}
    return obj


def load_yaml(path: Path) -> dict:
    return _subst(yaml.safe_load(path.read_text()) or {}) if path.exists() else {}


@dataclass
class Context:
    settings: dict
    pipeline: dict
    http: Http = field(default_factory=Http)

    def section(self, name: str) -> dict:
        return self.settings.get(name) or {}


_ctx: Optional[Context] = None


def default_context() -> Context:
    cfg = Path(os.environ.get("NOC_MCP_CONFIG", HERE / "config" / "backends.yaml"))
    if not cfg.exists():
        cfg = HERE / "config" / "backends.example.yaml"
    pipe = Path(os.environ.get("NOC_MCP_PIPELINE", HERE / "config" / "pipeline.yaml"))
    return Context(load_yaml(cfg), load_yaml(pipe))


def get_context() -> Context:
    global _ctx
    if _ctx is None:
        _ctx = default_context()
    return _ctx


def set_context(ctx: Optional[Context]) -> None:
    global _ctx
    _ctx = ctx
