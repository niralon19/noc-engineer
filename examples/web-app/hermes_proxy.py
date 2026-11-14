"""Backend proxy: lets your web app's chat talk to Hermes without exposing API_SERVER_KEY to the browser.

FOR THE LLM / DEVELOPER OPENING THIS FILE
Drop this router into the app's existing Python backend (FastAPI). It streams Hermes' answer back to the UI.
- Hermes API: OpenAI-compatible, POST {HERMES_URL}/v1/chat/completions, Bearer API_SERVER_KEY.
- Continuity: X-Hermes-Session-Id = the UI conversation id (one per chat thread);
  X-Hermes-Session-Key = the logged-in user (scopes long-term memory per user).
- Idempotency-Key per user message so a network retry does not run the investigation twice.
- Auth: use the app's own login; only allowed team members may reach this route.
Requires: fastapi, httpx. Config from env: HERMES_URL (k8s Service/Route), HERMES_API_KEY (= API_SERVER_KEY).
"""
import os
import uuid

import httpx
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

HERMES_URL = os.environ["HERMES_URL"].rstrip("/")          # e.g. http://hermes-noc-engineer:8642
HERMES_API_KEY = os.environ["HERMES_API_KEY"]
MODEL = os.environ.get("HERMES_MODEL_NAME", "noc-engineer")  # = gateway.api_server.model_name

router = APIRouter()


def current_user(request: Request) -> str:
    """Replace with the app's real auth dependency."""
    raise NotImplementedError


@router.post("/api/noc-agent/chat")
async def chat(request: Request, user: str = Depends(current_user)):
    body = await request.json()            # {"conversation_id": "...", "messages": [{"role": "user", "content": "..."}]}
    headers = {
        "Authorization": f"Bearer {HERMES_API_KEY}",
        "X-Hermes-Session-Id": body["conversation_id"],
        "X-Hermes-Session-Key": f"user:{user}",
        "Idempotency-Key": body.get("message_id") or str(uuid.uuid4()),
    }
    payload = {"model": MODEL, "messages": body["messages"], "stream": True}

    async def relay():
        async with httpx.AsyncClient(timeout=httpx.Timeout(600, connect=10)) as client:
            async with client.stream("POST", f"{HERMES_URL}/v1/chat/completions",
                                     json=payload, headers=headers) as r:
                r.raise_for_status()
                async for line in r.aiter_lines():
                    if line.startswith(":"):       # keepalive comments
                        continue
                    yield line + "\n"

    return StreamingResponse(relay(), media_type="text/event-stream")
