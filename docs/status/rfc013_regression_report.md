# RFC-013 Regression Report

- generated_at: 2026-03-02
- scope: RFC-013 targeted regression + full `tests/` smoke with first-failure stop

## Commands and Results

1. `python -m pytest tests/test_nonlinear_predictor.py tests/test_work_classifier.py tests/test_variance_compressor.py tests/test_tension_engine.py -v --tb=short`
   - result: `73 passed`
   - status: pass

2. `python -m pytest tests/test_genesis_integration.py -v --tb=short`
   - result: `7 passed`
   - status: pass

3. `python -m pytest tests/ --timeout=30 -x --tb=short -q`
   - result: argument parsing failed (`unrecognized arguments: --timeout=30`)
   - status: invalid command in current environment (`pytest-timeout` option unavailable)

4. rerun: `python -m pytest tests/ -x --tb=short -q`
   - collected: `1085`
   - executed before stop: `506`
   - result: `505 passed, 1 failed, 1 warning`
   - first failure: `tests/test_pipeline_compute_gate.py::test_pipeline_rate_limit_free_tier`

5. focused confirm: `python -m pytest tests/test_pipeline_compute_gate.py::test_pipeline_rate_limit_free_tier -vv --tb=short`
   - result: `1 failed`
   - assertion: expected route `block_rate_limit`, actual `route_single_cloud`
   - location: `tests/test_pipeline_compute_gate.py:79`

## Assessment

- RFC-013 direct surfaces are green in this run (`73 + 7` targeted tests all pass).
- Full-suite remains non-green due to one compute-gate routing assertion mismatch.
- Inference: this blocker appears outside RFC-013 module set (`nonlinear_predictor`, `work_classifier`, `variance_compressor`) and should be tracked separately as compute-gate behavior drift.
