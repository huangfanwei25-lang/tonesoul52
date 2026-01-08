# Patch Pack (Proposed Diffs Only)

All diffs below are proposals; apply manually if desired.

## 1) requirements.txt (add runtime deps)
```diff
+streamlit>=1.25.0
+plotly>=5.18.0
+pandas>=2.0.0
+psutil>=5.9.0
```

## 2) pyproject.toml (align runtime deps)
```diff
 [project]
 dependencies = [
-    "requests>=2.25.0",
+    "requests>=2.25.0",
+    "numpy>=1.24.0",
+    "chromadb>=0.4.0",
+    "sentence-transformers>=2.2.0",
+    "streamlit>=1.25.0",
+    "plotly>=5.18.0",
+    "pandas>=2.0.0",
+    "psutil>=5.9.0",
 ]
```

## 3) body/dashboard/app.py (portable doc links)
```diff
-        - **[STREI Operational Protocol](file:///c:/Users/user/Desktop/倉庫/docs/governance/STREI_OPERATIONAL_PROTOCOL.md)**
-        - **[Temporal Audit Specification](file:///c:/Users/user/Desktop/倉庫/docs/governance/TEMPORAL_AUDIT_SPEC.md)**
-        - **[Communication Standard](file:///c:/Users/user/Desktop/倉庫/docs/governance/COMMUNICATION_STANDARD.md)**
+        - **[STREI Operational Protocol](docs/governance/STREI_OPERATIONAL_PROTOCOL.md)**
+        - **[Temporal Audit Specification](docs/governance/TEMPORAL_AUDIT_SPEC.md)**
+        - **[Communication Standard](docs/governance/COMMUNICATION_STANDARD.md)**
```

## 4) body/spine/controller.py (avoid emoji on import)
```diff
- print("🧠 Spine Controller Ready")
+ # Print only when running interactively to avoid encoding issues on import
+ if __name__ == "__main__":
+     print("Spine Controller Ready")
```

## 5) yuhun_cli.py (banner extraction)
- Move banner string to `yuhun/strings.py` and ensure UTF-8 encoding.
- Replace garbled characters with ASCII-friendly fallback.

```
```
