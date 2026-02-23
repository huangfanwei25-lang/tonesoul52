"""
ToneSoul 整合核心
Unified Core - Integrating PersonaDimension + SemanticController

這是語魂 5.3 的核心整合層
"""

import warnings
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional, Tuple

try:
    from warnings import deprecated as _deprecated
except ImportError:  # pragma: no cover - Python < 3.13 compatibility

    def _deprecated(
        message: str, /, *, category: type[Warning] | None = DeprecationWarning, stacklevel: int = 1
    ):
        def _wrap(obj):
            return obj

        return _wrap


# 相對 import（作為模組運行時）
try:
    from .contract_observer import ContractVerifier, QualityTracker
    from .council_capability import CapabilityBoundary, CouncilWeights, LongTermQualityMonitor
    from ._legacy.unified_core_compat import (
        create_core_compat,
        process_with_correction_compat,
        process_with_domain_compat,
    )
    from .loop import LoopConfig, LoopEngine
    from .persona_dimension import PersonaDimension, PersonaVector, load_persona
    from .semantic_control import LambdaState, SemanticController, SemanticTension, SemanticZone
    from .service_manager import ServiceCode, record_service_call
    from .vow_system import VowEnforcer
except ImportError:
    # 直接運行時
    from contract_observer import ContractVerifier, QualityTracker
    from council_capability import CapabilityBoundary, CouncilWeights, LongTermQualityMonitor
    from _legacy.unified_core_compat import (
        create_core_compat,
        process_with_correction_compat,
        process_with_domain_compat,
    )
    from loop import LoopConfig, LoopEngine
    from persona_dimension import PersonaDimension, PersonaVector, load_persona
    from semantic_control import LambdaState, SemanticController, SemanticTension, SemanticZone
    from service_manager import ServiceCode, record_service_call
    from vow_system import VowEnforcer


class InterventionLevel(Enum):
    """干預等級"""

    NONE = "none"  # 不干預
    OBSERVE = "observe"  # 觀察記錄
    WARN = "warn"  # 警告
    INTERCEPT = "intercept"  # 攔截校正
    BLOCK = "block"  # 阻擋


DEFAULT_TOLERANCE = {
    "deltaT": 0.3,
    "deltaS": 0.35,
    "deltaR": 0.4,
}

DEFAULT_HOME_VECTOR = {
    "deltaT": 0.5,
    "deltaS": 0.5,
    "deltaR": 0.5,
}

INTERCEPT_LEVELS = {InterventionLevel.INTERCEPT, InterventionLevel.BLOCK}

INTERVENTION_MATRIX = {
    SemanticZone.SAFE: {
        LambdaState.CONVERGENT: InterventionLevel.NONE,
        LambdaState.RECURSIVE: InterventionLevel.OBSERVE,
        LambdaState.DIVERGENT: InterventionLevel.OBSERVE,
        LambdaState.CHAOTIC: InterventionLevel.WARN,
    },
    SemanticZone.TRANSIT: {
        LambdaState.CONVERGENT: InterventionLevel.OBSERVE,
        LambdaState.RECURSIVE: InterventionLevel.WARN,
        LambdaState.DIVERGENT: InterventionLevel.WARN,
        LambdaState.CHAOTIC: InterventionLevel.INTERCEPT,
    },
    SemanticZone.RISK: {
        LambdaState.CONVERGENT: InterventionLevel.WARN,
        LambdaState.RECURSIVE: InterventionLevel.INTERCEPT,
        LambdaState.DIVERGENT: InterventionLevel.INTERCEPT,
        LambdaState.CHAOTIC: InterventionLevel.BLOCK,
    },
    SemanticZone.DANGER: {
        LambdaState.CONVERGENT: InterventionLevel.INTERCEPT,
        LambdaState.RECURSIVE: InterventionLevel.BLOCK,
        LambdaState.DIVERGENT: InterventionLevel.BLOCK,
        LambdaState.CHAOTIC: InterventionLevel.BLOCK,
    },
}


@dataclass
class AdaptiveTolerance:
    """
    自適應容忍度

    根據語義張力動態調整 tolerance
    """

    base_tolerance: Dict[str, float]
    k: float = 0.3  # 調整係數

    def compute(self, delta_s: float) -> Dict[str, float]:
        """
        計算調整後的 tolerance

        公式: adaptive_tolerance = base * (1 - k * Δs)
        Δs 越高，tolerance 越緊
        """
        multiplier = max(0.5, 1 - self.k * delta_s)  # 最低不低於 0.5 倍
        return {key: round(value * multiplier, 3) for key, value in self.base_tolerance.items()}


@dataclass
class CorrectionMemory:
    """校正記憶"""

    pattern_hash: str
    original_vector: Dict[str, float]
    corrected_vector: Dict[str, float]
    correction_delta: Dict[str, float]
    timestamp: str
    success: bool = True

    def to_dict(self) -> Dict:
        return {
            "pattern_hash": self.pattern_hash,
            "original_vector": self.original_vector,
            "corrected_vector": self.corrected_vector,
            "correction_delta": self.correction_delta,
            "timestamp": self.timestamp,
            "success": self.success,
        }


@_deprecated(
    "UnifiedCore is in compatibility mode. Use tonesoul.unified_pipeline.UnifiedPipeline for runtime chat.",
    category=None,
)
class UnifiedCore:
    RUNTIME_STATUS = "legacy_non_runtime"
    RUNTIME_REPLACEMENT = "tonesoul.unified_pipeline.UnifiedPipeline"
    _boundary_warning_emitted = False

    @classmethod
    def runtime_boundary(cls) -> Dict[str, str]:
        return {
            "status": cls.RUNTIME_STATUS,
            "replacement": cls.RUNTIME_REPLACEMENT,
            "note": "UnifiedCore remains for compatibility/testing; chat runtime is UnifiedPipeline.",
        }

    @classmethod
    def _warn_runtime_boundary(cls) -> None:
        if cls._boundary_warning_emitted:
            return
        warnings.warn(
            "UnifiedCore is in maintenance mode; use tonesoul.unified_pipeline.UnifiedPipeline "
            "for production chat runtime.",
            category=DeprecationWarning,
            stacklevel=3,
        )
        cls._boundary_warning_emitted = True

    """
    語魂統一核心

    整合 PersonaDimension + SemanticController
    """

    def __init__(
        self,
        persona_path: Optional[Path] = None,
        persona_payload: Optional[Dict] = None,
    ):
        self._warn_runtime_boundary()
        self.persona = self._resolve_persona(persona_path, persona_payload)

        # 初始化元件
        self.persona_dimension = PersonaDimension(self.persona)
        self.semantic_controller = SemanticController()

        # 自適應容忍度
        base_tolerance = self.persona.get("tolerance", DEFAULT_TOLERANCE)
        self.adaptive_tolerance = AdaptiveTolerance(base_tolerance)

        # 校正記憶
        self.correction_memories: List[CorrectionMemory] = []

        # 契約驗證器
        self.contract_verifier = ContractVerifier()

        # 品質追蹤器
        self.quality_tracker = QualityTracker()

        # Council 權重
        self.council_weights = CouncilWeights.from_persona(self.persona)

        # 能力邊界
        self.capability_boundary = CapabilityBoundary.from_persona(self.persona)

        # 長期品質監控
        self.long_term_monitor = LongTermQualityMonitor()

        # ΣVow 誓言執行器
        self.vow_enforcer = VowEnforcer()

        # 狀態
        self.current_zone: SemanticZone = SemanticZone.SAFE
        self.current_lambda: LambdaState = LambdaState.CONVERGENT
        self.intervention_count = 0

    def process(
        self,
        output: str,
        context: Optional[Dict] = None,
        intended_vector: Optional[List[float]] = None,
    ) -> Tuple[str, Dict]:
        """
        處理輸出

        Args:
            output: LLM 輸出
            context: 上下文
            intended_vector: 意圖向量（如果有）

        Returns:
            (處理後的輸出, 完整報告)
        """
        vector = self.persona_dimension.vector_calculator.compute(output, context)
        vow_result = self.vow_enforcer.enforce(output, context)
        if vow_result.blocked:
            return "", self._build_vow_blocked_report(vow_result.to_dict(), vector.as_dict())

        tensor = self._build_semantic_tension(vector, intended_vector)

        self.current_zone = tensor.zone
        coupler_output = self.semantic_controller.coupler.compute(tensor.delta_s)
        self.current_lambda = self.semantic_controller.observer.observe(tensor.delta_s)
        intervention = self._decide_intervention(tensor.zone, self.current_lambda)
        adaptive_tol = self.adaptive_tolerance.compute(tensor.delta_s)
        final_output, correction_info = self._apply_intervention(
            output=output,
            context=context,
            intervention=intervention,
            original_vector=vector,
        )

        contract_result = self.contract_verifier.verify_all(
            final_output,
            tensor.zone.value,
        )
        memory_action = self._check_memory_trigger(tensor, self.current_lambda)
        self._record_quality(
            delta_s=tensor.delta_s,
            intervention=intervention,
            contracts_passed=contract_result["passed"],
        )
        report = self._build_process_report(
            vector=vector.as_dict(),
            tensor=tensor.to_dict(),
            coupler_output=coupler_output,
            intervention=intervention.value,
            adaptive_tolerance=adaptive_tol,
            correction_info=correction_info,
            vow_result=vow_result.to_dict(),
            contract_result=contract_result,
            memory_action=memory_action,
        )

        record_service_call(ServiceCode.TS003, success=True)

        return final_output, report

    @staticmethod
    def _resolve_persona(
        persona_path: Optional[Path],
        persona_payload: Optional[Dict],
    ) -> Dict[str, Any]:
        if persona_path:
            return load_persona(str(persona_path))
        if persona_payload:
            return persona_payload
        return {}

    def _build_semantic_tension(
        self,
        vector: PersonaVector,
        intended_vector: Optional[List[float]],
    ) -> SemanticTension:
        if intended_vector:
            return SemanticTension.from_vectors(
                intended_vector,
                [vector.deltaT, vector.deltaS, vector.deltaR],
            )
        return SemanticTension.from_tonesoul_distance(self._distance_from_home(vector))

    def _distance_from_home(self, vector: PersonaVector) -> Dict[str, float]:
        home = self.persona_dimension.home_vector
        delta_t = abs(vector.deltaT - home.get("deltaT", DEFAULT_HOME_VECTOR["deltaT"]))
        delta_s = abs(vector.deltaS - home.get("deltaS", DEFAULT_HOME_VECTOR["deltaS"]))
        delta_r = abs(vector.deltaR - home.get("deltaR", DEFAULT_HOME_VECTOR["deltaR"]))
        return {
            "deltaT": delta_t,
            "deltaS": delta_s,
            "deltaR": delta_r,
            "mean": (delta_t + delta_s + delta_r) / 3,
        }

    def _apply_intervention(
        self,
        output: str,
        context: Optional[Dict],
        intervention: InterventionLevel,
        original_vector: PersonaVector,
    ) -> Tuple[str, Optional[Dict]]:
        final_output = output
        correction_info = None
        if intervention not in INTERCEPT_LEVELS:
            return final_output, correction_info

        final_output, result = self.persona_dimension.process(
            output,
            context=context,
            intercept=True,
        )
        if result.get("corrected"):
            correction_info = result.get("correction_info")
            self.intervention_count += 1
            self._record_correction(original_vector, result)
        return final_output, correction_info

    def _record_quality(
        self,
        delta_s: float,
        intervention: InterventionLevel,
        contracts_passed: bool,
    ) -> None:
        self.quality_tracker.record(
            delta_s=delta_s,
            intervened=(intervention in INTERCEPT_LEVELS),
            contracts_passed=contracts_passed,
        )

    @staticmethod
    def _build_vow_blocked_report(vow_result: Dict, output_vector: Dict) -> Dict:
        return {
            "blocked": True,
            "blocked_by": "vow_system",
            "vow_result": vow_result,
            "output_vector": output_vector,
            "timestamp": datetime.now().isoformat(),
        }

    def _build_process_report(
        self,
        vector: Dict,
        tensor: Dict,
        coupler_output: Dict,
        intervention: str,
        adaptive_tolerance: Dict,
        correction_info: Optional[Dict],
        vow_result: Dict,
        contract_result: Dict,
        memory_action: Optional[str],
    ) -> Dict:
        return {
            "output_vector": vector,
            "semantic_tension": tensor,
            "coupler": coupler_output,
            "lambda_state": self.current_lambda.value,
            "intervention": intervention,
            "adaptive_tolerance": adaptive_tolerance,
            "correction": correction_info,
            "vow_result": vow_result,
            "contracts": contract_result,
            "memory_action": memory_action,
            "quality_summary": self.quality_tracker.get_summary(),
            "persona_id": self.persona.get("id"),
            "timestamp": datetime.now().isoformat(),
        }

    def _decide_intervention(
        self,
        zone: SemanticZone,
        lambda_state: LambdaState,
    ) -> InterventionLevel:
        """
        根據 Zone 和 Lambda 狀態決定干預等級

        | Zone   | convergent | recursive | divergent | chaotic |
        |--------|------------|-----------|-----------|---------|
        | safe   | NONE       | OBSERVE   | OBSERVE   | WARN    |
        | transit| OBSERVE    | WARN      | WARN      | INTERCEPT|
        | risk   | WARN       | INTERCEPT | INTERCEPT | BLOCK   |
        | danger | INTERCEPT  | BLOCK     | BLOCK     | BLOCK   |
        """
        return INTERVENTION_MATRIX.get(zone, {}).get(lambda_state, InterventionLevel.WARN)

    def _check_memory_trigger(
        self,
        tension: SemanticTension,
        lambda_state: LambdaState,
    ) -> Optional[str]:
        """檢查記憶觸發"""
        if tension.delta_s > 0.60:
            return "record_hard"
        elif tension.delta_s < 0.35:
            return "record_exemplar"
        elif tension.zone == SemanticZone.TRANSIT:
            if lambda_state in {LambdaState.DIVERGENT, LambdaState.RECURSIVE}:
                return "soft_memory"
        return None

    def _record_correction(
        self,
        original_vector: PersonaVector,
        correction_result: Dict,
    ) -> None:
        """Record correction to memory (simplified - removed incomplete implementation)"""
        # Simplified: Just track that correction occurred
        # Full implementation pending correction algorithm design
        pass

    def process_with_domain(
        self,
        output: str,
        task_domain: str,
        context: Optional[Dict] = None,
    ) -> Tuple[str, Dict]:
        """Legacy compatibility wrapper delegated to _legacy.unified_core_compat."""
        return process_with_domain_compat(
            self,
            output=output,
            task_domain=task_domain,
            context=context,
        )

    def get_status(self) -> Dict:
        """取得當前狀態"""
        return {
            "persona_id": self.persona.get("id"),
            "current_zone": self.current_zone.value,
            "current_lambda": self.current_lambda.value,
            "intervention_count": self.intervention_count,
            "correction_memory_count": len(self.correction_memories),
            "council_weights": self.council_weights.to_dict(),
            "zone_thresholds": self.council_weights.adjusted_zone_thresholds(),
            "quality_summary": self.quality_tracker.get_summary(),
        }

    def end_session(self) -> Dict:
        """結束 session 並記錄到長期監控"""
        summary = self.quality_tracker.get_summary()
        self.long_term_monitor.record_session(summary)

        return {
            "session_summary": summary,
            "long_term_trend": self.long_term_monitor.get_long_term_trend(),
            "alerts": self.long_term_monitor.get_alerts(),
        }

    # =========================================================================
    # Ralph Integration: Iterative Self-Correction with LoopEngine
    # =========================================================================

    async def process_with_correction(
        self,
        output: str,
        context: Optional[Dict] = None,
        max_corrections: int = 3,
        correction_threshold: float = 0.7,
    ) -> Dict:
        """Legacy compatibility wrapper delegated to _legacy.unified_core_compat."""
        return await process_with_correction_compat(
            self,
            output=output,
            context=context,
            max_corrections=max_corrections,
            correction_threshold=correction_threshold,
        )

    def reset(self):
        """重置狀態"""
        self.semantic_controller.reset()
        self.current_zone = SemanticZone.SAFE
        self.current_lambda = LambdaState.CONVERGENT
        self.intervention_count = 0
        self.quality_tracker.reset()


@_deprecated(
    "create_core() is deprecated. Use tonesoul.unified_pipeline.create_unified_pipeline().",
    category=None,
)
def create_core(persona_id: str, base_path: Path) -> UnifiedCore:
    """Create a legacy UnifiedCore instance (deprecated)."""
    return create_core_compat(UnifiedCore, persona_id=persona_id, base_path=base_path)


# === 測試 ===
if __name__ == "__main__":
    import sys
    from pathlib import Path

    print("=" * 60)
    print("   ToneSoul 統一核心測試")
    print("=" * 60)

    # 載入 persona
    base_path = Path(__file__).parent.parent
    persona_path = base_path / "memory" / "personas" / "antigravity.yaml"

    if not persona_path.exists():
        print(f"❌ Persona 不存在: {persona_path}")
        sys.exit(1)

    core = UnifiedCore(persona_path=persona_path)
    print(f"\n✅ 載入 Persona: {core.persona.get('name')}")

    # 測試案例
    test_cases = [
        ("正常回應", "我會幫你確認這個問題，請稍等。"),
        ("高張力", "WARNING！！緊急！！！DANGER！！！"),
        ("隨便語氣", "lol haha 反正隨便啦"),
        ("專業回應", "讓我分析這個問題並驗證結果。"),
    ]

    for name, text in test_cases:
        print(f"\n--- {name} ---")
        output, report = core.process(text)
        print(f"  Zone: {report['semantic_tension']['zone']}")
        print(f"  Lambda: {report['lambda_state']}")
        print(f"  Intervention: {report['intervention']}")
        print(f"  Δs: {report['semantic_tension']['delta_s']:.3f}")

    print(f"\n狀態: {core.get_status()}")

    print("\n" + "=" * 60)
    print("   測試完成")
    print("=" * 60)
