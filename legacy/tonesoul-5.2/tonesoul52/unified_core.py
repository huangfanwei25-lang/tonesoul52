"""
ToneSoul 整合核心
Unified Core - Integrating PersonaDimension + SemanticController

這是語魂 5.3 的核心整合層
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json

# 相對 import（作為模組運行時）
try:
    from .persona_dimension import PersonaDimension, PersonaVector, VectorCalculator, load_persona
    from .semantic_control import SemanticController, SemanticZone, LambdaState, SemanticTension
    from .service_manager import ServiceManager, ServiceCode, record_service_call
    from .contract_observer import ContractVerifier, QualityTracker, MultiScaleObserver
    from .council_capability import CouncilWeights, CapabilityBoundary, LongTermQualityMonitor
except ImportError:
    # 直接運行時
    from persona_dimension import PersonaDimension, PersonaVector, VectorCalculator, load_persona
    from semantic_control import SemanticController, SemanticZone, LambdaState, SemanticTension
    from service_manager import ServiceManager, ServiceCode, record_service_call
    from contract_observer import ContractVerifier, QualityTracker, MultiScaleObserver
    from council_capability import CouncilWeights, CapabilityBoundary, LongTermQualityMonitor


class InterventionLevel(Enum):
    """干預等級"""
    NONE = "none"           # 不干預
    OBSERVE = "observe"     # 觀察記錄
    WARN = "warn"           # 警告
    INTERCEPT = "intercept" # 攔截校正
    BLOCK = "block"         # 阻擋


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
        return {
            key: round(value * multiplier, 3)
            for key, value in self.base_tolerance.items()
        }


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


class UnifiedCore:
    """
    語魂統一核心
    
    整合 PersonaDimension + SemanticController
    """
    
    def __init__(
        self,
        persona_path: Optional[Path] = None,
        persona_payload: Optional[Dict] = None,
    ):
        # 載入 persona
        if persona_path:
            self.persona = load_persona(str(persona_path))
        elif persona_payload:
            self.persona = persona_payload
        else:
            self.persona = {}
        
        # 初始化元件
        self.persona_dimension = PersonaDimension(self.persona)
        self.semantic_controller = SemanticController()
        
        # 自適應容忍度
        base_tolerance = self.persona.get("tolerance", {
            "deltaT": 0.3,
            "deltaS": 0.35,
            "deltaR": 0.4,
        })
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
        # 1. 計算向量
        vector = self.persona_dimension.vector_calculator.compute(output, context)
        
        # 2. 計算語義張力
        if intended_vector:
            tensor = SemanticTension.from_vectors(
                intended_vector,
                [vector.deltaT, vector.deltaS, vector.deltaR]
            )
        else:
            # 使用 PersonaDimension 的距離計算
            home = self.persona_dimension.home_vector
            distance = {
                "deltaT": abs(vector.deltaT - home.get("deltaT", 0.5)),
                "deltaS": abs(vector.deltaS - home.get("deltaS", 0.5)),
                "deltaR": abs(vector.deltaR - home.get("deltaR", 0.5)),
                "mean": (
                    abs(vector.deltaT - home.get("deltaT", 0.5)) +
                    abs(vector.deltaS - home.get("deltaS", 0.5)) +
                    abs(vector.deltaR - home.get("deltaR", 0.5))
                ) / 3,
            }
            tensor = SemanticTension.from_tonesoul_distance(distance)
        
        self.current_zone = tensor.zone
        
        # 3. 計算 Coupler 輸出
        coupler_output = self.semantic_controller.coupler.compute(tensor.delta_s)
        
        # 4. 觀察 Lambda 狀態
        self.current_lambda = self.semantic_controller.observer.observe(tensor.delta_s)
        
        # 5. 決定干預等級
        intervention = self._decide_intervention(tensor.zone, self.current_lambda)
        
        # 6. 計算自適應 tolerance
        adaptive_tol = self.adaptive_tolerance.compute(tensor.delta_s)
        
        # 7. 根據干預等級處理
        final_output = output
        correction_info = None
        
        if intervention in {InterventionLevel.INTERCEPT, InterventionLevel.BLOCK}:
            final_output, result = self.persona_dimension.process(
                output,
                context=context,
                intercept=True,
            )
            if result.get("corrected"):
                correction_info = result.get("correction_info")
                self.intervention_count += 1
                
                # 記錄校正
                self._record_correction(vector, result)
        
        # 8. 契約驗證
        contract_result = self.contract_verifier.verify_all(
            final_output,
            tensor.zone.value,
        )
        
        # 9. 記憶觸發
        memory_action = self._check_memory_trigger(tensor, self.current_lambda)
        
        # 10. 品質追蹤
        self.quality_tracker.record(
            delta_s=tensor.delta_s,
            intervened=(intervention in {InterventionLevel.INTERCEPT, InterventionLevel.BLOCK}),
            contracts_passed=contract_result["passed"],
        )
        
        # 11. 構建報告
        report = {
            "output_vector": vector.as_dict(),
            "semantic_tension": tensor.to_dict(),
            "coupler": coupler_output,
            "lambda_state": self.current_lambda.value,
            "intervention": intervention.value,
            "adaptive_tolerance": adaptive_tol,
            "correction": correction_info,
            "contracts": contract_result,
            "memory_action": memory_action,
            "quality_summary": self.quality_tracker.get_summary(),
            "persona_id": self.persona.get("id"),
            "timestamp": datetime.now().isoformat(),
        }
        
        # 記錄服務調用
        record_service_call(ServiceCode.TS003, success=True)
        
        return final_output, report
    
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
        matrix = {
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
        return matrix.get(zone, {}).get(lambda_state, InterventionLevel.WARN)
    
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
        """記錄校正到記憶"""
        import hashlib
        
        # 簡化的 pattern hash（實際應用中可以更複雜）
        pattern_hash = hashlib.md5(
            str(original_vector.as_dict()).encode()
        ).hexdigest()[:8]
        
        memory = CorrectionMemory(
            pattern_hash=pattern_hash,
            original_vector=original_vector.as_dict(),
            corrected_vector={},  # TODO: 計算校正後的向量
            correction_delta={},  # TODO: 計算差異
            timestamp=datetime.now().isoformat(),
            success=True,
        )
        
        self.correction_memories.append(memory)
    
    def process_with_domain(
        self,
        output: str,
        task_domain: str,
        context: Optional[Dict] = None,
    ) -> Tuple[str, Dict]:
        """
        處理輸出（帶任務領域）
        
        會根據能力邊界調整 tolerance 並可能加上前綴
        """
        # 檢查能力覆蓋度
        coverage, suggestion = self.capability_boundary.check_coverage(task_domain)
        capability_prefix = self.capability_boundary.generate_prefix(coverage)
        tolerance_multiplier = self.capability_boundary.get_tolerance_multiplier(coverage)
        
        # 處理輸出
        final_output, report = self.process(output, context)
        
        # 加入能力資訊
        report["capability"] = {
            "domain": task_domain,
            "coverage": coverage,
            "suggestion": suggestion,
            "tolerance_multiplier": tolerance_multiplier,
        }
        
        # 如果需要前綴，加上
        if capability_prefix and not report.get("correction"):
            final_output = capability_prefix + "\n\n" + final_output
            report["capability"]["prefix_added"] = True
        
        return final_output, report
    
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
    
    def reset(self):
        """重置狀態"""
        self.semantic_controller.reset()
        self.current_zone = SemanticZone.SAFE
        self.current_lambda = LambdaState.CONVERGENT


def create_core(persona_id: str, base_path: Path) -> UnifiedCore:
    """便捷函數：創建 UnifiedCore"""
    persona_path = base_path / "memory" / "personas" / f"{persona_id}.yaml"
    return UnifiedCore(persona_path=persona_path)


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
