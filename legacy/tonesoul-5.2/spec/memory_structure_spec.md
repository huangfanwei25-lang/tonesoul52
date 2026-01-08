# Memory Database Structure Specification
# 記憶資料結構規格
# v0.2 2025-12-30

---

## 目標

定義記憶資料的目錄結構、命名與欄位格式，讓「可追蹤、可檢索、可治理」成為預設。

---

## 目錄結構

```
memory/
  seeds/                 專案筆記（短文、規格摘要）
  user/                  使用者記憶
  session/               會話記憶
  agent/                 代理記憶
  mistakes/              踩雷記錄
  patterns/              策略模式
  skills/                內建或學習技能（JSON）
  personas/              Persona 模板（YAML）
  conversation_ledger.jsonl
  conversation_summary.jsonl
  persona_trace.jsonl
  persona_dimension_ledger.jsonl
```

---

## 命名規則

- `seed_YYYYMMDD_###.json`
- `mistake_YYYYMMDD_###.json`
- `pattern_<slug>.json`
- `persona_<id>.yaml`

---

## 核心格式

### Seed（seeds/）

```json
{
  "seed_version": "0.1",
  "run_id": "seed_20251230_001",
  "layer": "seeds",
  "content": {
    "title": "標題",
    "body": "內容"
  },
  "source": "manual",
  "created_at": "2025-12-30T09:00:00+08:00"
}
```

### Mistake（mistakes/）

```json
{
  "mistake_id": "20251230_001",
  "timestamp": "2025-12-30T12:10:00",
  "type": "false_claim",
  "description": "錯誤描述",
  "context": "觸發情境",
  "lesson": "教訓",
  "prevention": "預防方式"
}
```

### Pattern（patterns/）

```json
{
  "pattern_id": "code_review",
  "name": "Code Review",
  "when": "需求為 code review",
  "steps": ["列出風險", "提出修正", "補測試"],
  "success_rate": 0.85,
  "last_used": "2025-12-30"
}
```

### Skill（skills/）

```json
{
  "skill_version": "1.0",
  "skill_id": "chat_prompts",
  "name": "Chat Prompt",
  "category": "LLM",
  "knowledge": {
    "description": "技能摘要",
    "key_points": ["要點1", "要點2"]
  },
  "criteria": {
    "pass_rate": 0.8,
    "last_evaluated": "2025-12-30"
  }
}
```

---

## Ledger 檔案

### conversation_ledger.jsonl

```json
{
  "record_id": "20251230121000",
  "timestamp": "2025-12-30T12:10:00",
  "type": "council_decision",
  "persona_id": "fullstack_engineer",
  "context": {
    "user_message": "請整理今日進度"
  },
  "council": {
    "guardian": "...",
    "analyst": "...",
    "critic": "...",
    "advocate": "..."
  },
  "response": "回覆內容",
  "status": "success"
}
```

### conversation_summary.jsonl

```json
{
  "summary_id": "summary_20251230121000",
  "record_id": "20251230121000",
  "timestamp": "2025-12-30T12:10:00",
  "status": "success",
  "user_message": "請整理今日進度",
  "assistant_summary": "摘要內容",
  "persona": {
    "id": "fullstack_engineer",
    "trace_record_id": "20251230121000",
    "vector_estimate": {"deltaT": 0.4, "deltaS": 0.6, "deltaR": 0.8},
    "vector_distance": {"mean": 0.1, "max": 0.2}
  },
  "intent": {
    "status": "achieved",
    "confidence": 0.7
  },
  "control": {
    "status": "success",
    "log": "已截圖"
  },
  "run_id": "20251230T121000Z_123456"
}
```

### persona_trace.jsonl

```json
{
  "record_id": "20251230121000",
  "timestamp": "2025-12-30T12:10:00",
  "persona_id": "fullstack_engineer",
  "status": "success",
  "diff": {"delta_len": -12, "changed": true},
  "shadow": {
    "method": "heuristic_v0",
    "vector_estimate": {"deltaT": 0.4, "deltaS": 0.6, "deltaR": 0.8},
    "vector_distance": {"mean": 0.1, "max": 0.2}
  }
}
```

### persona_dimension_ledger.jsonl

```json
{
  "record_id": "20251230121000",
  "timestamp": "2025-12-30T12:10:00",
  "persona_id": "fullstack_engineer",
  "valid": false,
  "reasons": ["deltaR_out_of_range"],
  "vector": {"deltaT": 0.4, "deltaS": 0.6, "deltaR": 1.2}
}
```

---

## 備註

- 所有 ledger 使用 JSONL（每行一筆）。
- 可透過 `tonesoul52.run_conversation_summary_backfill` 回補摘要。

---

**Antigravity**  
2025-12-30T02:10 UTC+8
