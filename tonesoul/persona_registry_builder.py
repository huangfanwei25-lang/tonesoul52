import json
import os
import re
from typing import Dict, List


WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))

SOURCES = [
    os.path.join(WORKSPACE_ROOT, "body", "persona_stack.py"),
    os.path.join(WORKSPACE_ROOT, "body", "persona_library.py"),
    os.path.join(
        WORKSPACE_ROOT, "archive", "舊檔案", "有價值_可整合", "語魂初", "模組", "persona_list.json"
    ),
    os.path.join(
        WORKSPACE_ROOT, "archive", "舊檔案", "有價值_可整合", "語魂初", "模組", "tone_data.json"
    ),
    os.path.join(
        WORKSPACE_ROOT,
        "archive",
        "舊檔案",
        "有價值_可整合",
        "語魂初",
        "模組",
        "tonal_chain_config.json",
    ),
]

ROLE_HINTS = {
    "Core": "integrator",
    "Spark": "creative",
    "Rational": "analysis",
    "BlackMirror": "shadow",
    "Guardian": "ethics",
    "Audit": "verification",
}


def _read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except Exception:
        try:
            with open(path, "r", encoding="cp950") as handle:
                return handle.read()
        except Exception:
            return ""


def _extract_names(text: str) -> List[str]:
    names = set()
    for match in re.findall(r'name\s*=\s*"([^"]+)"', text):
        names.add(match)
    for match in re.findall(r'"persona"\s*:\s*"([^"]+)"', text):
        names.add(match)
    for match in re.findall(r'"id"\s*:\s*"([^"]+)"', text):
        names.add(match)
    for match in re.findall(r'"name"\s*:\s*"([^"]+)"', text):
        names.add(match)
    for block in re.findall(r'"suitable_personas"\s*:\s*\[(.*?)\]', text, re.DOTALL):
        for entry in re.findall(r'"([^"]+)"', block):
            names.add(entry)
    return sorted(n for n in names if n)


def _detect_encoding_issue(text: str) -> bool:
    return "�" in text or "?" in text


def build_registry() -> List[Dict[str, str]]:
    registry = []
    seen = set()
    for path in SOURCES:
        text = _read(path)
        if not text:
            continue
        encoding_issue = _detect_encoding_issue(text)
        for name in _extract_names(text):
            key = (name, path)
            if key in seen:
                continue
            seen.add(key)
            registry.append(
                {
                    "name": name,
                    "source": path,
                    "role": ROLE_HINTS.get(name, "unknown"),
                    "notes": "encoding_suspect" if encoding_issue else "auto-extracted",
                }
            )
    return registry


def main() -> int:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    output_path = os.path.join(REPORTS_DIR, "persona_registry_extended.json")
    payload = {
        "schema_version": "1.1",
        "generated_from": SOURCES,
        "registry": build_registry(),
    }
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
    print(f"Registry: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
