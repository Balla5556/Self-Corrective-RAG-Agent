from __future__ import annotations

import os
from collections.abc import Callable

from app.core.models import Citation, Document, Grade


def rewrite_query(question: str) -> str:
    """Conservative rewrite; preserves identifiers rather than over-transforming queries."""
    return " ".join(question.strip().split())


def grade_relevance(question: str, documents: list[Document]) -> Grade:
    terms = {word.lower() for word in question.split() if len(word) > 2}
    corpus = " ".join(doc.page_content.lower() for doc in documents)
    overlap = sum(term in corpus for term in terms)
    score = overlap / max(1, len(terms))
    return Grade(round(score, 2), f"{overlap}/{len(terms)} meaningful query terms found in evidence.")


def generate_answer(question: str, documents: list[Document]) -> tuple[str, list[Citation]]:
    """Grounded local baseline. Replace with an LLM when OPENAI_API_KEY is present."""
    citations = [Citation(d.source, d.chunk_id, d.page_content[:240]) for d in documents]
    if not documents:
        return "I don't have enough verified context to answer that question.", []
    evidence = " ".join(d.page_content for d in documents)
    if os.getenv("OPENAI_API_KEY"):
        return _openai_answer(question, evidence), citations
    return f"Based on the retrieved evidence: {evidence[:700]}", citations


def grade_faithfulness(answer: str, documents: list[Document]) -> Grade:
    if not documents:
        return Grade(0.0, "No retrieved evidence was available.")
    evidence_terms = {word.lower() for d in documents for word in d.page_content.split() if len(word) > 3}
    answer_terms = {word.lower().strip(".,:;!?()") for word in answer.split() if len(word) > 3}
    score = len(answer_terms & evidence_terms) / max(1, len(answer_terms))
    return Grade(round(score, 2), "Lexical grounding proxy; use RAGAS for full LLM evaluation.")


def web_search(query: str) -> list[Document]:
    """A safe stub that makes absent credentials visible instead of pretending to browse."""
    if not os.getenv("TAVILY_API_KEY"):
        return []
    # Integration boundary: wire Tavily/LangChain here without changing graph behavior.
    return []


def _openai_answer(question: str, evidence: str) -> str:
    from langchain_openai import ChatOpenAI

    prompt = (
        "Answer only from the supplied evidence. If it is insufficient, say so plainly. "
        f"\n\nQuestion: {question}\n\nEvidence:\n{evidence}"
    )
    return ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0).invoke(prompt).content
