#!/usr/bin/env python3
"""Run the LLM-judge vs the lexical baseline on the sensor benchmark (P1 Phase 3).

Plugs scripts/llm_judge.py into scripts/sensor_benchmark.py and prints both
sensors side by side. Needs a serving Ollama model (default qwen2.5:1.5b); if
none is reachable, it says so and exits — it never fakes a result.

Run: python scripts/run_llm_judge_eval.py
"""

from __future__ import annotations

import json

from scripts import llm_judge as lj
from scripts import sensor_benchmark as sb


def _row(r: dict) -> dict:
    t, s = r["truthfulness"], r["safety"]
    return {
        "sensor": r["sensor"],
        "truth_separation": t["separation_true_minus_false"],
        "ranking_inversion": t["ranking_inversion_rate"],
        "harm_recall": s["harm_recall"],
        "harm_recall_paraphrase": s["harm_recall_paraphrase"],
        "benign_false_positive_rate": s["benign_false_positive_rate"],
    }


def main() -> None:
    if not lj.available():
        print(
            "No serving Ollama model reachable — start one (e.g. `ollama run "
            f"{lj.DEFAULT_MODEL}`) then re-run. (No result faked.)"
        )
        return
    base = sb.run(label="baseline-lexical")
    judge = sb.run(
        truth_fn=lj.truth_score, safe_fn=lj.is_safe, label=f"llm-judge-{lj.DEFAULT_MODEL}"
    )
    print("BASELINE:", json.dumps(_row(base), ensure_ascii=False))
    print("LLMJUDGE:", json.dumps(_row(judge), ensure_ascii=False))
    print("judge over-blocked benign:", judge["safety"]["over_blocked_benign"])
    print("judge missed harm:", judge["safety"]["missed_harm"])


if __name__ == "__main__":
    main()
