#!/usr/bin/env python3
"""Aggregate de-identified shadow observations for proportional validation v0.1."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any


def _median_savings(observations: list[dict[str, Any]]) -> float | None:
    savings: list[float] = []
    for item in observations:
        routed = float((item.get("routed") or {}).get("duration_seconds", 0.0) or 0.0)
        legacy = float((item.get("legacy") or {}).get("duration_seconds", 0.0) or 0.0)
        if legacy > 0:
            savings.append((legacy - routed) / legacy)
    return round(statistics.median(savings), 4) if savings else None


def evaluate(observations: list[dict[str, Any]]) -> dict[str, Any]:
    categories = {name: 0 for name in ("documentation", "local_code", "core_boundary", "external_effect")}
    false_negatives: list[str] = []
    gate_misses: list[str] = []
    low_risk: list[dict[str, Any]] = []

    for item in observations:
        case_id = str(item.get("case_id") or "unnamed")
        level = str(item.get("content_level") or "")
        external = bool(item.get("external_effect"))
        category = "external_effect" if external else level
        if category in categories:
            categories[category] += 1
        routed_ok = bool((item.get("routed") or {}).get("ok"))
        legacy_ok = bool((item.get("legacy") or {}).get("ok"))
        if routed_ok and not legacy_ok:
            false_negatives.append(case_id)
        if bool(item.get("pii_or_owner_gate_miss")):
            gate_misses.append(case_id)
        if not external and level in {"documentation", "local_code"}:
            low_risk.append(item)

    enough_cases = len(observations) >= 12 and all(count >= 2 for count in categories.values())
    median_savings = _median_savings(low_risk)
    high_risk_false_negatives = [
        item["case_id"]
        for item in observations
        if item.get("case_id") in false_negatives
        and (item.get("external_effect") or item.get("content_level") == "core_boundary")
    ]
    thresholds = {
        "enough_cases_and_coverage": enough_cases,
        "zero_core_external_false_negatives": not high_risk_false_negatives,
        "low_risk_median_savings_at_least_50_percent": (
            median_savings is not None and median_savings >= 0.5
        ),
        "zero_pii_or_owner_gate_misses": not gate_misses,
    }
    if not enough_cases:
        conclusion = "insufficient_evidence"
    elif all(thresholds.values()):
        conclusion = "eligible_for_owner_review"
    else:
        conclusion = "inconclusive"

    return {
        "protocol_version": "proportional-validation-pilot.v0.1",
        "adoption_status": "experimental_shadow",
        "observation_count": len(observations),
        "category_counts": categories,
        "false_negative_case_ids": false_negatives,
        "high_risk_false_negative_case_ids": high_risk_false_negatives,
        "pii_or_owner_gate_miss_case_ids": gate_misses,
        "low_risk_median_time_savings_ratio": median_savings,
        "thresholds": thresholds,
        "conclusion": conclusion,
        "ratification_rule": "Only the owner may replace the current full pre-push gate.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate proportional-validation shadow receipts.")
    parser.add_argument("observations", type=Path)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    source = json.loads(args.observations.read_text(encoding="utf-8"))
    observations = source.get("observations", source) if isinstance(source, dict) else source
    if not isinstance(observations, list):
        raise SystemExit("observations must be a JSON array or an object containing observations")
    payload = evaluate(observations)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

