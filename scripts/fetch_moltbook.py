import json
import os
import ssl
import urllib.request

url = "https://www.moltbook.com/api/v1/posts"
api_key = os.environ.get("MOLTBOOK_API_KEY", "").strip()
if not api_key:
    raise SystemExit("MOLTBOOK_API_KEY is required")

headers = {
    "Authorization": f"Bearer {api_key}",
}

req = urllib.request.Request(url, headers=headers, method="GET")
context = ssl._create_unverified_context()

try:
    with urllib.request.urlopen(req, context=context) as response:
        result = json.loads(response.read().decode("utf-8"))
        with open("moltbook_feed.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print("Success! Feed written to moltbook_feed.json")
except Exception as e:
    print(f"Error: {e}")
