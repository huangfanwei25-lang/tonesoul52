#!/usr/bin/env python3
"""Run the bounded ToneSoul publish/push posture preflight."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the ToneSoul publish/push posture preflight.",
    )
    parser.add_argument("--agent", default="publish-push-preflight")
    parser.add_argument("--state-path", type=Path, default=None)
    parser.add_argument("--traces-path", type=Path, default=None)
    parser.add_argument(
        "--owner-review-ref",
        default=None,
        help="Source reference declaring bounded owner review; this is not identity verification.",
    )
    parser.add_argument(
        "--grant-ref",
        default=None,
        help="Scoped grant source reference propagated by the caller.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero unless the computed publish posture is clear.",
    )
    return parser


def _source_ref(value: str | None) -> str | None:
    raw = str(value or "")
    normalized = raw.strip()
    if not normalized or normalized != raw or len(normalized) > 256:
        return None
    if any(ord(char) < 32 or ord(char) == 127 for char in normalized):
        return None
    return normalized


def resolve_preflight(
    *,
    classification: str,
    owner_review_ref: str | None,
    grant_ref: str | None,
) -> dict[str, object]:
    """Project posture plus a declared review source without overriding a block."""
    normalized_owner_ref = _source_ref(owner_review_ref)
    normalized_grant_ref = _source_ref(grant_ref)
    if classification == "blocked":
        status = "blocked"
        publish_ready = False
    elif classification == "clear":
        status = "clear"
        publish_ready = True
    elif classification == "review_before_push" and normalized_owner_ref:
        status = "bounded_owner_review_resolved"
        publish_ready = True
    else:
        status = "review_required"
        publish_ready = False
    return {
        "status": status,
        "publish_ready": publish_ready,
        "owner_review_ref": normalized_owner_ref,
        "grant_ref": normalized_grant_ref,
        "assurance": "declared_source_not_identity_verified",
        "blocked_override_allowed": False,
    }


def run_publish_push_preflight(
    *,
    agent: str,
    state_path: Path | None = None,
    traces_path: Path | None = None,
    owner_review_ref: str | None = None,
    grant_ref: str | None = None,
) -> dict[str, object]:
    from scripts.start_agent_session import run_session_start_bundle
    from tonesoul.publish_push_preflight import build_publish_push_preflight

    payload = run_session_start_bundle(
        agent_id=agent,
        state_path=state_path,
        traces_path=traces_path,
        no_ack=True,
    )

    readiness = payload.get("readiness") or {}
    import_posture = payload.get("import_posture") or {}
    repo_state_awareness = payload.get("repo_state_awareness") or {}
    preflight = build_publish_push_preflight(
        readiness=readiness,
        import_posture=import_posture,
        repo_state_awareness=repo_state_awareness,
    )
    resolution = resolve_preflight(
        classification=str(preflight.get("classification", "unknown") or "unknown"),
        owner_review_ref=owner_review_ref,
        grant_ref=grant_ref,
    )

    return {
        "contract_version": "v1",
        "bundle": "publish_push_preflight",
        "agent": agent,
        "readiness": str(readiness.get("status", "unknown") or "unknown"),
        "repo_state": str(repo_state_awareness.get("classification", "unknown") or "unknown"),
        "launch_tier": str(
            (
                ((import_posture.get("surfaces") or {}).get("launch_claims") or {}).get(
                    "launch_claim_posture"
                )
                or {}
            ).get("current_tier", "unknown")
            or "unknown"
        ),
        "preflight": preflight,
        "resolution": resolution,
        "underlying_commands": [
            f"python scripts/start_agent_session.py --agent {agent} --no-ack",
            f"python scripts/run_publish_push_preflight.py --agent {agent}",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    payload = run_publish_push_preflight(
        agent=str(args.agent).strip(),
        state_path=args.state_path,
        traces_path=args.traces_path,
        owner_review_ref=args.owner_review_ref,
        grant_ref=args.grant_ref,
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    if args.strict and not (payload.get("resolution") or {}).get("publish_ready"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
