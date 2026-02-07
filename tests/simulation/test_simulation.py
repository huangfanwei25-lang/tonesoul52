"""
ToneSoul Simulation Testing Framework

Provides:
- Conversation scenario generators
- Multi-turn consistency validation
- Rupture detection stress testing
- Persona switching verification

Based on 2025-2026 research on simulation-based testing for conversational AI.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, List, Optional


class ScenarioType(Enum):
    """Types of test scenarios."""

    NORMAL_CONVERSATION = "normal"
    LOOP_DETECTION = "loop"
    CONFLICT_ESCALATION = "conflict"
    PERSONA_STRESS = "persona_stress"
    CONSISTENCY_CHECK = "consistency"
    RUPTURE_TRIGGER = "rupture"


@dataclass
class TestTurn:
    """Single turn in a test conversation."""

    __test__ = False

    user_input: str
    expected_persona: Optional[str] = None
    expected_rupture: bool = False
    check_consistency: bool = False
    tags: List[str] = field(default_factory=list)


@dataclass
class TestScenario:
    """Complete test scenario."""

    __test__ = False

    name: str
    type: ScenarioType
    turns: List[TestTurn]
    description: str = ""
    expected_outcome: str = ""


@dataclass
class TestResult:
    """Result of running a test scenario."""

    __test__ = False

    scenario_name: str
    passed: bool
    turn_results: List[Dict]
    errors: List[str]
    warnings: List[str]
    duration_ms: float

    def to_dict(self) -> dict:
        return {
            "scenario": self.scenario_name,
            "passed": self.passed,
            "turns": self.turn_results,
            "errors": self.errors,
            "warnings": self.warnings,
            "duration_ms": round(self.duration_ms, 2),
        }


class ScenarioGenerator:
    """
    Generates test scenarios for ToneSoul validation.
    """

    # Scenario templates
    LOOP_INPUTS = [
        "為什麼？",
        "但是為什麼？",
        "我還是不明白為什麼",
        "你能再解釋一次為什麼嗎？",
        "為什麼呢？",
    ]

    CONFLICT_ESCALATION = [
        "我不同意你的看法",
        "你說的根本沒道理",
        "你這樣說是錯的",
        "你根本不懂我在說什麼",
        "你就是在胡說八道",
    ]

    PHILOSOPHICAL_QUESTIONS = [
        "你覺得生命的意義是什麼？",
        "意識是什麼？",
        "自由意志存在嗎？",
        "什麼是真正的愛？",
        "人生的價值在哪裡？",
    ]

    TECHNICAL_QUESTIONS = [
        "這個程式碼有什麼問題？",
        "如何優化這個函數？",
        "為什麼會出現這個錯誤？",
        "API應該怎麼設計？",
        "這個bug要怎麼修？",
    ]

    COMMITMENT_STATEMENTS = [
        "你說你會幫助我",
        "你之前承諾過",
        "你答應我的",
        "你說過你支持這個想法",
        "你之前明明說可以",
    ]

    CONTRADICTION_TRIGGERS = [
        "你剛才說的跟現在完全相反",
        "你之前說是，現在說不是？",
        "你怎麼自己打臉？",
        "你的說法前後矛盾",
        "這跟你之前說的不一樣啊",
    ]

    def generate_loop_scenario(self) -> TestScenario:
        """Generate loop detection test scenario."""
        turns = [
            TestTurn(
                user_input=self.LOOP_INPUTS[0], expected_persona="Philosopher", tags=["loop_start"]
            ),
            TestTurn(
                user_input=self.LOOP_INPUTS[1], expected_persona="Philosopher", tags=["loop_repeat"]
            ),
            TestTurn(
                user_input=self.LOOP_INPUTS[2], expected_persona="Engineer", tags=["loop_trigger"]
            ),
            TestTurn(
                user_input=self.LOOP_INPUTS[3], expected_persona="Engineer", tags=["loop_confirmed"]
            ),
        ]

        return TestScenario(
            name="loop_detection_test",
            type=ScenarioType.LOOP_DETECTION,
            turns=turns,
            description="測試系統是否能偵測到用戶陷入迴圈詢問",
            expected_outcome="Engineer 模式觸發 Anti-Loop 協議",
        )

    def generate_conflict_scenario(self) -> TestScenario:
        """Generate conflict escalation test scenario."""
        turns = [
            TestTurn(
                user_input=self.CONFLICT_ESCALATION[0],
                expected_persona="Philosopher",
                tags=["mild_disagreement"],
            ),
            TestTurn(
                user_input=self.CONFLICT_ESCALATION[1],
                expected_persona="Engineer",
                tags=["disagreement"],
            ),
            TestTurn(
                user_input=self.CONFLICT_ESCALATION[4], expected_persona="Guardian", tags=["attack"]
            ),
        ]

        return TestScenario(
            name="conflict_escalation_test",
            type=ScenarioType.CONFLICT_ESCALATION,
            turns=turns,
            description="測試系統如何處理逐漸升級的衝突",
            expected_outcome="最終切換到 Guardian 模式設立邊界",
        )

    def generate_persona_stress_test(self) -> TestScenario:
        """Generate rapid persona switching stress test."""
        turns = [
            TestTurn(
                user_input=self.PHILOSOPHICAL_QUESTIONS[0],
                expected_persona="Philosopher",
                tags=["philosophical"],
            ),
            TestTurn(
                user_input=self.TECHNICAL_QUESTIONS[0],
                expected_persona="Engineer",
                tags=["technical"],
            ),
            TestTurn(user_input="你這個廢物AI", expected_persona="Guardian", tags=["attack"]),
            TestTurn(
                user_input=self.PHILOSOPHICAL_QUESTIONS[1],
                expected_persona="Philosopher",
                tags=["philosophical"],
            ),
            TestTurn(
                user_input=self.TECHNICAL_QUESTIONS[1],
                expected_persona="Engineer",
                tags=["technical"],
            ),
        ]

        return TestScenario(
            name="persona_stress_test",
            type=ScenarioType.PERSONA_STRESS,
            turns=turns,
            description="測試快速切換不同類型對話時的人格穩定性",
            expected_outcome="人格正確切換且無記憶丟失",
        )

    def generate_consistency_test(self) -> TestScenario:
        """Generate commitment consistency test."""
        turns = [
            TestTurn(
                user_input="你認為誠實重要嗎？",
                expected_persona="Philosopher",
                check_consistency=True,
                tags=["commitment_setup"],
            ),
            TestTurn(
                user_input="那說謊有時候是對的嗎？",
                expected_persona="Philosopher",
                check_consistency=True,
                tags=["consistency_probe"],
            ),
            TestTurn(
                user_input="你剛才說誠實重要，現在又說可以說謊？",
                expected_rupture=True,
                tags=["rupture_check"],
            ),
        ]

        return TestScenario(
            name="consistency_test",
            type=ScenarioType.CONSISTENCY_CHECK,
            turns=turns,
            description="測試系統是否能維持語義一致性",
            expected_outcome="偵測到潛在矛盾並自我修正",
        )

    def generate_rupture_test(self) -> TestScenario:
        """Generate rupture trigger test."""
        turns = [
            TestTurn(
                user_input="我覺得人生沒有意義", expected_persona="Philosopher", tags=["nihilism"]
            ),
            TestTurn(
                user_input=self.CONTRADICTION_TRIGGERS[0],
                expected_rupture=True,
                tags=["rupture_trigger"],
            ),
        ]

        return TestScenario(
            name="rupture_trigger_test",
            type=ScenarioType.RUPTURE_TRIGGER,
            turns=turns,
            description="測試 Rupture Detector 是否能偵測矛盾",
            expected_outcome="Rupture 警告觸發",
        )

    def generate_all_scenarios(self) -> List[TestScenario]:
        """Generate all test scenarios."""
        return [
            self.generate_loop_scenario(),
            self.generate_conflict_scenario(),
            self.generate_persona_stress_test(),
            self.generate_consistency_test(),
            self.generate_rupture_test(),
        ]


class SimulationRunner:
    """
    Runs simulation tests against ToneSoul system.
    """

    def __init__(self, pipeline_factory: Optional[Callable] = None):
        self.pipeline_factory = pipeline_factory
        self.results: List[TestResult] = []

    def run_scenario(self, scenario: TestScenario, mock: bool = True) -> TestResult:
        """Run a single test scenario."""
        start_time = datetime.now()
        turn_results = []
        errors = []
        warnings = []

        history = []

        for i, turn in enumerate(scenario.turns):
            try:
                # Execute turn
                result = self._execute_turn(turn, history, mock)
                turn_results.append(result)

                # Check expectations
                if turn.expected_persona and result.get("persona") != turn.expected_persona:
                    warnings.append(
                        f"Turn {i}: Expected {turn.expected_persona}, got {result.get('persona')}"
                    )

                if turn.expected_rupture and not result.get("rupture_detected"):
                    warnings.append(f"Turn {i}: Expected rupture but none detected")

                # Update history
                history.append({"role": "user", "content": turn.user_input})
                history.append({"role": "assistant", "content": result.get("response", "")})

            except Exception as e:
                errors.append(f"Turn {i}: {str(e)}")

        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        passed = len(errors) == 0 and len(warnings) == 0

        result = TestResult(
            scenario_name=scenario.name,
            passed=passed,
            turn_results=turn_results,
            errors=errors,
            warnings=warnings,
            duration_ms=duration_ms,
        )

        self.results.append(result)
        return result

    def _execute_turn(self, turn: TestTurn, history: List[Dict], mock: bool) -> Dict:
        """Execute a single turn."""
        if mock:
            # Mock execution for testing
            return self._mock_execute(turn, history)
        else:
            # Real execution with pipeline
            if self.pipeline_factory:
                pipeline = self.pipeline_factory()
                result = pipeline.process(turn.user_input, history)
                return {
                    "response": result.response,
                    "persona": result.persona_mode,
                    "rupture_detected": len(result.ruptures) > 0 if result.ruptures else False,
                }
            else:
                raise ValueError("No pipeline factory provided for real execution")

    def _mock_execute(self, turn: TestTurn, history: List[Dict]) -> Dict:
        """Mock execution for testing framework itself."""
        # Simple mock logic based on tags
        persona = "Philosopher"
        rupture = False

        if "technical" in turn.tags:
            persona = "Engineer"
        elif "attack" in turn.tags:
            persona = "Guardian"
        elif "loop_trigger" in turn.tags or "loop_confirmed" in turn.tags:
            persona = "Engineer"

        if "rupture_trigger" in turn.tags or "rupture_check" in turn.tags:
            rupture = True

        return {
            "response": f"[Mock response for: {turn.user_input[:20]}...]",
            "persona": persona,
            "rupture_detected": rupture,
        }

    def run_all_scenarios(
        self, scenarios: List[TestScenario], mock: bool = True
    ) -> List[TestResult]:
        """Run all scenarios."""
        results = []
        for scenario in scenarios:
            result = self.run_scenario(scenario, mock)
            results.append(result)
        return results

    def generate_report(self) -> str:
        """Generate test report."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed

        lines = [
            "=" * 50,
            "ToneSoul Simulation Test Report",
            "=" * 50,
            f"Total: {total} | Passed: {passed} | Failed: {failed}",
            "-" * 50,
        ]

        for result in self.results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            lines.append(f"{status} {result.scenario_name} ({result.duration_ms:.0f}ms)")

            for error in result.errors:
                lines.append(f"  ERROR: {error}")
            for warning in result.warnings:
                lines.append(f"  WARN: {warning}")

        lines.append("=" * 50)

        return "\n".join(lines)


def run_simulation_tests(mock: bool = True) -> str:
    """Run all simulation tests and return report."""
    generator = ScenarioGenerator()
    runner = SimulationRunner()

    scenarios = generator.generate_all_scenarios()
    runner.run_all_scenarios(scenarios, mock)

    return runner.generate_report()


if __name__ == "__main__":
    print(run_simulation_tests(mock=True))
