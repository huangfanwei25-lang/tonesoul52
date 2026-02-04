import os
import socket
from dataclasses import dataclass
from typing import List, Optional

from .config import KNOWN_ENTRYPOINTS


@dataclass
class CheckResult:
    name: str
    ok: bool
    error: Optional[str] = None


def check_entrypoints() -> List[CheckResult]:
    results: List[CheckResult] = []
    for ep in KNOWN_ENTRYPOINTS:
        exists = os.path.exists(ep.path)
        results.append(
            CheckResult(name=f"entrypoint:{ep.name}", ok=exists, error=None if exists else ep.path)
        )
    return results


def check_ollama(host: str = "127.0.0.1", port: int = 11434, timeout: float = 0.5) -> CheckResult:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        return CheckResult(name="ollama:tcp", ok=True)
    except Exception as exc:
        return CheckResult(name="ollama:tcp", ok=False, error=str(exc))
    finally:
        sock.close()


def main() -> int:
    results = []
    results.extend(check_entrypoints())
    results.append(check_ollama())

    failed = [r for r in results if not r.ok]
    for result in results:
        status = "OK" if result.ok else "FAIL"
        if result.ok:
            print(f"{status}: {result.name}")
        else:
            print(f"{status}: {result.name} -> {result.error}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
