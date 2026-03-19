from __future__ import annotations

import importlib
import sys
import warnings

import pytest


def _import_with_warnings(module_name: str):
    sys.modules.pop(module_name, None)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        module = importlib.import_module(module_name)
    dep_warnings = [item for item in caught if issubclass(item.category, DeprecationWarning)]
    return module, dep_warnings


@pytest.mark.parametrize(
    ("module_name", "expected_name"),
    [
        ("tonesoul.market.forecaster", "MarketDreamEngine"),
        ("tonesoul.market.gold_detector", "GoldDetector"),
    ],
)
def test_import_emits_deprecation_warning(module_name: str, expected_name: str) -> None:
    _, dep_warnings = _import_with_warnings(module_name)

    assert dep_warnings
    assert "deprecated" in str(dep_warnings[0].message).lower()


@pytest.mark.parametrize(
    ("module_name", "expected_name"),
    [
        ("tonesoul.market.forecaster", "MarketDreamEngine"),
        ("tonesoul.market.gold_detector", "GoldDetector"),
    ],
)
def test_module_still_importable(module_name: str, expected_name: str) -> None:
    module, _ = _import_with_warnings(module_name)

    assert getattr(module, expected_name)
