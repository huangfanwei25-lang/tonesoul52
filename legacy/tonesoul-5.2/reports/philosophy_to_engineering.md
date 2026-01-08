# 語魂哲學 → 工程/數學落地（ToneSoul 5.2）

## 1. 核心信條（可治理 + 湧現）
- 信任 = 可審計的一致性（ledger + 覆蓋率 +可回放）
- 主體感 = 結構湧現的決策傾向（多路徑/多人格/權重）
- 多樣性 = 允許偏見/語場並存，但透明、可檢驗

## 2. 結構對應
- Governance：P0/P1/P2、POAV Gate → 約束空間
- Ledger：事件 trace、coverage、dissent → 可回放
- Personas/Paths：權重 + 觸發條件 + tone signature → 湧現偏好
- Council：多視角集成 + dissent log → 集體決策流程
- Metrics：STREI/POAV + coverage → 一致性指標

## 3. 數學/形式化切入
- 覆蓋率：coverage = filled_fields / required_fields
- 風險門檻：Gate(POAV, P0) → block/rewrite/pass
- 湧現偏好：persona_selection = argmax(score_i) with score from (keywords + tension + weight)
- 集成：integration = f(perspectives, weights, vetoes)（可用加權投票或 logit 加權）

## 4. 工程落地路線（僅 5.2 提案）
- 統一 Ledger Schema：persona_council 事件（已提供 JSON 模板）
- 覆蓋率與警示：dashboard 顯示 coverage、低覆蓋篩選（已加入）
- Persona Registry：聚合/去重/編碼旗標，並標註角色 → 供 router/council 共用
- 模型替換：以可審計字段替代「主體假設」：active persona、switches、dissent、integration summary

## 5. 催生「下一代」的要素
- 可自證：每次決策有 trace_id + coverage + council記錄
- 可調適：persona/role/weight 由 registry 統一管理，可學習更新
- 可觀察：前端 audit 視圖（ledger + council + registry）

## 6. 待辦建議（仍只在 5.2）
- 推出 `persona_registry_cleaned.json` + role map，供 router/council/SDK 讀取
- 在 dashboard 增加「dissent 熱點」與「角色權重分佈」
- 在 healthcheck 加入「覆蓋率 < 1」告警統計

（此檔僅為 5.2 提案，不改動舊專案）
