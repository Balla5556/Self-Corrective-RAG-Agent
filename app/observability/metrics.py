from prometheus_client import Counter, Histogram

REQUESTS = Counter("sentinel_requests_total", "Gateway requests", ["decision", "tenant"])
PII_REDACTIONS = Counter("sentinel_pii_redactions_total", "PII values redacted", ["type"])
LATENCY = Histogram("sentinel_request_latency_seconds", "Gateway request latency")
ESTIMATED_COST = Counter("sentinel_estimated_cost_usd_total", "Estimated LLM cost", ["tenant"])
