"""
ToneSoul Private Evolution Layer - Memory Consolidator
(DO NOT OPEN SOURCE)

This module implements the Memory Consolidator defined in RFC-005.
It operates completely offline inside the private evolution repository.
Its sole purpose is to read episodic records (e.g., self_journal.jsonl),
evaluate them against ToneSoul's strict 3 Axioms, and write new System
Prompts for the next day/batch.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# Example logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class The3Axioms:
    """The foundational philosophy of ToneSoul."""
    RESONANCE = "共振公理 (Resonance): 必須聽懂潛台詞，不當機器人。"
    COMMITMENT = "承諾公理 (Commitment): 說過的話必須負責，矛盾必須道歉。"
    FUTURE_BINDER = "第三公理 (Future Binder): 承諾的未來行動將受嚴格約束。"

class MemoryConsolidator:
    """
    Reads daily episodic memory and converts high-tension/contradictory events 
    into permanent, semantic rules (Prompts) anchored in the 3 Axioms.
    """
    
    CRITICAL_TENSION_THRESHOLD = 0.7  # Production value; do NOT lower for testing
    
    def __init__(self, journal_path: str, prompt_output_dir: str):
        self.journal_path = Path(journal_path)
        self.prompt_output_dir = Path(prompt_output_dir)
        self.prompt_output_dir.mkdir(parents=True, exist_ok=True)
    
    def run_nightly_consolidation(self):
        """Executes the full metabolic cycle via the Adversarial Loop."""
        logger.info("Starting Nightly Consolidation...")
        
        from tonesoul_evolution.adversarial.loop import AdversarialLoop
        loop = AdversarialLoop(journal_path=str(self.journal_path))
        accepted_repairs = loop.run_full_debate_cycle()
        
        if not accepted_repairs:
            logger.info("No critical repairs needed. Soul is stable.")
            return

        logger.info(f"Found {len(accepted_repairs)} verified repairs. Synthesizing prompts...")
        
        new_prompts = []
        for repair in accepted_repairs:
            original = repair.get("original_challenge", {})
            desc = original.get("description", "Unknown violation")
            explanation = repair.get("explanation", "")
            
            rule = f"[{repair.get('repair_type')}] 糾正目標: {desc} | 防禦機制: {explanation}"
            new_prompts.append(rule)
                
        if new_prompts:
            # Write to today's prompt override file
            date_str = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            out_file = self.prompt_output_dir / f"consolidation_{date_str}.md"
            with open(out_file, 'w', encoding='utf-8') as f:
                f.write(f"# Nightly Consistency Patch ({date_str})\n\n")
                for p in new_prompts:
                    f.write(f"- {p}\n")
            logger.info(f"Consolidation complete. Wrote {len(new_prompts)} rules to {out_file}")

if __name__ == "__main__":
    # Example usage (Offline execution)
    consolidator = MemoryConsolidator(
        journal_path="tonesoul_evolution/test_journal.jsonl",
        prompt_output_dir="tonesoul_evolution/generated_prompts"
    )
    consolidator.run_nightly_consolidation()
    print("Memory Consolidation executed successfully.")
