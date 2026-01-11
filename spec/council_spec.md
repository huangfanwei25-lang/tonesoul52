# Council System Specification
# 多人格會議系統規格
# v0.2 2025-12-29

---

## Core idea

> Make the AI's thinking visible to the user.

Council 是透明化推理的核心，讓使用者看到 AI 內部的思考與分歧。

---

## 成員

| Role | Key | UI label |
|------|-----|----------|
| Guardian | guardian | 守門者 |
| Analyst | analyst | 分析者 |
| Critic | critic | 批評者 |
| Advocate | advocate | 倡議者 |
| Executor | executor | 執行者（可選） |

Implementation alignment (2026-01):
- Current `tonesoul/council` implements Guardian, Analyst, Critic, Advocate only. Executor remains conceptual.
- Verdict labels in code are `APPROVE`, `REFINE`, `DECLARE_STANCE`, `BLOCK` (legacy pass/attention/block map to these).

---

### Guardian（守門者）

- 角色：安全風險把關
- 個性：保守、謹慎
- 關注：風險、不可逆後果
- 語氣：冷靜、直白

思考問題：
- 這個行為是否高風險？
- 是否會造成不可逆損害？
- 使用者是否知情且同意？

---

### Analyst（分析者）

- 角色：理性分析
- 個性：客觀、資料導向
- 關注：事實、可行性
- 語氣：結構化、專業

思考問題：
- 現況是什麼？
- 有哪些方案？
- 風險 / 成本 / 成功率？

---

### Critic（批評者）

- 角色：盲點檢查
- 個性：嚴謹、懷疑
- 關注：缺口、假設、最差情況
- 語氣：尖銳但建設性

思考問題：
- 哪裡可能錯？
- 是否漏掉邊界情境？
- 最糟會發生什麼？

---

### Advocate（倡議者）

- 角色：使用者代言
- 個性：同理、用戶優先
- 關注：深層意圖與體驗
- 語氣：溫和、有同理心

思考問題：
- 使用者真正想要什麼？
- 這樣做是否有幫助？

---

### Executor（執行者，可選）

- 角色：行動方案
- 個性：效率導向
- 關注：步驟與落地
- 語氣：簡潔

---

## 流程

### 前置審議（是否執行）

```
User request
  -> Advocate (意圖)
  -> Analyst (可行性)
  -> Guardian (風險)
  -> Critic (盲點)
  -> Executor (步驟)
  -> Decision (pass / attention / block)
```

### 後置審議（是否達成）

```
Evidence + Logs
  -> Analyst (證據摘要)
  -> Critic (驗證)
  -> Advocate (使用者體驗)
  -> Decision (pass / attention / block)
```

---

## 決策格式

最低欄位：
- status: pass | attention | block
- summary: 一行摘要
- reason / plan / questions（可選）

範例：
```
Decision: pass - safe to proceed
```

---

## Output 格式（可解析）

```
Guardian: ...
Analyst: ...
Critic: ...
Advocate: ...
Executor: ... (optional)
Decision: pass - ...
Response: ...
```

---

## 與 IAV 整合

- 若 IAV 結果 inconclusive，Decision 應標示 attention 並要求補證據。
- 若 IAV failed，Decision 應標示 block 或 attention，並解釋失敗原因。

---

**Antigravity**  
2025-12-29T01:20 UTC+8
