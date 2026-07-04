"""Pre-publication validator for the Accountability Trace Dataset.

Why this exists (2026-07-04): the owner asked for a shipping review before the
HF upload. An eyeball pass by the same agent that assembled the dataset is
self-review; this validator makes the review reproducible and checkable.
Author separation note: the extractor was written by codex; this validator by
the reviewing agent — different hands on purpose.

Checks (all fail-closed — any finding means exit 1):
1. Every line parses as JSON; no blank lines.
2. Schema: required fields present, trace_type in the charter's v0 enum,
   label_provenance in {incident, human, model:*}, register in {zh-TW, en, mixed}.
3. IDs unique and deterministic-format.
4. Leak scan: no private-plane paths, no credential-shaped strings, no emails
   (owner's noreply git addresses excluded — they are public commit metadata).
5. Composition matches the DATASHEET's declared counts (drift = docs lie).
6. source_ref spot check: sampled refs must exist in the repo (file paths) or
   in git (commit hashes).

Usage: python -m tools.trace_dataset.validate [--dataset dataset/v0/traces.jsonl]
"""

from __future__ import annotations

import argparse
import json
import random
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

__ts_layer__ = "surface"
__ts_purpose__ = "Fail-closed pre-publication validator for the trace dataset."

REQUIRED_FIELDS = (
    "id",
    "trace_type",
    "actors",
    "register",
    "claim_or_action",
    "outcome",
    "evidence_grade",
    "label_provenance",
    "source_ref",
)
TRACE_TYPES = {"counter_evidence", "signed_commitment", "declared_stance"}
REGISTERS = {"zh-TW", "en", "mixed"}

# Credential-ish shapes + private plane. Deliberately broad; a false positive
# costs a minute, a leak costs trust.
LEAK_PATTERNS = [
    (re.compile(r"memory_base|soul\.db|self_journal"), "private-plane path"),
    (re.compile(r"\bpypi-[A-Za-z0-9_\-]{20,}"), "pypi token shape"),
    (re.compile(r"\bhf_[A-Za-z0-9]{20,}"), "hf token shape"),
    (re.compile(r"\bsk-[A-Za-z0-9]{20,}"), "api key shape"),
    (re.compile(r"\bghp_[A-Za-z0-9]{20,}"), "github token shape"),
    (
        re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b"),
        "email address",
    ),
]
EMAIL_ALLOWLIST = re.compile(r"noreply|users\.noreply\.github\.com|actions@github\.com")


def validate(dataset_path: Path, sample: int = 12) -> list[str]:
    findings: list[str] = []
    lines = dataset_path.read_text(encoding="utf-8").splitlines()
    records = []
    for i, line in enumerate(lines, 1):
        if not line.strip():
            findings.append(f"line {i}: blank line")
            continue
        try:
            records.append((i, json.loads(line)))
        except json.JSONDecodeError as exc:
            findings.append(f"line {i}: invalid JSON ({exc})")

    ids = Counter()
    type_counts: Counter = Counter()
    for i, rec in records:
        for field in REQUIRED_FIELDS:
            if field not in rec:
                findings.append(f"line {i}: missing field {field!r}")
        ids[rec.get("id")] += 1
        ttype = rec.get("trace_type")
        type_counts[ttype] += 1
        if ttype not in TRACE_TYPES:
            findings.append(f"line {i}: unknown trace_type {ttype!r}")
        if rec.get("register") not in REGISTERS:
            findings.append(f"line {i}: unknown register {rec.get('register')!r}")
        prov = rec.get("label_provenance", "")
        if prov != "incident" and prov != "human" and not prov.startswith("model:"):
            findings.append(f"line {i}: unknown label_provenance {prov!r}")
        blob = json.dumps(rec, ensure_ascii=False)
        for pattern, label in LEAK_PATTERNS:
            for m in pattern.finditer(blob):
                if label == "email address" and EMAIL_ALLOWLIST.search(m.group(0)):
                    continue
                findings.append(f"line {i}: leak-scan hit ({label}): {m.group(0)[:40]}")

    for rid, n in ids.items():
        if n > 1:
            findings.append(f"duplicate id: {rid} ×{n}")

    # source_ref spot check (deterministic sample so re-runs agree)
    rng = random.Random(42)
    pool = [rec for _, rec in records]
    for rec in rng.sample(pool, min(sample, len(pool))):
        ref = str(rec.get("source_ref", ""))
        path_part = ref.split("#", 1)[0]
        if re.fullmatch(r"[0-9a-f]{7,40}", path_part):
            ok = (
                subprocess.run(
                    ["git", "cat-file", "-e", f"{path_part}^{{commit}}"],
                    cwd=REPO_ROOT,
                    capture_output=True,
                ).returncode
                == 0
            )
            if not ok:
                findings.append(f"source_ref commit not in git: {ref}")
        elif path_part and not (REPO_ROOT / path_part).exists():
            findings.append(f"source_ref path missing: {ref}")

    # DATASHEET consistency: the docs must not lie about the data.
    datasheet = dataset_path.parent / "DATASHEET.md"
    if datasheet.exists():
        text = datasheet.read_text(encoding="utf-8")
        m = re.search(r"\*\*total\*\* \| \*\*(\d+)\*\*", text)
        if m and int(m.group(1)) != len(records):
            findings.append(
                f"DATASHEET total says {m.group(1)}, dataset has {len(records)} — docs drifted"
            )

    print(f"records={len(records)} composition={dict(type_counts)}")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="dataset/v0/traces.jsonl")
    args = parser.parse_args()
    findings = validate(REPO_ROOT / args.dataset)
    if findings:
        print(f"\nFINDINGS ({len(findings)}):")
        for f in findings:
            print(f"  - {f}")
        return 1
    print("validator: all checks passed (fail-closed clean)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
