"""
Dispatch runner for repo_healthcheck workflow.

Reads workflow-dispatch inputs from environment variables and invokes
`scripts/run_repo_healthcheck.py` with validated flags.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from typing import Mapping

TIMEOUT_VALIDATION_ERROR_PREFIX = "::error::sdh_timeout must be a positive integer"


@dataclass(frozen=True)
class DispatchConfig:
    include_sdh: bool
    web_base: str
    api_base: str
    sdh_timeout: str
    check_council_modes: bool


def _env_text(env: Mapping[str, str], key: str, default: str = "") -> str:
    return str(env.get(key, default)).strip()


def _env_bool(env: Mapping[str, str], key: str, default: bool) -> bool:
    raw = _env_text(env, key, "true" if default else "false").lower()
    if raw in {"1", "true", "yes", "on"}:
        return True
    if raw in {"0", "false", "no", "off"}:
        return False
    return default


def _load_config(env: Mapping[str, str]) -> DispatchConfig:
    return DispatchConfig(
        include_sdh=_env_bool(env, "TS_INCLUDE_SDH", default=False),
        web_base=_env_text(env, "TS_WEB_BASE"),
        api_base=_env_text(env, "TS_API_BASE"),
        sdh_timeout=_env_text(env, "TS_SDH_TIMEOUT"),
        check_council_modes=_env_bool(env, "TS_CHECK_COUNCIL_MODES", default=True),
    )


def _emit_warning(message: str) -> None:
    print(f"::warning::{message}")


def build_command(config: DispatchConfig) -> tuple[list[str], list[str], str | None]:
    command = [
        "python",
        "scripts/run_repo_healthcheck.py",
        "--strict",
        "--allow-missing-discussion",
    ]
    warnings: list[str] = []

    timeout_value = config.sdh_timeout
    if timeout_value:
        if not timeout_value.isdigit() or int(timeout_value) < 1:
            return (
                command,
                warnings,
                f"{TIMEOUT_VALIDATION_ERROR_PREFIX}. got='{timeout_value}'",
            )

    if config.include_sdh:
        if config.web_base and not config.api_base:
            warnings.append(
                "include_sdh=true and web_base is set but api_base is empty; "
                "api_base will fallback to verify_7d default."
            )
        if config.api_base and not config.web_base:
            warnings.append(
                "include_sdh=true and api_base is set but web_base is empty; "
                "web_base will fallback to verify_7d default."
            )
        command.append("--include-sdh")
        command.append(
            "--check-council-modes" if config.check_council_modes else "--no-check-council-modes"
        )
        if config.web_base:
            command.extend(["--web-base", config.web_base])
        if config.api_base:
            command.extend(["--api-base", config.api_base])
        if timeout_value:
            command.extend(["--sdh-timeout", timeout_value])
    elif config.web_base or config.api_base or timeout_value:
        warnings.append(
            "SDH inputs were provided but include_sdh=false; web/api/timeout inputs will be ignored."
        )

    return command, warnings, None


def main() -> int:
    config = _load_config(os.environ)
    command, warnings, error = build_command(config)

    if error:
        print(error)
        return 1

    for warning in warnings:
        _emit_warning(warning)

    result = subprocess.run(command, check=False)
    return int(result.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
