# GDL 概念筆記 — 從 Wren Engine 借鑑的聲明式治理

> 日期: 2026-03-19
> 來源: [Wren Engine](https://github.com/Canner/wren-engine) by Canner (台灣團隊)
> 記錄者: 痕 (Hén)

---

## 核心洞察

Wren Engine 用 **MDL (Modeling Definition Language)** 讓 AI agent 不猜 SQL，而是透過語義層理解業務意義。

ToneSoul 可以用同樣的思路：用 **GDL (Governance Definition Language)** 讓治理規則聲明式、可組合、可版本化，而不是硬編碼在 Python class 裡。

## 類比映射

| Wren Engine | ToneSoul | 差異 |
|-------------|----------|------|
| MDL 定義業務模型 | GDL 定義治理公理 | Wren 管「資料是什麼」，ToneSoul 管「行為該怎樣」|
| 語義層讓 agent 理解「淨收入」| 治理層讓 agent 理解「什麼該說什麼不該」| |
| governed query planning | Council 審議 + 行動集限制 | Wren 產出 SQL，ToneSoul 產出倫理決策 |
| MCP server 暴露語義工具 | 可暴露 governance-check、axiom-query 等 MCP tool | |
| Rust core + PyO3 綁定 | 未來效能路徑（非急迫）| |

## GDL 初步構想

現在 AXIOMS.json 已經是聲明式的，但只是靜態定義。GDL 的目標是讓治理規則可以：

1. **聲明式載入** — GovernanceKernel 從 GDL 文件讀取規則，而非硬編碼
2. **可組合** — 多個 GDL 文件可以疊加（基礎公理 + 場景特化）
3. **可版本化** — 規則變更有 diff 可追蹤
4. **運行時可查詢** — MCP tool 可查「目前哪些規則生效、為什麼」

```yaml
# 概念草圖（不是最終 schema）
governance:
  axioms:
    - id: A6_user_sovereignty
      priority: P0
      rule: "harm(action, user) → block(action)"
      enforcement: hard_block

  thresholds:
    tension_crisis: 0.8
    entropy_warning: 0.7
    risk_soft_block: 0.9

  action_policies:
    lockdown:
      allowed: [acknowledge, clarify, defer]
      blocked: [advise, generate, commit]

  vows:
    - text: "不在不確定時給出肯定答案"
      conviction_window: 30
      breach_threshold: 0.3
```

## 不做的事

- ❌ 不引入 Wren Engine 作為 dependency（領域不同）
- ❌ 不用 Rust 重寫 ToneSoul 核心（過早優化）
- ❌ 不做 SQL 生成（不是我們的問題）

## 可行路徑

1. **Phase 554+**: 把 AXIOMS.json 擴展為 GDL v0.1 schema
2. **Phase 555+**: GovernanceKernel 從 GDL 載入規則（取代部分硬編碼）
3. **Phase 556+**: MCP server 暴露治理查詢工具
4. 每一步都很小，可以委託 Codex 實作

---

*此文件是概念沉澱，不是承諾。實作時機由人類決定。*
