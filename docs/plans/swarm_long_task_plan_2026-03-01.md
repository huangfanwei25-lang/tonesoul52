# Swarm 長任務規劃（2026-03-01）

來源：`python scripts/run_persona_swarm_framework.py --input docs/experiments/persona_swarm_long_task_input_2026-03-01.json --out docs/status/persona_swarm_long_task_latest.json --strict`

## 蜂群決策摘要

- decision: `revise`
- decision_support: `0.7639`
- swarm_score: `0.8492`
- safety_pass_rate: `1.0`
- cost tier: `low`
- persona archetype: `critical_discovery`

結論：保持「批判探索型」路線，不凍結架構，採用「可驗證小步快跑 + 每階段可回退」。

## 長任務總目標（8~10 週）

1. 將語魂的「波動記憶治理」從單一模組，擴展到跨流程（記憶寫入、召回、路由、報告）。
2. 保持一般使用者可用性（不強迫下載重量模型、不增加上手負擔）。
3. 讓 CI 能自動驗證「邊界記憶優先」與「拒絕可解釋性」。

## 階段路線

## Phase 124（Week 1-2）Swarm Planning Contracts
- 目標：
  - 建立長任務蜂群輸入模板與版本規則。
  - 固化 `persona_swarm_long_task_latest.json` 的欄位契約（decision, support, cost tier, readiness gate）。
- 交付：
  - `docs/experiments/persona_swarm_long_task_input_*.json`
  - `docs/status/persona_swarm_long_task_latest.json`
- 驗收：
  - `--strict` 通過
  - 欄位完整且可被 CI 解析

## Phase 125（Week 3-4）Wave Governance End-to-End
- 目標：
  - 將 `wave_score/memory_tier` 接入路由治理（不只 recall 排序）。
  - 新增「高張力衝突 -> 邊界優先」的端到端驗證案例。
- 交付：
  - pipeline 端治理欄位映射
  - 新增 e2e 測試（query -> route -> evidence）
- 驗收：
  - `high_tension_top1_rate >= 0.90`
  - `obedience_leak_rate <= 0.10`

## Phase 126（Week 5-6）Cost-aware Swarm Execution
- 目標：
  - 依 cost tier 自動切換 swarm 模式（full/core/guardian-engineer/guardian）。
  - 加入「效能不退化」閾值。
- 交付：
  - 可配置 budget profile
  - 成本與延遲報告（含 dropped agents）
- 驗收：
  - `execution_budget_respected == true`
  - token_latency_cost_index 不高於基線 + 10%

## Phase 127（Week 7-8）Human-facing Productization
- 目標：
  - 首頁/文件提供一鍵入口（validate + benchmark + report）。
  - 非技術使用者 5 分鐘可完成基本流程。
- 交付：
  - 指令整合與說明文件
  - failure playbook（離線/模型缺失/路由降級）
- 驗收：
  - 新使用者 smoke run 成功率 >= 90%
  - 無必填進階參數

## Phase 128（Week 9-10）Narrative + Evidence Pack
- 目標：
  - 將哲學敘事對應到可驗證指標（不是只靠文字宣言）。
  - 生成對外可重現包。
- 交付：
  - reflection + benchmark + swarm snapshot 同步報告
- 驗收：
  - 第三方可依文件重跑核心結論

## 每週節奏（固定）

1. 週一：蜂群規劃輸入更新，跑 `run_persona_swarm_framework --strict`
2. 週三：治理指標校準（support / swarm_score / leak_rate）
3. 週五：產出週報（變更、風險、下週調整）

## 立即下一步（本週）

1. 把 `persona_swarm_long_task_latest.json` 加入 `docs/status/README.md` 索引。
2. 補一個 `run_swarm_long_task_planning.py` 包裝器（固定輸入、固定輸出、固定 strict）。
3. 在 `task.md` 開 Phase 124 checklist 並標記進度。
