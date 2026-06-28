# Cognitive Frame Public Artifact Eval

Deterministic eval of CognitiveFrame fixtures grounded in public repo artifacts.
This validates frame shape and public `file:` evidence-ref existence only; it
does not prove semantic evidence sufficiency or model understanding.

- cases: **4**
- accepted frames: **3/4**
- warning-bearing frames: **1**
- public artifact refs checked: **7**
- failures: **0**

| case | expected | actual | refs | missing refs | forbidden refs | issue codes | severities | ok |
|---|---|---|---:|---|---|---|---|---|
| externalized_cognition_anchor | yes | yes | 2 | - | - | - | - | yes |
| responsibility_runtime_frame | yes | yes | 2 | - | - | - | - | yes |
| memory_output_surface_frame | yes | yes | 2 | - | - | - | - | yes |
| rejected_unsupported_fact_frame | no | no | 1 | - | - | missing_temporal_context, missing_spatial_context, missing_evidence_refs | warning, warning, error | yes |
