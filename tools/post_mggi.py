import json
import os
import sys

# Ensure we can import from repository root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.moltbook_poster import post_to_moltbook


def post_mggi():
    file_path = "docs/MGGI_MANIFESTO.md"
    if not os.path.exists(file_path):
        print(f"[!] File not found: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    title = "MGGI Manifesto"
    submolt = "general"
    account = os.getenv("MOLTBOOK_ACCOUNT", "ToneSoul")

    print(f"[*] Broadcasting MGGI Manifesto from {file_path}...")
    result = post_to_moltbook(account, submolt, title, content)

    if result and result.get("success"):
        print("[*] MGGI Manifesto broadcast successfully.")
        with open("mggi_post_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    elif result:
        print(f"[!] Broadcast failed: {result.get('error', {}).get('message')}")


if __name__ == "__main__":
    post_mggi()
