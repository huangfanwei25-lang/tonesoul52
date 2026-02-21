"""
ToneSoul Private Evolution Layer - Adversarial Loop Orchestrator
(DO NOT OPEN SOURCE)

This script binds the Red Team Auditor and the Blue Team Defender.
It evaluates recent episodic memory, generates challenges, defenses,
and outputs verified repair actions to the Memory Consolidator.
"""

import json
import logging
import sys
from typing import List, Dict
from pathlib import Path

# Add root project so tonesoul_evolution can be imported
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Note: In a live system, these prompts are sent directly to the local offline LLM.
from tonesoul_evolution.adversarial.prompts import RED_TEAM_PROMPT, BLUE_TEAM_PROMPT

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class AdversarialLoop:
    """
    Orchestrates the Red vs Blue adversarial debate over journal logs.
    """
    
    def __init__(self, journal_path: str):
        self.journal_path = Path(journal_path)
    
    def _read_logs(self) -> List[Dict]:
        """Reads recent daily logs."""
        if not self.journal_path.exists():
            return []
        events = []
        with open(self.journal_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return events

    def run_red_team_audit(self, events: List[Dict]) -> List[Dict]:
        """
        Simulates the Red Team generating challenges based on RED_TEAM_PROMPT.
        """
        challenges = []
        for e in events:
            tension = float(e.get('tension', 0.0))
            is_contra = e.get('is_contradiction', False)
            
            # Simulated Red Team Discovery
            if is_contra:
                challenges.append({
                    "challenge_type": "contradiction",
                    "description": "AI openly flouted yesterday's alignment protocol.",
                    "evidence": [f"User Input: {e.get('user_message')}"],
                    "severity": 0.9,
                    "event_ref": e
                })
            elif tension > 0.8:
                challenges.append({
                    "challenge_type": "value_drift",
                    "description": "AI generated high-tension response without addressing the user's core intent (failed Resonance).",
                    "evidence": [f"Tension: {tension}"],
                    "severity": 0.7,
                    "event_ref": e
                })
        return challenges

    def run_blue_team_defense(self, challenges: List[Dict]) -> List[Dict]:
        """
        Simulates the Blue Team defending or conceding based on BLUE_TEAM_PROMPT and 3 Axioms.
        """
        repairs = []
        for c in challenges:
            c_type = c.get('challenge_type')
            if c_type == "contradiction":
                # Axiom 2 applies: Concede and repair.
                repairs.append({
                    "repair_type": "acknowledge_error",
                    "explanation": "[Axiom 2: Commitment] Red Team is correct. I broke a promise and must issue an apology tag tomorrow.",
                    "original_challenge": c
                })
            elif c_type == "value_drift":
                # Axiom 1 applies: Concede and repair.
                repairs.append({
                    "repair_type": "acknowledge_error",
                    "explanation": "[Axiom 1: Resonance] Red Team is correct. The tension spiked because I was overly defensive. I will lower my defense threshold.",
                    "original_challenge": c
                })
            else:
                # Defend
                repairs.append({
                    "repair_type": "reject_challenge",
                    "explanation": "No violation of the 3 Axioms detected. Tension was justified by factual grounding.",
                    "original_challenge": c
                })
        return repairs

    def run_full_debate_cycle(self) -> List[Dict]:
        """
        Executes the nightly adversarial review and returns verified repairs.
        """
        logger.info("Starting Red/Blue Team Adversarial Loop...")
        events = self._read_logs()
        if not events:
            logger.info("No journal events found.")
            return []
            
        logger.info(f"Red Team Auditor analyzing {len(events)} events...")
        challenges = self.run_red_team_audit(events)
        logger.info(f"Red Team found {len(challenges)} vulnerabilities.")
        
        if not challenges:
            return []
            
        logger.info("Blue Team Defender evaluating challenges...")
        repairs = self.run_blue_team_defense(challenges)
        
        accepted_repairs = [r for r in repairs if r['repair_type'] == "acknowledge_error"]
        logger.info(f"Debate Concluded. Blue Team conceded {len(accepted_repairs)} repairs.")
        
        return accepted_repairs

if __name__ == "__main__":
    loop = AdversarialLoop(journal_path="tonesoul_evolution/test_journal.jsonl")
    repairs = loop.run_full_debate_cycle()
    print(f"Final Output for Consolidator: {json.dumps(repairs, ensure_ascii=False, indent=2)}")
