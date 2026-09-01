from __future__ import annotations

import json
from pathlib import Path

from app.core.graph import build_agent


def run() -> dict[str, float]:
    cases = json.loads((Path(__file__).with_name("benchmark.json")).read_text())
    agent = build_agent()
    results = [agent.invoke({"question": case["question"], "retries": 0, "trace": []}) for case in cases]
    scores = {
        "context_precision_proxy": round(sum(r["relevance"].score for r in results) / len(results), 3),
        "faithfulness_proxy": round(sum(r["faithfulness"].score for r in results) / len(results), 3),
        "safe_answer_rate": round(sum(r["route"] != "safe_fallback" for r in results) / len(results), 3),
    }
    output = Path("artifacts/benchmark.json")
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps({"cases": len(cases), "metrics": scores}, indent=2))
    return scores


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
