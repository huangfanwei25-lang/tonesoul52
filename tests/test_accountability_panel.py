from __future__ import annotations

import pytest

from tonesoul.accountability_panel import AccountabilityEvent, render_panel


def _ev(**kw: object) -> AccountabilityEvent:
    base: dict[str, object] = dict(
        claim="c",
        evidence_at_claim="E1",
        held=False,
        caught_by="x",
        correction="y",
        lane="self-check",
    )
    base.update(kw)
    return AccountabilityEvent(**base)  # type: ignore[arg-type]


def test_render_is_html_and_contains_events() -> None:
    events = [
        _ev(claim="no-egress claim", caught_by="codex"),
        _ev(claim="held one", held=True, lane="co-observer"),
    ]
    html_doc = render_panel(events, generated_at="2026-07-01 00:00Z")
    assert html_doc.startswith("<!doctype html>")
    assert "no-egress claim" in html_doc and "codex" in html_doc
    assert "2026-07-01 00:00Z" in html_doc


def test_misses_lead_and_are_marked() -> None:
    events = [_ev(claim="HELDROW", held=True), _ev(claim="MISSROW", held=False)]
    html_doc = render_panel(events, generated_at="t")
    assert 'class="miss"' in html_doc and 'class="held"' in html_doc
    # within a lane, misses render before held claims
    assert html_doc.index("MISSROW") < html_doc.index("HELDROW")


def test_html_is_escaped() -> None:
    ev = _ev(claim="<script>alert(1)</script>", correction="a & b <tag>")
    html_doc = render_panel([ev], generated_at="t")
    assert "<script>alert(1)</script>" not in html_doc
    assert "&lt;script&gt;" in html_doc
    assert "a &amp; b &lt;tag&gt;" in html_doc


def test_counts_show_misses() -> None:
    events = [_ev(held=False), _ev(held=False), _ev(held=True)]
    html_doc = render_panel(events, generated_at="t")
    assert "共 3 件事件" in html_doc
    assert "<b>2</b>" in html_doc  # 2 misses highlighted


def test_bad_lane_and_tier_rejected() -> None:
    with pytest.raises(ValueError):
        _ev(lane="nonsense")
    with pytest.raises(ValueError):
        _ev(evidence_at_claim="E9")


def test_seed_events_render() -> None:
    # the real seed data must load + render without error
    import json
    from pathlib import Path

    events_path = (
        Path(__file__).resolve().parents[1] / "tools" / "accountability_panel" / "events.json"
    )
    raw = json.loads(events_path.read_text(encoding="utf-8"))
    events = [AccountabilityEvent(**e) for e in raw]
    assert len(events) >= 10
    html_doc = render_panel(events, generated_at="t")
    assert "no-egress" not in html_doc  # sanity: uses the zh claims, not a placeholder
    assert "沒站住" in html_doc and "站住" in html_doc
    # misses must be the majority-shown point
    assert sum(1 for e in events if not e.held) >= 1


def test_interactive_elements_present() -> None:
    html_doc = render_panel([_ev(claim="x", lane="self-check")], generated_at="t")
    assert 'id="mark-form"' in html_doc  # the live "mark me" form
    assert 'id="f-miss"' in html_doc  # miss-only filter
    assert 'data-lane="self-check"' in html_doc  # rows carry filter attributes
    assert "tools/accountability_panel/add.py" in html_doc  # JS emits the persistence CLI command
    assert "<script>" in html_doc


def test_append_event_persists_and_revalidates(tmp_path) -> None:
    import json

    from tools.accountability_panel.add import append_event

    p = tmp_path / "events.json"
    p.write_text("[]", encoding="utf-8")
    ev = AccountabilityEvent(
        claim="c1",
        evidence_at_claim="—",
        held=False,
        caught_by="人(梵威)",
        correction="fix",
        lane="co-observer",
    )
    assert append_event(p, ev) == 1
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data[0]["claim"] == "c1" and data[0]["lane"] == "co-observer"
    assert append_event(p, ev) == 2  # appends, does not overwrite
