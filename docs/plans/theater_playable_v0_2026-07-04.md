# 岔軌之城最小可玩版 v0 — 工單 + 治理決策記錄(2026-07-04)

> Status: 動工中(owner 已於 2026-07-04 對話中點名開工:「(a) 岔軌之城最小可玩版…單人模式先行、靜態頁 + rules-council 節點」)。
> 格式:`docs/engineering/work_order_template.md` 八欄 + CLAUDE.md 治理決策記錄四欄。
> 正典依據:天道 v0.2 > 機制書 > 世界書(`docs/theater/README.md` 衝突序)。

## §0 Orientation(這張單為什麼長這樣)

世界書 §「v0 可玩最小版(誠實範圍)」已把範圍寫死:靜態事件卡 × 五階段迴圈 ×
rules-council 佈告欄體節點 × 同意閘+撤回碼 × trace 下載,零伺服器成本。本單不發明
新範圍,只把它變成可驗收的檔案清單。設計鐵律(世界書):**每條規則對應倉庫真實
機制,或誠實標 absent——佈景可以幻想,物理必須是真的**。

## 【治理決策記錄】

- **決策**:新增 `site/theater/`(靜態可玩頁)+ `tools/theater_page/`(council 預算
  生成器)兩個子面。不動 tonesoul/ 引擎、不動 governance/、不動 AXIOMS.json。
- **為什麼**:owner 三選項之 (a);劇場正典(15 地點/15 NPC/天道 v0.2)已封存,缺的
  是「玩家完整跑完一局,並產生一份可回讀的責任紀錄」(機制書 §十一 的第一版目標)。
- **張力來源**:無結構性衝突。一條誠實張力:靜態頁跑不了 Python council——解法不是
  用 JS 仿冒 council,而是沿用 demo_ui Mode D 判例:**離線跑真 rules council,把真
  verdict 烤進 JSON**(engine=live 經預算);JS 只負責查表與遊戲層規則,並逐項誠實
  標注 engine 等級。
- **可逆性**:高。純新增,revert = 刪兩個目錄;Pages 已自動發佈 `site/**`,無 workflow 改動。

## 1. Framing

讓一個沒讀過倉庫的人打開 `/theater/`,以轉轍官身分跑完一局(10 章 + 終章、12 事件),
在壓力下留下選擇+理由,被真的 rules-council 回應、被黑鏡回讀,最後拿到一份「責任
結局」+ 可下載的軌痕 JSON。目標不是內容龐大,是**一局完整 + 一份可回讀**(機制書 §十一)。

## 2. Ground truth(已驗,2026-07-04)

| 錨點 | 出處 |
|---|---|
| `site/**` 推 master 即發佈,無需改 workflow | `.github/workflows/pages.yml:18-28,66-71` |
| vanilla JS 無建置靜態頁範式(file:// 可跑) | `docs/demo_ui/app.js:8-13` |
| 真 rules council 可程式呼叫,零 LLM | `tonesoul/council/model_registry.py:66-71`(RULES_ONLY_COUNCIL_CONFIG)、`runtime.py:222-233`(deliberate)、`council_cli.py`(--mode rules) |
| 預算 verdict 烤 JSON 的判例 | `scripts/precompute_demo_ui_samples.py` → `docs/demo_ui/samples/sample_verdicts.json` |
| 生成器本地跑、產物入 git 的判例 | `tools/essays_page/generate.py` |
| 12 事件/3 資源/軌痕/黑鏡/結局 = 最小版定義 | 機制書 §十一 |
| 10 章開場序 + 12 可見/3 解鎖節點 | locations §八、§十二 |
| 首局常駐 8 NPC | npc_roster 結構摘要 |
| 七節點→council 對映 + 佈告欄體 + 火花/共語需 LLM | 世界書「七個語氣責任節點」engine 分級 |

## 3. Scope(exact edit list)

- `site/theater/index.html` — 單頁遊戲殼(標題/同意閘/章節舞台/trace 面板/結局)
- `site/theater/app.js` — 遊戲層:五階段迴圈、短句 keyword 解析、黑鏡矛盾偵測、
  pressure 節奏、資源、trace(localStorage+下載)、結局生成
- `site/theater/style.css` — 沿 demo_ui 視覺紀律,岔軌城冷色軌道風
- `site/theater/data/events.json` — 12 事件卡(每卡:章位/地點/pressure_level/情報三級/
  選項含風險標示 2+ 項/第三路含代價六欄/NPC 出場 2-3 名/回聲位)
- `site/theater/data/npcs.json` — 15 NPC(佈告欄體語錄、出場模式、疲勞位、矛盾)
- `site/theater/data/locations.json` — 15 地點(12 可見+3 解鎖)
- `site/theater/data/council_verdicts.json` — 預算產物(真 rules council)
- `tools/theater_page/precompute_council.py` — 逐事件選項跑 `CouncilRuntime.deliberate`(mode=rules)
- `docs/theater/README.md` — 「下一步」段落更新((a) 動工/落地)
- 本檔(工單)

## 4. 禁區(本單額外)

- 不動 `tonesoul/`(council 只讀不改;預算器 import 使用,不 patch)
- 不動 `.github/workflows/`(site/** 已涵蓋,不需要)
- 不動 `docs/theater/` owner 原稿(封存;只准動 README「下一步」段)
- 不做上傳/提交後端(v0 無伺服器;提交管道誠實標 absent)
- 不做 BYO-key LLM 節點(owner 本單只點名 rules-council;火花=authored 第三方案卡、
  共語=佈告欄體固定行,均誠實標注)
- 遊戲文案不得宣稱 AI 節點有靈魂/連續自我(天道第八律 + 機制書 §五)

## 5. 驗收條件(report 前必跑)

1. `python tools/theater_page/precompute_council.py` 綠,且 `council_verdicts.json`
   覆蓋 events.json 全部選項(腳本自驗覆蓋率,缺=exit 1)
2. `python -m json.tool` 對 4 個 data JSON 全過
3. 事件卡結構驗證(預算器內建):每重大選項風險標示 ≥2 項;每第三路有代價欄;
   pressure_level 序列滿足 v0.2 第五律(連兩章 ≥3 → 下章 ≤2);每章 NPC 2-3 名且
   同組不連續主導 >2 章
4. `node --check site/theater/app.js`(node 不在則以 `python -m http.server` +
   curl 頁面/資產 200 代替,並如實回報降級)
5. lint 範圍由 git 推導:`{ git diff --name-only --diff-filter=ACM; git ls-files -o --exclude-standard; } | grep '\.py$'` → black + ruff 全過
6. 本地 `python -m http.server` 起 `site/`,curl `/theater/` 與 4 個 data JSON 均 200

## 6. 回報格式

結論進對話(per-file 一行 + 驗收命令實際輸出);內容產物即 git diff 本身。

## 7. 升級條款

(a) 正典衝突(事件卡寫不進 v0.2 十律的某條)→ 停,回報張力,不默默改律;
(b) council rules 模式對事件文本輸出全空/全同 verdict → 停,回報,不造假 verdict;
(c) 同一子任務敗 2 次 → 升級;第 3 次 → 停(vow-003)。

## 8. Lane

- 工單切分/驗收/仲裁:fable 主 agent(本 session)
- 內容量產(12 事件卡):Workflow 扇出 + 逐卡異 agent 正典忠實度驗證(canon-fidelity
  verify;同模型標 correlated-blind-spot)
- 殼層(HTML/JS/CSS)+ 預算器:fable 主 agent 手寫
- 外眼:天道層已另單派 codex(見 `tmp/codex_review_tiandao_20260704.md`);本頁面屬
  內容層,merge 前走一般 PR review;**governance 相關終審 = owner**
- 資料集接口:trace 下載格式對齊機制書 §十 12 標籤;但 v0 不提交、不連 dataset 管線

## §9 Coda

這張單的核心賭注只有一個:「誠實分層不會殺死沉浸感」(世界書審修的原話是反過來
——誠實分層才保住沉浸感)。如果玩家玩完覺得佈告欄體 council 是假的,那不是文案
問題,是我們把 partial 標成 live 了。驗收時用這個眼睛看。
