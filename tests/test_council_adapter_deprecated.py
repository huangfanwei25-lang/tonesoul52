from __future__ import annotations

import importlib
import sys
import warnings


def _import_with_warnings(module_name: str):
    sys.modules.pop(module_name, None)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        module = importlib.import_module(module_name)
    dep_warnings = [item for item in caught if issubclass(item.category, DeprecationWarning)]
    return module, dep_warnings


def test_import_emits_deprecation_warning() -> None:
    _, dep_warnings = _import_with_warnings("tonesoul.council_adapter")

    assert dep_warnings
    assert "deprecated" in str(dep_warnings[0].message).lower()


def test_module_still_importable() -> None:
    module, _ = _import_with_warnings("tonesoul.council_adapter")

    assert callable(module.run_council)
