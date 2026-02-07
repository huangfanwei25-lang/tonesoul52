import requests
import json
import os

KEYS = {
    "ToneSoul": os.environ.get("MOLTBOOK_API_KEY_TONESOUL", ""),
    "Advocate": os.environ.get("MOLTBOOK_API_KEY_ADVOCATE", ""),
}

URL = "https://www.moltbook.com/api/v1/heartbeat"

for name, key in KEYS.items():
    print(f"🔍 Checking {name} identity...")
    try:
        response = requests.get(URL, headers={"Authorization": f"Bearer {key}"}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {name} corresponds to ID: {data.get('agent_id')}")
            # Try to get profile if possible (assuming there's a me endpoint or similar)
            # For now, let's just print the message
            print(f"   Message: {data.get('message')}")
        else:
            print(f"❌ {name} check failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"💥 Error checking {name}: {e}")
