# Operations runbook

## Alerts to configure

- `sentinel_requests_total{decision="blocked"}` spikes: inspect new policy patterns and client behavior.
- `sentinel_requests_total{decision="error"}` rises: check provider status, credentials, and egress.
- p95 `sentinel_request_latency_seconds` breaches your application SLO.
- Daily per-tenant cost approaches its budget: notify the tenant before blocking.

## Incident response

1. Capture the correlation ID returned in `x-sentinel-request-id`.
2. Query the audit ledger by request ID; do not ask operators to collect raw customer prompts.
3. Determine whether the decision was policy, limit, or upstream-related.
4. If a pattern bypassed policy, add a regression test before changing a rule or classifier threshold.
5. Rotate any credential exposed outside the expected boundary.

## Data retention

Set an organization-specific retention schedule for audit metadata. Never log raw prompts or responses merely to ease debugging. If content review is essential, use a separately authorized, encrypted, access-controlled workflow.
