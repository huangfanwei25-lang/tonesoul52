import subprocess
import sys
from pathlib import Path


def main() -> int:
    app_path = Path(__file__).resolve().parent / "frontend" / "app.py"

    if not app_path.exists():
        print(f"Dashboard app not found: {app_path}")
        return 1

    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path)]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
