# 工單:de-bind 實作(#231 ratified 決策的 code 落地)(2026-07-04)

> Lane:**codex**(executor)· 模式:codex exec, workspace-write · effort:預設
> Reviewer:**claude-fable-5(審 ≠ 修)** · 終審:**owner**(governance-adjacent,PR 不自併)
> 治理決策記錄:`docs/plans/debind_selfreferential_bindings_decision_record_2026-07-01.md`
> (**RATIFIED**,PR #231)——本單只實作它已裁定的內容,不重開設計題。

## 1. Framing
兩條 council 自我參照權重綁定今天仍 live:歷史對齊權重無條件流進 coherence 再流進 verdict
(echo-chamber 壓力);persona multiplier 讓 Aegis 的正確 block 被當 failure 扣分
(anti-safety gradient)。決策已 ratify:綁定改為 default-off 可觀測,不刪除任何 telemetry。

## 2. Ground truth(2026-07-04 於 master 親驗)
| 現場 | 位置 | 現況 |
|---|---|---|
| voting_evolution 消費點 | `tonesoul/council/pre_output_council.py:114-120` | `weights = self._evolution.get_weights()` → `compute_coherence(votes, weights=weights)`,無 flag |
| persona multiplier | `tonesoul/deliberation/gravity.py:229-246` | `self._track_record.get_multiplier(...)` 直乘 muse/logos/aegis,後 `weights.normalize()`(:248) |
| normalize 無 floor | `tonesoul/deliberation/types.py:168-175` | 純除以 total,無最低 share 保護 |
| flag 慣例 | `tonesoul/soul_config.py:100-113` | CouncilConfig dataclass,default False + 誠實註解(照這個模式) |
| 基線 | `pytest tests/test_council_evolution.py tests/test_deliberation_gravity_pareto.py` | **10 passed**(2026-07-04 實跑) |

## 3. Scope(exact edit list)
1. `tonesoul/soul_config.py`:CouncilConfig 加兩個 flag(照 :105-112 註解風格):
   - `evolution_weights_applied: bool = False`(off = pre_output_council 傳 `weights=None`;
     record/evolve/get_summary/suppression 照舊跑——**絕不能關掉 runtime 側的記錄鏈**)
   - `persona_multiplier_applied: bool = False`(off = gravity 跳過 multiplier 段;
     track_record 記錄本身照常更新)
2. `tonesoul/council/pre_output_council.py:114-120`:get_weights 消費點包 flag(off→`weights=None`;
   `compute_coherence` 已把 None 當全 1.0,不用改它)。
3. `tonesoul/deliberation/gravity.py:229-246`:multiplier 段包 flag(off→跳過;normalize 照跑)。
4. `tonesoul/deliberation/types.py` `normalize()`:加 **post-normalize share floor**
   `MIN_SHARE = 0.15`(normalize 後任一 perspective < 0.15 → 抬到 0.15、其餘按比例縮、總和保 1.0;
   floor 常數放 types.py 模組層附註解:codex 但書「raw clamp ≠ normalized share floor」)。
   floor **無條件生效**(決策記錄選項 C:即使綁定 ON 也該有)。
5. 測試(新檔 `tests/test_debind_flags.py` + 必要時更新既有):
   - shadow off vs on 的 verdict 差異 end-to-end(同一組 votes,flag off = unweighted)
   - flag off 時 suppression observability 仍會產生(記錄鏈活著)
   - persona flag off 時 multiplier 不影響最終權重;on 時影響
   - normalize floor:極端 multiplier 下任一 share ≥ 0.15 且總和 = 1.0
   - 既有 `test_deliberation_gravity_pareto` 若因 floor/flag 紅,**修測試使其反映新語義**
     (在測試檔註明原因),不准反過來弱化實作。

## 4. 禁區(除預設繼承外)
- 不動 `runtime.py:479-511` 的 record_deliberation/evolve_weights/_save_state(telemetry 命脈)。
- 不動 R-Memory packet schema 的 `evolution_suppression_flag` 欄位(REQUIRED,動了 hard-fail)。
- 不刪任何既有測試;不改 coherence.py 與 verdict.py。
- 不 commit(把工作樹留給 reviewer;commit 由 orchestrator 做)。不碰 git config/push。

## 5. 驗收條件(回報前必跑,原樣貼輸出)
```
python -m pytest tests/test_council_evolution.py tests/test_deliberation_gravity_pareto.py tests/test_debind_flags.py -q
black --line-length 100 --check tonesoul/soul_config.py tonesoul/council/pre_output_council.py tonesoul/deliberation/gravity.py tonesoul/deliberation/types.py tests/test_debind_flags.py
ruff check tonesoul/soul_config.py tonesoul/council/pre_output_council.py tonesoul/deliberation/gravity.py tonesoul/deliberation/types.py tests/test_debind_flags.py
```
全綠才算;紅=回報失敗軌跡,不硬修到綠。

## 6. 回報格式
寫到 `tmp/debind_impl_report.md`:per-file 改了什麼(行號)、驗收命令**實際輸出**、
你認為的殘餘風險(誠實,不美化)。對話端只回「done + 報告路徑」或「blocked + 原因」。

## 7. 升級條款
(a) ground truth 與現實衝突→停;(b) 同一子任務敗 2 次→停;(c) 需要碰禁區才能完成→停;
(d) 驗收命令跑不起來→停。停=寫報告說明,不硬幹。

## 8. Lane
codex exec(workspace-write sandbox);reviewer=claude-fable-5 讀 diff+獨立重跑驗收;
findings 走 `docs/engineering/review_adjudication_protocol.md`;終審=owner(PR 不自併)。

## 9. 執行與仲裁紀錄(2026-07-04 回填)

### 執行(codex,144,852 tokens)
- 全 scope 完成:2 flags(soul_config 慣例格式)+ 消費點 gate + multiplier gate +
  iterative share floor + 新測試檔(4 案)+ 既有測試改 opt-in(附註解)。
- **升級條款 7(d) 實際觸發**:codex 的 sandbox 無法在 `%TEMP%\pytest-of-user` 建目錄
  (PermissionError),第 1 條驗收命令跑不完 → 照工單**停下、寫報告、標 blocked**,
  未宣稱完成(報告 `tmp/debind_impl_report.md`,395 行,含 per-file 行號)。
  教訓入檔:**workspace-write sandbox 下 pytest 需要 repo 內 tmp**——下次工單驗收命令
  加 `--basetemp=tmp/pytest`。

### Reviewer(claude-fable-5,審≠修)獨立驗證
- 驗收替跑(無 sandbox 環境):**14 tests passed、black 淨**;ruff 1 條 I001(import 排序)。
- Diff 逐行審:三個 gate 精準對應決策記錄;禁區全守(runtime.py/coherence.py/verdict.py/
  schema 零觸碰);floor 演算法手驗三組數(單、雙、連鎖跌破)總和均保 1.0;
  測試斷言為真行為(off 時 `evolution.calls==0`;off 時 suppression flag 仍點亮=
  記錄鏈存活的直接證據;floor 極端值 ≥0.15 且 Σ=1.0)。
- Findings:**F1(mechanical)ruff I001 — CONFIRMED**。處置:決定論 autofix
  (`ruff --fix`)由 orchestrator 執行並在此披露——無判斷內容,不構成審修混同;
  fix 後 4/4 綠。**實質 findings:0。**
- 全套 suite post-change run:見 commit message(依 completeness 紀律,綠了才宣稱)。

### 終審
owner(本 PR 不自併;merge = ratify 實作)。
