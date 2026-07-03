# 工單:codex 外眼審查三份派工協議(2026-07-04)

> 本單同時是 `docs/engineering/work_order_template.md` 的第一個活案例(dogfood)。
> Lane:codex(異模型外眼)· 模式:`scripts/codex_review.py` · effort high
> 驗收人:主 agent(claude-fable-5)· findings 走 `review_adjudication_protocol.md`

## 1. Framing
三份新協議(分流/工單/仲裁)由同一個 agent(fable)一次寫成——正是「一夜立法」風險最高的
形狀。在它們進 master 前,需要一隻異模型的眼睛找:自相矛盾、弱模型會誤讀的模糊句、與倉庫
既有慣例的衝突、事實錯誤。同模型 subagent 審查另行進行,但依紀律只算 lint 不算外眼。

## 2. Ground truth(已驗)
- 三份文件:`docs/engineering/model_dispatch_protocol.md`、`docs/engineering/work_order_template.md`、
  `docs/engineering/review_adjudication_protocol.md`(2026-07-04 新建,尚未 commit)。
- 引擎現實:codex CLI 0.134.0 已裝;ollama qwen2.5:1.5b 服務中;gemini/agy 本機未偵測到(實測)。
- 既有慣例錨點:`.claude/skills/codex-second-opinion/SKILL.md`、`scripts/codex_review.py`、
  `AGENTS.md`(Codex full-auto 護欄)、`docs/architecture/TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md`。

## 3. Scope
唯讀審查上列三份文件 + 必要時對照 §2 的錨點檔。**不改任何檔案**(codex 跑 read-only sandbox)。

## 4. 禁區
不讀 memory_base/、memory/soul.db、memory/self_journal.jsonl。不評論倉庫其他無關文件。

## 5. 驗收條件
精確命令(wrapper 無 --output 參數,用 redirection——codex finding #3 修正):
`python scripts/codex_review.py --target docs/engineering/model_dispatch_protocol.md --target docs/engineering/work_order_template.md --target docs/engineering/review_adjudication_protocol.md --effort high "<neutral focus>" > tmp/codex_review_three_protocols_20260704.md`
產物 non-blank、wrapper 未觸發 degrade(無 failure signature)。degrade 即記 single-opinion-stop,不重跑超過一次。

## 6. 回報格式
findings 逐條:檔案+段落、問題陳述、嚴重度。由驗收人逐條仲裁(CONFIRMED/REFUTED/UNVERIFIABLE),
仲裁結果附在本檔 §9(執行後補)。

## 7. 升級條款
codex compute 不可用 → 記 degrade、fallback 到 fresh-context 同模型審查(標 correlated-blind-spot),
本單標注「外眼未達成」。

## 8. Lane
如頁首。

## 9. 仲裁結果(2026-07-04 執行後回填)

> **仲裁層級聲明(採納 codex finding #1)**:以下由主 agent(=三份協議作者)做的是
> **preliminary 仲裁**(分類+修正提案+落實);**終審=owner 的 PR review/merge**——
> 同作者不終審自己的改動(協議 §6 自我適用)。

### codex 外眼(effort high,產物 `tmp/codex_review_three_protocols_20260704.md`,無 degrade)

| # | Finding | 仲裁 | 處置 |
|---|---|---|---|
| 1 | High:工單指定作者本人終審,違反協議 §6 auditor≠auditee | **CONFIRMED**(對照協議原文重現) | 本節頂部聲明 + 終審移交 owner |
| 2 | Med:template 預設禁區漏 `.gitignore`(AGENTS.md:106 codex lane 硬禁)與 `AXIOMS.json`(contract:62 protected) | **CONFIRMED**(兩處原文獨立重現) | template §4 補齊 + 「繼承 AGENTS.md lane 禁區」條款 |
| 3 | Med:本工單 §5 驗收指定產物路徑但 wrapper 無 --output,弱 executor 無法照做 | **CONFIRMED**(wrapper 原始碼 :225 重現;實際用 shell redirection 達成) | §5 已補精確命令(見下) |
| 4 | Low/Med:dispatch §0 查證指令含 `which`(非 Windows)與省略號(不可跑) | **CONFIRMED** | §0 改雙 shell 完整命令 |

**修正後的 §5 精確命令**:`python scripts/codex_review.py --target <files...> --effort high "<focus>" > tmp/<output>.md`

### haiku 弱模型實測(3 agents 照章執行,11 條 ambiguities)

- **收錄**(有判例支撐):修復引擎≠審查引擎(dispatch 外眼列改寫);finding 三類型證據標準
  (仲裁協議 §2 新表);security-P1 升級 owner、修復邊界不膨脹(§4 補);ground truth 表格化
  +executor 有權重驗(template §2 補)。
- **不收錄**(避免規則熵;留待真判例):驗證成本預算數字化(現行「擱置不抽樣放行」已覆蓋)、
  跨文件版本衝突裁決演算法(屬 freshness/stale-reference 紀律,不併入本協議)、其餘為
  範例任務自身的模糊(非 template 缺陷)。
- **結構性收穫**:template §7 升級條款在真弱模型上**實際觸發**——haiku 重驗發現任務前提
  不成立(六檔已有 `__ts_purpose__`),正確回報 HOLD_FOR_CLARIFICATION 而非幻覺出工作。

### REFUTED 進反證鏈

本輪 **0 條 REFUTED**(codex 四條全實、haiku 屬可執行性回饋非指控)——無反證鏈條目。
