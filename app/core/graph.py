from __future__ import annotations

import os
from pathlib import Path

from langgraph.graph import END, START, StateGraph

from app.core.models import AgentState, trace
from app.core.retrieval import HybridRetriever
from app.core.services import (
    generate_answer,
    grade_faithfulness,
    grade_relevance,
    rewrite_query,
    web_search,
)

DEFAULT_CORPUS = Path(__file__).parents[2] / "data" / "knowledge"


def build_agent(retriever: HybridRetriever | None = None):
    retriever = retriever or HybridRetriever.from_directory(DEFAULT_CORPUS)
    threshold = float(os.getenv("RELEVANCE_THRESHOLD", "0.35"))

    def rewrite(state: AgentState):
        question = rewrite_query(state["question"])
        return {"rewritten_question": question, "trace": trace(state, "rewrite", question)}

    def retrieve(state: AgentState):
        docs = retriever.search(state["rewritten_question"])
        return {"documents": docs, "trace": trace(state, "retrieve", f"Retrieved {len(docs)} chunks")}

    def relevance(state: AgentState):
        result = grade_relevance(state["rewritten_question"], state["documents"])
        return {"relevance": result, "trace": trace(state, "relevance", result.rationale)}

    def choose(state: AgentState):
        if state["relevance"].score >= threshold:
            return "generate"
        if state.get("retries", 0) < 1:
            return "rewrite"
        return "web_search"

    def retry(state: AgentState):
        return {"retries": state.get("retries", 0) + 1, "trace": trace(state, "retry", "Low relevance; retrying query")}

    def search_web(state: AgentState):
        docs = web_search(state["rewritten_question"])
        return {"documents": [*state.get("documents", []), *docs], "route": "web_search", "trace": trace(state, "web_search", f"Added {len(docs)} web sources")}

    def generate(state: AgentState):
        answer, citations = generate_answer(state["question"], state["documents"])
        return {"answer": answer, "citations": citations, "route": state.get("route", "generate"), "trace": trace(state, "generate", "Generated evidence-constrained response")}

    def faithfulness(state: AgentState):
        result = grade_faithfulness(state["answer"], state["documents"])
        return {"faithfulness": result, "trace": trace(state, "faithfulness", result.rationale)}

    def final_route(state: AgentState):
        return "safe_fallback" if state["faithfulness"].score < 0.2 else "end"

    def safe_fallback(state: AgentState):
        return {"answer": "I can’t verify a sufficiently grounded answer from the available sources.", "route": "safe_fallback", "trace": trace(state, "safe_fallback", "Blocked an insufficiently grounded answer")}

    graph = StateGraph(AgentState)
    for name, node in [("rewrite", rewrite), ("retrieve", retrieve), ("relevance", relevance), ("retry", retry), ("web_search", search_web), ("generate", generate), ("faithfulness", faithfulness), ("safe_fallback", safe_fallback)]:
        graph.add_node(name, node)
    graph.add_edge(START, "rewrite")
    graph.add_edge("rewrite", "retrieve")
    graph.add_edge("retrieve", "relevance")
    graph.add_conditional_edges("relevance", choose, {"generate": "generate", "rewrite": "retry", "web_search": "web_search"})
    graph.add_edge("retry", "rewrite")
    graph.add_edge("web_search", "generate")
    graph.add_edge("generate", "faithfulness")
    graph.add_conditional_edges("faithfulness", final_route, {"safe_fallback": "safe_fallback", "end": END})
    graph.add_edge("safe_fallback", END)
    return graph.compile()
