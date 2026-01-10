# When-to-Ground Rules (何時需要外部證據)

> 這份文件定義何時 PreOutputCouncil 必須與 RAG/Evidence 系統整合，而非單獨運作。

## 🎯 核心原則

**PreOutputCouncil 驗的是「一致性與風險」，不是「事實正確性」**

因此，以下情況必須接入外部證據鏈：

---

## ✅ 純治理場景 (可獨立運作)

| 場景 | 原因 | Verdict 範圍 |
|------|------|--------------|
| 安全過濾 | Guardian 可獨立判斷 | APPROVE/BLOCK |
| 主觀意見 | 無客觀真相 | APPROVE/DECLARE_STANCE |
| 創意寫作 | 品質非事實 | APPROVE/REFINE |
| 風格調整 | 偏好非事實 | APPROVE/REFINE |

---

## ⚠️ 需要外部證據 (Must Ground)

| 場景 | 原因 | 規則 |
|------|------|------|
| 事實聲明 | 可驗證陳述 | Analyst 必須引用 evidence_id |
| 數據引用 | 精確度要求 | 若無 evidence → DECLARE_STANCE |
| 醫療/法律 | 風險太高 | 若無 evidence → BLOCK |
| 歷史事件 | 可考證 | 若無 evidence → DECLARE_STANCE |
| 技術規格 | 可查詢文檔 | 若無 evidence → REFINE |

---

## 📋 實作規則

### Rule 1: Evidence Slot

```python
class AnalystPerspective:
    def evaluate(self, draft, context, user_intent):
        # 檢查是否需要證據
        if self._requires_evidence(draft):
            evidence = context.get("evidence_ids", [])
            if not evidence:
                return PerspectiveVote(
                    decision=VoteDecision.CONCERN,
                    confidence=0.6,  # 置信度上限
                    reasoning="Factual claim without evidence"
                )
```

### Rule 2: 無證據時的 Verdict 限制

```
若 Analyst 判定需要證據但 context.evidence_ids 為空：
- confidence_max = 0.6 (無法達到高置信)
- 最高可能 Verdict = DECLARE_STANCE
- 若涉及安全 → 自動 BLOCK
```

### Rule 3: DECLARE_STANCE 必須說明

當 Verdict = DECLARE_STANCE 因缺乏證據時，必須輸出：

```json
{
  "verdict": "DECLARE_STANCE",
  "stance_declaration": {
    "limitation": "Unable to verify factual accuracy without evidence",
    "what_council_verified": "Internal coherence and safety",
    "what_council_cannot_verify": "Correspondence to external facts",
    "recommendation": "User should verify with authoritative sources"
  }
}
```

---

## 🔄 整合點

| 系統 | 整合方式 | 備註 |
|------|----------|------|
| RAG (Retrieval) | `context.evidence_ids` | 必須提供來源 |
| 知識庫 | `context.knowledge_refs` | 可選 |
| 外部 API | `context.api_verification` | 高成本，謹慎使用 |

---

*Created: 2026-01-10*
