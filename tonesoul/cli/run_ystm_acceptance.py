from typing import Dict, List

from ..ystm.acceptance import run_acceptance


def main() -> List[Dict[str, str]]:
    results = run_acceptance()
    for result in results:
        line = f"{result['test']}: {result['status']}"
        if result["status"] != "PASS":
            line = f"{line} - {result.get('error', 'unknown error')}"
        print(line)
    failures = [result for result in results if result["status"] != "PASS"]
    if failures:
        raise SystemExit(1)
    return results


if __name__ == "__main__":
    main()
