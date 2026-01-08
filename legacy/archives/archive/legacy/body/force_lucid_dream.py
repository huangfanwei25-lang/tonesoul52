import os
import sys
# Helper for debug
sys.path.append(os.getcwd())

from body.dream.weaver import DreamWeaver
from body.memory.hippocampus import MemoryConsolidator

# 1. Create a "Buggy" File
target_file = "body/debug_target.py"
with open(target_file, "w", encoding="utf-8") as f:
    f.write("# This file has a bug.\ndef multiply(a, b):\n    return a + b # BUG: Should be *")

print(f" Created buggy file: {target_file}")

# 2. Inject Memory
memory = MemoryConsolidator()
memory.engrave(
    content=f"Dream Insight on Code Audit: {target_file}: The function multiply uses addition instead of multiplication. This is a critical logic error.",
    source_id="manual_injection",
    importance=0.99, # High importance to force selection
    tags=["code_audit"]
)
print(" Injected 'Code Audit' memory.")

# 3. Trigger Dream
print(" Forcing REM Cycle...")
weaver = DreamWeaver(memory)
insights = weaver.enter_rem_cycle(duration_seconds=60)

# 4. Check Result
print("\n --- Inspection ---")
with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

print(f"File content:\n{content}")

if "*" in content:
    print(" SUCCESS: The Dream repaired the code!")
else:
    print(" FAILURE: Code remains buggy.")
