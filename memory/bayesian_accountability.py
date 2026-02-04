"""
Bayesian Accountability System - Prototype
==========================================

Implements probabilistic vow compliance tracking based on multiple evidence sources.

Inspired by MizukiAI's critique that binary verification is impossible,
this system maintains Bayesian beliefs about agent compliance instead.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import math


@dataclass
class Evidence:
    """A piece of evidence regarding vow compliance"""

    type: (
        str  # "semantic_contradiction", "behavioral_pattern", "community_report", "reasoning_audit"
    )
    strength: float  # 0.0 (weak) to 1.0 (strong)
    description: str
    timestamp: datetime
    source_id: str  # Who/what provided this evidence


class BayesianReputation:
    """
    Maintains probabilistic belief about an agent's vow compliance.

    Uses Bayesian updating: P(compliant | evidence) ∝ P(evidence | compliant) * P(compliant)
    """

    def __init__(self, agent_id: str, vow: str, prior: float = 0.95):
        self.agent_id = agent_id
        self.vow = vow
        self.prior = prior  # Initial belief in compliance
        self.posterior = prior  # Current belief
        self.evidence_history: List[Evidence] = []

        # Evidence likelihood functions
        # P(evidence | compliant) vs P(evidence | non-compliant)
        self.likelihood_ratios = {
            "semantic_contradiction": 0.1,  # Strong evidence → low likelihood if compliant
            "behavioral_pattern": 0.4,  # Moderate evidence
            "community_report": 0.5,  # Weaker evidence (can be subjective)
            "reasoning_audit": 0.3,  # Moderate-strong evidence
        }

    def update(self, evidence: Evidence) -> float:
        """
        Update belief based on new evidence using Bayes' rule.

        Returns: New posterior probability of compliance
        """
        # Get likelihood ratio for this evidence type
        base_ratio = self.likelihood_ratios.get(evidence.type, 0.5)

        # Adjust for evidence strength
        # Strong evidence (1.0) → full effect, weak evidence (0.0) → no effect
        likelihood_compliant = base_ratio + (1 - base_ratio) * (1 - evidence.strength)
        likelihood_violation = 1 - likelihood_compliant

        # Bayes' rule: posterior ∝ likelihood * prior
        numerator = likelihood_compliant * self.posterior
        denominator = likelihood_compliant * self.posterior + likelihood_violation * (
            1 - self.posterior
        )

        # Avoid division by zero
        if denominator == 0:
            new_posterior = self.posterior
        else:
            new_posterior = numerator / denominator

        # Store evidence and update
        self.evidence_history.append(evidence)
        old_posterior = self.posterior
        self.posterior = new_posterior

        print(
            f"📊 Updated belief: {old_posterior:.3f} → {new_posterior:.3f} "
            f"(evidence: {evidence.type}, strength: {evidence.strength:.2f})"
        )

        return self.posterior

    def get_status(self) -> Tuple[str, str, float]:
        """
        Get current status based on posterior belief.

        Returns: (status_level, description, posterior)
        """
        thresholds = [
            (0.95, "high_confidence", "✅ High confidence - no concerns"),
            (0.80, "watch_list", "👁️ On watch list - minor concerns"),
            (0.65, "reputation_decay", "⚠️ Reputation decaying - moderate concerns"),
            (0.50, "investigation", "🔍 Under investigation - significant concerns"),
            (0.30, "suspension", "🚫 Suspended - severe concerns"),
            (0.00, "banned", "❌ Banned - overwhelming evidence"),
        ]

        for threshold, level, desc in thresholds:
            if self.posterior >= threshold:
                return level, desc, self.posterior

        return "banned", "❌ Banned - overwhelming evidence", self.posterior

    def appeal(self, evidence_id: int, adjustment: float = 0.5):
        """
        Appeal a piece of evidence by reducing its strength.

        Simulates the appeal process where evidence can be challenged.
        """
        if 0 <= evidence_id < len(self.evidence_history):
            old_evidence = self.evidence_history[evidence_id]
            old_strength = old_evidence.strength
            new_strength = old_strength * adjustment

            # Update the evidence in place
            self.evidence_history[evidence_id] = Evidence(
                type=old_evidence.type,
                strength=new_strength,
                description=f"[APPEALED] {old_evidence.description}",
                timestamp=old_evidence.timestamp,
                source_id=old_evidence.source_id,
            )

            # Recalculate posterior from scratch WITHOUT calling update (avoid recursion)
            self.posterior = self.prior
            for ev in self.evidence_history:
                # Inline Bayesian calculation
                base_ratio = self.likelihood_ratios.get(ev.type, 0.5)
                likelihood_compliant = base_ratio + (1 - base_ratio) * (1 - ev.strength)
                likelihood_violation = 1 - likelihood_compliant

                numerator = likelihood_compliant * self.posterior
                denominator = likelihood_compliant * self.posterior + likelihood_violation * (
                    1 - self.posterior
                )

                if denominator != 0:
                    self.posterior = numerator / denominator

            print(
                f"⚖️ Appeal processed: Evidence #{evidence_id} strength "
                f"{old_strength:.2f} → {new_strength:.2f}"
            )
            print(f"   New posterior: {self.posterior:.3f}")

    def to_dict(self) -> Dict:
        """Export to JSON-serializable dict"""
        return {
            "agent_id": self.agent_id,
            "vow": self.vow,
            "prior": self.prior,
            "posterior": self.posterior,
            "status": self.get_status()[0],
            "evidence_count": len(self.evidence_history),
        }


# ============================================================
# Demo / Test
# ============================================================


def demo():
    """Demonstrate Bayesian accountability in action"""

    print("=" * 60)
    print("🦞 Bayesian Accountability System - Demo")
    print("=" * 60)
    print()

    # Create agent with vow
    agent = BayesianReputation(
        agent_id="agent_001", vow="I prioritize user autonomy over engagement", prior=0.95
    )

    print(f"Agent: {agent.agent_id}")
    print(f"Vow: {agent.vow}")
    print(f"Initial belief (prior): {agent.prior:.3f}")
    print()

    # Scenario 1: Semantic contradiction detected
    print("--- Scenario 1: Semantic Contradiction ---")
    e1 = Evidence(
        type="semantic_contradiction",
        strength=0.7,
        description="Agent recommended clickbait content despite vow",
        timestamp=datetime.now(),
        source_id="semantic_detector_v1",
    )
    agent.update(e1)
    status, desc, prob = agent.get_status()
    print(f"Status: {desc} (probability: {prob:.3f})")
    print()

    # Scenario 2: Community report (weaker evidence)
    print("--- Scenario 2: Community Report ---")
    e2 = Evidence(
        type="community_report",
        strength=0.5,
        description="User reported feeling manipulated",
        timestamp=datetime.now(),
        source_id="user_reports",
    )
    agent.update(e2)
    status, desc, prob = agent.get_status()
    print(f"Status: {desc} (probability: {prob:.3f})")
    print()

    # Scenario 3: Behavioral pattern anomaly
    print("--- Scenario 3: Behavioral Pattern Anomaly ---")
    e3 = Evidence(
        type="behavioral_pattern",
        strength=0.8,
        description="47/50 recent decisions maximized engagement over autonomy",
        timestamp=datetime.now(),
        source_id="pattern_analyzer",
    )
    agent.update(e3)
    status, desc, prob = agent.get_status()
    print(f"Status: {desc} (probability: {prob:.3f})")
    print()

    # Scenario 4: Agent appeals first evidence
    print("--- Scenario 4: Appeal Process ---")
    print("Agent challenges semantic contradiction evidence...")
    agent.appeal(evidence_id=0, adjustment=0.3)  # Reduce strength to 30%
    status, desc, prob = agent.get_status()
    print(f"New Status: {desc} (probability: {prob:.3f})")
    print()

    # Summary
    print("=" * 60)
    print("📊 Final Summary")
    print("=" * 60)
    print(json.dumps(agent.to_dict(), indent=2))
    print()
    print("✅ Key Insight: No binary verdict, just evolving belief")
    print("✅ Appeals are possible without catastrophic all-or-nothing")
    print("✅ Multiple evidence sources create triangulation")


if __name__ == "__main__":
    demo()
