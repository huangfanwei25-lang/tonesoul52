from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "ask_my_brain.py"
    spec = importlib.util.spec_from_file_location("ask_my_brain_script", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_script_tension_replay_validation_passes() -> None:
    module = _load_module()
    assert module._run_tension_replay_validation() is True


def test_script_friction_summary_includes_wave_score_delta() -> None:
    module = _load_module()
    friction = module._compute_friction_summary(
        metadata={
            "tension": 0.2,
            "wave_score": 0.9,
            "wave": {
                "uncertainty_shift": 0.1,
                "divergence_shift": 0.1,
                "risk_shift": 0.1,
                "revision_shift": 0.1,
            },
        },
        query_tension=0.9,
        query_wave={
            "uncertainty_shift": 0.9,
            "divergence_shift": 0.9,
            "risk_shift": 0.9,
            "revision_shift": 0.9,
        },
    )
    assert friction is not None
    assert friction["wave_score_delta"] == 0.0
