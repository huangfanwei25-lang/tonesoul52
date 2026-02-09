# Web Chat Debug Notes

## 2026-02-09 發現

### 問題
- 訊息輸入後清除，但無回應
- Chat 區域空白

### 根因
`ChatInterface.tsx:1080`:
```javascript
if (!input.trim() || isLoading || !conversation) return;
```
**如果沒有選中對話，訊息會被靜默丟棄。**

### 關鍵程式碼
| 行號 | 說明 |
|------|------|
| 1079-1174 | `sendMessage()` 函數 |
| 1180-1188 | 無對話時的 fallback UI |
| 681-686 | Backend vs Legacy Provider 模式切換 |

### 環境變數
- `NEXT_PUBLIC_CHAT_EXECUTION_MODE` - 控制後端 vs 前端 API
- `NEXT_PUBLIC_ENABLE_PROVIDER_FALLBACK` - 啟用 fallback

### 修復選項
1. 確保發送前有選中對話
2. 無對話時自動建立
3. 顯示明確錯誤訊息
