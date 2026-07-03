"""Extract v0 accountability traces from the public, whitelisted repository sources."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVENTS_SOURCE = REPO_ROOT / "tools" / "accountability_panel" / "events.json"
JUDGMENT_SOURCE = REPO_ROOT / "docs" / "plans" / "judgment_open_vs_monopoly_2026-07-02.md"
GIT_LOG_FORMAT = (
    "%H%x00%aI%x00%(trailers:key=Agent,valueonly,separator=%x00)%x00"
    "%(trailers:key=Trace-Topic,valueonly,separator=%x00)%x00%s"
)

SCHEMA_KEYS = (
    "id",
    "trace_type",
    "occurred_at",
    "actors",
    "register",
    "claim_or_action",
    "outcome",
    "evidence_grade",
    "label_provenance",
    "source_ref",
    "links",
)

VALID_EVIDENCE_GRADES = {"E0", "E1", "E2", "E3", "E4"}
TRACE_PREFIXES = {
    "counter_evidence": "counter_evidence",
    "signed_commitment": "signed_commitment",
    "declared_stance": "declared_stance",
}

_CJK_RE = re.compile(r"[\u3400-\u9fff]")
_LATIN_RE = re.compile(r"[A-Za-z]")
_DATE_RE = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")
_JUDGMENT_RE = re.compile(r"^\*\*判決:(.*?)\*\*", re.MULTILINE)


def detect_register(text: str) -> str:
    """Return zh-TW, en, or mixed using the v0 simple CJK/Latin heuristic."""
    has_cjk = bool(_CJK_RE.search(text))
    has_latin = bool(_LATIN_RE.search(text))
    if has_cjk and has_latin:
        return "mixed"
    if has_cjk:
        return "zh-TW"
    return "en"


def extract_events(raw_events: Sequence[Mapping[str, object]] | None = None) -> list[dict]:
    """Extract counter-evidence traces from the whitelisted events ledger."""
    events = list(raw_events) if raw_events is not None else _load_events()
    traces = []
    for index, event in enumerate(events, start=1):
        claim = _as_text(event.get("claim"))
        correction = _as_text(event.get("correction"))
        outcome = event.get("outcome")
        trace = _with_id(
            {
                "trace_type": "counter_evidence",
                "occurred_at": None,
                "actors": {
                    "claimant": _as_text(event.get("lane")) or "unknown",
                    "challenger": _nullable_text(event.get("caught_by")),
                },
                "register": detect_register(" ".join([claim, correction])),
                "claim_or_action": claim,
                "outcome": _nullable_text(outcome),
                "evidence_grade": _evidence_grade(event.get("evidence_at_claim")),
                "label_provenance": "incident",
                "source_ref": f"tools/accountability_panel/events.json#{index}",
                "links": [],
            }
        )
        traces.append(trace)
    return traces


def extract_commits(git_log: str | None = None) -> list[dict]:
    """Extract signed commitments from a single git-log payload."""
    payload = git_log if git_log is not None else _load_git_log()
    traces = []
    for entry in _parse_git_log(payload):
        commit_hash, occurred_at, agent, topic, subject = entry
        if not agent:
            continue
        claim_or_action = topic or subject
        trace = _with_id(
            {
                "trace_type": "signed_commitment",
                "occurred_at": occurred_at or None,
                "actors": {"claimant": agent, "challenger": None},
                "register": detect_register(" ".join([agent, topic, subject])),
                "claim_or_action": claim_or_action,
                "outcome": subject or None,
                "evidence_grade": "unlabeled",
                "label_provenance": "incident",
                "source_ref": commit_hash,
                "links": [],
            }
        )
        traces.append(trace)
    return traces


def extract_judgments(markdown: str | None = None) -> list[dict]:
    """Extract declared stance traces from the whitelisted judgment document."""
    text = markdown if markdown is not None else _load_judgment_text()
    title = _first_heading(text)
    judgment = _first_match(_JUDGMENT_RE, text)
    blind_spot = "correlated-blind-spot" if "correlated-blind-spot" in text else None
    occurred_at = _first_match(_DATE_RE, text)
    claim_or_action = title
    if blind_spot:
        claim_or_action = f"{claim_or_action} [{blind_spot}]"
    trace = _with_id(
        {
            "trace_type": "declared_stance",
            "occurred_at": occurred_at,
            "actors": {"claimant": "honest-judgment", "challenger": "adversarial adjudication"},
            "register": detect_register(" ".join(part for part in [title, judgment or ""] if part)),
            "claim_or_action": claim_or_action,
            "outcome": judgment,
            "evidence_grade": "unlabeled",
            "label_provenance": "incident",
            "source_ref": "docs/plans/judgment_open_vs_monopoly_2026-07-02.md",
            "links": [],
        }
    )
    return [trace]


def extract_all() -> list[dict]:
    """Extract all v0 trace types in a stable source order."""
    return [*extract_events(), *extract_commits(), *extract_judgments()]


def stats_lines(traces: Sequence[Mapping[str, object]]) -> list[str]:
    """Build deterministic stats lines for the CLI --stats output."""
    counts: dict[str, int] = {}
    occurred_at_values = []
    for trace in traces:
        trace_type = _as_text(trace.get("trace_type"))
        counts[trace_type] = counts.get(trace_type, 0) + 1
        occurred_at = _nullable_text(trace.get("occurred_at"))
        if occurred_at:
            occurred_at_values.append(occurred_at)

    lines = [f"total: {len(traces)}"]
    for trace_type in sorted(counts):
        lines.append(f"{trace_type}: {counts[trace_type]}")
    if occurred_at_values:
        lines.append(f"time_range: {min(occurred_at_values)} .. {max(occurred_at_values)}")
    else:
        lines.append("time_range: null .. null")
    return lines


def write_jsonl(path: Path, traces: Sequence[Mapping[str, object]]) -> None:
    """Write UTF-8/LF JSONL with one trace per line."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(trace, ensure_ascii=False, sort_keys=False) for trace in traces]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8", newline="\n")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract ToneSoul accountability traces v0.")
    parser.add_argument("--out", type=Path, default=Path("dataset/v0/traces.jsonl"))
    parser.add_argument("--stats", action="store_true")
    args = parser.parse_args(argv)

    traces = extract_all()
    write_jsonl(args.out, traces)
    if args.stats:
        for line in stats_lines(traces):
            sys.stdout.write(f"{line}\n")
    return 0


def _load_events() -> list[dict]:
    _assert_allowed_path(EVENTS_SOURCE, EVENTS_SOURCE)
    return json.loads(EVENTS_SOURCE.read_text(encoding="utf-8"))


def _load_judgment_text() -> str:
    _assert_allowed_path(JUDGMENT_SOURCE, JUDGMENT_SOURCE)
    return JUDGMENT_SOURCE.read_text(encoding="utf-8")


def _load_git_log() -> str:
    result = subprocess.run(
        ["git", "log", "--no-merges", f"--format={GIT_LOG_FORMAT}"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout


def _assert_allowed_path(path: Path, allowed: Path) -> None:
    if path.resolve() != allowed.resolve():
        raise ValueError(f"refusing to read non-whitelisted source: {path}")


def _parse_git_log(payload: str) -> list[tuple[str, str, str, str, str]]:
    entries = []
    for raw_line in payload.splitlines():
        if not raw_line.strip():
            continue
        parts = raw_line.split("\0", 4)
        if len(parts) != 5:
            continue
        commit_hash, occurred_at, agent, topic, subject = (_clean_part(part) for part in parts)
        entries.append((commit_hash, occurred_at, agent, topic, subject))
    return entries


def _with_id(trace_without_id: Mapping[str, object]) -> dict:
    payload = json.dumps(
        trace_without_id, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    trace_type = _as_text(trace_without_id.get("trace_type"))
    prefix = TRACE_PREFIXES[trace_type]
    trace_id = f"{prefix}_{hashlib.sha256(payload.encode('utf-8')).hexdigest()[:12]}"
    return {"id": trace_id, **{key: trace_without_id[key] for key in SCHEMA_KEYS if key != "id"}}


def _evidence_grade(value: object) -> str:
    grade = _as_text(value)
    return grade if grade in VALID_EVIDENCE_GRADES else "unlabeled"


def _as_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _nullable_text(value: object) -> str | None:
    text = _as_text(value)
    return text or None


def _clean_part(value: str) -> str:
    return value.strip().replace("\r\n", "\n").replace("\r", "\n")


def _first_heading(markdown: str) -> str:
    match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
    return match.group(1).strip() if match else ""


def _first_match(pattern: re.Pattern[str], text: str) -> str | None:
    match = pattern.search(text)
    return match.group(1).strip() if match and match.groups() else match.group(0) if match else None


if __name__ == "__main__":
    raise SystemExit(main())
