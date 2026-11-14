"""Client for the rule & configuration management system. Paths and field names come from config (rules:)."""
from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Any, Optional
from urllib.parse import quote

import yaml

from clients.http import bearer
from context import HERE, Context
from schemas.common import is_tbd, not_configured


def dig(obj: Any, path: str) -> Any:
    """Follow a dotted path ('a.b.0.c') into JSON; '' returns obj."""
    if not path:
        return obj
    for part in path.split("."):
        if isinstance(obj, list) and part.isdigit():
            obj = obj[int(part)] if int(part) < len(obj) else None
        elif isinstance(obj, dict):
            obj = obj.get(part)
        else:
            return None
    return obj


class Rules:
    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.cfg = ctx.section("rules")

    def _get(self, key: str, **values: str) -> Any:
        tmpl = self.cfg.get(key)
        if is_tbd(tmpl) or is_tbd(self.cfg.get("base_url")):
            raise not_configured(f"rules.{key}")
        path = tmpl
        for k, v in values.items():
            path = path.replace("{" + k + "}", quote(str(v), safe=""))
        return self.ctx.http.get(self.cfg["base_url"].rstrip("/") + path, headers=bearer(self.cfg.get("token")))

    def rule(self, rule_id: str) -> Any:
        return self._get("get_rule_path", rule_id=rule_id)

    def changes(self, rule_id: Optional[str], start: str, end: str) -> list[dict]:
        if rule_id:
            body = self._get("changes_path", rule_id=rule_id, start=start, end=end)
        else:
            body = self._get("global_changes_path", start=start, end=end)
        items = dig(body, self.cfg.get("changes_list_field", "")) or []
        fields = self.cfg.get("change_fields") or {}
        return [{k: dig(i, v) for k, v in fields.items()} | {"_raw_keys": sorted(i)[:15]} if fields else i for i in items]

    def path(self, rule_id: str) -> Optional[dict]:
        if not is_tbd(self.cfg.get("rule_path_path")) and not is_tbd(self.cfg.get("base_url")):
            return self._get("rule_path_path", rule_id=rule_id)
        f = Path(self.cfg.get("rule_paths_file") or "config/rule-paths.yaml")
        f = f if f.is_absolute() else HERE / f
        if not f.exists():
            raise not_configured("rules.rule_path_path or rules.rule_paths_file")
        table = (yaml.safe_load(f.read_text()) or {}).get("rules", {})
        if rule_id in table:
            return table[rule_id]
        for pattern, value in table.items():
            if fnmatch.fnmatch(rule_id, pattern):
                return value
        return None
