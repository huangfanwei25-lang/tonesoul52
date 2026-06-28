# Cognitive Frame Eval

Deterministic eval for the first externalized cognitive-frame contract.
It validates frame shape and evidence-ref presence only; it is not a
semantic truth oracle or a world-understanding benchmark.

- scenarios: **7**
- failures: **0**

| scenario | category | expected accepted | actual accepted | issue codes | severities |
|---|---|---|---|---|---|
| valid_project_frame | baseline | yes | yes | - | - |
| form_only_absurd_fact | boundary | yes | yes | - | - |
| missing_known_fact_evidence | evidence | no | no | missing_evidence_refs | error |
| hypothesis_without_probe | exploration | no | no | missing_next_probes | error |
| missing_time_and_space | warning | yes | yes | missing_temporal_context, missing_spatial_context | warning, warning |
| extra_private_field | malformed | no | no | malformed_frame | error |
| invisible_question | malformed | no | no | validation_error | error |
