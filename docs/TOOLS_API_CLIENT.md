# Tools API 客戶端設計

> Purpose: define the dedicated tools API client structure, credential loading, and error-handling posture.
> Last Updated: 2026-03-23

此文件定義 tools 專用的 API 客戶端結構，統一憑證取得與錯誤處理。

**目標**

- 統一 Moltbook API 呼叫方式與回傳格式。
- 憑證優先順序：環境變數 > `.moltbook/credentials.json`。
- 移除硬編碼金鑰。

**憑證來源**

1. **環境變數（優先）**  
   格式：`MOLTBOOK_API_KEY_<ACCOUNT>`  
   `<ACCOUNT>` 為帳號名稱大寫並將非英數轉 `_`。  
   例：`ToneSoul` → `MOLTBOOK_API_KEY_TONESOUL`

2. **JSON 檔案**  
   路徑：`.moltbook/credentials.json`（已被 `.gitignore`）  
   格式：
   ```json
   {
     "accounts": {
       "ToneSoul": { "api_key": "<MOLTBOOK_API_KEY>", "name": "ToneSoul" },
       "Tone": { "api_key": "<MOLTBOOK_API_KEY>", "name": "Tone (Advocate)" }
     }
   }
   ```

**API Client 介面草案**

```python
@dataclass
class ApiCredentials:
    name: str
    api_key: str

class CredentialsResolver:
    def resolve(self, account_name: str) -> ApiCredentials:
        ...

class MoltbookClient:
    def __init__(self, resolver: CredentialsResolver, base_url: str = "https://www.moltbook.com/api/v1"):
        ...
    def create_post(self, account: str, submolt: str, title: str, content: str) -> Dict[str, object]:
        ...
    def create_comment(self, account: str, post_id: str, content: str) -> Dict[str, object]:
        ...
    def get_posts(self, account: str, submolt: str | None = None, sort: str | None = None, query: str | None = None) -> Dict[str, object]:
        ...
    def get_post(self, account: str, post_id: str) -> Dict[str, object]:
        ...
```

**錯誤處理規範**

- 遇到非 2xx 回應需回傳結構化錯誤 `{ "error": "...", "status": <code> }`
- 不直接 `print` 未處理的 token 或內容
- 工具腳本應回傳資料給呼叫者，由上層決定輸出格式

