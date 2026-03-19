from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import scripts.run_market_sweep as run_market_sweep


def test_main_reads_legacy_cache_and_writes_private_cache(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(run_market_sweep, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        run_market_sweep,
        "PRIVATE_CACHE_PATH",
        tmp_path / "memory" / "autonomous" / "market" / "market_sweep_cache.json",
    )
    monkeypatch.setattr(
        run_market_sweep,
        "LEGACY_CACHE_PATH",
        tmp_path / "market_sweep_cache.json",
    )
    monkeypatch.setattr(
        run_market_sweep,
        "STATUS_REPORT_PATH",
        tmp_path / "docs" / "status" / "market_sweep_latest.txt",
    )

    run_market_sweep.LEGACY_CACHE_PATH.write_text(
        json.dumps(["1101"], ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        run_market_sweep,
        "MarketDataIngestor",
        lambda: SimpleNamespace(is_available=True),
    )
    monkeypatch.setattr(run_market_sweep, "GoldDetector", lambda: object())
    monkeypatch.setattr(
        run_market_sweep,
        "get_all_twse_stocks",
        lambda _ingestor: [("1101", "Alpha", "tech"), ("1102", "Beta", "tech")],
    )
    monkeypatch.setattr(run_market_sweep.time, "sleep", lambda *_args, **_kwargs: None)

    def _scan_single(_ingestor: object, _detector: object, stock_id: str) -> SimpleNamespace:
        return SimpleNamespace(
            verdict="SILVER",
            gold_score=0.6,
            trailing_eps=1.2,
            current_pe=14.5,
            signals=[],
            stock_id=stock_id,
        )

    monkeypatch.setattr(run_market_sweep, "scan_single", _scan_single)

    run_market_sweep.main()

    private_cache = json.loads(run_market_sweep.PRIVATE_CACHE_PATH.read_text(encoding="utf-8"))
    assert private_cache == ["1101", "1102"]
    assert run_market_sweep.STATUS_REPORT_PATH.exists()
    report_text = run_market_sweep.STATUS_REPORT_PATH.read_text(encoding="utf-8")
    assert "SILVER STOCKS (1):" in report_text
    assert "1102 Beta" in report_text
