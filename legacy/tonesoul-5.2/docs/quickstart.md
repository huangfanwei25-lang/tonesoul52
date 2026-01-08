# ToneSoul 5.2 Quickstart

Goal: run the minimal end-to-end YSS pipeline and inspect artifacts.

## 1) Install

```bash
pip install -e .
```

## 2) Healthcheck

```bash
python -m tonesoul52.run_healthcheck
```

## 3) Run the pipeline (minimal)

```bash
python -m tonesoul52.run_yss_pipeline --task "Hello World" --objective "Test the pipeline"
```

Outputs (example paths):
- `5.2/run/execution/<run_id>/context.yaml`
- `5.2/run/execution/<run_id>/frame_plan.json`
- `5.2/run/execution/<run_id>/constraints.md`
- `5.2/run/execution/<run_id>/execution_report.md`
- `5.2/run/execution/<run_id>/gate_report.json`
- `5.2/run/execution/<run_id>/audit_request.json`

## 4) Validate gates for a run

```bash
python -m tonesoul52.run_yss_gates --run-dir 5.2/run/execution/<run_id>
```

## 5) Optional: YSTM demo visuals

```bash
python -m tonesoul52.run_ystm_demo
```

Outputs:
- `5.2/reports/ystm_demo/terrain.html`
- `5.2/reports/ystm_demo/terrain_p2.html`

## Next steps

- `5.2/reports/execution_architecture_v0.4.md`
- `5.2/reports/implementation_roadmap.md`
- `5.2/reports/trace_levels.md`
