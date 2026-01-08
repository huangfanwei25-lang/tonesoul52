# Patch Pack - Detailed (Proposed Only)

This file provides per-file patch suggestions. No legacy edits are applied.

## A) requirements.txt
Add missing runtime dependencies used by dashboard and sensors.
```diff
+# Dashboard + sensors runtime
+streamlit>=1.25.0
+plotly>=5.18.0
+pandas>=2.0.0
+psutil>=5.9.0
```

## B) pyproject.toml
Align runtime dependencies with actual imports.
```diff
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
```

## C) body/dashboard/app.py
Replace absolute file:// links with relative paths.
```diff
-        - **[STREI Operational Protocol](file:///c:/Users/user/Desktop/倉庫/docs/governance/STREI_OPERATIONAL_PROTOCOL.md)**
-        - **[Temporal Audit Specification](file:///c:/Users/user/Desktop/倉庫/docs/governance/TEMPORAL_AUDIT_SPEC.md)**
-        - **[Communication Standard](file:///c:/Users/user/Desktop/倉庫/docs/governance/COMMUNICATION_STANDARD.md)**
+        - **[STREI Operational Protocol](docs/governance/STREI_OPERATIONAL_PROTOCOL.md)**
+        - **[Temporal Audit Specification](docs/governance/TEMPORAL_AUDIT_SPEC.md)**
+        - **[Communication Standard](docs/governance/COMMUNICATION_STANDARD.md)**
```

## D) body/spine/controller.py
Avoid import-time emoji output that breaks cp950.
```diff
- print("🧠 Spine Controller Ready")
+ # Print only when running directly to avoid console encoding issues.
+ if __name__ == "__main__":
+     print("Spine Controller Ready")
```

## E) yuhun_cli.py
Move banner to a separate module and replace garbled characters.
Suggested steps:
- Create `yuhun/strings.py` with ASCII banner fallback.
- Import banner from `yuhun/strings.py`.

```diff
- BANNER = """
- <garbled banner>
- """
+ from yuhun.strings import BANNER
```

## F) ToneSoul-Repo/app.py
Re-save file in UTF-8 and replace garbled prompts.
Suggested replacements:
- Replace `\n浣狅?` with `\nYou> `.
- Replace broken strings (e.g., `??`) with clean ASCII equivalents.
