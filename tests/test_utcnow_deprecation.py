from __future__ import annotations

import subprocess
from pathlib import Path


def test_tracked_python_files_do_not_call_deprecated_utcnow() -> None:
    result = subprocess.run(
        ["git", "ls-files", "*.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    pattern = "datetime." + "utcnow("
    offenders: list[str] = []

    for rel_path in result.stdout.splitlines():
        path = Path(rel_path)
        if pattern in path.read_text(encoding="utf-8"):
            offenders.append(rel_path)

    assert offenders == []
