import os
import sys
from unittest.mock import patch


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from yuhun_cli import YuHunCLI  # noqa: E402


def main() -> int:
    cli = YuHunCLI(verbose=False)
    sample_inputs = ["Hello, who are you?", "What is the meaning of life?", "exit"]

    def fake_input(prompt: str = "") -> str:
        if sample_inputs:
            return sample_inputs.pop(0)
        return "exit"

    try:
        with patch("builtins.input", side_effect=fake_input):
            cli.process("Hello")
        print("YuHun loop smoke test completed.")
        return 0
    except Exception as exc:
        print(f"YuHun loop smoke test encountered an error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
