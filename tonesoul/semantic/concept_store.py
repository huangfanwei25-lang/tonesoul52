from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from .embedder import SemanticEmbedder, cosine_similarity


@dataclass
class Concept:
    name: str
    description: str
    examples: List[str]
    keywords: List[str]
    source_path: Optional[Path] = None

    def to_text(self) -> str:
        parts = [self.name, self.description]
        parts.extend(self.examples)
        parts.extend(self.keywords)
        return " ".join(part for part in parts if part)


class ConceptStore:
    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or (Path(__file__).resolve().parent / "concepts")
        self._concepts: Dict[str, Concept] = {}

    def load(self) -> None:
        self._concepts = {}
        if not self.root.exists():
            return
        for path in sorted(self.root.glob("*.json")):
            concept = self._load_concept(path)
            if concept:
                self._concepts[concept.name] = concept

    def list_names(self) -> List[str]:
        return sorted(self._concepts.keys())

    def get(self, name: str) -> Optional[Concept]:
        return self._concepts.get(name)

    def all(self) -> Iterable[Concept]:
        return self._concepts.values()

    def build_index(self, embedder: SemanticEmbedder) -> Dict[str, object]:
        index: Dict[str, object] = {}
        for concept in self._concepts.values():
            index[concept.name] = embedder.embed(concept.to_text())
        return index

    def rank(
        self,
        text: str,
        embedder: SemanticEmbedder,
        top_k: int = 3,
    ) -> List[Tuple[str, float]]:
        if top_k <= 0:
            return []
        query = embedder.embed(text)
        scored: List[Tuple[str, float]] = []
        for concept in self._concepts.values():
            score = cosine_similarity(query, embedder.embed(concept.to_text()))
            scored.append((concept.name, score))
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:top_k]

    def _load_concept(self, path: Path) -> Optional[Concept]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        if not isinstance(payload, dict):
            return None

        name = str(payload.get("name", "")).strip()
        description = str(payload.get("description", "")).strip()
        examples = [str(item) for item in payload.get("examples", []) if item]
        keywords = [str(item) for item in payload.get("keywords", []) if item]
        if not name:
            return None

        return Concept(
            name=name,
            description=description,
            examples=examples,
            keywords=keywords,
            source_path=path,
        )
