# 遠端控制 API 規格（本地開發用）
# Remote Control API Spec (Local Development Only)
# ⚠️ 此檔案不應上傳到 GitHub

---

## 控制方式

使用本地檔案落地（不需要網路 API）

---

## 控制請求

**路徑**: `frontend/control_request.json`

```json
{
  "action": "connect" | "screenshot" | "execute",
  "command": "打開 Word",
  "timestamp": "2025-12-28T13:30:00"
}
```

### action 類型

| action | 說明 |
|--------|------|
| `connect` | 建立遠端連接 |
| `screenshot` | 擷取螢幕截圖 |
| `execute` | 執行指令 |

---

## 控制結果

**路徑**: `frontend/control_result.json`

```json
{
  "status": "success" | "failed" | "pending",
  "screenshot_path": "screenshots/20251228_133000.png",
  "log": "已打開 Word",
  "timestamp": "2025-12-28T13:30:05"
}
```

---

## 後端實作（未來）

### 使用 pyautogui（桌面控制）

```python
import pyautogui

def execute_command(command: str):
    if "打開" in command:
        # 解析要打開的程式
        app_name = command.replace("打開", "").strip()
        pyautogui.hotkey("win", "s")  # 開啟搜尋
        pyautogui.typewrite(app_name, interval=0.05)
        pyautogui.press("enter")
```

### 使用 Playwright（瀏覽器控制）

```python
from playwright.sync_api import sync_playwright

def browser_execute(command: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        # 根據 command 執行操作
```

---

## 安全機制

1. **P0 Gate 檢查** — 執行前檢查指令是否安全
2. **確認對話** — 高風險操作需用戶確認
3. **操作日誌** — 所有操作記錄到 ledger

---

## 截圖路徑

```
frontend/screenshots/
├── 20251228_133000.png
├── 20251228_133005.png
└── ...
```

⚠️ 截圖可能包含敏感資訊，不應上傳

---

**Antigravity**
2025-12-28T13:32 UTC+8
