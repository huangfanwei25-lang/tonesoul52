# OpenClaw 完整整合任務

## 🎯 目標

將 OpenClaw 開源框架完整整合到 ToneSoul52，建立免費可用的治理層基礎設施。

---

## 📋 整合清單

### 1. Gateway 協議整合

- [x] 建立 `tonesoul/gateway/` 目錄
- [x] 實作 WebSocket 客戶端連接 `ws://127.0.0.1:18789`
- [x] 整合 Session 模型到 Genesis 責任鏈
- [x] 建立 Channel 路由配置

**檔案**:
- `tonesoul/gateway/__init__.py`
- `tonesoul/gateway/client.py`
- `tonesoul/gateway/session.py`

---

### 2. Skills 平台整合

- [x] 將 BenevolenceFilter 包裝成 OpenClaw Skill
- [x] 將 Council 系統包裝成 OpenClaw Skill
- [x] 建立 Skill 註冊機制
- [x] 更新 `integrations/openclaw/skills/`

**檔案**:
- `integrations/openclaw/skills/tonesoul/SKILL.md`
- `integrations/openclaw/skills/tonesoul/benevolence.py`
- `integrations/openclaw/skills/tonesoul/council.py`

---

### 3. Responsibility Chain Auditor 整合

- [x] 將仁慈函數整合到 OpenClaw 審計流程
- [x] 實作三層審計 Hook：
  - 屬性歸屬檢查
  - 影子路徑追蹤
  - 仁慈函數判定
- [x] 建立審計日誌格式

**檔案**:
- `tonesoul/openclaw_auditor.py`

---

### 4. Heartbeat + Cron 整合

- [x] 實作定時責任審計
- [x] 建立 Heartbeat 協議
- [x] 整合 Council 定期檢查

**檔案**:
- `tonesoul/heartbeat.py`

---

### 5. 文件更新

- [x] 更新 `integrations/openclaw/SOUL.md`
- [x] 建立 `integrations/openclaw/README.md`
- [x] 更新主倉庫 README.md

---

## 🔧 免費架構限制

| 資源 | 策略 |
|------|------|
| **無 API 費用** | 使用本地模型或免費配額 |
| **無雲服務** | 本地 Gateway（localhost） |
| **無付費依賴** | 只用開源套件 |

---

## 📐 技術規格

### Gateway 連接

```python
# tonesoul/gateway/client.py
import websockets
import asyncio

class GatewayClient:
    def __init__(self, uri="ws://127.0.0.1:18789"):
        self.uri = uri
        self.connected = False
    
    async def connect(self):
        self.ws = await websockets.connect(self.uri)
        self.connected = True
    
    async def send_audit(self, audit_result):
        await self.ws.send(json.dumps({
            "type": "audit",
            "payload": audit_result.to_dict()
        }))
```

### Skill 格式

```markdown
# tonesoul/SKILL.md
---
name: ToneSoul Governance
version: 1.0.0
description: AI responsibility and governance layer
author: Fan1234-1
---

## Tools
- benevolence_audit: Run CPT benevolence filter
- council_deliberate: Multi-perspective council review
- genesis_track: Track responsibility chain
```

---

## ⏳ 預計時間

| 階段 | 時間 |
|------|------|
| Gateway 整合 | 30 分鐘 |
| Skills 整合 | 20 分鐘 |
| Auditor 整合 | 15 分鐘 |
| Heartbeat | 10 分鐘 |
| 文件 | 10 分鐘 |
| **總計** | **~85 分鐘** |

---

## 🤖 執行者

**交給 Codex 執行**

Codex 應該：
1. 閱讀此任務文件
2. 研究 OpenClaw 原始碼
3. 逐步實作每個整合項目
4. 完成後更新此文件的清單狀態
