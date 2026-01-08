from typing import Dict

from .evidence_collector import main


if __name__ == "__main__":
    paths: Dict[str, str] = main()
    print(f"evidence_summary.md: {paths['evidence_summary']}")
