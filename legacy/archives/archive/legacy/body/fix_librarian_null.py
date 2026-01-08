import sys
import os

sys.path.append(os.getcwd())

from body.surgeon.surgeon import Surgeon

def fix_librarian_null():
    print("🚑 [Autopoiesis] Triggering Surgeon to fix NoneType errors...")
    
    target_file = "body/skills/librarian.py"
    instruction = (
        "Fix the 'NoneType object has no attribute text' error. "
        "In the loop, before accessing .text, check if the element (title, summary, etc.) is None. "
        "If None, use a default value like 'Unknown' or empty string. "
        "Also ensure authors are extracted safely."
    )
    
    surgeon = Surgeon(provider="ollama")
    result = surgeon.operate(target_file, instruction)
    
    print(result)

if __name__ == "__main__":
    fix_librarian_null()
