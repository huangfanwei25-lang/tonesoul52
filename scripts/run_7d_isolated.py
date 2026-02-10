"""
Run full 7D audit with isolated local backend/web services.

This script avoids local port pollution by starting project-owned services on
dedicated ports, then running `scripts/verify_7d.py --include-sdh`.
"""

from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO
from urllib.parse import urlparse

DEFAULT_API_BASE = os.environ.get("TONESOUL_AUDIT_API_BASE", "http://127.0.0.1:5001")
DEFAULT_WEB_BASE = os.environ.get("TONESOUL_AUDIT_WEB_BASE", "http://127.0.0.1:3002")
DEFAULT_STARTUP_TIMEOUT = 90
DEFAULT_SDH_TIMEOUT = 40
LOG_TAIL_LINES = 40


@dataclass
class ProcessHandle:
    name: str
    process: subprocess.Popen[str]
    stdout_file: TextIO
    stderr_file: TextIO
    stdout_path: Path
    stderr_path: Path


def _parse_base_url(url: str, name: str) -> tuple[str, int]:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"{name} must use http/https: {url}")
    host = parsed.hostname
    if not host:
        raise ValueError(f"{name} missing host: {url}")
    port = parsed.port
    if port is None:
        raise ValueError(f"{name} must include explicit port: {url}")
    if host not in {"127.0.0.1", "localhost"}:
        raise ValueError(f"{name} must target localhost for isolated run: {url}")
    return host, port


def _port_in_use(host: str, port: int) -> bool:
    target = "127.0.0.1" if host == "localhost" else host
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.4)
        return sock.connect_ex((target, port)) == 0


def _wait_for_url(url: str, timeout_seconds: int) -> bool:
    deadline = time.monotonic() + max(1, timeout_seconds)
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if 200 <= int(response.status) < 500:
                    return True
        # Startup probes can intermittently reset connections before the web
        # server is fully ready; treat these as retryable signals.
        except (
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            ConnectionResetError,
            ConnectionAbortedError,
            ConnectionRefusedError,
            OSError,
        ):
            pass
        time.sleep(1)
    return False


def _npm_executable() -> str:
    return "npm.cmd" if os.name == "nt" else "npm"


def _open_log(path: Path) -> TextIO:
    path.parent.mkdir(parents=True, exist_ok=True)
    return path.open("w", encoding="utf-8", errors="replace")


def _start_process(
    name: str,
    command: list[str],
    env: dict[str, str],
    repo_root: Path,
    log_dir: Path,
) -> ProcessHandle:
    stdout_path = log_dir / f"{name}.log"
    stderr_path = log_dir / f"{name}.err"
    stdout_file = _open_log(stdout_path)
    stderr_file = _open_log(stderr_path)
    process = subprocess.Popen(
        command,
        cwd=repo_root,
        env=env,
        stdout=stdout_file,
        stderr=stderr_file,
        text=True,
    )
    return ProcessHandle(name, process, stdout_file, stderr_file, stdout_path, stderr_path)


def _stop_process_tree(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            check=False,
            capture_output=True,
            text=True,
        )
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def _tail_file(path: Path, max_lines: int = LOG_TAIL_LINES) -> str:
    if not path.exists():
        return ""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(lines[-max_lines:])


def _print_startup_error(name: str, handle: ProcessHandle) -> None:
    print(f"[FAIL] {name} failed to become ready.")
    stdout_tail = _tail_file(handle.stdout_path)
    stderr_tail = _tail_file(handle.stderr_path)
    print(f"  stdout log: {handle.stdout_path}")
    print(f"  stderr log: {handle.stderr_path}")
    if stdout_tail:
        print("  ---- stdout tail ----")
        print(stdout_tail)
    if stderr_tail:
        print("  ---- stderr tail ----")
        print(stderr_tail)


def _cleanup_logs(handles: list[ProcessHandle]) -> None:
    for handle in handles:
        for path in (handle.stdout_path, handle.stderr_path):
            try:
                path.unlink(missing_ok=True)
            except OSError:
                continue


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run full 7D audit on isolated local ports.")
    parser.add_argument(
        "--api-base", default=DEFAULT_API_BASE, help="Backend base URL with explicit port."
    )
    parser.add_argument(
        "--web-base", default=DEFAULT_WEB_BASE, help="Web base URL with explicit port."
    )
    parser.add_argument(
        "--startup-timeout",
        type=int,
        default=DEFAULT_STARTUP_TIMEOUT,
        help="Seconds to wait for backend/web readiness.",
    )
    parser.add_argument(
        "--sdh-timeout",
        type=int,
        default=DEFAULT_SDH_TIMEOUT,
        help="Timeout passed to verify_7d SDH check.",
    )
    parser.add_argument(
        "--web-script",
        choices=["start", "dev"],
        default="start",
        help="npm script used to launch web service.",
    )
    parser.add_argument(
        "--strict-soft-fail",
        action="store_true",
        help="Return non-zero when 7D soft-fail checks fail.",
    )
    parser.add_argument(
        "--keep-logs",
        action="store_true",
        help="Keep startup logs even when audit succeeds.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    log_dir = repo_root / "tmp" / "7d_isolated_logs"

    api_host, api_port = _parse_base_url(args.api_base, "api-base")
    web_host, web_port = _parse_base_url(args.web_base, "web-base")

    if _port_in_use(api_host, api_port):
        print(f"[FAIL] api-base port already in use: {args.api_base}")
        return 1
    if _port_in_use(web_host, web_port):
        print(f"[FAIL] web-base port already in use: {args.web_base}")
        return 1

    handles: list[ProcessHandle] = []
    try:
        backend_env = os.environ.copy()
        backend_env["TONESOUL_API_HOST"] = "127.0.0.1"
        backend_env["TONESOUL_API_PORT"] = str(api_port)
        backend = _start_process(
            "7d_backend",
            [sys.executable, "apps/api/server.py"],
            backend_env,
            repo_root,
            log_dir,
        )
        handles.append(backend)
        print(f"[INFO] Started backend: {args.api_base}")
        if not _wait_for_url(f"{args.api_base.rstrip('/')}/api/health", args.startup_timeout):
            _print_startup_error("backend", backend)
            return 1

        web_env = os.environ.copy()
        web_env["TONESOUL_BACKEND_URL"] = args.api_base
        web = _start_process(
            "7d_web",
            [
                _npm_executable(),
                "--prefix",
                "apps/web",
                "run",
                args.web_script,
                "--",
                "--port",
                str(web_port),
            ],
            web_env,
            repo_root,
            log_dir,
        )
        handles.append(web)
        print(f"[INFO] Started web: {args.web_base} ({args.web_script})")
        if not _wait_for_url(args.web_base.rstrip("/") + "/", args.startup_timeout):
            _print_startup_error("web", web)
            return 1

        verify_cmd = [
            sys.executable,
            "scripts/verify_7d.py",
            "--include-sdh",
            "--web-base",
            args.web_base,
            "--api-base",
            args.api_base,
            "--timeout",
            str(max(1, args.sdh_timeout)),
        ]
        if args.strict_soft_fail:
            verify_cmd.append("--strict-soft-fail")
        print("[INFO] Running:", " ".join(verify_cmd))
        result = subprocess.run(verify_cmd, cwd=repo_root, check=False)
        return int(result.returncode)
    finally:
        for handle in reversed(handles):
            _stop_process_tree(handle.process)
            handle.stdout_file.close()
            handle.stderr_file.close()
        if not args.keep_logs:
            _cleanup_logs(handles)


if __name__ == "__main__":
    raise SystemExit(main())
