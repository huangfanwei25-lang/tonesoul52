import hashlib
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

import numpy as np

from .energy import EnergyConfig, apply_energy_totals, compute_raw_total
from .schema import (
    MathCoords,
    Node,
    NodeAudit,
    NodeDrift,
    NodeScalar,
    NodeWhat,
    SourceRef,
    Where,
    WhereField,
    WhereTask,
    WhereTime,
    stable_hash,
    utc_now,
)


@dataclass(frozen=True)
class EmbeddingConfig:
    dims: int = 12


def tokenize(text: str) -> List[str]:
    tokens = re.split(r"[^\w]+", text.lower())
    return [token for token in tokens if token]


def simple_embed(text: str, dims: int) -> np.ndarray:
    """Simple embedding using token hashing (non-cryptographic)."""
    vec = np.zeros(dims, dtype=float)
    for token in tokenize(text):
        # MD5 used for deterministic index calculation, not security
        digest = hashlib.md5(token.encode("utf-8"), usedforsecurity=False).hexdigest()
        idx = int(digest, 16) % dims
        vec[idx] += 1.0
    return vec


def embed_text(text: str, config: EmbeddingConfig) -> np.ndarray:
    return simple_embed(text, dims=config.dims)


def _clean_str(value: object) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _to_optional_float(value: object) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _math_coords_from_segment(segment: Dict[str, object]) -> Optional[MathCoords]:
    math_data = segment.get("math_coords") if isinstance(segment.get("math_coords"), dict) else {}
    height = segment.get("math_height")
    if height is None:
        height = math_data.get("height")
    geology = segment.get("math_geology")
    if geology is None:
        geology = math_data.get("geology")
    ruggedness = segment.get("math_ruggedness")
    if ruggedness is None:
        ruggedness = math_data.get("ruggedness")

    coords = MathCoords(
        height=_to_optional_float(height),
        geology=_clean_str(geology),
        ruggedness=_to_optional_float(ruggedness),
    )
    if coords.height is None and coords.geology is None and coords.ruggedness is None:
        return None
    return coords


def _source_from_segment(segment: Dict[str, object], text: str) -> tuple[SourceRef, Optional[str]]:
    source = segment.get("source") if isinstance(segment.get("source"), dict) else {}
    source_type = _clean_str(segment.get("source_type")) or _clean_str(source.get("type")) or "demo"
    source_uri = _clean_str(segment.get("source_uri")) or _clean_str(source.get("uri"))
    source_hash = (
        _clean_str(segment.get("source_hash"))
        or _clean_str(source.get("hash"))
        or stable_hash(text)
    )
    source_grade = _clean_str(segment.get("source_grade")) or _clean_str(source.get("grade"))
    retrieved_at = _clean_str(segment.get("source_retrieved_at")) or _clean_str(
        source.get("retrieved_at")
    )
    verified_by = _clean_str(segment.get("source_verified_by")) or _clean_str(
        source.get("verified_by")
    )
    return (
        SourceRef(
            type=source_type,
            uri=source_uri,
            hash=source_hash,
            grade=source_grade,
            retrieved_at=retrieved_at,
            verified_by=verified_by,
        ),
        source_grade,
    )


def build_nodes(
    segments: Sequence[Dict[str, object]],
    created_by: str = "ystm_demo",
    config: EmbeddingConfig = EmbeddingConfig(),
    energy: EnergyConfig = EnergyConfig(),
) -> List[Node]:
    nodes: List[Node] = []
    created_at = utc_now()
    for index, segment in enumerate(segments):
        text = str(segment["text"])
        v_sem = embed_text(text, config)
        norm = float(np.linalg.norm(v_sem))
        e_srsp = float(segment.get("E_srsp", 0.0))
        e_risk = float(segment.get("E_risk", 0.0))
        raw_total = compute_raw_total(norm, e_srsp, e_risk, energy)
        source_ref, source_grade = _source_from_segment(segment, text)
        math_coords = _math_coords_from_segment(segment)
        node = Node(
            id=f"node_{index + 1:03d}",
            text=text,
            source=source_ref,
            where=Where(
                where_time=WhereTime(
                    turn_id=int(segment.get("turn_id", index + 1)),
                    event_index=index,
                    timestamp=segment.get("timestamp"),
                    version_id=segment.get("version_id"),
                ),
                where_field=WhereField(
                    mode=str(segment["mode"]),
                    submode=segment.get("submode"),
                    confidence=float(segment.get("mode_confidence", 0.9)),
                ),
                where_task=WhereTask(
                    domain=str(segment["domain"]),
                    subdomain=segment.get("subdomain"),
                    confidence=float(segment.get("domain_confidence", 0.9)),
                ),
            ),
            what=NodeWhat(v_sem=v_sem.tolist(), mu=norm),
            scalar=NodeScalar(E_energy=norm, E_srsp=e_srsp, E_risk=e_risk, E_total=raw_total),
            drift=NodeDrift(),
            audit=NodeAudit(created_at=created_at, created_by=created_by, updates=[]),
            source_grade=source_grade,
            math_coords=math_coords,
        )
        nodes.append(node)

    nodes = apply_energy_totals(nodes, energy)

    for index in range(1, len(nodes)):
        prev_node = nodes[index - 1]
        current = nodes[index]
        delta_v = np.array(current.what.v_sem) - np.array(prev_node.what.v_sem)
        current.drift = NodeDrift(
            delta_v=delta_v.tolist(),
            delta_norm=float(np.linalg.norm(delta_v)),
            drift_ref={"from_node_id": prev_node.id},
        )

    return nodes
