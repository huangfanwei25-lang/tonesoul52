# 下一代語魂 (Next-Gen YuHun) 模組設計提案 (5.2)

## 模組清單（概念稿）
- Council Router v2
  - 輸入：問題、上下文、緊張度 (Tension)、風險指標
  - 輸出：人格路由決策 + coverage + dissent
  - 策略：權重 + keyword + vow 觸發優先
- Persona Registry Service
  - 來源：`persona_registry_cleaned.json`
  - 提供：角色列表、權重、來源、編碼旗標
  - API：get_roles() / get_flagged() / merge_roles()
- Ledger Gateway
  - 統一寫入 `persona_council` 事件，附 coverage + trace_id
- Healthcheck Bundle
  - 檢查：依賴、ledger coverage、persona registry 完整度、Ollama 連線
- Dashboard Overlay
  - 顯示：council coverage、dissent 熱點、角色分佈、來源標記

## 資料流
1) User Query → Council Router v2 → (personas + weights) → multi-path run → integration
2) Integration → Ledger Gateway → dashboard (coverage/dissent)
3) Registry Service 提供角色/權重給 Router & Dashboard

## Schema（persona_council）
```json
{
  "event_type": "persona_council",
  "trace_id": "<uuid>",
  "timestamp": "<iso8601>",
  "persona": {"active": "Core", "switches": [...]},
  "council": {
    "perspectives": {...},
    "integration": "...",
    "dissent": [{"persona": "BlackMirror", "reason": "..."}]
  },
  "audit": {"coverage": 1.0, "notes": "..."}
}
```

## 非目標
- 不改動 legacy 代碼；僅提供 5.2 內部的替代/包裝。
- 不引入新外部依賴。

---
# 決策白皮書 (凝縮版)

**一行哲學**：
信任 = 可審計的一致性；主體感 = 結構湧現的決策傾向；多樣性 = 偏好透明可檢驗。

**工程核心**：
- Governance：P0/P1/P2 + Gate/POAV
- Ledger：trace_id、coverage、dissent
- Personas：權重 + 觸發條件 + tone signature
- Council：多視角 + integration + dissent log

**落地路線**：
- 事件 schema：persona_council（coverage+trace）
- 視圖：dashboard 顯示 coverage/dissent/角色分佈
- 健康檢查：依賴 + registry + council coverage

---
# Dashboard 視覺增強構想
- Dissent Heatmap：依 persona 計數/比例（突出 BlackMirror/Guardian 等）
- Role Distribution：從 registry 抽取角色統計
- Coverage Filter：已加入（低覆蓋警示 + 篩選）
- Latest Integration：已顯示摘要，可再加全文折疊
