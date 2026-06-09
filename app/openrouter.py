import json
from typing import AsyncIterator

import httpx

from app.config import DEFAULT_MODEL, ZAI_API_KEY, ZAI_BASE_URL

_client: httpx.AsyncClient | None = None


class ZAIError(Exception):
    pass


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            timeout=httpx.Timeout(300.0, connect=15.0),
            limits=httpx.Limits(max_connections=50, max_keepalive_connections=20),
        )
    return _client


def _headers() -> dict[str, str]:
    if not ZAI_API_KEY:
        raise ZAIError("ZAI_API_KEY is not set. Add it to your .env file.")
    return {
        "Authorization": f"Bearer {ZAI_API_KEY}",
        "Content-Type": "application/json",
        "Accept-Language": "en-US,en",
    }


async def stream_chat(
    messages: list[dict[str, str]],
    model: str | None = None,
) -> AsyncIterator[str]:
    payload = {
        "model": model or DEFAULT_MODEL,
        "messages": messages,
        "stream": True,
        "temperature": 0.7,
        "max_tokens": 2048,
    }

    client = _get_client()
    try:
        async with client.stream(
            "POST",
            f"{ZAI_BASE_URL.rstrip('/')}/chat/completions",
            headers=_headers(),
            json=payload,
        ) as response:
            if response.status_code != 200:
                body = await response.aread()
                raise ZAIError(f"Z.AI error {response.status_code}: {body.decode()}")

            async for line in response.aiter_lines():
                if not line:
                    continue
                if not line.startswith("data: "):
                    continue
                data = line[6:]
                if data.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                except json.JSONDecodeError:
                    continue
                delta = chunk.get("choices", [{}])[0].get("delta", {})
                content = delta.get("content")
                if content:
                    yield content
    except Exception as e:
        raise ZAIError(f"Connection failed: {str(e)}")

async def generate_chat_title(message_content: str) -> str:
    payload = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": "You are a title generator. Generate a very short (3 to 5 words max) descriptive title for this message. Do not use quotes or punctuation."},
            {"role": "user", "content": message_content[:1000]}
        ],
        "temperature": 0.5,
        "max_tokens": 15,
    }
    client = _get_client()
    try:
        response = await client.post(
            f"{ZAI_BASE_URL.rstrip('/')}/chat/completions",
            headers=_headers(),
            json=payload,
        )
        if response.status_code == 200:
            data = response.json()
            title = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            return title.strip('"\'*')[:80]
    except Exception:
        pass
    return "New chat"
