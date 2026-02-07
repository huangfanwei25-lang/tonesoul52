from __future__ import annotations

import json
import socket
import subprocess
import sys


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def test_verify_openclaw_probe_script_smoke():
    port = _find_free_port()
    cmd = [
        sys.executable,
        "scripts/verify_openclaw_probe.py",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
        "--timeout",
        "3",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["probe"]["ok"] is True
    assert payload["received_count"] >= 1
