import os
import subprocess
import sys


def main() -> int:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    target = os.path.join(repo_root, "yuhun_cli.py")
    if not os.path.exists(target):
        print(f"Missing yuhun_cli.py: {target}")
        return 1

    cmd = [sys.executable, target, "-h"]
    completed = subprocess.run(cmd, cwd=repo_root, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
