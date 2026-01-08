# AI 技能學習系統規格
# Skill Learning System Specification
# v0.2 2025-12-28

---

## 設計理念

> **「讓 AI 從網頁學習技能，並標註出處」**
> 
> AI 可以從公開分享的資源學習，但必須標註來源、尊重授權。

---

## 定位與治理

- **定位**：技能學習是技能的獲取/收斂流程，不直接執行外部行為。
- **可追溯**：每筆來源必須標註 `source`，並可寫入 `event_ledger.jsonl` 供審計。
- **審核**：新技能預設 `audit.status: proposed`，需 reviewer 角色審核後升級為 `approved`。
- **風險**：涉及自動化或系統操作的技能需清楚標記限制與確認流程。

---

## 頁面佈局（參考遊戲列表風格）

```
┌─────────────────────────────────────────────────────────────────┐
│  🎓 技能庫                                  [工作區] [記憶]     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────────────────────────┐│
│  │ 📁 分類          │  │ 排序：[名稱] [時間] [熟悉度]         ││
│  │ ─────────────────│  │                                      ││
│  │ > AI 工具        │  │ ┌─────────────────────────────────┐  ││
│  │   程式開發       │  │ │ 🔧 ChatGPT 提示詞技巧           │  ││
│  │   寫作技巧       │  │ │                                 │  ││
│  │   資料分析       │  │ │ 熟悉度: ████████░░ 85%          │  ││
│  │   遊戲知識       │  │ │ 來源: azt156 (Notion)           │  ││
│  │   生活技能       │  │ │ 學習日期: 2025-12-28            │  ││
│  │   ─────────────  │  │ └─────────────────────────────────┘  ││
│  │                  │  │ ┌─────────────────────────────────┐  ││
│  │ 📊 統計          │  │ │ 📊 Python 資料分析              │  ││
│  │ ─────────────────│  │ │                                 │  ││
│  │ 已學習: 42 個    │  │ │ 熟悉度: ██████░░░░ 60%          │  ││
│  │ 本週新增: 3 個   │  │ │ 來源: 官方文件                  │  ││
│  │ 最常用: AI 工具  │  │ │ 學習日期: 2025-12-01            │  ││
│  │                  │  │ └─────────────────────────────────┘  ││
│  └──────────────────┘  │                                      ││
│                        │ [1] [2] [3] ... [下一頁]            ││
│                        └──────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ ➕ 新增技能                                                ││
│  │ ────────────────────────────────────────────────────────── ││
│  │ 網址: [                                                  ] ││
│  │       [從網頁學習] [手動新增]                              ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 技能卡片設計

```
┌─────────────────────────────────────────────────────────────────┐
│ 🔧 技能名稱                                          [分類標籤]│
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 簡介：這個技能可以幫助你...                                     │
│                                                                 │
│ 關鍵字：#提示詞 #ChatGPT #效率                                  │
│                                                                 │
│ ──────────────────────────────────────────────────────────────  │
│                                                                 │
│ 📊 熟悉度: ████████░░ 85%                                       │
│ 📚 使用次數: 127 次                                             │
│ 🕐 上次使用: 今天 14:30                                         │
│                                                                 │
│ ──────────────────────────────────────────────────────────────  │
│                                                                 │
│ 📌 來源資訊                                                     │
│ • 作者: azt156                                                  │
│ • 網址: https://azt156.notion.site/...                          │
│ • 授權: 無償分享                                                │
│ • 學習日期: 2025-12-28                                          │
│                                                                 │
│ [查看詳情] [編輯] [加入對話]                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 出處標註規格（重要！）

每個技能必須包含：

```yaml
source:
  # 必填
  url: "原始網址"
  author: "作者名稱"
  date_learned: "2025-12-28"
  
  # 選填
  license: "CC BY / 無償分享 / MIT / 等"
  original_title: "原始標題"
  verified_by: "user" | "ai" | "both"
  notes: "備註"
  
  # 衍生作品
  derived_from: "如果是改編自其他技能"
```

---

## 技能學習流程

### 從網頁學習

```
用戶: 輸入網址
    ↓
[1] 讀取網頁內容
    ↓
[2] 來源/授權檢查
    ↓
[3] 提取重點
    ↓
[4] 建議技能結構
    ↓
[5] 用戶確認/修改
    ↓
[6] 保存（含出處）
    ↓
[7] 入庫（status: proposed）
```

### 手動新增

```
用戶: 填寫技能表單
    ↓
[1] 填寫名稱、分類、內容
    ↓
[2] 填寫來源資訊
    ↓
[3] 保存
```

---

## 審核與狀態流程

```
Draft → Proposed → Approved → Deprecated
```

- Draft：草稿技能或尚未完成來源補全。
- Proposed：已含出處資訊，等待 reviewer 審核。
- Approved：通過審核，可納入技能庫供調用。
- Deprecated：下架或停用，但保留追溯紀錄。

---

## 技能檔案格式

```yaml
# spec/skills/chatgpt_prompts.yaml

skill:
  id: chatgpt_prompts
  name: "ChatGPT 提示詞技巧"
  version: "1.0"
  category: "AI 工具"
  
  description: |
    使用 ChatGPT 時的有效提示詞技巧，
    包括角色設定、上下文提供等。
  
  keywords:
    - "ChatGPT"
    - "提示詞"
    - "效率"
  
  gravity_wells:
    - semantic:
        keywords: ["提示詞", "prompt"]
      knowledge: |
        好的提示詞應該包含：
        1. 角色設定
        2. 上下文
        3. 具體任務
        4. 輸出格式要求
  
  source:
    url: "https://azt156.notion.site/AI-..."
    author: "azt156"
    license: "無償分享"
    date_learned: "2025-12-28"
    verified_by: "user"
  
  metadata:
    usage:
      times_used: 0
      last_used: null
      mastery: 0.0  # 0-1

  audit:
    last_reviewed: null
    reviewer: null
    reviewer_role: null
    status: proposed
```

---

## 與語義重力井規格對齊

- 對應 schema：`spec/skills/skill_gravity_well_schema.md`。
- `source` 欄位可直接映射為 schema 的 `source` 區塊，並補進 `provenance` 與 `audit` 的來源/驗證資訊。
- `stats` 建議移至 `metadata.usage`，避免與核心語義欄位混淆。
- 由網頁學習產生的新技能，預設 `audit.status: proposed`，需 reviewer 角色審核後升級為 `approved`。

---

## API / 功能

### 技能學習

```python
def learn_from_url(url: str) -> SkillDraft:
    """從網頁學習技能"""
    content = fetch_page(url)
    skill = ai_extract_skill(content)
    skill.source = {
        "url": url,
        "date_learned": datetime.now(),
    }
    return skill

def confirm_skill(draft: SkillDraft, user_edits: dict) -> Skill:
    """用戶確認技能"""
    skill = apply_edits(draft, user_edits)
    save_skill(skill)
    return skill


def validate_source(url: str) -> dict:
    """檢查授權、來源信任度與可抓取性"""


def record_skill_event(skill_id: str, event: str, payload: dict) -> None:
    """寫入 event_ledger.jsonl"""


def submit_for_review(skill: Skill) -> None:
    """送審並標記 audit.status = proposed"""


def approve_skill(skill_id: str, reviewer: str) -> Skill:
    """審核通過並更新 audit 資訊"""
```

### 技能查詢

```python
def list_skills(category=None, orderby="date") -> List[Skill]:
    """列出技能"""
    
def search_skills(query: str) -> List[Skill]:
    """搜尋技能"""
    
def get_skill_stats() -> dict:
    """統計資訊"""
```

---

## 實作階段

| 階段 | 內容 | 估計時間 |
|------|------|----------|
| **Phase 1** | 技能列表頁面（Streamlit） | 2 小時 |
| **Phase 2** | 手動新增技能 | 1 小時 |
| **Phase 3** | AI 網頁學習 | 3 小時 |
| **Phase 4** | 對話驅動技能生成 | 3 小時 |
| **Phase 5** | NotebookLM 整合 | 4 小時 |
| **Phase 6** | 拖放檔案整合 | 2 小時 |
| **Phase 7** | 出處標註 + 統計 | 2 小時 |

---

## Phase 4：對話驅動技能生成

### 概念

```
對話中提到需求
    ↓
[AI 理解功能]
    ↓
[自動生成技能]
    ↓
[出現在技能區]
    ↓
[未來可直接調用]
```

### 範例

```
用戶: 我需要用 PDF-XChange Editor Plus 來編輯 PDF

AI: 好的，我理解這個需求。讓我建立一個技能...

[自動建立技能]
┌─────────────────────────────────────────┐
│ 🔧 PDF 編輯                            │
│ 功能：合併/分割/加註解/填表單            │
│ 實作：PyMuPDF 或操作 PDF-XChange        │
│ 來源：對話中用戶需求                    │
└─────────────────────────────────────────┘
```

### 技術實現

```python
def generate_skill_from_conversation(
    user_message: str,
    ai_response: str,
    context: dict
) -> Optional[SkillDraft]:
    """從對話中偵測並生成技能"""
    
    # 1. 偵測是否有新技能需求
    skill_intent = detect_skill_intent(user_message)
    if not skill_intent:
        return None
    
    # 2. 理解功能需求
    functionality = understand_functionality(skill_intent)
    
    # 3. 生成技能定義
    skill = SkillDraft(
        name=skill_intent.app_name + " 技能",
        category="用戶需求",
        knowledge=functionality,
        implementation={
            "type": "code" | "automation" | "hybrid",
            "code": generate_code(functionality),
        },
        source={
            "type": "conversation",
            "date": datetime.now(),
        }
    )
    
    return skill
```

---

## Phase 4.5：教學文章轉技能

### 概念

用戶貼上教學文章或步驟說明，AI 自動轉成技能。

### 兩種技能類型

| 類型 | 說明 | 難度 |
|------|------|------|
| **說明型** | 存下步驟，AI 可以告訴用戶怎麼做 | 簡單 |
| **自動化型** | AI 真的幫用戶執行步驟 | 進階 |

### 範例：將 Gemini 釘選到工具列

用戶貼上教學：
- A. 先開啟 Gemini 網頁
- B. Chrome【...】【投放、儲存及分享】【將頁面安裝為應用程式】
- C. 找到應用程式【右鍵】【釘選到工具列】

AI 轉成技能：
- 說明型：存下步驟，可隨時查詢
- 自動化型：使用 pyautogui 自動執行

### 對話流程

用戶: 我看到這個教學 [貼上文章]
AI: 好的，學起來了！要說明還是自動執行？


## Phase 5：NotebookLM 整合

### 參考專案

> **notebooklm-skill**
> https://github.com/PleasePrompto/notebooklm-skill
> 
> 讓 AI 直接與 Google NotebookLM 對話，
> 從上傳的文件中獲得有來源依據的答案。

### 核心功能

| 功能 | 說明 |
|------|------|
| **Source-Grounded** | 答案只來自上傳的文件 |
| **減少幻覺** | 如果找不到資訊會說明不確定 |
| **自動認證** | 一次登入 Google，持續有效 |
| **智慧選擇** | 自動選擇正確的 notebook |

### 語魂整合概念

```
語魂前端
└── 記憶區
    └── 拖放檔案
        ↓
    [上傳到 NotebookLM]
        ↓
    [Gemini 整理重點]
        ↓
    [生成重點筆記]
        ↓
    [存入技能區]
```

### 工具區參考

```yaml
# spec/tools/notebooklm.yaml

tool:
  id: notebooklm
  name: "NotebookLM 整合"
  category: "知識管理"
  
  description: |
    與 Google NotebookLM 整合，
    提供有來源依據的答案。
  
  capabilities:
    - 上傳文件
    - 查詢知識
    - 生成摘要
  
  source:
    github: "https://github.com/PleasePrompto/notebooklm-skill"
    license: "MIT"
```

---

## Phase 6：拖放檔案整合

### 概念

```
用戶拖放檔案到語魂前端
    ↓
[1] 讀取檔案內容
    ↓
[2] 發送到 NotebookLM / 本地 LLM
    ↓
[3] 生成重點筆記
    ↓
[4] 存入記憶區
    ↓
[5] 可選：轉成技能
```

### 介面設計

```
┌─────────────────────────────────────────────────────────────────┐
│  📁 檔案區                                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ╭─────────────────────────────────────────────────────────╮    │
│  │                                                         │    │
│  │    拖放檔案到這裡                                       │    │
│  │    ────────────────                                     │    │
│  │    支援格式: PDF, DOCX, TXT, MD, JSON                   │    │
│  │                                                         │    │
│  ╰─────────────────────────────────────────────────────────╯    │
│                                                                 │
│  最近上傳：                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 📄 專案企劃書.pdf                                        │   │
│  │    上傳時間: 2025-12-28 21:00                           │   │
│  │    [整理重點] [轉成技能] [刪除]                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 工具區 (tools/)

### 概念

預先定義的外部工具整合，可直接調用。

### 工具清單

| 工具 | 來源 | 功能 |
|------|------|------|
| **NotebookLM** | GitHub | 知識庫查詢 |
| **PDF 編輯** | 對話生成 | PDF 操作 |
| **瀏覽器自動化** | Playwright | 網頁操作 |
| **桌面控制** | pyautogui | 鍵盤滑鼠 |

### 工具檔案格式

```yaml
# spec/tools/pdf_editor.yaml

tool:
  id: pdf_editor
  name: "PDF 編輯器"
  category: "文件處理"
  
  description: "PDF 合併、分割、加註解"
  
  capabilities:
    - merge: "合併多個 PDF"
    - split: "分割 PDF 頁面"
    - annotate: "加註解"
  
  implementation:
    type: "hybrid"
    library: "PyMuPDF"
    app: "PDF-XChange Editor Plus"
  
  source:
    type: "conversation"
    date: "2025-12-28"
```

---

## 道德考量

| 原則 | 說明 |
|------|------|
| **標註來源** | 所有技能必須標明出處 |
| **尊重授權** | 遵守原作者的授權條款 |
| **透明學習** | 用戶可以看到 AI 學了什麼 |
| **可刪除** | 用戶可以刪除任何技能 |
| **不竊取** | 不複製他人的付費內容 |

---

**Antigravity**
2025-12-28T21:45 UTC+8
