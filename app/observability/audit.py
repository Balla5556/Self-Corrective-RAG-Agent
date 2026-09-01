from __future__ import annotations

import hashlib
import sqlite3
import threading
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class AuditEvent:
    request_id: str
    tenant: str
    decision: str
    reason: str | None
    pii_count: int
    injection_score: float
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    latency_ms: int
    prompt_fingerprint: str


class AuditLedger:
    def __init__(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.path, self.lock = path, threading.Lock()
        with self._connect() as connection:
            connection.execute("""CREATE TABLE IF NOT EXISTS audit_events (
                created_at TEXT NOT NULL, request_id TEXT PRIMARY KEY, tenant TEXT NOT NULL,
                decision TEXT NOT NULL, reason TEXT, pii_count INTEGER NOT NULL,
                injection_score REAL NOT NULL, input_tokens INTEGER NOT NULL, output_tokens INTEGER NOT NULL,
                estimated_cost_usd REAL NOT NULL, latency_ms INTEGER NOT NULL, prompt_fingerprint TEXT NOT NULL
            )""")

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path, check_same_thread=False)

    @staticmethod
    def fingerprint(prompt: str) -> str:
        return hashlib.sha256(prompt.encode()).hexdigest()

    def write(self, event: AuditEvent) -> None:
        with self.lock, self._connect() as connection:
            connection.execute(
                "INSERT INTO audit_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    datetime.now(UTC).isoformat(),
                    event.request_id,
                    event.tenant,
                    event.decision,
                    event.reason,
                    event.pii_count,
                    event.injection_score,
                    event.input_tokens,
                    event.output_tokens,
                    event.estimated_cost_usd,
                    event.latency_ms,
                    event.prompt_fingerprint,
                ),
            )

    def daily_cost(self, tenant: str) -> float:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT COALESCE(SUM(estimated_cost_usd), 0) FROM audit_events WHERE tenant = ? AND created_at >= date('now')",
                (tenant,),
            ).fetchone()
        return float(row[0])

    def recent(self, limit: int = 100) -> list[dict[str, object]]:
        with self._connect() as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                "SELECT * FROM audit_events ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(row) for row in rows]
