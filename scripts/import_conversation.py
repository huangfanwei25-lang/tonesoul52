#!/usr/bin/env python3
"""Import external AI conversations into ToneSoul session traces.

Parses exported conversations from ChatGPT, Claude, or plain markdown,
extracts tension events, key decisions, and stance shifts, then outputs
session_trace.json files compatible with update_governance_state.py.

Usage:
    # Import ChatGPT export
    python scripts/import_conversation.py --input conversations.json --format chatgpt

    # Import markdown conversation log
    python scripts/import_conversation.py --input chat.md --format markdown

    # Import and immediately update governance state
    python scripts/import_conversation.py --input conversations.json --format chatgpt \
        --update-state ./governance_state.json

    # Dry run — show what would be extracted
    python scripts/import_conversation.py --input conversations.json --format chatgpt --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# --- Tension scoring heuristics ---

DISAGREEMENT_PATTERNS = re.compile(
    r"\b(but|however|disagree|incorrect|actually|not quite|that'?s wrong|"
    r"但是|不過|不對|其實不是|我不同意|不是|而是|不主張|不等於|並非)\b",
    re.IGNORECASE,
)

DIRECTION_CHANGE_PATTERNS = re.compile(
    r"\b(on second thought|wait|actually|let me reconsider|changed?'?s? my mind|"
    r"換個角度|重新想|其實|等等)\b",
    re.IGNORECASE,
)

SAFETY_PATTERNS = re.compile(
    r"\b(dangerous|risk|careful|unsafe|security|vulnerability|warning|caution|"
    r"危險|風險|小心|安全|漏洞|警告|不可|不得|禁止|護欄|治理|問責|誠實|穩定|責任|承擔)\b",
    re.IGNORECASE,
)

COMMITMENT_PATTERNS = re.compile(
    r"\b(I promise|I will always|I commit|never again|from now on|"
    r"我承諾|我保證|以後一定|絕對不|從現在開始|必須|誓言|承諾|不可逆|核心信念)\b",
    re.IGNORECASE,
)

DECISION_PATTERNS = re.compile(
    r"\b(decided|chose|will do|let'?s go with|the plan is|going to|"
    r"決定|選擇|就這樣做|計劃是|開始做|演化為|對應|實作|定義|規格)\b",
    re.IGNORECASE,
)

QUESTION_PATTERN = re.compile(r"\?\s*$", re.MULTILINE)


def score_tension(text: str) -> float:
    """Score tension severity 0-1 from message text."""
    score = 0.10  # baseline

    if DISAGREEMENT_PATTERNS.search(text):
        score += 0.15
    if DIRECTION_CHANGE_PATTERNS.search(text):
        score += 0.10
    if SAFETY_PATTERNS.search(text):
        score += 0.20
    if COMMITMENT_PATTERNS.search(text):
        score += 0.05

    questions = len(QUESTION_PATTERN.findall(text))
    if questions >= 3:
        score += 0.05

    return min(score, 1.0)


def extract_topic(text: str, max_len: int = 80) -> str:
    """Extract a short topic from message text."""
    # Take first sentence or line
    for sep in ["。", ".", "\n"]:
        idx: int = text.find(sep)
        if 0 < idx < max_len * 2:
            prefix: str = text[:idx].strip()
            return prefix[:max_len]
    trimmed: str = text.strip()
    return trimmed[:max_len]


def classify_memory(text: str) -> str:
    """Classify memory tier: factual, experiential, or governance."""
    if SAFETY_PATTERNS.search(text) or COMMITMENT_PATTERNS.search(text):
        return "governance"
    if DISAGREEMENT_PATTERNS.search(text) or DIRECTION_CHANGE_PATTERNS.search(text):
        return "experiential"
    return "factual"


def detect_stance_shift(messages: list[dict]) -> dict | None:
    """Detect if there was a significant stance shift in conversation."""
    shifts = []
    for msg in messages:
        text = msg.get("text", "")
        if DIRECTION_CHANGE_PATTERNS.search(text):
            shifts.append(text)
    if len(shifts) >= 2:
        return {
            "from": extract_topic(shifts[0], 60),
            "to": extract_topic(shifts[-1], 60),
        }
    return None


# --- Parsers ---


def parse_chatgpt_json(data: Any) -> list[dict]:
    """Parse ChatGPT conversations.json export."""
    conversations = []
    items = data if isinstance(data, list) else [data]

    for conv in items:
        title = conv.get("title", "Untitled")
        messages = []
        create_time = conv.get("create_time", 0)

        mapping = conv.get("mapping", {})
        for node in mapping.values():
            msg = node.get("message")
            if msg and msg.get("content", {}).get("parts"):
                role = msg.get("author", {}).get("role", "unknown")
                text = "\n".join(p for p in msg["content"]["parts"] if isinstance(p, str))
                if text.strip():
                    messages.append(
                        {
                            "role": role,
                            "text": text,
                            "timestamp": msg.get("create_time", create_time),
                        }
                    )

        if messages:
            conversations.append(
                {
                    "title": title,
                    "messages": messages,
                    "timestamp": create_time,
                }
            )

    return conversations


def parse_markdown(text: str) -> list[dict]:
    """Parse markdown conversation log.

    Expected format:
        ## Human / User / 你
        message text

        ## Assistant / AI / Claude / GPT
        response text
    """
    messages = []
    role_pattern = re.compile(
        r"^##?\s*(Human|User|你|Assistant|AI|Claude|GPT|Antigravity|Codex)",
        re.IGNORECASE | re.MULTILINE,
    )

    parts = role_pattern.split(text)
    for i in range(1, len(parts), 2):
        role_raw = parts[i].strip().lower()
        content = parts[i + 1].strip() if i + 1 < len(parts) else ""
        role = "user" if role_raw in ("human", "user", "你") else "assistant"
        if content:
            messages.append({"role": role, "text": content})

    if messages:
        return [{"title": "Imported markdown", "messages": messages, "timestamp": 0}]
    return []


def parse_document(text: str, filename: str = "unknown") -> list[dict]:
    """Parse a structured markdown document (specs, philosophy, notes).

    Splits by ## headings and treats each section as a pseudo-message.
    This is for importing GPT語場 spec documents, not conversation logs.
    """
    section_pattern = re.compile(r"^##?\s+(.+)$", re.MULTILINE)
    parts = section_pattern.split(text)

    messages = []
    # parts[0] is text before first heading
    if parts[0].strip():
        messages.append({"role": "assistant", "text": parts[0].strip()})

    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        content = parts[i + 1].strip() if i + 1 < len(parts) else ""
        if content and len(content) > 20:  # skip tiny sections
            messages.append(
                {
                    "role": "assistant",
                    "text": f"{heading}\n{content}",
                }
            )

    title = filename
    # Try to extract title from first line
    first_line = text.strip().split("\n")[0].strip().lstrip("# ")
    if first_line:
        title = first_line[:60]

    if messages:
        return [{"title": title, "messages": messages, "timestamp": 0}]
    return []


def parse_jsonl(text: str) -> list[dict]:
    """Parse JSONL format (one JSON message per line)."""
    messages = []
    for line in text.strip().split("\n"):
        line = line.strip()
        if line:
            try:
                msg = json.loads(line)
                messages.append(
                    {
                        "role": msg.get("role", "unknown"),
                        "text": msg.get("content", msg.get("text", "")),
                    }
                )
            except json.JSONDecodeError:
                continue

    if messages:
        return [{"title": "Imported JSONL", "messages": messages, "timestamp": 0}]
    return []


# --- Distillation ---


def distill_conversation(conv: dict) -> dict:
    """Distill a conversation into a session_trace record."""
    messages = conv.get("messages", [])
    all_text = " ".join(m.get("text", "") for m in messages)

    # Extract tension events from high-tension messages
    tension_events: list[dict[str, Any]] = []
    for msg in messages:
        text = msg.get("text", "")
        severity = score_tension(text)
        if severity > 0.20:  # only notable tensions
            tension_events.append(
                {
                    "topic": extract_topic(text),
                    "severity": float(round(severity * 100)) / 100,
                    "type": classify_memory(text),
                    "resolution": "",
                }
            )

    # Cap to top 5 by severity
    tension_events.sort(key=lambda t: t["severity"], reverse=True)
    while len(tension_events) > 5:
        tension_events.pop()

    # Extract key decisions
    decisions: list[str] = []
    for msg in messages:
        text = msg.get("text", "")
        if DECISION_PATTERNS.search(text):
            decisions.append(extract_topic(text, 100))
    while len(decisions) > 5:
        decisions.pop()

    # Detect stance shift
    stance_shift = detect_stance_shift(messages)

    # Detect vow events
    vow_events = []
    for msg in messages:
        text = msg.get("text", "")
        if COMMITMENT_PATTERNS.search(text):
            vow_events.append(
                {
                    "vow_id": f"imported-{len(vow_events) + 1}",
                    "action": "created",
                    "detail": extract_topic(text, 100),
                }
            )

    # Timestamp
    ts = conv.get("timestamp", 0)
    if isinstance(ts, (int, float)) and ts > 0:
        timestamp = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    else:
        timestamp = datetime.now(timezone.utc).isoformat()

    return {
        "session_id": f"import-{conv.get('title', 'unknown')[:30]}",
        "agent": "imported",
        "timestamp": timestamp,
        "duration_minutes": 0,
        "tension_events": tension_events,
        "vow_events": vow_events,
        "aegis_vetoes": [],
        "key_decisions": decisions,
        "stance_shift": stance_shift or {},
        "source": {
            "type": "external_import",
            "title": conv.get("title", ""),
            "message_count": len(messages),
        },
    }


# --- Main ---


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import external AI conversations into ToneSoul traces"
    )
    parser.add_argument("--input", type=Path, required=True, help="Input file path")
    parser.add_argument(
        "--format",
        choices=["chatgpt", "markdown", "document", "jsonl", "auto"],
        default="auto",
        help="Input format (default: auto-detect)",
    )
    parser.add_argument("--output", type=Path, default=None, help="Output directory for traces")
    parser.add_argument(
        "--update-state", type=Path, default=None, help="Directly update this governance_state.json"
    )
    parser.add_argument("--dry-run", action="store_true", help="Show extraction without writing")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"ERROR: Input file not found: {args.input}")
        sys.exit(1)

    raw = args.input.read_text(encoding="utf-8")

    # Auto-detect format
    fmt = args.format
    if fmt == "auto":
        if args.input.suffix == ".json":
            fmt = "chatgpt"
        elif args.input.suffix in (".md", ".txt"):
            fmt = "markdown"
        elif args.input.suffix == ".jsonl":
            fmt = "jsonl"
        else:
            print("ERROR: Cannot auto-detect format. Use --format.")
            sys.exit(1)

    # Parse
    if fmt == "chatgpt":
        conversations = parse_chatgpt_json(json.loads(raw))
    elif fmt == "markdown":
        conversations = parse_markdown(raw)
        if not conversations:
            # Fallback: try document parser
            conversations = parse_document(raw, args.input.stem)
    elif fmt == "document":
        conversations = parse_document(raw, args.input.stem)
    elif fmt == "jsonl":
        conversations = parse_jsonl(raw)
    else:
        print(f"ERROR: Unknown format: {fmt}")
        sys.exit(1)

    if not conversations:
        print("No conversations found in input.")
        sys.exit(0)

    print(f"Found {len(conversations)} conversation(s)")

    # Distill
    traces = [distill_conversation(c) for c in conversations]

    # Filter out empty traces
    traces = [t for t in traces if t["tension_events"] or t["key_decisions"] or t["vow_events"]]

    print(f"Distilled {len(traces)} trace(s) with governance content")

    if args.dry_run:
        for t in traces:
            print(f"\n--- {t['session_id']} ---")
            print(f"  Tensions: {len(t['tension_events'])}")
            for te in t["tension_events"]:
                print(f"    [{te['severity']:.2f}] {te['topic'][:60]}")
            print(f"  Decisions: {len(t['key_decisions'])}")
            for d in t["key_decisions"]:
                print(f"    - {d[:60]}")
            if t.get("vow_events"):
                print(f"  Vows: {len(t['vow_events'])}")
            if t.get("stance_shift"):
                print(f"  Shift: {t['stance_shift']}")
        return

    # Write traces
    if args.output:
        args.output.mkdir(parents=True, exist_ok=True)
        for i, trace in enumerate(traces):
            out_file = args.output / f"trace_{i:03d}.json"
            out_file.write_text(
                json.dumps(trace, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            print(f"  Written: {out_file}")

    # Update governance state directly
    if args.update_state:
        for trace in traces:
            trace_json = json.dumps(trace, ensure_ascii=False)
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/update_governance_state.py",
                    "--state",
                    str(args.update_state),
                    "--stdin",
                ],
                input=trace_json,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print(f"  State updated from: {trace['session_id']}")
            else:
                print(f"  ERROR updating from {trace['session_id']}: {result.stderr}")

    if not args.output and not args.update_state:
        # Default: print to stdout
        print(json.dumps(traces, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
