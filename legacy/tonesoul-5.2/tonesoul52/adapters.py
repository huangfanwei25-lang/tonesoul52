import os
import subprocess
from dataclasses import dataclass
from typing import List, Optional

from .config import KNOWN_ENTRYPOINTS


@dataclass
class RunResult:
    name: str
    command: List[str]
    cwd: str
    returncode: Optional[int]
    error: Optional[str] = None


def _run(cmd: List[str], cwd: str) -> RunResult:
    try:
        completed = subprocess.run(cmd, cwd=cwd, check=False)
        return RunResult(
            name=cmd[0],
            command=cmd,
            cwd=cwd,
            returncode=completed.returncode,
        )
    except Exception as exc:
        return RunResult(
            name=cmd[0],
            command=cmd,
            cwd=cwd,
            returncode=None,
            error=str(exc),
        )


def list_entrypoints() -> List[str]:
    return [ep.name for ep in KNOWN_ENTRYPOINTS]


def run_entrypoint(name: str, dry_run: bool = True) -> RunResult:
    match = next((ep for ep in KNOWN_ENTRYPOINTS if ep.name == name), None)
    if match is None:
        return RunResult(name=name, command=[], cwd="", returncode=None, error="Unknown entrypoint")

    if not match.command:
        return RunResult(name=name, command=[], cwd="", returncode=None, error="No command configured")

    cmd = match.command.split()
    cwd = os.path.dirname(os.path.abspath(match.path))

    if dry_run:
        return RunResult(name=match.name, command=cmd, cwd=cwd, returncode=None)

    return _run(cmd, cwd)
