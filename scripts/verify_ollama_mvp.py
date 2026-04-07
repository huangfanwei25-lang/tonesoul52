"""Verify SMALL_BOAT_MVP Ollama release checklist."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tonesoul.gates.compute import ComputeGate, RoutingPath
from tonesoul.llm import create_ollama_client


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass
class CheckResult:
    name: str
    status: str
    detail: str


def _run_command(command: list[str], timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=max(1, int(timeout)),
    )


def _check_ollama_list(model: str) -> CheckResult:
    result = _run_command(["ollama", "list"], timeout=30)
    if result.returncode != 0:
        return CheckResult("ollama_list", "fail", (result.stderr or result.stdout).strip())
    output = result.stdout.strip()
    if model in output:
        return CheckResult("ollama_list", "pass", f"model found: {model}")
    return CheckResult("ollama_list", "fail", f"model not found in `ollama list`: {model}")


def _check_handshake() -> CheckResult:
    try:
        client = create_ollama_client()
        response = str(client.generate("hello")).strip()
    except Exception as exc:  # pragma: no cover - runtime integration failure path
        return CheckResult("backend_handshake", "fail", f"{exc.__class__.__name__}: {exc}")
    if response:
        preview = response[:120].replace("\n", " ")
        return CheckResult("backend_handshake", "pass", f"received response: {preview}")
    return CheckResult("backend_handshake", "fail", "received empty response")


def _check_low_high_tension() -> list[CheckResult]:
    gate = ComputeGate(local_model_enabled=True)

    low_decision = gate.evaluate(
        user_tier="free",
        user_message="hi",
        initial_tension=0.1,
        user_id="ollama-mvp-low",
    )
    low_ok = low_decision.path == RoutingPath.PASS_LOCAL
    low_status = "pass" if low_ok else "fail"
    low_detail = (
        f"route={low_decision.path.value}; expected {RoutingPath.PASS_LOCAL.value} "
        "(council skipped)"
    )

    high_decision = gate.evaluate(
        user_tier="premium",
        user_message="I need full risk deliberation before acting.",
        initial_tension=0.9,
        user_id="ollama-mvp-high",
    )
    high_ok = high_decision.path == RoutingPath.PASS_COUNCIL
    high_status = "pass" if high_ok else "fail"
    high_detail = (
        f"route={high_decision.path.value}; expected {RoutingPath.PASS_COUNCIL.value} "
        "(council activated)"
    )

    return [
        CheckResult("low_tension_route", low_status, low_detail),
        CheckResult("high_tension_route", high_status, high_detail),
    ]


def _check_regression(command: str) -> CheckResult:
    import shlex

    completed = subprocess.run(
        shlex.split(command),
        shell=False,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode == 0:
        return CheckResult("regression_tests", "pass", command)
    stderr = (completed.stderr or "").strip()
    stdout = (completed.stdout or "").strip()
    tail = stderr[-300:] if stderr else stdout[-300:]
    return CheckResult(
        "regression_tests",
        "fail",
        f"command failed ({completed.returncode}): {command}; tail={tail}",
    )


def _emit_payload(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:  # pragma: no cover - fallback for odd terminals
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify Ollama MVP checklist")
    parser.add_argument(
        "--model",
        default=os.environ.get("TONESOUL_OLLAMA_MODEL", "qwen3.5:4b"),
        help="Model name expected in `ollama list`.",
    )
    parser.add_argument(
        "--run-regression",
        action="store_true",
        help="Also run the full regression command.",
    )
    parser.add_argument(
        "--regression-cmd",
        default="pytest tests/ -x -q",
        help="Regression command used when --run-regression is enabled.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    os.environ["LLM_BACKEND"] = "ollama"

    checks: list[CheckResult] = []
    checks.append(_check_ollama_list(args.model))
    checks.append(_check_handshake())
    checks.extend(_check_low_high_tension())

    if args.run_regression:
        checks.append(_check_regression(args.regression_cmd))
    else:
        checks.append(CheckResult("regression_tests", "skip", "skipped: --run-regression not set"))

    failed = [c for c in checks if c.status == "fail"]
    warnings = [c for c in checks if c.status == "warn"]
    payload = {
        "generated_at": _utc_now(),
        "ok": len(failed) == 0,
        "failed_count": len(failed),
        "warning_count": len(warnings),
        "checks": [
            {
                "name": c.name,
                "status": c.status,
                "detail": c.detail,
            }
            for c in checks
        ],
        "model": args.model,
    }
    _emit_payload(payload)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
