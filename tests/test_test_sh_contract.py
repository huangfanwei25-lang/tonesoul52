from __future__ import annotations

from pathlib import Path


def test_fast_mode_uses_not_slow_marker_and_xdist() -> None:
    script = Path("test.sh").read_text(encoding="utf-8")

    assert 'python -m pytest tests/ -q "${PYTEST_IGNORES[@]}" -m "not slow" -n auto' in script


def test_full_mode_keeps_unfiltered_pytest_entry() -> None:
    script = Path("test.sh").read_text(encoding="utf-8")

    assert 'python -m pytest tests/ -q "${PYTEST_IGNORES[@]}" || fail "pytest failed"' in script
