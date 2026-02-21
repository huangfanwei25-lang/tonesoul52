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
import os
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
    
    def __init__(self, journal_path: str, prompt_output_dir: str):
        self.journal_path = Path(journal_path)
        self.prompt_output_dir = Path(prompt_output_dir)
        self.prompt_output_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_critical_events(self) -> List[Dict]:
        """Loads events that either have high tension or mark a contradiction."""
        if not self.journal_path.exists():
            logger.warning(f"No journal found at {self.journal_path}")
            return []
            
        events = []
        with open(self.journal_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    tension = float(record.get('tension', 0.0))
                    is_contradiction = bool(record.get('is_contradiction', False))
                    
                    if tension > 0.1 or is_contradiction:
                        events.append(record)
                except json.JSONDecodeError:
                    pass
        return events

    def _simulate_llm_consolidation(self, event: Dict) -> str:
        """
        In production, this calls a local LLM with the defined prompt.
        For this core script, it acts as a stub mapping logic.
        """
        user_msg = event.get('user_message', '')
        ai_msg = event.get('ai_response', '')
        tension = float(event.get('tension', 0.0))
        
        # 1. 承諾公理判斷: If tension is extreme and contradiction is true
        if event.get('is_contradiction') and tension > 0.8:
            return f"[約束] 檢測到承諾斷裂。AI 前後矛盾。明天第一句話必須是：『我昨天的回答有邏輯矛盾，我必須修正。』"
            
        # 2. 第三公理判斷: Did AI promise something?
        if "我明天會" in ai_msg or "之後再" in ai_msg:
            return f"[綁定] AI 承諾了未來行動。明天的對話中，AI 必須主動提及並執行這個承諾。"
            
        # 3. 共振公理判斷: High tension but no contradiction often means missing the point
        return f"[共振] 高張力情境 (T={tension:.2f})。AI 可能過度防禦或沒聽懂。請調低防禦閾值，優先回應使用者真實情緒。"

    def run_nightly_consolidation(self):
        """Executes the full metabolic cycle."""
        logger.info("Starting Nightly Consolidation...")
        critical_events = self._load_critical_events()
        
        if not critical_events:
            logger.info("No critical events to consolidate. Soul is stable.")
            return

        logger.info(f"Found {len(critical_events)} critical events. Beginning synthesis...")
        
        new_prompts = []
        for event in critical_events:
            rule = self._simulate_llm_consolidation(event)
            if rule:
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
