# Repo Healthcheck Latest

- generated_at: 2026-02-14T10:42:51Z
- overall_ok: false

| check | status | exit | duration_s | command |
| --- | --- | ---: | ---: | --- |
| python_lint | FAIL | 1 | 0.13 | `python -m ruff check tonesoul tests scripts` |
| python_format | FAIL | 1 | 3.61 | `python -m black --check tonesoul tests scripts` |
| python_tests | PASS | 0 | 85.11 | `python -m pytest tests -q` |
| web_lint | PASS | 0 | 5.80 | `npm --prefix apps/web run lint` |
| web_test | PASS | 0 | 1.94 | `npm --prefix apps/web run test` |
| git_hygiene | PASS | 0 | 1.67 | `python scripts/verify_git_hygiene.py` |
| persona_swarm | PASS | 0 | 0.26 | `python scripts/run_persona_swarm_framework.py --strict` |
| external_source_registry | PASS | 0 | 0.11 | `python scripts/verify_external_source_registry.py --strict` |
| audit_7d | PASS | 0 | 182.45 | `python scripts/verify_7d.py` |

## Failures
- `python_lint`:   latest_entry,
30 | |     load_index,
31 | |     update_index,
32 | |     write_tsr_metrics,
33 | | )
34 | | from .yss_gates import (
35 | |     GateResult,
36 | |     build_gate_report,
37 | |     build_test_gate,
38 | |     constraint_consistency,
39 | |     context_lint,
40 | |     dcs_gate,
41 | |     escalation_gate,
42 | |     evidence_completeness,
43 | |     guardian_gate,
44 | |     intent_achievement_gate,
45 | |     mercy_gate,
46 | |     p0_gate,
47 | |     poav_gate,
48 | |     role_alignment,
49 | |     router_replay,
50 | |     seed_schema_gate,
51 | |     tech_trace_gate,
52 | |     update_execution_report,
53 | | )
54 | | from .ystm.demo import DEFAULT_SEGMENTS, DemoConfig, write_demo_outputs
55 | | from .ystm.energy import EnergyConfig
56 | | from .ystm.ingest import load_segments, normalize_segments
57 | | from .ystm.representation import EmbeddingConfig
58 | | from .ystm.terrain import TerrainConfig
59 | | from .yss_unified_adapter import (
60 | |     build_multi_persona_eval_snapshot,
61 | |     build_unified_seed,
62 | |     write_multi_persona_eval_snapshot,
63 | | )
   | |_^
   |
help: Organize imports

Found 3 errors.
[*] 3 fixable with the `--fix` option.
- `python_format`: would reformat C:\Users\user\Desktop\倉庫\tests\test_custom_role_council.py
would reformat C:\Users\user\Desktop\倉庫\tonesoul\yss_unified_adapter.py
would reformat C:\Users\user\Desktop\倉庫\tonesoul\council\perspective_factory.py
would reformat C:\Users\user\Desktop\倉庫\tonesoul\unified_core.py
would reformat C:\Users\user\Desktop\倉庫\tonesoul\yss_pipeline.py
would reformat C:\Users\user\Desktop\倉庫\tonesoul\unified_pipeline.py

Oh no! 💥 💔 💥
6 files would be reformatted, 339 files would be left unchanged.
