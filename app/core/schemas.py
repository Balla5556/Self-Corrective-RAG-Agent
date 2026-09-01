from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str = Field(min_length=1, max_length=100_000)


class ChatRequest(BaseModel):
    model: str = Field(default="gpt-4o-mini", min_length=1, max_length=100)
    messages: list[ChatMessage] = Field(min_length=1, max_length=100)
    temperature: float = Field(default=0, ge=0, le=2)
    max_tokens: int = Field(default=512, ge=1, le=4096)


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str


class GatewayError(Exception):
    def __init__(self, status_code: int, code: str, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message
