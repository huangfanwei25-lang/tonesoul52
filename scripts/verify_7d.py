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
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RDD_MIN_CASES = 20
DDD_STALE_DAYS = 7
DDD_ALLOWED_INVALID_TOPICS: set[str] = set()
DDD_DISCUSSION_PATH = Path("memory/agent_discussion_curated.jsonl")
DDD_FRESHNESS_REMEDIATION = (
    "append one LESSONS_V1 closeout via "
    "`python tools/agent_discussion_tool.py append-lessons ...`"
)
DEFAULT_WEB_BASE = "http://127.0.0.1:3000"
DEFAULT_API_BASE = "http://127.0.0.1:5000"
AUDIT_WEB_BASE_ENV = "TONESOUL_AUDIT_WEB_BASE"
AUDIT_API_BASE_ENV = "TONESOUL_AUDIT_API_BASE"
COMMAND_TIMEOUT_ENV = "TONESOUL_VERIFY_COMMAND_TIMEOUT"
TDD_PYTEST_TIMEOUT_ENV = "TONESOUL_TDD_PYTEST_TIMEOUT"
TDD_TEST_TIER_ENV = "TONESOUL_TDD_TEST_TIER"


def _resolve_timeout_env(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        parsed = int(raw.strip())
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


DEFAULT_COMMAND_TIMEOUT = _resolve_timeout_env(COMMAND_TIMEOUT_ENV, 1200)
TDD_PYTEST_TIMEOUT = _resolve_timeout_env(TDD_PYTEST_TIMEOUT_ENV, 2400)
DEFAULT_TDD_TEST_TIER = os.environ.get(TDD_TEST_TIER_ENV, "blocking").strip() or "blocking"


@dataclass
class CheckResult:
    dimension: str
    gate: str
    status: str
    command: str
    note: str = ""


def _run(command: list[str], timeout: int = DEFAULT_COMMAND_TIMEOUT) -> tuple[bool, str, str, int]:
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


def _display_command(command: list[str]) -> str:
    rendered: list[str] = []
    for index, token in enumerate(command):
        text = str(token)
        if index == 0:
            executable = text.replace("\\", "/").rsplit("/", 1)[-1].lower()
            if executable.startswith("python"):
                rendered.append("python")
                continue
        rendered.append(text)
    return " ".join(rendered)


def _result(
    dimension: str, gate: str, status: str, command: list[str], note: str = ""
) -> CheckResult:
    return CheckResult(
        dimension=dimension,
        gate=gate,
        status=status,
        command=_display_command(command),
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
    cmd = [
        sys.executable,
        "tools/agent_discussion_tool.py",
        "tail",
        "--path",
        str(path),
        "--limit",
        "1",
    ]
    if not path.exists():
        return _result(
            "DDD_FRESHNESS",
            "SOFT_FAIL",
            "fail",
            cmd,
            f"discussion file not found; remediation: {DDD_FRESHNESS_REMEDIATION}",
        )
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
            (
                "no valid timestamp found in discussion channel; remediation: "
                f"{DDD_FRESHNESS_REMEDIATION}"
            ),
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
        (
            f"stale data: age_days={age_days:.2f}, threshold={stale_days}; remediation: "
            f"{DDD_FRESHNESS_REMEDIATION}"
        ),
    )


def _check_tdd() -> CheckResult:
    cmd = [sys.executable, "scripts/run_test_tier.py", "--tier", DEFAULT_TDD_TEST_TIER]
    ok, _, stderr, code = _run(cmd, timeout=TDD_PYTEST_TIMEOUT)
    if ok:
        return _result("TDD", "BLOCKING", "pass", cmd)
    return _result("TDD", "BLOCKING", "fail", cmd, f"exit={code}; {stderr[-300:]}")


def _check_ddd() -> CheckResult:
    discussion_path = DDD_DISCUSSION_PATH
    cmd = [
        sys.executable,
        str(Path("tools/agent_discussion_tool.py")),
        "audit",
        "--path",
        str(discussion_path),
    ]
    if not discussion_path.exists():
        return _result(
            "DDD",
            "BLOCKING",
            "fail",
            cmd,
            (
                f"curated discussion missing at {discussion_path}; run "
                f"'{sys.executable} tools/agent_discussion_tool.py curate' first"
            ),
        )

    ok, stdout, stderr, code = _run(cmd)
    if not ok:
        return _result("DDD", "BLOCKING", "fail", cmd, f"exit={code}; {stderr[-300:]}")
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        return _result("DDD", "BLOCKING", "fail", cmd, f"audit output parse error: {exc}")
    invalid = int(payload.get("invalid_entries", 0))
    if invalid != 0:
        return _result("DDD", "BLOCKING", "fail", cmd, f"invalid_entries={invalid}")
    semantic_invalid, disallowed_invalid = _count_semantic_invalid(discussion_path)
    if disallowed_invalid > 0:
        return _result(
            "DDD",
            "BLOCKING",
            "fail",
            cmd,
            (
                "status=invalid entries on disallowed topics: "
                f"{disallowed_invalid} (total_invalid={semantic_invalid})"
            ),
        )
    if semantic_invalid > 0:
        allowed_topics = ", ".join(sorted(DDD_ALLOWED_INVALID_TOPICS))
        return _result(
            "DDD",
            "BLOCKING",
            "pass",
            cmd,
            (
                f"preserved_invalid_entries={semantic_invalid}; "
                f"allowed_topics=[{allowed_topics}]"
            ),
        )
    return _result("DDD", "BLOCKING", "pass", cmd)


def _count_semantic_invalid(path: Path) -> tuple[int, int]:
    if not path.exists():
        return 0, 0
    total_invalid = 0
    disallowed_invalid = 0
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            status = payload.get("status")
            if not isinstance(status, str):
                continue
            if status.strip().lower() != "invalid":
                continue
            total_invalid += 1
            topic = payload.get("topic")
            if not isinstance(topic, str) or topic.strip() not in DDD_ALLOWED_INVALID_TOPICS:
                disallowed_invalid += 1
    return total_invalid, disallowed_invalid


def _check_ddd_hygiene() -> CheckResult:
    cmd = [
        sys.executable,
        str(Path("scripts/verify_memory_hygiene.py")),
        "--tail-lines",
        "200",
        "--discussion-path",
        str(DDD_DISCUSSION_PATH),
    ]
    ok, _, stderr, code = _run(cmd)
    if ok:
        return _result("DDD_HYGIENE", "BLOCKING", "pass", cmd)
    return _result("DDD_HYGIENE", "BLOCKING", "fail", cmd, f"exit={code}; {stderr[-300:]}")


def _check_xdd() -> CheckResult:
    xdd_candidates = [
        Path("tests/test_uncertainty.py"),
        Path("tests/test_escape_valve.py"),
        Path("tests/test_escape_valve_runtime.py"),
    ]
    xdd_targets = [str(path) for path in xdd_candidates if path.exists()]
    if not xdd_targets:
        return _result(
            "XDD",
            "BLOCKING",
            "fail",
            [sys.executable, "-m", "pytest", str(xdd_candidates[0]), "-q"],
            "no XDD uncertainty test file found",
        )

    cmd = [sys.executable, "-m", "pytest", *xdd_targets, "-q"]
    ok, _, stderr, code = _run(cmd)
    if ok:
        return _result("XDD", "BLOCKING", "pass", cmd)
    return _result("XDD", "BLOCKING", "fail", cmd, f"exit={code}; {stderr[-300:]}")


def _check_gdd() -> CheckResult:
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(Path("tests/test_genesis_integration.py")),
        str(Path("tests/test_provenance_chain.py")),
        "-q",
    ]
    ok, _, stderr, code = _run(cmd)
    if ok:
        return _result("GDD", "BLOCKING", "pass", cmd)
    return _result("GDD", "BLOCKING", "fail", cmd, f"exit={code}; {stderr[-300:]}")


def _check_cdd() -> CheckResult:
    cmd = [sys.executable, "-m", "pytest", "tests/test_api_server_contract.py", "-q"]
    ok, _, stderr, code = _run(cmd)
    if ok:
        return _result("CDD", "BLOCKING", "pass", cmd)
    return _result("CDD", "BLOCKING", "fail", cmd, f"exit={code}; {stderr[-300:]}")


def _check_rdd() -> CheckResult:
    cmd = [sys.executable, "-m", "pytest", str(Path("tests/red_team/")), "-q"]
    collect_cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(Path("tests/red_team/")),
        "--collect-only",
        "-q",
    ]
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


def _check_sdh(
    web_base: str,
    api_base: str,
    timeout: int,
    check_council_modes: bool = True,
) -> CheckResult:
    same_origin_mode = web_base.rstrip("/") == api_base.rstrip("/")
    cmd = [
        sys.executable,
        str(Path("scripts/verify_web_api.py")),
        "--web-base",
        web_base,
        "--api-base",
        api_base,
        "--timeout",
        str(timeout),
    ]
    if same_origin_mode:
        cmd.append("--same-origin")
    else:
        cmd.append("--require-backend")
    if check_council_modes and not same_origin_mode:
        cmd.append("--check-council-modes")
    ok, stdout, stderr, code = _run(cmd)
    if ok:
        return _result("SDH", "SOFT_FAIL", "pass", cmd)
    stderr_tail = stderr.strip()[-300:]
    stdout_tail = stdout.strip()[-300:]
    detail = stderr_tail or stdout_tail
    return _result("SDH", "SOFT_FAIL", "fail", cmd, f"exit={code}; {detail}")


def _calculate_score(results: list[CheckResult]) -> dict[str, int]:
    scores = {}
    # Dimensions: TDD, RDD, DDD, XDD, GDD, CDD, SDH
    weights = {
        "TDD": 20,
        "RDD": 20,
        "DDD": 15,
        "XDD": 15,
        "GDD": 10,
        "CDD": 10,
        "SDH": 10,
    }

    # Map sub-checks to main dimensions
    dim_map = {
        "TDD": "TDD",
        "RDD": "RDD",
        "DDD": "DDD",
        "DDD_FRESHNESS": "DDD",
        "DDD_HYGIENE": "DDD",
        "XDD": "XDD",
        "GDD": "GDD",
        "CDD": "CDD",
        "SDH": "SDH",
    }

    dim_results = defaultdict(list)
    for r in results:
        dim = dim_map.get(r.dimension, r.dimension)
        dim_results[dim].append(r)

    for dim, weight in weights.items():
        res_list = dim_results.get(dim, [])
        if not res_list:
            scores[dim] = 0
            continue

        passed_count = sum(1 for r in res_list if r.status == "pass")
        score = (passed_count / len(res_list)) * 100
        scores[dim] = int(score)

    total_score = sum((scores.get(dim, 0) * weight) / 100 for dim, weight in weights.items())
    scores["OVERALL"] = int(total_score)
    return scores


def _sync_to_markdown(scores: dict[str, int], results: list[CheckResult]):
    # Files to update
    targets = [
        Path("README.md"),
        Path("memory/ANTIGRAVITY_SYNC.md"),
    ]

    # Build status string for each dimension
    status_map = {}
    for dim in ["TDD", "RDD", "DDD", "XDD", "GDD", "CDD", "SDH"]:
        score = scores.get(dim, 0)
        emoji = "✅" if score >= 80 else "🟡" if score >= 50 else "❌"
        status_text = f"{emoji} {score}/100"

        # Add details if available (e.g. test count for TDD)
        if dim == "TDD":
            # Just a placeholder, as extracting actual count from pytest stderr is tricky in this run
            pass

        status_map[dim] = status_text

    for target in targets:
        if not target.exists():
            continue

        content = target.read_text(encoding="utf-8")

        # Update tables
        for dim, status in status_map.items():
            # Match "| DIM | Description | Status |" or "| DIM | Name | Status |"
            # Pattern for README.md: | TDD | 功能正確？ | ✅ 299 tests |
            # Pattern for SYNC.md: | TDD | 測試驅動 | ✅ 強 (343 tests) |
            pattern = rf"(\| {dim} \| [^|]+ \| )([^|]+)(\|)"
            replacement = rf"\1{status} \3"
            content = re.sub(pattern, replacement, content)

        target.write_text(content, encoding="utf-8")
        print(f"[7D] Synced status to {target}")


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
    parser.add_argument(
        "--check-council-modes",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable council mode switch checks in SDH web/api smoke.",
    )
    parser.add_argument("--web-base", default=_env_or_default(AUDIT_WEB_BASE_ENV, DEFAULT_WEB_BASE))
    parser.add_argument("--api-base", default=_env_or_default(AUDIT_API_BASE_ENV, DEFAULT_API_BASE))
    parser.add_argument("--timeout", type=int, default=40)
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Sync scores back to README.md and ANTIGRAVITY_SYNC.md",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    results = [
        _check_tdd(),
        _check_rdd(),
        _check_ddd(),
        _check_ddd_hygiene(),
        _check_ddd_freshness(DDD_DISCUSSION_PATH, DDD_STALE_DAYS),
        _check_xdd(),
        _check_gdd(),
        _check_cdd(),
    ]
    if args.include_sdh:
        results.append(
            _check_sdh(
                args.web_base,
                args.api_base,
                max(1, args.timeout),
                check_council_modes=bool(args.check_council_modes),
            )
        )
    else:
        skip_cmd = [
            sys.executable,
            str(Path("scripts/verify_web_api.py")),
            "--web-base",
            args.web_base,
            "--api-base",
            args.api_base,
            "--require-backend",
        ]
        if args.check_council_modes:
            skip_cmd.append("--check-council-modes")
        results.append(
            _result(
                "SDH",
                "SOFT_FAIL",
                "skip",
                skip_cmd,
                "skipped; use --include-sdh when web/backend are running",
            )
        )

    scores = _calculate_score(results)
    payload = _summary(results)
    payload["scores"] = scores

    print(json.dumps(payload, ensure_ascii=False, indent=2))

    if args.sync:
        sync_reasons: list[str] = []
        if payload["blocking_failures"] > 0:
            sync_reasons.append("blocking failures detected")
        if payload["soft_failures"] > 0:
            sync_reasons.append("soft failures detected")
        has_sdh_skip = any(r.dimension == "SDH" and r.status == "skip" for r in results)
        if has_sdh_skip:
            sync_reasons.append("SDH is skipped; run with --include-sdh before sync")
        if sync_reasons:
            print(f"[7D] Skip markdown sync: {'; '.join(sync_reasons)}")
        else:
            _sync_to_markdown(scores, results)

    if payload["blocking_failures"] > 0:
        return 1
    if args.strict_soft_fail and payload["soft_failures"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
