import os
import re

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
REQUIREMENTS = [
    "streamlit",
    "plotly",
    "pandas",
    "psutil",
    "numpy",
    "chromadb",
    "sentence-transformers",
    "requests",
]


def _read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except FileNotFoundError:
        return ""


def main() -> int:
    req_txt = _read(os.path.join(WORKSPACE_ROOT, "requirements.txt"))
    pyproject = _read(os.path.join(WORKSPACE_ROOT, "pyproject.toml"))

    missing = []
    for dep in REQUIREMENTS:
        in_req = re.search(rf"^{re.escape(dep)}", req_txt, re.MULTILINE)
        in_py = re.search(rf"\"{re.escape(dep)}", pyproject)
        if not in_req or not in_py:
            missing.append({"dep": dep, "requirements": bool(in_req), "pyproject": bool(in_py)})

    if not missing:
        print("Dependency scan: OK")
        return 0

    print("Dependency scan: FAIL")
    for item in missing:
        print(f"- {item['dep']}: requirements={item['requirements']} pyproject={item['pyproject']}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
