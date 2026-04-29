"""Pre-output council: convene perspectives before a draft reaches the user."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from tonesoul.soul_config import SOUL

from .base import IPerspective
from .coherence import compute_coherence
from .epistemic_labeler import EpistemicLabeler
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
    ):
        self.perspectives = self._normalize_perspectives(
            perspectives,
            perspective_config,
        )
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
        votes = [
            perspective.evaluate(draft_output, context, user_intent)
            for perspective in self.perspectives
        ]

        # Apply evolved voting weights if available
        weights = None
        try:
            from tonesoul.council.evolution import CouncilEvolution

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
        # Phase 864a Layer 1: attach epistemic metadata to every verdict.
        # Runs unconditionally — null labels would force every consumer
        # (verifier, audit, future calibration) to handle absence cases.
        verdict.epistemic_label = self._epistemic_labeler.label(
            draft_output=draft_output,
            context=context,
            user_intent=user_intent,
        )

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
