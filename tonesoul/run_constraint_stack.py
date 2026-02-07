from typing import Dict

from .constraint_stack import main

if __name__ == "__main__":
    paths: Dict[str, str] = main()
    print(f"constraints.md: {paths['constraints']}")
