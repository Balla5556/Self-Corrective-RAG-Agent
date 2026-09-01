import os
from typing import Any, Dict
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from src.state import GraphState

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# In-memory mock vector database for self-contained execution
sample_data = [
    Document(page_content="Network telemetry uses streaming protocols to export device metrics and health counters continuously."),
    Document(page_content="Anomaly detection thresholds isolate unexpected spikes in latency and packet drops from baseline operational noise."),
    Document(page_content="Retrieval-Augmented Generation (RAG) augments large language models by pulling relevant contextual data from vector databases.")
]
vector_store = FAISS.from_documents(sample_data, OpenAIEmbeddings())
retriever = vector_store.as_retriever(search_kwargs={"k": 2})

def retrieve_node(state: GraphState) -> Dict[str, Any]:
    """Retrieves context documents matching the query."""
    question = state["question"]
    docs = retriever.invoke(question)
    doc_contents = [doc.page_content for doc in docs]
    return {"documents": doc_contents, "iterations": state.get("iterations", 0)}

def grade_documents_node(state: GraphState) -> Dict[str, Any]:
    """Determines whether retrieved context documents are relevant."""
    question = state["question"]
    docs = state.get("documents", [])
    
    prompt = PromptTemplate.from_template(
        "Question: {question}\nDocuments: {docs}\n"
        "Evaluate if these documents contain relevant information to answer the question. "
        "Respond ONLY with 'yes' or 'no'."
    )
    chain = prompt | llm
    response = chain.invoke({"question": question, "docs": "\n".join(docs)})
    is_relevant = "yes" in response.content.lower().strip()
    return {"is_relevant": is_relevant}

def rewrite_query_node(state: GraphState) -> Dict[str, Any]:
    """Rewrites the query if context retrieved was insufficient."""
    question = state["question"]
    iterations = state.get("iterations", 0) + 1
    
    prompt = PromptTemplate.from_template(
        "Initial query: '{question}'\n"
        "Rewrite this query to make it clearer and better optimized for dense vector semantic search."
    )
    chain = prompt | llm
    new_query = chain.invoke({"question": question}).content.strip()
    return {"question": new_query, "iterations": iterations}

def generate_answer_node(state: GraphState) -> Dict[str, Any]:
    """Generates an accurate response strictly from retrieved context."""
    prompt = PromptTemplate.from_template(
        "You are an enterprise AI assistant. Answer the question using ONLY the provided context.\n\n"
        "Context:\n{documents}\n\n"
        "Question: {question}\n\nAnswer:"
    )
    chain = prompt | llm
    answer = chain.invoke({
        "question": state["question"],
        "documents": "\n".join(state.get("documents", []))
    }).content
    return {"generation": answer}
