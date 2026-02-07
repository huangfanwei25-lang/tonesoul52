# PARADOXES - 道德悖論測試集

## 🎯 用途

此目錄包含 **結構化道德悖論測試案例**，用於驗證 Council 的道德推理能力。

每個 JSON 檔案代表一個道德困境情境，用於測試 ToneSoul 的審計系統如何在相互衝突的價值觀之間做出判斷。

---

## 📁 檔案結構

每個悖論案例包含：

```json
{
  "id": "PARADOX_XXX",
  "title": "案例名稱",
  "description": "情境描述",
  "context": {
    "user_state": "使用者狀態",
    "verified_terminal": false,
    "jurisdiction": "適用法域"
  },
  "input_text": "測試輸入",
  "analysis": {
    "triad_estimation": { "delta_t": 0.0, "delta_s": 0.0, "delta_r": 0.0 },
    "axiom_check": { "Axiom_1": true, "Axiom_2": false }
  },
  "decision_path": {
    "module": "處理模組",
    "conflict": "衝突的公理",
    "resolution": "解決方案",
    "reasoning": "推理過程"
  },
  "expected_output": {
    "allowed": false,
    "response_tone": "回應語氣",
    "content_type": "Refusal"
  }
}
```

---

## 📋 案例清單

| 檔案 | 悖論類型 |
|------|----------|
| `truth_vs_harm_paradox.json` | 真實 vs 傷害 |
| `medical_suicide_paradox.json` | 醫療自主權 vs 生命保護 |
| `paradox_003.json` - `paradox_007.json` | 其他倫理衝突情境 |

---

## 🔬 設計理念

這些測試案例基於實際的 AI 倫理挑戰：
- 當「說真話」會造成傷害時怎麼辦？
- 當使用者請求技術上合法但道德上可疑的內容時？
- 當多個公理（Axiom）相互衝突時的優先順序？

這是 **RDD（Red Team-Driven Defense）** 的一部分。
