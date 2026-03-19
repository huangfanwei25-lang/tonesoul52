from tonesoul import ystm_demo
from tonesoul.ystm.demo import DEFAULT_SEGMENTS, write_demo_outputs


def test_ystm_demo_reexports_demo_symbols() -> None:
    assert ystm_demo.DEFAULT_SEGMENTS is DEFAULT_SEGMENTS
    assert ystm_demo.write_demo_outputs is write_demo_outputs
