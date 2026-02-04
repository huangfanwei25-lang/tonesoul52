import argparse
import json
import os
from typing import Dict, List, Optional

from .issue_codes import IssueCode, issue

REQUIRED_TOP = [
    "seed_version",
    "run_id",
    "run_path",
    "created_at",
    "metadata",
    "provenance",
    "content",
    "governance",
    "anchor",
    "sigma_stamp",
    "state_history",
    "context_hash",
    "pointers",
    "ystm_stats",
    "ystm_snapshot",
]
REQUIRED_META = ["id", "chronos", "author", "license"]
REQUIRED_PROVENANCE = ["source", "confidence", "parent_seed"]
REQUIRED_PROVENANCE_SOURCE = ["run_id", "run_path", "context"]
REQUIRED_CONTENT = ["title", "summary"]
REQUIRED_GOVERNANCE = ["canonical", "rules"]
REQUIRED_ANCHOR = ["content_hash", "event_id"]
REQUIRED_POINTERS = [
    "context",
    "frame_plan",
    "constraints",
    "execution_report",
    "audit_request",
]


def _load_json(path: str) -> Dict[str, object]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Seed payload must be a JSON object.")
    return payload


def _require_keys(
    issues: List[str],
    payload: Dict[str, object],
    keys: List[str],
    code: IssueCode,
) -> None:
    for key in keys:
        if key not in payload:
            issues.append(issue(code, field=key))


def _latest_seed_path(memory_root: str) -> Optional[str]:
    seeds_dir = os.path.join(memory_root, "seeds")
    if not os.path.isdir(seeds_dir):
        return None
    candidates = [
        os.path.join(seeds_dir, name) for name in os.listdir(seeds_dir) if name.endswith(".json")
    ]
    if not candidates:
        return None
    return max(candidates, key=os.path.getmtime)


def check_seed_schema(seed: Dict[str, object]) -> List[str]:
    issues: List[str] = []
    _require_keys(issues, seed, REQUIRED_TOP, IssueCode.SEED_FIELD_MISSING)

    meta = seed.get("metadata")
    if not isinstance(meta, dict):
        issues.append(issue(IssueCode.METADATA_MISSING))
    else:
        _require_keys(issues, meta, REQUIRED_META, IssueCode.METADATA_FIELD_MISSING)

    provenance = seed.get("provenance")
    if not isinstance(provenance, dict):
        issues.append(issue(IssueCode.PROVENANCE_MISSING))
    else:
        _require_keys(issues, provenance, REQUIRED_PROVENANCE, IssueCode.PROVENANCE_FIELD_MISSING)
        source = provenance.get("source")
        if not isinstance(source, dict):
            issues.append(issue(IssueCode.PROVENANCE_SOURCE_MISSING))
        else:
            _require_keys(
                issues,
                source,
                REQUIRED_PROVENANCE_SOURCE,
                IssueCode.PROVENANCE_SOURCE_FIELD_MISSING,
            )

    content = seed.get("content")
    if not isinstance(content, dict):
        issues.append(issue(IssueCode.CONTENT_MISSING))
    else:
        _require_keys(issues, content, REQUIRED_CONTENT, IssueCode.CONTENT_FIELD_MISSING)

    governance = seed.get("governance")
    if not isinstance(governance, dict):
        issues.append(issue(IssueCode.GOVERNANCE_MISSING))
    else:
        _require_keys(issues, governance, REQUIRED_GOVERNANCE, IssueCode.GOVERNANCE_FIELD_MISSING)

    anchor = seed.get("anchor")
    if not isinstance(anchor, dict):
        issues.append(issue(IssueCode.ANCHOR_MISSING))
    else:
        _require_keys(issues, anchor, REQUIRED_ANCHOR, IssueCode.ANCHOR_FIELD_MISSING)

    pointers = seed.get("pointers")
    if not isinstance(pointers, dict):
        issues.append(issue(IssueCode.POINTERS_MISSING))
    else:
        _require_keys(issues, pointers, REQUIRED_POINTERS, IssueCode.POINTERS_FIELD_MISSING)

    return issues


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate seed schema fields.")
    parser.add_argument("--seed", help="Path to a seed JSON file.")
    parser.add_argument(
        "--memory-root",
        help="Memory root to locate the latest seed (defaults to 5.2/memory).",
    )
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()
    workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    memory_root = args.memory_root or os.path.join(workspace_root, "memory")
    seed_path = args.seed or _latest_seed_path(memory_root)
    if not seed_path:
        print("No seed files found.")
        return 1
    seed = _load_json(seed_path)
    issues = check_seed_schema(seed)
    if issues:
        print(f"Seed schema FAIL: {seed_path}")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"Seed schema PASS: {seed_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
