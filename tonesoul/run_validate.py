import os
from typing import List

from .adapters import list_entrypoints, run_entrypoint
from .config import KNOWN_ENTRYPOINTS


def validate_entrypoints() -> List[str]:
    issues = []
    for ep in KNOWN_ENTRYPOINTS:
        if not os.path.exists(ep.path):
            issues.append(f"Missing: {ep.name} -> {ep.path}")
    return issues


def main() -> int:
    issues = validate_entrypoints()
    if issues:
        print("Entrypoint issues detected:")
        for issue in issues:
            print(f"- {issue}")
    else:
        print("All configured entrypoints exist.")

    print("\nDry-run commands:")
    for name in list_entrypoints():
        result = run_entrypoint(name, dry_run=True)
        cmd = " ".join(result.command)
        if cmd:
            print(f"- {name}: {cmd} (cwd: {result.cwd})")
        else:
            print(f"- {name}: <no command>")

    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
