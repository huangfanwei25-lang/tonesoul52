from __future__ import annotations

import json
from pathlib import Path

import scripts.run_private_memory_shadow_report as runner


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def test_build_report_tracks_active_and_shadow_pairs(tmp_path: Path) -> None:
    _write(
        tmp_path / "memory" / ".hierarchical_index" / "vows_meta.json",
        json.dumps(
            [{"statement": "a", "scope": ["output"], "verdict": "COMMIT"}],
            ensure_ascii=False,
            indent=2,
        ),
    )
    _write(
        tmp_path / "memory" / "memory" / ".hierarchical_index" / "vows_meta.json",
        json.dumps(
            [
                {
                    "statement": "a",
                    "scope": ["general"],
                    "verdict": "COMMIT",
                    "agent_id": "ToneSoul",
                    "timestamp": "2026-02-02T10:53:53",
                    "metadata": {},
                }
            ],
            ensure_ascii=False,
            indent=2,
        ),
    )
    _write_bytes(tmp_path / "memory" / ".hierarchical_index" / "hierarchical.index", b"ACTIVE")
    _write_bytes(
        tmp_path / "memory" / "memory" / ".hierarchical_index" / "hierarchical.index",
        b"SHADOW",
    )
    _write(
        tmp_path / "spec" / "governance" / "basename_divergence_registry_v1.json",
        json.dumps(
            {
                "version": "v1",
                "entries": [
                    {
                        "basename": "vows_meta.json",
                        "status": "unresolved_private_shadow",
                        "strategy": "defer_private_shadow_cleanup",
                        "paths": [
                            "memory/.hierarchical_index/vows_meta.json",
                            "memory/memory/.hierarchical_index/vows_meta.json",
                        ],
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
    )

    payload = runner.build_report(tmp_path)

    assert payload["metrics"]["pair_count"] == 2
    assert payload["metrics"]["divergent_pair_count"] == 2
    assert payload["registry_alignment"]["entry_present"] is True
    assert payload["registry_alignment"]["paths_match_expected"] is True
    vows_pair = next(pair for pair in payload["pairs"] if pair["relative_path"] == "vows_meta.json")
    assert vows_pair["comparison_mode"] == "json_structural_compare"
    assert vows_pair["active_item_count"] == 1
    assert vows_pair["shadow_item_count"] == 1
    assert vows_pair["key_shape_match"] is False
    assert vows_pair["needs_review"] is False


def test_main_writes_private_shadow_artifacts(tmp_path: Path) -> None:
    _write(
        tmp_path / "memory" / ".hierarchical_index" / "vows_meta.json",
        json.dumps([{"statement": "a", "scope": [], "verdict": "COMMIT"}], indent=2),
    )
    _write(
        tmp_path / "memory" / "memory" / ".hierarchical_index" / "vows_meta.json",
        json.dumps([{"statement": "b", "scope": [], "verdict": "COMMIT"}], indent=2),
    )

    exit_code = runner.main(["--repo-root", str(tmp_path), "--out-dir", "docs/status"])

    assert exit_code == 0
    payload = json.loads(
        (tmp_path / "docs" / "status" / runner.JSON_FILENAME).read_text(encoding="utf-8")
    )
    markdown = (tmp_path / "docs" / "status" / runner.MARKDOWN_FILENAME).read_text(encoding="utf-8")
    assert payload["contract"]["deferred_cleanup_phase"] == "private_memory_lane_cleanup"
    assert "# Private Memory Shadow Latest" in markdown
