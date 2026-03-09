"""Delegation Test v6: use think=false to disable qwen3.5 thinking mode."""

import json
import time

import requests

with open("tonesoul/adaptive_gate.py", "r", encoding="utf-8") as f:
    code = f.read()

# Extract the AdaptiveGate evaluate method (core logic)
lines = code.split("\n")
core = []
capture = False
for line in lines:
    if "def evaluate(" in line:
        capture = True
    if capture:
        core.append(line)
    if capture and "return GateDecision(" in line:
        # Get a few more lines for closing
        pass
    if capture and len(core) > 3 and line.strip() == ")":
        break
core_code = "\n".join(core[:60])

PROMPT = f"""Review this Python code. List 3 potential issues or improvements in Traditional Chinese. Be concise, one sentence per point.

```python
{core_code}
```

3 個問題或改進建議："""

print(f"Prompt: {len(PROMPT)} chars")
start = time.time()

r = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "qwen3.5:4b",
        "messages": [{"role": "user", "content": PROMPT}],
        "stream": False,
        "think": False,
        "options": {"temperature": 0.3, "num_predict": 300},
    },
    timeout=120,
)
elapsed = time.time() - start
data = r.json()
msg = data.get("message", {})
response = msg.get("content", "")
tokens = data.get("eval_count", 0)

result = {
    "response": response,
    "tokens": tokens,
    "time_seconds": round(elapsed, 1),
    "speed_tps": round(tokens / max(elapsed, 0.1), 1),
}

with open("reports/delegation_test_result.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\nTime: {elapsed:.1f}s | Tokens: {tokens} | Speed: {result['speed_tps']} tok/s")
print(f"Response length: {len(response)} chars")
print(f"\n{'='*60}")
print(response[:1500] if response else "[EMPTY]")
