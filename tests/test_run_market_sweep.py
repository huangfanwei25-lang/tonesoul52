from __future__ import annotations

import pytest

import scripts.run_market_sweep as run_market_sweep


def test_main_exits_with_phase_581_notice() -> None:
    with pytest.raises(SystemExit) as exc_info:
        run_market_sweep.main()

    assert str(exc_info.value) == run_market_sweep.EXIT_MESSAGE
