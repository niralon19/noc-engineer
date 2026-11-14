"""Small HTTP layer used by every client: timeouts, bounded body, typed errors, no secret logging.

Tests replace Http with a fake that implements request().
"""
from __future__ import annotations

from typing import Any, Optional

import json as _json

import requests

from schemas.common import ToolError

MAX_BODY_BYTES = 5_000_000


class Http:
    def __init__(self, timeout: float = 20.0, verify: Any = True):
        self.timeout, self.verify = timeout, verify
        self.session = requests.Session()

    def request(self, method: str, url: str, *, params: Optional[dict] = None, json: Any = None,
                headers: Optional[dict] = None, auth: Any = None, timeout: Optional[float] = None,
                verify: Any = None) -> Any:
        try:
            r = self.session.request(method, url, params=params, json=json, headers=headers, auth=auth,
                                     timeout=timeout or self.timeout, verify=self.verify if verify is None else verify,
                                     stream=True)
        except requests.Timeout as e:
            raise ToolError("backend_timeout", f"timeout calling {_host(url)}", retryable=True) from e
        except requests.RequestException as e:
            raise ToolError("backend_unreachable", f"cannot reach {_host(url)}: {type(e).__name__}", retryable=True) from e
        body = r.raw.read(MAX_BODY_BYTES + 1, decode_content=True)
        if len(body) > MAX_BODY_BYTES:
            raise ToolError("result_too_large", f"{_host(url)} returned more than {MAX_BODY_BYTES} bytes; narrow the query")
        if r.status_code in (401, 403):
            raise ToolError("backend_auth", f"{_host(url)} rejected credentials ({r.status_code})")
        if r.status_code == 404:
            raise ToolError("not_found", f"{_host(url)}: not found")
        if r.status_code >= 400:
            raise ToolError("backend_error", f"{_host(url)} returned {r.status_code}: {body[:300].decode(errors='replace')}",
                            retryable=r.status_code >= 500)
        if not body:
            return None
        try:
            return _json.loads(body)
        except ValueError:
            return body.decode(errors="replace")

    def get(self, url: str, **kw: Any) -> Any:
        return self.request("GET", url, **kw)

    def post(self, url: str, **kw: Any) -> Any:
        return self.request("POST", url, **kw)


def _host(url: str) -> str:
    return url.split("/")[2] if "://" in url else url


def bearer(token: Optional[str]) -> dict:
    return {"Authorization": f"Bearer {token}"} if token else {}
