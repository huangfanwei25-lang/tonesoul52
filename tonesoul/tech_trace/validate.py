import argparse
import json
import os
from typing import Dict, List, Set

from ..issue_codes import IssueCode, issue


def _load_json(path: str) -> Dict[str, object]:
    with open(path, "r", encoding="utf-8-sig") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Normalize payload must be a JSON object.")
    return payload


def _validate_claims(payload: Dict[str, object], issues: List[str]) -> Set[str]:
    claim_ids: Set[str] = set()
    claims = payload.get("claims")
    if claims is None:
        return claim_ids
    if not isinstance(claims, list):
        issues.append(issue(IssueCode.CLAIMS_NOT_LIST))
        return claim_ids
    for idx, item in enumerate(claims):
        if not isinstance(item, dict):
            issues.append(issue(IssueCode.CLAIM_INDEX_NOT_OBJECT, index=idx))
            continue
        text = item.get("text") or item.get("claim") or item.get("statement")
        if not isinstance(text, str) or not text.strip():
            issues.append(issue(IssueCode.CLAIM_INDEX_TEXT_MISSING, index=idx))
        claim_id = item.get("id")
        if isinstance(claim_id, str) and claim_id:
            claim_ids.add(claim_id)
    return claim_ids


def _validate_links(payload: Dict[str, object], issues: List[str]) -> None:
    links = payload.get("links")
    if links is None:
        return
    if not isinstance(links, list):
        issues.append(issue(IssueCode.LINKS_NOT_LIST))
        return
    for idx, item in enumerate(links):
        if not isinstance(item, dict):
            issues.append(issue(IssueCode.LINK_INDEX_NOT_OBJECT, index=idx))
            continue
        uri = item.get("uri") or item.get("url")
        if not isinstance(uri, str) or not uri.strip():
            issues.append(issue(IssueCode.LINK_INDEX_URI_MISSING, index=idx))


def _validate_attributions(
    payload: Dict[str, object],
    claim_ids: Set[str],
    issues: List[str],
    strict: bool,
) -> None:
    attributions = payload.get("attributions")
    if attributions is None:
        return
    if not isinstance(attributions, list):
        issues.append(issue(IssueCode.ATTRIBUTIONS_NOT_LIST))
        return
    if strict and attributions and not claim_ids:
        issues.append(issue(IssueCode.ATTRIBUTIONS_CLAIMS_MISSING))
    for idx, item in enumerate(attributions):
        if not isinstance(item, dict):
            issues.append(issue(IssueCode.ATTRIBUTION_INDEX_NOT_OBJECT, index=idx))
            continue
        source_ref = item.get("source_ref") or item.get("reference") or item.get("uri")
        if not isinstance(source_ref, str) or not source_ref.strip():
            issues.append(issue(IssueCode.ATTRIBUTION_INDEX_SOURCE_REF_MISSING, index=idx))
        claim_id = item.get("claim_id")
        if strict and claim_ids and claim_id is None:
            issues.append(issue(IssueCode.ATTRIBUTION_INDEX_CLAIM_ID_MISSING, index=idx))
        if claim_id is not None and (not isinstance(claim_id, str) or not claim_id.strip()):
            issues.append(issue(IssueCode.ATTRIBUTION_INDEX_CLAIM_ID_INVALID, index=idx))
        if (
            strict
            and claim_ids
            and isinstance(claim_id, str)
            and claim_id
            and claim_id not in claim_ids
        ):
            issues.append(issue(IssueCode.ATTRIBUTION_INDEX_CLAIM_ID_UNKNOWN, index=idx))


def validate_normalize_payload(payload: Dict[str, object], strict: bool = False) -> List[str]:
    issues: List[str] = []
    claim_ids = _validate_claims(payload, issues)
    _validate_links(payload, issues)
    _validate_attributions(payload, claim_ids, issues, strict)
    return issues


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate Tech-Trace normalized payloads.")
    parser.add_argument("--normalize", required=True, help="Path to normalized JSON payload.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Require attributions to reference known claim ids when claims are present.",
    )
    parser.add_argument("--output", help="Optional output JSON path.")
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()
    try:
        payload = _load_json(args.normalize)
    except Exception as exc:
        parser.error(str(exc))
    issues = validate_normalize_payload(payload, strict=args.strict)
    result = {
        "normalize_path": args.normalize,
        "strict": args.strict,
        "passed": not issues,
        "issue_count": len(issues),
        "issues": issues,
    }
    if args.output:
        output_path = args.output
        if output_path:
            output_path = os.path.abspath(output_path)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as handle:
                json.dump(result, handle, indent=2)
    if issues:
        print(f"Tech-Trace normalize validation FAIL: {args.normalize}")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"Tech-Trace normalize validation PASS: {args.normalize}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
