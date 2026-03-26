from __future__ import annotations

import json
from pathlib import Path

from tonesoul.zone_registry import rebuild_from_traces


def test_rebuild_from_traces_ignores_missing_timestamp_for_last_seen(tmp_path: Path) -> None:
    traces_path = tmp_path / "session_traces.jsonl"
    governance_path = tmp_path / "governance_state.json"

    traces_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "session_id": "real-1",
                        "timestamp": "2026-03-26T10:00:00+00:00",
                        "topics": ["governance"],
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "session_id": "test-001",
                        "topics": ["governance"],
                    },
                    ensure_ascii=False,
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    governance_path.write_text("{}", encoding="utf-8")

    world = rebuild_from_traces(
        traces_path=traces_path,
        governance_path=governance_path,
    )

    governance_zone = next(zone for zone in world.zones if zone.zone_id == "governance")
    assert governance_zone.visit_count == 2
    assert governance_zone.first_seen == "2026-03-26T10:00:00+00:00"
    assert governance_zone.last_seen == "2026-03-26T10:00:00+00:00"
