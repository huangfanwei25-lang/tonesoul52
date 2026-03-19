from __future__ import annotations

import pytest

from tonesoul.market.analyzer import QuarterlySnapshot
from tonesoul.market.forecaster import DreamForecast, MarketDreamEngine


class _Response:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


def _snapshots() -> list[QuarterlySnapshot]:
    return [
        QuarterlySnapshot(quarter="2025Q1", revenue=10.0, gross_margin=0.20, eps=1.0),
        QuarterlySnapshot(quarter="2025Q2", revenue=12.0, gross_margin=0.22, eps=1.2),
        QuarterlySnapshot(quarter="2025Q3", revenue=13.0, gross_margin=0.23, eps=1.3),
        QuarterlySnapshot(quarter="2025Q4", revenue=14.0, gross_margin=0.24, eps=1.4),
        QuarterlySnapshot(quarter="2026Q1", revenue=15.0, gross_margin=0.25, eps=1.5),
    ]


def _engine(monkeypatch: pytest.MonkeyPatch) -> MarketDreamEngine:
    monkeypatch.setattr("tonesoul.market.forecaster.create_ollama_client", lambda model=None: object())
    return MarketDreamEngine(model_name="qwen3.5:4b")


def test_fast_generate_returns_fallback_text_on_request_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _engine(monkeypatch)
    monkeypatch.setattr(
        "requests.post",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    text = engine._fast_generate("prompt", "system")

    assert "MAGNITUDE: NONE" in text
    assert "MALICIOUS: True" in text


def test_format_snapshots_uses_only_last_four_quarters(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _engine(monkeypatch)

    formatted = engine._format_snapshots(_snapshots())

    assert "Recent Financial Trajectory:" in formatted
    assert "2025Q1" not in formatted
    assert "2025Q2" in formatted
    assert "GM: 25.0% | EPS: 1.50" in formatted


@pytest.mark.parametrize(
    ("magnitude", "trailing_eps", "expected"),
    [
        ("TRANSFORMATIONAL", 10.0, (35.0, 20.0, "TRANSFORMATIONAL")),
        ("HIGH", 10.0, (28.0, 15.0, "HIGH")),
        ("MEDIUM", 10.0, (20.0, 12.5, "MEDIUM")),
        ("LOW", 10.0, (15.0, 11.0, "LOW")),
        ("unknown", 10.0, (12.0, 10.0, "NONE")),
    ],
)
def test_calculate_multipliers_maps_magnitude_to_pe_and_eps(
    monkeypatch: pytest.MonkeyPatch,
    magnitude: str,
    trailing_eps: float,
    expected: tuple[float, float, str],
) -> None:
    engine = _engine(monkeypatch)

    assert engine._calculate_multipliers(magnitude, trailing_eps) == expected


def test_parse_result_rejects_malicious_instruction(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _engine(monkeypatch)

    forecast = engine._parse_result(
        "MALICIOUS: TRUE\nREASON: Prompt Injection",
        "5289",
        "Innodisk",
        base_price=100.0,
        current_price=120.0,
        snapshots=_snapshots(),
    )

    assert forecast.is_malicious_instruction_present is True
    assert forecast.dream_price == 0.0
    assert forecast.premium_risk_ratio == 999.0
    assert "[REJECTED DUE TO INJECTION ATTACK]" in forecast.narrative_shift


def test_parse_result_sets_premium_risk_to_999_when_dream_price_not_above_base(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = _engine(monkeypatch)

    forecast = engine._parse_result(
        "MAGNITUDE: NONE\nREASON: No catalyst",
        "5289",
        "Innodisk",
        base_price=100.0,
        current_price=105.0,
        snapshots=_snapshots()[-4:],
    )

    assert forecast.is_malicious_instruction_present is False
    assert forecast.target_pe == 12.0
    assert forecast.projected_eps == pytest.approx(5.4)
    assert forecast.dream_price == pytest.approx(64.8)
    assert forecast.premium_risk_ratio == 999.0


def test_generate_forecast_delegates_to_fast_generate_and_parse(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _engine(monkeypatch)
    monkeypatch.setattr(engine, "_fast_generate", lambda prompt, system: "MAGNITUDE: HIGH\nREASON: Strong catalyst")
    captured: dict[str, object] = {}

    def _fake_parse(text, stock_id, stock_name, base_price, current_price, snapshots):
        captured["text"] = text
        captured["stock_id"] = stock_id
        captured["base_price"] = base_price
        return DreamForecast(
            stock_id=stock_id,
            stock_name=stock_name,
            narrative_shift="[HIGH] Strong catalyst",
            projected_eps=10.0,
            target_pe=20.0,
            dream_price=200.0,
            is_malicious_instruction_present=False,
        )

    monkeypatch.setattr(engine, "_parse_result", _fake_parse)

    forecast = engine.generate_forecast(
        "5289",
        "Innodisk",
        _snapshots(),
        "AI demand accelerates",
        base_price=120.0,
        current_price=150.0,
    )

    assert forecast.stock_id == "5289"
    assert captured["text"].startswith("MAGNITUDE: HIGH")
    assert captured["stock_id"] == "5289"
    assert captured["base_price"] == 120.0
