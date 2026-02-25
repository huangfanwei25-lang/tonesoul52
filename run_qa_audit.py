import requests
import json
import sys

def run_qa_audit(file_path):
    print(f"Reading target file: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        code_content = f.read()

    # Get the skill content
    with open(".agent/skills/qa_auditor/SKILL.md", "r", encoding="utf-8") as f:
        skill_content = f.read()

    system_prompt = f"You are the QA Auditor.\n{skill_content}"
    user_prompt = f"Audit the following `{file_path}` file with extreme prejudice focusing on D3 race conditions and D4 environment issues. Keep output concise. Code:\n\n{code_content[:3000]}" # Truncated to avoid context limits of 4b model

    print("Sending to local Ollama (qwen3:4b)...")
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "qwen3:4b", # Updated to use the correct model name
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": False,
                "think": False, # Crucial for qwen3 flag
                "options": {
                    "temperature": 0.8,
                    "num_predict": 1024, 
                },
            },
            timeout=180,
        )
        response.raise_for_status()
        result = response.json().get("message", {}).get("content", "")
        
        output_file = "QA_RECORD_core.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result)
        
        print(f"Audit complete. Results saved to {output_file}")
        
    except Exception as e:
        print(f"Error calling Ollama: {e}")

if __name__ == "__main__":
    run_qa_audit("api/_shared/core.py")
