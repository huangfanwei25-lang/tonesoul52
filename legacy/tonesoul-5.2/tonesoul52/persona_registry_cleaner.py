import json
import os
from collections import Counter
from typing import List


REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
SOURCE_PATH = os.path.join(REPORTS_DIR, "persona_registry_extended.json")
OUTPUT_PATH = os.path.join(REPORTS_DIR, "persona_registry_cleaned.json")
SUMMARY_PATH = os.path.join(REPORTS_DIR, "persona_registry_cleaned.md")


def _normalize(name: str) -> str:
    return name.strip().lower()


def main() -> int:
    if not os.path.exists(SOURCE_PATH):
        print(f"Missing registry: {SOURCE_PATH}")
        return 1

    with open(SOURCE_PATH, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    registry = payload.get("registry", [])
    merged = {}

    for entry in registry:
        name = entry.get("name", "")
        if not name:
            continue
        key = _normalize(name)
        rec = merged.setdefault(key, {
            "name": name,
            "roles": set(),
            "sources": set(),
            "notes": set(),
        })
        role = entry.get("role", "unknown")
        if role:
            rec["roles"].add(role)
        src = entry.get("source", "")
        if src:
            rec["sources"].add(src)
        note = entry.get("notes", "")
        if note:
            rec["notes"].add(note)

    cleaned = []
    for rec in merged.values():
        cleaned.append({
            "name": rec["name"],
            "roles": sorted(rec["roles"]),
            "sources": sorted(rec["sources"]),
            "notes": sorted(rec["notes"]),
        })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as handle:
        json.dump({"schema_version": "1.0", "registry": cleaned}, handle, indent=2, ensure_ascii=False)

    role_counter = Counter()
    note_counter = Counter()
    for c in cleaned:
        for r in c["roles"]:
            role_counter[r] += 1
        for n in c["notes"]:
            note_counter[n] += 1

    lines: List[str] = []
    lines.append("# Persona Registry Cleaned")
    lines.append("")
    lines.append(f"Total unique personas: {len(cleaned)}")
    lines.append("")
    lines.append("## Role Distribution")
    for role, count in role_counter.most_common():
        lines.append(f"- {role}: {count}")
    lines.append("")
    lines.append("## Notes Distribution")
    for note, count in note_counter.most_common():
        label = note or "(none)"
        lines.append(f"- {label}: {count}")

    with open(SUMMARY_PATH, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))

    print(f"Cleaned registry: {OUTPUT_PATH}")
    print(f"Summary: {SUMMARY_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
