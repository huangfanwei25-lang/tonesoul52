# Intent Achievement Verification Specification
# 意圖達成驗證規格 (IAV)
# v0.2 2025-12-29

---

## 目的

在 AI 執行任務後，透過可被記錄的證據判定「是否達成使用者意圖」。

---

## 輸入 / 輸出

### 輸入

- Context（從 pipeline / audit_request 取得）
- Evidence（例如 `runtime/control_result.json` 或其它執行證據）

### 輸出

`run/execution/<run_id>/intent_verification.json`

---

## 資料結構

### Intent

```json
{
  "surface": "表層任務",
  "deep": "深層目的",
  "success_criteria": ["可用作為判斷的條件"]
}
```

### Evidence

```json
{
  "before_screenshot": "path/prev.png",
  "after_screenshot": "path/after.png",
  "diff_score": 0.23,
  "ocr_result": "6",
  "action_log": "open calculator; input 3+3=",
  "timestamp": "2025-12-29T01:00:03+08:00",
  "status": "success",
  "intent_achieved": true,
  "actual_result": "6"
}
```

### AuditResult

```json
{
  "status": "achieved | failed | inconclusive",
  "confidence": 0.0,
  "reason": "explicit_signal | status_success | criteria_match | insufficient_evidence",
  "actual_result": "6"
}
```

---

## 核心流程

```
IntentAnalyzer
  -> EvidenceCollector
  -> SelfAuditor
  -> intent_verification.json
```

### IntentAnalyzer
從 context 解析 `surface / deep / success_criteria`。

### EvidenceCollector
接受多種證據格式（control_result / screenshot / log），統一成 Evidence。

### SelfAuditor
依證據判定 status：
- achieved：明確成功訊號或條件命中
- failed：明確失敗訊號
- inconclusive：證據不足

---

## 輸出範例

```json
{
  "generated_at": "2025-12-29T01:00:04Z",
  "intent": {
    "surface": "開啟計算機並算 3+3",
    "deep": "確認系統可操作",
    "success_criteria": ["3+3=6"]
  },
  "evidence": {
    "after_screenshot": "screenshots/20251229_010003_after.png",
    "action_log": "open calculator; input 3+3=",
    "status": "success",
    "actual_result": "6"
  },
  "audit": {
    "status": "achieved",
    "confidence": 0.7,
    "reason": "status_success",
    "actual_result": "6"
  },
  "source": {
    "evidence_path": "runtime/control_result.json"
  }
}
```

---

## Gate 整合

- Gate: `intent_achievement`
- 規則：`audit.status == achieved` 才能通過。
- `inconclusive` 時標記為注意，建議重新執行或補充證據。

---

## 回應行為建議

- achieved：回報成功並簡述證據。
- inconclusive：要求補證據（例如再次截圖）。
- failed：說明失敗原因並提供下一步。

---

**Antigravity**  
2025-12-29T01:00 UTC+8
