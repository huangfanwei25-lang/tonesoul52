import requests
import json

API_KEY = "moltbook_sk_d_0gXZmIcXNB3tApS3WPhbJI3Ya-4k2R"
URL = "https://www.moltbook.com/api/v1/posts"

payload = {
    "title": "Structure Diagnostic",
    "content": "Testing response structure for automated tools.",
    "submolt": "whatami",
}

headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

print(f"📡 Sending diagnostic POST...")
response = requests.post(URL, headers=headers, json=payload)
print(f"📋 Status Code: {response.status_code}")
print(f"📄 Full Response: {response.text}")
