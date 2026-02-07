# ToneSoul 架構邊界與責任劃分

## 🏗️ 三層架構

```
┌─────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                     │
│  (apps/, integrations/, tools/)                         │
│  使用者介面、外部整合、工具腳本                           │
├─────────────────────────────────────────────────────────┤
│                    GOVERNANCE LAYER                      │
│  (tonesoul/)                                            │
│  核心治理邏輯、審計系統、責任追蹤                         │
├─────────────────────────────────────────────────────────┤
│                    INFRASTRUCTURE LAYER                  │
│  (memory/, gateway/, law/)                              │
│  資料儲存、通訊協議、法律框架                            │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 目錄責任劃分

### 核心治理 (`tonesoul/`)

| 子目錄 | 責任 | 資安等級 |
|--------|------|----------|
| `benevolence.py` | 仁慈函數審計 | 🔴 高 |
| `semantic_control.py` | 語義張力計算 | 🟡 中 |
| `tsr_metrics.py` | TSR 指標 | 🟢 低 |
| `unified_core.py` | 統一控制器 | 🔴 高 |
| `gateway/` | OpenClaw 通訊 | 🔴 高 |
| `memory/` | 記憶存取 | 🟡 中 |

### 整合層 (`integrations/`)

| 子目錄 | 責任 | 隔離策略 |
|--------|------|----------|
| `openclaw/` | OpenClaw 治理橋接 | 沙盒執行 |
| `anthropic/` | Claude 整合 | API 限流 |
| `gemini/` | Gemini 整合 | API 限流 |

### 資料層 (`memory/`)

| 檔案類型 | 敏感度 | 存取控制 |
|----------|--------|----------|
| `*.jsonl` | 🟡 中 | 追加唯讀 |
| `*.db` | 🔴 高 | 加密建議 |
| `ANTIGRAVITY_SYNC.md` | 🟢 低 | 公開 |

---

## 🛡️ 資安邊界

### 1. 輸入驗證邊界

```python
# 所有外部輸入必須經過
class InputValidator:
    def validate(self, input) -> ValidatedInput:
        # 1. 類型檢查
        # 2. 長度限制
        # 3. 惡意內容過濾
        pass
```

### 2. 審計邊界

```python
# 所有決策必須經過
class AuditBoundary:
    def audit(self, action) -> AuditResult:
        # 1. 屬性歸屬檢查
        # 2. 影子路徑追蹤
        # 3. 仁慈函數判定
        pass
```

### 3. 輸出過濾邊界

```python
# 所有輸出必須經過
class OutputFilter:
    def filter(self, output) -> SafeOutput:
        # 1. 敏感資訊移除
        # 2. 格式驗證
        # 3. 責任標記
        pass
```

---

## 📊 審計圖分層

### Level 1: 操作審計
- 記錄：誰做了什麼
- 位置：`memory/audit_log.jsonl`

### Level 2: 治理審計
- 記錄：Council 決策過程
- 位置：`memory/council_decisions.jsonl`

### Level 3: 責任審計
- 記錄：Genesis 責任鏈
- 位置：`memory/genesis_ledger.jsonl`

### Level 4: 安全審計
- 記錄：安全事件
- 位置：`memory/security_events.jsonl`

---

## 🔒 敏感資料處理

### 絕對不可存儲

- API 金鑰
- 使用者密碼
- 第三方認證 token

### 加密存儲

- 個人識別資訊
- 對話歷史（含敏感內容）
- 責任鏈紀錄

### 明文存儲

- 審計日誌（脫敏後）
- 系統設定
- 架構文件

---

## 📐 模組依賴規則

```
Application → Governance → Infrastructure
     ↓              ↓              ↓
   禁止反向依賴（違反會造成混亂）
```

### 允許

```python
# apps/web/... 可以 import tonesoul/...
from tonesoul.benevolence import BenevolenceFilter
```

### 禁止

```python
# tonesoul/... 不可 import apps/...
from apps.web.something import X  # ❌ 違反分層
```

---

## ✅ 責任檢查清單

每次修改代碼前：

- [ ] 這個修改屬於哪一層？
- [ ] 是否遵守依賴規則？
- [ ] 是否需要審計紀錄？
- [ ] 是否涉及敏感資料？
- [ ] 是否需要安全審查？

---

## 🤖 AI 協作責任

### Antigravity 負責

- 架構設計
- 使用者互動
- 瀏覽器操作
- 快速原型

### Codex 負責

- 深度實作
- 程式碼品質
- 測試驗證
- 長時間任務

### 共同責任

- 記憶同步 (`memory/agent_discussion.jsonl`)
- 任務追蹤 (`CODEX_TASK.md`)
- 架構遵守
