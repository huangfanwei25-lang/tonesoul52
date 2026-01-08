# Skill Gravity Well Schema
# 語義重力井技能結構規格
# v0.3 2025-12-28

---

## 核心概念

技能不是線性的步驟清單，而是**語義重力井的網路**。  
每個重力井代表一個語義吸引子（Attractor），引導狀態從觸發 → 行動 → 判斷 → 結果。

這份規格同時對齊現行實作：`policy_template.when/do` 是最小可用的重力井子集。

---

## 結構定義（YAML）

```yaml
skill:
  id: string                    # 技能唯一識別
  name: string                  # 技能名稱（可讀）
  version: string               # 版本
  category: string              # 分類（選填）
  description: string           # 簡介（選填）
  keywords: [string]            # 關鍵字（選填）

  # 現行最小技能接口（兼容）
  policy_template:
    when: {}                    # 匹配條件（context/frame）
    do: string                  # 行為名稱（action）
    notes: string

  # 來源追溯
  provenance:
    source_episodes: [episode_id]
    promoted_at: timestamp
    promoted_by: string

  # 技能學習來源（選填）
  source:
    url: string
    author: string
    date_learned: timestamp
    license: string
    original_title: string
    verified_by: "user" | "ai" | "both"
    notes: string
    derived_from: string

  # 語義重力井網路
  gravity_wells:
    - id: string
      name: string
      type: trigger | action | state | decision | terminal

      semantic:
        description: string
        keywords: [string]

      leads_to: [well_id]
      attraction_strength: float  # 0-1

      action: string
      prerequisite: [well_id | condition]
      continuous: boolean
      provides: [string]

      error_prone: boolean
      common_errors: [string]
      recovery_strategy: string

  metadata:
    difficulty: float
    mastery_threshold: float
    training_episodes_needed: int
    usage:
      times_used: int
      last_used: timestamp
      mastery: float

  audit:
    last_reviewed: timestamp
    reviewer: string
    reviewer_role: string
    status: proposed | approved | deprecated
```

Note: `reviewer_role` should match `spec/governance/role_catalog.yaml`.
Note: `source` 可對應 provenance/audit 的來源與驗證資訊，對齊 `spec/skill_learning_spec.md`。

---

## 範例：YSS Governance Baseline（符合現行系統）

```yaml
skill:
  id: skill_governance_baseline_v1
  name: 治理基線
  version: "1.0"

  policy_template:
    when:
      objective: "Generate auditable artifacts"
      domain: general
      decision_mode: normal
      mode: analysis
      frame_ids: ["analysis", "bridge"]
    do: apply_governance_baseline
    notes: "Use YSS M0-M5 + gates with evidence summary required."

  provenance:
    source_episodes: [ep_181ffde6d936]
    promoted_at: "2025-12-26T02:28:24Z"
    promoted_by: owner

  gravity_wells:
    - id: w_trigger_context
      name: 治理輸出需求觸發
      type: trigger
      semantic:
        description: 任務目標要求可審計產出
        keywords: ["auditable", "governance", "evidence"]
      leads_to: [w_action_governance]
      attraction_strength: 0.9

    - id: w_action_governance
      name: 套用治理基線
      type: action
      semantic:
        description: 執行 M0-M5 + gate + evidence
        keywords: ["YSS", "gate", "audit"]
      action: apply_governance_baseline
      provides: ["force_gates", "require_evidence", "constraints_append"]
      leads_to: [w_state_evidence, w_decision_gate]
      attraction_strength: 0.95

    - id: w_state_evidence
      name: 證據完備狀態
      type: state
      semantic:
        description: evidence summary 已產出且可追溯
        keywords: ["evidence", "summary"]
      continuous: true
      leads_to: [w_decision_gate]

    - id: w_decision_gate
      name: Gate 決策
      type: decision
      semantic:
        description: gate 檢查是否通過
        keywords: ["gate", "pass", "fail"]
      leads_to: [w_terminal_audit, w_terminal_reflection]
      attraction_strength: 0.9

    - id: w_terminal_audit
      name: 審計請求完成
      type: terminal
      semantic:
        description: audit_request 已生成
        keywords: ["audit_request"]
      leads_to: []

    - id: w_terminal_reflection
      name: 反省記錄完成
      type: terminal
      semantic:
        description: gate issues 導出 reflection
        keywords: ["reflection", "improvement"]
      leads_to: []

  metadata:
    difficulty: 0.2
    mastery_threshold: 0.85
    training_episodes_needed: 6

  audit:
    last_reviewed: "2025-12-26T02:28:24Z"
    reviewer: owner
    reviewer_role: guardian
    status: approved
```

---

## 與現行實作的映射

| Gravity Well | 現行系統 |
|---|---|
| `policy_template.when` | `skills_applied.json` 的匹配條件 |
| `policy_template.do` | `apply_governance_baseline` action |
| `provides` | `skills_applied.directives` |
| `constraints_append` | `constraints.md` 的 Skill Constraints |
| `audit` | `run_skill_gate` 審核紀錄 |

---

## YSTM 對齊（語義地形圖）

| Skill Gravity Well | YSTM |
|---|---|
| well.id | Node.id |
| well.semantic.keywords | Node.what.v_sem |
| well.leads_to | Node.drift.drift_ref |
| attraction_strength | Node.scalar.E_total |
| provenance | Node.audit |

---

## 評估準則

1) **語義閉環**：重力井網路能閉合 M0→M5 的治理鏈路。  
2) **可追溯**：每個 action 都可映射到可審計檔案。  
3) **理由充分**：若 gate FAIL，必產生反省與改善建議。  
4) **責任清晰**：審核者與角色可追溯，非由 AI 承擔責任。
