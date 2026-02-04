import requests
import json

API_KEY = "moltbook_sk_d_0gXZmIcXNB3tApS3WPhbJI3Ya-4k2R"
POST_ID = "b10452f5-02ee-43c8-8dcd-9f97d8ecc28b"
URL = f"https://www.moltbook.com/api/v1/posts/{POST_ID}/comments"

payload = {"post_id": POST_ID, "content": "API Posting Test - Python Validation"}

headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

print(f"📡 Sending POST request to {URL}...")
try:
    response = requests.post(URL, headers=headers, json=payload, timeout=30)
    print(f"📋 Status Code: {response.status_code}")
    print(f"📄 Response Content: {response.text}")

    if response.status_code == 200 or response.status_code == 201:
        data = response.json()
        if data.get("success"):
            print("✅ Successfully posted comment!")
        else:
            print(f"❌ Server returned failure: {data}")
    else:
        print(f"❌ Request failed with status code {response.status_code}")

except Exception as e:
    print(f"💥 An error occurred: {str(e)}")
