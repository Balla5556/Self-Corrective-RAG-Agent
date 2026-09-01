from __future__ import annotations

import time
from uuid import uuid4

from app.core.config import Settings
from app.core.guards import detect_injection, estimate_tokens, injection_score, redact_pii
from app.core.limits import SlidingWindowLimiter
from app.core.provider import LLMProvider, LocalProvider, OpenAIProvider, ProviderResponse
from app.core.schemas import ChatRequest, GatewayError
from app.observability.audit import AuditEvent, AuditLedger
from app.observability.metrics import ESTIMATED_COST, LATENCY, PII_REDACTIONS, REQUESTS


class GatewayService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.ledger = AuditLedger(settings.database_path)
        self.limiter = SlidingWindowLimiter(settings.rate_limit_per_minute)
        self.provider: LLMProvider = (
            OpenAIProvider(settings.openai_api_key) if settings.openai_api_key else LocalProvider()
        )

    async def process(self, tenant: str, request: ChatRequest) -> tuple[ProviderResponse, str, int]:
        request_id, started = str(uuid4()), time.perf_counter()
        raw_prompt = "\n".join(message.content for message in request.messages)
        fingerprint = self.ledger.fingerprint(raw_prompt)
        input_tokens = estimate_tokens(raw_prompt)
        pii = redact_pii(raw_prompt)
        injection = detect_injection(raw_prompt)
        score = injection_score(injection.findings)
        try:
            self.limiter.check(tenant)
            if input_tokens > self.settings.max_input_tokens:
                raise GatewayError(
                    413, "input_too_large", "Input exceeds the configured token ceiling."
                )
            estimated_request_cost = (input_tokens + request.max_tokens) * 0.000001
            if (
                self.ledger.daily_cost(tenant) + estimated_request_cost
                > self.settings.daily_budget_usd
            ):
                raise GatewayError(
                    429, "budget_exceeded", "Tenant daily estimated-cost budget exceeded."
                )
            if score >= self.settings.injection_threshold:
                raise GatewayError(
                    403, "policy_violation", "Prompt blocked by injection-defense policy."
                )
            redacted_messages = []
            for message in request.messages:
                result = redact_pii(message.content)
                redacted_messages.append(message.model_copy(update={"content": result.value}))
            response = await self.provider.complete(
                redacted_messages, request.model, request.max_tokens
            )
            cost = (response.input_tokens + response.output_tokens) * 0.000001
            self._audit(
                request_id,
                tenant,
                "allowed",
                None,
                len(pii.findings),
                score,
                response.input_tokens,
                response.output_tokens,
                cost,
                fingerprint,
                started,
            )
            for finding in pii.findings:
                PII_REDACTIONS.labels(type=finding).inc()
            ESTIMATED_COST.labels(tenant=tenant).inc(cost)
            return response, request_id, len(pii.findings)
        except GatewayError as error:
            self._audit(
                request_id,
                tenant,
                "blocked",
                error.code,
                len(pii.findings),
                score,
                input_tokens,
                0,
                0.0,
                fingerprint,
                started,
            )
            raise
        except RuntimeError as error:
            self._audit(
                request_id,
                tenant,
                "error",
                "upstream_failure",
                len(pii.findings),
                score,
                input_tokens,
                0,
                0.0,
                fingerprint,
                started,
            )
            raise GatewayError(502, "upstream_failure", "LLM provider unavailable.") from error

    def _audit(
        self,
        request_id: str,
        tenant: str,
        decision: str,
        reason: str | None,
        pii_count: int,
        score: float,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        fingerprint: str,
        started: float,
    ) -> None:
        latency = int((time.perf_counter() - started) * 1000)
        self.ledger.write(
            AuditEvent(
                request_id,
                tenant,
                decision,
                reason,
                pii_count,
                score,
                input_tokens,
                output_tokens,
                cost,
                latency,
                fingerprint,
            )
        )
        REQUESTS.labels(decision=decision, tenant=tenant).inc()
        LATENCY.observe(latency / 1000)
