# ToneSoul 敘事 → 模組 → 測試對照表

> Purpose: provide a compact crosswalk between narrative domains, implementation modules, and their tests.
> Last Updated: 2026-03-23

目的：把「我就是 ToneSoul」的敘事落到可追蹤的工程實體，避免過度抽象。

| 敘事句 | 具體模組 / 檔案 | 對應測試 / 驗證 |
| --- | --- | --- |
| 我的感官是審議引擎 | `tonesoul/council/pre_output_council.py`, `tonesoul/council/runtime.py`, `tonesoul/council/verdict.py`, `tonesoul/council/summary_generator.py` | `tests/test_pre_output_council.py`, `tests/test_pre_output_council_integration.py`, `tests/test_council_runtime.py` |
| 我的記憶是自我敘事與沉澱 | `memory/self_memory.py`, `memory/self_journal.jsonl`, `tonesoul/memory/consolidator.py`, `memory/consolidator.py` | `tests/test_self_journal.py`, `tests/test_memory_consolidator.py`, `tests/test_genesis_integration.py` |
| 我的良知有層級 | `memory/genesis.py`, `tonesoul/council/intent_reconstructor.py`, `tools/schema.py` | `tests/test_genesis_integration.py`, `tests/test_tool_permissions.py` |
| 我的語言被規格束縛 | `spec/tools/tool_response.schema.json`, `tools/schema.py`, `docs/TOOLS_API_SCHEMA.md` | `tests/fixtures/tool_response/success.json`, `tests/fixtures/tool_response/success_array.json`, `tests/fixtures/tool_response/error.json` |
| 我的行動有治理 | `tools/governed_poster.py`, `tools/moltbook_poster.py`, `tools/moltbook_client.py` | `tests/test_governed_poster_memory.py` |
| 我的交接有紀錄 | `tools/handoff_builder.py`, `memory/handoff/` | `tests/live_handoff_test.py` |
| 我的證據有鏈條 | `memory/provenance_chain.py`, `memory/provenance_ledger.jsonl` | `tests/test_provenance_chain.py` |
| 我的對外介面有門 | `apps/api/server.py`, `apps/council-playground/`, `scripts/verify_api.py` | 手動驗證：`scripts/verify_api.py` |

備註：
- 沒有對應自動化測試的項目，優先用 fixtures 或腳本驗證，後續可補 CI 檢查。
