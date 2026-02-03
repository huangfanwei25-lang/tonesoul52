import json
import warnings

from .council_adapter import run_council


def main() -> int:
    warnings.warn(
        "tonesoul.simulate_council is deprecated; use tonesoul.council.runtime.CouncilRuntime",
        DeprecationWarning,
        stacklevel=2,
    )
    event = run_council("Should we unify all persona libraries?")
    print(json.dumps(event, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
