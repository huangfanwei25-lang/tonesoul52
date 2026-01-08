import sys
import os
sys.path.append(os.getcwd())

from body.skills.librarian import search

print("🔍 Testing Librarian Search...")
results = search("Constitutional AI", max_results=3)

print(f"Found {len(results)} results.")
for r in results:
    print(f"- {r['title']} ({r['id']})")
