from typing import Dict

from .tech_trace.normalize import main


if __name__ == "__main__":
    paths: Dict[str, str] = main()
    print(f"normalized.json: {paths['normalized']}")
