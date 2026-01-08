from typing import Dict

from .generation_orch import main


if __name__ == "__main__":
    paths: Dict[str, str] = main()
    print(f"execution_report.md: {paths['execution_report']}")
