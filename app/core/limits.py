from __future__ import annotations

import time
from collections import defaultdict, deque

from app.core.schemas import GatewayError


class SlidingWindowLimiter:
    def __init__(self, max_requests: int, window_seconds: int = 60):
        self.max_requests, self.window_seconds = max_requests, window_seconds
        self._events: dict[str, deque[float]] = defaultdict(deque)

    def check(self, tenant: str) -> None:
        now = time.monotonic()
        events = self._events[tenant]
        while events and events[0] <= now - self.window_seconds:
            events.popleft()
        if len(events) >= self.max_requests:
            raise GatewayError(429, "rate_limited", "Tenant request rate limit exceeded.")
        events.append(now)
