# SentinelRAG knowledge base

The faithfulness gate evaluates whether the answer is supported by retrieved context. When evidence is insufficient, the system returns a transparent safe fallback instead of presenting an unsupported answer.

The document grader computes a relevance score after hybrid retrieval. If the score falls below the configured relevance threshold, the agent retries a conservative query rewrite once. If evidence remains weak, it routes to the web search fallback.

Hybrid retrieval combines vector similarity and lexical BM25-style matching. Exact product names, error codes, and uncommon technical terms benefit from lexical matching, while embeddings capture semantic similarity.

RAGAS evaluation tracks context precision, faithfulness, and answer relevance. Proxy scores are appropriate for fast offline CI, while full RAGAS evaluation should be run with an LLM judge before reporting results publicly.
