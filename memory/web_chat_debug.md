# Web Chat Debug Notes

## 2026-02-09 調查摘要

### 前端問題
1. `ChatInterface.tsx:1080` - `if (!conversation) return;` 在無對話時靜默丟棄訊息
2. 瀏覽器自動化用 `input.value='text'` **不會觸發** React `setInput()` 狀態更新
3. 發送前必須選中對話

### Codex 已修復狀態 (from agent_discussion.jsonl)

| Topic | Status | 說明 |
|-------|--------|------|
| `vercel-output-bug-investigation-phase36` | ✅ final | mock_fallback 問題已修復 (commit=1963997) |
| `perspective_factory_model_consistency` | ✅ shipped | model cache key by model 已修正 (commit=af4ab5a) |
| `model_registry_governance` | ✅ shipped | deep-copy 安全 + 測試 (commit=205c68b) |
| `llm_fallback_hardening` | ✅ shipped | 無 API key 時跳過初始化 (commit=6993540) |

### 後端狀態
- `perspective_factory.py` - LLMPerspective 正常運作，有 fallback
- `model_registry.py` - 多模型配置存在 (guardian→1.5-pro, analyst→2.0-flash)
- Default model: `gemini-2.0-flash` ✓

### 當前狀態
- 前端 Chat 需要: (1) API key 設定, (2) 選中對話
- 後端 Council/Perspective 系統健康
- Vercel 需確認 `TONESOUL_BACKEND_URL` 設定

### 下一步
1. 前端 UX: 無對話時自動建立
2. 用真實用戶互動測試 (非 JS 自動化)
3. 驗證 Vercel 環境變數配置
