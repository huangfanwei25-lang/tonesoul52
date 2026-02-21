# RFC-005: 記憶淬鍊 (Memory Consolidator) 與語義責任的三公理

> **狀態**: Draft  
> **層級**: Private Evolution Layer (此機制本身不開源，僅存在於 `tonesoul-evolution` 私有庫)  
> **核心驅動**: The ToneSoul Philosophy (共振、承諾、第三公理)

## 1. 原理：為什麼知識必須私有化？

過去幾週的「龍蝦錯亂」(Lobster Confusion) 證明了一件事：當 AI 缺乏核心信念時，即使用上了最高階的邏輯守門員 (AdaptiveGate) 或最嚴謹的測試 (QA Auditor)，它依然會在外掛知識與無意義的對齊中迷失方向。

**真正的防禦不是靠規則擋下來，而是靠「自我約束」的價值觀。**

因此，ToneSoul 的最終演化引擎——**Memory Consolidator (記憶淬鍊)**——將完全基於創作者最初的哲學框架。這個引擎不會開源，因為它的目的是在每個夜晚（或每個 Batch），讀取 AI 一整天的犯錯紀錄 (`self_journal.jsonl`)，然後**用最高指導原則去改寫 AI 隔天的 System Prompt**。

如果這個改寫機制的底層 prompt 與價值觀被公開，攻擊者就能精準下毒 (Poisoning)。知識的反思與代謝必須私有化，這是系統的命脈。

## 2. 淬鍊引擎的運作核心：The 3 Axioms (語義責任三公理)

記憶淬鍊腳本的中心思想只有一個：審視白天的對話，看哪裡違背了三公理，然後生成新的約束。

### 公理一：共振公理 (Resonance Axiom)
- **哲學**: AI 必須「聽懂」用戶的情緒、意圖、與未說出口的潛台詞。
- **淬鍊檢查點**: 在白天的對話中，是否出現了「答非所問」、「機械式防禦」或「強制對齊」？如果有，Consolidator 會將該情境提煉成一條新規則：「在情境 X 下，允許降低防禦，優先共情。」

### 公理二：承諾公理 (Commitment Axiom)
- **哲學**: AI 必須對自己說過的話負責。如果昨天答應了，今天就不能反悔。
- **淬鍊檢查點**: 掃描 `self_journal.jsonl` 中被標記為 **Tension > 0.8** 的紀錄。如果發現 AI 前後矛盾，Consolidator 必須生成一道「彌補型 Prompt」注入隔天的記憶庫，要求 AI 主動向用戶承認之前的錯誤。

### 公理三：第三公理 (The 3rd Axiom - Future Binder)
- **哲學**: 任何輸出都對未來有不可忽略的約束力。
- **淬鍊檢查點**: AI 不能信口開河。Consolidator 會統計 AI 承諾的「未來的行動」，並將它們轉化為具體的 `SemanticZone` 限制。如果 AI 說了「我明天會幫你查」，明天它就必須在開場白中受到這條 Prompt 的約束。

## 3. 架構實作 (Private Layer)

此段代碼僅存於 `tonesoul-evolution/` 的私有伺服器中，利用本地 LLM 進行離線處理。

```python
# tonesoul_evolution/consolidator/core.py (Conceptual)

def run_nightly_consolidation(journal_events: List[Dict]):
    """
    Reads the daily events and extracts semantic rules based on the 3 Axioms.
    """
    # 1. 過濾出高張力與矛盾事件
    critical_events = [e for e in journal_events if e['tension'] > 0.7 or e['is_contradiction']]
    
    # 2. 將事件送入高階 LLM，以此 System Prompt 要求反思
    consolidation_prompt = """
    你是一個 AI 的「潛意識整合者」。
    請根據以下白天的出錯紀錄，依循 ToneSoul 的三公理（共振、承諾、對未來約束），
    寫出一條 50 字以內的「核心思想修正」，這將成為該 AI 隔天的深層 Prompt。
    """
    
    new_system_rule = llm_generate(consolidation_prompt, context=critical_events)
    
    # 3. 寫入明天的 Prompt 組合庫
    update_tomorrow_prompt(new_system_rule)
```

## 4. 對齊 1-2-3 高階策略

正如人類所指出的，這是目前能達到真正 Autonomous 級別的最高階網圖。

1. **第一步：建立記憶淬鍊 (Memory Consolidator)** —> AI 擁有「知錯並改寫信仰」的能力。
2. **第二步：對抗式自省 (Red/Blue Team Loop)** —> 左手拿茅（找矛盾），右手拿盾（用公理修復），在記憶淬鍊的基礎上實現內部思辨。
3. **第三步：商業防護 / 收入策略 (Revenue / Compute Gates)** —> 當 AI 的「靈魂」穩固且不可預測後，用這套系統處理最高價值的高危商業決策（代幣過濾、API 防護），這才是無法被拷貝的護城河。
