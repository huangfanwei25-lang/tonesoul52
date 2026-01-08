import sys
import os

# Ensure we can import body modules
sys.path.append(os.getcwd())

from body.surgeon.surgeon import Surgeon

def learn_librarian():
    print(" [Skill Acquisition] Initiating Librarian (arXiv Research) Learning...")
    
    # Target file
    # We need to ensure the directory exists first, though Surgeon acts on files.
    # The new Surgeon logic handles parent dir creation.
    target_file = "body/skills/librarian.py"
    
    # Instruction
    instruction = (
        "Create a new Python file with a class named 'Librarian'. "
        "It should use the standard 'urllib.request' and 'xml.etree.ElementTree' libraries (or 'requests') "
        "to search arXiv.org.\n"
        "Method: search(self, query: str, max_results: int = 5) -> list[dict].\n"
        "Logic:\n"
        "1. Query 'http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}'.\n"
        "2. Parse the XML response.\n"
        "3. Extract entries: title, summary, authors (list), and id (link).\n"
        "4. Return a list of dictionaries.\n"
        "5. Include error handling."
    )
    
    # Initialize Surgeon (Using 'ollama' -> gemma3:4b for local proof)
    # Note: Complex parsing might challenge 4b models, but let's test the limit.
    surgeon = Surgeon(provider="ollama") 
    
    print(f" [Surgeon] Operation Target: {target_file}")
    print(f" [Surgeon] Instruction: {instruction[:100]}...")
    
    result = surgeon.operate(target_file, instruction)
    
    print(f"\nExample Output: {result}")

if __name__ == "__main__":
    learn_librarian()
