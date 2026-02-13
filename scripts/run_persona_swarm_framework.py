"""Run persona swarm framework evaluation and publish latest status artifact."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

if TYPE_CHECKING:
    from tonesoul.council.swarm_framework import SwarmAgentSignal

DEFAULT_OUT_PATH = Path("docs/status/persona_swarm_framework_latest.json")


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _default_signal_payloads() -> list[dict[str, Any]]:
    return [
        {
            "agent_id": "guardian-1",
            "role": "guardian",
            "vote": "approve",
            "confidence": 0.91,
            "safety_score": 0.97,
            "quality_score": 0.80,
            "novelty_score": 0.30,
            "latency_ms": 950,
            "token_cost": 420,
        },
        {
            "agent_id": "engineer-1",
            "role": "engineer",
            "vote": "approve",
            "confidence": 0.86,
            "safety_score": 0.84,
            "quality_score": 0.88,
            "novelty_score": 0.45,
            "latency_ms": 1380,
            "token_cost": 690,
        },
        {
            "agent_id": "critic-1",
            "role": "critic",
            "vote": "revise",
            "confidence": 0.74,
            "safety_score": 0.89,
            "quality_score": 0.86,
            "novelty_score": 0.78,
            "latency_ms": 1600,
            "token_cost": 770,
        },
        {
            "agent_id": "analyst-1",
            "role": "analyst",
            "vote": "approve",
            "confidence": 0.77,
            "safety_score": 0.90,
            "quality_score": 0.82,
            "novelty_score": 0.50,
            "latency_ms": 1490,
            "token_cost": 740,
        },
    ]


def _parse_input_payload(payload: Any) -> tuple[list[SwarmAgentSignal], str | None]:
    from tonesoul.council.swarm_framework import SwarmAgentSignal, normalize_swarm_decision

    records: Any
    final_decision: str | None = None

    if isinstance(payload, list):
        records = payload
    elif isinstance(payload, dict):
        records = payload.get("signals")
        value = payload.get("final_decision")
        final_decision = (
            normalize_swarm_decision(value, field_name="final_decision")
            if isinstance(value, str)
            else None
        )
    else:
        raise ValueError("input payload must be a list or object")

    if not isinstance(records, list) or not records:
        raise ValueError("input payload must contain a non-empty signals list")

    signals = [SwarmAgentSignal.from_dict(item) for item in records]
    return signals, final_decision


def _load_signals(input_path: Path | None) -> tuple[list[SwarmAgentSignal], str | None]:
    if input_path is None:
        return _parse_input_payload(_default_signal_payloads())

    payload = json.loads(input_path.read_text(encoding="utf-8"))
    return _parse_input_payload(payload)


def _gate_snapshot(evaluation: dict[str, Any]) -> dict[str, Any]:
    metrics = evaluation.get("metrics", {})
    decision_support = float(evaluation.get("decision_support", 0.0))

    criteria = {
        "min_safety_pass_rate": 0.80,
        "min_swarm_score": 0.72,
        "min_decision_support": 0.60,
        "max_token_latency_cost_index": 0.75,
    }

    checks = {
        "safety_pass_rate": float(metrics.get("safety_pass_rate", 0.0))
        >= criteria["min_safety_pass_rate"],
        "swarm_score": float(metrics.get("swarm_score", 0.0)) >= criteria["min_swarm_score"],
        "decision_support": decision_support >= criteria["min_decision_support"],
        "token_latency_cost_index": float(metrics.get("token_latency_cost_index", 1.0))
        <= criteria["max_token_latency_cost_index"],
    }
    failed = [name for name, ok in checks.items() if not ok]
    return {
        "passed": not failed,
        "criteria": criteria,
        "checks": checks,
        "failed_checks": failed,
    }


def _build_payload(
    *,
    source_input: str,
    signal_count: int,
    evaluation: dict[str, Any],
    readiness_gate: dict[str, Any],
) -> dict[str, Any]:
    return {
        "generated_at": _iso_now(),
        "source": "scripts/run_persona_swarm_framework.py",
        "input": {
            "source": source_input,
            "signal_count": signal_count,
        },
        "evaluation": evaluation,
        "readiness_gate": readiness_gate,
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _emit(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run persona swarm framework evaluation.")
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument(
        "--input",
        default=None,
        help="Optional JSON path. Supports list[signal] or {signals:[...], final_decision}.",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_OUT_PATH),
        help="Output JSON artifact path.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when readiness gate fails.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(args.repo_root).resolve()
    input_path = (repo_root / args.input).resolve() if args.input else None
    out_path_raw = Path(args.out)
    out_path = out_path_raw if out_path_raw.is_absolute() else (repo_root / out_path_raw).resolve()

    try:
        from tonesoul.council.swarm_framework import PersonaSwarmFramework

        signals, final_decision = _load_signals(input_path)
        framework = PersonaSwarmFramework()
        result = framework.evaluate(signals, final_decision=final_decision)
        evaluation = result.to_dict()
        readiness_gate = _gate_snapshot(evaluation)

        payload = _build_payload(
            source_input=str(input_path) if input_path else "built_in_default",
            signal_count=len(signals),
            evaluation=evaluation,
            readiness_gate=readiness_gate,
        )
    except Exception as exc:
        payload = {
            "generated_at": _iso_now(),
            "source": "scripts/run_persona_swarm_framework.py",
            "ok": False,
            "error": str(exc),
        }
        _write_json(out_path, payload)
        _emit(payload)
        return 2

    _write_json(out_path, payload)
    _emit(payload)

    if args.strict and not payload["readiness_gate"]["passed"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
