import sys
import os

sys.path.append(os.getcwd())

from body.surgeon.surgeon import Surgeon

def fix_librarian_ns():
    print("🚑 [Autopoiesis] Triggering Surgeon to fix XML Namespace error...")
    
    target_file = "body/skills/librarian.py"
    instruction = (
        "Fix the XML parsing logic. The arXiv Atom feed uses the namespace '{http://www.w3.org/2005/Atom}'. "
        "Update the find/findall calls to include the namespace. "
        "For example: root.findall('{http://www.w3.org/2005/Atom}entry'). "
        "Also extract authors correctly from 'author/name'."
    )
    
    surgeon = Surgeon(provider="ollama")
    result = surgeon.operate(target_file, instruction)
    
    print(result)

if __name__ == "__main__":
    fix_librarian_ns()
