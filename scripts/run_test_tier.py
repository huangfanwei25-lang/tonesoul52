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
    "fast": [
        "tests/test_runtime_adapter.py",
        "tests/test_start_agent_session.py",
        "tests/test_diagnose.py",
        "tests/test_run_r_memory_packet.py",
        "tests/test_verify_7d.py",
    ],
    "blocking": [
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
    "full": ["tests"],
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a curated ToneSoul pytest tier instead of hard-coding ad hoc commands."
    )
    parser.add_argument(
        "--tier",
        choices=sorted(TIER_TARGETS),
        default="blocking",
        help="Which pytest tier to run.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Print the selected tier targets instead of executing pytest.",
    )
    return parser


def _tier_targets(tier: str) -> list[str]:
    return list(TIER_TARGETS[tier])


def _build_pytest_command(
    python_executable: str,
    tier: str,
    *,
    extra_args: Iterable[str] | None = None,
) -> list[str]:
    command = [python_executable, "-m", "pytest", *_tier_targets(tier), "-q"]
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

    command = _build_pytest_command(sys.executable, args.tier)
    proc = subprocess.run(command)
    return int(proc.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
