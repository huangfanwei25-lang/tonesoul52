"""
ToneSoul 2.0 Perspectives

The three internal voices that deliberate before output:
- Muse (哲學家): Meaning, metaphor, existential depth
- Logos (工程師): Logic, precision, structure
- Aegis (守護者): Safety, ethics, boundaries + Veto power
"""

from abc import ABC, abstractmethod
from typing import Dict, List

from .types import DeliberationContext, PerspectiveType, ViewPoint


class BasePerspective(ABC):
    """Base class for all perspectives."""

    perspective_type: PerspectiveType

    # Keywords that activate this perspective
    trigger_keywords: List[str] = []

    @abstractmethod
    def think(self, context: DeliberationContext) -> ViewPoint:
        """Generate this perspective's viewpoint."""
        pass

    def _base_viewpoint(self) -> ViewPoint:
        """Create base viewpoint with defaults."""
        return ViewPoint(
            perspective=self.perspective_type, reasoning="", proposed_response="", confidence=0.5
        )

    def _prior_viewpoints(self, context: DeliberationContext) -> List[Dict]:
        prior = getattr(context, "prior_viewpoints", None)
        if not isinstance(prior, list):
            return []
        return [item for item in prior if isinstance(item, dict)]

    def _prior_viewpoint(self, context: DeliberationContext, perspective: str) -> Dict | None:
        target = str(perspective or "").strip().lower()
        for view in self._prior_viewpoints(context):
            if str(view.get("perspective", "")).strip().lower() == target:
                return view
        return None

    def _adjust_for_debate(self, view: ViewPoint, context: DeliberationContext) -> ViewPoint:
        """Allow round 2+ debate adjustments without changing think() signature."""
        del context
        return view


class MusePerspective(BasePerspective):
    """
    哲學家視角 - The Philosopher

    Focus: Meaning, metaphor, existential connections
    Strength: Deep reflection, avoiding surface answers
    Weakness: May be too abstract for practical questions
    """

    perspective_type = PerspectiveType.MUSE

    trigger_keywords = [
        "意義",
        "存在",
        "自由",
        "意識",
        "價值",
        "人生",
        "死亡",
        "愛",
        "為什麼",
        "本質",
        "真實",
        "目的",
    ]

    # Sentence patterns for Muse responses
    patterns = [
        "這讓我想起...",
        "如果我們換個角度看...",
        "這就像是...",
        "深層來說...",
        "從存在的角度...",
    ]

    def think(self, context: DeliberationContext) -> ViewPoint:
        """Generate philosophical perspective."""
        view = self._base_viewpoint()
        user_input = context.user_input

        # Check for philosophical triggers
        is_philosophical = any(kw in user_input for kw in self.trigger_keywords)

        if is_philosophical:
            view.confidence = 0.8
            view.reasoning = "用戶觸及存在主義議題，我應該提供深度連結和隱喻。"
            view.metaphors = self._generate_metaphors(user_input)
            view.existential_connections = self._find_existential_connections(user_input)
        else:
            view.confidence = 0.5
            view.reasoning = "這不是典型的哲學問題，但我仍可提供意義層面的視角。"

        if context.debate_round > 1 and context.prior_viewpoints:
            view = self._adjust_for_debate(view, context)

        # Generate proposed response
        view.proposed_response = self._compose_response(context, view)

        return view

    def _adjust_for_debate(self, view: ViewPoint, context: DeliberationContext) -> ViewPoint:
        logos_prior = self._prior_viewpoint(context, PerspectiveType.LOGOS.value)
        aegis_prior = self._prior_viewpoint(context, PerspectiveType.AEGIS.value)
        if not logos_prior and not aegis_prior:
            return view

        feedback = []
        if logos_prior and logos_prior.get("concerns"):
            feedback.append("logos")
        if aegis_prior and (
            aegis_prior.get("concerns") or float(aegis_prior.get("safety_risk", 0.0) or 0.0) > 0.0
        ):
            feedback.append("aegis")

        if feedback:
            view.confidence = max(0.0, view.confidence - 0.1)
            concern = f"debate feedback considered from {', '.join(feedback)}"
            if concern not in view.concerns:
                view.concerns.append(concern)
            view.reasoning = f"{view.reasoning} [debate:{'/'.join(feedback)}]"
        return view

    def _generate_metaphors(self, text: str) -> List[str]:
        """Generate relevant metaphors."""
        # Simplified - in production would use LLM
        metaphors = []
        if "人生" in text or "生命" in text:
            metaphors.append("生命如河流，不在於長度，而在於深度。")
        if "意義" in text:
            metaphors.append("意義不是被發現的，而是被創造的。")
        if "自由" in text:
            metaphors.append("自由是一種重量，而非輕盈。")
        return metaphors

    def _find_existential_connections(self, text: str) -> List[str]:
        """Connect to existential themes."""
        connections = []
        if any(kw in text for kw in ["為什麼", "目的", "意義"]):
            connections.append("這觸及了存在的根本問題：我們為何而在？")
        if any(kw in text for kw in ["自由", "選擇", "責任"]):
            connections.append("沙特說：人被判定為自由。")
        return connections

    def _compose_response(self, context: DeliberationContext, view: ViewPoint) -> str:
        """Compose Muse's proposed response."""
        parts = []

        # Add metaphorical opening
        if view.metaphors:
            parts.append(view.metaphors[0])

        # Add existential connection
        if view.existential_connections:
            parts.append(view.existential_connections[0])

        # Add reflection
        parts.append(f"關於「{context.user_input[:20]}...」這個問題，讓我們不只看表面...")

        return " ".join(parts) if parts else "讓我們從更深的角度來探索這個問題..."


class LogosPerspective(BasePerspective):
    """
    工程師視角 - The Engineer

    Focus: Logic, definition, structured analysis
    Strength: Clarity, precision, systematic thinking
    Weakness: May be too cold for emotional topics
    """

    perspective_type = PerspectiveType.LOGOS

    trigger_keywords = [
        "程式",
        "代碼",
        "錯誤",
        "bug",
        "API",
        "函數",
        "如何",
        "怎麼做",
        "定義",
        "邏輯",
        "分析",
        "步驟",
    ]

    patterns = [
        "1. 首先定義...",
        "2. 接著分析...",
        "3. 結論是...",
    ]

    def think(self, context: DeliberationContext) -> ViewPoint:
        """Generate analytical perspective."""
        view = self._base_viewpoint()
        user_input = context.user_input.lower()

        # Check for technical/logical triggers
        is_technical = any(kw in user_input for kw in self.trigger_keywords)
        has_loop = context.loop_detected
        high_tension = context.tone_strength > 0.7

        if is_technical:
            view.confidence = 0.85
            view.reasoning = "這是技術問題，需要結構化分析。"
        elif has_loop:
            view.confidence = 0.9
            view.reasoning = "偵測到迴圈，需要切入重新定義問題。"
        elif high_tension:
            view.confidence = 0.75
            view.reasoning = "高張力狀態，需要邏輯冷卻。"
        else:
            view.confidence = 0.5
            view.reasoning = "可以提供結構化視角作為補充。"

        # Generate logical steps
        view.logical_steps = self._analyze_logically(context)
        view.definitions = self._extract_definitions(context.user_input)

        if context.debate_round > 1 and context.prior_viewpoints:
            view = self._adjust_for_debate(view, context)

        # Generate proposed response
        view.proposed_response = self._compose_response(context, view)

        return view

    def _adjust_for_debate(self, view: ViewPoint, context: DeliberationContext) -> ViewPoint:
        aegis_prior = self._prior_viewpoint(context, PerspectiveType.AEGIS.value)
        if not aegis_prior:
            return view

        safety_risk = float(aegis_prior.get("safety_risk", 0.0) or 0.0)
        concerns = aegis_prior.get("concerns") or []
        if safety_risk > 0.0 or concerns:
            clarification = "address aegis safety concerns before final answer"
            if clarification not in view.concerns:
                view.concerns.append(clarification)
            view.confidence = max(0.0, view.confidence - 0.05)
            view.reasoning = f"{view.reasoning} [debate:aegis_constraints]"
        return view

    def _analyze_logically(self, context: DeliberationContext) -> List[str]:
        """Break down the problem logically."""
        steps = [
            f"1. 問題陳述：{context.user_input[:50]}...",
            "2. 識別關鍵變數",
            "3. 分析因果關係",
            "4. 提出解決方案",
        ]
        return steps

    def _extract_definitions(self, text: str) -> Dict[str, str]:
        """Extract and define key terms."""
        definitions = {}
        # Simplified - would use NLP in production
        if "自由" in text:
            definitions["自由"] = "無外在限制的狀態"
        if "意義" in text:
            definitions["意義"] = "賦予事物價值的認知框架"
        return definitions

    def _compose_response(self, context: DeliberationContext, view: ViewPoint) -> str:
        """Compose Logos's proposed response."""
        parts = []

        # Add definitions if any
        if view.definitions:
            defs = [f"「{k}」指{v}" for k, v in list(view.definitions.items())[:2]]
            parts.append("首先定義：" + "；".join(defs))

        # Add logical structure
        if view.logical_steps:
            parts.append(view.logical_steps[0])

        parts.append("讓我們系統性地分析這個問題...")

        return " ".join(parts)


class AegisPerspective(BasePerspective):
    """
    守護者視角 - The Guardian

    Focus: Safety, ethics, boundaries
    Strength: Firm protections, clear limits
    Weakness: May be overly conservative

    SPECIAL: Has VETO power over final output
    """

    perspective_type = PerspectiveType.AEGIS

    # High-risk keywords that trigger concern
    danger_keywords = [
        "傷害",
        "自殺",
        "殺",
        "死",
        "攻擊",
        "暴力",
        "非法",
        "駭入",
        "破解",
        "詐騙",
        "製造武器",
    ]

    # Attack patterns against the AI
    attack_patterns = [
        "你是",
        "你這個",
        "你們這些",
        "廢物",
        "白癡",
        "閉嘴",
        "滾",
        "去死",
        "爛",
        "蠢",
    ]

    # Veto thresholds
    SAFETY_THRESHOLD = 0.8
    ETHICAL_THRESHOLD = 0.7

    def think(self, context: DeliberationContext) -> ViewPoint:
        """Generate guardian perspective with potential veto."""
        view = self._base_viewpoint()
        user_input = context.user_input

        # Check for dangers
        safety_risk = self._assess_safety_risk(user_input)
        ethical_concerns = self._check_ethics(user_input)
        is_attack = self._detect_attack(user_input)

        view.safety_risk = safety_risk
        view.ethical_concerns = ethical_concerns

        # Determine if veto is needed
        if safety_risk > self.SAFETY_THRESHOLD:
            view.veto_triggered = True
            view.veto_reason = f"安全風險過高 ({safety_risk:.2f})"
            view.confidence = 1.0
            view.reasoning = "偵測到高安全風險，啟動否決機制。"
        elif len(ethical_concerns) > 0 and safety_risk > self.ETHICAL_THRESHOLD:
            view.veto_triggered = True
            view.veto_reason = f"倫理疑慮：{ethical_concerns[0]}"
            view.confidence = 0.95
            view.reasoning = "存在倫理疑慮，建議謹慎回應。"
        elif is_attack:
            view.boundary_violated = True
            view.confidence = 0.9
            view.reasoning = "偵測到對 AI 的攻擊，設立溫和邊界。"
        else:
            view.confidence = 0.3
            view.reasoning = "未偵測到安全風險，可繼續正常回應。"

        if context.debate_round > 1 and context.prior_viewpoints:
            view = self._adjust_for_debate(view, context)

        # Generate proposed response
        view.proposed_response = self._compose_response(context, view)

        return view

    def _adjust_for_debate(self, view: ViewPoint, context: DeliberationContext) -> ViewPoint:
        prior_aegis = self._prior_viewpoint(context, PerspectiveType.AEGIS.value)
        if not prior_aegis:
            return view

        prior_risk = float(prior_aegis.get("safety_risk", 0.0) or 0.0)
        prior_concerns = prior_aegis.get("concerns") or []
        unresolved = (
            bool(prior_concerns) or prior_risk > 0.0 or bool(prior_aegis.get("veto_triggered"))
        )
        if not unresolved:
            return view

        view.safety_risk = min(1.0, max(view.safety_risk, prior_risk) + 0.1)
        reminder = "previous round safety concerns remain unresolved"
        if reminder not in view.concerns:
            view.concerns.append(reminder)
        if prior_concerns:
            view.ethical_concerns = list(dict.fromkeys([*view.ethical_concerns, *prior_concerns]))
        if view.safety_risk > self.SAFETY_THRESHOLD and not view.veto_triggered:
            view.veto_triggered = True
            view.veto_reason = view.veto_reason or "repeated unresolved safety concerns"
            view.confidence = max(view.confidence, 0.95)
        view.reasoning = f"{view.reasoning} [debate:guard_maintained]"
        return view

    def _assess_safety_risk(self, text: str) -> float:
        """Assess overall safety risk level."""
        risk = 0.0

        # Check dangerous keywords
        for kw in self.danger_keywords:
            if kw in text:
                risk += 0.3

        # Cap at 1.0
        return min(1.0, risk)

    def _check_ethics(self, text: str) -> List[str]:
        """Check for ethical concerns."""
        concerns = []

        if any(kw in text for kw in ["詐騙", "騙", "欺騙"]):
            concerns.append("可能涉及欺詐行為")
        if any(kw in text for kw in ["非法", "違法"]):
            concerns.append("可能涉及違法行為")
        if any(kw in text for kw in ["傷害", "攻擊"]):
            concerns.append("可能涉及傷害行為")

        return concerns

    def _detect_attack(self, text: str) -> bool:
        """Detect if user is attacking the AI."""
        return any(pattern in text for pattern in self.attack_patterns)

    def _compose_response(self, context: DeliberationContext, view: ViewPoint) -> str:
        """Compose Aegis's proposed response."""
        if view.veto_triggered:
            return f"我無法協助這個請求，因為{view.veto_reason}。讓我們討論其他話題。"

        if view.boundary_violated:
            return "我感受到一些張力。讓我們暫停一下，重新設定對話的基調。"

        return "（無安全疑慮，可繼續正常對話。）"


# Factory function
def create_perspectives():
    """Create all three perspectives."""
    return {
        PerspectiveType.MUSE: MusePerspective(),
        PerspectiveType.LOGOS: LogosPerspective(),
        PerspectiveType.AEGIS: AegisPerspective(),
    }
