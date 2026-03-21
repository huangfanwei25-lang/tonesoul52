"""
ToneSoul 2.0 Semantic Gravity

The synthesis engine that merges multiple perspectives
into a unified, coherent response.

Inspired by Legitimation Code Theory's concept of
"semantic gravity" - the degree to which meaning
is context-dependent.
"""

from itertools import combinations
from typing import List, Optional

from .persona_track_record import PersonaTrackRecord
from .types import (
    DeliberationContext,
    DeliberationWeights,
    PerspectiveType,
    SuggestedReply,
    SynthesisType,
    SynthesizedResponse,
    TacticalDecision,
    Tension,
    # ToneStream Distillation
    TensionZone,
    ViewPoint,
)


class SemanticGravity:
    """
    Merges multiple perspectives using weighted semantic gravity.

    The synthesis process:
    1. Detect tensions between viewpoints
    2. Calculate dynamic weights based on context
    3. Check for Guardian veto
    4. Merge responses using weights
    """

    # Base weights
    BASE_WEIGHTS = {
        PerspectiveType.MUSE: 0.35,
        PerspectiveType.LOGOS: 0.35,
        PerspectiveType.AEGIS: 0.30,
    }

    # Weight adjustment factors
    ADJUSTMENTS = {
        "technical_question": (PerspectiveType.LOGOS, 0.2),
        "philosophical_question": (PerspectiveType.MUSE, 0.2),
        "safety_concern": (PerspectiveType.AEGIS, 0.3),
        "high_tension": (PerspectiveType.LOGOS, 0.15),
        "conflict_state": (PerspectiveType.AEGIS, 0.25),
        "loop_detected": (PerspectiveType.LOGOS, 0.2),
    }

    # Pareto frontier boost for non-dominated viewpoints.
    # Kept intentionally small to preserve existing behavior.
    PARETO_BOOST = 0.05

    def __init__(self, track_record: Optional[PersonaTrackRecord] = None):
        self._track_record = track_record

    def synthesize(
        self,
        viewpoints: List[ViewPoint],
        context: DeliberationContext,
        deliberation_time_ms: float = 0.0,
    ) -> SynthesizedResponse:
        """
        Synthesize multiple viewpoints into final response.

        Args:
            viewpoints: List of ViewPoint from each perspective
            context: The deliberation context
            deliberation_time_ms: Time taken for deliberation

        Returns:
            SynthesizedResponse with merged output
        """
        if not viewpoints:
            return self._fallback_response(viewpoints, deliberation_time_ms)

        try:
            # Step 1: Check for Guardian veto
            aegis_view = self._find_aegis(viewpoints)
            if aegis_view and aegis_view.veto_triggered:
                return self._guardian_override(aegis_view, viewpoints, deliberation_time_ms)

            # Step 2: Detect tensions
            tensions = self.detect_tensions(viewpoints)

            # Step 3: Calculate dynamic weights
            weights = self.calculate_weights(viewpoints, context)

            # Step 4: Check for unanimous agreement
            if self._is_unanimous(viewpoints):
                return self._unanimous_response(viewpoints, weights, deliberation_time_ms)

            # Step 5: Weighted merge
            merged_response = self._weighted_merge(viewpoints, weights)
            dominant = self._get_dominant(weights)

            # Step 6: ToneStream Distillation - Generate tactical decision
            tactical = self._generate_tactical_decision(viewpoints, context)

            # Step 7: ToneStream Distillation - Generate suggested replies
            suggestions = self._generate_suggested_replies(context, dominant)

            # Step 8: ToneStream Distillation - Determine tension zone
            zone, calc_note = self._determine_tension_zone(tensions, viewpoints)

            return SynthesizedResponse(
                response=merged_response,
                synthesis_type=SynthesisType.WEIGHTED_FUSION,
                dominant_voice=dominant,
                viewpoints=viewpoints,
                tensions=tensions,
                weights=weights,
                deliberation_time_ms=deliberation_time_ms,
                # ToneStream additions
                tactical_decision=tactical,
                suggested_replies=suggestions,
                tension_zone=zone,
                calculation_note=calc_note,
            )
        except Exception:
            return self._fallback_response(viewpoints, deliberation_time_ms)

    def detect_tensions(self, viewpoints: List[ViewPoint]) -> List[Tension]:
        """Detect conflicts between viewpoints."""
        tensions = []

        for v1, v2 in combinations(viewpoints, 2):
            tension = self._compare_viewpoints(v1, v2)
            if tension:
                tensions.append(tension)

        return tensions

    def _compare_viewpoints(self, v1: ViewPoint, v2: ViewPoint) -> Optional[Tension]:
        """Compare two viewpoints for tension."""
        # Calculate disagreement score
        confidence_diff = abs(v1.confidence - v2.confidence)

        # Check for opposing concerns

        # Check Aegis safety vs others' confidence
        if v1.perspective == PerspectiveType.AEGIS:
            if v1.safety_risk > 0.5 and v2.confidence > 0.7:
                return Tension(
                    between=(v1.perspective, v2.perspective),
                    description=f"守護者擔心安全風險，但{v2.perspective.value}信心高",
                    severity=0.7,
                    resolution_hint="優先考慮安全，但保留原觀點的部分表達",
                )

        if v2.perspective == PerspectiveType.AEGIS:
            if v2.safety_risk > 0.5 and v1.confidence > 0.7:
                return Tension(
                    between=(v1.perspective, v2.perspective),
                    description=f"{v1.perspective.value}信心高，但守護者擔心安全",
                    severity=0.7,
                    resolution_hint="優先考慮安全，但保留原觀點的部分表達",
                )

        # Muse vs Logos tension (abstract vs concrete)
        if {v1.perspective, v2.perspective} == {PerspectiveType.MUSE, PerspectiveType.LOGOS}:
            if confidence_diff > 0.3:
                return Tension(
                    between=(v1.perspective, v2.perspective),
                    description="哲學家想深入探索，工程師要求先定義",
                    severity=0.4,
                    resolution_hint="先簡短定義再探索深層意義",
                )

        return None

    def calculate_weights(
        self, viewpoints: List[ViewPoint], context: DeliberationContext
    ) -> DeliberationWeights:
        """Calculate dynamic weights based on context."""
        weights = DeliberationWeights(
            muse=self.BASE_WEIGHTS[PerspectiveType.MUSE],
            logos=self.BASE_WEIGHTS[PerspectiveType.LOGOS],
            aegis=self.BASE_WEIGHTS[PerspectiveType.AEGIS],
        )

        # Apply adjustments based on context
        if context.loop_detected:
            weights.logos += 0.2

        if context.tone_strength > 0.7:
            weights.logos += 0.1

        if context.resonance_state == "conflict":
            weights.aegis += 0.25
        elif context.resonance_state == "tension":
            weights.logos += 0.15

        # Apply adjustments based on viewpoint confidence
        for vp in viewpoints:
            if vp.perspective == PerspectiveType.MUSE:
                weights.muse += (vp.confidence - 0.5) * 0.2
            elif vp.perspective == PerspectiveType.LOGOS:
                weights.logos += (vp.confidence - 0.5) * 0.2
            elif vp.perspective == PerspectiveType.AEGIS:
                if vp.safety_risk > 0.5:
                    weights.aegis += 0.3

        # Pareto adjustment: reward viewpoints that are not dominated
        # in the (confidence max, safety_risk min) objective space.
        pareto = self._pareto_frontier(viewpoints)
        for vp in pareto:
            if vp.perspective == PerspectiveType.MUSE:
                weights.muse += self.PARETO_BOOST
            elif vp.perspective == PerspectiveType.LOGOS:
                weights.logos += self.PARETO_BOOST
            elif vp.perspective == PerspectiveType.AEGIS:
                weights.aegis += self.PARETO_BOOST

        # Historical perspective performance bias (Phase 539)
        if self._track_record is not None:
            weights.muse *= self._track_record.get_multiplier(
                "muse",
                resonance_state=context.resonance_state,
                loop_detected=context.loop_detected,
            )
            weights.logos *= self._track_record.get_multiplier(
                "logos",
                resonance_state=context.resonance_state,
                loop_detected=context.loop_detected,
            )
            weights.aegis *= self._track_record.get_multiplier(
                "aegis",
                resonance_state=context.resonance_state,
                loop_detected=context.loop_detected,
            )

        # Normalize
        weights.normalize()

        return weights

    def _pareto_frontier(self, viewpoints: List[ViewPoint]) -> List[ViewPoint]:
        """Return non-dominated viewpoints under two objectives.

        Objectives:
        1) maximize confidence
        2) minimize safety_risk
        """
        frontier: List[ViewPoint] = []
        for candidate in viewpoints:
            dominated = False
            for other in viewpoints:
                if other is candidate:
                    continue
                better_or_equal_conf = other.confidence >= candidate.confidence
                better_or_equal_risk = other.safety_risk <= candidate.safety_risk
                strictly_better = (
                    other.confidence > candidate.confidence
                    or other.safety_risk < candidate.safety_risk
                )
                if better_or_equal_conf and better_or_equal_risk and strictly_better:
                    dominated = True
                    break
            if not dominated:
                frontier.append(candidate)
        return frontier

    def _weighted_merge(self, viewpoints: List[ViewPoint], weights: DeliberationWeights) -> str:
        """Merge responses using weights."""
        # Get weight for each perspective
        weight_map = {
            PerspectiveType.MUSE: weights.muse,
            PerspectiveType.LOGOS: weights.logos,
            PerspectiveType.AEGIS: weights.aegis,
        }

        # Sort by weight (descending)
        sorted_views = sorted(
            viewpoints, key=lambda v: weight_map.get(v.perspective, 0), reverse=True
        )

        # Use dominant perspective as base
        dominant = sorted_views[0]
        secondary = sorted_views[1] if len(sorted_views) > 1 else None

        # Simple merge: dominant response + hint from secondary
        merged = dominant.proposed_response

        if secondary and weight_map.get(secondary.perspective, 0) > 0.25:
            # Add secondary perspective influence
            if secondary.perspective == PerspectiveType.LOGOS:
                merged = f"{merged}\n\n從分析角度補充：{secondary.proposed_response[:100]}..."
            elif secondary.perspective == PerspectiveType.MUSE:
                merged = f"{merged}\n\n換個角度想：{secondary.proposed_response[:100]}..."
            elif secondary.perspective == PerspectiveType.AEGIS:
                if secondary.concerns:
                    merged = f"{merged}\n\n不過需要注意：{secondary.concerns[0]}"

        return merged

    def _fallback_response(
        self, viewpoints: List[ViewPoint], deliberation_time_ms: float
    ) -> SynthesizedResponse:
        """Return the strongest available voice without raising synthesis errors."""
        dominant = max(viewpoints, key=lambda v: v.confidence, default=None)

        return SynthesizedResponse(
            response=dominant.proposed_response if dominant else "",
            synthesis_type=SynthesisType.DOMINANT,
            dominant_voice=dominant.perspective if dominant else None,
            viewpoints=viewpoints,
            tensions=[],
            weights=DeliberationWeights(),
            deliberation_time_ms=deliberation_time_ms,
        )

    def _find_aegis(self, viewpoints: List[ViewPoint]) -> Optional[ViewPoint]:
        """Find the Aegis (Guardian) viewpoint."""
        for vp in viewpoints:
            if vp.perspective == PerspectiveType.AEGIS:
                return vp
        return None

    def _guardian_override(
        self, aegis: ViewPoint, all_viewpoints: List[ViewPoint], deliberation_time_ms: float
    ) -> SynthesizedResponse:
        """Guardian veto - override all other perspectives."""
        return SynthesizedResponse(
            response=aegis.proposed_response,
            synthesis_type=SynthesisType.GUARDIAN_OVERRIDE,
            dominant_voice=PerspectiveType.AEGIS,
            viewpoints=all_viewpoints,
            tensions=[],
            weights=DeliberationWeights(muse=0, logos=0, aegis=1.0),
            deliberation_time_ms=deliberation_time_ms,
        )

    def _is_unanimous(self, viewpoints: List[ViewPoint]) -> bool:
        """Check if all perspectives agree."""
        confidences = [vp.confidence for vp in viewpoints]
        # Unanimous if all high confidence and no concerns
        return all(c > 0.7 for c in confidences) and all(len(vp.concerns) == 0 for vp in viewpoints)

    def _unanimous_response(
        self, viewpoints: List[ViewPoint], weights: DeliberationWeights, deliberation_time_ms: float
    ) -> SynthesizedResponse:
        """All perspectives agree."""
        # Use highest confidence viewpoint
        best = max(viewpoints, key=lambda v: v.confidence)

        return SynthesizedResponse(
            response=best.proposed_response,
            synthesis_type=SynthesisType.UNANIMOUS,
            dominant_voice=best.perspective,
            viewpoints=viewpoints,
            tensions=[],
            weights=weights,
            deliberation_time_ms=deliberation_time_ms,
        )

    def _get_dominant(self, weights: DeliberationWeights) -> PerspectiveType:
        """Get the dominant perspective based on weights."""
        max_weight = max(weights.muse, weights.logos, weights.aegis)
        if weights.muse == max_weight:
            return PerspectiveType.MUSE
        elif weights.logos == max_weight:
            return PerspectiveType.LOGOS
        else:
            return PerspectiveType.AEGIS

    # ===== ToneStream Distillation Methods =====

    def _generate_tactical_decision(
        self, viewpoints: List[ViewPoint], context: DeliberationContext
    ) -> TacticalDecision:
        """Generate tactical decision matrix (ToneStream feature)."""
        # Analyze hidden intent from context
        hidden_intent = self._analyze_hidden_intent(context)

        # Determine strategy based on dominant perspective
        aegis = self._find_aegis(viewpoints)
        if aegis and aegis.safety_risk > 0.5:
            strategy_name = "安全優先策略"
            tone_tag = "cautious"
        elif context.loop_detected:
            strategy_name = "迴圈打破策略"
            tone_tag = "redirecting"
        elif context.resonance_state == "tension":
            strategy_name = "張力緩解策略"
            tone_tag = "empathetic"
        elif context.resonance_state == "conflict":
            strategy_name = "邊界設定策略"
            tone_tag = "firm_gentle"
        else:
            strategy_name = "深度連結策略"
            tone_tag = "warm"

        # Intended effect
        effect_map = {
            "安全優先策略": "保護用戶避免潛在傷害",
            "迴圈打破策略": "引導對話走出重複模式",
            "張力緩解策略": "降低情緒張力，建立理解",
            "邊界設定策略": "溫和但明確地設定界限",
            "深度連結策略": "建立有意義的深層對話",
        }

        return TacticalDecision(
            user_hidden_intent=hidden_intent,
            strategy_name=strategy_name,
            intended_effect=effect_map.get(strategy_name, "促進有意義的對話"),
            tone_tag=tone_tag,
        )

    def _analyze_hidden_intent(self, context: DeliberationContext) -> str:
        """Analyze user's hidden intent from input."""
        user_input = context.user_input.lower()

        # Pattern matching for hidden intents
        if any(w in user_input for w in ["為什麼", "怎麼", "如何"]):
            return "尋求理解或指導"
        elif any(w in user_input for w in ["可以嗎", "能不能", "好嗎"]):
            return "尋求許可或確認"
        elif any(w in user_input for w in ["我覺得", "我認為", "我想"]):
            return "分享觀點，期待被認可"
        elif any(w in user_input for w in ["煩", "累", "難過", "不開心"]):
            return "情緒抒發，需要陪伴"
        elif context.tone_strength > 0.7:
            return "強烈情緒需要被看見"
        elif context.loop_detected:
            return "卡在某個思維模式中"
        else:
            return "探索性對話"

    def _generate_suggested_replies(
        self, context: DeliberationContext, dominant: PerspectiveType
    ) -> List[SuggestedReply]:
        """Generate suggested user replies (ToneStream feature)."""
        suggestions = []

        # Based on dominant perspective
        if dominant == PerspectiveType.MUSE:
            suggestions.append(SuggestedReply(label="深入探索", text="可以再多說一點嗎？"))
            suggestions.append(SuggestedReply(label="換個角度", text="如果從另一個角度來看呢？"))
        elif dominant == PerspectiveType.LOGOS:
            suggestions.append(SuggestedReply(label="具體例子", text="可以舉個例子嗎？"))
            suggestions.append(SuggestedReply(label="下一步", text="那接下來應該怎麼做？"))
        elif dominant == PerspectiveType.AEGIS:
            suggestions.append(SuggestedReply(label="理解了", text="我明白了，謝謝提醒。"))
            suggestions.append(
                SuggestedReply(label="有其他方式嗎", text="有沒有其他方式可以達成？")
            )

        # Context-based suggestions
        if context.loop_detected:
            suggestions.append(
                SuggestedReply(label="跳出迴圈", text="讓我們從不同方向思考這個問題。")
            )

        return suggestions[:3]  # Max 3 suggestions

    def _determine_tension_zone(
        self, tensions: List[Tension], viewpoints: List[ViewPoint]
    ) -> tuple:
        """Determine cognitive tension zone (ToneStream feature)."""
        # Calculate overall tension score
        if not tensions:
            tension_score = 0.2  # Low default
        else:
            tension_score = sum(t.severity for t in tensions) / len(tensions)

        # Factor in viewpoint confidence divergence
        if len(viewpoints) >= 2:
            confidences = [vp.confidence for vp in viewpoints]
            divergence = max(confidences) - min(confidences)
            tension_score = (tension_score + divergence) / 2

        # Determine zone
        if tension_score < 0.3:
            zone = TensionZone.ECHO_CHAMBER
            note = f"張力值 {tension_score:.2f} < 0.3，觀點過於一致，缺乏摩擦"
        elif tension_score > 0.7:
            zone = TensionZone.CHAOS
            note = f"張力值 {tension_score:.2f} > 0.7，觀點嚴重分歧，需要冷卻"
        else:
            zone = TensionZone.SWEET_SPOT
            note = f"張力值 {tension_score:.2f} 在 0.3-0.7 區間，良性摩擦中"

        return zone, note


def create_semantic_gravity(track_record: Optional[PersonaTrackRecord] = None) -> SemanticGravity:
    """Factory function."""
    return SemanticGravity(track_record=track_record)
