from typing import Dict

from .frame_router import main


if __name__ == "__main__":
    paths: Dict[str, str] = main()
    print(f"frame_plan.json: {paths['frame_plan']}")
