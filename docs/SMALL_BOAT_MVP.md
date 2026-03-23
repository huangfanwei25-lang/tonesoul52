# 🚤 小船 MVP — 語魂本地多模型部署設計

> Purpose: local-first MVP plan for running a smaller on-device ToneSoul stack under limited hardware constraints.
> Last Updated: 2026-03-23

> **日期**：2026-02-14
> **狀態**：設計稿，待 Fan 審閱
> **前提**：環境開通後手動部署

---

## 目標

在本地跑起語魂全管線，用 Ollama 同時調用多個小模型，零雲端成本。

---

## 1. 硬體需求

| 項目 | 最低 | 建議 |
|------|:----:|:----:|
| RAM | 8 GB | 16 GB |
| 磁碟 | 5 GB | 10 GB |
| GPU | 不需要 | 有更好（CUDA/Metal 加速） |
| OS | Windows 10+ | 同左 |

---

## 2. 模型選擇

Ollama 同時載入多模型時，每個模型佔用獨立 RAM。所以要選**最小但堪用**的組合。

### 方案 A：極省 RAM（8GB 筆電）

| 角色 | 模型 | 大小 | 用途 |
|------|------|:----:|------|
| 主對話 | `qwen2.5:3b` | 1.9 GB | 一般回應生成 |
| 議會全員 | 同上（共用） | 0 GB | 用不同 system prompt 區分 |

**總 RAM 佔用**：~3 GB（剩 5 GB 給系統）

### 方案 B：多模型異質化（16GB）

| 角色 | 模型 | 大小 | 為什麼選它 |
|------|------|:----:|-----------|
| 主對話 + Arbiter | `llama3:8b` | 4.7 GB | 綜合能力最強 |
| Guardian | `qwen2.5:3b` | 1.9 GB | 快速安全判斷 |
| Philosopher | `phi3:mini` | 2.3 GB | 偏推理能力 |
| Engineer | 純 Python 規則 | 0 GB | 不需要 LLM |

**總 RAM 佔用**：~9 GB（剩 7 GB 給系統）

### 方案 C：單模型 + Cost Gate（推薦起步方案）

| 角色 | 模型 | 大小 | 備註 |
|------|------|:----:|------|
| 全部 | `qwen2.5:7b` | 4.4 GB | 單一模型最佳性價比 |

低張力：直接回應（1 次呼叫）
高張力：開議會（3 次呼叫，同一模型不同 prompt）

**總 RAM 佔用**：~5 GB

> **建議先用方案 C 起步**，等跑穩了再升級到方案 B。

---

## 3. 現有代碼盤點

語魂已經有多模型支援的基礎設施：

### ✅ 已完成（不需要改）

| 檔案 | 功能 | 狀態 |
|------|------|:----:|
| `tonesoul/llm/ollama_client.py` | Ollama HTTP 客戶端 | ✅ 完整 |
| `tonesoul/council/model_registry.py` | 視角→模型映射 | ✅ 已有 3 種配置 |
| `tonesoul/council/pre_output_council.py` | 議會驗證流程 | ✅ 支援 perspective_config |
| `tonesoul/unified_pipeline.py` | `LLM_BACKEND=ollama` 切換 | ✅ 已有 |

### 🔨 需要新增/修改

| 項目 | 說明 | 工作量 |
|------|------|:------:|
| **Ollama 模型映射** | `model_registry.py` 新增 `OLLAMA_COUNCIL_CONFIG` | ~20 行 |
| **多模型 OllamaClient** | 讓 `create_ollama_client(model=...)` 支援同時存在多個實例 | ~10 行 |
| **Cost Gate 路由** | 在 `unified_pipeline.process()` 裡加 tension 閾值判斷 | ~30 行 |
| **啟動腳本** | 一鍵拉模型 + 啟動的 shell script | ~15 行 |

**總工作量：~75 行代碼**

---

## 4. 多模型同時調用原理

Ollama 天生支援同一台機器跑多個模型。呼叫時只要指定不同的 `model` 參數：

```python
# 同一個 Ollama server，不同模型
main_client = OllamaClient(model="llama3:8b")        # 主對話
guardian_client = OllamaClient(model="qwen2.5:3b")    # Guardian
philosopher_client = OllamaClient(model="phi3:mini")  # Philosopher

# 它們共用同一個 http://localhost:11434
# Ollama 會自動管理模型載入/卸載
```

### 注意事項
1. **首次呼叫較慢**：模型需從磁碟載入 RAM（~5-10 秒）
2. **RAM 不夠時**：Ollama 會自動卸載最久沒用的模型（LRU）
3. **平行呼叫**：Ollama 支援，但 RAM 需同時容納所有活躍模型

---

## 5. 新增的模型映射配置

```python
# model_registry.py 新增

OLLAMA_COUNCIL_CONFIG = {
    # 方案 B：異質多模型
    "guardian": {"mode": "llm", "model": "qwen2.5:3b"},
    "analyst":  {"mode": "rules"},                       # 零成本
    "critic":   {"mode": "llm", "model": "phi3:mini"},
    "advocate": {"mode": "rules"},                       # 零成本
    "axiomatic": {"mode": "rules"},                      # 確定性
}

OLLAMA_SINGLE_CONFIG = {
    # 方案 C：單模型 + Cost Gate
    "guardian":  {"mode": "llm", "model": "qwen2.5:7b"},
    "analyst":   {"mode": "rules"},
    "critic":    {"mode": "llm", "model": "qwen2.5:7b"},
    "advocate":  {"mode": "rules"},
    "axiomatic": {"mode": "rules"},
}
```

---

## 6. Cost Gate 路由邏輯

```python
# unified_pipeline.py 新增（process() 方法內）

# Step 2.5: Cost Gate — 決定是否啟動議會
COUNCIL_TENSION_THRESHOLD = float(
    os.getenv("COUNCIL_TENSION_THRESHOLD", "0.5")
)

if tension_score < COUNCIL_TENSION_THRESHOLD:
    # 快路徑：不開議會，直接回應
    council_verdict = _skip_council_default_verdict()
else:
    # 慢路徑：啟動議會（多模型）
    council_verdict = self._get_council().validate(
        draft_output=draft_response,
        context=context,
    )
```

---

## 7. 啟動腳本

```powershell
# scripts/start_local.ps1

Write-Host "🚤 語魂小船 — 本地啟動" -ForegroundColor Cyan

# 1. 確認 Ollama 在跑
$ollama = Get-Process ollama -ErrorAction SilentlyContinue
if (-not $ollama) {
    Write-Host "啟動 Ollama..." -ForegroundColor Yellow
    Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep 3
}

# 2. 拉模型（首次才需要）
Write-Host "確認模型..." -ForegroundColor Yellow
ollama pull qwen2.5:7b    # 方案 C 主模型

# 如果要方案 B，取消下面的註解：
# ollama pull llama3:8b
# ollama pull qwen2.5:3b
# ollama pull phi3:mini

# 3. 設定環境變數
$env:LLM_BACKEND = "ollama"
$env:COUNCIL_TENSION_THRESHOLD = "0.5"

# 4. 啟動語魂後端
Write-Host "啟動語魂..." -ForegroundColor Green
python -m tonesoul.server

Write-Host "✅ 語魂已在本地運行" -ForegroundColor Green
```

---

## 8. 效能預估

| 場景 | 模型呼叫次數 | 預估延遲 | RAM |
|------|:----------:|:-------:|:---:|
| 低張力日常對話 | 1 次 | 2-5 秒 | 5 GB |
| 高張力議會（方案 C） | 3 次同模型 | 6-15 秒 | 5 GB |
| 高張力議會（方案 B） | 3 次異模型 | 8-20 秒 | 9 GB |
| 純 Python 步驟（衰減/圖譜/圖鏈） | 0 次 | <100 ms | 0 |

---

## 9. 驗證清單

- [x] `ollama list` 確認模型已下載
- [x] `LLM_BACKEND=ollama python -c "from tonesoul.llm import create_ollama_client; c = create_ollama_client(); print(c.generate('hello'))"` 成功回應
- [x] 低張力訊息不觸發議會（看 log 確認 `council skipped`）
- [x] 高張力訊息觸發議會（看 log 確認 `council activated`）
- [x] `pytest tests/ -x -q` 現有 849 tests 不受影響

建議改用單一指令驗證以上 5 項：
`python scripts/verify_ollama_mvp.py --run-regression`

---

## 10. 未來升級路徑

```
現在：方案 C（單模型 qwen2.5:7b + Cost Gate）  ← 起步
  ↓
穩定後：方案 B（異質多模型 llama3 + qwen + phi3）
  ↓
進階：方案 B + 雲端備援（tension > 0.8 → Gemini API）
  ↓
遠期：章魚架構（每條手臂一個專業化模型）
```

---

## 11. 蜂群審計補充（AI 公司團隊型態）

> 目的：把「技術可跑」升級成「團隊可營運、可擴張、可商業化」。

### 11.1 團隊拓撲（Swarm Org）

建議公司型態採「一個核心 + 三個專業群」：

| 單位 | 主要責任 | 對應語魂模組 |
|------|---------|-------------|
| **Swarm Core（核心）** | 決策整合、路線治理、跨組協調 | `unified_pipeline`, `pre_output_council`, cost gate |
| **Safety/Ops 群** | Guardian 策略、SLO、事故處理 | fail-fast、workflow、runbook |
| **Reasoning/Data 群** | 模型選型、議會品質、評估指標 | `model_registry`, `persona_swarm` metrics |
| **Product/GTM 群** | 方案包裝、價值主張、客戶導入 | 價格層、部署流程、培訓與交付 |

核心原則：
1. 中央不做微管理，只做「規則、閾值、升降級決策」。
2. 每群有明確 owner，跨群透過固定節奏同步，而非即時拉扯。

### 11.2 權責邊界（Ownership / RACI）

| 決策項目 | Responsible | Accountable | Consulted |
|---------|-------------|-------------|-----------|
| `COUNCIL_TENSION_THRESHOLD` 調整 | Safety/Ops | Swarm Core Lead | Reasoning/Data |
| 模型映射變更（B/C 方案） | Reasoning/Data | Swarm Core Lead | Safety/Ops |
| 事故分級與復原 | Safety/Ops | Ops Lead | Swarm Core |
| 價格與方案層級 | Product/GTM | Product Lead | Swarm Core, Finance |

### 11.3 治理節奏（Tension Council）

建議固定三層會議節奏：
1. **Daily 15m**：昨日錯誤率、平均延遲、觸發議會比例。
2. **Weekly 45m**：fail-fast 觸發案例審查 + 閾值調整提案。
3. **Bi-weekly 60m**：模型層級/方案層級調整（是否由 C 升 B，或加入雲端備援）。

### 11.4 可靠性基線（SLO + On-call）

最小可營運 SLO：
1. 低張力快路徑：`p95 < 5s`，可用性 `>= 99%`
2. 高張力議會：`p95 < 15s`，可用性 `>= 95%`
3. Swarm artifact 產生成功率：`>= 99%`

On-call 機制：
1. Primary（工程）+ Secondary（Ops）雙值班。
2. 事故分級：
   - Sev1：Ollama 無法回應 / pipeline 全斷
   - Sev2：議會持續超時或 fail-fast 異常飆升
3. 每次事故都要留下 postmortem（時間線、根因、修復、預防）。

### 11.5 Runbook（最小版本）

1. **Ollama 不可用**
   - 重啟 `ollama serve`
   - 驗證 `ollama list`
   - 跑 smoke 指令確認回應
2. **延遲暴增**
   - 檢查 RAM 佔用與模型是否頻繁換入換出
   - 暫時提高快路徑比例（調整 tension threshold）
3. **議會過度跳過/過度啟動**
   - 對照 `tension_score` 分布與實際 route
   - 校正 threshold 與 fail-fast 條件

### 11.6 商業化結構（Unit Economics）

建議先定義三層產品包：

| 方案 | 技術層 | 目標客群 | 商業定位 |
|------|-------|---------|---------|
| **Starter** | 方案 C（單模型 + cost gate） | 個人/小團隊 | 低成本快速落地 |
| **Pro** | 方案 B（異質模型議會） | 中小企業 | 平衡品質與成本 |
| **Enterprise Guarded** | B + 高張力雲端備援 | 高風險場景 | 安全優先與審計可追蹤 |

每個方案至少追蹤：
1. 每日活躍 session
2. 平均每 session 成本（token + latency proxy）
3. 人工審核節省時數
4. 方案升級率（Starter -> Pro）

### 11.7 90 天落地路線（公司節奏）

1. **Day 1-14（可跑）**
   - 方案 C 穩定啟動
   - 建立基本監控與 incident 模板
2. **Day 15-45（可管）**
   - 上線 fail-fast + cost tier + CI artifact
   - 跑每週治理會議，固定調 threshold
3. **Day 46-90（可賣）**
   - 推出 Starter/Pro 兩層包
   - 完成 2-3 個導入案例與 ROI 數據

### 11.8 審計結論（給團隊）

這份小船 MVP 已經不是只有「本地可跑」。
若補上上述組織與治理層，它就會變成：

1. 可營運：有人值班、可回復、可追責
2. 可擴張：有分工、可複製、可逐層升級
3. 可商業：有方案層、成本層、價值層

也就是從「工程草稿」轉為「AI 公司最小作業系統（Company OS）」。
