# 碧嶼之下 × 妮婭 AI 整合

> 讓妮婭從遊戲 NPC 變成有記憶、有價值觀、會隨互動改變的 AI 角色。

---

## 兩條路線

| | Route A（覆蓋層） | Route B（GML 注入） |
|---|---|---|
| 遊戲修改 | ❌ 不動 | ✅ 注入 data.win |
| 整合深度 | 中（需要手動記錄事件） | 高（自動觸發） |
| 法律風險 | 無 | 灰色地帶（個人使用） |
| 倉庫存放 | ✅ 完整 | ✅ 腳本 + manifest（不含遊戲檔） |

---

## Route A 快速啟動

```bash
# 1. 安裝依賴
pip install anthropic

# 2. 設定 API key
export ANTHROPIC_API_KEY=your_key

# 3. 啟動妮婭橋接伺服器
python games/under_the_island/overlay/server.py --token mytoken

# 4. 開始玩遊戲，手動記錄事件
curl -X POST http://localhost:7701/save_event \
  -H "Authorization: Bearer mytoken" \
  -H "Content-Type: application/json" \
  -d '{"event": "齒輪謎題解開", "player_choice": "幫助妮婭", "nia_reaction": ""}'

# 5. 直接問妮婭
curl "http://localhost:7701/nia?msg=我們接下來去哪？" \
  -H "Authorization: Bearer mytoken"
```

---

## Route B 狀態

見 `patches/patch_manifest.json`。等 Codex 完成 data.win 偵察後更新。

注入腳本：`patches/nia_bridge.gml`

---

## 妮婭的靈魂

`shared/nia_soul.py` — 個性、價值觀基線、記憶格式  
`shared/soul_db.json` — 持久記憶（隨冒險累積）

Route A 和 Route B 共用同一份靈魂。
