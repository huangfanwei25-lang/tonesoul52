import importlib

from tonesoul import ystm_demo
from tonesoul.ystm.demo import DEFAULT_SEGMENTS, write_demo_outputs


def test_ystm_demo_reexports_demo_symbols() -> None:
    assert ystm_demo.DEFAULT_SEGMENTS is DEFAULT_SEGMENTS
    assert ystm_demo.write_demo_outputs is write_demo_outputs


def test_ystm_demo_exports_expected_public_surface() -> None:
    assert ystm_demo.__all__ == ["DEFAULT_SEGMENTS", "write_demo_outputs"]


def test_ystm_demo_wrapper_docstring_mentions_compatibility() -> None:
    assert "Compatibility wrapper" in (ystm_demo.__doc__ or "")


def test_ystm_demo_module_reloads_with_same_symbols() -> None:
    reloaded = importlib.reload(ystm_demo)

    assert reloaded.DEFAULT_SEGMENTS is DEFAULT_SEGMENTS
    assert reloaded.write_demo_outputs is write_demo_outputs
