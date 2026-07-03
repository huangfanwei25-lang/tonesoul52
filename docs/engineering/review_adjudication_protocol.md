# Review 仲裁協議(Review Adjudication Protocol)

> Status: v1(2026-07-04)· 性質:**reviewer-agnostic 通用協議**——把已成文的 codex lane 紀律
> (`.claude/skills/codex-second-opinion/SKILL.md` rule d、`scripts/codex_review.py`)推廣到
> **任意 reviewer**:codex、Gemini/AGY、人類 PR comment、同模型 subagent、未來任何外眼。
> 核心一句:**reviewer 沒有決策權。finding 是指控,不是事實;查證後才存在。**
> 為什麼是鐵律:多 agent 流程最常見的死法=reviewer 一開口 executor 就開修,假陽性沒被擋,
> 任務越修越歪(外部實戰 + 語魂判例:2026-06-29 同模型對 fail-closed 核心產出自信但錯的 fix,
> 靠既有測試才擋下)。

## 1. 流程(五步,每步有產物)

1. **收**:reviewer 的 findings **寫實體檔**(不經對話轉述——轉述即污染)。記 reviewer 身分與模型。
2. **仲裁**:仲裁者(主 agent 或 owner)逐條分類,每條必附證據:
   - **CONFIRMED** —— 仲裁者**獨立重現**(自己讀碼到那一行 / 自己跑出那個輸出)。reviewer 說了不算。
   - **REFUTED** —— 附反證(code 實際行為、測試輸出)。
   - **UNVERIFIABLE** —— 查證成本過高或無 oracle;**標注後不修**,不默默吞掉。
3. **分流**:只有 CONFIRMED 進修復工單(走 `work_order_template.md`);REFUTED 進反證鏈
   (`tools/accountability_panel/events.json`,challenger = reviewer id)——被推翻的指控是
   問責資產,不是垃圾;UNVERIFIABLE 留在仲裁檔裡等新證據。
4. **修**:executor 只看得到 CONFIRMED 清單。reviewer 與 executor **不直接對話**。
5. **覆驗**:修復後 re-run 原重現步驟;綠了才 close。

## 2. 強度分級(判準)

**先分 finding 類型——三類的證據標準不同**(2026-07-04 haiku 仲裁實測補):

| 類型 | 例 | CONFIRMED 的門檻 |
|---|---|---|
| bug-class(correctness/security) | 「token 比對用 == 有 timing 風險」 | 讀到那一行 + 確認無既有防護(如 `hmac.compare_digest`) |
| factual-class(文件/數字) | 「文件說八代,實際七個」 | 對照 source-of-truth 重數一次(stale-reference 紀律適用) |
| opinion-class(架構/品味/「建議重寫」) | 「整個 memory/ 過度複雜」 | **預設 UNVERIFIABLE**——除非附量化失敗案例;無 oracle 的審美指控不進修復工單,升級 owner 當方向題 |

| 情況 | 等級 | 處置 |
|---|---|---|
| 兩個獨立 reviewer(異模型)各自到達同一 finding | E2+ | 高信心,仍要重現一次 |
| 單一 reviewer 到達,仲裁者讀碼重現 | CONFIRMED | 進修復 |
| 單一 reviewer 到達,無法重現 | 存疑 | 要求 reviewer 給重現步驟;給不出→UNVERIFIABLE |
| reviewer 同意你原本的判斷 | **不是證明** | 「codex agrees ≠ proven」(skill 原文);信心+,證據不變 |

## 3. Independence 紀律

- 給 reviewer 的 focus/prompt **不得夾帶自己的結論**(「我覺得沒問題,幫我確認」=污染;
  taint 偵測前例:`scripts/codex_review.py` 的 _TAINT regex,含中英文)。
- **同模型 review 一律標 correlated-blind-spot**——它是 lint,不是外眼(判例:同模型 fan-out
  分佈相關同盲點;紅隊在同模型自評「0 bypass」中找到 2 個真 bypass)。
- reviewer 的「aggressive 報 P1」是 feature 不是 bug——寬進嚴出:讓它多報,仲裁擋假的。
  **絕不因為假陽性多就叫 reviewer 收斂**——那是在教 reviewer 自我審查,盲點會回來。

## 4. Fail-closed

- reviewer 沒真跑(rate-limit、auth 失敗、輸出可疑地短)→ **single-opinion-stop**:明說
  「本結論未經第二眼」,不假裝(degrade 偵測前例:`codex_review.py` 的 _FAILURE_SIGNATURE)。
- 仲裁者時間不夠逐條查證 → 整批標 UNVERIFIED 擱置,**不抽樣放行**(70%×N ≠ 95%,R1)。
- **security / governance-fail-closed 類的 P1**:CONFIRMED 判定後**升級 owner(或異模型二審)再修**,仲裁 subagent 不獨自放行高風險修復。
- executor 修 CONFIRMED 項時**發現新問題→回仲裁,不順手修**(= 工單 template §7 升級條款;修復邊界不膨脹)。

## 5. 活判例(本協議自己的第一批)

- 2026-07-03:同模型 critic 對七條論點仲裁——**推翻 1 條**(C1「語魂是純判例系統」,反例:公理
  閾值是先驗立法)、削弱 2 條、修正 4 個數字;全部 CONFIRMED 後才進交付。REFUTED 方向的
  norm(「數字對不上」)反過來修了主 agent 的簡報。
- 2026-06-29:codex 抓到 string-grep 冒充 import 證據(三處),主 agent 對碼覆驗後改判——
  單方 finding + 獨立重現 = CONFIRMED 的標準案例。

## 6. 誠實限制

- 本協議 advisory,無 CI enforcement;它的第一個真實違反案例(誰跳過仲裁直接修了)請寫回 §5。
- 仲裁者自己也會錯——高風險判定(governance/fail-closed 相關)升級 owner 或異模型第二眼,
  仲裁者不終審自己深度參與過的改動(auditor ≠ auditee)。
