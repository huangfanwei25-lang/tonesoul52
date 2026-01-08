# Patch Proposal: Import + Encoding Fixes

## A) yuhun_cli.py (ensure path + utf-8 output)
```diff
@@
-import sys
-import os
+import sys
+import os
@@
-ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
-sys.path.insert(0, os.path.join(ROOT_DIR, 'body'))
-sys.path.insert(0, os.path.join(ROOT_DIR, 'core'))
+ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
+if ROOT_DIR not in sys.path:
+    sys.path.insert(0, ROOT_DIR)
+sys.path.insert(0, os.path.join(ROOT_DIR, 'body'))
+sys.path.insert(0, os.path.join(ROOT_DIR, 'core'))
+
+# Avoid cp950 emoji crashes on Windows terminals
+try:
+    sys.stdout.reconfigure(encoding="utf-8")
+    sys.stderr.reconfigure(encoding="utf-8")
+except Exception:
+    pass
```

## B) body/yuhun_metrics.py (prefer absolute import)
```diff
@@
-    from .neuro_sensor_v2 import VectorNeuroSensor
+    from body.neuro_sensor_v2 import VectorNeuroSensor
```

## C) body/neuro_sensor_v2.py (prefer absolute import)
```diff
@@
-    from .spine_system import ISensor, ToneSoulTriad
+    from body.spine_system import ISensor, ToneSoulTriad
```

## D) yuhun_cli.py (ASCII log symbol)
```diff
@@
-    self._log(f"⚠️ Multi-Path Engine: {e}")
+    self._log(f"[WARN] Multi-Path Engine: {e}")
```
