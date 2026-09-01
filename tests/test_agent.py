from app.core.graph import build_agent
from app.core.models import Document
from app.core.retrieval import HybridRetriever


def test_grounded_question_generates_answer():
    retriever = HybridRetriever([Document("The faithfulness gate blocks unsupported answers.", "test.md", "1")])
    result = build_agent(retriever).invoke({"question": "What does the faithfulness gate block?", "retries": 0, "trace": []})
    assert result["route"] == "generate"
    assert result["citations"]


def test_unknown_question_uses_safe_fallback():
    retriever = HybridRetriever([])
    result = build_agent(retriever).invoke({"question": "Who won the lunar marathon?", "retries": 0, "trace": []})
    assert result["route"] == "safe_fallback"
    assert result["retries"] == 1
