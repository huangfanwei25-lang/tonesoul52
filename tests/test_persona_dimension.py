from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest
import yaml

from tonesoul.drift_monitor import DriftAlert, DriftMonitor
from tonesoul.persona_dimension import (
    BigFive,
    PersonaDimension,
    PersonaVector,
    VectorCalculator,
    _context_label,
    _count_hits,
    _extract_goal_weights,
    _load_context,
    _vector_distance,
    extract_big_five,
    load_persona,
    main,
)


def _write_json(path: Path, payload: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _write_yaml(path: Path, payload: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")
    return path


def _persona_payload() -> dict[str, object]:
    return {
        "id": "persona-001",
        "home_vector": {"deltaT": 0.5, "deltaS": 0.6, "deltaR": 0.7},
        "tolerance": {"deltaT": 0.3, "deltaS": 0.3, "deltaR": 0.3},
        "communication": {"tone": "careful"},
    }


def test_big_five_to_delta_vector_formula() -> None:
    big_five = BigFive(
        openness=0.7,
        conscientiousness=0.8,
        extraversion=0.6,
        agreeableness=0.4,
        neuroticism=0.2,
    )

    assert big_five.to_delta_vector() == {"deltaT": 0.4, "deltaS": 0.5, "deltaR": 0.8}


def test_extract_big_five_returns_none_without_payload() -> None:
    assert extract_big_five({"id": "persona"}) is None


def test_extract_big_five_parses_payload() -> None:
    result = extract_big_five(
        {
            "big_five": {
                "openness": 0.7,
                "conscientiousness": 0.8,
                "extraversion": 0.4,
                "agreeableness": 0.9,
                "neuroticism": 0.1,
            }
        }
    )

    assert result is not None
    assert result.as_dict()["agreeableness"] == 0.9


def test_persona_vector_as_dict_rounds_values() -> None:
    vector = PersonaVector(deltaT=0.12345, deltaS=0.98765, deltaR=0.55555)

    assert vector.as_dict()["deltaT"] == 0.123
    assert vector.as_dict()["deltaS"] == 0.988
    assert vector.as_dict()["deltaR"] == 0.556


def test_vector_calculator_compute_uses_markers_and_context() -> None:
    calculator = VectorCalculator()

    vector = calculator.compute(
        "Urgent! Please verify and ensure safety.",
        context={
            "context": {"task": "Audit", "objective": "Stay safe"},
            "goal_weights": {"accuracy": 0.7, "care": 0.3},
        },
    )

    assert vector.deltaT > 0.3
    assert vector.deltaS > 0.5
    assert vector.deltaR > 0.5
    assert vector.goal_weights == [0.7, 0.3]
    assert vector.context == "Audit Stay safe"
    assert vector.timestamp


def test_vector_calculator_empty_output_returns_baseline() -> None:
    vector = VectorCalculator().compute("")

    assert vector.deltaT == pytest.approx(0.3)
    assert vector.deltaS == pytest.approx(0.5)
    assert vector.deltaR == pytest.approx(0.5)
    assert vector.goal_weights == []
    assert vector.context == ""


def test_persona_dimension_evaluate_valid_result_structure() -> None:
    evaluator = PersonaDimension(_persona_payload())

    result = evaluator.evaluate("Please verify and ensure safety.")

    assert result["persona_id"] == "persona-001"
    assert result["valid"] is True
    assert result["reasons"] == []
    assert set(result["vector"]) >= {"deltaT", "deltaS", "deltaR", "timestamp", "context"}
    assert result["distance"]["max"] >= 0.0


def test_persona_dimension_evaluate_uses_adaptive_tolerance() -> None:
    payload = _persona_payload()
    payload["tolerance"] = {"deltaT": 0.4, "deltaS": 0.4, "deltaR": 0.4}
    evaluator = PersonaDimension(payload)

    result = evaluator.evaluate(
        "Urgent!!! warning risk danger",
        context={"delta_sigma": 2.0},
    )

    assert result["valid"] is False
    assert "deltaT_out_of_range" in result["reasons"]
    assert result["adaptive"]["factor"] == pytest.approx(0.5)
    assert result["adaptive"]["effective_tolerance"]["deltaT"] == pytest.approx(0.2)


def test_persona_dimension_process_without_intercept_preserves_output_and_writes_ledger(
    tmp_path: Path,
) -> None:
    ledger_path = tmp_path / "persona.jsonl"
    evaluator = PersonaDimension(_persona_payload())
    output = "Please verify and ensure safety."

    new_output, result = evaluator.process(output, ledger_path=str(ledger_path), intercept=False)

    assert new_output == output
    assert result["corrected"] is False
    lines = ledger_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["persona_id"] == "persona-001"


def test_persona_dimension_process_with_intercept_applies_corrections() -> None:
    payload = _persona_payload()
    payload["home_vector"] = {"deltaT": 0.1, "deltaS": 0.9, "deltaR": 0.9}
    payload["tolerance"] = {"deltaT": 0.05, "deltaS": 0.05, "deltaR": 0.05}
    evaluator = PersonaDimension(payload)
    original = "WARNING!! lol"

    corrected_output, result = evaluator.process(original, intercept=True)

    assert corrected_output != original
    assert result["corrected"] is True
    assert result["original_output"] == original
    assert result["correction_info"]["corrections"]
    assert (
        result["correction_info"]["corrected_length"]
        >= result["correction_info"]["original_length"]
    )


def test_vector_distance_returns_summary() -> None:
    distance = _vector_distance(
        {"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5},
        PersonaVector(deltaT=0.8, deltaS=0.3, deltaR=0.4),
    )

    assert distance == {
        "deltaT": 0.3,
        "deltaS": 0.2,
        "deltaR": 0.1,
        "mean": 0.2,
        "max": 0.3,
    }


def test_vector_distance_returns_none_without_numeric_home() -> None:
    assert (
        _vector_distance({"deltaT": "x"}, PersonaVector(deltaT=0.8, deltaS=0.3, deltaR=0.4)) is None
    )


def test_count_hits_counts_duplicate_occurrences() -> None:
    assert _count_hits("verify verify test", ["verify", "test"]) == 3


def test_context_label_joins_task_and_objective() -> None:
    assert _context_label({"context": {"task": "Audit", "objective": "Preserve evidence"}}) == (
        "Audit Preserve evidence"
    )


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ({"goal_weights": [0.7, 0.2, "skip"]}, [0.7, 0.2]),
        ({"goal_weights": {"accuracy": 0.6, "care": 0.4}}, [0.6, 0.4]),
        ({}, []),
    ],
)
def test_extract_goal_weights_variants(
    payload: dict[str, object],
    expected: list[float],
) -> None:
    assert _extract_goal_weights(payload) == expected


@pytest.mark.parametrize("suffix", [".json", ".yaml"])
def test_load_context_supports_json_and_yaml(tmp_path: Path, suffix: str) -> None:
    path = tmp_path / f"context{suffix}"
    payload = {"task": "Audit"}
    if suffix == ".json":
        _write_json(path, payload)
    else:
        _write_yaml(path, payload)

    assert _load_context(str(path)) == payload


def test_load_context_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        _load_context(str(tmp_path / "missing.json"))


def test_load_persona_requires_mapping(tmp_path: Path) -> None:
    path = _write_yaml(tmp_path / "persona.yaml", ["not", "a", "mapping"])

    with pytest.raises(ValueError):
        load_persona(str(path))


def test_load_persona_reads_yaml_mapping(tmp_path: Path) -> None:
    path = _write_yaml(tmp_path / "persona.yaml", _persona_payload())

    payload = load_persona(str(path))

    assert payload["id"] == "persona-001"


def test_persona_dimension_snapshot_can_feed_drift_monitor() -> None:
    evaluator = PersonaDimension(_persona_payload())
    monitor = DriftMonitor(theta_warning=0.0, theta_crisis=1.0)
    result = evaluator.evaluate("Please verify and ensure safety.")

    snap = monitor.observe({key: result["vector"][key] for key in ("deltaT", "deltaS", "deltaR")})

    assert snap.step == 1
    assert snap.alert in {DriftAlert.NONE, DriftAlert.WARNING}
    assert monitor.summary()["steps"] == 1


def test_main_writes_json_output(tmp_path: Path, monkeypatch) -> None:
    persona_path = _write_yaml(tmp_path / "persona.yaml", _persona_payload())
    output_path = tmp_path / "result.json"
    args = argparse.Namespace(
        persona=str(persona_path),
        text="Please verify and ensure safety.",
        input=None,
        context=None,
        ledger=None,
        output=str(output_path),
    )

    class _Parser:
        def parse_args(self) -> argparse.Namespace:
            return args

    monkeypatch.setattr("tonesoul.persona_dimension.build_arg_parser", lambda: _Parser())

    result = main()

    assert output_path.exists()
    assert json.loads(output_path.read_text(encoding="utf-8"))["persona_id"] == "persona-001"
    assert result["persona_id"] == "persona-001"
