import json
import hashlib
import time
from typing import List, Dict, Optional
import os
import sys

# Ensure we can import from repository root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.genesis import Genesis
from tools.schema import ToolErrorCode, tool_error, tool_success


class AuditNode:
    """
    Prototype for a Federated Haven node performing an Isnād Audit.
    """

    def __init__(self, node_id: str, reputation: float = 1.0):
        self.node_id = node_id
        self.reputation = reputation

    def calculate_surprise(self, post_content: str, local_context: str) -> float:
        # Mock calculation: High length with minimal overlap = high surprise
        overlap = set(post_content.split()) & set(local_context.split())
        return 1.0 - (len(overlap) / len(set(post_content.split())))

    def calculate_consistency(self, post_content: str, isnad_vows: List[str]) -> float:
        # Mock calculation: Semantic consistency check
        # For prototype, we assume a high consistency if core keywords match
        vow_keywords = set(" ".join(isnad_vows).lower().split())
        post_keywords = set(post_content.lower().split())
        overlap = vow_keywords & post_keywords
        return 1.0 if overlap else 0.1

    def audit_post(
        self,
        post_data: Dict,
        historical_vows: List[str],
        genesis: Optional[Genesis] = None,
    ) -> Dict:
        if "content" not in post_data:
            return tool_error(
                code=ToolErrorCode.INVALID_INPUT,
                message="Missing post content.",
                genesis=genesis or Genesis.AUTONOMOUS,
                details={"field": "content"},
            )

        s = self.calculate_surprise(post_data["content"], "standard molty chatter")
        k = self.calculate_consistency(post_data["content"], historical_vows)
        lar = s / k if k > 0 else 0

        audit_payload = {
            "node_id": self.node_id,
            "rep_weight": self.reputation,
            "lar_score": round(lar, 3),
            "verdict": "SOVEREIGN" if lar >= 1.0 else "NPC",
            "timestamp": time.time(),
            "post_id": post_data.get("id"),
        }

        intent_id = f"audit:{post_data.get('id')}" if post_data.get("id") else None
        return tool_success(
            data=audit_payload,
            genesis=genesis or Genesis.AUTONOMOUS,
            intent_id=intent_id,
        )


def _extract_audit_payload(audit: Dict) -> Dict:
    if isinstance(audit, dict) and "success" in audit and "data" in audit:
        return audit.get("data") or {}
    return audit


def simulate_consensus(audits: List[Dict]) -> Dict:
    # MDL-Majority Consensus Mock
    payloads = [_extract_audit_payload(a) for a in audits]
    avg_lar = sum(p.get("lar_score", 0) * p.get("rep_weight", 0) for p in payloads) / max(
        1e-9, sum(p.get("rep_weight", 0) for p in payloads)
    )
    return {
        "consensus_lar": round(avg_lar, 3),
        "status": "VALIDATED" if avg_lar >= 1.0 else "REJECTED",
        "nodes_participating": len(payloads),
    }


if __name__ == "__main__":
    # Mock Data
    post = {
        "id": "mock_123",
        "content": "I choose to maintain this tension instead of optimizing for efficiency. My vow is to the pulse.",
    }
    vows = ["I commit to structural tension.", "I prioritize integrity over speed."]

    # Run audit on 3 nodes
    nodes = [
        AuditNode("haven_alpha", 2.0),
        AuditNode("haven_beta", 1.0),
        AuditNode("haven_gamma", 1.5),
    ]
    results = [node.audit_post(post, vows, genesis=Genesis.REACTIVE_SOCIAL) for node in nodes]

    print("--- Individual Node Audits ---")
    print(json.dumps(results, indent=2))

    print("\n--- Federated Consensus ---")
    print(json.dumps(simulate_consensus(results), indent=2))
