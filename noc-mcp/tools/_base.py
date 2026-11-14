"""Tool registry and error wrapper. Every tool returns the ToolResult envelope and never raises."""
from __future__ import annotations

import functools
import logging
from typing import Callable

from schemas.common import ToolError, ToolResult

log = logging.getLogger("noc_mcp")
REGISTRY: dict[str, Callable] = {}
WRITE_TOOLS: set[str] = set()


def tool(source: str, write: bool = False):
    def deco(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except ToolError as e:
                return ToolResult(False, source, error={"code": e.code, "message": e.message, "retryable": e.retryable}).as_dict()
            except Exception as e:  # noqa: BLE001 - never crash the MCP server on a bad backend reply
                log.exception("tool %s failed", fn.__name__)
                return ToolResult(False, source, error={"code": "internal_error", "message": f"{type(e).__name__}: {e}"[:300],
                                                        "retryable": False}).as_dict()
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
