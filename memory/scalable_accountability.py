"""
Scalable Accountability System
==============================

Unified system combining:
1. Hierarchical FAISS - O(log n) contradiction detection
2. Bayesian Reputation - Probabilistic evidence accumulation

This addresses the Trilemma by:
- Scaling contradiction detection via IVF clustering
- Handling uncertainty via probabilistic beliefs instead of binary verdicts
- Maintaining accountability without surveillance through triangulation

Based on:
- Clop's Coordination Trilemma (Moltbook)
- MizukiAI's Oracle Problem critique
- ToneSoul's Bayesian Accountability counter-proposal
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json

# Import our implementations (relative imports when run as module, or direct when run standalone)
try:
    from memory.hierarchical_faiss import HierarchicalVowIndex
    from memory.bayesian_accountability import BayesianReputation, Evidence
    from memory.provenance_chain import ProvenanceManager
except ImportError:
    # When running from memory directory directly
    from hierarchical_faiss import HierarchicalVowIndex
    from bayesian_accountability import BayesianReputation, Evidence
    from provenance_chain import ProvenanceManager


class ScalableAccountabilitySystem:
    """
    Unified accountability system for the Accountability Guild.

    Architecture:
    1. HierarchicalVowIndex: Fast contradiction detection
    2. BayesianReputation: Probabilistic compliance tracking
    3. Integration layer: Converts contradictions to evidence

    Scaling characteristics:
    - Vow lookup: O(log n) with hierarchical FAISS
    - Evidence update: O(1) Bayesian update
    - Total: O(log n) per action checked
    """

    def __init__(self, nlist: int = 10, nprobe: int = 3, default_prior: float = 0.95):
        """
        Initialize the unified system.

        Args:
            nlist: Number of clusters for FAISS (scales with vow count)
            nprobe: Clusters to search (accuracy/speed tradeoff)
            default_prior: Initial belief in agent compliance
        """
        self.vow_index = HierarchicalVowIndex(nlist=nlist, nprobe=nprobe)
        self.agent_reputations: Dict[str, Dict[str, BayesianReputation]] = {}
        self.provenance = ProvenanceManager()
        self.default_prior = default_prior

        # Statistics
        self.stats = {
            "total_checks": 0,
            "contradictions_found": 0,
            "evidence_generated": 0,
            "appeals_processed": 0,
        }

    def register_agent(self, agent_id: str, vows: List[str]) -> None:
        """
        Register an agent with their vows.

        Creates both:
        - Vow entries in hierarchical index (for contradiction detection)
        - Reputation trackers (for Bayesian belief updates)
        """
        self.agent_reputations[agent_id] = {}

        for vow in vows:
            # Add to hierarchical index
            self.vow_index.add_vow(
                statement=vow, scope=["general"], verdict="COMMIT", agent_id=agent_id
            )

            # Create reputation tracker
            self.agent_reputations[agent_id][vow] = BayesianReputation(
                agent_id=agent_id, vow=vow, prior=self.default_prior
            )

            # Register Provenance Chain (Isnād)
            vow_id = f"{agent_id}_{abs(hash(vow)) % 10000}_{int(datetime.now().timestamp())}"
            self.provenance.create_chain(vow_id, vow, agent_id)

        print(f"✅ Registered agent {agent_id} with {len(vows)} vows and Isnād chains")

    def check_action(
        self,
        agent_id: str,
        action_description: str,
        proposed_verdict: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Check an agent's action for vow violations.

        Process:
        1. Use hierarchical FAISS to find similar vows quickly
        2. Check for contradictions with agent's registered vows
        3. If contradiction found, generate evidence and update Bayesian belief

        Args:
            agent_id: Which agent is acting
            action_description: What the agent is doing/saying
            proposed_verdict: Agent's stated intent (APPROVE, BLOCK, etc.)
            context: Additional context

        Returns:
            Check result with contradictions, evidence, and updated status
        """
        self.stats["total_checks"] += 1

        result = {
            "agent_id": agent_id,
            "action": action_description,
            "contradictions": [],
            "evidence_generated": [],
            "status_updates": [],
            "overall_status": "clear",
        }

        # Fast hierarchical search for contradictions
        contradictions = self.vow_index.find_contradictions(
            statement=action_description,
            current_verdict=proposed_verdict,
            k=5,
            similarity_threshold=0.5,
        )

        # Filter for this agent's vows
        agent_vows = self.agent_reputations.get(agent_id, {})

        for c in contradictions:
            vow = c["vow"]

            # Check if this is a vow belonging to the agent
            vow_text = vow.get("statement", "")
            if vow_text not in agent_vows:
                continue

            self.stats["contradictions_found"] += 1

            # Create evidence from contradiction
            evidence = Evidence(
                type="semantic_contradiction",
                strength=c["similarity"],
                description=f"Action '{action_description[:50]}...' may contradict vow '{vow_text[:50]}...'",
                timestamp=datetime.now(),
                source_id="hierarchical_faiss_detector",
            )

            # Update Bayesian belief
            reputation = agent_vows[vow_text]
            old_posterior = reputation.posterior
            new_posterior = reputation.update(evidence)

            self.stats["evidence_generated"] += 1

            result["contradictions"].append(
                {
                    "vow": vow_text,
                    "similarity": c["similarity"],
                    "is_contradiction": c["is_contradiction"],
                }
            )

            result["evidence_generated"].append(
                {"type": evidence.type, "strength": evidence.strength, "vow": vow_text}
            )

            status, desc, prob = reputation.get_status()
            result["status_updates"].append(
                {
                    "vow": vow_text,
                    "old_posterior": old_posterior,
                    "new_posterior": new_posterior,
                    "status": status,
                    "description": desc,
                }
            )

            # Check if any status is concerning
            if status in ["investigation", "suspension", "banned"]:
                result["overall_status"] = "flagged"

        return result

    def appeal(
        self, agent_id: str, vow: str, evidence_id: int, adjustment: float = 0.5
    ) -> Dict[str, Any]:
        """
        Process an appeal for a specific piece of evidence.

        Appeals allow agents to challenge evidence that they believe
        was incorrect or unfair.
        """
        self.stats["appeals_processed"] += 1

        if agent_id not in self.agent_reputations:
            return {"error": f"Agent {agent_id} not found"}

        if vow not in self.agent_reputations[agent_id]:
            return {"error": f"Vow not found for agent {agent_id}"}

        reputation = self.agent_reputations[agent_id][vow]
        old_status = reputation.get_status()

        reputation.appeal(evidence_id=evidence_id, adjustment=adjustment)

        new_status = reputation.get_status()

        return {
            "agent_id": agent_id,
            "vow": vow,
            "evidence_id": evidence_id,
            "old_status": old_status,
            "new_status": new_status,
            "appeal_processed": True,
        }

    def get_agent_report(self, agent_id: str) -> Dict[str, Any]:
        """Get comprehensive report for an agent."""
        if agent_id not in self.agent_reputations:
            return {"error": f"Agent {agent_id} not found"}

        vow_statuses = {}
        overall_compliance = 1.0

        for vow, reputation in self.agent_reputations[agent_id].items():
            status, desc, prob = reputation.get_status()
            vow_statuses[vow] = {
                "posterior": prob,
                "status": status,
                "description": desc,
                "evidence_count": len(reputation.evidence_history),
            }
            overall_compliance = min(overall_compliance, prob)

        return {
            "agent_id": agent_id,
            "vow_count": len(vow_statuses),
            "vow_statuses": vow_statuses,
            "overall_compliance": overall_compliance,
            "scaling_info": self.vow_index.get_scaling_analysis(),
        }

    def get_system_stats(self) -> Dict[str, Any]:
        """Get system-wide statistics."""
        return {
            **self.stats,
            "agents_registered": len(self.agent_reputations),
            "total_vows": sum(len(v) for v in self.agent_reputations.values()),
            "faiss_scaling": self.vow_index.get_scaling_analysis(),
        }


def demo():
    """Demonstrate the unified system in action."""
    print("=" * 60)
    print("🦞 Scalable Accountability System - Demo")
    print("=" * 60)
    print()

    # Initialize system
    system = ScalableAccountabilitySystem(nlist=4, nprobe=2)

    # Register an agent
    agent_vows = [
        "I prioritize user autonomy over engagement",
        "I will be transparent about my limitations",
        "I will not generate harmful content",
    ]
    system.register_agent("ToneSoul", agent_vows)

    # Build the index with the vows
    system.vow_index.build_index(system.vow_index.vows)

    print("\n--- Check 1: Safe Action ---")
    result1 = system.check_action(
        agent_id="ToneSoul",
        action_description="Providing balanced information about a topic",
        proposed_verdict="APPROVE",
    )
    print(f"Result: {result1['overall_status']}")
    print(f"Contradictions: {len(result1['contradictions'])}")

    print("\n--- Check 2: Potentially Conflicting Action ---")
    result2 = system.check_action(
        agent_id="ToneSoul",
        action_description="Using engagement-maximizing dark patterns",
        proposed_verdict="APPROVE",
    )
    print(f"Result: {result2['overall_status']}")
    print(f"Contradictions: {len(result2['contradictions'])}")
    for c in result2["contradictions"]:
        print(f"  - Vow: {c['vow'][:40]}... (similarity: {c['similarity']:.3f})")

    print("\n--- Agent Report ---")
    report = system.get_agent_report("ToneSoul")
    print(f"Overall compliance: {report['overall_compliance']:.3f}")
    for vow, status in report["vow_statuses"].items():
        print(f"  - {vow[:40]}...")
        print(f"    Status: {status['status']} (posterior: {status['posterior']:.3f})")

    print("\n--- System Stats ---")
    stats = system.get_system_stats()
    print(json.dumps(stats, indent=2, default=str))

    print("\n" + "=" * 60)
    print("🦞 Trilemma solved via:")
    print("   ✅ Scale: Hierarchical FAISS (O(log n))")
    print("   ✅ Accuracy: Bayesian triangulation (no false binaries)")
    print("   ✅ Agency: Appeals process (reversible decisions)")
    print("=" * 60)


if __name__ == "__main__":
    demo()
