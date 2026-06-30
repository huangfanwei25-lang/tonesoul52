# 【治理決策記錄】calibration → latitude binding（2026-06-30）

> 對象：`calibration_score`（#227，目前 score-only）是否該接上去，**綁未來信任 / 縮 latitude**
> （在 council 裡 down-weight、或 gate、或降 trust score）。
> 狀態：**owner-gated，待梵威 ratify。** 這份記錄是分析 + 建議，不是已生效的決定。

---

## 0. 這份記錄怎麼來的（方法與誠實限制）

由一個 11-agent workflow 產出：4 個事實驗證器（直接讀 origin/master 程式碼）＋ 5 個張力視角
（各自被一個對抗式驗證器再驗一遍）＋ 1 個完整性批判。

**誠實限制（必須先講）：**
- **single-model**：子代理接不到 codex（不同模型），所以張力分析是**同模型家族**——有
  correlated-blind-spot 風險。其中的 Monte Carlo 數字（如「完美校準者在 min_n=10 被誤判
  99.6%」）**在 owner 依賴前需不同模型重現**。程式碼層的事實（disjoint perspective 集合、
  resolver 不存在、`persona_track_record` 無 decay）是直接讀碼驗的，可信度較高。
- 一條視角（goodhart-gaming）的 agent 失敗了；但 Goodhart 已被 anti-pattern #1 的理由 + 其餘
  視角充分覆蓋（它是橫貫所有張力的那條）。
- 程式碼讀自 origin/master（#227, `1b297ae`）；本地 master 一度 stale 於 #212（stale-reference
  family，已用 fetch 避開）。

---

## 1. 決策（建議，待 ratify）

**現在不要 bind。`calibration_score` 維持 score-only。** 不是膽小，是四個查證後的理由：

1. **enforce 現在根本造不出來**：每一條防護措施都依賴一個「獨立、簽章、horizon-committed 的
   outcome resolver」——而它**不存在**（finance ground truth 是未建的 #226，「需資料源 + 地端
   模型」）。沒有它，就沒有可當 penalty 依據的 outcome 來源。
2. **5 條防護措施全部「不成立 as written」**：對抗式驗證把每一條都打穿了（見 §4）。
3. **想要的後果結構，已經有一部分**：council 已有兩條 live binding（見 §3.B），它們已經供應了
   「內部訊號能達到的」那部分後果。
4. **restraint 是 thesis**，這裡剛好也是經驗上對的選擇。

**但「不做」不是中性的**（見 §5）：後果缺口是 thesis 的真實短板。若要前進，正確順序是
**先治理 resolver、不是先治理 binding**（見 §6）。

---

## 2. 為什麼要評估這件事（脈絡）

- 倫理紅隊指出「我的選擇是空的，因為做錯不 cost 我」→ 想建後果結構。
- #227 落地 confidence-calibration primitive（Brier/ECE/reliability，**只 score**）。
- 本記錄評估的就是「把它接上去綁 latitude」這一刀——`calibration_score` 自己的 docstring 已標
  「binding is owner-gated」，這份記錄即那道 owner gate。

---

## 3. 張力來源（和哪些現有設計衝突）

**這節最重要，也修正了我先前的框架。**

**A. 反轉一條明文 anti-pattern。** outcome→voting-weight 是 v0b spec **anti-pattern #1「明文
禁止」**（`outcome_persistence.py:20` 與 `calibration_bucket_b.py:57` 各自重申）。理由是
Goodhart——防 council 塌成 yes-machine。**這是硬原則，不是 staging gate**（要和「先驗收集再看
數字」那條較弱的 feature-flag 延後區分開）。

**B. 但「我們從不綁 weight」是錯的——已經有兩條 live binding。**
- `voting_evolution`：對齊最終 verdict 的 perspective +0.05，normalize 後**相對壓低異議者**
  （`runtime.py:504` / `pre_output_council.py:116`，live）。
- `persona_track_record`：verdict type（approve=1.0 / block=0.0）→ `[0.85, 1.15]` multiplier，
  live 在 `gravity.py:230-245`。
- **關鍵區別**：兩者綁的是**內部自指訊號**（council 自己的 verdict），**不是外部 outcome**。
  新這一刀把**訊號類別**換成「現實 resolved 的 calibration」——這才是 anti-pattern #1 精確禁止
  的那條線。所以正確說法是：**不是「第一次綁 weight」，是「第一次讓現實 outcome 綁 weight」。**

**C. 既有 binding 自己就帶 conformity 警告。** `voting_evolution` 已 ship 一個
`suppression_observability` flag，警告「壓低異議 → council 偏 conformity」。新 binding 是往**同
方向**再推一把。

**D. 兩套 perspective 本體論不相容。** penalty 作用在 `gravity` 的 `{Muse, Logos, Aegis}`；而
量測 conformity 用的是 `voting_evolution` 的 `{guardian, analyst, critic, advocate, axiomatic}`
——**兩個 disjoint 集合，無 bridge**。任何「安全嗎」的儀表會指向**不是被罰的那個 council**。

**E. Axiom 4（非零張力）。** binding **永不可 silence / zero** 一個 perspective（唯一合法歸零是
Aegis 的 P0 safety veto，calibration **絕不可碰**）；最壞只能 `[0.85,1.15]` 的 15% clamp。但
clamp bound 的是 **raw multiplier**，`normalize()` 後的**真實 influence share** 會 leak 更低，且
**跨 cycle 複利**。

**F. Axiom 8 / un-gated write。** durable trust score 是 first-party memory（不被 egress gate
擋），但這個降 latitude 的寫入**該 owner-gated + 上 Aegis hash-chain audit**——不能像
`persona_track_record` 那樣每 cycle 靜默 `save()` + `except: pass` 靜默重置（那正是 Axiom 8 P0 的
un-gated-write 隱患，#219 就是為了避開它才做成 owner-gated）。

**G. meta.not_for。** label 只能是「系統內治理反思訊號」，**不能**是「認證此 reasoner 不可信 /
不安全」（否則踩 safety-certification 邊界 + corpus-poisoning trust store）。

**H. E0（可被修正）。** penalty 必須**可復原**（decaying / rolling window），不能是永久烙印。但
`persona_track_record` 是 **monotonic 無 decay 且 gitignored**——所以「decaying window」是
**net-new code，不是繼承**。誰以為「沿用既有 track-record」就會默默繼承那個「永久、版控看不見」
的烙印。

---

## 4. 防護措施 vs 它們的破綻（對抗式驗證結果）

提出的 5 條防護**全部「不成立 as written」**。關鍵破綻：

- **右但早（right-but-early）**：安全聲音的早期警告在短 horizon 上 resolve 成「錯」→ 被罰 →
  壓低 → 更少機會翻案 → **自我強化的壓制螺旋**。提議的免疫鑰匙（`suppression_recovery_rate`）
  是 **vapor**：該函數回單一全-council 聚合值、**無 per-perspective**、且自承「不量測 minority
  是否正確」。保護不了它存在的目的（那個 council 永遠不會回心轉意的孤獨正確聲音）。
- **小樣本噪音**：在 primitive 自己的 `min_n=10`，一個**完美校準**的 reasoner 被誤判 ~99.6%
  （single-model Monte Carlo，**待重現**）。要 `n≥200` + CI 下界 gate 才壓得住。
- **選擇性下注（killer）**：只對簡單的 call 標信心 → 被罰 ~0%（同一個過度自信 reasoner，全
  portfolio 可見時 100% 被抓）。**這把後果結構反轉成「reasoner 自己決定哪些 call 算數」。** 統計
  修不了 selection bias。
- **outcome 來源就是攻擊面**：`_validate` 只 range-check；**in-range-but-wrong / poisoned /
  self-resolved** 的 label 直接翻 verdict，沒有任何 guard。誰寫 outcome，誰就控制 calibration 的
  ground truth——而且能把它當**遙控器**去重塑 council 聽誰的（外部攻擊面）。
- **fail 方向必須相反**：必須 **fail-NEUTRAL**（缺 / 舊 / 壞資料 → full latitude），不是抄
  `decide_fail_closed` 的 deny。但 fail-neutral 又可被「永遠保持 n<min_n / 讓資料過期」**farm 成
  永久 full latitude**。
- **safe-to-flip gate 結構性失效**：它讀的 conformity 訊號是 §3.D 那組 disjoint 的 perspective，
  且 tension 訊號（`gravity` 的 ECHO_CHAMBER）**根本沒被持久化**——所以 divergence ledger 沒資料，
  gate 退化成「shadow 跑乾淨」這個專案自己命名過的陷阱。
- **三重 penalty 疊加在安全軸**：verdict-type（block→0.0）+ voting_evolution 對齊 + calibration，
  三條獨立子系統都往**同一個安全 perspective 的 deliberative weight** 壓，而那個 weight 必須活著
  BLOCK 才到得了 veto。

---

## 5. 「什麼都不做」也是一種治理失敗

完整性批判補的一條：本記錄每條張力都在講 binding 的危險，**沒有一條**講「永遠 score-only」的
代價。但那個代價是真的——後果缺口是 thesis 自己診斷出的短板；讓 calibration 永遠 inert ＝
**宣稱有後果結構卻沒有**＝對自己敘事的 claim>evidence（decorative theater）。

只是：今天「不做」剛好也是**唯一前提存在**的選項（resolver 不存在）。所以建議是「現在不做」，
**不是「永遠不做」**——差別在 §6 的順序。

---

## 6. 可逆性 + 建議路徑（resolver 先行的三階段）

**可逆性。** score-only 現狀**完全可逆**。一旦 enforce + durable trust store，可逆性**大幅下降**：
已 ship 的 N 個 cycle 不能重來；gitignored 的永久 store 會把烙印帶進下個 session。所以分階段 +
預設 OFF 是硬要求。

**sequencing 修正（完整性批判的核心建議）。** 原本「staged shadow→enforce」frame 方向對，但有
**sequencing error**：它治理 binding，卻把 resolver 當「前提」。反了——**resolver 才是權力集中
處**（誰判 call 錯、什麼 horizon、什麼權威、怎麼簽章）。正確順序：

- **Phase A — 先建 + 治理 outcome resolver**（它自己一份決策記錄）：獨立、簽章、horizon
  事前 committed、quorum / 雙來源。只在**有外部 ground truth 的 domain**（finance market-close）
  證明。**倫理 / 認識論 verdict：永久 shadow**（沒有、也不可能有外部 resolver）。
- **Phase B — 有可信 resolver 後，calibration 跑 shadow**：ledger 記在**被罰的那組 perspective**
  （Muse/Logos/Aegis）、**持久化 tension 訊號**、由**不同模型**紅隊。沿用 #219 的 default-OFF flag
  + try/except 隔離 + fake adapter + divergence ledger。
- **Phase C — owner-gated enforce**（獨立 PR）：**net-new decaying store**（非繼承
  persona_track_record 的 monotonic store）、clamp **複合** penalty（三條 binding 一起，不是各自
  clamp）、永不碰 P0 veto、永不低於 post-normalize floor、上 audit chain。

**另一條 owner 該明確選的叉路。** 如果擔心的是 conformity / yes-machine，**更便宜更誠實的替代**
可能是把**現有那兩條 self-referential binding 降成 shadow / observe-only**，而不是再加第三條。
先修已經在製造壓力的引擎，比新增一個同向的更符合 thesis。

---

## 7. 給 owner 的明確選擇

1. **採納建議**：現在不 bind，維持 score-only。**（推薦）**
2. **啟動 Phase A**：授權我起草「outcome resolver」的獨立決策記錄（finance domain 先）。
3. **考慮 de-bind**：授權我盤點 + 評估把現有兩條 binding 降 shadow。
4. **其他方向 / 先擱置。**

> 註：這份記錄本身**不該被當成「決定」merge 後就生效**——它記錄的是建議。實際的治理決定是你的；
> 你 ratify 哪一條，我再動。

---

接 [`consequence_structure_calibration_2026-06-30.md`](consequence_structure_calibration_2026-06-30.md)
（#227 design + gap map）、[`responsibility_runtime_dream_shadow_wiring_2026-06-29.md`](responsibility_runtime_dream_shadow_wiring_2026-06-29.md)
（#219 shadow→enforce 同紀律）。
