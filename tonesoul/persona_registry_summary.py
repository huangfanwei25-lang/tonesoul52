import json
import os
from collections import Counter

REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
REGISTRY_PATH = os.path.join(REPORTS_DIR, "persona_registry_extended.json")
OUTPUT_PATH = os.path.join(REPORTS_DIR, "persona_registry_summary.md")


def main() -> int:
    if not os.path.exists(REGISTRY_PATH):
        print(f"Missing registry: {REGISTRY_PATH}")
        return 1

    with open(REGISTRY_PATH, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    registry = payload.get("registry", [])
    roles = Counter(item.get("role", "unknown") for item in registry)
    notes = Counter(item.get("notes", "") for item in registry)

    lines = []
    lines.append("# Persona Registry Summary")
    lines.append("")
    lines.append(f"Total entries: {len(registry)}")
    lines.append("")
    lines.append("## Role Distribution")
    for role, count in roles.most_common():
        lines.append(f"- {role}: {count}")
    lines.append("")
    lines.append("## Notes")
    for note, count in notes.most_common():
        label = note or "(none)"
        lines.append(f"- {label}: {count}")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))

    print(f"Summary: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
