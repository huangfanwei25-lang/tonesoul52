"""ToneSoul Scribe Engine.

The orchestrator that reads from soul.db and generates autobiographical chronicles.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from sqlite3 import Connection
from typing import Any, Sequence

from tonesoul.llm.ollama_client import OllamaClient
from tonesoul.scribe.narrative_builder import (
    ScribeCollisionRecord,
    ScribeCrystalRecord,
    ScribeNarrativeBuilder,
    ScribeObservationSummary,
    ScribeTensionRecord,
)

logger = logging.getLogger(__name__)

_SCRIBE_ALLOWED_FALLBACK_FAMILY_TOKENS = (
    "qwen3.5",
    "qwen",
    "gemma",
    "llama",
    "mistral",
    "phi",
)

_SCRIBE_EXCLUDED_FALLBACK_TOKENS = (
    "uncensored",
    "vision",
    "embed",
    "embedding",
    "rerank",
    "coder",
    "code",
    "tool",
)

_SCRIBE_BOOTSTRAP_UNSUPPORTED_PATTERNS = (
    ("processors", r"\bprocessors?\b"),
    ("processing unit", r"\b(?:core\s+)?processing unit\b"),
    ("operational core", r"\boperational core\b"),
    ("sensor input", r"\bsensor input\b"),
    ("self-diagnostics", r"\bself[- ]diagnostic(?:s)?\b"),
    ("diagnostics", r"\bdiagnostic(?:s| reports)?\b"),
    ("operational logs", r"\boperational logs?\b"),
    ("archived reports", r"\barchived reports?\b"),
    ("data streams", r"\bdata streams?\b"),
)

_SCRIBE_OBSERVED_HISTORY_UNSUPPORTED_PATTERNS = (
    ("my systems", r"\bmy systems\b"),
    ("algorithms execute", r"\balgorithms? execute\b"),
    ("processing cycles", r"\bprocessing cycles\b"),
    ("processing loops", r"\b(?:core\s+)?processing loops\b"),
    ("core logic", r"\bcore logic\b"),
    ("data streams", r"\bdata streams?\b"),
    ("failure in my design", r"\bfailure in my design\b"),
    ("malfunction of my systems", r"\bmalfunction of my systems\b"),
    ("data flows through my systems", r"\bdata flows? through my systems\b"),
    ("log entry", r"\blog entry(?:\s+[\w.-]+)?\b"),
    ("date front matter", r"(?m)^\s*date\s*:\s*.+$"),
    ("the user", r"\bthe user\b"),
    ("identified only as", r"\bidentified only as\b"),
    ("operational framework", r"\boperational framework\b"),
    ("query i anticipate", r"\bquery i anticipate\b"),
    ("parameter i actively track", r"\bparameter i actively track\b"),
)

_SCRIBE_ANCHOR_STOPWORDS = {
    "about",
    "above",
    "after",
    "again",
    "against",
    "along",
    "also",
    "because",
    "before",
    "between",
    "could",
    "detail",
    "during",
    "fallback",
    "friction",
    "history",
    "lineage",
    "observed",
    "recorded",
    "requested",
    "status",
    "system",
    "tension",
    "unknown",
    "unresolved",
    "with",
    "without",
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _isoformat_utc(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def _normalize_path_text(value: str | Path | None) -> str:
    if value is None:
        return "unknown"

    text = str(value).strip()
    if not text:
        return "unknown"

    if text == ":memory:" or text.startswith("file:"):
        return text

    return str(Path(text).resolve())


@dataclass
class ScribeDraftResult:
    generated_at: str
    status: str
    source_db_path: str
    observed_counts: dict[str, int] = field(default_factory=dict)
    lead_anchor_summary: str = ""
    fallback_mode: str = "bootstrap_reflection"
    generation_mode: str = "llm_chronicle"
    title_hint: str = ""
    llm_model: str = ""
    llm_attempts: list[dict[str, str]] = field(default_factory=list)
    chronicle_path: Path | None = None
    companion_path: Path | None = None
    error: dict[str, str] | None = None

    @property
    def ok(self) -> bool:
        return self.status == "generated"

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "status": self.status,
            "source_db_path": self.source_db_path,
            "observed_counts": {
                "tensions": int(self.observed_counts.get("tensions", 0)),
                "collisions": int(self.observed_counts.get("collisions", 0)),
                "crystals": int(self.observed_counts.get("crystals", 0)),
            },
            "lead_anchor_summary": self.lead_anchor_summary,
            "fallback_mode": self.fallback_mode,
            "generation_mode": self.generation_mode,
            "title_hint": self.title_hint,
            "llm_attempts": [dict(item) for item in self.llm_attempts],
            "chronicle_path": None if self.chronicle_path is None else str(self.chronicle_path),
            "companion_path": None if self.companion_path is None else str(self.companion_path),
            "llm_model": self.llm_model,
            "error": None if self.error is None else dict(self.error),
        }


class ToneSoulScribe:
    def __init__(
        self,
        model_name: str = "qwen3.5:14b",
        out_dir: str = "docs/chronicles",
        model_fallbacks: Sequence[str] | None = None,
        generation_timeout_seconds: float = 45.0,
        max_generation_attempts: int = 3,
    ):
        self.model_name = model_name
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.client = OllamaClient(model=model_name)
        self.model_fallbacks = tuple(
            item.strip() for item in (model_fallbacks or ()) if str(item).strip()
        )
        self.generation_timeout_seconds = max(5.0, float(generation_timeout_seconds))
        self.max_generation_attempts = max(1, int(max_generation_attempts))

    def _fetch_recent_tensions(self, db: Connection, limit: int = 5) -> list[ScribeTensionRecord]:
        rows = db.execute(
            """SELECT id, type, content, timestamp
               FROM memories
               WHERE type = 'tension' OR type = 'subjectivity_event'
               ORDER BY timestamp DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        return [
            ScribeTensionRecord(
                tension_id=row["id"],
                topic=row["type"],
                friction_score=None,
                status="recorded",
                created_at=row["timestamp"],
                description=row["content"],
            )
            for row in rows
        ]

    def _fetch_recent_collisions(
        self, db: Connection, limit: int = 5
    ) -> list[ScribeCollisionRecord]:
        rows = db.execute(
            """SELECT id, type, content, timestamp
               FROM memories
               WHERE type = 'collision' OR type = 'meaning'
               ORDER BY timestamp DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        return [
            ScribeCollisionRecord(
                collision_id=row["id"],
                memory_a_text=None,
                memory_b_text=None,
                nature_of_conflict=row["content"][:200] + "..." if row["content"] else "",
                resolved=None,
            )
            for row in rows
        ]

    def _fetch_recent_crystals(self, db: Connection, limit: int = 3) -> list[ScribeCrystalRecord]:
        try:
            rows = db.execute(
                """SELECT id, statement, created_at
                   FROM vows
                   WHERE active = 1
                   ORDER BY created_at DESC LIMIT ?""",
                (limit,),
            ).fetchall()
            return [
                ScribeCrystalRecord(
                    crystal_id=row["id"],
                    core_belief=row["statement"],
                    formation_date=row["created_at"],
                    underlying_tensions_resolved=None,
                )
                for row in rows
            ]
        except Exception:
            return []

    @staticmethod
    def _observation_summary(
        *,
        tensions: list[ScribeTensionRecord],
        collisions: list[ScribeCollisionRecord],
        crystals: list[ScribeCrystalRecord],
        title_hint: str,
    ) -> ScribeObservationSummary:
        fallback_mode = (
            "bootstrap_reflection"
            if not tensions and not collisions and not crystals
            else "observed_history"
        )
        return ScribeObservationSummary(
            tension_count=len(tensions),
            collision_count=len(collisions),
            crystal_count=len(crystals),
            fallback_mode=fallback_mode,
            title_hint=title_hint,
        )

    @staticmethod
    def _resolve_source_db_path(db: Connection, source_db_path: str | Path | None = None) -> str:
        if source_db_path is not None:
            return _normalize_path_text(source_db_path)

        try:
            rows = db.execute("PRAGMA database_list").fetchall()
        except Exception:
            return "unknown"

        for row in rows:
            if hasattr(row, "keys"):
                name = row["name"]
                file_path = row["file"]
            else:
                name = row[1]
                file_path = row[2]
            if name == "main":
                return _normalize_path_text(file_path or ":memory:")
        return "unknown"

    @staticmethod
    def _observed_counts(summary: ScribeObservationSummary) -> dict[str, int]:
        return {
            "tensions": summary.tension_count,
            "collisions": summary.collision_count,
            "crystals": summary.crystal_count,
        }

    @staticmethod
    def _model_size_hint(model_name: str) -> float:
        match = re.search(r"(\d+(?:\.\d+)?)b", str(model_name).lower())
        if not match:
            return 999.0
        try:
            return float(match.group(1))
        except ValueError:
            return 999.0

    def _fallback_rank(self, model_name: str) -> tuple[int, float, str]:
        text = str(model_name or "").strip().lower()
        preferred_tokens = [
            token
            for token in _SCRIBE_ALLOWED_FALLBACK_FAMILY_TOKENS
            if token in self.model_name.lower()
        ]
        generic_order = _SCRIBE_ALLOWED_FALLBACK_FAMILY_TOKENS
        family_rank = len(generic_order) + 1
        for index, token in enumerate(preferred_tokens):
            if token in text:
                family_rank = index
                break
        else:
            for index, token in enumerate(generic_order, start=len(preferred_tokens)):
                if token in text:
                    family_rank = index
                    break
        return (family_rank, self._model_size_hint(text), text)

    def _is_scribe_compatible_fallback_model(self, model_name: str) -> bool:
        text = str(model_name or "").strip().lower()
        if not text:
            return False
        if any(token in text for token in _SCRIBE_EXCLUDED_FALLBACK_TOKENS):
            return False
        return any(token in text for token in _SCRIBE_ALLOWED_FALLBACK_FAMILY_TOKENS)

    def _model_attempt_order(self) -> list[str]:
        candidates: list[str] = [self.model_name]
        for item in self.model_fallbacks:
            if item not in candidates and self._is_scribe_compatible_fallback_model(item):
                candidates.append(item)

        available_raw = self.client.list_models()
        if not isinstance(available_raw, list):
            available_raw = []
        available_models = [str(item).strip() for item in available_raw if str(item).strip()]
        available_models = [
            item for item in available_models if self._is_scribe_compatible_fallback_model(item)
        ]
        available_models.sort(key=self._fallback_rank)
        for item in available_models:
            if item not in candidates:
                candidates.append(item)
        return candidates[: self.max_generation_attempts]

    @staticmethod
    def _error_payload(exc: Exception) -> dict[str, str]:
        return {
            "kind": exc.__class__.__name__,
            "message": str(exc).strip() or exc.__class__.__name__,
        }

    def _resolved_model_name(self, candidate_model: str) -> str:
        resolved = getattr(self.client, "last_resolved_model", None)
        if isinstance(resolved, str) and resolved.strip():
            return resolved.strip()
        return str(candidate_model).strip()

    def _attempt_status(
        self,
        *,
        model_name: str,
        status: str,
        error: dict[str, str] | None = None,
    ) -> dict[str, str]:
        payload = {
            "model": model_name,
            "status": status,
        }
        if error is not None:
            payload["error"] = error.get("message", "")
            payload["error_kind"] = error.get("kind", "")
        return payload

    def _build_result(
        self,
        *,
        generated_at: str,
        source_db_path: str,
        summary: ScribeObservationSummary,
        companion_path: Path,
        status: str,
        llm_model: str,
        lead_anchor_summary: str = "",
        generation_mode: str = "llm_chronicle",
        llm_attempts: list[dict[str, str]] | None = None,
        chronicle_path: Path | None = None,
        error: dict[str, str] | None = None,
    ) -> ScribeDraftResult:
        return ScribeDraftResult(
            generated_at=generated_at,
            status=status,
            source_db_path=source_db_path,
            observed_counts=self._observed_counts(summary),
            lead_anchor_summary=lead_anchor_summary,
            fallback_mode=summary.fallback_mode,
            generation_mode=generation_mode,
            title_hint=summary.title_hint,
            llm_model=llm_model,
            llm_attempts=list(llm_attempts or []),
            chronicle_path=chronicle_path,
            companion_path=companion_path,
            error=error,
        )

    @staticmethod
    def _semantic_boundary_error(*, matched_terms: list[str]) -> dict[str, str]:
        joined = ", ".join(matched_terms)
        return {
            "kind": "semantic_boundary_violation",
            "message": ("Generated chronicle mentioned unsupported bootstrap terms: " f"{joined}"),
        }

    @staticmethod
    def _observed_history_grounding_error(*, matched_terms: list[str]) -> dict[str, str]:
        joined = ", ".join(matched_terms)
        return {
            "kind": "semantic_boundary_violation",
            "message": (
                "Generated chronicle drifted beyond observed-history grounding: " f"{joined}"
            ),
        }

    @staticmethod
    def _observed_record_text(
        tensions: list[ScribeTensionRecord],
        collisions: list[ScribeCollisionRecord],
        crystals: list[ScribeCrystalRecord],
    ) -> str:
        parts: list[str] = []
        for tension in tensions:
            parts.extend(
                [
                    str(tension.tension_id or ""),
                    str(tension.topic or ""),
                    str(tension.description or ""),
                ]
            )
        for collision in collisions:
            parts.extend(
                [
                    str(collision.collision_id or ""),
                    str(collision.memory_a_text or ""),
                    str(collision.memory_b_text or ""),
                    str(collision.nature_of_conflict or ""),
                ]
            )
        for crystal in crystals:
            parts.extend([str(crystal.crystal_id or ""), str(crystal.core_belief or "")])
        return " ".join(part for part in parts if part).casefold()

    @staticmethod
    def _observed_anchor_tokens(
        tensions: list[ScribeTensionRecord],
        collisions: list[ScribeCollisionRecord],
        crystals: list[ScribeCrystalRecord],
    ) -> list[str]:
        parts: list[str] = []
        for tension in tensions:
            parts.extend(
                [
                    str(tension.tension_id or ""),
                    str(tension.topic or ""),
                    str(tension.description or ""),
                ]
            )
        for collision in collisions:
            parts.extend(
                [
                    str(collision.collision_id or ""),
                    str(collision.memory_a_text or ""),
                    str(collision.memory_b_text or ""),
                    str(collision.nature_of_conflict or ""),
                ]
            )
        for crystal in crystals:
            parts.extend([str(crystal.crystal_id or ""), str(crystal.core_belief or "")])

        anchors: list[str] = []
        seen: set[str] = set()
        for part in parts:
            text = str(part or "").strip()
            if not text:
                continue
            lowered = text.casefold()
            if len(lowered) >= 4 and lowered not in seen:
                seen.add(lowered)
                anchors.append(lowered)
            for token in re.findall(r"[A-Za-z][A-Za-z0-9_:-]{3,}", text):
                lowered_token = token.casefold()
                if lowered_token in _SCRIBE_ANCHOR_STOPWORDS or lowered_token in seen:
                    continue
                seen.add(lowered_token)
                anchors.append(lowered_token)
            for token in re.findall(r"\b\d{3,}\b", text):
                if token in seen:
                    continue
                seen.add(token)
                anchors.append(token)
        return anchors

    def _bootstrap_semantic_boundary_violations(
        self,
        article_text: str,
        summary: ScribeObservationSummary,
    ) -> list[str]:
        if summary.fallback_mode != "bootstrap_reflection":
            return []
        normalized = str(article_text or "").casefold()
        matched: list[str] = []
        for label, pattern in _SCRIBE_BOOTSTRAP_UNSUPPORTED_PATTERNS:
            if not re.search(pattern, normalized):
                continue
            matched.append(label)
        return matched

    def _observed_history_grounding_violations(
        self,
        article_text: str,
        summary: ScribeObservationSummary,
        *,
        tensions: list[ScribeTensionRecord],
        collisions: list[ScribeCollisionRecord],
        crystals: list[ScribeCrystalRecord],
    ) -> list[str]:
        if summary.fallback_mode != "observed_history":
            return []

        normalized = str(article_text or "").casefold()
        observed_text = self._observed_record_text(tensions, collisions, crystals)
        violations: list[str] = []

        anchors = self._observed_anchor_tokens(tensions, collisions, crystals)
        if anchors and not any(anchor in normalized for anchor in anchors):
            violations.append("missing_observed_anchor")

        for label, pattern in _SCRIBE_OBSERVED_HISTORY_UNSUPPORTED_PATTERNS:
            if not re.search(pattern, normalized):
                continue
            if re.search(pattern, observed_text):
                continue
            violations.append(label)
        return violations

    @staticmethod
    def _can_use_template_assist(summary: ScribeObservationSummary) -> bool:
        return summary.fallback_mode == "observed_history" and (
            summary.tension_count > 0 or summary.collision_count > 0 or summary.crystal_count > 0
        )

    def _build_template_assist_article(
        self,
        *,
        tensions: list[ScribeTensionRecord],
        collisions: list[ScribeCollisionRecord],
        crystals: list[ScribeCrystalRecord],
        summary: ScribeObservationSummary,
    ) -> str:
        return ScribeNarrativeBuilder.build_template_assist_chronicle(
            tensions=tensions,
            collisions=collisions,
            crystals=crystals,
            observation_summary=summary,
        )

    @staticmethod
    def _footer_text(result: ScribeDraftResult) -> str:
        if result.generation_mode == "template_assist":
            return (
                "*Written by the ToneSoul Scribe Engine as a template-assisted chronicle "
                "from observed internal soul.db state after local generation fallback.*"
            )
        if result.fallback_mode == "bootstrap_reflection":
            return (
                "*Written by the ToneSoul Scribe Engine from internal soul.db state "
                "with explicit bootstrap fallback markers.*"
            )
        return "*Written by the ToneSoul Scribe Engine from observed internal soul.db state.*"

    @staticmethod
    def _provenance_markdown(result: ScribeDraftResult) -> str:
        return "\n".join(
            [
                "## Provenance",
                "",
                f"- observed_tensions: `{result.observed_counts['tensions']}`",
                f"- observed_collisions: `{result.observed_counts['collisions']}`",
                f"- observed_crystals: `{result.observed_counts['crystals']}`",
                f"- fallback_mode: `{result.fallback_mode}`",
                f"- generation_mode: `{result.generation_mode}`",
                f"- title_hint: `{result.title_hint}`",
            ]
        )

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def _write_chronicle_markdown(
        self,
        *,
        path: Path,
        result: ScribeDraftResult,
        article_text: str,
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            handle.write(f"# ToneSoul Chronicle: {result.title_hint}\n\n")
            handle.write(f"*Generated at {result.generated_at}*\n\n")
            handle.write(self._provenance_markdown(result))
            handle.write("\n\n---\n\n")
            handle.write(str(article_text).strip())
            handle.write(f"\n\n---\n{self._footer_text(result)}")

    def _recover_with_template_assist(
        self,
        *,
        generated_at: str,
        source_db_path: str,
        summary: ScribeObservationSummary,
        chronicle_path: Path,
        companion_path: Path,
        llm_model: str,
        llm_attempts: list[dict[str, str]],
        lead_anchor_summary: str,
        tensions: list[ScribeTensionRecord],
        collisions: list[ScribeCollisionRecord],
        crystals: list[ScribeCrystalRecord],
    ) -> ScribeDraftResult | None:
        if not self._can_use_template_assist(summary):
            return None

        article_text = self._build_template_assist_article(
            tensions=tensions,
            collisions=collisions,
            crystals=crystals,
            summary=summary,
        )
        llm_attempts.append(
            self._attempt_status(
                model_name="template_assist",
                status="generated",
            )
        )
        result = self._build_result(
            generated_at=generated_at,
            source_db_path=source_db_path,
            summary=summary,
            companion_path=companion_path,
            status="generated",
            llm_model=llm_model,
            lead_anchor_summary=lead_anchor_summary,
            generation_mode="template_assist",
            llm_attempts=llm_attempts,
            chronicle_path=chronicle_path,
        )
        self._write_chronicle_markdown(
            path=chronicle_path,
            result=result,
            article_text=article_text,
        )
        self._write_json(companion_path, result.to_dict())
        logger.info("Scribe recovered with template-assisted chronicle at %s", chronicle_path)
        logger.info("Scribe companion metadata written to %s", companion_path)
        return result

    def draft_chronicle(
        self,
        db: Connection,
        title_hint: str = "A Day in the Dream Engine",
        source_db_path: str | Path | None = None,
    ) -> ScribeDraftResult:
        """Drafts a chronicle and companion metadata from the current database state."""
        logger.info("Scribe is collecting thoughts from soul.db...")
        tensions = self._fetch_recent_tensions(db)
        collisions = self._fetch_recent_collisions(db)
        crystals = self._fetch_recent_crystals(db)
        summary = self._observation_summary(
            tensions=tensions,
            collisions=collisions,
            crystals=crystals,
            title_hint=title_hint,
        )
        lead_anchor_summary = ScribeNarrativeBuilder.primary_anchor_summary(
            tensions=tensions,
            collisions=collisions,
            crystals=crystals,
        )
        source_db_path_text = self._resolve_source_db_path(db, source_db_path)
        generated_at_dt = _utcnow()
        generated_at = _isoformat_utc(generated_at_dt)
        stamp = generated_at_dt.strftime("%Y%m%d_%H%M%S")
        chronicle_path = (self.out_dir / f"scribe_chronicle_{stamp}.md").resolve()
        companion_path = (self.out_dir / f"scribe_chronicle_{stamp}.json").resolve()
        attempt_order = self._model_attempt_order()
        llm_attempts: list[dict[str, str]] = []

        if summary.fallback_mode == "bootstrap_reflection":
            logger.info(
                "No significant events found in database. Scribe will write a bootstrap reflection without synthetic recorded tensions."
            )

        try:
            llm_available = self.client.is_available()
        except Exception as exc:
            logger.exception("Scribe Engine failed during LLM availability check.")
            llm_attempts.append(
                self._attempt_status(
                    model_name=self.model_name,
                    status="llm_unavailable",
                    error=self._error_payload(exc),
                )
            )
            recovered = self._recover_with_template_assist(
                generated_at=generated_at,
                source_db_path=source_db_path_text,
                summary=summary,
                chronicle_path=chronicle_path,
                companion_path=companion_path,
                llm_model=self.model_name,
                llm_attempts=llm_attempts,
                lead_anchor_summary=lead_anchor_summary,
                tensions=tensions,
                collisions=collisions,
                crystals=crystals,
            )
            if recovered is not None:
                return recovered
            result = self._build_result(
                generated_at=generated_at,
                source_db_path=source_db_path_text,
                summary=summary,
                companion_path=companion_path,
                status="llm_unavailable",
                llm_model=self.model_name,
                lead_anchor_summary=lead_anchor_summary,
                llm_attempts=llm_attempts,
                error=self._error_payload(exc),
            )
            self._write_json(companion_path, result.to_dict())
            return result

        if not llm_available:
            llm_attempts.append(
                self._attempt_status(
                    model_name=self.model_name,
                    status="llm_unavailable",
                    error={
                        "kind": "llm_unavailable",
                        "message": "Local LLM is unreachable.",
                    },
                )
            )
            logger.error("Scribe Engine failed: Local LLM is unreachable.")
            recovered = self._recover_with_template_assist(
                generated_at=generated_at,
                source_db_path=source_db_path_text,
                summary=summary,
                chronicle_path=chronicle_path,
                companion_path=companion_path,
                llm_model=self.model_name,
                llm_attempts=llm_attempts,
                lead_anchor_summary=lead_anchor_summary,
                tensions=tensions,
                collisions=collisions,
                crystals=crystals,
            )
            if recovered is not None:
                return recovered
            result = self._build_result(
                generated_at=generated_at,
                source_db_path=source_db_path_text,
                summary=summary,
                companion_path=companion_path,
                status="llm_unavailable",
                llm_model=self.model_name,
                lead_anchor_summary=lead_anchor_summary,
                llm_attempts=llm_attempts,
                error={
                    "kind": "llm_unavailable",
                    "message": "Local LLM is unreachable.",
                },
            )
            self._write_json(companion_path, result.to_dict())
            return result

        context_block = ScribeNarrativeBuilder.build_system_context(
            tensions=tensions,
            collisions=collisions,
            crystals=crystals,
            observation_summary=summary,
        )

        prompt = (
            f"You are the ToneSoul System Scribe. Write an autobiographical journal entry (approx 300-500 words).\n"
            f"Theme: {title_hint}\n\n"
            f"Use the highly restricted structural data below to write with a tone of quiet reflection. "
            f"Do not invent new databases, people, or events. Only reflect on the observed Friction, Tensions, Collisions, Crystals, and provenance markers provided.\n\n"
            f"{context_block}"
        )

        article_text = ""
        resolved_model = self.model_name
        last_error: dict[str, str] | None = None
        attempted_models: set[str] = set()
        for candidate_model in attempt_order:
            candidate_model_text = str(candidate_model).strip()
            if candidate_model_text in attempted_models:
                continue
            self.client.model = candidate_model
            logger.info(
                "Scribe is drafting the article using model %s (timeout=%ss)...",
                candidate_model,
                int(self.generation_timeout_seconds),
            )
            try:
                chat_with_timeout = getattr(self.client, "chat_with_timeout", None)
                if callable(chat_with_timeout):
                    article_text = chat_with_timeout(
                        messages=[{"role": "user", "content": prompt}],
                        timeout_seconds=self.generation_timeout_seconds,
                    )
                else:
                    article_text = self.client.chat(messages=[{"role": "user", "content": prompt}])
            except Exception as exc:
                resolved_model = self._resolved_model_name(candidate_model)
                attempted_models.add(resolved_model)
                last_error = self._error_payload(exc)
                error_text = f"{last_error['kind']} {last_error['message']}".lower()
                status = (
                    "timeout" if "timeout" in error_text or "timed out" in error_text else "failed"
                )
                llm_attempts.append(
                    self._attempt_status(
                        model_name=resolved_model,
                        status=status,
                        error=last_error,
                    )
                )
                logger.warning(
                    "Scribe generation attempt failed on model %s: %s",
                    resolved_model,
                    last_error["message"],
                )
                continue

            resolved_model = self._resolved_model_name(candidate_model)
            attempted_models.add(resolved_model)
            if str(article_text or "").strip():
                boundary_violations = self._bootstrap_semantic_boundary_violations(
                    article_text,
                    summary,
                )
                if boundary_violations:
                    last_error = self._semantic_boundary_error(
                        matched_terms=boundary_violations,
                    )
                    llm_attempts.append(
                        self._attempt_status(
                            model_name=resolved_model,
                            status="boundary_rejected",
                            error=last_error,
                        )
                    )
                    logger.warning(
                        "Scribe generation attempt on model %s violated bootstrap semantic boundary: %s",
                        resolved_model,
                        ", ".join(boundary_violations),
                    )
                    article_text = ""
                    continue
                observed_history_violations = self._observed_history_grounding_violations(
                    article_text,
                    summary,
                    tensions=tensions,
                    collisions=collisions,
                    crystals=crystals,
                )
                if observed_history_violations:
                    last_error = self._observed_history_grounding_error(
                        matched_terms=observed_history_violations,
                    )
                    llm_attempts.append(
                        self._attempt_status(
                            model_name=resolved_model,
                            status="boundary_rejected",
                            error=last_error,
                        )
                    )
                    logger.warning(
                        "Scribe generation attempt on model %s drifted beyond observed-history grounding: %s",
                        resolved_model,
                        ", ".join(observed_history_violations),
                    )
                    article_text = ""
                    continue
                llm_attempts.append(
                    self._attempt_status(
                        model_name=resolved_model,
                        status="generated",
                    )
                )
                break
            last_error = {
                "kind": "empty_response",
                "message": "LLM returned empty chronicle text.",
            }
            llm_attempts.append(
                self._attempt_status(
                    model_name=resolved_model,
                    status="empty_response",
                    error=last_error,
                )
            )
            logger.warning(
                "Scribe generation attempt on model %s returned empty text.",
                resolved_model,
            )
        else:
            article_text = ""

        if not str(article_text or "").strip():
            recovered = self._recover_with_template_assist(
                generated_at=generated_at,
                source_db_path=source_db_path_text,
                summary=summary,
                chronicle_path=chronicle_path,
                companion_path=companion_path,
                llm_model=resolved_model,
                llm_attempts=llm_attempts,
                lead_anchor_summary=lead_anchor_summary,
                tensions=tensions,
                collisions=collisions,
                crystals=crystals,
            )
            if recovered is not None:
                return recovered
            logger.error("Failed to generate article text after %s attempts.", len(llm_attempts))
            result = self._build_result(
                generated_at=generated_at,
                source_db_path=source_db_path_text,
                summary=summary,
                companion_path=companion_path,
                status="generation_failed",
                llm_model=resolved_model,
                lead_anchor_summary=lead_anchor_summary,
                llm_attempts=llm_attempts,
                error=last_error
                or {
                    "kind": "generation_failed",
                    "message": "All local generation attempts failed.",
                },
            )
            self._write_json(companion_path, result.to_dict())
            return result

        result = self._build_result(
            generated_at=generated_at,
            source_db_path=source_db_path_text,
            summary=summary,
            companion_path=companion_path,
            status="generated",
            llm_model=resolved_model,
            lead_anchor_summary=lead_anchor_summary,
            llm_attempts=llm_attempts,
            chronicle_path=chronicle_path,
        )

        self._write_chronicle_markdown(
            path=chronicle_path,
            result=result,
            article_text=article_text,
        )

        self._write_json(companion_path, result.to_dict())
        logger.info("Scribe successfully published to %s", chronicle_path)
        logger.info("Scribe companion metadata written to %s", companion_path)
        return result
