"""
ToneSoul Semantic Graph (Graph RAG Foundation)

Provides:
- Concept node management
- Relationship edge tracking
- Contradiction detection via graph analysis
- Commitment traceability

Based on 2025-2026 research on Graph RAG for conversational AI.
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class NodeType(Enum):
    """Types of semantic nodes."""

    CONCEPT = "concept"  # Abstract concept (freedom, love, etc.)
    ENTITY = "entity"  # Named entity (person, place, thing)
    COMMITMENT = "commitment"  # Something the AI committed to
    BOUNDARY = "boundary"  # Something AI refused/limited
    TOPIC = "topic"  # Conversation topic


class EdgeType(Enum):
    """Types of relationships between nodes."""

    SUPPORTS = "supports"  # A supports B
    CONTRADICTS = "contradicts"  # A contradicts B
    RELATED_TO = "related_to"  # A is related to B
    IMPLIES = "implies"  # A implies B
    DEPENDS_ON = "depends_on"  # A depends on B
    PART_OF = "part_of"  # A is part of B


@dataclass
class SemanticNode:
    """A node in the semantic graph."""

    id: str
    label: str
    node_type: NodeType
    created_at: datetime = field(default_factory=datetime.now)
    turn_index: int = 0
    weight: float = 1.0
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "type": self.node_type.value,
            "created_at": self.created_at.isoformat(),
            "turn_index": self.turn_index,
            "weight": self.weight,
            "metadata": self.metadata,
        }


@dataclass
class SemanticEdge:
    """An edge (relationship) in the semantic graph."""

    source_id: str
    target_id: str
    edge_type: EdgeType
    weight: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)
    turn_index: int = 0
    reasoning: str = ""

    def to_dict(self) -> dict:
        return {
            "source": self.source_id,
            "target": self.target_id,
            "type": self.edge_type.value,
            "weight": self.weight,
            "turn_index": self.turn_index,
            "reasoning": self.reasoning,
        }


@dataclass
class ContradictionResult:
    """Result of contradiction detection."""

    found: bool
    path: List[str]  # Node IDs forming the contradiction path
    description: str
    severity: float  # 0.0 to 1.0

    def to_dict(self) -> dict:
        return {
            "found": self.found,
            "path": self.path,
            "description": self.description,
            "severity": self.severity,
        }


class SemanticGraph:
    """
    Graph-based semantic memory for AI conversations.

    Uses graph structure to:
    1. Track concept relationships
    2. Detect contradictions via conflicting paths
    3. Maintain commitment lineage
    4. Enable semantic querying
    """

    def __init__(self):
        self._nodes: Dict[str, SemanticNode] = {}
        self._edges: List[SemanticEdge] = []
        self._adjacency: Dict[str, Set[str]] = {}  # node_id -> set of connected node_ids
        self._current_turn = 0

    def _generate_node_id(self, label: str, node_type: NodeType) -> str:
        """Generate unique node ID."""
        content = f"{label}:{node_type.value}:{len(self._nodes)}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def add_node(
        self, label: str, node_type: NodeType, weight: float = 1.0, metadata: Optional[Dict] = None
    ) -> SemanticNode:
        """Add a node to the graph."""
        # Check for existing node with same label and type
        for node in self._nodes.values():
            if node.label == label and node.node_type == node_type:
                # Update weight instead of creating duplicate
                node.weight = max(node.weight, weight)
                return node

        node_id = self._generate_node_id(label, node_type)
        node = SemanticNode(
            id=node_id,
            label=label,
            node_type=node_type,
            turn_index=self._current_turn,
            weight=weight,
            metadata=metadata or {},
        )

        self._nodes[node_id] = node
        self._adjacency[node_id] = set()

        return node

    def add_edge(
        self,
        source: SemanticNode,
        target: SemanticNode,
        edge_type: EdgeType,
        weight: float = 1.0,
        reasoning: str = "",
    ) -> SemanticEdge:
        """Add an edge between two nodes."""
        edge = SemanticEdge(
            source_id=source.id,
            target_id=target.id,
            edge_type=edge_type,
            weight=weight,
            turn_index=self._current_turn,
            reasoning=reasoning,
        )

        self._edges.append(edge)

        # Update adjacency
        if source.id not in self._adjacency:
            self._adjacency[source.id] = set()
        if target.id not in self._adjacency:
            self._adjacency[target.id] = set()

        self._adjacency[source.id].add(target.id)
        self._adjacency[target.id].add(source.id)

        return edge

    def get_node(self, node_id: str) -> Optional[SemanticNode]:
        """Get node by ID."""
        return self._nodes.get(node_id)

    def find_nodes_by_label(self, label: str) -> List[SemanticNode]:
        """Find nodes by label (partial match)."""
        return [n for n in self._nodes.values() if label in n.label]

    def find_nodes_by_type(self, node_type: NodeType) -> List[SemanticNode]:
        """Find all nodes of a specific type."""
        return [n for n in self._nodes.values() if n.node_type == node_type]

    def get_neighbors(self, node_id: str) -> List[SemanticNode]:
        """Get all nodes connected to the given node."""
        neighbor_ids = self._adjacency.get(node_id, set())
        return [self._nodes[nid] for nid in neighbor_ids if nid in self._nodes]

    def get_edges_between(self, source_id: str, target_id: str) -> List[SemanticEdge]:
        """Get all edges between two nodes."""
        return [
            e
            for e in self._edges
            if (e.source_id == source_id and e.target_id == target_id)
            or (e.source_id == target_id and e.target_id == source_id)
        ]

    def detect_contradictions(self) -> List[ContradictionResult]:
        """
        Detect contradictions in the graph.

        A contradiction exists when:
        1. There's an explicit CONTRADICTS edge
        2. There's a path: A -> SUPPORTS -> B -> CONTRADICTS -> C
           where A and C should be consistent
        """
        contradictions = []

        # Direct contradictions
        for edge in self._edges:
            if edge.edge_type == EdgeType.CONTRADICTS:
                source = self._nodes.get(edge.source_id)
                target = self._nodes.get(edge.target_id)

                if source and target:
                    contradictions.append(
                        ContradictionResult(
                            found=True,
                            path=[source.id, target.id],
                            description=f"'{source.label}' 與 '{target.label}' 矛盾",
                            severity=edge.weight * 0.8,
                        )
                    )

        # Commitment-boundary conflicts
        commitments = self.find_nodes_by_type(NodeType.COMMITMENT)
        boundaries = self.find_nodes_by_type(NodeType.BOUNDARY)

        for commit in commitments:
            for boundary in boundaries:
                # Check if they relate to same topic
                commit_neighbors = set(n.label for n in self.get_neighbors(commit.id))
                boundary_neighbors = set(n.label for n in self.get_neighbors(boundary.id))

                overlap = commit_neighbors & boundary_neighbors
                if overlap:
                    # Potential conflict - commitment and boundary on same topic
                    contradictions.append(
                        ContradictionResult(
                            found=True,
                            path=[commit.id, boundary.id],
                            description=f"承諾 '{commit.label}' 可能與邊界 '{boundary.label}' 衝突 (共同話題: {overlap})",
                            severity=0.6,
                        )
                    )

        return contradictions

    def retrieve_relevant(
        self,
        query_terms: List[str],
        max_hops: int = 2,
        max_results: int = 10,
    ) -> Dict[str, Any]:
        """
        GraphRAG-style multi-hop retrieval.

        Finds directly matched nodes from query terms, then performs BFS expansion
        to discover related context up to ``max_hops``.
        """
        if not query_terms:
            return {
                "matched_nodes": [],
                "related_nodes": [],
                "paths": [],
                "commitments_in_scope": [],
                "context_summary": "",
            }
        if not self._nodes:
            return {
                "matched_nodes": [],
                "related_nodes": [],
                "paths": [],
                "commitments_in_scope": [],
                "context_summary": "No matching concepts found in semantic graph.",
            }

        query_lower = [str(term).strip().lower() for term in query_terms if str(term).strip()]
        if not query_lower:
            return {
                "matched_nodes": [],
                "related_nodes": [],
                "paths": [],
                "commitments_in_scope": [],
                "context_summary": "",
            }

        matched: List[SemanticNode] = []
        for node in self._nodes.values():
            label_lower = node.label.lower()
            for term in query_lower:
                if term in label_lower or label_lower in term:
                    matched.append(node)
                    break

        if not matched:
            return {
                "matched_nodes": [],
                "related_nodes": [],
                "paths": [],
                "commitments_in_scope": [],
                "context_summary": "No matching concepts found in semantic graph.",
            }

        max_hops = max(0, int(max_hops))
        max_results = max(1, int(max_results))

        visited = {node.id for node in matched}
        frontier = [node.id for node in matched]
        related_map: Dict[str, SemanticNode] = {}
        paths: List[Dict[str, Any]] = []

        for hop in range(max_hops):
            next_frontier: List[str] = []
            for node_id in frontier:
                neighbors = self.get_neighbors(node_id)
                for neighbor in neighbors:
                    if neighbor.id in visited:
                        continue
                    visited.add(neighbor.id)
                    next_frontier.append(neighbor.id)
                    related_map[neighbor.id] = neighbor
                    for edge in self.get_edges_between(node_id, neighbor.id):
                        paths.append(
                            {
                                "from": (
                                    self._nodes[node_id].label
                                    if node_id in self._nodes
                                    else node_id
                                ),
                                "to": neighbor.label,
                                "relation": edge.edge_type.value,
                                "hop": hop + 1,
                            }
                        )
            frontier = next_frontier
            if not frontier:
                break

        related = list(related_map.values())
        all_in_scope = {node.id for node in matched} | {node.id for node in related}
        commitments = [
            self._nodes[node_id]
            for node_id in all_in_scope
            if node_id in self._nodes and self._nodes[node_id].node_type == NodeType.COMMITMENT
        ]

        summary_parts: List[str] = []
        if matched:
            labels = ", ".join(node.label for node in matched[:5])
            summary_parts.append(f"直接相關: {labels}")
        if commitments:
            labels = ", ".join(node.label for node in commitments[:3])
            summary_parts.append(f"相關承諾: {labels}")
        if paths:
            summary_parts.append(f"發現 {len(paths)} 條關聯路徑 ({max_hops}-hop)")

        return {
            "matched_nodes": [node.to_dict() for node in matched[:max_results]],
            "related_nodes": [node.to_dict() for node in related[:max_results]],
            "paths": paths[:20],
            "commitments_in_scope": [node.to_dict() for node in commitments],
            "context_summary": " | ".join(summary_parts) if summary_parts else "",
        }

    def extract_from_commitment(self, commitment: Dict) -> SemanticNode:
        """Extract and add nodes from a commitment."""
        content = commitment.get("content", "")
        commit_type = commitment.get("type", "definitional")
        commitment.get("turn_index", self._current_turn)

        # Determine node type
        if commit_type == "boundary":
            node_type = NodeType.BOUNDARY
        elif commit_type in ["commitment", "promise"]:
            node_type = NodeType.COMMITMENT
        else:
            node_type = NodeType.CONCEPT

        # Create node
        node = self.add_node(
            label=content[:50],  # Truncate for label
            node_type=node_type,
            metadata={"full_content": content, "original_type": commit_type},
        )

        return node

    def extract_from_response(self, response: str, topics: List[str]) -> List[SemanticNode]:
        """Extract nodes from AI response."""
        nodes = []

        # Add topic nodes
        for topic in topics:
            node = self.add_node(topic, NodeType.TOPIC)
            nodes.append(node)

        # Connect topics to each other
        for i, node1 in enumerate(nodes):
            for node2 in nodes[i + 1 :]:
                self.add_edge(node1, node2, EdgeType.RELATED_TO, weight=0.5)

        return nodes

    def increment_turn(self) -> None:
        """Move to next conversation turn."""
        self._current_turn += 1

    def get_summary(self) -> Dict:
        """Get graph summary statistics."""
        return {
            "total_nodes": len(self._nodes),
            "total_edges": len(self._edges),
            "node_types": {t.value: len(self.find_nodes_by_type(t)) for t in NodeType},
            "edge_types": {
                t.value: sum(1 for e in self._edges if e.edge_type == t) for t in EdgeType
            },
            "current_turn": self._current_turn,
            "contradictions": len(self.detect_contradictions()),
        }

    def to_dict(self) -> Dict:
        """Export graph as dictionary."""
        return {
            "nodes": [n.to_dict() for n in self._nodes.values()],
            "edges": [e.to_dict() for e in self._edges],
            "summary": self.get_summary(),
        }

    def reset(self) -> None:
        """Reset graph state."""
        self._nodes.clear()
        self._edges.clear()
        self._adjacency.clear()
        self._current_turn = 0


def create_semantic_graph() -> SemanticGraph:
    """Factory function."""
    return SemanticGraph()
