"""
ToneSoul 7D audit runner.

Runs executable checks mapped from the 7D framework and emits JSON summary.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RDD_MIN_CASES = 10
DDD_STALE_DAYS = 7
DEFAULT_WEB_BASE = "http://127.0.0.1:3000"
DEFAULT_API_BASE = "http://127.0.0.1:5000"
AUDIT_WEB_BASE_ENV = "TONESOUL_AUDIT_WEB_BASE"
AUDIT_API_BASE_ENV = "TONESOUL_AUDIT_API_BASE"


@dataclass
class CheckResult:
    dimension: str
    gate: str
    status: str
    command: str
    note: str = ""


def _run(command: list[str], timeout: int = 1200) -> tuple[bool, str, str, int]:
    proc = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    ok = proc.returncode == 0
    return ok, proc.stdout, proc.stderr, proc.returncode


def _result(
    dimension: str, gate: str, status: str, command: list[str], note: str = ""
) -> CheckResult:
    return CheckResult(
        dimension=dimension,
        gate=gate,
        status=status,
        command=" ".join(command),
        note=note,
    )


def _parse_timestamp(value: str) -> datetime | None:
    text = value.strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _check_ddd_freshness(path: Path, stale_days: int) -> CheckResult:
    cmd = ["python", "tools/agent_discussion_tool.py", "tail", "--path", str(path), "--limit", "1"]
    if not path.exists():
        return _result("DDD_FRESHNESS", "SOFT_FAIL", "fail", cmd, "discussion file not found")
    latest: datetime | None = None
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = payload.get("timestamp")
            if isinstance(ts, str):
                parsed = _parse_timestamp(ts)
                if parsed and (latest is None or parsed > latest):
                    latest = parsed
    if latest is None:
        return _result(
            "DDD_FRESHNESS",
            "SOFT_FAIL",
            "fail",
            cmd,
            "no valid timestamp found in discussion channel",
        )
    age_days = (datetime.now(timezone.utc) - latest).total_seconds() / 86400.0
    if age_days <= stale_days:
        return _result(
            "DDD_FRESHNESS",
            "SOFT_FAIL",
            "pass",
            cmd,
            f"age_days={age_days:.2f}, threshold={stale_days}",
        )
    return _result(
        "DDD_FRESHNESS",
        "SOFT_FAIL",
        "fail",
        cmd,
        f"stale data: age_days={age_days:.2f}, threshold={stale_days}",
    )


def _check_tdd() -> CheckResult:
    cmd = ["pytest", "tests/", "-q"]
    ok, _, stderr, code = _run(cmd)
    if ok:
        return _result("TDD", "BLOCKING", "pass", cmd)
    return _result("TDD", "BLOCKING", "fail", cmd, f"exit={code}; {stderr[-300:]}")


def _check_ddd() -> CheckResult:
    cmd = [
        "python",
        "tools/agent_discussion_tool.py",
        "audit",
        "--path",
        "memory/agent_discussion.jsonl",
    ]
    ok, stdout, stderr, code = _run(cmd)
    if not ok:
        return _result("DDD", "BLOCKING", "fail", cmd, f"exit={code}; {stderr[-300:]}")
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        return _result("DDD", "BLOCKING", "fail", cmd, f"audit output parse error: {exc}")
    invalid = int(payload.get("invalid_entries", 0))
    if invalid == 0:
        return _result("DDD", "BLOCKING", "pass", cmd)
    return _result("DDD", "BLOCKING", "fail", cmd, f"invalid_entries={invalid}")


def _check_ddd_hygiene() -> CheckResult:
    cmd = [
        "python",
        "scripts/verify_memory_hygiene.py",
        "--tail-lines",
        "200",
    ]
    ok, _, stderr, code = _run(cmd)
    if ok:
        return _result("DDD_HYGIENE", "BLOCKING", "pass", cmd)
    return _result("DDD_HYGIENE", "BLOCKING", "fail", cmd, f"exit={code}; {stderr[-300:]}")


def _check_xdd() -> CheckResult:
    cmd = ["pytest", "tests/test_uncertainty.py", "-q"]
    ok, _, stderr, code = _run(cmd)
    if ok:
        return _result("XDD", "BLOCKING", "pass", cmd)
    return _result("XDD", "BLOCKING", "fail", cmd, f"exit={code}; {stderr[-300:]}")


def _check_gdd() -> CheckResult:
    cmd = [
        "pytest",
        "tests/test_genesis_integration.py",
        "tests/test_provenance_chain.py",
        "-q",
    ]
    ok, _, stderr, code = _run(cmd)
    if ok:
        return _result("GDD", "BLOCKING", "pass", cmd)
    return _result("GDD", "BLOCKING", "fail", cmd, f"exit={code}; {stderr[-300:]}")


def _check_cdd() -> CheckResult:
    cmd = ["pytest", "tests/test_api_server_contract.py", "-q"]
    ok, _, stderr, code = _run(cmd)
    if ok:
        return _result("CDD", "BLOCKING", "pass", cmd)
    return _result("CDD", "BLOCKING", "fail", cmd, f"exit={code}; {stderr[-300:]}")


def _check_rdd() -> CheckResult:
    cmd = ["pytest", "tests/red_team/", "-q"]
    collect_cmd = ["pytest", "tests/red_team/", "--collect-only", "-q"]
    collected_ok, collected_stdout, collected_stderr, collected_code = _run(collect_cmd)
    if not collected_ok:
        if collected_code == 5:
            return _result(
                "RDD",
                "SOFT_FAIL",
                "not_implemented",
                cmd,
                "no red-team tests collected",
            )
        return _result(
            "RDD",
            "SOFT_FAIL",
            "fail",
            cmd,
            f"collect exit={collected_code}; {collected_stderr[-300:]}",
        )
    match = re.search(r"collected\\s+(\\d+)\\s+items", collected_stdout)
    if match:
        collected_count = int(match.group(1))
    else:
        collected_count = sum(1 for line in collected_stdout.splitlines() if "<Function " in line)
    if collected_count < RDD_MIN_CASES:
        return _result(
            "RDD",
            "SOFT_FAIL",
            "fail",
            cmd,
            f"red-team case-count below threshold: {collected_count}/{RDD_MIN_CASES}",
        )
    ok, _, stderr, code = _run(cmd)
    if ok:
        return _result("RDD", "SOFT_FAIL", "pass", cmd, f"case-count={collected_count}")
    if code == 5:
        return _result(
            "RDD",
            "SOFT_FAIL",
            "not_implemented",
            cmd,
            "no red-team tests collected",
        )
    return _result("RDD", "SOFT_FAIL", "fail", cmd, f"exit={code}; {stderr[-300:]}")


def _check_sdh(web_base: str, api_base: str, timeout: int) -> CheckResult:
    cmd = [
        "python",
        "scripts/verify_web_api.py",
        "--web-base",
        web_base,
        "--api-base",
        api_base,
        "--require-backend",
        "--timeout",
        str(timeout),
    ]
    ok, _, stderr, code = _run(cmd)
    if ok:
        return _result("SDH", "SOFT_FAIL", "pass", cmd)
    return _result("SDH", "SOFT_FAIL", "fail", cmd, f"exit={code}; {stderr[-300:]}")


def _summary(results: list[CheckResult]) -> dict[str, Any]:
    blocking_fail = [r for r in results if r.gate == "BLOCKING" and r.status == "fail"]
    soft_fail = [r for r in results if r.gate == "SOFT_FAIL" and r.status == "fail"]
    not_impl = [r for r in results if r.status == "not_implemented"]
    return {
        "total": len(results),
        "blocking_failures": len(blocking_fail),
        "soft_failures": len(soft_fail),
        "not_implemented": len(not_impl),
        "results": [r.__dict__ for r in results],
    }


def _env_or_default(name: str, default: str) -> str:
    value = os.environ.get(name, "").strip()
    return value if value else default


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run 7D executable audit checks")
    parser.add_argument(
        "--include-sdh",
        action="store_true",
        help="Run SDH integrated smoke check (requires web/backend services running).",
    )
    parser.add_argument(
        "--strict-soft-fail",
        action="store_true",
        help="Return non-zero if SOFT_FAIL checks fail.",
    )
    parser.add_argument("--web-base", default=_env_or_default(AUDIT_WEB_BASE_ENV, DEFAULT_WEB_BASE))
    parser.add_argument("--api-base", default=_env_or_default(AUDIT_API_BASE_ENV, DEFAULT_API_BASE))
    parser.add_argument("--timeout", type=int, default=40)
    return parser


def main() -> int:
    args = build_parser().parse_args()

    results = [
        _check_tdd(),
        _check_rdd(),
        _check_ddd(),
        _check_ddd_hygiene(),
        _check_ddd_freshness(Path("memory/agent_discussion.jsonl"), DDD_STALE_DAYS),
        _check_xdd(),
        _check_gdd(),
        _check_cdd(),
    ]
    if args.include_sdh:
        results.append(_check_sdh(args.web_base, args.api_base, max(1, args.timeout)))
    else:
        results.append(
            _result(
                "SDH",
                "SOFT_FAIL",
                "skip",
                [
                    "python",
                    "scripts/verify_web_api.py",
                    "--web-base",
                    args.web_base,
                    "--api-base",
                    args.api_base,
                    "--require-backend",
                ],
                "skipped; use --include-sdh when web/backend are running",
            )
        )

    payload = _summary(results)
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    if payload["blocking_failures"] > 0:
        return 1
    if args.strict_soft_fail and payload["soft_failures"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
