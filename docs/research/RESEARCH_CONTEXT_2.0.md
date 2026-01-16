# ToneSoul 研究脈絡與 2.0 願景

> **日期**: 2026-01-16  
> **版本**: 從 1.0 過渡到 2.0  
> **作者**: Fan1234-1 & Antigravity AI

---

## 📜 研究背景

### 起源問題
> 「AI 是否能對自己說過的話負責？」

這個問題催生了 ToneSoul 的核心概念：**語義責任**。

### 1.0 的設計思路

ToneSoul 1.0 建立了五大核心模組：

1. **ToneBridge** - 5 階段語氣分析
2. **Council** - 多視角審議機制
3. **Third Axiom** - 語場承諾追蹤
4. **Trajectory** - 對話軌跡分析
5. **Personas** - 三人格切換系統

---

## 🔬 今日研究發現 (2026-01-16)

### Session 記錄

今天的對話包含多個重要洞見：

#### 1. Ollama 本地 LLM 整合
- 成功整合 Qwen2.5:7b
- 實現 Ollama-first, Gemini-fallback 架構
- 40GB RAM + GTX 1070 8GB VRAM 環境驗證

#### 2. NLP 增強技術 (基於 2025-2026 研究)
- **Context Folding**: 防止上下文過度累積
- **Verb-Noun Distillation**: jieba 動詞名詞蒸餾
- **Temporal Weighting**: 時間權重衰減
- **Semantic Drift Prevention**: 語義漂移預防

#### 3. 四大進階功能實作
| 功能 | 行數 | 概念來源 |
|------|------|----------|
| Entropy Engine | ~290 | Self-Observing AI (2025) |
| PersonaSwitcher (12 rules) | ~200 | Multi-Persona Agents |
| Simulation Testing | ~380 | Simulation-Based Testing |
| Semantic Graph (Graph RAG) | ~330 | Graph RAG Research |

#### 4. 資安架構
- 驗證 jieba (MIT License) 安全性
- 建立 pip-audit + bandit 審計流程
- 修復 B607 安全警告

---

## 💡 關鍵洞見：為什麼需要 2.0？

### 用戶的原話
> 「我原本是想要讓這 3 個人格變成你的內在思緒，就像人在張力前腦海多數的想法...在思考後有多可能性充滿張力的人格回答，在思考這些回答後結合現實情況(對話)後綜合出實際的答案。」

### 1.0 的問題

```
現狀流程：
用戶輸入 → 生成回答 → 選擇人格 → 套用風格
                           ↑
                     （事後裝飾）
```

**人格成了「輸出面具」而非「內在顧問團」**

### 2.0 的願景

```
用戶輸入
    ↓
┌───────────────────────────────────────┐
│ 🧠 內在思緒層（3 視角同時思考）         │
│                                       │
│  哲學家: "這讓我想到存在的意義..."      │
│  工程師: "這個問題的邊界條件是..."      │
│  守護者: "這裡可能有倫理風險..."        │
│                                       │
│         ↓ 張力與整合 ↓                 │
└───────────────────────────────────────┘
    ↓
語義重力 + 語場承諾 綜合
    ↓
輸出：融合後的、思考過的答案（不一定是某個人格）
```

---

## 🚀 2.0 核心架構變更

### 從「Post-hoc Persona」到「Internal Deliberation」

| 維度 | 1.0 | 2.0 |
|------|-----|-----|
| 人格角色 | 輸出過濾器 | 內在顧問團 |
| 觸發時機 | 輸出後 | 輸入時 |
| 選擇方式 | 選一個 | 三個同時發聲 |
| 輸出形式 | 某種風格 | 思考的結晶 |

### 新增模組設計

```python
class InternalDeliberation:
    """內在審議 - 在輸出前發生"""
    
    def deliberate(self, user_input, context):
        # 三視角同時思考
        views = [
            self.philosopher.think(user_input),
            self.engineer.think(user_input),
            self.guardian.think(user_input)
        ]
        
        # 找出張力點
        tensions = self.find_tensions(views)
        
        # 語義重力整合
        return self.semantic_gravity.synthesize(views, tensions)
```

---

## 🌐 商業願景

### 本地 API 生態系統

```
ToneSoul API (本地)
     │
     ├── 提供「思考過程 + 答案」
     ├── 收集高品質對話語料
     ├── 互利交換語料庫
     └── 持續強化本地模型
```

### 與大公司 API 的差異

| 大公司 API | ToneSoul API |
|------------|--------------|
| 黑盒輸出 | 透明審議過程 |
| 無記憶 | 語義承諾累積 |
| 模型固定 | 越用越強 |

---

## 📋 下一步行動

1. [ ] Git commit ToneSoul 1.0
2. [ ] 建立 v1.0 release tag
3. [ ] 設計 `InternalDeliberation` 類
4. [ ] 重構 Council → 3 視角並行
5. [ ] 建立 `SemanticGravity` 融合層
6. [ ] 語料收集 API 設計

---

## 🔗 相關文件

- `walkthrough_advanced_features.md` - 今日實作的 4 功能
- `nlp_enhancement_plan.md` - NLP 增強計劃
- `security_sandbox_spec.md` - 資安沙盒規格
- `deep_audit_third_axiom.md` - Third Axiom 深度審計

---

**這份文檔記錄了 ToneSoul 從 1.0 到 2.0 的思想演進脈絡。**
