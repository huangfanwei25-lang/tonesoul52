from typing import Dict

from .tech_trace.capture import main

if __name__ == "__main__":
    paths: Dict[str, str] = main()
    print(f"capture.json: {paths['capture']}")
