"""
Dispatch runner for persona_swarm workflow.

Reads workflow-dispatch inputs from environment variables and invokes
`scripts/run_persona_swarm_framework.py` with validated flags.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

INPUT_PATH_VALIDATION_ERROR_PREFIX = "::error::input_path does not exist"


@dataclass(frozen=True)
class DispatchConfig:
    strict: bool
    input_path: str


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
        strict=_env_bool(env, "TS_SWARM_STRICT", default=True),
        input_path=_env_text(env, "TS_SWARM_INPUT_PATH"),
    )


def _emit_warning(message: str) -> None:
    print(f"::warning::{message}")


def build_command(config: DispatchConfig) -> tuple[list[str], list[str], str | None]:
    command = ["python", "scripts/run_persona_swarm_framework.py"]
    warnings: list[str] = []

    if config.strict:
        command.append("--strict")

    if config.input_path:
        path = Path(config.input_path)
        if not path.exists():
            return (
                command,
                warnings,
                f"{INPUT_PATH_VALIDATION_ERROR_PREFIX}. got='{config.input_path}'",
            )
        command.extend(["--input", config.input_path])
        if path.suffix.lower() != ".json":
            warnings.append(
                "input_path does not end with .json; make sure this is an intentional custom format."
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
