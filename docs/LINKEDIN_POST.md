# LinkedIn launch post

Built a production-minded **Self-Corrective Agentic RAG** system with automated evaluation. 🛡️

Standard RAG can sound confident even when retrieved context is thin or irrelevant. I built SentinelRAG to make that failure mode visible—and correctable.

Key architecture decisions:

- **Corrective routing:** grades retrieved evidence, retries a conservative query rewrite, then escalates to web search only when context remains weak.
- **Hybrid retrieval:** combines semantic and lexical signals so technical identifiers and concepts are both retrievable.
- **Faithfulness gate:** blocks answers that cannot be grounded in the retrieved sources and returns a transparent fallback instead.
- **Evaluation-first workflow:** benchmark harness captures context precision, faithfulness, and answer relevance proxies locally, with a RAGAS integration point for LLM-as-a-judge evaluation.
- **MLOps baseline:** Dockerized Streamlit UI, evidence/citation display, typed LangGraph state, offline unit tests, and GitHub Actions CI.

📊 On my domain-specific benchmark, the corrective workflow achieved **[X]% context-precision improvement** and **[Y]% reduction in unsupported answers** versus the baseline. *(Replace only after running your benchmark.)*

The part I’m happiest with: the agent does not merely produce an answer—it exposes the route, evidence, relevance score, and faithfulness decision that led to it.

🔗 GitHub: [repository link]
💻 Demo: [deployed Streamlit / Hugging Face Space link]

#GenerativeAI #RAG #AgenticAI #MLOps #LangGraph #Python #Docker #MachineLearning

## Suggested asset

Record a 15-second screen capture: one grounded query, one out-of-corpus query that triggers the fallback, then expand the trace and citations. Lead the post with that video or a screenshot of the trace—use the Mermaid architecture from the README as the carousel's second slide.
