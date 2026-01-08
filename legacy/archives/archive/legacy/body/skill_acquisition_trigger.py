import sys
import os

# Ensure we can import body modules
sys.path.append(os.getcwd())

from body.surgeon.surgeon import Surgeon

def learn_proprioception():
    print(" [Skill Acquisition] Initiating Proprioception Learning...")
    
    # Target file (Does not exist yet)
    target_file = "body/sensors/proprioception.py"
    
    # Instruction
    instruction = (
        "Create a new Python file with a class named 'HardwareSensor'. "
        "It should use the 'psutil' library to measure system resources. "
        "Method 'read()' should return a dictionary with 'cpu_percent' (float) "
        "and 'memory_percent' (float). "
        "Include error handling to return default values (0.0) if psutil is missing or fails."
    )
    
    # Initialize Surgeon (Using OpenAI for smart coding if available, else Ollama)
    # We'll stick to 'openai' provider as set in previous steps for 'smart' operations if keys were assumed,
    # but to be safe for local execution without keys, I'll let Surgeon default or pick based on Env.
    # The user environment might not have OPENAI_KEY set in this shell.
    # However, Surgeon defaults to 'openai'. Let's explicitely check or try 'ollama' if we want to be fully local.
    # Given the complexity is low, 'ollama' (gemma3:4b/llava) might struggle with perfect python syntax from scratch?
    # No, 'gemma3:4b' is decent at code. Let's try 'ollama' to prove "Local Autopoiesis".
    
    surgeon = Surgeon(provider="ollama") 
    
    print(f" [Surgeon] Operation Target: {target_file}")
    print(f" [Surgeon] Instruction: {instruction}")
    
    result = surgeon.operate(target_file, instruction)
    
    print(f"\nExample Output: {result}")

if __name__ == "__main__":
    learn_proprioception()
