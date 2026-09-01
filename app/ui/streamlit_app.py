from __future__ import annotations

import streamlit as st

from app.core.graph import build_agent

st.set_page_config(page_title="SentinelRAG", page_icon="🛡️", layout="wide")
st.title("🛡️ SentinelRAG")
st.caption("A self-corrective RAG agent that surfaces its evidence and confidence gates.")

if "agent" not in st.session_state:
    st.session_state.agent = build_agent()

question = st.text_input("Ask about the knowledge base", placeholder="How does the faithfulness gate work?")
if st.button("Run agent", type="primary", disabled=not question):
    with st.spinner("Retrieving, grading, and grounding…"):
        result = st.session_state.agent.invoke({"question": question, "retries": 0, "trace": []})
    st.subheader("Answer")
    st.write(result["answer"])
    left, middle, right = st.columns(3)
    left.metric("Route", result.get("route", "generate"))
    middle.metric("Context relevance", f"{result['relevance'].score:.0%}")
    right.metric("Faithfulness", f"{result['faithfulness'].score:.0%}")
    with st.expander("Evidence & citations", expanded=True):
        for citation in result.get("citations", []):
            st.markdown(f"**{citation.source} · {citation.chunk_id}**  \n{citation.excerpt}")
    with st.expander("Agent trace"):
        for event in result["trace"]:
            st.write(f"`{event.step}` — {event.detail}")
