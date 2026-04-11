from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, Iterable, List, Optional, Set

from tonesoul.schemas import MemorySubjectivityPayload, SubjectivityLayer

if TYPE_CHECKING:
    from tonesoul.perception.stimulus import EnvironmentStimulus

from .soul_db import MemoryLayer, MemoryRecord, MemorySource, SoulDB, SqliteSoulDB

ENVIRONMENT_STIMULUS_TYPE = "environment_stimulus"
ENVIRONMENT_STIMULUS_SOURCE = MemorySource.CUSTOM
ENVIRONMENT_STIMULUS_LAYER = MemoryLayer.WORKING.value
_REVIEWED_SUBJECTIVITY_STATES = {
    "approved",
    "governance_reviewed",
    "human_reviewed",
    "reviewed",
}


def _has_evidence(payload: Dict[str, object]) -> bool:
    evidence_ids = payload.get("evidence_ids")
    if isinstance(evidence_ids, list) and any(str(item).strip() for item in evidence_ids):
        return True

    evidence = payload.get("evidence")
    if isinstance(evidence, list) and any(str(item).strip() for item in evidence):
        return True

    transcript = payload.get("transcript")
    if not isinstance(transcript, dict):
        return False

    contract = transcript.get("multi_agent_contract")
    if isinstance(contract, dict):
        records = contract.get("records")
        if isinstance(records, list):
            for record in records:
                if not isinstance(record, dict):
                    continue
                record_evidence = record.get("evidence")
                if isinstance(record_evidence, list) and any(
                    str(item).strip() for item in record_evidence
                ):
                    return True
    return False


def _has_provenance(payload: Dict[str, object]) -> bool:
    for key in ("intent_id", "genesis", "provenance", "isnad"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return True
        if isinstance(value, (list, dict)) and value:
            return True

    transcript = payload.get("transcript")
    if not isinstance(transcript, dict):
        return False

    for key in ("intent_id", "genesis", "provenance", "isnad"):
        value = transcript.get(key)
        if isinstance(value, str) and value.strip():
            return True
        if isinstance(value, (list, dict)) and value:
            return True
    return False


def _intentional_forgetting_gate(payload: Dict[str, object]) -> tuple[bool, List[str]]:
    """Filter out content not worth remembering.

    Inspired by Harness Engineering's "net" metaphor: intentional gaps
    let unnecessary information flow through, preventing pressure buildup.

    Returns (should_keep, reasons_to_forget).
    """
    # Structured payloads with explicit type bypass the forgetting gate —
    # handoffs, crystallizations, and audit records are always worth keeping.
    payload_type = str(payload.get("type") or "").strip().lower()
    if payload_type in {"handoff", "crystal", "audit", "governance_retro"}:
        return True, []

    reasons: List[str] = []

    # Empty or trivially short content
    content = str(payload.get("content") or payload.get("text") or payload.get("summary") or "")
    if len(content.strip()) < 10:
        reasons.append("content_too_short")

    # Duplicate signal: if content_hash matches a known ephemeral pattern
    tags = payload.get("tags")
    if isinstance(tags, list):
        tag_set = {str(t).strip().lower() for t in tags}
        ephemeral_markers = {"ephemeral", "transient", "scratch", "temp", "debug"}
        if tag_set & ephemeral_markers:
            reasons.append("ephemeral_tag")

    # Observation-only with no actionable content
    observation_mode = str(payload.get("observation_mode") or "").strip().lower()
    if observation_mode == "passive_noise":
        reasons.append("passive_noise")

    return len(reasons) == 0, reasons


def _promotion_gate(payload: Dict[str, object]) -> tuple[bool, List[str]]:
    reasons: List[str] = []
    if not _has_evidence(payload):
        reasons.append("missing_evidence")
    if not _has_provenance(payload):
        reasons.append("missing_provenance")
    subjectivity_layer = str(payload.get("subjectivity_layer") or "").strip().lower()
    if subjectivity_layer in {
        SubjectivityLayer.VOW.value,
        SubjectivityLayer.IDENTITY.value,
    } and not _has_strong_promotion_gate(payload):
        reasons.append("subjectivity_requires_review")
    return len(reasons) == 0, reasons


def _has_strong_promotion_gate(payload: Dict[str, object]) -> bool:
    gate = payload.get("promotion_gate")
    review_basis = ""
    if isinstance(gate, str):
        return gate.strip().lower() in _REVIEWED_SUBJECTIVITY_STATES
    if not isinstance(gate, dict):
        return False

    review_basis = str(gate.get("review_basis") or "").strip()

    for key in ("status", "decision", "mode"):
        value = gate.get(key)
        if (
            isinstance(value, str)
            and value.strip().lower() in _REVIEWED_SUBJECTIVITY_STATES
            and review_basis
        ):
            return True

    for key in ("reviewed_by", "approved_by"):
        value = gate.get(key)
        if isinstance(value, str) and value.strip() and review_basis:
            return True
        if isinstance(value, list) and any(str(item).strip() for item in value) and review_basis:
            return True

    return bool(review_basis and (gate.get("human_review") or gate.get("governance_review")))


class MemoryWriteRejectedError(ValueError):
    def __init__(self, reasons: Iterable[str]) -> None:
        self.reasons = [str(reason).strip() for reason in reasons if str(reason).strip()]
        message = ", ".join(self.reasons) or "memory write rejected"
        super().__init__(message)


@dataclass
class MemoryWriteResult:
    written: int = 0
    skipped: int = 0
    rejected: int = 0
    record_ids: List[str] = field(default_factory=list)
    reject_reasons: List[str] = field(default_factory=list)


class MemoryWriteGateway:
    """
    Canonical durable writer for non-conversational memory inputs.

    Environment perception should persist into `soul.db` first. Audit mirrors
    such as `self_journal.jsonl` remain separate concerns and are intentionally
    not handled here.
    """

    def __init__(self, soul_db: Optional[SoulDB] = None) -> None:
        self.soul_db = soul_db or SqliteSoulDB()

    def write_payload(self, source: MemorySource, payload: Dict[str, object]) -> str:
        if not isinstance(payload, dict):
            raise TypeError("write_payload expects a dict payload")

        normalized_payload = dict(payload)
        normalized_payload = self._normalize_subjectivity_payload(normalized_payload)
        provenance = self._extract_provenance_payload(normalized_payload)
        if provenance is not None and "provenance" not in normalized_payload:
            normalized_payload["provenance"] = provenance

        # Intentional forgetting — let unworthy content flow through the net
        keep, forget_reasons = _intentional_forgetting_gate(normalized_payload)
        if not keep:
            raise MemoryWriteRejectedError(forget_reasons)

        gate_ok, reasons = _promotion_gate(normalized_payload)
        if not gate_ok:
            raise MemoryWriteRejectedError(reasons)

        return self._append_payload(source, normalized_payload, provenance=provenance)

    def write_environment_stimuli(
        self,
        stimuli: Iterable[EnvironmentStimulus],
        *,
        dedupe: bool = True,
    ) -> MemoryWriteResult:
        result = MemoryWriteResult()
        seen_hashes = self._existing_environment_hashes() if dedupe else set()

        for stimulus in stimuli:
            if not hasattr(stimulus, "to_memory_payload") or not hasattr(stimulus, "source_url"):
                raise TypeError("write_environment_stimuli expects EnvironmentStimulus values")

            content_hash = self._resolve_content_hash(stimulus)
            if dedupe and content_hash in seen_hashes:
                result.skipped += 1
                continue

            payload = self._build_environment_payload(stimulus, content_hash=content_hash)
            try:
                record_id = self.write_payload(ENVIRONMENT_STIMULUS_SOURCE, payload)
            except MemoryWriteRejectedError as exc:
                result.rejected += 1
                result.reject_reasons.extend(exc.reasons)
                continue
            result.written += 1
            result.record_ids.append(record_id)
            if dedupe:
                seen_hashes.add(content_hash)

        return result

    def stream_environment_stimuli(self, *, limit: Optional[int] = None) -> List[MemoryRecord]:
        records = [
            record
            for record in self.soul_db.stream(ENVIRONMENT_STIMULUS_SOURCE, limit=None)
            if self._is_environment_record(record)
        ]
        if limit is None:
            return records
        resolved_limit = int(limit)
        if resolved_limit <= 0:
            return []
        return records[-resolved_limit:]

    def _existing_environment_hashes(self) -> Set[str]:
        hashes: Set[str] = set()
        for record in self.stream_environment_stimuli():
            content_hash = str(record.payload.get("content_hash") or "").strip().lower()
            if content_hash:
                hashes.add(content_hash)
        return hashes

    def _build_environment_payload(
        self,
        stimulus: EnvironmentStimulus,
        *,
        content_hash: str,
    ) -> dict[str, object]:
        payload = stimulus.to_memory_payload()
        observation_mode = str(payload.get("observation_mode") or "remote_feed").strip().lower()
        payload["content_hash"] = content_hash
        payload["observation_mode"] = observation_mode
        payload["timestamp"] = str(payload.get("timestamp") or stimulus.ingested_at)
        payload["layer"] = str(payload.get("layer") or ENVIRONMENT_STIMULUS_LAYER)
        payload["tags"] = self._merge_tags(
            payload.get("tags"),
            observation_mode=observation_mode,
        )
        payload["evidence"] = self._build_environment_evidence(stimulus)
        payload["provenance"] = {
            "kind": "environment_stimulus",
            "source_url": stimulus.source_url,
            "ingested_at": stimulus.ingested_at,
            "content_hash": content_hash,
            "observation_mode": observation_mode,
        }
        return payload

    def _is_environment_record(self, record: MemoryRecord) -> bool:
        payload = record.payload if isinstance(record.payload, dict) else {}
        return str(payload.get("type") or "").strip() == ENVIRONMENT_STIMULUS_TYPE

    def _append_payload(
        self,
        source: MemorySource,
        payload: Dict[str, object],
        *,
        provenance: object,
    ) -> str:
        try:
            return self.soul_db.append(source, payload, provenance=provenance)
        except TypeError:
            return self.soul_db.append(source, payload)

    def _build_environment_evidence(self, stimulus: EnvironmentStimulus) -> List[str]:
        evidence: List[str] = []
        for candidate in (
            stimulus.raw_excerpt,
            stimulus.summary,
            stimulus.source_url,
        ):
            text = str(candidate or "").strip()
            if not text:
                continue
            evidence.append(text[:500])
        return evidence

    def _extract_provenance_payload(self, payload: Dict[str, object]) -> object:
        provenance = payload.get("provenance")
        if isinstance(provenance, str) and provenance.strip():
            return provenance.strip()
        if isinstance(provenance, (list, dict)) and provenance:
            return provenance

        for key in ("intent_id", "genesis", "isnad"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return {key: value.strip()}
            if isinstance(value, (list, dict)) and value:
                return {key: value}

        transcript = payload.get("transcript")
        if isinstance(transcript, dict):
            transcript_provenance = transcript.get("provenance")
            if isinstance(transcript_provenance, str) and transcript_provenance.strip():
                return transcript_provenance.strip()
            if isinstance(transcript_provenance, (list, dict)) and transcript_provenance:
                return transcript_provenance
            for key in ("intent_id", "genesis", "isnad"):
                value = transcript.get(key)
                if isinstance(value, str) and value.strip():
                    return {key: value.strip()}
                if isinstance(value, (list, dict)) and value:
                    return {key: value}

        return None

    def _resolve_content_hash(self, stimulus: EnvironmentStimulus) -> str:
        candidate = str(stimulus.content_hash or "").strip().lower()
        if candidate:
            return candidate
        digest_input = "\n".join(
            [
                str(stimulus.source_url or ""),
                str(stimulus.topic or ""),
                str(stimulus.summary or ""),
                str(stimulus.raw_excerpt or ""),
            ]
        )
        return hashlib.sha256(digest_input.encode("utf-8")).hexdigest()[:16]

    def _merge_tags(self, value: object, *, observation_mode: str = "remote_feed") -> List[str]:
        merged: List[str] = []
        seen: Set[str] = set()

        for item in value if isinstance(value, list) else []:
            text = str(item).strip()
            if not text:
                continue
            marker = text.lower()
            if marker in seen:
                continue
            seen.add(marker)
            merged.append(text)

        for tag in ("environment", "perception"):
            if tag in seen:
                continue
            seen.add(tag)
            merged.append(tag)

        observation_tag = f"observation:{str(observation_mode or 'remote_feed').strip().lower()}"
        if observation_tag not in seen:
            seen.add(observation_tag)
            merged.append(observation_tag)

        return merged

    def _normalize_subjectivity_payload(self, payload: Dict[str, object]) -> Dict[str, object]:
        try:
            normalized_fields = MemorySubjectivityPayload.normalize_fields(payload)
        except Exception as exc:
            reasons: List[str] = []
            errors = getattr(exc, "errors", None)
            if callable(errors):
                for error in errors():
                    loc = error.get("loc") or []
                    field_name = str(loc[0]) if loc else "subjectivity_payload"
                    if field_name == "subjectivity_layer":
                        reasons.append("invalid_subjectivity_layer")
                    elif field_name == "confidence":
                        reasons.append("invalid_subjectivity_confidence")
                    elif field_name == "promotion_gate":
                        reasons.append("invalid_promotion_gate")
                    elif field_name == "decay_policy":
                        reasons.append("invalid_decay_policy")
                    elif field_name == "source_record_ids":
                        reasons.append("invalid_source_record_ids")
                    else:
                        reasons.append(f"invalid_{field_name}")
            raise MemoryWriteRejectedError(reasons or ["invalid_subjectivity_payload"]) from exc

        if not normalized_fields:
            return payload

        normalized_payload = dict(payload)
        normalized_payload.update(normalized_fields)
        return normalized_payload
