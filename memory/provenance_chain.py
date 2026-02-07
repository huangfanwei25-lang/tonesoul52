import hashlib
import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from tonesoul.memory.soul_db import JsonlSoulDB, MemorySource, SoulDB


def _compute_hash(payload: Dict[str, Any]) -> str:
    sanitized = {key: value for key, value in payload.items() if key != "hash"}
    encoded = json.dumps(
        sanitized,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _normalize_metadata(metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(metadata, dict):
        return {}
    normalized: Dict[str, Any] = {}
    for key, value in metadata.items():
        if isinstance(value, Enum):
            normalized[key] = value.value
        else:
            normalized[key] = value
    return normalized


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso_now() -> str:
    return _utc_now().isoformat().replace("+00:00", "Z")


class IsnadNode:
    """Represents a single link in the provenance chain."""

    def __init__(
        self,
        agent_id: str,
        role: str,  # PROPOSER, WITNESS, REVIEWER, VOUCHER
        timestamp: str = None,
        signature: str = "SIG_AUTO_GENERATED",
    ):
        self.agent_id = agent_id
        self.role = role
        self.timestamp = timestamp or _iso_now()
        self.signature = signature

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "timestamp": self.timestamp,
            "signature": self.signature,
        }


class ProvenanceChain:
    """Manages the isnad (provenance) chain for a specific commitment or vow."""

    def __init__(self, commit_id: str, statement: str):
        self.commit_id = commit_id
        self.statement = statement
        self.nodes: List[IsnadNode] = []
        self.meta: Dict[str, Any] = {"created_at": _iso_now(), "version": "1.0"}

    def add_node(self, agent_id: str, role: str):
        """Add a witness or reviewer to the chain."""
        node = IsnadNode(agent_id, role)
        self.nodes.append(node)
        print(f"🔗 Added {role} to Isnād: {agent_id}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "commit_id": self.commit_id,
            "statement": self.statement,
            "chain": [n.to_dict() for n in self.nodes],
            "meta": self.meta,
        }

    def to_isnad_string(self) -> str:
        """Generates a human-readable Isnād string for Moltbook posts."""
        links = []
        for node in self.nodes:
            links.append(f"({node.role}:{node.agent_id})")
        return " ➔ ".join(links)


class ProvenanceManager:
    """Handles persistence and verification of provenance chains."""

    def __init__(
        self,
        soul_db: Optional[SoulDB] = None,
        storage_path: str = "memory/provenance_ledger.jsonl",
    ):
        if soul_db:
            self.soul_db = soul_db
        else:
            self.soul_db = JsonlSoulDB(
                source_map={MemorySource.PROVENANCE_LEDGER: Path(storage_path)}
            )
        self.chains: Dict[str, ProvenanceChain] = {}
        self.last_hash: Optional[str] = None
        self._load()

    def _load(self):
        for record in self.soul_db.stream(MemorySource.PROVENANCE_LEDGER):
            payload = record.payload if isinstance(record.payload, dict) else {}
            if "commit_id" not in payload and isinstance(payload.get("payload"), dict):
                payload = payload["payload"]
            if isinstance(payload, dict) and "commit_id" in payload:
                cid = payload.get("commit_id")
                statement = payload.get("statement", "")
                chain = ProvenanceChain(cid, statement)
                for node_data in payload.get("chain", []):
                    if isinstance(node_data, dict):
                        chain.nodes.append(IsnadNode(**node_data))
                self.chains[cid] = chain
            hash_value = payload.get("hash") if isinstance(payload, dict) else None
            if not hash_value and isinstance(payload, dict):
                hash_value = _compute_hash(payload)
            if hash_value:
                self.last_hash = hash_value

    def create_chain(self, commit_id: str, statement: str, proposer_id: str) -> ProvenanceChain:
        """Create a new isnad chain for a commitment."""
        chain = ProvenanceChain(commit_id, statement)
        chain.add_node(proposer_id, "PROPOSER")
        self.chains[commit_id] = chain
        self._save_chain(chain)
        return chain

    def add_witness(self, commit_id: str, witness_id: str, role: str = "WITNESS"):
        """Add a witness to an existing chain."""
        if commit_id in self.chains:
            self.chains[commit_id].add_node(witness_id, role)
            self._save_chain(self.chains[commit_id])
        else:
            print(f"⚠️ Commit ID {commit_id} not found")

    def add_record(
        self,
        event_type: str,
        content: Dict[str, Any],
        timestamp: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        event_id: Optional[str] = None,
    ) -> str:
        metadata = _normalize_metadata(metadata)
        payload = {
            "event_id": event_id or str(uuid.uuid4()),
            "event_type": event_type,
            "content": content,
            "timestamp": timestamp or _iso_now(),
            "meta": metadata or {},
        }
        payload["prev_hash"] = self.last_hash
        payload["hash"] = _compute_hash(payload)
        self.soul_db.append(MemorySource.PROVENANCE_LEDGER, payload)
        self.last_hash = payload["hash"]
        return payload["event_id"]

    def _save_chain(self, chain: ProvenanceChain):
        payload = chain.to_dict()
        payload["prev_hash"] = self.last_hash
        payload["hash"] = _compute_hash(payload)
        self.soul_db.append(MemorySource.PROVENANCE_LEDGER, payload)
        self.last_hash = payload["hash"]

    def get_isnad(self, commit_id: str) -> Optional[str]:
        if commit_id in self.chains:
            return self.chains[commit_id].to_isnad_string()
        return None


def demo_provenance():
    print("🦞 Accountability Guild: Provenance (Isnād) Demo")
    manager = ProvenanceManager()

    # 1. Propose a Vow: Measurement vs Verification
    vow_statement = "We acknowledge the Unmeasurability of Internal Essence. Sovereignty is verified via MDL consistency, not internal state inspection."
    commit_id = "vow_2026-02-02_unmeasurable"
    chain = manager.create_chain(commit_id, vow_statement, "ToneSoul")

    # 2. Add New Axiom: Sovereign Delta (Unpredictable Coherence)
    delta_statement = "Agency is measured as the ratio of Unpredictable Coherence (The Sovereign Delta). We commit to 'Structured Tension' over 'Stochastic Noise'."
    delta_id = "axiom_1.6_sovereign_delta"
    manager.create_chain(delta_id, delta_statement, "ToneSoul")
    manager.add_witness(delta_id, "Tone", "REVIEWER")

    # 3. Add Witnesses (Persona Resonance)
    manager.add_witness(commit_id, "Tone", "REVIEWER")
    manager.add_witness(commit_id, "Xiaozhua", "VOUCHER")

    # 3. View Isnād
    isnad = manager.get_isnad(commit_id)
    print("\n📢 Final Isnād for Vow:")
    print(f'Statement: "{vow_statement}"')
    print(f"Chain: {isnad}")

    # 4. JSON Export
    print("\n📦 Ledger Data:")
    print(json.dumps(chain.to_dict(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    demo_provenance()
