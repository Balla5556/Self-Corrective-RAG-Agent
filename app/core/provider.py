from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.core.schemas import ChatMessage


@dataclass(frozen=True)
class ProviderResponse:
    content: str
    input_tokens: int
    output_tokens: int
    model: str


class LLMProvider:
    async def complete(
        self, messages: list[ChatMessage], model: str, max_tokens: int
    ) -> ProviderResponse:
        raise NotImplementedError


class LocalProvider(LLMProvider):
    """Credential-free deterministic provider, intentionally marked in every response."""

    async def complete(
        self, messages: list[ChatMessage], model: str, max_tokens: int
    ) -> ProviderResponse:
        prompt = messages[-1].content
        content = f"[Sentinel local demo] Request accepted after policy checks: {prompt[:300]}"
        return ProviderResponse(
            content, max(1, len(prompt) // 4), max(1, len(content) // 4), "sentinel-local"
        )


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def complete(
        self, messages: list[ChatMessage], model: str, max_tokens: int
    ) -> ProviderResponse:
        payload = {
            "model": model,
            "messages": [m.model_dump() for m in messages],
            "max_tokens": max_tokens,
        }
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json=payload,
                )
                response.raise_for_status()
        except httpx.HTTPError as error:
            raise RuntimeError("Upstream LLM provider request failed") from error
        body = response.json()
        usage = body.get("usage", {})
        return ProviderResponse(
            body["choices"][0]["message"]["content"],
            usage.get("prompt_tokens", 0),
            usage.get("completion_tokens", 0),
            body.get("model", model),
        )
