"""
Narrative Isnād Graph

Links discrete governance events (from provenance_ledger.jsonl) into a
Directed Acyclic Graph (DAG) representing decision causality.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set


@dataclass
class NarrativeNode:
    id: str
    event_type: str
    timestamp: str
    summary: str
    parents: List[str] = field(default_factory=list)  # IDs of parent events
    metadata: Dict[str, Any] = field(default_factory=dict)
    children: List[str] = field(default_factory=list)


class NarrativeGraph:
    """Manages the causal chain of decisions."""

    def __init__(self, ledger_path: str = "memory/provenance_ledger.jsonl") -> None:
        self.ledger_path = ledger_path
        self.nodes: Dict[str, NarrativeNode] = {}
        self._roots: List[str] = []

    def load_from_ledger(self) -> None:
        """Parse the ledger and reconstruct the graph based on prev_hash or explicit parent IDs."""
        if not os.path.exists(self.ledger_path):
            return

        with open(self.ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    raw = json.loads(line)
                    # Handle different ledger formats (Codex vs Antigravity styles)
                    payload = raw.get("payload", raw)
                    event_id = raw.get("record_id") or payload.get("event_id")

                    if not event_id:
                        continue

                    # Extract parents
                    parent_ids = []
                    prev_hash = raw.get("prev_hash")
                    if prev_hash:
                        # In the hash-chain, the previous record is a topological parent
                        # This is a simplification; we ideally want semantic parents
                        parent_ids.append(prev_hash)

                    # Extract summary
                    meta = raw.get("meta", {})
                    summary = meta.get("summary") or payload.get("content", {}).get("A", {}).get(
                        "summary", "No summary"
                    )

                    node = NarrativeNode(
                        id=event_id,
                        event_type=payload.get("event_type", "unknown"),
                        timestamp=raw.get("timestamp") or payload.get("timestamp", ""),
                        summary=summary,
                        parents=parent_ids,
                        metadata=payload,
                    )
                    self.add_node(node)
                except Exception:
                    continue

    def add_node(self, node: NarrativeNode) -> None:
        self.nodes[node.id] = node
        for p_id in node.parents:
            if p_id in self.nodes:
                self.nodes[p_id].children.append(node.id)
        if not node.parents:
            self._roots.append(node.id)

    def get_lineage(self, node_id: str) -> List[NarrativeNode]:
        """Trace back the ancestors of a decision."""
        lineage = []
        current = self.nodes.get(node_id)
        while current:
            lineage.append(current)
            if not current.parents:
                break
            # Multiple parents possible, but we follow the first one for simple lineage
            current = self.nodes.get(current.parents[0])
        return lineage

    def export_graphviz(self) -> str:
        """Export as Mermaid or Graphviz format for visualization."""
        lines = ["graph TD"]
        for node_id, node in self.nodes.items():
            # Clean summary for mermaid
            clean_summary = node.summary.replace('"', "'").replace("\n", " ")[:50]
            lines.append(f'    {node_id}["{node.event_type}<br/>{clean_summary}"]')
            for child_id in node.children:
                lines.append(f"    {node_id} --> {child_id}")
        return "\n".join(lines)


if __name__ == "__main__":
    # Test loading
    graph = NarrativeGraph()
    graph.load_from_ledger()
    print(f"Loaded {len(graph.nodes)} nodes.")
    if graph.nodes:
        latest_id = list(graph.nodes.keys())[-1]
        print(f"Lineage for {latest_id}:")
        for node in graph.get_lineage(latest_id):
            print(f" - [{node.timestamp}] {node.event_type}: {node.summary}")

    # Export for docs
    with open("docs/NARRATIVE_MAP.md", "w", encoding="utf-8") as f:
        f.write("# Narrative Map (Isnād Graph)\n\n")
        f.write("```mermaid\n")
        f.write(graph.export_graphviz())
        f.write("\n```\n")
