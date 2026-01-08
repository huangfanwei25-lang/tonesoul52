import os
import py_compile
import json
from typing import List, Dict, Any

class Doctor:
    """
    Phase 19: The Doctor (The Sensor & Mentor).
    Responsible for forays into the codebase to detect 'pain points' (errors, debt, axiom violations).
    Guides the Surgeon in the self-healing cycle.
    """
    def __init__(self, workspace_root: str = None):
        if not workspace_root:
            self.workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        else:
            self.workspace_root = workspace_root
            
        self.ignore_dirs = {".git", "__pycache__", "temp", "archive", "venv", ".venv", "node_modules"}
        self.report_path = os.path.join(self.workspace_root, "body", "surgeon", "surgery_report.json")

    def forage(self, target_dir: str = "body") -> List[Dict[str, Any]]:
        """
        Walks the target directory and identifies files with syntax or basic structural errors.
        """
        findings = []
        full_target = os.path.join(self.workspace_root, target_dir)
        
        print(f"🩺 [Doctor] Starting forage in {target_dir}...")
        
        for root, dirs, files in os.walk(full_target):
            # Prune ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            for file in files:
                if file.endswith(".py"):
                    # Normalize path for comparison and logging
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.workspace_root)
                    print(f"🔍 [Doctor] Scanning: {rel_path}")
                    issue = self.scan_syntax(rel_path)
                    if issue:
                        print(f"⚠️ [Doctor] Found issue in {rel_path}: {issue['type']}")
                        findings.append(issue)
        
        print(f"📊 [Doctor] Forage complete. Found {len(findings)} potential pain points.")
        return findings

    def scan_syntax(self, rel_path: str) -> Dict[str, Any]:
        """Checks for syntax errors in a python file."""
        abs_path = os.path.join(self.workspace_root, rel_path)
        try:
            # Attempt to compile
            py_compile.compile(abs_path, doraise=True)
            return None
        except py_compile.PyCompileError as e:
            # Extract error message
            msg = str(e)
            return {
                "file": rel_path,
                "type": "SYNTAX_ERROR",
                "severity": "CRITICAL",
                "description": msg,
                "suggested_action": "Syntactic Stabilization"
            }
        except Exception as e:
            return {
                "file": rel_path,
                "type": "IO_ERROR",
                "severity": "HIGH",
                "description": f"Failed to access file: {e}",
                "suggested_action": "System Audit"
            }

    def audit_axioms(self, rel_path: str, code_content: str) -> List[Dict[str, Any]]:
        """
        Mentorship Phase: Audits code against AXIOMS and logical best practices.
        Uses LLM to detect 'Soft Defects' (Redundancy, Axiom Drift).
        """
        from body.brain.llm_client import LLMClient
        llm = LLMClient()
        
        system_prompt = (
            "You are the ToneSoul Doctor (Architectural Auditor).\n"
            "Analyze the provided code against the 7 AXIOMS (Continuity, Responsibility, Ethics, etc.).\n"
            "Identify logical redundancy or architectural drift.\n"
            "Format: JSON list of issues. Each issue: {type, severity, description, suggested_action}."
        )
        
        user_prompt = f"Audit this file: {rel_path}\n\nCode:\n{code_content}"
        
        try:
            response = llm.chat_complete(
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
            )
            findings_raw = response.get("content", "[]")
            # Cleanup and parse
            if "```json" in findings_raw:
                findings_raw = findings_raw.split("```json")[1].split("```")[0].strip()
            
            import json
            issues = json.loads(findings_raw)
            return issues if isinstance(issues, list) else []
        except Exception as e:
            print(f"⚠️ [Doctor] Axiom Audit failed: {e}")
            return []

    def generate_report(self, verified_surgeries: List[Dict[str, Any]]):
        """Persists the diagnosis and simulation results for the user."""
        report = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            "status": "WAKE_UP_PENDING",
            "total_surgeries": len(verified_surgeries),
            "surgeries": verified_surgeries
        }
        with open(self.report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"📝 [Doctor] Metabolic report generated: {os.path.basename(self.report_path)}")

import time

if __name__ == "__main__":
    # Quick Test
    doc = Doctor()
    findings = doc.forage()
    doc.generate_report(findings)
