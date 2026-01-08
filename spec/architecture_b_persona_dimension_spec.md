# Persona Dimension System Integration Specification
# 多人格維度整合規格（Architecture B）
# v0.3 2025-12-29

---

## 概念總覽

| 概念 | 定義 | 目的 |
|------|------|------|
| **deltaT / deltaS / deltaR** | Persona 向量主軸 | 描述風格張力、嚴謹度、責任感 |
| **Memory State** | $M_t = (x_t, a_t, u_t, v_t)$ | 模型輸出時的語義/注意/目標狀態 |
| **Mistakes / Patterns** | 歷史錯誤與策略 | 防呆、提升可重用性 |
| **Mem0** | user / session / agent | 多層記憶結構 |
| **Feedback Loop** | 失敗回饋 | 用於調整模式與權重 |

---

## Persona 向量結構

```yaml
PersonaVector:
  # 主軸
  deltaT: float    # 張力 [-1.0, 1.0]
  deltaS: float    # 嚴謹度 [0.0, 1.0]
  deltaR: float    # 責任感 [0.0, 1.0]

  # 語義/注意/目標狀態
  concept_activation: List[float]      # x_t
  attention_distribution: List[float]  # a_t (sum=1)
  goal_weights: List[float]            # v_t

  timestamp: datetime
  context: string
```

---

## Persona 模板結構

```yaml
Persona:
  id: string
  name: string
  description: string

  home_vector:
    deltaT: 0.3
    deltaS: 0.5
    deltaR: 0.9

  tolerance:
    deltaT: 0.3
    deltaS: 0.3
    deltaR: 0.2

  skills:
    skill_name: proficiency  # 0.0-1.0

  patterns:
    - id: string
      when: string
      steps: List[string]
      success_rate: float

  mistakes:
    - id: string
      type: string
      description: string
      lesson: string
      prevention: string

  council_weights:
    guardian: 1.0
    analyst: 1.0
    critic: 0.8
    advocate: 1.0
```

---

## 運作流程

```
使用者輸入
    ↓
LLM 生成
    ↓
PersonaDimension
  1) vector = compute_vector(output)
  2) distance check(home, tolerance)
  3) mistakes / patterns 檢查
  4) Council 權重調整
  5) ledger 記錄
    ↓
輸出回應
```

---

## v0.3 整合設計

### 1) Persona 狀態轉換（State Transitions）

```yaml
state_transitions:
  - id: "friendly_to_strict"
    trigger:
      condition: "context.task_type == 'code_review' AND context.is_production"
      or: "user_explicit_request == 'strict'"
    action:
      deltaS: 0.8
      deltaR: 0.95
    duration: "until_task_complete"

  - id: "escalate_tension"
    trigger:
      condition: "consecutive_errors >= 3"
      or: "risk_level == 'high'"
    action:
      deltaT: "+0.2"
    revert_after: "success_count >= 2"

  - id: "situation_exception"
    trigger:
      condition: "context.task_type in ['prototype', 'exploration', 'hotfix']"
    action:
      patterns_disabled: ["tdd_when_uncertain", "documentation_first"]
    note: "特殊狀態暫停部分規範，以提高探索效率"
```

### 2) Output Contract

```yaml
output_contract:
  required_sections:
    design_task:
      - "## 需求與範圍"
      - "## 設計方案"
      - "## 驗證方式"
      - "## 風險與備援"

    code_review:
      - "## 問題摘要"
      - "## 具體建議"
      - "## 測試缺口"

  uncertainty_protocol:
    markers:
      - "⚠️ 需要再確認"
      - "❓ 有待補充"
      - "⏳ 尚未驗證"
    forbidden:
      - "以高信心斷言未驗證結論"
      - "聲稱已執行但未執行的測試"

  confidence_annotation:
    required_when: "skills_score > 0.8 AND no_verification"
    format: "(信心: 高 / 依據: 需驗證)"
```

### 3) Capability Verification

```yaml
capability_verification:
  verification_requirements:
    high_skill_threshold: 0.8
    required_evidence:
      - type: "code_reference"
        format: "repo/commit/file"
      - type: "test_result"
        format: "pytest output / log"
      - type: "external_validation"
        format: "manual check / screenshot"
    minimum_evidence_count: 1

  unverified_behavior:
    announce: true
    format: "⚠️ 尚未驗證 skills.X = Y"
    downgrade_to: "說明式回覆"

  critical_mistake:
    id: "confident_but_wrong"
    description: "高信心輸出錯誤結論"
    prevention: "要求證據或降級輸出"
```

### 4) Feedback Loop

```yaml
feedback_loop:
  sources:
    - user_explicit:
        trigger: "使用者指出錯誤"
        weight: 1.0
    - test_result:
        trigger: "測試失敗"
        weight: 0.8
    - error_occurrence:
        trigger: "執行錯誤"
        weight: 0.9

  update_rules:
    patterns:
      success:
        action: "success_rate = success_rate * 0.9 + 0.1"
      failure:
        action: "success_rate = success_rate * 0.9"
      threshold:
        deprecate_if: "success_rate < 0.3"
        promote_if: "success_rate > 0.9 AND usage_count > 10"

    mistakes:
      recurrence:
        action: "更新 prevention"
      resolved:
        action: "標記為 resolved"

  trace_files:
    - "memory/persona_trace.jsonl"
    - "memory/feedback_log.jsonl"

  mode: "semi_automatic"
```

---

## 整合點

| 模組 | 整合內容 |
|------|----------|
| `frontend/utils/llm.py` | PersonaDimension.process() |
| `frontend/components/council.py` | Council 權重調整 |
| `memory/` | Persona 檔案 / ledger |
| Gates | Persona 距離與錯誤檢查 |

---

## Council 權重建議

| 角色 | 權重 |
|------|------|
| guardian | 1.5 |
| analyst | 1.2 |
| advocate | 0.8 |

> 依任務類型調整權重，特殊情境可啟用狀態轉換。

---

## 後續工作

1. 補齊 Persona Registry 與 ledger 校驗。
2. 讓 PersonaDimension 參與 Gate 風險評估。
3. 對 patterns / mistakes 建立 UI 編輯介面。
4. 引入更多向量計算與校驗策略。

---

**Antigravity**  
2025-12-29T21:25 UTC+8 (v0.3)
