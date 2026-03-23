# Spec / Law 一頁式對照

> Purpose: crosswalk the implementation-facing `spec/` lane against the governance-facing `law/` lane in one retrieval surface.
> Last Updated: 2026-03-23

> 目的：降低 `spec/`（可實作規格）與 `law/`（治理規範）重複敘述，建立單一對照入口。

## 分工原則

- `spec/`：描述「要做什麼、輸入輸出、契約與驗證方式」。
- `law/`：描述「為何這樣做、治理約束、風險邊界與審計原則」。
- 兩者關係：`spec` 可實作，`law` 可問責，最終在測試與 CI 匯流。

## 對照表

| 主題 | `spec/` 代表文件 | `law/` 代表文件 | 實作入口 |
| --- | --- | --- | --- |
| Council 審議契約 | `spec/council_spec.md` | `law/engineering/law_v0.2_2026-02-09.md` | `tonesoul/council/` |
| 預輸出治理 | `spec/pre_output_council_spec.md` | `law/engineering/codex_action_law_10.md` | `tonesoul/pre_output_council.py` |
| 記憶與責任鏈 | `spec/memory_structure_spec.md` | `law/docs/LAW_HIERARCHY.md` | `tonesoul/memory/`, `memory/` |
| 語義控制與張力 | `spec/wfgy_semantic_control_spec.md` | `law/engineering` 系列條文 | `tonesoul/semantic_control.py` |
| 工具與外部來源治理 | `spec/tools/*.md` | `law/EXAMPLES/`、`law/docs/` | `scripts/verify_external_source_registry.py` |

## 變更準則

1. 新增 `spec` 前，先確認是否已有對應 `law` 約束；若無，補一條治理說明。  
2. 新增 `law` 前，先確認是否能映射到至少一個可驗證 `spec` 或測試。  
3. 任何跨域變更（`spec + law + runtime`）至少附一個 CI 證據（測試或檢查輸出）。

## 快速檢查清單

- 這個需求有 `spec` 契約嗎？
- 這個需求有 `law` 邊界嗎？
- 有對應到哪個 runtime 模組？
- 有哪個測試或腳本能證明它正在被執行？
