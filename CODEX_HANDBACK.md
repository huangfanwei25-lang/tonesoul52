# Codex 交回報告

**Phase**: 582-583 Inter-Soul Tension Protocol
**完成日期**: 2026-03-20
**狀態**: 已完成 / 待痕審核

## 修改摘要
- 新增 `tonesoul/inter_soul/` 套件，落地四個核心型別、bridge、negotiation、sovereignty。
- `TensionPacket` 具備 HMAC-SHA256 簽章與驗章，序列化規則對齊 `tools/handoff_builder.py` 的 canonical JSON 思路。
- `LocalInterSoulBridge` 採 in-memory append-only history，讓張力交換和 rupture 通知可追蹤，不會在接收後被抹平。
- `TensionNegotiator` 實作三種結果：
  `ALIGNED`
  `DIVERGENT`
  `SOVEREIGN_OVERRIDE`
- `SovereigntyGuard` 可從 repo 版 `AXIOMS.json` 與 list-style axioms 兩種格式建構主權邊界。
- 新增 4 個測試檔，共 17 個測試，覆蓋型別、bridge、協商與主權守衛。

## Inter-Soul Public API
- `tonesoul.inter_soul.TensionPacket`
- `tonesoul.inter_soul.RuptureNotice`
- `tonesoul.inter_soul.NegotiationOutcome`
- `tonesoul.inter_soul.SovereigntyBoundary`
- `tonesoul.inter_soul.InterSoulBridge`
- `tonesoul.inter_soul.LocalInterSoulBridge`
- `tonesoul.inter_soul.NegotiationResult`
- `tonesoul.inter_soul.TensionNegotiator`
- `tonesoul.inter_soul.SovereigntyGuard`

## 主權映射
- Axiom `3` (`Governance Gate (POAV)`, P0) -> `zone`
- Axiom `6` (`User Sovereignty Constraint`, P0) -> `lambda_state`

目前 `SovereigntyGuard.build_boundary()` 只會把有明確 field 映射的 P0 axiom 納入 `SovereigntyBoundary`。這樣可以避免憑空發明 governance field，同時保留後續擴充空間。

## 哲學原則落點
- 不消除分歧：
  `NegotiationOutcome.DIVERGENT` 被當成正常結果，不是失敗分支。
- 記憶沉澱：
  `LocalInterSoulBridge` 保留 `tension_history` / `rupture_history`，不是只做一次性傳遞。
- 主權實體：
  `SovereigntyBoundary` 是硬約束；protected field 有差異時直接回 `SOVEREIGN_OVERRIDE`。

## 測試結果
- `ruff check tonesoul/inter_soul tests/test_inter_soul_types.py tests/test_inter_soul_bridge.py tests/test_inter_soul_negotiation.py tests/test_inter_soul_sovereignty.py` -> passed
- `pytest tests/test_inter_soul_types.py tests/test_inter_soul_bridge.py tests/test_inter_soul_negotiation.py tests/test_inter_soul_sovereignty.py -q` -> 17 passed, 1 warning
- `ruff check tonesoul tests` -> passed
- `pytest tests/ -x --tb=short -q` -> 2572 passed, 9 warnings

## 風險 / 注意事項
- `SovereigntyGuard.check_violation()` 是 payload-field 檢查器；若直接把完整 packet 丟進去，它會把 packet 內已有的 protected field 視為觸碰主權欄位。現階段 `TensionNegotiator` 是先算差異欄位再判斷，所以行為正確。
- 目前只映射了 `zone` / `lambda_state` 兩個主權欄位。若未來 AXIOMS 增加更細的治理欄位，需要同步擴充 `_DEFAULT_FIELD_MAP`。
- `signals` 目前限制為 `Dict[str, float]`，所以像 `resistance` 這類複合結構在 Inter-Soul 層應先壓平成數值再交換。

## 重要檔案修改
- `tonesoul/inter_soul/types.py`
  目的：定義 signed tension packet、rupture notice、negotiation outcome、sovereignty boundary。
- `tonesoul/inter_soul/bridge.py`
  目的：定義 bridge protocol 與 local append-only bridge。
- `tonesoul/inter_soul/negotiation.py`, `tonesoul/inter_soul/sovereignty.py`
  目的：定義協商引擎、主權守衛與 AXIOMS 對應規則。
