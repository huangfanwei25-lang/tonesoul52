import os
import subprocess
import sys


def test_commitment_extractor_import_is_cp950_safe() -> None:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "cp950"
    proc = subprocess.run(
        [sys.executable, "-c", "import tonesoul.tonebridge.commitment_extractor"],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
