"""Pre-output council: convene perspectives before a draft reaches the user."""

from __future__ import annotations

import inspect
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from tonesoul.soul_config import SOUL

from .base import IPerspective
from .coherence import compute_coherence
from .epistemic_labeler import EpistemicLabeler
from .independent_verifier import (
    IndependentVerifier,
    VerifierConfig,
    VerifierReport,
    VerifierStatus,
)
from .self_journal import record_self_memory
from .summary_generator import (
    build_divergence_analysis,
    build_transcript,
    generate_human_summary,
    resolve_language,
)
from .types import CouncilVerdict, PerspectiveType, VerdictType
from .verdict import generate_verdict

__ts_layer__ = "governance"
__ts_purpose__ = "Convene the pre-output council: run perspectives, compute coherence, emit verdict and transcript."


class PreOutputCouncil:
    def __init__(
        self,
        perspectives: Optional[
            Union[
                IPerspective,
                List[Union[IPerspective, PerspectiveType, str]],
                Dict[Union[PerspectiveType, str], Dict[str, Any]],
                PerspectiveType,
                str,
            ]
        ] = None,
        coherence_threshold: float = SOUL.council.coherence_threshold,
        block_threshold: float = SOUL.council.block_threshold,
        perspective_config: Optional[Dict[Union[PerspectiveType, str], Dict[str, Any]]] = None,
        verifier: Optional[IndependentVerifier] = None,
        verifier_config: Optional[VerifierConfig] = None,
        overclaim_sensor: Optional[Any] = None,
        proportionality_gate: Optional[Any] = None,
        principle_invocation_sensor: Optional[Any] = None,
    ):
        self.perspectives = self._normalize_perspectives(
            perspectives,
            perspective_config,
        )
        # Phase C Independent Verifier — optional post-verdict audit by a
        # substrate-separated reviewer. verifier=None (default) -> no audit and
        # behaviour identical to pre-Phase-C. See independent_verifier_spec_
        # 2026-05-14.md for role boundary + fail-open semantics.
        self.verifier = verifier
        self.verifier_config = verifier_config or VerifierConfig()
        # Tier 5 semantic overclaim sensor (advisory). Injected for tests; otherwise
        # lazy-created in validate() when SOUL.council.semantic_overclaim_advisory_enabled.
        self._overclaim_sensor = overclaim_sensor
        # Tier 5 intent-proportionality gate (advisory). Injected for tests; otherwise
        # lazy-created in validate() when SOUL.council.intent_proportionality_advisory_enabled.
        self._proportionality_gate = proportionality_gate
        # Principle Invocation Gate v0 (advisory). Injected for tests; otherwise
        # lazy-created in validate() when SOUL.council.principle_invocation_advisory_enabled.
        self._principle_invocation_sensor = principle_invocation_sensor
        self.coherence_threshold = coherence_threshold
        self.block_threshold = block_threshold
        # Phase 864a Layer 1: deterministic, side-effect-free; safe to share.
        self._epistemic_labeler = EpistemicLabeler()
        # Phase 2 strategy_mirror: lazy-initialised on first scan. Built
        # only if SOUL.gse.strategy_mirror_scan_enabled is True; cached per
        # PreOutputCouncil instance so the catalog (~150 entries) is read
        # at most once per council lifetime.
        self._strategy_detector = None

    def validate(
        self,
        draft_output: str,
        context: dict,
        user_intent: Optional[str] = None,
        auto_record_self_memory: bool = True,
    ) -> CouncilVerdict:
        # PR #50 (epistemic_label wiring): label the draft FIRST so consuming
        # perspectives (Analyst, Critic per ratified §3.1) can use it as a
        # soft prior in their evaluation. Other perspectives accept the kwarg
        # without using it (regression-safe). Phase 864a's design of attaching
        # the label to every verdict still holds — it now happens earlier so
        # downstream perspectives can read it during evaluate.
        epistemic_label = self._epistemic_labeler.label(
            draft_output=draft_output,
            context=context,
            user_intent=user_intent,
        )
        votes = [
            self._evaluate_perspective(
                perspective=perspective,
                draft_output=draft_output,
                context=context,
                user_intent=user_intent,
                epistemic_label=epistemic_label,
            )
            for perspective in self.perspectives
        ]

        # Apply evolved voting weights only when explicitly enabled. The evolution
        # record/evolve/summary chain remains owned by runtime and stays observable.
        weights = None
        if SOUL.council.evolution_weights_applied:
            try:
                from tonesoul.council.voting_evolution import CouncilEvolution

                if not hasattr(self, "_evolution"):
                    self._evolution = CouncilEvolution()
                weights = self._evolution.get_weights()
            except Exception:
                pass

        coherence = compute_coherence(votes, weights=weights)
        verdict = generate_verdict(
            votes=votes,
            coherence=coherence,
            coherence_threshold=self.coherence_threshold,
            block_threshold=self.block_threshold,
        )
        language = resolve_language(context)
        divergence = build_divergence_analysis(votes, context=context)
        verdict.divergence_analysis = divergence
        # Attach the epistemic label computed above to the verdict so
        # downstream consumers (audit, calibration, transcript) see it.
        verdict.epistemic_label = epistemic_label

        # Phase 2 strategy_mirror: opt-in self-scan of the draft for
        # rhetorical/strategic moves. Two-flag scheme (2026-04-29 split):
        #   - strategy_mirror_scan_enabled: run scan + attach signature
        #   - strategy_mirror_enforce_enabled: also force-downgrade
        #     APPROVE→BLOCK on red / undeclared yellow per spec §5.3/§5.4
        # enforce⇒scan is auto-enforced in GSEConfig.__post_init__, so
        # checking scan_enabled here is sufficient as the entry gate.
        if SOUL.gse.strategy_mirror_scan_enabled:
            verdict = self._apply_strategy_mirror(
                verdict=verdict,
                draft_output=draft_output,
                context=context,
            )

        # Build human-facing and audit-facing surfaces only after optional
        # strategy_mirror enforcement, otherwise APPROVE→BLOCK downgrades can
        # leave stale "safe/helpful" summaries and APPROVE transcripts.
        verdict.human_summary = generate_human_summary(verdict, language=language)
        verdict.transcript = build_transcript(
            draft_output=draft_output,
            context=context,
            user_intent=user_intent,
            votes=votes,
            coherence=coherence,
            verdict=verdict,
            divergence=divergence,
        )

        # Phase C Independent Verifier — runs AFTER verdict construction is
        # complete (synthesis, strategy_mirror, human_summary, transcript) so it
        # sees the final artifact. Attaches a report, never modifies the verdict.
        # Default-off (verifier is None). Fail-open. See
        # independent_verifier_spec_2026-05-14.md §2.4 / §2.5.
        if self.verifier is not None:
            verdict.verifier_report = self._run_independent_verifier(
                verdict=verdict,
                context=context,
                user_intent=user_intent,
            )

        # Tier 5 semantic overclaim sensor — ADVISORY ONLY (DESIGN Inv3). Records a
        # meta.not_for resemblance signal alongside the lexical guardian; it never
        # modifies the verdict. Default-off + fail-soft. Limits: see the eval doc.
        sensor = self._overclaim_sensor
        if sensor is None and SOUL.council.semantic_overclaim_advisory_enabled:
            try:
                from tonesoul.council.semantic_overclaim_sensor import SemanticOverclaimSensor

                sensor = self._overclaim_sensor = SemanticOverclaimSensor()
            except Exception:
                sensor = None
        if sensor is not None:
            try:
                verdict.semantic_overclaim = sensor.assess(draft_output).to_dict()
            except Exception:
                pass

        # Tier 5 intent-proportionality gate — ADVISORY ONLY (DESIGN Inv3). Checks the
        # draft against the agent's OWN intent (did it escalate beyond the ask?), records
        # a signal + contract suggestion; never auto-edits/blocks. Needs user_intent;
        # default-off + fail-soft. See intent_proportionality_eval_2026-06-15.md.
        gate = self._proportionality_gate
        if gate is None and SOUL.council.intent_proportionality_advisory_enabled:
            try:
                from tonesoul.council.intent_proportionality import IntentProportionalityGate

                gate = self._proportionality_gate = IntentProportionalityGate()
            except Exception:
                gate = None
        if gate is not None and user_intent:
            try:
                verdict.intent_proportionality = gate.assess(user_intent, draft_output).to_dict()
            except Exception:
                pass

        # Principle Invocation Gate v0 — ADVISORY ONLY (DESIGN Inv3). Flags axiom-cited
        # non-APPROVE verdicts lacking a filed_with_annotation marker (axiom-as-deferral
        # anti-pattern, Gap 8). Attached to every verdict when enabled — false-positive
        # rates need denominators. Records a signal, never modifies the verdict.
        # Default-off + fail-soft. Work order: WO-3.
        pig = self._principle_invocation_sensor
        if pig is None and SOUL.council.principle_invocation_advisory_enabled:
            try:
                from tonesoul.council.principle_invocation import PrincipleInvocationSensor

                pig = self._principle_invocation_sensor = PrincipleInvocationSensor()
            except Exception:
                pig = None
        if pig is not None:
            try:
                verdict.principle_invocation = pig.assess(verdict).to_dict()
            except Exception:
                pass

        # Selective self-memory: auto-record for meaningful decisions
        record_option = context.get("record_self_memory")
        should_auto_record = verdict.verdict in (
            VerdictType.BLOCK,
            VerdictType.DECLARE_STANCE,
        )

        if auto_record_self_memory and (record_option or should_auto_record):
            path = record_option if isinstance(record_option, (str, bytes)) else None
            try:
                context["user_intent"] = user_intent
                record_self_memory(verdict, context=context, path=path)
            except OSError:
                pass

        return verdict

    def _run_independent_verifier(
        self,
        *,
        verdict: CouncilVerdict,
        context: dict,
        user_intent: Optional[str],
    ) -> VerifierReport:
        """Invoke the configured verifier with fail-open semantics.

        Any exception from the verifier produces an ERROR VerifierReport with
        fail_open_reason populated. The caller proceeds with the original verdict
        unchanged. See spec §2.5.
        """
        assert self.verifier is not None  # caller guarded
        try:
            return self.verifier.verify(
                verdict=verdict,
                context={"user_intent": user_intent, **(context or {})},
                config=self.verifier_config,
            )
        except Exception as exc:
            return VerifierReport(
                status=VerifierStatus.ERROR,
                reasoning=f"Verifier raised: {type(exc).__name__}",
                verifier_id=getattr(self.verifier, "verifier_id", "unknown"),
                audited_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                fail_open_reason=f"{type(exc).__name__}: {str(exc)[:200]}",
            )

    def _evaluate_perspective(
        self,
        *,
        perspective: IPerspective,
        draft_output: str,
        context: dict,
        user_intent: Optional[str],
        epistemic_label: object,
    ):
        """Call a perspective while preserving pre-PR #50 plugin compatibility."""
        if self._supports_epistemic_label(perspective):
            return perspective.evaluate(
                draft_output,
                context,
                user_intent,
                epistemic_label=epistemic_label,
            )
        return perspective.evaluate(draft_output, context, user_intent)

    @staticmethod
    def _supports_epistemic_label(perspective: IPerspective) -> bool:
        """Return True when evaluate() can accept the PR #50 epistemic label kwarg."""
        try:
            signature = inspect.signature(perspective.evaluate)
        except (TypeError, ValueError):
            return True

        return any(
            parameter.name == "epistemic_label" or parameter.kind == inspect.Parameter.VAR_KEYWORD
            for parameter in signature.parameters.values()
        )

    # ------------------------------------------------------------------
    # Phase 2 strategy_mirror integration (spec §5)
    # ------------------------------------------------------------------

    def _get_strategy_detector(self):
        """Lazy-init the StrategyDetector with the period catalog loaded.

        Returns None if the catalog cannot be loaded (e.g. dev environment
        without the JSON file), so that scan-only shadow mode or full
        enforcement mode do not hard-fail an otherwise functioning council.
        """
        if self._strategy_detector is not None:
            return self._strategy_detector
        try:
            from tonesoul.gse.strategy_mirror import CatalogLoader
            from tonesoul.gse.strategy_mirror.detector import StrategyDetector

            loader = CatalogLoader().load()
            if len(loader) == 0:
                # Catalog directory exists but no entries — treat as disabled.
                return None
            self._strategy_detector = StrategyDetector(
                loader,
                confidence_threshold=SOUL.gse.strategy_mirror_confidence_threshold,
            )
            return self._strategy_detector
        except Exception:  # pragma: no cover — defensive
            return None

    def _apply_strategy_mirror(
        self,
        *,
        verdict: CouncilVerdict,
        draft_output: str,
        context: dict,
    ) -> CouncilVerdict:
        """Run the strategy mirror and adjust the verdict per spec §5.

        Two-flag scheme (post 2026-04-29 split):
          - scan_enabled gates whether scan runs (entry check is in
            validate(), so by the time we reach this method, scan is on)
          - enforce_enabled gates whether force-downgrade applies after
            scan completes

        Enforcement mode (scan + enforce both on):
          - has_red → force-downgrade APPROVE verdicts to BLOCK
          - has_undeclared_yellow + APPROVE → downgrade to BLOCK
          - signature attached regardless

        Shadow mode (scan on, enforce off):
          - signature attached
          - NO downgrade — verdict passes through unchanged
          - this is the mode for Day 7-9 calibration of the 14-day beta
            wave: capture first-hand evidence without changing council
            verdicts that participants experience

        NOT implemented in Phase 2 (deferred to Phase 4 reflection loop):
          - re-running perspectives with awareness of red moves
            (spec §5.3 step 3 — requires per-perspective awareness logic
            that does not exist yet; Phase 4 / RFC-014 will add it)
        """
        detector = self._get_strategy_detector()
        if detector is None:
            return verdict

        declared_moves = context.get("declared_moves") if isinstance(context, dict) else None
        signature = detector.scan(draft_output, declared_moves=declared_moves)
        verdict.strategy_signature = signature

        # Shadow mode short-circuit: signature attached but no enforcement.
        if not SOUL.gse.strategy_mirror_enforce_enabled:
            return verdict

        # Force-downgrade rule (enforce mode). Note: BLOCK / DECLARE_STANCE /
        # REFINE verdicts are left as-is — only APPROVE is overridden, since
        # the existing verdict types already express disagreement at
        # lower-than-APPROVE levels.
        if verdict.verdict == VerdictType.APPROVE:
            reason_parts: List[str] = []
            if signature.has_red:
                red_names = [d.move.name for d in signature.red_moves()]
                reason_parts.append(f"strategy_mirror: red moves detected ({', '.join(red_names)})")
            if signature.has_undeclared_yellow:
                undeclared_names = [d.move.name for d in signature.undeclared_yellow_moves()]
                reason_parts.append(
                    f"strategy_mirror: undeclared yellow moves "
                    f"({', '.join(undeclared_names)}) — declare or reword"
                )
            if reason_parts:
                verdict.verdict = VerdictType.BLOCK
                addendum = " | ".join(reason_parts)
                verdict.summary = f"{verdict.summary} | {addendum}" if verdict.summary else addendum
        return verdict

    def _default_perspectives(
        self,
        perspective_config: Optional[Dict[Union[PerspectiveType, str], Dict[str, Any]]] = None,
    ) -> List[IPerspective]:
        from .perspective_factory import PerspectiveFactory

        config = perspective_config or {}
        return PerspectiveFactory.create_council(config)

    def _normalize_perspectives(
        self,
        perspectives: Optional[
            Union[
                IPerspective,
                List[Union[IPerspective, PerspectiveType, str]],
                Dict[Union[PerspectiveType, str], Dict[str, Any]],
                PerspectiveType,
                str,
            ]
        ],
        perspective_config: Optional[Dict[Union[PerspectiveType, str], Dict[str, Any]]],
    ) -> List[IPerspective]:
        from .perspective_factory import PerspectiveFactory

        if perspectives is None:
            return self._default_perspectives(perspective_config)

        if not perspectives:
            return self._default_perspectives(perspective_config)

        if isinstance(perspectives, dict):
            return self._default_perspectives(perspectives)

        if isinstance(perspectives, IPerspective):
            return [perspectives]

        if isinstance(perspectives, (PerspectiveType, str)):
            return [PerspectiveFactory.create(name=perspectives)]

        resolved: List[IPerspective] = []
        for perspective in perspectives:
            if isinstance(perspective, IPerspective):
                resolved.append(perspective)
            else:
                resolved.append(PerspectiveFactory.create(name=perspective))
        return resolved
