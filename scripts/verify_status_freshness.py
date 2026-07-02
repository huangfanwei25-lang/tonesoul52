"""
Verify freshness of docs/status/*_latest.* accountability artifacts.

Why this exists (2026-07-02): an external audit found abc_firewall_latest.md
(generated 2026-03-22, ok=true) masking a live regression — two entrypoint
docs had lost their doctrine references while the committed artifact still
said 7/7 pass. A system whose core claim is auditability cannot let its own
audit artifacts silently expire. This verifier makes staleness itself a
checkable, fail-able condition ("Claim <= Evidence" applied to evidence age).

Classification (measured against the actual artifact population, 2026-07-02):
- assertive: the JSON carries an ok-style verdict field (ok / overall_ok /
  status_ok / passed). These assert something about *current* repo state; a
  stale ok=true is exactly the pathology above. Budget: --assertive-max-age
  (default 45 days). Stale assertive artifacts fail under --strict.
- episodic: everything else (characterizations, snapshots, inventories).
  `_latest` there means "last run of a series", not "current truth".
  Budget: --episodic-max-age (default 120 days). Stale episodic artifacts
  warn only.
- untimestamped: no recognizable timestamp, or timestamp is null. Always a
  warning; fails under --strict when the artifact is assertive, because an
  undated verdict cannot serve as evidence.
- future-dated: timestamp is ahead of now (typo'd year, timezone confusion).
  Treated like untimestamped — a verdict dated from the future would otherwise
  be immune to this check for its whole future window, which is exactly the
  masking pathology this verifier exists to catch.

Timestamp fields accepted (top level): generated_at, as_of, timestamp,
updated_at, generated_on, last_updated, date. Date-only values are treated
as midnight UTC of that day.

Scope: *_latest.json and *_latest.md only (other extensions — .jsonl/.html/.mmd —
are data/diagram surfaces, not verdict artifacts). Staleness is measured in whole
days and begins strictly after the budget (an artifact aged 45d23h with a 45-day
budget is still fresh; the direction of the rounding is lenient, never early).

Exit codes: 0 ok; 1 failures found and --strict given.

Usage:
    python scripts/verify_status_freshness.py
    python scripts/verify_status_freshness.py --strict --assertive-max-age 30
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STATUS_DIR = REPO_ROOT / "docs" / "status"

JSON_FILENAME = "status_freshness_latest.json"
MARKDOWN_FILENAME = "status_freshness_latest.md"

TIMESTAMP_KEYS = (
    "generated_at",
    "as_of",
    "timestamp",
    "updated_at",
    "generated_on",
    "last_updated",
    "date",
)
VERDICT_KEYS = ("ok", "overall_ok", "status_ok", "passed")

# The verifier's own outputs are regenerated on every run; auditing them here
# would only ever report "fresh" and adds noise, not assurance.
SELF_PATHS = (JSON_FILENAME, MARKDOWN_FILENAME)

# Line-anchored (a mid-prose quote of another artifact's timestamp must not date this
# one), tolerant of list/bold markup, and offset-preserving (+08:00 is not UTC).
MD_TS_PATTERN = re.compile(
    r"(?m)^[\s>*`-]{0,8}\*{0,2}(?:generated_at|Generated)\*{0,2}:\*{0,2}\s*`?"
    r"(\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:\d{2})?)?)"
)


@dataclass(frozen=True)
class ArtifactVerdict:
    path: str
    kind: str  # assertive | episodic
    timestamp: str | None
    timestamp_field: str | None
    age_days: int | None
    verdict: str  # fresh | stale | untimestamped
    note: str = ""


def _parse_timestamp(raw: object) -> datetime | None:
    if not isinstance(raw, str) or not raw.strip():
        return None
    value = raw.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _extract_json_timestamp(data: object) -> tuple[datetime | None, str | None]:
    if not isinstance(data, dict):
        return None, None
    for key in TIMESTAMP_KEYS:
        if key in data:
            parsed = _parse_timestamp(data.get(key))
            if parsed is not None:
                return parsed, key
    return None, None


def _extract_md_timestamp(text: str) -> datetime | None:
    match = MD_TS_PATTERN.search(text[:4000])
    if not match:
        return None
    return _parse_timestamp(match.group(1))


def _classify(data: object) -> str:
    if isinstance(data, dict) and any(key in data for key in VERDICT_KEYS):
        return "assertive"
    return "episodic"


def evaluate(
    now: datetime,
    assertive_max_age: int,
    episodic_max_age: int,
    status_dir: Path = STATUS_DIR,
    repo_root: Path = REPO_ROOT,
) -> list[ArtifactVerdict]:
    verdicts: list[ArtifactVerdict] = []
    for path in sorted(status_dir.glob("*_latest.json")):
        if path.name in SELF_PATHS:
            continue
        rel = path.relative_to(repo_root).as_posix()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        # ValueError covers JSONDecodeError AND UnicodeDecodeError (e.g. a UTF-16
        # artifact from PowerShell) — one bad file must not abort the whole sweep.
        except (ValueError, OSError) as exc:
            verdicts.append(
                ArtifactVerdict(
                    rel, "assertive", None, None, None, "untimestamped", f"unreadable: {exc}"
                )
            )
            continue
        kind = _classify(data)
        stamp, field = _extract_json_timestamp(data)
        if stamp is None:
            note = (
                "timestamp field present but null"
                if (isinstance(data, dict) and any(k in data for k in TIMESTAMP_KEYS))
                else "no recognizable timestamp field"
            )
            verdicts.append(ArtifactVerdict(rel, kind, None, None, None, "untimestamped", note))
            continue
        age = (now - stamp).days
        budget = assertive_max_age if kind == "assertive" else episodic_max_age
        if age < 0:
            verdict, note = "future-dated", "timestamp is ahead of now"
        else:
            verdict, note = ("stale" if age > budget else "fresh"), ""
        verdicts.append(ArtifactVerdict(rel, kind, stamp.isoformat(), field, age, verdict, note))

    # Markdown-only artifacts (no JSON twin): check via inline timestamp.
    for path in sorted(status_dir.glob("*_latest.md")):
        if path.name in SELF_PATHS:
            continue
        if path.with_suffix(".json").exists():
            continue  # twin already judged via JSON
        rel = path.relative_to(repo_root).as_posix()
        stamp = _extract_md_timestamp(path.read_text(encoding="utf-8", errors="replace"))
        if stamp is None:
            verdicts.append(
                ArtifactVerdict(
                    rel, "episodic", None, None, None, "untimestamped", "no generated_at line"
                )
            )
            continue
        age = (now - stamp).days
        if age < 0:
            verdict, note = "future-dated", "timestamp is ahead of now"
        else:
            verdict, note = ("stale" if age > episodic_max_age else "fresh"), ""
        verdicts.append(
            ArtifactVerdict(rel, "episodic", stamp.isoformat(), "md_inline", age, verdict, note)
        )
    return verdicts


def build_payload(
    verdicts: list[ArtifactVerdict],
    now: datetime,
    assertive_max_age: int,
    episodic_max_age: int,
) -> dict:
    stale_assertive = [v for v in verdicts if v.verdict == "stale" and v.kind == "assertive"]
    stale_episodic = [v for v in verdicts if v.verdict == "stale" and v.kind == "episodic"]
    untimestamped_assertive = [
        v for v in verdicts if v.verdict == "untimestamped" and v.kind == "assertive"
    ]
    untimestamped_episodic = [
        v for v in verdicts if v.verdict == "untimestamped" and v.kind == "episodic"
    ]
    future_assertive = [
        v for v in verdicts if v.verdict == "future-dated" and v.kind == "assertive"
    ]
    future_episodic = [v for v in verdicts if v.verdict == "future-dated" and v.kind == "episodic"]
    failures = len(stale_assertive) + len(untimestamped_assertive) + len(future_assertive)
    return {
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "scripts/verify_status_freshness.py",
        "overall_ok": failures == 0,
        "policy": {
            "assertive_max_age_days": assertive_max_age,
            "episodic_max_age_days": episodic_max_age,
            "assertive_marker": list(VERDICT_KEYS),
            "timestamp_fields": list(TIMESTAMP_KEYS),
        },
        "summary": {
            "artifact_count": len(verdicts),
            "fresh": sum(1 for v in verdicts if v.verdict == "fresh"),
            "stale_assertive": len(stale_assertive),
            "stale_episodic": len(stale_episodic),
            "untimestamped_assertive": len(untimestamped_assertive),
            "untimestamped_episodic": len(untimestamped_episodic),
            "future_dated_assertive": len(future_assertive),
            "future_dated_episodic": len(future_episodic),
            "failure_count": failures,
        },
        "failures": [
            asdict(v) for v in stale_assertive + untimestamped_assertive + future_assertive
        ],
        "warnings": [asdict(v) for v in stale_episodic + untimestamped_episodic + future_episodic],
        "entries": [asdict(v) for v in verdicts],
    }


def _render_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Status Artifact Freshness",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- overall_ok: `{str(payload['overall_ok']).lower()}`",
        f"- policy: assertive<= {payload['policy']['assertive_max_age_days']}d,"
        f" episodic<= {payload['policy']['episodic_max_age_days']}d",
        f"- artifacts: {summary['artifact_count']}"
        f" (fresh {summary['fresh']},"
        f" stale assertive {summary['stale_assertive']},"
        f" stale episodic {summary['stale_episodic']},"
        f" untimestamped {summary['untimestamped_assertive'] + summary['untimestamped_episodic']})",
        "",
    ]
    if payload["failures"]:
        lines.append("## Failures (stale, undated, or future-dated assertive artifacts)")
        lines.append("")
        lines.append("| artifact | age (days) | issue |")
        lines.append("|---|---|---|")
        for entry in payload["failures"]:
            age = entry["age_days"] if entry["age_days"] is not None else "—"
            issue = entry["verdict"] + (f" ({entry['note']})" if entry["note"] else "")
            lines.append(f"| {entry['path']} | {age} | {issue} |")
        lines.append("")
    if payload["warnings"]:
        lines.append("## Warnings (episodic)")
        lines.append("")
        lines.append("| artifact | age (days) | issue |")
        lines.append("|---|---|---|")
        for entry in payload["warnings"]:
            age = entry["age_days"] if entry["age_days"] is not None else "—"
            issue = entry["verdict"] + (f" ({entry['note']})" if entry["note"] else "")
            lines.append(f"| {entry['path']} | {age} | {issue} |")
        lines.append("")
    lines.append(
        "A stale assertive artifact is treated as a failure because an expired"
        " `ok=true` can mask a live regression (incident of 2026-07-02,"
        " abc_firewall). Regenerate via the owning script, or rename one-off"
        " records from `*_latest.*` to dated filenames so they leave the"
        " freshness contract."
    )
    lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify docs/status/*_latest.* artifacts are fresh enough to serve as evidence."
    )
    parser.add_argument("--assertive-max-age", type=int, default=45, metavar="DAYS")
    parser.add_argument("--episodic-max-age", type=int, default=120, metavar="DAYS")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 when any assertive artifact is stale or undated.",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Report only; do not update docs/status/status_freshness_latest.*",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    now = datetime.now(timezone.utc)
    verdicts = evaluate(now, args.assertive_max_age, args.episodic_max_age)
    payload = build_payload(verdicts, now, args.assertive_max_age, args.episodic_max_age)
    if not args.no_write:
        (STATUS_DIR / JSON_FILENAME).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        (STATUS_DIR / MARKDOWN_FILENAME).write_text(
            _render_markdown(payload), encoding="utf-8", newline="\n"
        )
    summary = payload["summary"]
    print(
        "status_freshness "
        f"ok={str(payload['overall_ok']).lower()} "
        f"artifacts={summary['artifact_count']} fresh={summary['fresh']} "
        f"stale_assertive={summary['stale_assertive']} "
        f"stale_episodic={summary['stale_episodic']} "
        f"untimestamped={summary['untimestamped_assertive'] + summary['untimestamped_episodic']}"
    )
    for entry in payload["failures"]:
        age = entry["age_days"] if entry["age_days"] is not None else "?"
        print(f"  FAIL {entry['path']} age={age}d {entry['note']}".rstrip())
    if args.strict and not payload["overall_ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
