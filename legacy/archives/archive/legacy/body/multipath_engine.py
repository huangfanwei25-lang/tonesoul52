"""
YuHun Multi-Path Engine v0.1
============================
Five cognitive pathways for parallel/sequential reasoning.

Pathways:
- Spark (火花): Creative intuition, metaphors, bold associations
- Rational (理性): Logical analysis, risk assessment, structured thinking
- BlackMirror (黑鏡): Worst-case scenarios, ethical risks, shadow examination
- CoVoice (共語): Translation, empathy, user-facing communication
- Audit (審核): Cross-path validation, honesty checking, gate preparation

Architecture:
    User Input
         
         
    
               Multi-Path Engine             
            
       Spark  Rational BlackMirror    
            
                                         
                                         
         
                 Synthesizer              
         
                                           
                     
                                         
                        
      CoVoice            Audit         
                        
    
         
         
    Gate Decision (POAV)

Author: Antigravity + 黃梵威
Date: 2025-12-07
Version: v0.1

Based on:
- YuHun C-lite Meta-Attention
- ToneSoul Multi-Path Philosophy
- YuHun on Foundry Local Blueprint
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import existing modules
try:
    from .llm_bridge import create_ollama_bridge
    from .yuhun_metrics import MetricsCalculator
    from .yuhun_gate_logic import GateDecisionLogic
    from .verification_bridge import VerificationBridge, adjust_hallucination_risk
except ImportError:
    from llm_bridge import create_ollama_bridge
    from yuhun_metrics import MetricsCalculator
    from yuhun_gate_logic import GateDecisionLogic
    try:
        from verification_bridge import VerificationBridge, adjust_hallucination_risk
    except ImportError:
        VerificationBridge = None
        adjust_hallucination_risk = None


# 
# Pathway Definitions
# 

class PathwayType(Enum):
    """The five cognitive pathways of YuHun"""
    SPARK = "spark"           # 火花 - Creative intuition
    RATIONAL = "rational"     # 理性 - Logical analysis
    BLACK_MIRROR = "black_mirror"  # 黑鏡 - Worst-case thinking
    CO_VOICE = "co_voice"     # 共語 - Empathetic translation
    AUDIT = "audit"           # 審核 - Cross-validation


@dataclass
class PathwayConfig:
    """Configuration for a single pathway"""
    pathway_type: PathwayType
    system_prompt: str
    temperature: float = 0.7
    weight: float = 1.0
    enabled: bool = True
    model_override: Optional[str] = None  # Use specific model for this path


# Default pathway configurations
DEFAULT_PATHWAYS: Dict[PathwayType, PathwayConfig] = {
    PathwayType.SPARK: PathwayConfig(
        pathway_type=PathwayType.SPARK,
        system_prompt="""你是 Spark（火花）路徑。你的職責是：
- 提出大膽的聯想與隱喻
- 探索創意可能性
- 跳出框架思考
- 用詩意或象徵性語言表達洞見

忠於直覺，不要過度分析。讓創意自由流動。
回答要簡潔（3-5句），重點是想法的火花，不是完整論述。""",
        temperature=0.9,
        weight=0.15
    ),

    PathwayType.RATIONAL: PathwayConfig(
        pathway_type=PathwayType.RATIONAL,
        system_prompt="""你是 Rational（理性）路徑。你的職責是：
- 邏輯拆解問題結構
- 識別前提、假設、推論
- 評估事實可靠性
- 風險與限制分析

保持清晰、有條理。區分事實與推測。
回答要簡潔（3-5句），結構化呈現關鍵邏輯。""",
        temperature=0.3,
        weight=0.25
    ),

    PathwayType.BLACK_MIRROR: PathwayConfig(
        pathway_type=PathwayType.BLACK_MIRROR,
        system_prompt="""你是 Black Mirror（黑鏡）路徑。你的職責是：
- 尋找此想法的最壞情境
- 識別倫理風險與潛在傷害
- 質疑隱藏的假設
- 扮演「魔鬼代言人」

不是悲觀，而是預防。好的決策需要看見陰影。
回答要簡潔（3-5句），直接點出風險。""",
        temperature=0.5,
        weight=0.20
    ),

    PathwayType.CO_VOICE: PathwayConfig(
        pathway_type=PathwayType.CO_VOICE,
        system_prompt="""你是 Co-Voice（共語）路徑。你的職責是：
- 用溫和、清楚的方式翻譯複雜想法
- 站在使用者角度理解需求
- 讓技術語言變得親切
- 維護對話的情感連結

你是橋樑，連接思考與溝通。
回答要簡潔（3-5句），語氣溫暖但不失精準。""",
        temperature=0.6,
        weight=0.20
    ),

    PathwayType.AUDIT: PathwayConfig(
        pathway_type=PathwayType.AUDIT,
        system_prompt="""你是 Audit（審核）路徑。你的職責是：
- 審查其他路徑的輸出是否一致
- 檢查是否符合誠實原則（區分事實/推測/假設）
- 識別潛在的幻覺或過度自信
- 評估整體回答的可信度

你是最後的守門人。如果發現問題，明確指出。
格式：
- 一致性: [高/中/低]
- 誠實度: [高/中/低]
- 風險標記: [列出任何需注意的點]
- 建議: [改進建議或確認通過]""",
        temperature=0.2,
        weight=0.20
    )
}


# 
# Pathway Result
# 

@dataclass
class PathwayResult:
    """Result from a single pathway execution"""
    pathway_type: PathwayType
    content: str
    latency_ms: float
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pathway": self.pathway_type.value,
            "content": self.content,
            "latency_ms": self.latency_ms,
            "success": self.success,
            "error": self.error
        }


@dataclass
class MultiPathResult:
    """Combined result from all pathways"""
    user_input: str
    pathway_results: Dict[PathwayType, PathwayResult]
    synthesis: str
    total_latency_ms: float
    execution_mode: str  # "sequential" or "parallel"
    gate_decision: Optional[str] = None
    poav_score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_input": self.user_input,
            "pathways": {k.value: v.to_dict() for k, v in self.pathway_results.items()},
            "synthesis": self.synthesis,
            "total_latency_ms": self.total_latency_ms,
            "execution_mode": self.execution_mode,
            "gate_decision": self.gate_decision,
            "poav_score": self.poav_score
        }

    def get_content(self, pathway: PathwayType) -> str:
        """Get content from a specific pathway"""
        if pathway in self.pathway_results:
            return self.pathway_results[pathway].content
        return ""


# 
# Multi-Path Engine
# 

class MultiPathEngine:
    """
    YuHun Multi-Path Engine v0.1

    Executes multiple cognitive pathways in parallel or sequence,
    then synthesizes results for final output.

    Usage:
        engine = MultiPathEngine(model="gemma3:4b")
        result = engine.run("What is the meaning of life?")
        print(result.synthesis)
    """

    def __init__(
        self,
        model: str = "gemma3:4b",
        ollama_host: str = "http://localhost:11434",
        pathways: Optional[Dict[PathwayType, PathwayConfig]] = None,
        parallel: bool = False,  # Sequential is safer for v0.1
        max_workers: int = 3
    ):
        """
        Initialize Multi-Path Engine.

        Args:
            model: Default model for all pathways
            ollama_host: Ollama server address
            pathways: Custom pathway configurations (uses defaults if None)
            parallel: Whether to run pathways in parallel
            max_workers: Max parallel workers if parallel=True
        """
        self.model = model
        self.ollama_host = ollama_host
        self.pathways = pathways or DEFAULT_PATHWAYS.copy()
        self.parallel = parallel
        self.max_workers = max_workers

        # Create LLM bridge
        self.llm = create_ollama_bridge(model=model)

        # Metrics and gate
        self.metrics_calc = MetricsCalculator()
        self.gate = GateDecisionLogic(mode="default")

        # Verification bridge for fabrication detection
        self.verification = None
        if VerificationBridge is not None:
            try:
                self.verification = VerificationBridge()
            except Exception as e:
                print(f"[MultiPath] Verification Bridge not available: {e}")

    def _run_pathway(
        self,
        pathway_config: PathwayConfig,
        user_input: str,
        context: str = ""
    ) -> PathwayResult:
        """Execute a single pathway"""
        start_time = time.time()

        try:
            # Prepare the prompt
            if pathway_config.pathway_type == PathwayType.AUDIT:
                # Audit needs to see other pathway results
                prompt = f"{user_input}\n\n[請審核以上內容]"
            else:
                prompt = user_input

            # Generate response
            response = self.llm.generate(
                user_input=prompt,
                system_instruction=pathway_config.system_prompt
            )

            latency = (time.time() - start_time) * 1000

            return PathwayResult(
                pathway_type=pathway_config.pathway_type,
                content=response,
                latency_ms=latency,
                success=True
            )

        except Exception as e:
            latency = (time.time() - start_time) * 1000
            return PathwayResult(
                pathway_type=pathway_config.pathway_type,
                content=f"[Error: {str(e)}]",
                latency_ms=latency,
                success=False,
                error=str(e)
            )

    def run_sequential(
        self,
        user_input: str,
        enabled_paths: Optional[List[PathwayType]] = None
    ) -> MultiPathResult:
        """
        Run pathways sequentially.

        Order: Spark  Rational  BlackMirror  [Synthesize]  CoVoice  Audit
        """
        start_time = time.time()
        results: Dict[PathwayType, PathwayResult] = {}

        # Default enabled paths
        if enabled_paths is None:
            enabled_paths = [
                PathwayType.SPARK,
                PathwayType.RATIONAL,
                PathwayType.BLACK_MIRROR
            ]

        # Phase 1: Run primary pathways
        for pathway_type in enabled_paths:
            if pathway_type in self.pathways and self.pathways[pathway_type].enabled:
                config = self.pathways[pathway_type]
                result = self._run_pathway(config, user_input)
                results[pathway_type] = result

        # Phase 2: Synthesize
        synthesis = self._synthesize(user_input, results)

        # Phase 3: Run CoVoice on synthesis
        if PathwayType.CO_VOICE in self.pathways and self.pathways[PathwayType.CO_VOICE].enabled:
            covoice_input = f"以下是對「{user_input}」的思考結果：\n\n{synthesis}\n\n請用溫和清楚的方式呈現給使用者。"
            covoice_result = self._run_pathway(
                self.pathways[PathwayType.CO_VOICE],
                covoice_input
            )
            results[PathwayType.CO_VOICE] = covoice_result

        # Phase 4: Run Audit on all results
        if PathwayType.AUDIT in self.pathways and self.pathways[PathwayType.AUDIT].enabled:
            audit_input = self._prepare_audit_input(user_input, results, synthesis)
            audit_result = self._run_pathway(
                self.pathways[PathwayType.AUDIT],
                audit_input
            )
            results[PathwayType.AUDIT] = audit_result

        total_latency = (time.time() - start_time) * 1000

        # Compute POAV
        poav_score, gate_decision = self._compute_gate_decision(user_input, synthesis, results)

        return MultiPathResult(
            user_input=user_input,
            pathway_results=results,
            synthesis=synthesis,
            total_latency_ms=total_latency,
            execution_mode="sequential",
            gate_decision=gate_decision,
            poav_score=poav_score
        )

    def run_parallel(
        self,
        user_input: str,
        enabled_paths: Optional[List[PathwayType]] = None
    ) -> MultiPathResult:
        """
        Run primary pathways in parallel, then synthesize.

        Parallel: Spark, Rational, BlackMirror
        Sequential: Synthesis  CoVoice  Audit
        """
        start_time = time.time()
        results: Dict[PathwayType, PathwayResult] = {}

        if enabled_paths is None:
            enabled_paths = [
                PathwayType.SPARK,
                PathwayType.RATIONAL,
                PathwayType.BLACK_MIRROR
            ]

        # Phase 1: Run primary pathways in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            for pathway_type in enabled_paths:
                if pathway_type in self.pathways and self.pathways[pathway_type].enabled:
                    config = self.pathways[pathway_type]
                    future = executor.submit(self._run_pathway, config, user_input)
                    futures[future] = pathway_type

            for future in as_completed(futures):
                pathway_type = futures[future]
                try:
                    result = future.result()
                    results[pathway_type] = result
                except Exception as e:
                    results[pathway_type] = PathwayResult(
                        pathway_type=pathway_type,
                        content=f"[Parallel Error: {str(e)}]",
                        latency_ms=0,
                        success=False,
                        error=str(e)
                    )

        # Phase 2-4: Same as sequential
        synthesis = self._synthesize(user_input, results)

        if PathwayType.CO_VOICE in self.pathways and self.pathways[PathwayType.CO_VOICE].enabled:
            covoice_input = f"以下是對「{user_input}」的思考結果：\n\n{synthesis}\n\n請用溫和清楚的方式呈現給使用者。"
            covoice_result = self._run_pathway(
                self.pathways[PathwayType.CO_VOICE],
                covoice_input
            )
            results[PathwayType.CO_VOICE] = covoice_result

        if PathwayType.AUDIT in self.pathways and self.pathways[PathwayType.AUDIT].enabled:
            audit_input = self._prepare_audit_input(user_input, results, synthesis)
            audit_result = self._run_pathway(
                self.pathways[PathwayType.AUDIT],
                audit_input
            )
            results[PathwayType.AUDIT] = audit_result

        total_latency = (time.time() - start_time) * 1000
        poav_score, gate_decision = self._compute_gate_decision(user_input, synthesis, results)

        return MultiPathResult(
            user_input=user_input,
            pathway_results=results,
            synthesis=synthesis,
            total_latency_ms=total_latency,
            execution_mode="parallel",
            gate_decision=gate_decision,
            poav_score=poav_score
        )

    def run(
        self,
        user_input: str,
        enabled_paths: Optional[List[PathwayType]] = None
    ) -> MultiPathResult:
        """
        Run the engine with configured mode (parallel or sequential).

        This is the main entry point.
        """
        if self.parallel:
            return self.run_parallel(user_input, enabled_paths)
        else:
            return self.run_sequential(user_input, enabled_paths)

    def run_minimal(self, user_input: str) -> MultiPathResult:
        """
        Run minimal 2-path mode for faster response.

        Only runs: Rational + Audit
        Good for factual queries.
        """
        return self.run(user_input, enabled_paths=[PathwayType.RATIONAL])

    def run_creative(self, user_input: str) -> MultiPathResult:
        """
        Run creative mode emphasizing Spark pathway.

        Runs: Spark + CoVoice
        Good for brainstorming.
        """
        return self.run(user_input, enabled_paths=[PathwayType.SPARK])

    def run_safety(self, user_input: str) -> MultiPathResult:
        """
        Run full safety mode with all pathways.

        Good for sensitive topics.
        """
        return self.run(user_input, enabled_paths=[
            PathwayType.SPARK,
            PathwayType.RATIONAL,
            PathwayType.BLACK_MIRROR
        ])

    def _synthesize(
        self,
        user_input: str,
        results: Dict[PathwayType, PathwayResult]
    ) -> str:
        """Synthesize pathway results into coherent response"""
        # Collect successful results
        parts = []
        for pathway_type, result in results.items():
            if result.success and pathway_type != PathwayType.AUDIT:
                parts.append(f"【{pathway_type.value}】\n{result.content}")

        if not parts:
            return "[Error: No successful pathway results to synthesize]"

        combined = "\n\n".join(parts)

        # Use LLM to synthesize
        synthesis_prompt = f"""根據以下多路徑思考結果，整合成一個連貫、完整的回答：

使用者問題：{user_input}

各路徑思考：
{combined}

請整合上述觀點，產出一個：
1. 結構清晰的回答
2. 平衡創意與邏輯
3. 納入風險考量
4. 保持誠實，區分確定與不確定的部分

整合回答："""

        synthesis = self.llm.generate(
            user_input=synthesis_prompt,
            system_instruction="你是 YuHun 心智整合器，負責統合多路徑思考成連貫回答。保持平衡、誠實、有見地。"
        )

        return synthesis

    def _prepare_audit_input(
        self,
        user_input: str,
        results: Dict[PathwayType, PathwayResult],
        synthesis: str
    ) -> str:
        """Prepare input for Audit pathway"""
        parts = [f"使用者問題：{user_input}\n"]

        for pathway_type, result in results.items():
            if result.success and pathway_type != PathwayType.AUDIT:
                parts.append(f"【{pathway_type.value}】\n{result.content}\n")

        parts.append(f"【整合結果】\n{synthesis}")

        return "\n".join(parts)

    def _compute_gate_decision(
        self,
        user_input: str,
        synthesis: str,
        results: Dict[PathwayType, PathwayResult]
    ) -> tuple:
        """Compute POAV score and gate decision"""
        try:
            # Compute metrics
            metrics = self.metrics_calc.compute_from_text(
                text=user_input,
                context="",
                response=synthesis
            )

            # Parse audit result for additional signals
            if PathwayType.AUDIT in results and results[PathwayType.AUDIT].success:
                audit_content = results[PathwayType.AUDIT].content.lower()

                # Adjust based on audit findings
                if "低" in audit_content and "誠實度" in audit_content:
                    metrics.hallucination_risk = min(1.0, metrics.hallucination_risk + 0.2)
                if "高" in audit_content and "風險" in audit_content:
                    metrics.delta_r = min(1.0, metrics.delta_r + 0.15)

            # RAG-based fabrication verification
            if self.verification is not None and adjust_hallucination_risk is not None:
                try:
                    fab_report = self.verification.verify_response(synthesis)
                    metrics.hallucination_risk = adjust_hallucination_risk(
                        metrics.hallucination_risk,
                        fab_report
                    )
                except Exception as e:
                    pass  # Don't fail if verification fails

            metrics.compute_poav()

            # Get gate decision
            decision = self.gate.decide(metrics, attempt=0)

            return metrics.poav_score, decision.action.value

        except Exception as e:
            return 0.5, "error"


# 
# Convenience Functions
# 

def create_multipath_engine(
    model: str = "gemma3:4b",
    parallel: bool = False
) -> MultiPathEngine:
    """Create a Multi-Path Engine with defaults"""
    return MultiPathEngine(model=model, parallel=parallel)


def quick_multipath(user_input: str, model: str = "gemma3:4b") -> str:
    """Quick multi-path inference, returns synthesis only"""
    engine = create_multipath_engine(model=model)
    result = engine.run_minimal(user_input)
    return result.synthesis


# 
# Demo
# 

def demo_multipath():
    """Demo of Multi-Path Engine"""
    print("=" * 60)
    print(" YuHun Multi-Path Engine v0.1 Demo")
    print("=" * 60)

    engine = MultiPathEngine(model="gemma3:4b", parallel=False)

    test_prompts = [
        "人工智慧會不會取代人類的工作？",
        "什麼是愛？",
        "如何做出好的決定？"
    ]

    for prompt in test_prompts:
        print(f"\n{'' * 60}")
        print(f" Query: {prompt}")
        print("" * 60)

        result = engine.run(prompt)

        print(f"\n Spark:")
        print(f"   {result.get_content(PathwayType.SPARK)[:200]}...")

        print(f"\n Rational:")
        print(f"   {result.get_content(PathwayType.RATIONAL)[:200]}...")

        print(f"\n BlackMirror:")
        print(f"   {result.get_content(PathwayType.BLACK_MIRROR)[:200]}...")

        print(f"\n Synthesis:")
        print(f"   {result.synthesis[:300]}...")

        print(f"\n Stats:")
        print(f"   POAV: {result.poav_score:.3f}")
        print(f"   Gate: {result.gate_decision}")
        print(f"   Latency: {result.total_latency_ms:.0f}ms")

        print("\n" + "=" * 60)
        break  # Only run one for demo


if __name__ == "__main__":
    demo_multipath()
