from typing import List, TypedDict

class GraphState(TypedDict):
    """Represents the state of the Self-Corrective RAG agent graph."""
    question: str
    generation: str
    documents: List[str]
    is_relevant: bool
    iterations: int
