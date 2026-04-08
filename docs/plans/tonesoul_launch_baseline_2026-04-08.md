# ToneSoul Launch Baseline（2026-04-08）

> 目的：統一記錄語魂目前的 launch 狀態，取代分散在 5+ 個檔案裡的過時判斷。
> 範圍：internal alpha → collaborator beta → public launch 三層定義。
> 前置文件：`tonesoul_launch_maturity_program_2026-03-30.md`（已被本文件取代為 current truth）

---

## 1. Launch 三層定義

| 層級 | 意思 | 必要條件 | 目前狀態 |
|------|------|----------|----------|
| **Internal Alpha** | 創作者和受信任的 AI agent 可以使用 | 基本 continuity、docs 可發現、claims 誠實 | **已達成** |
| **Collaborator Beta** | 小規模外部協作者可以在指導下使用 | 重複驗證、launch ops 明確、backend 決定、安全審計通過 | **接近但有 blockers** |
| **Public Launch** | 公開 claims 不會過度承諾 | overclaim 邊界明確、operations 穩定、驗證覆蓋更廣 | **未達成** |

---

## 2. 系統現狀快照

### 程式碼
- 91 個 Python 模組（`tonesoul/`）
- 405 個測試檔案，3019 個測試
- 845 個 commits
- 紅隊審計：2 輪，18 個 findings，17 已修復

### 治理引擎
- Soul Integral: 動態計算，指數衰減
- Vow System: 3 個活躍 vow，enforcer 已 fail-closed
- Tension Engine: 事件驅動，history 持久化
- Baseline Drift: caution/innovation/autonomy 三軸
- Reflex Arc: soul band 分類、gate modifier、vow enforcement、council block
- Council: 多角色審議，dossier 產出
- Escape Valve: circuit breaker for constraint loops
- Governance Depth Routing: light/standard/full 三層（Phase 848-854 已關閉）

### 記憶層
- Backend: **FileStore**（Redis 可用但本機未啟動）
- Session traces: 4（1 個已簽名 + chained）
- Compactions: 1
- Subject snapshots: 2
- Aegis Shield: Ed25519 簽名 + SHA-256 hash chain + content filter
- Temporal validity: compaction/snapshot 帶 `valid_from`/`valid_until`

### 操作面
- CLI: `start_agent_session.py`（tier 0/1/2）、`end_agent_session.py`、`run_observer_window.py`、`diagnose`
- HTTP Gateway: `scripts/gateway.py`（認證必填、CORS 限制）
- Dashboard: Streamlit（`apps/dashboard/`）
- 自我改善: 17 trial promoted, 1 parked

---

## 3. Collaborator Beta Blockers

### 硬阻擋（必須解決）

| # | Blocker | 嚴重度 | 說明 |
|---|---------|--------|------|
| B1 | **無端到端使用驗證** | HIGH | 沒有人類操作者完整走過一次治理感知 session 循環 |
| B2 | **Backend 決定未做** | MEDIUM | FileStore vs Redis — 目前預設 file，Redis 依賴外部服務 |
| B3 | **Vow 語義分析缺失** | MEDIUM | 紅隊 #14：vow evaluator 只有關鍵字比對，不能抓語義違反 |

### 軟阻擋（建議解決）

| # | Issue | 說明 |
|---|-------|------|
| S1 | Design center 不存在 | 沒有一份文件解釋「語魂為什麼這樣分層」 |
| S2 | Dashboard 未對齊 tier model | Status panel 沒有反映 tier 0/1/2 的資訊層級 |
| S3 | 公開 claim 沒有 honesty gate | 沒有機制防止 overclaiming（例如：「AI 有意識」） |
| S4 | Session trace 太少 | 4 個 trace 不足以驗證 continuity resilience |

---

## 4. 各 Phase 對照

| Phase | 目標 | 狀態 |
|-------|------|------|
| 721 | 整合 launch baseline | **本文件** |
| 722 | 重複 live continuity validation | 已有 1 次 wave（7/7 passing），需要更多 |
| 723 | Backend 決定 | **未做**（B2）|
| 724 | Launch operations surface | 已有 `tonesoul_launch_operations_surface_2026-03-30.md`，需更新 |
| 725 | Public claim honesty gate | **未做**（S3）|
| 726 | Go/no-go review | 已有框架（`tonesoul_collaborator_beta_go_nogo_review_2026-03-30.md`），需依據本文件重做判斷 |
| 729 | Design center | **未做**（S1）|
| 730 | 3-day execution program | 需等 729 |

---

## 5. 建議路徑

1. **Phase 723**（Backend 決定）→ 最小決定：FileStore 作為 collaborator beta 預設，Redis 作為可選升級
2. **Phase 729**（Design center）→ 寫一份 `DESIGN_CENTER.md` 解釋分層邏輯
3. **Phase 725**（Honesty gate）→ 在 session-start 加入 claim 邊界提示
4. **Phase 726**（Go/no-go）→ 依據 B1-B3 和 S1-S4 做顯式判斷
5. **B1 端到端驗證** → 等人類操作者有空時做

---

## 6. 歷史文件交叉參照

以下文件已被本文件取代為 current truth：
- `docs/plans/tonesoul_launch_maturity_program_2026-03-30.md`
- `docs/plans/tonesoul_launch_validation_matrix_2026-03-30.md`
- `docs/plans/tonesoul_launch_operations_surface_2026-03-30.md`
- `docs/plans/tonesoul_collaborator_beta_go_nogo_review_2026-03-30.md`
- `docs/plans/release_readiness_staging.md`（2026-02-14，非常過時）
