import os
import sys
import shutil
from typing import Dict, Any

# Ensure imports work from body/surgeon context
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from body.brain.llm_client import LLMClient
from body.surgeon.sandbox import Sandbox
# from modules.ethics.guardian import Guardian # Guardian Logic imported dynamically to avoid conflicts

class Surgeon:
    """
    Phase 19: The Surgeon.
    Orchestrates the Self-Correction Loop:
    Diagnosis -> Prescription -> Simulation (Sandbox) -> Operation (Apply)
    """
    def __init__(self, provider="openai"):
        self.llm = LLMClient(provider=provider) # Needs smart brain
        self.sandbox = Sandbox()
        
    def operate(self, file_path_rel: str, issue_description: str) -> Dict[str, Any]:
        """
        Attempts to fix an issue in a specific file inside the sandbox.
        Does NOT apply to main repository. Returns the simulation report.
        """
        full_path = os.path.join(self.sandbox.workspace_root, file_path_rel)
        mode = "edit"
        original_code = ""

        if not os.path.exists(full_path):
            mode = "create"
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
        else:
            with open(full_path, 'r', encoding='utf-8') as f:
                original_code = f.read()

        system_prompt = (
            "You are an Expert Python Surgeon (ToneSoul Auto-Coder).\n"
            "Your Goal: Fix the reported issue in the code.\n"
            "Constraint 1: Return ONLY the full corrected python code. No markdown blocks, no commentary.\n"
        )
        
        user_prompt = f"Fix this code:\n\n{original_code}\n\nIssue: {issue_description}"

        try:
            response = self.llm.chat_complete(
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
            )
            new_code = response.get("content", "")
            if new_code.startswith("```"): 
                new_code = new_code.split("```")[1].replace("python", "").strip()

            sandbox_file = self.sandbox.setup(file_path_rel)
            self.sandbox.apply_patch(sandbox_file, new_code)
            
            passed, log = self.sandbox.verify(f"python3 -m py_compile {os.path.basename(sandbox_file)}")
            
            return {
                "success": passed,
                "file": file_path_rel,
                "new_code": new_code,
                "report": log if not passed else "Syntax verification passed in Fortress.",
                "type": mode
            }
            
        except Exception as e:
            return {"success": False, "file": file_path_rel, "report": str(e)}
        finally:
            self.sandbox.teardown()

    def _apply_to_main(self, full_path: str, new_content: str):
        # Create Backup first if file exists
        if os.path.exists(full_path):
            shutil.copy2(full_path, full_path + ".bak")
            print(f"✨ [Surgeon] Backup created (.bak).")
        else:
            print(f"✨ [Surgeon] Creating new file.")
            
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✨ [Surgeon] Applied content to {os.path.basename(full_path)}.")

import shutil
