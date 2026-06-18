"""
ToneSoul test tier runner.

Provides a small number of curated pytest tiers so operational gates do not
need to duplicate the entire regression suite.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from typing import Iterable

TIER_TARGETS: dict[str, list[str]] = {
    "smoke": [
        "tests/test_runtime_adapter.py",
        "tests/test_start_agent_session.py",
        "tests/test_diagnose.py",
        "tests/test_run_r_memory_packet.py",
        "tests/test_verify_7d.py",
    ],
    "core": [
        "tests/test_council_compact.py",
        "tests/test_mcp_server.py",
        "tests/test_runtime_adapter.py",
        "tests/test_receiver_posture.py",
        "tests/test_risk_calculator.py",
        "tests/test_run_v1_2_tool_entry_smoke.py",
        "tests/test_start_agent_session.py",
        "tests/test_vscode_extension_skeleton.py",
        "tests/test_diagnose.py",
        "tests/test_run_r_memory_packet.py",
        "tests/test_observer_window.py",
        "tests/test_unified_pipeline_dispatch.py",
        "tests/test_unified_pipeline_v2_runtime.py",
        "tests/test_run_monthly_consolidation.py",
        "tests/test_run_collaborator_beta_preflight.py",
        "tests/test_run_launch_continuity_validation_wave.py",
        "tests/test_verify_7d.py",
        "tests/test_verify_incremental_commit_attribution.py",
        "tests/test_workflow_contracts.py",
        "tests/test_tonesoul_config.py",
    ],
    "slow": ["tests"],
    "full": ["tests"],
}

TIER_ALIASES: dict[str, str] = {
    "fast": "smoke",
    "blocking": "core",
}

MARKER_EXPRESSIONS: dict[str, str | None] = {
    "smoke": "not slow",
    "core": "not slow",
    "slow": "slow",
    "full": None,
}

XDIST_DEFAULT_TIERS = {"smoke", "core", "slow"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a curated ToneSoul pytest tier instead of hard-coding ad hoc commands."
    )
    parser.add_argument(
        "--tier",
        choices=sorted([*TIER_TARGETS, *TIER_ALIASES]),
        default="core",
        help="Which pytest tier to run.",
    )
    parser.add_argument(
        "--workers",
        default="auto",
        help="pytest-xdist worker count for parallel tiers; use 0 to run serially.",
    )
    parser.add_argument(
        "--no-xdist",
        action="store_true",
        help="Run the selected tier without pytest-xdist.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Print the selected tier targets instead of executing pytest.",
    )
    return parser


def _canonical_tier(tier: str) -> str:
    return TIER_ALIASES.get(tier, tier)


def _tier_targets(tier: str) -> list[str]:
    return list(TIER_TARGETS[_canonical_tier(tier)])


def _build_pytest_command(
    python_executable: str,
    tier: str,
    *,
    extra_args: Iterable[str] | None = None,
    workers: str = "auto",
    use_xdist: bool = True,
) -> list[str]:
    canonical_tier = _canonical_tier(tier)
    command = [python_executable, "-m", "pytest", *_tier_targets(canonical_tier), "-q"]

    marker_expression = MARKER_EXPRESSIONS[canonical_tier]
    if marker_expression is not None:
        command.extend(["-m", marker_expression])

    if use_xdist and workers != "0" and canonical_tier in XDIST_DEFAULT_TIERS:
        command.extend(["-n", workers])

    if extra_args:
        command.extend(extra_args)
    return command


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    targets = _tier_targets(args.tier)
    if args.list:
        for target in targets:
            print(target)
        return 0

    command = _build_pytest_command(
        sys.executable,
        args.tier,
        workers=args.workers,
        use_xdist=not args.no_xdist,
    )
    proc = subprocess.run(command)
    return int(proc.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
