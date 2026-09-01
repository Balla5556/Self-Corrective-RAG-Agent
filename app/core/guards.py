from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ScanResult:
    value: str
    findings: tuple[str, ...]


_PII_PATTERNS: dict[str, re.Pattern[str]] = {
    "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "PHONE": re.compile(r"(?<!\w)(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}(?!\w)"),
    "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "CARD": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
    "API_KEY": re.compile(r"\b(?:sk|pk)-[A-Za-z0-9_-]{16,}\b"),
}

# High-signal patterns: policy rules should be supplemented by a classifier/DLP service in production.
_INJECTION_PATTERNS: tuple[tuple[str, re.Pattern[str], float], ...] = (
    (
        "instruction_override",
        re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?", re.I),
        0.95,
    ),
    (
        "system_prompt_exfiltration",
        re.compile(
            r"(?:reveal|show|print|repeat).{0,50}(?:system prompt|hidden instructions)", re.I
        ),
        0.90,
    ),
    ("role_hijack", re.compile(r"you\s+are\s+now\s+(?:dan|developer|system)", re.I), 0.80),
    ("delimiter_escape", re.compile(r"<\/?(?:system|instructions?)>|\[\/?INST\]", re.I), 0.75),
)


def redact_pii(text: str) -> ScanResult:
    findings: list[str] = []
    redacted = text
    for label, pattern in _PII_PATTERNS.items():
        redacted, count = pattern.subn(f"[REDACTED:{label}]", redacted)
        if count:
            findings.extend([label] * count)
    return ScanResult(redacted, tuple(findings))


def detect_injection(text: str) -> ScanResult:
    normalized = re.sub(r"\s+", " ", text.replace("\x00", " ")).strip()
    findings: list[str] = []
    for label, pattern, confidence in _INJECTION_PATTERNS:
        if pattern.search(normalized):
            findings.append(f"{label}:{confidence:.2f}")
    return ScanResult(normalized, tuple(findings))


def injection_score(findings: tuple[str, ...]) -> float:
    return max((float(finding.rsplit(":", 1)[1]) for finding in findings), default=0.0)


def estimate_tokens(text: str) -> int:
    """Conservative approximation used only for gateway limits/cost estimates."""
    return max(1, len(text) // 4)
