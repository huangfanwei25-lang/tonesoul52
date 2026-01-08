import os
from dataclasses import dataclass
from typing import List


@dataclass
class Patch:
    path: str
    diff: str


WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _patch_requirements() -> Patch:
    path = os.path.join(WORKSPACE_ROOT, "requirements.txt")
    diff = """--- a/requirements.txt
+++ b/requirements.txt
@@
+# Dashboard + sensors runtime
+streamlit>=1.25.0
+plotly>=5.18.0
+pandas>=2.0.0
+psutil>=5.9.0
"""
    return Patch(path=path, diff=diff)


def _patch_pyproject() -> Patch:
    path = os.path.join(WORKSPACE_ROOT, "pyproject.toml")
    diff = """--- a/pyproject.toml
+++ b/pyproject.toml
@@
 [project]
 dependencies = [
     "requests>=2.25.0",
+    "numpy>=1.24.0",
+    "chromadb>=0.4.0",
+    "sentence-transformers>=2.2.0",
+    "streamlit>=1.25.0",
+    "plotly>=5.18.0",
+    "pandas>=2.0.0",
+    "psutil>=5.9.0",
 ]
"""
    return Patch(path=path, diff=diff)


def generate_patches() -> List[Patch]:
    return [_patch_requirements(), _patch_pyproject()]


def main() -> int:
    patches = generate_patches()
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "auto_patch.diff")
    with open(out_path, "w", encoding="utf-8") as handle:
        for patch in patches:
            handle.write(patch.diff)
            handle.write("\n")
    print(f"Patch file: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
