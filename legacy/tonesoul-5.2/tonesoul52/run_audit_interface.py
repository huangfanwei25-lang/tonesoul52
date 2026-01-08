from typing import Dict

from .audit_interface import main


if __name__ == "__main__":
    paths: Dict[str, str] = main()
    print(f"audit_request.json: {paths['audit_request']}")
