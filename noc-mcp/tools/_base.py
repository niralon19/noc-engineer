"""Tool registry and error wrapper. Every tool returns the ToolResult envelope and never raises."""
from __future__ import annotations

import functools
import inspect
import logging
import time
from typing import Callable

from schemas.common import ToolError, ToolResult

log = logging.getLogger("noc_mcp")
REGISTRY: dict[str, Callable] = {}
WRITE_TOOLS: set[str] = set()


def tool(source: str, write: bool = False):
    def deco(fn: Callable) -> Callable:
        sig = inspect.signature(fn)

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            started = time.monotonic()
            try:
                result = fn(*args, **kwargs)
            except ToolError as e:
                result = ToolResult(False, source, error={"code": e.code, "message": e.message, "retryable": e.retryable}).as_dict()
            except Exception as e:  # noqa: BLE001 - never crash the MCP server on a bad backend reply
                log.exception("tool %s failed", fn.__name__)
                result = ToolResult(False, source, error={"code": "internal_error", "message": f"{type(e).__name__}: {e}"[:300],
                                                          "retryable": False}).as_dict()
            try:
                bound = dict(sig.bind_partial(*args, **kwargs).arguments)
            except TypeError:
                bound = dict(kwargs)
            _audit_call(fn.__name__, bound, result, time.monotonic() - started)
            return result
        REGISTRY[fn.__name__] = wrapper
        if write:
            WRITE_TOOLS.add(fn.__name__)
        return wrapper
    return deco


def as_list(value) -> list[str]:
    """Accept a list or a comma-separated string."""
    if value is None or value == "":
        return []
    if isinstance(value, str):
        return [v.strip() for v in value.split(",") if v.strip()]
    return [str(v) for v in value]


def _audit_call(name: str, kwargs: dict, result: dict, seconds: float) -> None:
    """Every invocation is audited (read and write). Audit failures never break the tool."""
    try:
        from context import get_context
        from security.policy import audit
        outcome = "ok" if result.get("ok") else f"error:{(result.get('error') or {}).get('code')}"
        audit(get_context(), name, {**kwargs, "_ms": int(seconds * 1000), "_write": name in WRITE_TOOLS}, outcome)
    except Exception:  # noqa: BLE001
        log.exception("audit failed for %s", name)
