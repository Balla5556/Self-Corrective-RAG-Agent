from __future__ import annotations

import re
from pathlib import Path

from app.core.models import Document


class HybridRetriever:
    """Dependency-light hybrid retriever for a portable demo and deterministic tests.

    Swap this class for a FAISS embedding index in production; its public interface
    intentionally remains a simple `search(query, k)` method.
    """

    def __init__(self, documents: list[Document]):
        self.documents = documents

    @classmethod
    def from_directory(cls, directory: str | Path) -> "HybridRetriever":
        docs: list[Document] = []
        for path in sorted(Path(directory).glob("*.md")):
            content = path.read_text(encoding="utf-8")
            chunks = [part.strip() for part in content.split("\n\n") if part.strip()]
            docs.extend(
                Document(chunk, path.name, f"{path.stem}-{index}")
                for index, chunk in enumerate(chunks)
            )
        return cls(docs)

    def search(self, query: str, k: int = 4) -> list[Document]:
        query_terms = set(_terms(query))
        scored = []
        for document in self.documents:
            terms = set(_terms(document.page_content))
            # lexical score is a reliable fallback for exact technical vocabulary
            score = len(query_terms & terms) / max(1, len(query_terms))
            scored.append((score, document))
        return [document for score, document in sorted(scored, reverse=True, key=lambda x: x[0])[:k] if score]


def _terms(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_-]+", text.lower())
