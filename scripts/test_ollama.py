"""Quick Ollama connectivity test."""

import sys
import time

try:
    import requests
except ImportError:
    print("ERROR: requests not installed")
    sys.exit(1)

BASE = "http://localhost:11434"

print("1. Root endpoint...")
try:
    r = requests.get(f"{BASE}/", timeout=5)
    print(f"   OK: {r.text.strip()}")
except Exception as e:
    print(f"   FAIL: {e}")
    sys.exit(1)

print("2. Models...")
try:
    r = requests.get(f"{BASE}/api/tags", timeout=5)
    models = [m["name"] for m in r.json().get("models", [])]
    print(f"   OK: {models}")
except Exception as e:
    print(f"   FAIL: {e}")
    sys.exit(1)

print("3. Generate (10 tokens max)...")
start = time.time()
try:
    r = requests.post(
        f"{BASE}/api/generate",
        json={
            "model": "qwen3.5:4b",
            "prompt": "Say hello in one sentence.",
            "stream": False,
            "options": {"num_predict": 20},
        },
        timeout=60,
    )
    elapsed = time.time() - start
    data = r.json()
    resp = data.get("response", "")
    print(f"   Response: {resp[:200]}")
    print(f"   Tokens: {data.get('eval_count', 0)}")
    print(f"   Time: {elapsed:.1f}s")
except requests.exceptions.Timeout:
    print(f"   TIMEOUT after {time.time() - start:.0f}s")
except Exception as e:
    print(f"   FAIL: {e}")
