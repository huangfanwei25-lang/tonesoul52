from __future__ import annotations

import pytest

import scripts.run_gold_scan as run_gold_scan
import scripts.test_dream_engine_5289 as dream_engine_script


def test_run_gold_scan_exits_with_phase_581_notice() -> None:
    with pytest.raises(SystemExit) as exc_info:
        run_gold_scan.main()

    assert str(exc_info.value) == run_gold_scan.EXIT_MESSAGE


def test_test_dream_engine_5289_exits_with_phase_581_notice() -> None:
    with pytest.raises(SystemExit) as exc_info:
        dream_engine_script.main()

    assert str(exc_info.value) == dream_engine_script.EXIT_MESSAGE
