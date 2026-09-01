from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    api_keys: dict[str, str]
    database_path: str
    rate_limit_per_minute: int
    daily_budget_usd: float
    max_input_tokens: int
    injection_threshold: float
    openai_api_key: str | None
    openai_model: str

    @classmethod
    def from_env(cls) -> Settings:
        pairs = os.getenv("SENTINEL_API_KEYS", "demo-key:demo").split(",")
        api_keys = dict(pair.strip().split(":", 1) for pair in pairs if ":" in pair)
        return cls(
            api_keys=api_keys,
            database_path=os.getenv("SENTINEL_DATABASE_PATH", "./data/sentinel.db"),
            rate_limit_per_minute=int(os.getenv("SENTINEL_RATE_LIMIT_PER_MINUTE", "60")),
            daily_budget_usd=float(os.getenv("SENTINEL_DAILY_BUDGET_USD", "5")),
            max_input_tokens=int(os.getenv("SENTINEL_MAX_INPUT_TOKENS", "4000")),
            injection_threshold=float(os.getenv("SENTINEL_INJECTION_THRESHOLD", "0.70")),
            openai_api_key=os.getenv("OPENAI_API_KEY") or None,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        )
