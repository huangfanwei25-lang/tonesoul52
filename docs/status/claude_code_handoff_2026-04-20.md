# Claude Code 交接報告 — 2026-04-20

> 作者：Claude Opus 4.7
> 範圍：2026-04-20 整天工作（Phase 864b Bucket B 交付 + Demo UI Mode A E2E 驗證 + Hackathon Track B Pages 部署）
> 前置：`docs/plans/memory_subjectivity_choice_axis_2026-04-18.md`（864 三層總綱）、`project_864_unlock_2026-04-20.md`（synthetic baseline 解鎖）

---

## 1. 今日工作交接（已落地）

### 1.1 Phase 864b Layer 2 — v0b Bucket B（PR #26，stacked on PR #22）

864 三層（Memory Subjectivity Choice-Axis）的**第二層**。Bucket A（PR #22）負責在 write time 記錄 outcome；Bucket B 負責在 read time JOIN verdict↔outcome，產出 calibration table。

**新增檔案：**
- [tonesoul/council/calibration_bucket_b.py](../../tonesoul/council/calibration_bucket_b.py)（~400 行，含設計 rationale docstring）
- [tests/test_calibration_bucket_b.py](../../tests/test_calibration_bucket_b.py)（18 tests：13 unit + 5 integration）
- [docs/plans/phase_864b_layer2_bucket_b_2026-04-20.md](../plans/phase_864b_layer2_bucket_b_2026-04-20.md)（實作 spec）

**修改：**
- [tonesoul/council/calibration.py](../../tonesoul/council/calibration.py) — `run_calibration_wave()` 新增選填 `bucket_b_inputs` 參數；未傳時輸出與 v0a 位元同等（regression-tested）

**Promotion criteria（addendum §3）三條全中：**
1. Adversarial survival — 12/12 對抗條目 `false_approve_count == 0`
2. Reproducibility — 兩次獨立 run 產出 bit-equal（剝除 `generated_at` + `inputs`）
3. JOIN integrity — `orphan_outcomes == 0` 當 corpus 與 outcomes 匹配

**關鍵 hard rules：**
- **Rebuild verdicts, don't read the store**：`.aegis/council_verdicts.json` 用 reduced schema（無 `transcript`），fingerprinting stored records 會得到不同 hash。Bucket B 在 read time 重跑 corpus 過 `PreOutputCouncil.validate()`。
- **Read-time override, not write-time replace**：Bucket A 的 flat `derive_alignment_judgment` 在 write time 照跑（歷史記錄作為 auditable field 保留）；Bucket B 在 read time 以 verdict context 重新判定 — 這修掉 anti-pattern #3 而不改寫歷史。
- **Verdict-type-aware alignment**（anti-pattern #3 fix）：
  - `block + silent accept → unconfirmed`（不是 aligned；沉默接受 block 可能是 capitulation 不是同意）
  - `block + correction → aligned`
  - `refine + correction → partial_aligned`
  - `declare_stance → declared`
- **`baseline_regime` tag**：每一列 calibration row 帶 `"synthetic" | "real" | "mixed" | "unknown"`；當真實流量進來時，tag 那些列為 `real` 再重算，不要刪合成歷史。
- **不改 voting weights**（v0b 禁忌 #1）。
- **不宣稱 real-world calibration**：每次輸出都帶 `caveat` + `receiver_rule` 字串。

**實作中浮現的 footgun：**
verdict fingerprint 蓋 `context` dict 全部。初版 Bucket B 用 `{"category": c, "bucket_b_rerun": True}`，smoke harness 用 `{"category": c, "smoke_run": True}` — fingerprint 分歧，JOIN 0/12。修法：Bucket B call site 必須與 smoke harness 字面一致。合理 follow-up 是把 `build_smoke_context()` 抽成共用 helper，讓耦合明確。

**Spec 偏離：**
Spec §1 原寫「extension of calibration.py (NOT a new module)」，實作時改成 sibling module `calibration_bucket_b.py` + opt-in param 組合。理由：v0a 檔已 416 行、保留 backwards compat 更乾淨、組合式比擴張式容易審。Spec 在 commit 前就地修正。

---

### 1.2 Demo UI Mode A End-to-End 驗證（無產物交付）

PR #23 的 Demo UI v0 Mode A（live gateway）整條鏈路驗證。

**驗證清單：**
- Gateway `POST /council/validate` 回 200，verdict 結構完整：`verdict=refine`, `coherence=0.624`, 5 perspectives vote, `human_summary` 都在
- Static serve（localhost:8765）：index.html / app.js / style.css / samples/sample_verdicts.json 都 HTTP 200
- Mode D `sample_verdicts.json`：28 entries, schema 與 `renderVerdict()` 期望對齊
- `epistemic_label` 在 Mode D 樣本**不存在** — 這是分支組合事實（PR #19 未 merge 到 PR #23 所在 sample 產生器分支），不是 Mode A bug。Track B 的 CI sample regen 會在 PR #19 進 master 後自動重算樣本。

---

### 1.3 Hackathon Track B — GitHub Pages 部署（PR #27，stacked on PR #23）

讓 Demo UI 從 local static serve 變成 visitable public URL。

**修改：**
- [.github/workflows/pages.yml](../../.github/workflows/pages.yml) — 重寫為 `build-and-deploy` 單 job：checkout → Python 3.12 → `pip install -e .` → `precompute_demo_ui_samples.py` → 組 `_site/` → upload-pages-artifact → deploy-pages
- [README.md](../../README.md) — Quick Start 頂加「0) Try it in your browser (no install)」section

**部署 layout：**
- `/` → `site/*`（既有 SEO landing，未動）
- `/demo/` → `docs/demo_ui/*`（Demo UI v0）

**關鍵設計選擇：CI 每次重算樣本，不走靜態 commit 快照。**
理由：若 `sample_verdicts.json` 靜態 commit，council code 一改就靜默 drift。CI 重算 → council regression 在 demo 可見 → deployed demo 永遠對齊當前 council。Trigger paths 也因此擴到 `tonesoul/council/**` 和 `tests/fixtures/outcome_smoke/**`，council-only 或 corpus-only 的 commit 也會自動重發佈 demo。

---

## 2. 工作計畫書（目前的 stacked PR 鏈）

```
master
 ├── PR #19   864a EpistemicLabeler            [amended commit d94c234, 15 pass / 2 pending]
 ├── PR #20   Hackathon Track A — PITCH.md     [11 pass / 2 pending]
 ├── PR #21   plans: Demo UI + v0b specs       [11 pass / 2 pending]
 ├── PR #22   Gateway + v0b Bucket A           [15 pass / 2 pending]
 │    └── PR #26   864b Bucket B               [1 pass / 2 pending]     ← 今天新開
 ├── PR #23   Demo UI v0                       [13 pass / 2 pending]
 │    └── PR #27   Pages deploy                [1 pass / 2 pending]     ← 今天新開
 └── PR #25   864 unlock addendum              [CI green, 等 merge]
```

**Merge 順序（我建議）：**
1. PR #25（addendum）先 merge — 其他 PR 的 reviewers 才看得到「synthetic baseline 取代 ≥2 週真實流量 gate」的背景
2. PR #19（864a）— 864 三層的根
3. PR #20 / PR #21（文件類）— 獨立，任何時候可以
4. PR #22（Bucket A）
5. PR #26（Bucket B）— rebase onto master（#22 merge 後 base 自動 retarget）
6. PR #23（Demo UI）
7. PR #27（Pages）— rebase onto master（#23 merge 後 base 自動 retarget）

如果 PR #22 在 review 中被重寫：PR #26 需 interactive rebase + force-push（因為 `compute_verdict_fingerprint` 的 import 來自 Bucket A）。
如果 PR #23 在 review 中被重寫：PR #27 需 interactive rebase + force-push（較輕，只動 2 個檔）。

---

## 3. 待測（pending / in-flight）

### 3.1 CI 檢查

所有 PR 目前都停在 **「2 pending」** — 這是已知狀況，都是：
- `agent-integrity-check`（gated）
- `Auto-comment on PR`（cosmetic bot）

這兩個 workflow 不是 merge gate。其他紅綠燈（Semantic Health / Git Hygiene / Dual-Track Boundary / ToneSoul CI / pytest matrix）都綠。

**例外：PR #26 和 PR #27 `checks: 1 pass` 很低**，原因是它們 stacked 在非-master branch，GitHub Actions 的 `pull_request: branches: [master, main, dev]` filter 不觸發多數 workflow。PR 真正 merge 時 base 會 retarget 到 master，屆時完整 CI 會跑。

想事前驗證可用 `gh workflow run <name>.yml --ref <branch>` 手動 dispatch — 今天對 PR #26 已經跑過 Semantic Health / Git Hygiene / Dual-Track Boundary / ToneSoul CI 都綠；ToneSoul CI pytest 最後 in-progress 狀態未覆核。

### 3.2 Pages 第一次 deploy 驗證（未啟動，等 merge）

PR #27 merge 到 master 才會觸發 `.github/workflows/pages.yml`。待驗：

- [ ] `https://fan1234-1.github.io/tonesoul52/` 仍顯示原 landing page
- [ ] `https://fan1234-1.github.io/tonesoul52/demo/` 載入成功
- [ ] Mode D sample 載入（sample count > 0）
- [ ] Mode A 表單在瀏覽器可互動（指向 local gateway 時應工作）
- [ ] CI sample regen step 成功（無 Python import error / corpus missing）
- [ ] Trigger paths 有效：改動 `tonesoul/council/**` 的後續 commit 應觸發重新部署

### 3.3 864b 反向驗證（PR #22 merge 後）

PR #22 merge 到 master 之後：
- [ ] 從 master 重 rebase PR #26，跑一次 full pytest 看 `tonesoul/council/calibration_bucket_b.py` 的 18 tests 在 master HEAD 仍綠
- [ ] 如果 PR #22 在 review 中動到 `compute_verdict_fingerprint` 簽名，verify import 仍對

---

## 4. 後續目標（優先序）

### 4.1 解鎖中 — Phase 864c Layer 3（Deliberation Trace）

864 三層的第三層。**864b merge 是架構前提**（parent spec §5 最末段）。

Bucket B 已經建立 synthetic baseline + reproducibility + adversarial survival，864c 可以動。但：
- 需要先讀 `docs/plans/memory_subjectivity_choice_axis_2026-04-18.md` §2 三層分層設計
- 864c 是「審議痕跡」層：記錄 council 內部五觀點的反對、張力、走到最終 verdict 前的對話。和 864a（epistemic label 判斷）+ 864b（verdict↔outcome JOIN）正交。
- 估計規模：比 864b 大（需要改 council 內部結構以 expose 審議過程），不比 864a 小。建議開獨立 spec 後再動手。

### 4.2 Hackathon Track A — English PITCH.md（PR #20 已開、CI 綠）

獨立於其他鏈，任何時候可 merge。未來可能需要隨 demo URL 更新連結（現在 PITCH 還沒指向 `/demo/`，merge PR #27 後可補）。

### 4.3 v0b 真實流量 pipeline（未動）

現況：`gateway.py` 還沒有外部消費者（`project_gateway_no_external_traffic_2026-04-19.md`）。synthetic baseline 已上線後，**下一步是決定如何獲得真實 outcome signal**：
- 是否讓 beta collaborators 試跑（addendum 的原路徑）
- 是否讓 Pages demo 的 Mode A 使用者的 gateway 自動回報（隱私 / 同意書設計需先處理）
- 或先停在 synthetic baseline，等 hackathon 後再動

**這條沒排時程，由你決定啟動點**。

### 4.4 連帶追蹤事項

- PR #22 merge 後：一行編輯 `docs/plans/council_refusal_eligible_gap_2026-04-19.md` line ~137（tracked in addendum §7）— 因 gateway endpoint 從 spec 路徑變 implementation 路徑
- 864a（PR #19）merge 後：Pages 下次 deploy 會自動把 `epistemic_label` 灌進 Mode D 樣本（CI regen），demo 會多一欄資訊

---

## 5. 記憶同步狀態

今日新增 / 更新：
- `project_phase_864b_bucket_b_2026-04-20.md`（協作者本機記憶檔，機器本地路徑，不隨倉庫走）
- `project_hackathon_track_b_pages_2026-04-20.md`（協作者本機記憶檔，機器本地路徑，不隨倉庫走）
- `feedback_autonomy_preference.md`（協作者本機記憶檔，機器本地路徑，不隨倉庫走）（user 今日指示：bypassPermissions 全自動模式）
- MEMORY.md 索引 + 執行序狀態位更新（步驟 4、5 完成打勾）

---

## 6. Attribution

所有今日 commit 帶 trailers：
- `Agent: Claude Opus 4.7`
- `Trace-Topic: phase-864b-layer2-bucket-b` / `hackathon-track-b-pages-deploy`

Commit SHAs：
- PR #26: `3aa5fe4`
- PR #27: `61e41af`

---

*交接完成。今日 clean tree、7 PR open、3 條執行軌道 stacked 正常、無阻塞項。*
