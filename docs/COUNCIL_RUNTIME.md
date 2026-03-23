# Council Runtime 整合設計

> Purpose: describe the current council runtime facade, authoritative entrypoints, and deprecated migration boundaries.
> Last Updated: 2026-03-23

本文件定義 Council 的統一入口（Facade）與角色權重整合策略，目標是將現有的
`PreOutputCouncil` 與 `role_council.py` 收斂為單一 API。

**目標**

- 單一入口：所有審議呼叫都進 `CouncilRuntime.deliberate(...)`。
- 角色權重：保留 `role_council.py` 的治理角色/權重邏輯。
- 不破壞：先保持 `PreOutputCouncil` 的輸出語意，漸進整合。

**範圍**

- 新增 `tonesoul/council/runtime.py` 作為 Facade。
- 舊入口（`council_adapter.py`、`simulate_council.py`）標記 deprecated，逐步遷移。
- 不在本階段改動 `PreOutputCouncil` 內部邏輯。

**現況盤點（入口與呼叫點）**

- Council 核心：`tonesoul/council/pre_output_council.py`
- 角色權重：`tonesoul/role_council.py`
- 路由整合：`tonesoul/frame_router.py`
- 既有入口：`tonesoul/council_adapter.py`、`tonesoul/simulate_council.py`
- 主要呼叫點：`tonesoul/unified_pipeline.py`、`tonesoul/unified_controller.py`
- 工具側簡化 Council：`tools/governed_poster.py`

**核心介面（草案）**

```python
@dataclass
class CouncilRequest:
    draft_output: str
    context: dict
    user_intent: Optional[str] = None
    perspectives: Optional[Union[IPerspective, List[Union[IPerspective, PerspectiveType, str]], Dict[Union[PerspectiveType, str], Dict[str, Any]], PerspectiveType, str]] = None
    perspective_config: Optional[Dict[Union[PerspectiveType, str], Dict[str, Any]]] = None
    coherence_threshold: float = 0.6
    block_threshold: float = 0.3
    selected_frames: Optional[List[Dict[str, object]]] = None
    role_summary: Optional[Dict[str, object]] = None
    role_catalog: Optional[Dict[str, object]] = None

class CouncilRuntime:
    def deliberate(self, request: CouncilRequest) -> CouncilVerdict:
        """統一入口，內部整合 PreOutputCouncil + RoleCouncil 權重"""
```

**整合流程**

1. **角色權重評估**  
   若提供 `selected_frames` 或 `role_summary` / `role_catalog`，先計算
   `build_council_summary(...)` 得到 `decision_status` 與 `weighted_score`。

2. **閾值調整**  
   以角色權重結果調整 `PreOutputCouncil` 的 `coherence_threshold` 與
   `block_threshold`，避免在結果產生後再強行覆寫（會影響記憶記錄一致性）。

   建議規則（可後續調整）：
   - `decision_status == "block"`  
     `block_threshold = max(block_threshold, 0.5)`  
     `coherence_threshold = max(coherence_threshold, 0.7)`
   - `decision_status == "attention"`  
     `block_threshold = max(block_threshold, 0.4)`  
     `coherence_threshold = max(coherence_threshold, 0.65)`
   - `decision_status == "pass"`  
     不調整

3. **Council 審議**  
   使用調整後的閾值呼叫 `PreOutputCouncil.validate(...)`。

4. **結果附帶治理脈絡**  
   將 `role_council` 結果掛在 `CouncilVerdict.transcript` 中，便於審計與回溯。

**遷移策略**

- 優先將新呼叫導向 `CouncilRuntime.deliberate`。
- 既有入口加上 deprecation 註記，避免新功能再依賴舊 API。

**測試建議**

- 單元測試：`CouncilRuntime` 在三種 `decision_status` 下是否調整閾值。
- 整合測試：原本 `PreOutputCouncil` 的行為在 `decision_status == "pass"` 時不變。
- 回歸測試：`role_council` 仍可單獨產生一致的 `council_summary`。
