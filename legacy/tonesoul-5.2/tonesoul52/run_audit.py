import os
from typing import Dict

from .inventory import write_inventory_report


def main() -> Dict[str, str]:
    output_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    output_dir = os.path.abspath(output_dir)
    return write_inventory_report(output_dir)


if __name__ == "__main__":
    paths = main()
    print(f"Inventory JSON: {paths['json']}")
    print(f"Inventory MD: {paths['md']}")
