import os

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET_EXTS = {".py", ".md"}
SKIP_DIRS = {".git", ".venv", "__pycache__"}


def _is_text_file(path: str) -> bool:
    return os.path.splitext(path)[1].lower() in TARGET_EXTS


def scan_encoding_issues() -> list:
    issues = []
    for root, dirnames, files in os.walk(WORKSPACE_ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        if "\\5.2\\" in root:
            continue
        for name in files:
            path = os.path.join(root, name)
            if not _is_text_file(path):
                continue
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    handle.read()
            except UnicodeDecodeError as exc:
                issues.append({"path": path, "error": str(exc)})
    return issues


def main() -> int:
    issues = scan_encoding_issues()
    if not issues:
        print("Encoding scan: OK")
        return 0

    print("Encoding scan: FAIL")
    for item in issues:
        print(f"- {item['path']}: {item['error']}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
