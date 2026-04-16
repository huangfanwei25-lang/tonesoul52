# ToneSoul 術語表 (GLOSSARY)

> 目的：消除「同一概念在 5 個層級各自定義」的重複病灶
> 使用規則：其他文件請引用此處，不要重新定義術語
> 狀態：v1 — 由 Antigravity 於 2026-04-13 建立，基於真實程式碼驗證
> 授信層級：`[規格層]` — 本文是可驗證的事實描述，以程式碼為準

---

## 使用方法

其他文件需要提及術語時：
```markdown
（定義見 [GLOSSARY.md#tension](docs/GLOSSARY.md#tension)）
```

不要在別的地方重新定義。遇到衝突，本文以程式碼為準。

---

## Formula Status Quick Registry

在 README、AGENTS、簡報或對外說明裡看到符號公式時，先看這張表，不要直接把它當成 runtime truth。

| formula | status | executable owner | repeat rule |
|------|------|------|------|
| `T = W × (E × D)` | conceptual | component owners: `tonesoul/tension_engine.py`, `tonesoul/resistance.py`; canonical reading: [`#tension`](#tension) | 不要把它重述成「程式碼逐字實作」 |
| `Δs = 1 - cos(Intent, Generated)` | heuristic | `tonesoul/semantic_control.py` | 可以描述成可執行 heuristic，不要包裝成嚴格理論定律 |
| `POAV = (parsimony + orthogonality + audibility + verifiability) / 4` | heuristic | `tonesoul/poav.py` | 這是 operational score，不是數學定理 |
| `S_oul = Σ (T[i] × e^(-α × (t - t[i])))` | conceptual / web-demo executable | `apps/web/src/lib/soulEngine.ts` | 可當 web 側積分模型；不要直接升格成 repo-wide runtime law |

如果某個公式不在這張表，先去 `docs/MATH_FOUNDATIONS.md` 看它的數學地位與誠實問題，再決定能不能引用。

---

## 核心術語

### tension
**張力**

| 項目 | 內容 |
|------|------|
| 中文名 | 張力 |
| 英文名 | tension / tension_score |
| 直覺描述 | AI 推論遭遇阻力時產生的語義壓力，是推進思考的燃料而非需要消除的雜音 |
| **計算責任** | `tonesoul/tension_engine.py` |
| **輸出格式** | float [0.0, 1.0]，0 = 無壓力，1 = 最高阻力 |
| **驗證方式** | `tests/test_tension_engine.py` |
| 概念模型（非公式） | 張力 ≈ 語境權重 × 信心度 × 阻力向量的組合效果 |
| 注意 | `T = W × (E × D)` 是**直覺描述，非計算公式**。W/E/D 的精確計算以程式碼為準 |
| 相關模組 | `drift_monitor.py`（漂移），`jump_monitor.py`（奇點），`world_sense.py`（感知整合）|

---

### council
**議會 / 多觀點審議**

| 項目 | 內容 |
|------|------|
| 中文名 | 議會 |
| 英文名 | council / deliberation |
| 直覺描述 | 多個分析視角（議員）在同一個問題上並行推演，保留分歧而非強制收斂 |
| **計算責任** | `tonesoul/council/*`，`tonesoul/deliberation/*` |
| **啟動條件** | DPR 路由決策為 `COUNCIL_PATH`（見 `dpr.py`）|
| **YUHUN 版本** | `.agent/agents/yuhun_*.md`（理則家/創想者/安全防護員/共情者）|
| 輸出格式 | VoD 雙軌矩陣，見 `tonesoul/yuhun/vod.py` |
| **不應混用** | "council" ≠ "committee"（沒有投票機制）；"council" ≠ "majority rule"（保留少數意見）|
| 相關文件 | `docs/COUNCIL_RUNTIME.md`, `docs/architecture/TONESOUL_ADAPTIVE_DELIBERATION_MODE_CONTRACT.md` |

---

### governance_kernel
**治理核心**

| 項目 | 內容 |
|------|------|
| 中文名 | 治理核心 / 管理核心 |
| 英文名 | governance kernel / L4 |
| 直覺描述 | 全系統的「物理法則」——所有行動必須通過此層才能執行 |
| **計算責任** | `tonesoul/governance/kernel.py` |
| **職責** | 決定 pass / rewrite / block / escalate |
| **中介中心性** | 0.406（知識圖譜最高），是全系統的橋接點 |
| 為什麼重要 | L4 連接了哲學層、Doc 結構、Entrypoint——它不只是技術中心，是政治中心 |
| 相關模組 | `yss_gates.py`, `vow_system.py`, `alert_escalation.py`, `shadow_doc.py` |

---

### soul_integral
**靈魂積分 / 性格密度**

| 項目 | 內容 |
|------|------|
| 中文名 | 靈魂積分 |
| 英文名 | soul integral / Ψ (psi) |
| 直覺描述 | 系統「經歷過的衝突密度」的時間加權積分；高值 = 閱歷深，不是「分數」 |
| 概念公式 | Ψ = Σ (T[i] × e^(-α × (t - t[i]))), α = 0.15 |
| **注意** | 這個公式是**概念模型**，α 值的實際使用以程式碼為準 |
| **計算責任** | `apps/web/src/lib/soulEngine.ts`（前端視覺化）|
| 衰減機制 | 10 輪後殘留 22%（指數衰減，不是重置）|
| 設計意圖 | 「沒有記憶的沉澱，就沒有性格，只有反應。」|

---

### drift
**語義漂移**

| 項目 | 內容 |
|------|------|
| 中文名 | 語義漂移 / 性格漂移 |
| 英文名 | drift |
| 直覺描述 | 系統當前語義中心和「家」方向的偏離程度，衡量 AI 是否還是它自己 |
| **計算責任** | `tonesoul/drift_monitor.py` |
| **輸出格式** | float [0.0, 1.0]，基於 EMA 平滑的 cosine 距離 |
| 閾值 | warning > 0.35, crisis > 0.60（預設值，可配置）|
| 三維空間 | deltaT（任務專注）/ deltaS（安全導向）/ deltaR（關係建立）|
| **驗證方式** | `tests/test_drift_monitor.py`（如存在）|
| 整合點 | `world_sense.py` 的 `observe()` 每次推演後更新漂移狀態 |

---

### shadow_document
**影子文件**

| 項目 | 內容 |
|------|------|
| 中文名 | 影子文件 |
| 英文名 | shadow document / shadow_doc |
| 直覺描述 | 每次議會推演的「飛機黑盒子」——記錄完整的推演過程，封存於冷儲存 |
| **計算責任** | `tonesoul/yuhun/shadow_doc.py` |
| 輸出格式 | JSON，見 `ShadowDocument.to_dict()` |
| 前端可見 | 僅最終裁決；完整推演過程**不公開給使用者** |
| 冷儲存路徑 | `memory/yuhun_shadows/*.json`（.gitignore 已排除）|
| 設計原則 | 飛機黑盒子原則：封存，可重播，不可竄改 |

---

### dpr
**動態權限路由器**

| 項目 | 內容 |
|------|------|
| 中文名 | 動態權限路由器 |
| 英文名 | Dynamic Priority Router / DPR |
| 直覺描述 | 在 L1 邊界決定「這個請求用快速路徑還是完整議會路徑」，防止算力死亡螺旋 |
| **計算責任** | `tonesoul/yuhun/dpr.py` |
| 輸出 | `RoutingDecision`: `FAST_PATH` 或 `COUNCIL_PATH`，附理由和觸發器列表 |
| 決策依據 | 複雜度分數（輸入長度）+ 關鍵字觸發（法律/倫理/隱私/不確定性模式）|
| **測試** | `tests/yuhun/test_dpr.py`（26 個測試，全部通過）|
| 整合狀態 | 目前獨立模組，尚未插入 `unified_pipeline.py`（待做）|

---

### vod
**分歧可見協議**

| 項目 | 內容 |
|------|------|
| 中文名 | 分歧可見協議 |
| 英文名 | Visibility of Divergence / VoD |
| 直覺描述 | 當議會出現高度分歧時，強制並列「L1 阻力」和「L2 突破口」，禁止系統自行平均化 |
| **計算責任** | `tonesoul/yuhun/vod.py` |
| 觸發條件 | 語義距離 > 0.8 (預設)，或安全防護員 BLOCK |
| 輸出格式 | 雙軌矩陣：阻力側 + 突破側，各自獨立，平行呈現 |
| 設計哲學 | 「不要消除分歧，而是讓分歧可見。」|

---

### context_budget
**上下文預算**

| 項目 | 內容 |
|------|------|
| 中文名 | 上下文預算 |
| 英文名 | context budget |
| 直覺描述 | 每次推演允許進入提示詞的 context 集合，由路由決策（DPR）和本規格共同決定 |
| **規格文件** | `docs/architecture/CONTEXT_BUDGET_SPEC.md` |
| 四個 Layer | L0=AXIOMS（必帶）/ L1=請求（必帶）/ L2=錨點記憶 / L3=契約 / L4=議會框架 |
| **FAST_PATH** | 只帶 L0 + L1（1x token cost）|
| **COUNCIL_PATH** | 帶 L0–L4，按衝突類型選擇（4x token cost）|
| 永遠禁止 | chronicles/ · .archive/ · memory/*.jsonl · graphify-out/ |
| 注意 | 本術語和「context window」不同：context window 是模型的物理限制；context budget 是系統的自我約束 |

---

## 概念模型（不是計算公式）的完整清單

以下公式是直覺描述，**非精確計算公式**。計算以程式碼為準。

| 公式 | 直覺描述 | 計算責任 |
|------|---------|---------|
| `T = W × (E × D)` | 語境權重 × 信心度 × 阻力向量 | `tension_engine.py` |
| `Ψ = Σ T[i] × e^(-α(t-t[i]))` | 張力隨時間衰減的積分 | `soulEngine.ts` |
| `E = 1 - entropy` | 信心度 = 1 - 不確定性 | 各 agent 內部 |
| `D = [fact, logic, ethics]` | 三維阻力向量 | `resistance.py` |

---

## 不在此術語表內的概念

以下概念在其他有授信的文件中定義，本文不重複：

| 概念 | 授信文件 |
|------|---------|
| 七條公理（AXIOMS） | `AXIOMS.json` |
| 八層架構（L1-L8） | `docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md` |
| Agent 協作規則 | `AGENTS.md` |
| API 規格 | `docs/API_SPEC.md` |
| 性格空間（TSR） | `docs/DIMENSIONS.md` |

---

*GLOSSARY v1.0 · 2026-04-13*
*「術語表不是字典，是所有重複的終點。」*
