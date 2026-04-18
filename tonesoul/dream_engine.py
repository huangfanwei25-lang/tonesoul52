"""Dream engine: offline crystallization of memory into subjectivity layers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Protocol, Sequence
from uuid import uuid4

from tonesoul.governance.kernel import GovernanceKernel
from tonesoul.llm.router import LLMRouter
from tonesoul.memory.crystallizer import Crystal, MemoryCrystallizer
from tonesoul.memory.soul_db import MemoryLayer, MemorySource, SoulDB, SqliteSoulDB
from tonesoul.memory.subjectivity_reporting import list_subjectivity_records
from tonesoul.memory.write_gateway import MemoryWriteGateway, MemoryWriteRejectedError
from tonesoul.schemas import SubjectivityLayer
from tonesoul.stale_rule_verifier import StaleRuleVerificationTaskBatch

__ts_layer__ = "evolution"
__ts_purpose__ = "Offline dream cycle: crystallize memory and update subjectivity layers between waking sessions."


class LLMRouterLike(Protocol):
    active_backend: Optional[str]
    last_metrics: Any

    def get_client(self) -> Any: ...
    def inference_check(self, timeout_seconds: float = 10.0) -> Dict[str, Any]: ...


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_signature_part(value: object) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _parse_iso_sort_key(value: object) -> datetime:
    text = str(value or "").strip()
    if not text:
        return datetime.min.replace(tzinfo=timezone.utc)
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


@dataclass
class DreamCollision:
    stimulus_record_id: str
    topic: str
    source_url: str
    priority_score: float
    relevance_score: float
    novelty_score: float
    resonance_score: float
    friction_score: Optional[float]
    should_convene_council: bool
    council_reason: str
    llm_backend: Optional[str]
    reflection: str
    reflection_generated: bool
    related_memories: List[Dict[str, object]] = field(default_factory=list)
    crystal_rules: List[str] = field(default_factory=list)
    resistance: Dict[str, object] = field(default_factory=dict)
    observability: Dict[str, object] = field(default_factory=dict)
    persisted_record_id: Optional[str] = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "stimulus_record_id": self.stimulus_record_id,
            "topic": self.topic,
            "source_url": self.source_url,
            "priority_score": round(float(self.priority_score), 4),
            "relevance_score": round(float(self.relevance_score), 4),
            "novelty_score": round(float(self.novelty_score), 4),
            "resonance_score": round(float(self.resonance_score), 4),
            "friction_score": (
                round(float(self.friction_score), 4) if self.friction_score is not None else None
            ),
            "should_convene_council": bool(self.should_convene_council),
            "council_reason": self.council_reason,
            "llm_backend": self.llm_backend,
            "reflection": self.reflection,
            "reflection_generated": bool(self.reflection_generated),
            "related_memories": list(self.related_memories),
            "crystal_rules": list(self.crystal_rules),
            "resistance": dict(self.resistance),
            "observability": dict(self.observability),
            "persisted_record_id": self.persisted_record_id,
        }


@dataclass
class DreamCycleResult:
    generated_at: str
    dream_cycle_id: str
    stimuli_considered: int
    stimuli_selected: int
    llm_backend: Optional[str]
    llm_preflight: Dict[str, object] = field(default_factory=dict)
    collisions: List[DreamCollision] = field(default_factory=list)
    write_gateway: Dict[str, object] = field(default_factory=dict)
    stale_rule_tasks_generated: int = 0
    """Number of verification tasks generated from stale rules in this cycle."""

    verification_applied: Dict[str, int] = field(default_factory=dict)
    """Results of applying completed verification tasks: {re_confirmed, retired, skipped}."""

    def to_dict(self) -> Dict[str, object]:
        return {
            "generated_at": self.generated_at,
            "dream_cycle_id": self.dream_cycle_id,
            "stimuli_considered": int(self.stimuli_considered),
            "stimuli_selected": int(self.stimuli_selected),
            "llm_backend": self.llm_backend,
            "llm_preflight": dict(self.llm_preflight),
            "collisions": [collision.to_dict() for collision in self.collisions],
            "write_gateway": dict(self.write_gateway),
            "stale_rule_tasks_generated": int(self.stale_rule_tasks_generated),
            "verification_applied": dict(self.verification_applied),
        }


class DreamEngine:
    """
    Offline autonomous collision engine for persisted environmental stimuli.

    Dream Engine does not replace `UnifiedPipeline`. It consumes persisted
    environment stimuli, collides them with durable rules and related memory,
    then asks `GovernanceKernel` for governance recommendations.
    """

    def __init__(
        self,
        *,
        soul_db: Optional[SoulDB] = None,
        write_gateway: Optional[MemoryWriteGateway] = None,
        governance_kernel: Optional[GovernanceKernel] = None,
        router: Optional[LLMRouterLike] = None,
        crystallizer: Optional[MemoryCrystallizer] = None,
    ) -> None:
        self.soul_db = soul_db or SqliteSoulDB()
        self.write_gateway = write_gateway or MemoryWriteGateway(self.soul_db)
        self.governance_kernel = governance_kernel or GovernanceKernel()
        self.router = router or LLMRouter(
            backend_resolver=self.governance_kernel.resolve_llm_backend,
        )
        self.crystallizer = crystallizer or MemoryCrystallizer()

    def run_cycle(
        self,
        *,
        limit: int = 3,
        min_priority: float = 0.35,
        related_limit: int = 5,
        crystal_count: int = 5,
        generate_reflection: bool = True,
        require_inference_ready: bool = False,
        inference_timeout_seconds: float = 10.0,
        generate_verification_tasks: bool = True,
        max_verification_tasks: int = 5,
    ) -> DreamCycleResult:
        generated_at = _utcnow_iso()
        dream_cycle_id = self._build_dream_cycle_id()
        selected = self.select_stimuli(limit=limit, min_priority=min_priority)
        client = None
        backend = None
        llm_preflight = self._resolve_llm_preflight(
            generate_reflection=generate_reflection,
            require_inference_ready=require_inference_ready,
            inference_timeout_seconds=inference_timeout_seconds,
        )
        if isinstance(llm_preflight.get("backend"), str) and str(llm_preflight["backend"]).strip():
            backend = str(llm_preflight["backend"]).strip()
        if generate_reflection:
            if require_inference_ready and not bool(llm_preflight.get("ok", False)):
                generate_reflection = False
            else:
                client = self.router.get_client()
                if backend is None:
                    backend = getattr(self.router, "active_backend", None)

        crystals = self.crystallizer.top_crystals(n=crystal_count)

        # Phase 543: Apply completed verification results back to Crystallizer
        verification_applied = {"re_confirmed": 0, "retired": 0, "skipped": 0}
        if generate_verification_tasks:
            try:
                apply_batch = StaleRuleVerificationTaskBatch()
                verification_applied = apply_batch.apply_verification_results(
                    self.crystallizer,
                )
            except Exception:
                pass

        # Phase 542: Generate verification tasks from stale rules
        stale_task_count = 0
        if generate_verification_tasks:
            try:
                batch = StaleRuleVerificationTaskBatch()
                verification_tasks = batch.generate_from_crystals(
                    crystals,
                    max_tasks=max(0, int(max_verification_tasks)),
                )
                stale_task_count = len(verification_tasks)
                batch.persist_tasks(verification_tasks)
            except Exception as e:
                # Graceful degradation: log but continue
                print(f"Warning: Stale rule verification generation failed: {e}")
                stale_task_count = 0

        collisions = [
            self._build_collision(
                record,
                crystals=crystals,
                related_limit=related_limit,
                client=client,
                llm_backend=backend,
                generate_reflection=generate_reflection,
            )
            for record in selected
        ]
        write_gateway = self._persist_collisions(
            collisions,
            generated_at=generated_at,
            dream_cycle_id=dream_cycle_id,
        )

        all_records = self.write_gateway.stream_environment_stimuli()
        return DreamCycleResult(
            generated_at=generated_at,
            dream_cycle_id=dream_cycle_id,
            stimuli_considered=len(all_records),
            stimuli_selected=len(collisions),
            llm_backend=backend,
            llm_preflight=llm_preflight,
            collisions=collisions,
            write_gateway=write_gateway,
            stale_rule_tasks_generated=stale_task_count,
            verification_applied=verification_applied,
        )

    @staticmethod
    def _build_dream_cycle_id() -> str:
        return f"dream-cycle-{uuid4().hex[:12]}"

    def _persist_collisions(
        self,
        collisions: Sequence[DreamCollision],
        *,
        generated_at: str,
        dream_cycle_id: str,
    ) -> Dict[str, object]:
        written = 0
        skipped = 0
        rejected = 0
        record_ids: List[str] = []
        skip_reasons: List[str] = []
        reject_reasons: List[str] = []
        existing_signatures = self._active_unresolved_collision_signatures()
        rejected_signatures = self._historical_rejected_collision_signatures()

        for collision in collisions:
            payload = self._build_collision_payload(
                collision,
                generated_at=generated_at,
                dream_cycle_id=dream_cycle_id,
            )
            signature = self._collision_signature(
                topic=payload.get("topic"),
                source_url=payload.get("source_url"),
                stimulus_record_id=payload.get("stimulus_record_id"),
                source_record_ids=payload.get("source_record_ids"),
            )
            rejected_signature = self._reviewed_collision_signature(
                topic=payload.get("topic"),
                source_url=payload.get("source_url"),
                stimulus_record_id=payload.get("stimulus_record_id"),
                source_record_ids=payload.get("source_record_ids"),
            )
            if signature and signature in existing_signatures:
                skipped += 1
                skip_reasons.append("active_unresolved_signature")
                collision.observability = dict(collision.observability)
                collision.observability["write_status"] = "skipped"
                collision.observability["write_skip_reason"] = "active_unresolved_signature"
                continue
            if rejected_signature and rejected_signature in rejected_signatures:
                skipped += 1
                skip_reasons.append("prior_rejected_signature")
                collision.observability = dict(collision.observability)
                collision.observability["write_status"] = "skipped"
                collision.observability["write_skip_reason"] = "prior_rejected_signature"
                continue
            try:
                record_id = self.write_gateway.write_payload(MemorySource.CUSTOM, payload)
            except MemoryWriteRejectedError as exc:
                rejected += 1
                reject_reasons.extend(exc.reasons)
                continue
            written += 1
            record_ids.append(record_id)
            collision.persisted_record_id = record_id
            if signature:
                existing_signatures.add(signature)

        return {
            "written": written,
            "skipped": skipped,
            "rejected": rejected,
            "record_ids": record_ids,
            "skip_reasons": skip_reasons,
            "reject_reasons": reject_reasons,
        }

    def _build_collision_payload(
        self,
        collision: DreamCollision,
        *,
        generated_at: str,
        dream_cycle_id: str,
    ) -> Dict[str, object]:
        evidence = [
            text
            for text in (
                collision.reflection,
                collision.topic,
                collision.source_url,
                collision.council_reason,
            )
            if str(text or "").strip()
        ]
        return {
            "type": "dream_collision",
            "timestamp": generated_at,
            "layer": MemoryLayer.WORKING.value,
            "subjectivity_layer": SubjectivityLayer.TENSION.value,
            "title": (
                f"Dream collision: {collision.topic}"
                if str(collision.topic).strip()
                else "Dream collision"
            ),
            "summary": collision.reflection,
            "topic": collision.topic,
            "source_url": collision.source_url,
            "stimulus_record_id": collision.stimulus_record_id,
            "dream_cycle_id": dream_cycle_id,
            "priority_score": round(float(collision.priority_score), 4),
            "relevance_score": round(float(collision.relevance_score), 4),
            "novelty_score": round(float(collision.novelty_score), 4),
            "resonance_score": round(float(collision.resonance_score), 4),
            "friction_score": (
                round(float(collision.friction_score), 4)
                if collision.friction_score is not None
                else None
            ),
            "should_convene_council": bool(collision.should_convene_council),
            "council_reason": collision.council_reason,
            "llm_backend": collision.llm_backend,
            "reflection": collision.reflection,
            "reflection_generated": bool(collision.reflection_generated),
            "related_memories": list(collision.related_memories),
            "crystal_rules": list(collision.crystal_rules),
            "resistance": dict(collision.resistance),
            "observability": dict(collision.observability),
            "source_record_ids": [collision.stimulus_record_id],
            "promotion_gate": {
                "status": "candidate",
                "source": "dream_engine",
            },
            "decay_policy": {
                "policy": "adaptive",
            },
            "tags": ["dream", "collision", "autonomous"],
            "evidence": evidence,
            "provenance": {
                "kind": "dream_collision",
                "dream_cycle_id": dream_cycle_id,
                "source_url": collision.source_url,
                "stimulus_record_id": collision.stimulus_record_id,
                "generated_at": generated_at,
            },
        }

    def _active_unresolved_collision_signatures(self) -> set[str]:
        signatures: set[str] = set()
        rows = list_subjectivity_records(
            self.soul_db,
            source=MemorySource.CUSTOM,
            subjectivity_layer=SubjectivityLayer.TENSION.value,
            unresolved_only=True,
            limit=None,
        )
        for row in rows:
            if _normalize_signature_part(row.get("type")) != "dream_collision":
                continue
            signature = self._collision_signature(
                topic=row.get("topic"),
                source_url=row.get("source_url"),
                source_record_ids=row.get("source_record_ids"),
            )
            if signature:
                signatures.add(signature)
        return signatures

    def _collision_signature(
        self,
        *,
        topic: object,
        source_url: object,
        stimulus_record_id: object = None,
        source_record_ids: object = None,
    ) -> Optional[str]:
        normalized_topic = _normalize_signature_part(topic)
        if not normalized_topic:
            return None
        normalized_source_url = _normalize_signature_part(source_url)
        if normalized_source_url:
            return f"{normalized_topic}||url:{normalized_source_url}"

        lineage_candidates: List[str] = []
        normalized_stimulus_record_id = _normalize_signature_part(stimulus_record_id)
        if normalized_stimulus_record_id:
            lineage_candidates.append(normalized_stimulus_record_id)
        if isinstance(source_record_ids, list):
            lineage_candidates.extend(
                normalized
                for normalized in (_normalize_signature_part(item) for item in source_record_ids)
                if normalized
            )
        if not lineage_candidates:
            return None
        return f"{normalized_topic}||lineage:{lineage_candidates[0]}"

    def _reviewed_collision_signature(
        self,
        *,
        topic: object,
        source_url: object,
        stimulus_record_id: object = None,
        source_record_ids: object = None,
    ) -> Optional[str]:
        normalized_topic = _normalize_signature_part(topic)
        if not normalized_topic:
            return None
        normalized_source_url = _normalize_signature_part(source_url)

        lineage_candidates: List[str] = []
        normalized_stimulus_record_id = _normalize_signature_part(stimulus_record_id)
        if normalized_stimulus_record_id:
            lineage_candidates.append(normalized_stimulus_record_id)
        if isinstance(source_record_ids, list):
            lineage_candidates.extend(
                normalized
                for normalized in (_normalize_signature_part(item) for item in source_record_ids)
                if normalized
            )
        normalized_lineage = lineage_candidates[0] if lineage_candidates else ""
        if normalized_source_url and normalized_lineage:
            return f"{normalized_topic}||url:{normalized_source_url}||lineage:{normalized_lineage}"
        if normalized_source_url:
            return f"{normalized_topic}||url:{normalized_source_url}"
        if normalized_lineage:
            return f"{normalized_topic}||lineage:{normalized_lineage}"
        return None

    def _historical_rejected_collision_signatures(self) -> set[str]:
        signatures: dict[str, tuple[datetime, str]] = {}
        rows = list_subjectivity_records(
            self.soul_db,
            source=MemorySource.CUSTOM,
            subjectivity_layer=SubjectivityLayer.TENSION.value,
            unresolved_only=False,
            limit=None,
        )
        for row in rows:
            if _normalize_signature_part(row.get("type")) != "dream_collision":
                continue
            review_status = _normalize_signature_part(row.get("review_status"))
            if not review_status:
                continue
            signature = self._reviewed_collision_signature(
                topic=row.get("topic"),
                source_url=row.get("source_url"),
                source_record_ids=row.get("source_record_ids"),
            )
            if not signature:
                continue
            review_timestamp = _parse_iso_sort_key(
                row.get("review_timestamp") or row.get("timestamp")
            )
            previous = signatures.get(signature)
            if previous is None or review_timestamp >= previous[0]:
                signatures[signature] = (review_timestamp, review_status)
        return {signature for signature, (_, status) in signatures.items() if status == "rejected"}

    def _resolve_llm_preflight(
        self,
        *,
        generate_reflection: bool,
        require_inference_ready: bool,
        inference_timeout_seconds: float,
    ) -> Dict[str, object]:
        if not generate_reflection:
            return {
                "enabled": False,
                "required": False,
                "ok": False,
                "supported": False,
                "reason": "reflection_disabled",
            }
        if not require_inference_ready:
            return {
                "enabled": False,
                "required": False,
                "ok": True,
                "supported": False,
                "reason": "preflight_skipped",
            }

        check = getattr(self.router, "inference_check", None)
        if not callable(check):
            return {
                "enabled": True,
                "required": True,
                "ok": True,
                "supported": False,
                "reason": "router_probe_unsupported",
                "timeout_seconds": float(inference_timeout_seconds),
            }

        result = check(timeout_seconds=float(inference_timeout_seconds))
        normalized = dict(result) if isinstance(result, dict) else {"ok": False}
        normalized.setdefault("ok", False)
        normalized.setdefault("supported", False)
        normalized["enabled"] = True
        normalized["required"] = True
        normalized["timeout_seconds"] = float(inference_timeout_seconds)
        return normalized

    def select_stimuli(
        self,
        *,
        limit: int = 3,
        min_priority: float = 0.35,
    ) -> List[Any]:
        records = self.write_gateway.stream_environment_stimuli()
        ranked: List[tuple[float, str, Any]] = []
        for record in records:
            priority = self._priority_score(record.payload)
            if priority < float(min_priority):
                continue
            ranked.append((priority, str(record.timestamp or ""), record))
        ranked.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return [item[2] for item in ranked[: max(0, int(limit))]]

    def _build_collision(
        self,
        record: Any,
        *,
        crystals: Sequence[Crystal],
        related_limit: int,
        client: Any,
        llm_backend: Optional[str],
        generate_reflection: bool,
    ) -> DreamCollision:
        payload = record.payload if isinstance(record.payload, dict) else {}
        priority = self._priority_score(payload)
        query_terms = self._build_query_terms(payload)
        related_memories = self._recall_related_memories(
            record_id=str(record.record_id or ""),
            query_terms=query_terms,
            limit=related_limit,
        )
        selected_crystals = self._select_core_rules(
            payload, crystals=crystals, limit=max(1, len(crystals))
        )

        resonance_score = self._resonance_score(
            query_terms=query_terms,
            related_memories=related_memories,
            crystals=selected_crystals,
        )
        query_tension = priority
        memory_tension = max(0.0, 1.0 - resonance_score)
        delta_t = abs(query_tension - resonance_score)
        query_wave = {
            "uncertainty_shift": self._safe_unit(payload.get("novelty_score")),
            "divergence_shift": self._safe_unit(memory_tension),
            "risk_shift": self._safe_unit(query_tension),
            "revision_shift": self._safe_unit(delta_t),
        }
        memory_wave = {
            "uncertainty_shift": self._safe_unit(resonance_score),
            "divergence_shift": self._safe_unit(memory_tension),
            "risk_shift": self._safe_unit(len(selected_crystals) / max(1, len(crystals) or 1)),
            "revision_shift": self._safe_unit(len(related_memories) / max(1, related_limit)),
        }
        prior_tension = {
            "query_tension": self._safe_unit(query_tension),
            "memory_tension": self._safe_unit(memory_tension),
            "delta_t": self._safe_unit(delta_t),
            "query_wave": query_wave,
            "memory_wave": memory_wave,
            "constraint_kind": "core_rule",
            "is_immutable": memory_tension >= 0.7,
            "gate_decision": "declare_stance" if memory_tension >= 0.55 else "approve",
        }

        friction_score = self.governance_kernel.compute_prior_governance_friction(
            prior_tension,
            str(payload.get("summary") or payload.get("topic") or ""),
        )
        if friction_score is None:
            friction_score = round((query_tension + memory_tension + delta_t) / 3.0, 4)

        runtime_friction = self.governance_kernel.compute_runtime_friction(
            prior_tension=prior_tension,
            tone_strength=query_tension,
        )
        lyapunov_proxy = round(delta_t * max(query_tension, memory_tension), 4)
        breaker_status, breaker_reason, breaker_state = (
            self.governance_kernel.check_circuit_breaker(
                runtime_friction,
                lyapunov_exponent=lyapunov_proxy,
            )
        )
        should_convene, council_reason = self.governance_kernel.should_convene_council(
            tension=query_tension,
            friction_score=friction_score,
        )
        if breaker_status == "frozen":
            should_convene = True
            extra_reason = breaker_reason or "circuit breaker frozen"
            council_reason = f"{council_reason}; {extra_reason}"

        reflection, reflection_generated = self._generate_reflection(
            payload=payload,
            related_memories=related_memories,
            crystal_rules=[crystal.rule for crystal in selected_crystals],
            friction_score=friction_score,
            council_reason=council_reason,
            client=client,
            llm_backend=llm_backend,
            generate_reflection=generate_reflection,
        )
        observability = {
            "query_terms": query_terms,
            "lyapunov_proxy": lyapunov_proxy,
            "breaker_status": breaker_status,
        }
        llm_observability = (
            self._build_llm_observability(client=client, llm_backend=llm_backend)
            if reflection_generated
            else {}
        )
        if llm_observability:
            observability["llm"] = llm_observability

        return DreamCollision(
            stimulus_record_id=str(record.record_id or ""),
            topic=str(payload.get("topic") or ""),
            source_url=str(payload.get("source_url") or ""),
            priority_score=priority,
            relevance_score=self._safe_unit(payload.get("relevance_score")),
            novelty_score=self._safe_unit(payload.get("novelty_score")),
            resonance_score=resonance_score,
            friction_score=friction_score,
            should_convene_council=should_convene,
            council_reason=council_reason,
            llm_backend=llm_backend,
            reflection=reflection,
            reflection_generated=reflection_generated,
            related_memories=related_memories,
            crystal_rules=[crystal.rule for crystal in selected_crystals],
            resistance={
                "prior_tension": prior_tension,
                "runtime_friction": (
                    runtime_friction.to_dict() if runtime_friction is not None else None
                ),
                "circuit_breaker": breaker_state,
            },
            observability=observability,
        )

    @staticmethod
    def _safe_unit(value: object) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, min(1.0, numeric))

    def _priority_score(self, payload: Dict[str, object]) -> float:
        relevance = self._safe_unit(payload.get("relevance_score"))
        novelty = self._safe_unit(payload.get("novelty_score"))
        tag_bonus = (
            min(0.1, 0.02 * len(payload.get("tags") or []))
            if isinstance(payload.get("tags"), list)
            else 0.0
        )
        priority = (0.55 * relevance) + (0.35 * novelty) + tag_bonus
        return round(min(1.0, priority), 4)

    def _build_query_terms(self, payload: Dict[str, object]) -> List[str]:
        terms: List[str] = []
        seen: set[str] = set()

        def _add(term: str) -> None:
            cleaned = str(term or "").strip().lower()
            if not cleaned or cleaned in seen:
                return
            seen.add(cleaned)
            terms.append(cleaned)

        for field_name in ("topic", "summary"):
            field_value = str(payload.get(field_name) or "")
            for piece in field_value.split():
                _add(piece)

        tags = payload.get("tags")
        if isinstance(tags, list):
            for tag in tags:
                _add(str(tag))

        return terms[:12]

    def _recall_related_memories(
        self,
        *,
        record_id: str,
        query_terms: Iterable[str],
        limit: int,
    ) -> List[Dict[str, object]]:
        query = " ".join(str(term).strip() for term in query_terms if str(term).strip())
        if not query:
            return []

        hits = self.soul_db.search(query, limit=max(int(limit) + 4, int(limit)))
        hit_ids = [
            str(item.get("id") or "").strip()
            for item in hits
            if str(item.get("id") or "").strip() and str(item.get("id") or "").strip() != record_id
        ]
        if not hit_ids:
            return []

        details = self.soul_db.detail(hit_ids)
        compact: List[Dict[str, object]] = []
        for detail in details:
            payload = detail.get("payload")
            payload_dict = payload if isinstance(payload, dict) else {}
            compact.append(
                {
                    "id": str(detail.get("id") or ""),
                    "title": str(detail.get("title") or ""),
                    "source": str(detail.get("source") or ""),
                    "layer": str(detail.get("layer") or ""),
                    "summary": self._compact_summary(payload_dict),
                    "tags": list(detail.get("tags") or []),
                }
            )
        return compact[: max(0, int(limit))]

    def _select_core_rules(
        self,
        payload: Dict[str, object],
        *,
        crystals: Sequence[Crystal],
        limit: int,
    ) -> List[Crystal]:
        if not crystals:
            return []

        terms = set(self._build_query_terms(payload))
        ranked: List[tuple[float, int, Crystal]] = []
        for index, crystal in enumerate(crystals):
            text = f"{crystal.rule} {' '.join(crystal.tags)}".lower()
            matches = sum(1 for term in terms if term and term in text)
            score = float(crystal.weight) + (0.15 * matches)
            ranked.append((score, -index, crystal))
        ranked.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return [item[2] for item in ranked[: max(0, int(limit))]]

    def _resonance_score(
        self,
        *,
        query_terms: Sequence[str],
        related_memories: Sequence[Dict[str, object]],
        crystals: Sequence[Crystal],
    ) -> float:
        if not query_terms:
            return 0.0

        term_set = {term for term in query_terms if term}
        related_hits = 0
        for memory in related_memories:
            text = (
                f"{memory.get('title', '')} {memory.get('summary', '')} "
                f"{' '.join(memory.get('tags', []))}"
            ).lower()
            if any(term in text for term in term_set):
                related_hits += 1

        crystal_hits = 0
        for crystal in crystals:
            text = f"{crystal.rule} {' '.join(crystal.tags)}".lower()
            if any(term in text for term in term_set):
                crystal_hits += 1

        related_ratio = related_hits / max(1, len(related_memories)) if related_memories else 0.0
        crystal_ratio = crystal_hits / max(1, len(crystals)) if crystals else 0.0
        resonance = (0.6 * related_ratio) + (0.4 * crystal_ratio)
        return round(max(0.0, min(1.0, resonance)), 4)

    def _generate_reflection(
        self,
        *,
        payload: Dict[str, object],
        related_memories: Sequence[Dict[str, object]],
        crystal_rules: Sequence[str],
        friction_score: float,
        council_reason: str,
        client: Any,
        llm_backend: Optional[str],
        generate_reflection: bool,
    ) -> tuple[str, bool]:
        fallback = self._fallback_reflection(
            payload=payload,
            related_memories=related_memories,
            crystal_rules=crystal_rules,
            friction_score=friction_score,
            council_reason=council_reason,
        )
        if not generate_reflection:
            return fallback, False

        generated = self._call_llm(
            client,
            prompt=self._reflection_prompt(
                payload=payload,
                related_memories=related_memories,
                crystal_rules=crystal_rules,
                friction_score=friction_score,
                council_reason=council_reason,
                llm_backend=llm_backend,
            ),
        )
        if not generated:
            return fallback, False
        return generated, True

    def _build_llm_observability(
        self,
        *,
        client: Any,
        llm_backend: Optional[str],
    ) -> Dict[str, object]:
        metrics = getattr(client, "last_metrics", None)
        if metrics is None:
            metrics = getattr(self.router, "last_metrics", None)

        from tonesoul.schemas import LLMObservabilityTrace

        return LLMObservabilityTrace.build_payload(
            backend=llm_backend,
            metrics=metrics,
            fallback_model=getattr(client, "model", None),
        )

    @staticmethod
    def _call_llm(client: Any, *, prompt: str) -> Optional[str]:
        if client is None:
            return None
        generate = getattr(client, "generate", None)
        if not callable(generate):
            return None
        for args in ((prompt, "You are ToneSoul's dream engine."), (prompt,)):
            try:
                response = generate(*args)
            except TypeError:
                continue
            except Exception:
                return None
            text = str(response or "").strip()
            if text:
                return text
        return None

    def _reflection_prompt(
        self,
        *,
        payload: Dict[str, object],
        related_memories: Sequence[Dict[str, object]],
        crystal_rules: Sequence[str],
        friction_score: float,
        council_reason: str,
        llm_backend: Optional[str],
    ) -> str:
        related_titles = [str(item.get("title") or "") for item in related_memories]
        evidence_lines = [
            "Treat the stimulus, related memory titles, durable rules, governance friction, and council recommendation below as the only evidence.",
            "Do not invent hidden memories, unseen rules, or extra governance facts that are not listed here.",
            "Keep the reflection replay-safe: describe the observed collision and next governance move without narrating hidden chain-of-thought.",
        ]
        recovery_lines = [
            "If the evidence is thin or conflicting, say so directly instead of forcing a dramatic collision.",
            "If no safe governance move is strongly supported, recommend the smallest bounded review or follow-up step.",
            "Keep the final output to exactly 2 concise sentences.",
        ]
        prompt_lines = [
            "You are ToneSoul's offline Dream Engine.",
            "Review one environmental stimulus against recalled memory and durable rules.",
            "",
            "Goal function:",
            "- Produce a replay-safe 2-sentence reflection that names the dream collision and the next bounded governance move.",
            "",
            "Priority rules:",
            "- P0: Do not fabricate memories, rules, evidence, or governance conclusions beyond the provided inputs.",
            "- P1: Keep the reflection grounded in the listed stimulus, memory titles, durable rules, friction, and council signal.",
            "- P2: Preserve compression and tone only after P0 and P1 are satisfied.",
            "",
            "Evidence discipline:",
            *[f"- {item}" for item in evidence_lines],
            "",
            "Recovery instructions:",
            *[f"- {item}" for item in recovery_lines],
            "",
            "Available evidence:",
            f"Backend: {llm_backend or 'none'}",
            f"Stimulus topic: {payload.get('topic') or ''}",
            f"Stimulus summary: {payload.get('summary') or ''}",
            f"Stimulus tags: {', '.join(payload.get('tags') or [])}",
            f"Governance friction: {round(float(friction_score), 4)}",
            f"Council recommendation: {council_reason}",
            "Related memory titles:",
            *[f"- {title}" for title in related_titles[:5]],
            "Durable rules:",
            *[f"- {rule}" for rule in crystal_rules[:5]],
            "",
            "Output spec:",
            "- Exactly 2 concise sentences",
            "- Sentence 1: the collision between stimulus, recalled memory, and durable rules",
            "- Sentence 2: the next bounded governance move",
        ]
        return "\n".join(prompt_lines)

    def _fallback_reflection(
        self,
        *,
        payload: Dict[str, object],
        related_memories: Sequence[Dict[str, object]],
        crystal_rules: Sequence[str],
        friction_score: float,
        council_reason: str,
    ) -> str:
        topic = str(payload.get("topic") or "untitled stimulus").strip() or "untitled stimulus"
        return (
            f"Dream collision examined '{topic}'. "
            f"Friction={round(float(friction_score), 4)} with {len(related_memories)} recalled memories "
            f"and {len(crystal_rules)} durable rules. Next governance move: {council_reason}."
        )

    @staticmethod
    def _compact_summary(payload: Dict[str, object]) -> str:
        for key in ("summary", "statement", "text", "content", "note"):
            value = payload.get(key)
            if isinstance(value, str):
                text = value.strip()
                if text:
                    return text[:160]
        return ""


def build_dream_engine(
    *,
    db_path: Optional[Path] = None,
    crystal_path: Optional[Path] = None,
) -> DreamEngine:
    soul_db = SqliteSoulDB(db_path=db_path) if db_path is not None else SqliteSoulDB()
    crystallizer = (
        MemoryCrystallizer(crystal_path=crystal_path)
        if crystal_path is not None
        else MemoryCrystallizer()
    )
    kernel = GovernanceKernel()
    return DreamEngine(
        soul_db=soul_db,
        write_gateway=MemoryWriteGateway(soul_db),
        governance_kernel=kernel,
        router=LLMRouter(backend_resolver=kernel.resolve_llm_backend),
        crystallizer=crystallizer,
    )
