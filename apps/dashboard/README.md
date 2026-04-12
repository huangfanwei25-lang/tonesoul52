# ToneSoul Dashboard

語魂治理儀表板 — 讓 AI 的治理狀態一目了然。

## 需求

- Python 3.10+
- Streamlit (`pip install streamlit`)
- Ollama（對話功能需要）

## 安裝

```bash
# 安裝 Python 依賴
pip install streamlit requests pyyaml

# 安裝 Ollama（對話功能需要）
# 到 https://ollama.com 下載安裝
# 然後拉取模型：
ollama pull llava
```

## 啟動

```bash
# 一鍵啟動（自動開瀏覽器）
python scripts/launch_dashboard.py

# 或手動啟動
streamlit run apps/dashboard/frontend/app.py

# 指定 port
python scripts/launch_dashboard.py --port 8502

# 不開瀏覽器
python scripts/launch_dashboard.py --no-browser
```

## 功能

| 頁面 | 功能 |
|---|---|
| 首頁 | 治理狀態總覽、壓力指數、誓言卡片 |
| 對話工作區 | 與 AI 對話，每個回應經過 Council 審議 |
| AI 記憶 | 查看和新增 AI 的長期記憶 |
| 決策回顧 | 每次決策的審議記錄和追溯 |

## 記憶指令

在對話工作區中說「記住 XXX」或「幫我記 XXX」，AI 會自動存入長期記憶。

也可以在「AI 記憶」頁面右側的表單手動新增。

## 環境變數

| 變數 | 預設 | 說明 |
|---|---|---|
| `TS_MODEL` | `llava` | Ollama 模型名稱 |
| `TS_WEB_SEARCH_ENDPOINT` | （無） | 網路搜尋端點 |
