from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, TypedDict


@dataclass(frozen=True)
class Document:
    page_content: str
    source: str
    chunk_id: str


@dataclass(frozen=True)
class Grade:
    score: float
    rationale: str


@dataclass(frozen=True)
class Citation:
    source: str
    chunk_id: str
    excerpt: str


@dataclass
class TraceEvent:
    step: str
    detail: str


class AgentState(TypedDict, total=False):
    question: str
    rewritten_question: str
    documents: list[Document]
    relevance: Grade
    answer: str
    citations: list[Citation]
    faithfulness: Grade
    route: Literal["generate", "rewrite", "web_search", "safe_fallback"]
    retries: int
    trace: list[TraceEvent]


def trace(state: AgentState, step: str, detail: str) -> list[TraceEvent]:
    return [*state.get("trace", []), TraceEvent(step, detail)]
