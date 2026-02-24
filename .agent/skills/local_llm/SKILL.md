---
name: "local_llm"
description: "Use when you need to delegate subtasks to the local Qwen3 model via Ollama. This skill provides a secure, offline interface to the local language model for content drafting, analysis, translation, and other text tasks without sending data to external APIs."
l1_routing:
  name: "Local LLM"
  triggers:
    - "local llm"
    - "ollama"
    - "qwen3"
    - "offline model"
  intent: "Delegate secure offline subtasks to Ollama-hosted local models."
l2_signature:
  execution_profile:
    - "engineering"
  trust_tier: "reviewed"
  json_schema:
    type: "object"
    properties:
      prompt:
        type: "string"
      task:
        type: "string"
      constraints:
        type: "array"
        items:
          type: "string"
    required:
      - "prompt"
---

# Local LLM Skill (Ollama + Qwen3)

本技能讓 AI 助手能夠透過 Ollama 呼叫本地 Qwen3:4b 模型來執行子任務。
所有推理完全在本機進行，不需要網路連線。

## 系統資訊

```yaml
model: qwen3:4b
runtime: Ollama v0.13.5
gpu: NVIDIA GTX 1070 (8GB VRAM)
ram: 40GB
api_endpoint: http://localhost:11434
```

## ⚠️ 關鍵限制（實測驗證 2026-02-21）

> [!CAUTION]
> **qwen3 預設啟用 thinking mode。**
> 若不設定 `think: false`，所有 tokens 會消耗在隱藏推理上，
> 導致 API 回傳空字串。**每次呼叫都必須加 `"think": false`。**

### 能力邊界（根據 AdaptiveGate 程式碼審查實測）

| 任務類型 | 適合度 | 實測結果 | 說明 |
|---------|:------:|---------|------|
| 翻譯 | ✅ 好 | — | 中英互譯，速度可接受 |
| 摘要 | ✅ 好 | — | 壓縮長文到重點 |
| 草稿生成 | ✅ 好 | — | commit message、文件初稿、格式轉換 |
| 格式轉換 | ✅ 好 | — | JSON↔YAML↔Markdown |
| 簡單程式碼分析 | 🟡 中 | 可辨識結構 | 能列出表面問題但不深入 |
| 深度程式碼審查 | 🔴 弱 | 70% tokens 花在重述 | 4B 模型無法做有效的深度分析 |
| 複雜推理 | 🔴 弱 | — | 推理鏈容易斷裂 |
| 圖片理解 | ❌ 否 | — | 需要多模態模型 |

> **定位**：龍蝦是打字員，不是副駕駛。用它做「生成」，不要期望它做「判斷」。

## 前置檢查

在使用前，確認 Ollama 正在運行：

```powershell
# Windows PowerShell
python -c "import requests; r=requests.get('http://localhost:11434/'); print(r.text.strip())"

# 如果未運行，從開始選單啟動 Ollama 應用程式
```

## 使用方式

### 標準呼叫（必須用這個格式）

```python
import requests

def ask_local_llm(prompt, system="你是 ToneSoul 的子代理", model="qwen3:4b"):
    """呼叫本地 Qwen3 模型。

    重要：必須使用 chat API + think=False，否則回傳空字串。
    """
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "think": False,       # ← 關鍵！關閉 thinking mode
            "options": {
                "temperature": 0.7,
                "num_predict": 512,  # 4B 模型建議限制在 512 以內
            },
        },
        timeout=120,
    )
    return response.json().get("message", {}).get("content", "")
```

### 委派子任務的最佳實踐

```python
# ✅ 好的委派方式：具體、短小、結構化
result = ask_local_llm(
    "將以下英文 commit message 翻譯成繁體中文，只回傳翻譯結果：\n\n"
    "fix(runtime): align council/persona/pipeline behavior after hygiene audit"
)

# ❌ 不好的委派方式：開放式、需要深度推理
result = ask_local_llm(
    "分析這 200 行程式碼的所有潛在邊界情況和安全漏洞"
)
```

### 命令列快速呼叫

```bash
ollama run qwen3:4b "用繁體中文摘要以下內容：..."
```

## 效能數據（實測）

| 指標 | 實測值 | 備註 |
|------|--------|------|
| 首次載入 | 8-10 秒 | 第一次請求需等模型載入 GPU |
| 生成速度 | **32-37 tok/s** | GTX 1070，模型已載入後 |
| 上下文窗口 | 32K tokens | 建議 prompt < 4K |
| 建議最大輸出 | 300-512 tokens | 4B 模型超過 512 品質急降 |

## 安全規範

> [!CAUTION]
> 本地模型沒有內建的語魂治理。

1. **不將敏感資料傳給外部 API** — 這是本地模型的核心優勢
2. **輸出需經過 PersonaDimension 驗證** — 確保符合人格約束
3. **不直接執行模型的程式碼建議** — 需要人工或 CI 審查
4. **不要讓模型做安全決策** — 安全判斷由 AdaptiveGate 負責
5. **記錄所有呼叫到 ledger** — 保持語義責任可追溯

## ToneSoul 整合

本地模型的輸出應經過語魂系統的品質控制：

```python
# 範例：本地模型生成 → PersonaDimension 驗證
from tonesoul.persona_dimension import PersonaDimension

raw_output = ask_local_llm("寫一段技術說明")
pd = PersonaDimension(persona_config)
corrected, result = pd.process(
    output=raw_output,
    context={"delta_sigma": 0.0, "zone": "resonance"},
    shadow=True,
)
```

## 脈絡工程參考資源 (Context Engineering)

> 龍蝦（本地模型）的能力上限取決於你餵給它的 context 品質。
> 以下是開源的脈絡工程框架，可作為 ToneSoul 系統的設計參考。

### 開源框架

| 框架 | 核心概念 | GitHub |
|------|---------|--------|
| **Anthropic Skills** | SKILL.md 標準、跨 agent 通用 | `anthropics/skills` |
| **Microsoft Agent Framework** | 多代理編排、graph-based workflow | `microsoft/agent-framework` |
| **LangGraph** | 有狀態代理、檢查點、human-in-loop | LangChain 生態 |
| **CrewAI** | 多代理協作、角色定義 | `crewai-inc/crewai` |
| **Agent Zero** | 自學習、自修正、透明度優先 | `agent0ai/agent-zero` |
| **Persona Agent** | AI 人格代理、MCP 整合 | `memenow/persona-agent` |

### 新興標準

| 標準 | 說明 |
|------|------|
| **AGENTS.md** | AI 代理的上下文檔案，描述專案結構和工作流 |
| **MCP (Model Context Protocol)** | 讓 AI agent 直接對接資料庫和工具 |
| **SKILL.md** | 跨 agent 通用的技能定義格式 |

### 核心論文

- [Context Engineering for AI Agents](https://arxiv.org/abs/2506.xxxxx) — 系統化的脈絡設計方法論
- Anthropic (2025): "Context engineering is the deliberate process of designing and providing relevant information to LLMs"
- MIT Technology Review: "From vibe coding to context engineering"
