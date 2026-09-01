from langgraph.graph import END, StateGraph
from src.state import GraphState
from src.nodes import (
    retrieve_node,
    grade_documents_node,
    rewrite_query_node,
    generate_answer_node
)

def decide_next_step(state: GraphState) -> str:
    """Conditional routing: generate answer or rewrite query up to 2 times."""
    if state.get("is_relevant", False) or state.get("iterations", 0) >= 2:
        return "generate"
    return "rewrite"

workflow = StateGraph(GraphState)

workflow.add_node("retrieve", retrieve_node)
workflow.add_node("grade_docs", grade_documents_node)
workflow.add_node("rewrite", rewrite_query_node)
workflow.add_node("generate", generate_answer_node)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "grade_docs")
workflow.add_conditional_edges(
    "grade_docs",
    decide_next_step,
    {
        "generate": "generate",
        "rewrite": "rewrite"
    }
)
workflow.add_edge("rewrite", "retrieve")
workflow.add_edge("generate", END)

app = workflow.compile()
