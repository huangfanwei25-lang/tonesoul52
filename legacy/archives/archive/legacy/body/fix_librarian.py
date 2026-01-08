import sys
import os

sys.path.append(os.getcwd())

from body.surgeon.surgeon import Surgeon

def fix_librarian():
    print("🚑 [Autopoiesis] Triggering Surgeon to fix encoding error...")
    
    target_file = "body/skills/librarian.py"
    instruction = "Fix the URL encoding issue in the search method. Use urllib.parse.quote for the query parameter to handle spaces."
    
    surgeon = Surgeon(provider="ollama")
    result = surgeon.operate(target_file, instruction)
    
    print(result)

if __name__ == "__main__":
    fix_librarian()
