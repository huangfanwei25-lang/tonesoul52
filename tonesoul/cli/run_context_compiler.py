from typing import Dict

from ..context_compiler import main

if __name__ == "__main__":
    paths: Dict[str, str] = main()
    print(f"context.yaml: {paths['context']}")
