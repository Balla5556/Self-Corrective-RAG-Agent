# Threat model

## Assets

- End-user prompts and embedded PII
- Provider credentials and tenant API keys
- System prompts, model output, and tool context
- Usage/cost telemetry and audit data

## Threats and controls

| Threat | Gateway control | Remaining risk |
| --- | --- | --- |
| Prompt injection / system-prompt extraction | Normalized rule scanner, configurable block threshold, audit event | Novel encodings and indirect injection require classifier and adversarial evaluation |
| PII sent to provider | Pattern redaction before provider invocation; raw body never persisted | Regex misses contextual or nonstandard PII; use enterprise DLP for regulated use |
| Key theft / tenant impersonation | Bearer authentication, keys excluded from Git, secret-manager deployment guidance | Use hashed/rotated keys and mTLS/OIDC in production |
| Cost abuse | Per-tenant sliding-window rate limit, token ceiling, daily budget | In-memory limiter is single-instance only; use Redis globally |
| Audit-data leakage | Store only fingerprint + metadata | Metadata may still be sensitive; enforce retention/access policy |
| Upstream outage | Typed 502, health endpoints, no silent provider substitution | Add retries/circuit breaker according to provider SLA |

## Security boundaries

The gateway is trusted to inspect the plaintext request and must run within the application’s security boundary. TLS terminates before the gateway only at a trusted load balancer. The LLM provider is an external data processor and receives only policy-approved, redacted content.

## Non-goals

This project does not claim perfect jailbreak prevention, malware detection, authorization of downstream tools, or compliance certification. It demonstrates a measurable defense-in-depth gateway and the operating practices needed to extend it responsibly.
