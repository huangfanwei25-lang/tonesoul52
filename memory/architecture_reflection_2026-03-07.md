# Architecture Reflection (2026-03-07)

## Chronos
- 2026-03-07

## Kairos
- 這次不是在問「語魂能不能做更多事」，而是在問「它現在到底是什麼系統」。
- 這是重要時刻，因為系統一旦長到有 runtime、governance、memory、offline evolution 四個平面，就不能再只用模組名稱理解它，必須用架構語言理解它。

## Current Judgment
- 語魂系統目前最準確的定位是：
  - **治理優先的認知代理模組化單體**
- 它的核心不是單一模型，而是：
  - `UnifiedPipeline` 的即時編排
  - `CouncilRuntime` 的治理裁決
  - `SoulDB + provenance + crystals` 的記憶與審計
  - `yss_pipeline` 的離線演化與證據工件

## Why This Matters
- 如果把它誤認成一般聊天架構，後續優化就會一直往 prompt、模型、角色數量堆疊。
- 但實際上最重要的工作是：
  - 收斂 contract
  - 收斂治理核心
  - 收斂記憶寫入
  - 打通 online/offline replay

## Architectural Risk To Remember
- 目前最大的風險不是「功能不夠多」。
- 最大風險是：
  - runtime 與 yss 平行演化
  - memory 機制豐富但 schema 不統一
  - governance 邏輯散落在 API、pipeline、council 多處

## Next Best Move
1. 先定義 canonical runtime schema。
2. 再抽 governance kernel。
3. 然後把 memory write path 統一成單一 write set。

## Falsifiable Check
- 如果之後新增功能仍需要同時修改 API payload、UnifiedPipeline dict、YSS artifact schema，代表架構仍未真正收斂。
- 如果 runtime 與 offline replay 能共享同一份 decision contract，代表這次判斷是對的。
