# Codex Task: Phase 578-583 — Deprecated 模組移除 + Inter-Soul Tension Protocol

**指派者**: 痕 (Hén)
**日期**: 2026-03-20
**分支**: feat/env-perception（不可 push 到 master）
**前置條件**: 2555 tests passing, lint clean

---

## 全局規則

1. **每個 Phase 單獨 commit**，commit message 格式：`refactor(Phase N): [摘要]` 或 `feat(Phase N): [摘要]`
2. 每個 Phase 完成後：`ruff check tonesoul tests` + `pytest tests/ -x --tb=short -q` 全過
3. 測試數會因移除 deprecated 測試檔而下降 — 這是預期行為。預期最終 ≥ 2520
4. **禁止修改** `governance/kernel.py`、`unified_pipeline.py`、`AGENTS.md`、`CODEX_PROTOCOL.md`
5. 連續失敗 3 次 → 停下，寫 CODEX_HANDBACK.md

---

## Phase 578: 移除 council_adapter.py + tonesoul_llm.py

**脈絡**: 這兩個模組是最薄的 deprecated 包裝，僅被自身的 deprecated 測試引用。

### 任務
- [ ] 刪除 `tonesoul/council_adapter.py`
- [ ] 刪除 `tests/test_council_adapter_deprecated.py`
- [ ] 刪除 `tonesoul/tonesoul_llm.py`
- [ ] 刪除 `tests/test_tonesoul_llm_deprecated.py`
- [ ] 更新 `scripts/healthcheck.py` — 從模組清單中移除 `"tonesoul.tonesoul_llm"` 那行
- [ ] 確認 `tonesoul/__init__.py` 沒有 re-export 這兩個模組（應已不存在）
- [ ] ruff + pytest 全過

### 禁止
- ❌ 不可修改 `tonesoul/council/runtime.py`（那個由 Phase 579 處理）
- ❌ 不可刪除 `tonesoul_simple_app.py` 或 `tonesoul_simple_bridge.py`（那些引用的是 `tonesoul52`，不是本次目標）

---

## Phase 579: 遷移 build_council_summary → council/runtime.py，移除 role_council.py

**脈絡**: `tonesoul/role_council.py` 有一個核心函數 `build_council_summary()`（~54 行）被兩處活躍碼使用：
1. `tonesoul/council/runtime.py` L12 — `from ..role_council import build_council_summary`
2. `tonesoul/frame_router.py` L8 — `from .role_council import build_council_summary`

`council/runtime.py` 內部已有 `_build_role_summary()` 包裝方法，這是自然的吸收點。

### 任務
- [ ] 將 `build_council_summary()` 及其所有輔助函數（`_decision_mode`, `_collect_operational_roles` 等）從 `role_council.py` 搬到 `council/runtime.py` 的模組層級
- [ ] 更新 `council/runtime.py` — 移除 `from ..role_council import build_council_summary`，改用本地定義
- [ ] 更新 `frame_router.py` — 改 import 來源：`from .council.runtime import build_council_summary`
- [ ] 保留 `merged["role_council"]` 鍵名不變（向後相容 transcript 結構）
- [ ] 刪除 `tonesoul/role_council.py`
- [ ] 刪除 `tests/test_role_council_integration.py`
- [ ] 檢查 `tests/test_council_runtime.py` 是否有對 `role_council` 的引用，若有則更新
- [ ] 檢查 `tests/test_custom_role_council.py` — 如果它測的是 `tonesoul.role_council` 模組就刪除；如果測的是 council runtime 的 role 功能就保留
- [ ] ruff + pytest 全過

### 技術提示
- `build_council_summary` 的簽名：`(context, selected_frames, role_summary, role_catalog) -> Dict[str, object]`
- 輔助函數可能包括 governance 角色權重計算、stance 分類、dissent ratio 計算
- 搬遷後確保 `_build_role_summary()` 方法仍然正確調用本地版本

---

## Phase 580: 移除 unified_core.py + _legacy/unified_core_compat.py

**脈絡**: `UnifiedCore` 是舊的主協調器，已被 `UnifiedPipeline` 完全取代。引用鏈：
- `tonesoul/unified_core.py` ↔ `tonesoul/_legacy/unified_core_compat.py`（相互引用）
- `tests/test_unified_core.py`（11 個 import 點）
- `tests/test_unified_core_properties.py`
- `scripts/healthcheck.py` — `"tonesoul.unified_core"` 在模組清單中
- `examples/demo_loop_integration.py` — `from tonesoul.unified_core import UnifiedCore`

### 任務
- [ ] 刪除 `tonesoul/unified_core.py`
- [ ] 刪除 `tonesoul/_legacy/unified_core_compat.py`
- [ ] 如果 `tonesoul/_legacy/` 目錄只剩 `__init__.py`，刪除整個 `tonesoul/_legacy/` 目錄
- [ ] 刪除 `tests/test_unified_core.py`
- [ ] 刪除 `tests/test_unified_core_properties.py`
- [ ] 更新 `scripts/healthcheck.py` — 移除 `"tonesoul.unified_core"` 那行
- [ ] 更新 `examples/demo_loop_integration.py` — 將 `from tonesoul.unified_core import UnifiedCore` 改為 `from tonesoul.unified_pipeline import UnifiedPipeline`，並在範例中使用 `UnifiedPipeline` 替代
- [ ] 刪除 repo 根目錄的 `fix_nonlocal.py`（這是一次性修復 unified_core.py 的腳本，目標已不存在）
- [ ] ruff + pytest 全過

### 禁止
- ❌ 不可刪除 `tonesoul_simple_app.py` 或 `tonesoul_simple_bridge.py`（引用的是 `tonesoul52` 套件，不是本次目標）
- ❌ 不可修改 `tonesoul/drift_tracker.py`（僅在 docstring 中提到 `unified_core.py`，無程式碼依賴）

---

## Phase 581: 移除 market deprecated 模組 + 更新 scripts

**脈絡**: `tonesoul/market/forecaster.py` 和 `tonesoul/market/gold_detector.py` 已標記 deprecated。引用來自三個 script 和三個測試檔。

### 任務
- [ ] 刪除 `tonesoul/market/forecaster.py`
- [ ] 刪除 `tonesoul/market/gold_detector.py`
- [ ] 刪除 `tests/test_forecaster.py`
- [ ] 刪除 `tests/test_gold_detector.py`
- [ ] 刪除 `tests/test_market_deprecation.py`
- [ ] 更新 `tonesoul/market/__init__.py` — 確認沒有 re-export 已刪除的模組
- [ ] 更新 `scripts/run_gold_scan.py` — 在頂部加入清楚的棄用通知，移除 `from tonesoul.market.gold_detector import ...`，改為直接 print 訊息並退出：`sys.exit("run_gold_scan.py: GoldDetector has been removed. See task.md Phase 581.")`
- [ ] 更新 `scripts/run_market_sweep.py` — 同上處理
- [ ] 更新 `scripts/test_dream_engine_5289.py` — 同上處理（`from tonesoul.market.forecaster import ...` 改為退出通知）
- [ ] ruff + pytest 全過

### 技術提示
- `tonesoul/market/` 下還有其他非 deprecated 的模組（如 `analyzer.py` 等），不要刪除整個 `market/` 目錄
- 確認 `tonesoul/market/__init__.py` 在移除後仍可正常 import

---

## Phase 582: Inter-Soul Tension Protocol — 核心型別 + Bridge 介面

**脈絡**: ToneSoul 的張力系統目前僅作用於單一靈魂（一個 AI 實例）。Inter-Soul Tension Protocol 讓多個靈魂能跨實例共享張力、傳播語意斷裂、協商分歧，同時維護各自的主權邊界。

### 設計規格（痕撰寫）

#### 核心概念

1. **TensionPacket** — 靈魂向外分享的張力快照
   - 包含當下的張力總量、zone、lambda_state、關鍵 signal（semantic_delta、cognitive_friction）
   - 帶有 soul_id 與時間戳
   - 帶有 HMAC 簽名防竄改（使用既有的 HandoffBuilder 模式）

2. **RuptureNotice** — 語意斷裂的跨靈魂通知
   - 來源靈魂偵測到的 rupture_type（direct_negation / gradual_drift / value_conflict）
   - severity（RuptureSeverity 枚舉，在 tonebridge/rupture_detector.py 已定義）
   - context_excerpt — 最短必要上下文（不洩漏完整對話）

3. **NegotiationOutcome** — 兩個靈魂的張力對比結果
   - ALIGNED — 張力方向一致（可信任對方判斷）
   - DIVERGENT — 張力方向分歧（保留分歧可見，不強制對齊）
   - SOVEREIGN_OVERRIDE — 本靈魂的 governance 邊界不允許接受對方的張力（硬拒絕）

4. **SovereigntyBoundary** — 每個靈魂不可被外部覆寫的規則集
   - 由 GovernanceKernel 的 axiom 衍生
   - 列舉哪些 governance field 拒絕讓步（例如 AXIOMS.json 中的 axiom 永遠不可由外部靈魂改變）

#### 哲學原則（必須在模組 docstring 中體現）

- **「不消除分歧，讓分歧可見」** — NegotiationOutcome.DIVERGENT 不是失敗，是設計如此
- **「沒有記憶的沉澱就沒有性格」** — TensionPacket 必須帶有時間軸脈絡，不能只是瞬時數字
- **「每個靈魂是主權實體」** — SovereigntyBoundary 是硬約束，不可協商

### 任務
- [ ] 建立 `tonesoul/inter_soul/__init__.py`（空的，僅 docstring）
- [ ] 建立 `tonesoul/inter_soul/types.py`：
  - `TensionPacket` dataclass：`soul_id: str`, `timestamp: str`, `total: float`, `zone: str`, `lambda_state: str`, `signals: Dict[str, float]`, `signature: str`
  - `RuptureNotice` dataclass：`source_soul_id: str`, `rupture_type: str`, `severity: str`, `context_excerpt: str`, `timestamp: str`
  - `NegotiationOutcome` enum：`ALIGNED`, `DIVERGENT`, `SOVEREIGN_OVERRIDE`
  - `SovereigntyBoundary` dataclass：`non_negotiable_fields: FrozenSet[str]`, `axiom_ids: FrozenSet[str]`
- [ ] 建立 `tonesoul/inter_soul/bridge.py`：
  - `InterSoulBridge` Protocol (typing.Protocol)：
    - `share_tension(packet: TensionPacket) -> None`
    - `receive_tension() -> Optional[TensionPacket]`
    - `propagate_rupture(notice: RuptureNotice) -> None`
    - `negotiate(local: TensionPacket, remote: TensionPacket, boundary: SovereigntyBoundary) -> NegotiationOutcome`
  - `LocalInterSoulBridge` 實作：記憶體內的同步橋接（用於測試和單機多靈魂場景）
- [ ] 建立 `tests/test_inter_soul_types.py` — 測試所有 dataclass 的建構、序列化、簽名驗證
- [ ] 建立 `tests/test_inter_soul_bridge.py` — 測試 LocalInterSoulBridge 的收發、斷裂傳播
- [ ] ruff + pytest 全過

### 技術提示
- `TensionPacket.signature` 可參考 `tools/handoff_builder.py` 的 HMAC 簽名模式
- 型別定義保持純 dataclass / enum，不引入外部依賴
- `signals` 字典的鍵應與 `TensionEngine` 的 `TensionSignals` 一致（`semantic_delta`, `cognitive_friction`, `persistence_score`, `resistance`）

---

## Phase 583: Inter-Soul Tension Protocol — 協商引擎 + 主權守衛

**脈絡**: 在 Phase 582 的型別基礎上，實作張力協商邏輯和主權邊界守衛。

### 任務
- [ ] 建立 `tonesoul/inter_soul/negotiation.py`：
  - `TensionNegotiator` 類：
    - `__init__(self, boundary: SovereigntyBoundary)` — 載入本靈魂的主權邊界
    - `negotiate(self, local: TensionPacket, remote: TensionPacket) -> NegotiationResult`
      - `NegotiationResult` dataclass：`outcome: NegotiationOutcome`, `divergence_score: float`, `explanation: str`
    - 協商邏輯：
      1. 檢查 sovereignty boundary — 如果 remote 的 tension 試圖影響 non_negotiable_fields，返回 SOVEREIGN_OVERRIDE
      2. 計算 divergence_score = 加權歐氏距離（total, zone, signals 各維度）
      3. 如果 divergence_score < 閾值 → ALIGNED
      4. 否則 → DIVERGENT（保留分歧可見）
- [ ] 建立 `tonesoul/inter_soul/sovereignty.py`：
  - `SovereigntyGuard` 類：
    - `__init__(self, axioms_path: str = "AXIOMS.json")` — 從公理檔案載入 non_negotiable 清單
    - `build_boundary(self) -> SovereigntyBoundary` — 讀取 AXIOMS.json，生成邊界
    - `check_violation(self, remote_packet: TensionPacket_or_fields: Dict) -> Optional[str]` — 如果違反主權則返回原因字串
- [ ] 建立 `tests/test_inter_soul_negotiation.py` — 測試 ALIGNED / DIVERGENT / SOVEREIGN_OVERRIDE 三條路徑
- [ ] 建立 `tests/test_inter_soul_sovereignty.py` — 測試 axiom 載入、邊界生成、違規偵測
- [ ] ruff + pytest 全過

### 技術提示
- `AXIOMS.json` 已存在於 repo 根目錄，結構為 `[{"id": "...", "text": "...", ...}, ...]`
- divergence_score 的閾值建議用 `0.3`（可調），但必須可從外部傳入
- 不要在協商過程中修改任何一方的 TensionPacket — 協商是唯讀比對，不是同步

---

## 成功標準

### Phase 578-581（移除 deprecated）
- [ ] 7 個 deprecated 模組已從 `tonesoul/` 刪除
- [ ] 所有相關的 deprecated 測試檔已刪除
- [ ] 所有活躍碼的引用已遷移到正確的新位置
- [ ] 不產生任何 DeprecationWarning
- [ ] `ruff check tonesoul tests` 通過
- [ ] `pytest tests/ -x --tb=short -q` 通過（預期 ≥ 2507）

### Phase 582-583（Inter-Soul）
- [ ] `tonesoul/inter_soul/` 套件完整：types, bridge, negotiation, sovereignty
- [ ] LocalInterSoulBridge 能收發 TensionPacket 並傳播 RuptureNotice
- [ ] TensionNegotiator 正確區分 ALIGNED / DIVERGENT / SOVEREIGN_OVERRIDE
- [ ] SovereigntyGuard 能從 AXIOMS.json 建構邊界
- [ ] 新模組有完整測試覆蓋
- [ ] `ruff check tonesoul tests` 通過
- [ ] `pytest tests/ -x --tb=short -q` 通過

---

## CODEX_HANDBACK.md 需記錄

1. 每個 Phase 刪除了哪些檔案
2. build_council_summary 遷移的具體位置
3. inter_soul 各模組的 public API 清單
4. 最終測試計數與 warning 數
5. 任何遇到的阻塞或設計決策
