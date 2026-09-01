# Architecture notes

The LangGraph state machine separates side effects (retrieval, web search, generation) from routing policy. This keeps the most consequential choices inspectable in a trace and simple to unit-test.

## Production hardening roadmap

- Replace the in-memory demo retriever with FAISS/Chroma and persistent embeddings.
- Implement Tavily search in `web_search` and record source URLs in citations.
- Send LangGraph traces to Phoenix or MLflow; scrub prompts and source data first.
- Add a gold evaluation set specific to the chosen domain and execute full RAGAS in a scheduled workflow.
- Establish release thresholds (for example, no regression in faithfulness) before deployment.
