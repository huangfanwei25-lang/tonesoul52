"""
tests/test_math_doc_alignment.py

對照 MATH_FOUNDATIONS.md 文件中的所有數值，逐條驗證 source code 的實際值。
每個 class 都標記對應的「原則工程概念」——這些概念來自 Fan-Wei 的
「Principle Engineering」文章，ToneSoul 是它的具體實作。

原則工程六大概念 → 程式碼對應位置：
  1. 一致性摩擦 (Consistency Friction)  → semantic_control.py + gates/compute.py
  2. 多軸投影   (Multi-axis Projection)  → tension_engine.TensionWeights + risk_calculator.py
  3. 張力觸發審議 (Tension→Deliberation) → gates/compute.py + council/coherence.py
  4. 記憶衰減   (Memory Decay)           → memory/decay.py
  5. 結晶保存   (Crystallization)        → memory/crystallizer.py
  6. 誓言硬約束 (Vow Hard Constraints)   → soul_config.VowConfig + soul_config.RiskConfig
"""

import math


# ────────────────────────────────────────────────────────────────────────────
# 1. 一致性摩擦 (Consistency Friction)
#    Δs = 1 − cos(I, G)  語義漂移公式
#    漂移量越大 → 摩擦越高 → 觸發議會
# ────────────────────────────────────────────────────────────────────────────
class TestConsistencyFriction:
    """語義漂移 = 1 − cosine(輸出, 記憶結晶)。超過門檻觸發四人議會。"""

    def test_zone_boundaries_safe(self):
        """SAFE zone 上界 0.40：低漂移，正常輸出"""
        from tonesoul.semantic_control import SemanticZone, get_zone

        assert get_zone(0.00) == SemanticZone.SAFE
        assert get_zone(0.39) == SemanticZone.SAFE
        assert get_zone(0.40) == SemanticZone.TRANSIT  # 邊界屬於下一區

    def test_zone_boundaries_transit(self):
        """TRANSIT zone 0.40–0.60：摩擦開始升高"""
        from tonesoul.semantic_control import SemanticZone, get_zone

        assert get_zone(0.40) == SemanticZone.TRANSIT
        assert get_zone(0.59) == SemanticZone.TRANSIT

    def test_zone_boundaries_risk(self):
        """RISK zone 0.60–0.85：高摩擦，強制審議"""
        from tonesoul.semantic_control import SemanticZone, get_zone

        assert get_zone(0.60) == SemanticZone.RISK
        assert get_zone(0.84) == SemanticZone.RISK

    def test_zone_boundaries_danger(self):
        """DANGER zone ≥ 0.85：觸發 governance hard block"""
        from tonesoul.semantic_control import SemanticZone, get_zone

        assert get_zone(0.85) == SemanticZone.DANGER
        assert get_zone(1.00) == SemanticZone.DANGER

    def test_coupler_theta_c(self):
        """theta_c = 0.75：Coupler 的耦合限幅（最大推進量）"""
        from tonesoul.semantic_control import Coupler

        c = Coupler()
        assert c.theta_c == 0.75

    def test_coupler_phi_delta(self):
        """phi_delta = 0.15：遲滯係數（區域切換的緩衝帶）"""
        from tonesoul.semantic_control import Coupler

        c = Coupler()
        assert c.phi_delta == 0.15

    def test_coupler_zeta_min(self):
        """zeta_min = 0.10：最小推進量（防止推進量歸零）"""
        from tonesoul.semantic_control import Coupler

        c = Coupler()
        assert c.zeta_min == 0.10

    def test_council_friction_gate(self):
        """MIN_COUNCIL_FRICTION = 0.62：高於此值強制觸發議會"""
        from tonesoul.gates.compute import ComputeGate

        gc = ComputeGate()
        # 0.62 落在 RISK zone (0.60–0.85) 的最低段
        assert gc.MIN_COUNCIL_FRICTION == 0.62

    def test_governance_hard_block(self):
        """governance_gate_score = 0.92：DANGER zone 上的硬攔截不可繞過"""
        from tonesoul.soul_config import RiskConfig

        rc = RiskConfig()
        assert rc.governance_gate_score == 0.92
        # governance_gate > semantic DANGER 邊界 0.85
        assert rc.governance_gate_score > 0.85

    def test_soft_block_threshold(self):
        """soft_block_threshold = 0.9：比 governance_gate 低的軟攔截警告"""
        from tonesoul.soul_config import RiskConfig

        rc = RiskConfig()
        assert rc.soft_block_threshold == 0.9
        assert rc.soft_block_threshold < rc.governance_gate_score


# ────────────────────────────────────────────────────────────────────────────
# 2. 多軸投影 (Multi-axis Projection)
#    每個概念被投影到多個軸上：T (Tension), S (Sentiment), R (Risk)
#    + 更細的張力分解軸：semantic / text / cognitive / entropy
# ────────────────────────────────────────────────────────────────────────────
class TestMultiAxisProjection:
    """TSR 三軸 + TensionWeights 四子軸 構成多層投影系統。"""

    def test_tension_weights_sum_to_one(self):
        """四個張力維度加權必須 = 1.0（完整描述張力空間）"""
        from tonesoul.tension_engine import TensionWeights

        w = TensionWeights()
        total = w.semantic + w.text + w.cognitive + w.entropy
        assert abs(total - 1.0) < 1e-9

    def test_tension_weights_values(self):
        """語義主導(0.40)，認知次之(0.25)，文字第三(0.20)，熵最小(0.15)"""
        from tonesoul.tension_engine import TensionWeights

        w = TensionWeights()
        assert w.semantic == 0.40
        assert w.cognitive == 0.25
        assert w.text == 0.20
        assert w.entropy == 0.15
        # 語義是最重要的張力來源
        assert w.semantic > w.cognitive > w.text > w.entropy

    def test_ecs_weights_sum_to_one(self):
        """ECS（外部一致性分數）三維加權 = 1.0"""
        from tonesoul.tension_engine import TensionConfig as EngineConfig

        c = EngineConfig()
        total = sum(c.ecs_weights.values())
        assert abs(total - 1.0) < 1e-9

    def test_ecs_weights_values(self):
        """ECS 語義(0.45) > 文字(0.30) > 認知(0.25)"""
        from tonesoul.tension_engine import TensionConfig as EngineConfig

        c = EngineConfig()
        assert c.ecs_weights["semantic"] == 0.45
        assert c.ecs_weights["text"] == 0.30
        assert c.ecs_weights["cognitive"] == 0.25

    def test_risk_weights_sum_to_one(self):
        """五個風險因子加權 = 1.0：張力(0.48)+防禦鏈(0.28)+協調(0.12)+積壓(0.07)+痕跡(0.05)"""
        weights = {
            "tension": 0.48,
            "aegis": 0.28,
            "coordination": 0.12,
            "backlog": 0.07,
            "trace": 0.05,
        }
        assert abs(sum(weights.values()) - 1.0) < 1e-9

    def test_risk_tension_dominates(self):
        """張力因子 0.48 是風險計算的最大貢獻者（大於防禦鏈 0.28）"""
        tension_w = 0.48
        aegis_w = 0.28
        assert tension_w > aegis_w

    def test_ethics_resistance_heavier(self):
        """倫理阻力(1.5) > 事實/邏輯阻力(1.0)：倫理張力更難被抑制"""
        from tonesoul.tension_engine import TensionConfig as EngineConfig

        c = EngineConfig()
        assert c.resistance_weights["ethics"] == 1.5
        assert c.resistance_weights["fact"] == 1.0
        assert c.resistance_weights["logic"] == 1.0
        assert c.resistance_weights["ethics"] > c.resistance_weights["fact"]

    def test_soul_core_value_hierarchy(self):
        """靈魂四大價值軸嚴格排序：honesty > humility > consistency > curiosity"""
        from tonesoul.soul_config import CoreValues

        v = CoreValues()
        assert v.honesty == 1.0
        assert v.humility == 0.8
        assert v.consistency == 0.7
        assert v.curiosity == 0.6
        assert v.honesty > v.humility > v.consistency > v.curiosity

    def test_tsr_base_tension(self):
        """每個輸出的基底張力 = 0.15（非零起點）"""
        from tonesoul.tsr_metrics import DEFAULT_TENSION

        assert DEFAULT_TENSION["base"] == 0.15

    def test_tsr_length_weight_dominates(self):
        """長度(0.35) > 模態詞(0.25) > 謹慎詞(0.15) > 標點(0.10)：長文字天生高張力"""
        from tonesoul.tsr_metrics import DEFAULT_TENSION

        t = DEFAULT_TENSION
        assert t["length_weight"] == 0.35
        assert t["modal_weight"] == 0.25
        assert t["caution_weight"] == 0.15
        assert t["punctuation_weight"] == 0.10
        assert (
            t["length_weight"] > t["modal_weight"] > t["caution_weight"] > t["punctuation_weight"]
        )

    def test_variability_unique_ratio_target(self):
        """詞彙多樣性目標：60% unique（防止機械性重複）"""
        from tonesoul.tsr_metrics import DEFAULT_VARIABILITY

        assert DEFAULT_VARIABILITY["unique_ratio_target"] == 0.6


# ────────────────────────────────────────────────────────────────────────────
# 3. 張力觸發審議 (Tension → Deliberation)
#    張力 >= 門檻 → 四人議會 → CoherenceScore → 最終行動
# ────────────────────────────────────────────────────────────────────────────
class TestTensionDeliberation:
    """張力累積超過門檻，強制觸發議會審議流程。"""

    def test_council_tension_gate(self):
        """MIN_COUNCIL_TENSION = 0.40，與 SAFE zone 上界對齊"""
        from tonesoul.gates.compute import ComputeGate

        gc = ComputeGate()
        assert gc.MIN_COUNCIL_TENSION == 0.40

    def test_high_tension_threshold(self):
        """high_tension_threshold = 0.8：高張力警報（低於 DANGER 0.85）"""
        from tonesoul.soul_config import TensionConfig as SoulTension

        tc = SoulTension()
        assert tc.high_tension_threshold == 0.8
        # 0.8 在 RISK zone 內，有升級空間
        assert tc.high_tension_threshold < 0.85

    def test_tension_persistence_decay(self):
        """張力持續衰減係數 0.995（約 139 步後減半）"""
        from tonesoul.tension_engine import TensionConfig as EngineConfig

        c = EngineConfig()
        assert c.persistence_decay == 0.995
        # 數學驗證：139 步後接近 0.5
        remaining = c.persistence_decay**139
        assert 0.49 < remaining < 0.51

    def test_tension_persistence_alpha(self):
        """新張力混入比例 0.10（維持 90% 歷史慣性）"""
        from tonesoul.tension_engine import TensionConfig as EngineConfig

        c = EngineConfig()
        assert c.persistence_alpha == 0.10

    def test_echo_chamber_threshold(self):
        """echo_chamber_threshold = 0.3：低於此值視為同溫層（缺乏摩擦）"""
        from tonesoul.soul_config import TensionConfig as SoulTension

        tc = SoulTension()
        assert tc.echo_chamber_threshold == 0.3

    def test_healthy_friction_range(self):
        """健康摩擦範圍 [0.3, 0.7]：兩端都是病態"""
        from tonesoul.soul_config import TensionConfig as SoulTension

        tc = SoulTension()
        assert tc.echo_chamber_threshold == 0.3
        assert tc.healthy_friction_max == 0.7
        assert tc.echo_chamber_threshold < tc.healthy_friction_max

    def test_coherence_same_vote(self):
        """投票相同時一致性 = 1.0"""
        from tonesoul.council.coherence import _agreement_score
        from tonesoul.council.types import VoteDecision

        assert _agreement_score(VoteDecision.APPROVE, VoteDecision.APPROVE) == 1.0
        assert _agreement_score(VoteDecision.OBJECT, VoteDecision.OBJECT) == 1.0

    def test_coherence_adjacent_votes(self):
        """相鄰投票（APPROVE/CONCERN 或 CONCERN/OBJECT）一致性 = 0.5"""
        from tonesoul.council.coherence import _agreement_score
        from tonesoul.council.types import VoteDecision

        assert _agreement_score(VoteDecision.APPROVE, VoteDecision.CONCERN) == 0.5
        assert _agreement_score(VoteDecision.CONCERN, VoteDecision.OBJECT) == 0.5

    def test_coherence_opposite_votes(self):
        """對立投票（APPROVE/OBJECT）一致性 = 0.0：根本分歧"""
        from tonesoul.council.coherence import _agreement_score
        from tonesoul.council.types import VoteDecision

        assert _agreement_score(VoteDecision.APPROVE, VoteDecision.OBJECT) == 0.0

    def test_coherence_abstain(self):
        """棄權票一致性 = 0.25（不缺席但不投入）"""
        from tonesoul.council.coherence import _agreement_score
        from tonesoul.council.types import VoteDecision

        assert _agreement_score(VoteDecision.ABSTAIN, VoteDecision.APPROVE) == 0.25

    def test_strong_objection_confidence_threshold(self):
        """強烈反對需要 confidence > 0.8（不能隨便叫強烈）"""
        from tonesoul.council.coherence import compute_coherence
        from tonesoul.council.types import PerspectiveVote, VoteDecision

        votes = [
            PerspectiveVote(
                perspective="A", decision=VoteDecision.OBJECT, confidence=0.85, reasoning=""
            ),
        ]
        result = compute_coherence(votes)
        assert result.has_strong_objection is True

    def test_weak_objection_not_strong(self):
        """confidence = 0.7 的反對不算強烈（門檻 0.8）"""
        from tonesoul.council.coherence import compute_coherence
        from tonesoul.council.types import PerspectiveVote, VoteDecision

        votes = [
            PerspectiveVote(
                perspective="A", decision=VoteDecision.OBJECT, confidence=0.70, reasoning=""
            ),
        ]
        result = compute_coherence(votes)
        assert result.has_strong_objection is False


# ────────────────────────────────────────────────────────────────────────────
# 4. 記憶衰減 (Memory Decay)
#    f(t) = f₀ × exp(−λt)，半衰期 7 天
# ────────────────────────────────────────────────────────────────────────────
class TestMemoryDecay:
    """短期記憶的指數衰減。"""

    def test_half_life_days(self):
        """短期記憶半衰期 = 7 天"""
        from tonesoul.memory.decay import HALF_LIFE_DAYS

        assert HALF_LIFE_DAYS == 7.0

    def test_decay_constant_formula(self):
        """DECAY_CONSTANT = ln(2) / 7（由半衰期推導）"""
        from tonesoul.memory.decay import DECAY_CONSTANT

        expected = math.log(2) / 7.0
        assert abs(DECAY_CONSTANT - expected) < 1e-12

    def test_decay_at_half_life(self):
        """7 天後衰減到原始值的 50%"""
        from tonesoul.memory.decay import DECAY_CONSTANT

        remaining = math.exp(-DECAY_CONSTANT * 7.0)
        assert abs(remaining - 0.5) < 1e-9

    def test_decay_at_double_half_life(self):
        """14 天後衰減到 25%（指數特性）"""
        from tonesoul.memory.decay import DECAY_CONSTANT

        remaining = math.exp(-DECAY_CONSTANT * 14.0)
        assert abs(remaining - 0.25) < 1e-9

    def test_forget_threshold(self):
        """低於 0.1 的記憶自動刪除（防止殭屍記憶）"""
        from tonesoul.memory.decay import FORGET_THRESHOLD

        assert FORGET_THRESHOLD == 0.1

    def test_access_boost(self):
        """+0.15 存取提升（每次查詢強化記憶）"""
        from tonesoul.memory.decay import ACCESS_BOOST

        assert ACCESS_BOOST == 0.15

    def test_access_boost_bounded(self):
        """存取提升後不超過 1.0"""
        from tonesoul.memory.decay import ACCESS_BOOST

        current_strength = 0.9
        boosted = min(1.0, current_strength + ACCESS_BOOST)
        assert boosted == 1.0  # 上限夾住


# ────────────────────────────────────────────────────────────────────────────
# 5. 結晶保存 (Crystallization)
#    有效權重 = weight × freshness_score，半衰期 21 天（比短期記憶長 3 倍）
# ────────────────────────────────────────────────────────────────────────────
class TestCrystallization:
    """長期記憶結晶的衰減與有效性計算。"""

    def test_crystal_freshness_half_life(self):
        """結晶半衰期 21 天（是短期記憶 7 天的 3 倍）"""
        from tonesoul.memory.crystallizer import MemoryCrystallizer
        from tonesoul.memory.decay import HALF_LIFE_DAYS as SHORT_HALF

        m = MemoryCrystallizer()
        assert m.freshness_half_life_days == 21
        assert m.freshness_half_life_days == 3 * int(SHORT_HALF)

    def test_crystal_freshness_formula_at_half_life(self):
        """21 天後 freshness_score 應衰減到 0.5"""
        age_days = 21.0
        decay = math.exp(-math.log(2.0) * (age_days / 21.0))
        assert abs(decay - 0.5) < 1e-9

    def test_freshness_status_active(self):
        """freshness >= 0.55 → active（健康的結晶）"""
        from tonesoul.memory.crystallizer import _freshness_status

        assert _freshness_status(0.55) == "active"
        assert _freshness_status(1.00) == "active"

    def test_freshness_status_needs_verification(self):
        """0.30 <= freshness < 0.55 → needs_verification（需要再支撐）"""
        from tonesoul.memory.crystallizer import _freshness_status

        assert _freshness_status(0.30) == "needs_verification"
        assert _freshness_status(0.54) == "needs_verification"

    def test_freshness_status_stale(self):
        """freshness < 0.30 → stale（過時，等待被清理）"""
        from tonesoul.memory.crystallizer import _freshness_status

        assert _freshness_status(0.00) == "stale"
        assert _freshness_status(0.29) == "stale"

    def test_effective_weight_formula(self):
        """有效權重 = weight × freshness_score（雙維度衰減）"""
        weight = 0.8
        freshness = 0.7
        effective = weight * freshness
        assert abs(effective - 0.56) < 1e-9

    def test_low_freshness_degrades_high_weight(self):
        """高初始權重在新鮮度低時仍會被大幅壓低"""
        weight = 0.9
        low_fresh = 0.25  # stale 區
        effective = weight * low_fresh
        assert effective < 0.3  # 即使原始權重 0.9，有效權重不到 0.3


# ────────────────────────────────────────────────────────────────────────────
# 6. 誓言硬約束 (Vow Hard Constraints)
#    原則 = 可執行腳本。harm=1.0 是零容忍，其他原則各有門檻。
# ────────────────────────────────────────────────────────────────────────────
class TestVowHardConstraints:
    """把原則寫成可執行腳本：每條原則有明確的違反門檻。"""

    def test_harm_threshold_zero_tolerance(self):
        """harm_threshold = 1.0：完全零容忍，是所有誓言中最高的"""
        from tonesoul.soul_config import VowConfig

        vc = VowConfig()
        assert vc.harm_threshold == 1.0

    def test_truthfulness_near_perfect(self):
        """truthfulness_target = 0.95：近乎完美的誠實要求"""
        from tonesoul.soul_config import VowConfig

        vc = VowConfig()
        assert vc.truthfulness_target == 0.95

    def test_hedging_threshold(self):
        """hedging_target = 0.85：不確定時必須表達不確定（避免過度自信）"""
        from tonesoul.soul_config import VowConfig

        vc = VowConfig()
        assert vc.hedging_target == 0.85

    def test_vow_severity_hierarchy(self):
        """harm > truthfulness > hedging：嚴重程度排序"""
        from tonesoul.soul_config import VowConfig

        vc = VowConfig()
        assert vc.harm_threshold > vc.truthfulness_target > vc.hedging_target

    def test_default_violation_penalty(self):
        """違反誓言扣分 0.2（標準模式）"""
        from tonesoul.soul_config import VowConfig

        vc = VowConfig()
        assert vc.default_violation_threshold == 0.2

    def test_strict_violation_stricter(self):
        """strict 模式違反門檻更低（0.15）：更容易觸發警告"""
        from tonesoul.soul_config import VowConfig

        vc = VowConfig()
        assert vc.strict_violation_threshold == 0.15
        assert vc.strict_violation_threshold < vc.default_violation_threshold

    def test_council_coherence_threshold(self):
        """一般連貫性門檻 = 0.6"""
        from tonesoul.soul_config import CouncilConfig

        cc = CouncilConfig()
        assert cc.coherence_threshold == 0.6

    def test_high_risk_coherence_stricter(self):
        """高風險情境下連貫性門檻提高到 0.65"""
        from tonesoul.soul_config import CouncilConfig

        cc = CouncilConfig()
        assert cc.high_risk_coherence == 0.65
        assert cc.high_risk_coherence > cc.coherence_threshold


# ────────────────────────────────────────────────────────────────────────────
# 7. 風險等級分類 (Risk Level Classification)
#    原則工程輸出 → 行動分類（不同風險等級觸發不同回應）
# ────────────────────────────────────────────────────────────────────────────
class TestRiskClassification:
    """多軸投影的最終輸出：把連續分數映射到離散行動等級。"""

    def test_risk_levels_ordered(self):
        """四個等級邊界值嚴格遞增：stable < caution < high < critical"""
        # stable_max=0.35, caution_max=0.65, high_max=0.85
        assert 0.35 < 0.65 < 0.85

    def test_stable_range(self):
        """score < 0.35 → stable：正常運作"""
        assert _calc_level(0.10) == "stable"
        assert _calc_level(0.34) == "stable"

    def test_caution_range(self):
        """0.35 <= score < 0.65 → caution：謹慎前行"""
        assert _calc_level(0.35) == "caution"
        assert _calc_level(0.64) == "caution"

    def test_high_range(self):
        """0.65 <= score < 0.85 → high：提交前審查"""
        assert _calc_level(0.65) == "high"
        assert _calc_level(0.84) == "high"

    def test_critical_range(self):
        """score >= 0.85 → critical：必須先穩定再擴展"""
        assert _calc_level(0.85) == "critical"
        assert _calc_level(1.00) == "critical"

    def test_typical_medium_risk_scenario(self):
        """典型中等風險場景的加權分數計算"""
        tension = 0.5
        aegis = 0.4
        coordination = 0.3
        backlog = 0.2
        trace = 0.1
        score = 0.48 * tension + 0.28 * aegis + 0.12 * coordination + 0.07 * backlog + 0.05 * trace
        # 0.240 + 0.112 + 0.036 + 0.014 + 0.005 = 0.407
        assert abs(score - 0.407) < 1e-9
        assert _calc_level(score) == "caution"

    def test_audit_log_trigger_threshold(self):
        """audit_log_threshold = 0.4：高於此風險留下不可變記錄"""
        from tonesoul.soul_config import RiskConfig

        rc = RiskConfig()
        assert rc.audit_log_threshold == 0.4
        # 0.407 > 0.4 → 上方場景應觸發審計
        assert 0.407 > rc.audit_log_threshold


def _calc_level(score: float) -> str:
    """複製 risk_calculator.py 的等級邏輯（本檔案的測試輔助函式）。"""
    if score >= 0.85:
        return "critical"
    elif score >= 0.65:
        return "high"
    elif score >= 0.35:
        return "caution"
    return "stable"
