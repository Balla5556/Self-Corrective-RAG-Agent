# LinkedIn launch post

Built **Sentinel Gateway** — an LLM security and observability layer for production GenAI applications. 🛡️

Most LLM demos focus on the model response. Production teams also need to answer: *Was sensitive data sent upstream? Did a user try to override the system prompt? Which tenant is driving cost and latency?*

Sentinel Gateway is an OpenAI-compatible FastAPI proxy that sits between an application and its LLM provider.

- Detects and blocks high-confidence prompt-injection attempts
- Redacts email, phone, SSN, card, and key-like PII before provider calls
- Enforces tenant-level authentication, request limits, token ceilings, and daily cost budgets
- Records privacy-preserving audit events—fingerprints and policy metadata, never raw prompts
- Exposes Prometheus metrics and an operations dashboard for blocks, redactions, latency, and cost
- Includes Docker, automated security tests, CI, and a formal threat model

The design choice I care most about: observability should not create a second data-leakage channel. The gateway intentionally logs *what happened* without storing customer prompts or model responses.

🔗 GitHub: [add repository link]
🎥 Demo: [add 20-second video showing PII redaction and a blocked injection]

#LLMOps #GenerativeAI #AIsecurity #MLOps #FastAPI #Observability #Python #OpenTelemetry
