"""
Commit attribution verifier.

Checks whether a commit message includes explicit multi-agent attribution
trailers. This improves traceability when multiple agents share the same
Git author identity.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from typing import Any

_AGENT_RE = re.compile(r"^Agent:\s*(.+)\s*$", re.IGNORECASE)
_TOPIC_RE = re.compile(r"^(Trace-Topic|Topic):\s*(.+)\s*$", re.IGNORECASE)


def _read_commit_message(rev: str) -> str:
    proc = subprocess.run(
        ["git", "log", "-1", "--pretty=%B", rev],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "failed to read git commit message")
    return proc.stdout


def parse_commit_message(message: str) -> dict[str, Any]:
    lines = [line.rstrip() for line in message.splitlines()]
    agent: str | None = None
    topic: str | None = None

    for line in lines:
        if agent is None:
            match_agent = _AGENT_RE.match(line)
            if match_agent:
                agent = match_agent.group(1).strip()
                continue
        if topic is None:
            match_topic = _TOPIC_RE.match(line)
            if match_topic:
                topic = match_topic.group(2).strip()
                continue

    summary = lines[0].strip() if lines else ""
    has_agent = bool(agent)
    has_topic = bool(topic)
    return {
        "ok": has_agent and has_topic,
        "summary": summary,
        "agent": agent,
        "topic": topic,
        "has_agent": has_agent,
        "has_topic": has_topic,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify commit attribution trailers.")
    parser.add_argument("--rev", default="HEAD", help="Git revision to inspect.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when attribution trailers are missing.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        message = _read_commit_message(args.rev)
    except RuntimeError as exc:
        payload = {"ok": False, "error": str(exc), "rev": args.rev}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1

    report = parse_commit_message(message)
    report["rev"] = args.rev
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if args.strict and not report["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
