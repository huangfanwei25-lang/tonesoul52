# Tools API Schema

> Purpose: standardize the output envelope used by `tools/` surfaces so responses stay traceable and testable.
> Last Updated: 2026-03-23

目的是讓 `tools/` 底下的輸出格式一致、可追蹤、可測試。

欄位定義
- `success`: 布林值，代表工具是否成功。
- `data`: 成功時的資料內容，型別為物件、陣列或 `null`。
- `error`: 失敗時的錯誤物件，或 `null`。
- `genesis`: 觸發來源（例如 `reactive_social`）。
- `responsibility_tier`: 由 `genesis` 映射的責任層級（`TIER_1` / `TIER_2` / `TIER_3`）。
- `intent_id`: 事件或請求的識別字串，可為 `null`。

錯誤物件格式
- `code`: 錯誤碼（`E001`~`E999`）。
- `message`: 可讀錯誤訊息。
- `details`: 可選的詳細資訊物件。

錯誤碼約定
- `E001` Invalid input
- `E002` Missing credentials
- `E003` Network error
- `E004` Upstream error
- `E010` Governance blocked
- `E999` Internal error

機器可驗證 Schema
- `spec/tools/tool_response.schema.json`

成功範例
```json
{
  "success": true,
  "data": {
    "payload": {"id": "abc123"},
    "post_id": "abc123"
  },
  "error": null,
  "genesis": "reactive_social",
  "responsibility_tier": "TIER_2",
  "intent_id": "moltbook:abc123"
}
```

失敗範例
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "E004",
    "message": "Upstream API error",
    "details": {"status": 401}
  },
  "genesis": "reactive_social",
  "responsibility_tier": "TIER_2",
  "intent_id": null
}
```
