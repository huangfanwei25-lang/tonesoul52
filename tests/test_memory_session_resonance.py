"""Tests for tonesoul.memory.session_resonance."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from tonesoul.memory.session_resonance import (
    RecurringPattern,
    ResonanceSignal,
    SessionFingerprint,
    background_tension_from_resonance,
    extract_recurring_patterns,
    find_resonances,
    fingerprint_session,
    resonance_score,
)


def _ts(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _now():
    return datetime.now(timezone.utc)


def _fp(
    session_id="s1",
    topics=None,
    tension_keywords=None,
    verdict="approve",
    drift_level=0.2,
    timestamp=None,
):
    return SessionFingerprint(
        session_id=session_id,
        topics=topics or ["governance", "tension", "council"],
        tension_keywords=tension_keywords or [],
        verdict=verdict,
        drift_level=drift_level,
        timestamp=timestamp or _ts(_now()),
    )


# ── SessionFingerprint ────────────────────────────────────────────────────────


class TestSessionFingerprint:
    def test_is_unresolved_for_block(self):
        fp = _fp(verdict="block")
        assert fp.is_unresolved is True

    def test_is_unresolved_for_refine(self):
        fp = _fp(verdict="refine")
        assert fp.is_unresolved is True

    def test_is_unresolved_for_declare_stance(self):
        fp = _fp(verdict="declare_stance")
        assert fp.is_unresolved is True

    def test_is_not_unresolved_for_approve(self):
        fp = _fp(verdict="approve")
        assert fp.is_unresolved is False

    def test_to_dict_has_required_keys(self):
        fp = _fp()
        d = fp.to_dict()
        for key in (
            "session_id",
            "topics",
            "tension_keywords",
            "verdict",
            "drift_level",
            "timestamp",
        ):
            assert key in d


# ── fingerprint_session ───────────────────────────────────────────────────────


class TestFingerprintSession:
    def test_returns_session_fingerprint(self):
        result = fingerprint_session({})
        assert isinstance(result, SessionFingerprint)

    def test_session_id_extracted(self):
        result = fingerprint_session({"session_id": "abc-123"})
        assert result.session_id == "abc-123"

    def test_session_id_override(self):
        result = fingerprint_session({"session_id": "from_trace"}, session_id="override")
        assert result.session_id == "override"

    def test_topics_from_topics_list(self):
        result = fingerprint_session({"topics": ["governance", "drift", "vow"]})
        assert len(result.topics) > 0

    def test_topics_from_learnings(self):
        result = fingerprint_session({"learnings": ["the vow system improved coherence"]})
        assert any(t in result.topics for t in ["vow", "system", "coherence"])

    def test_topics_from_aaak_keys(self):
        result = fingerprint_session({"keys": ["run the drift monitor next time"]})
        assert any(t in result.topics for t in ["drift", "monitor"])

    def test_verdict_extracted(self):
        result = fingerprint_session({"verdict": "refine"})
        assert result.verdict == "refine"

    def test_verdict_defaults_to_unknown(self):
        result = fingerprint_session({})
        assert result.verdict == "unknown"

    def test_tension_keywords_from_unresolved_events(self):
        trace = {
            "tension_events": [
                {"topic": "axiom violation", "severity": 0.8},  # no resolution
                {"topic": "fixed issue", "resolution": "done"},  # resolved
            ]
        }
        result = fingerprint_session(trace)
        assert any("axiom" in kw or "violation" in kw for kw in result.tension_keywords)

    def test_resolved_tension_not_in_keywords(self):
        trace = {
            "tension_events": [
                {"topic": "resolved tension", "resolution": "done"},
            ]
        }
        result = fingerprint_session(trace)
        assert "resolved" not in result.tension_keywords

    def test_drift_from_tension_summary(self):
        trace = {"tension_summary": {"max_severity": 0.75}}
        result = fingerprint_session(trace)
        assert abs(result.drift_level - 0.75) < 0.01

    def test_drift_clamped_to_unit_interval(self):
        trace = {"drift_level": 2.5}
        result = fingerprint_session(trace)
        assert result.drift_level <= 1.0

    def test_timestamp_auto_set_when_missing(self):
        result = fingerprint_session({})
        assert result.timestamp

    def test_agent_extracted(self):
        result = fingerprint_session({"agent": "claude-sonnet-4-6"})
        assert result.agent_id == "claude-sonnet-4-6"

    def test_anomalies_contribute_to_tension_keywords(self):
        trace = {"anomalies": ["carry: unresolved governance drift"]}
        result = fingerprint_session(trace)
        assert any(kw in result.tension_keywords for kw in ["governance", "drift", "unresolved"])


# ── resonance_score ───────────────────────────────────────────────────────────


class TestResonanceScore:
    def test_identical_topics_gives_high_score(self):
        topics = ["governance", "tension", "council", "drift"]
        fp_a = _fp(session_id="a", topics=topics, timestamp=_ts(_now()))
        fp_b = _fp(session_id="b", topics=topics, timestamp=_ts(_now()))
        score, overlap, _ = resonance_score(fp_a, fp_b)
        assert score > 0.7

    def test_disjoint_topics_gives_zero(self):
        fp_a = _fp(session_id="a", topics=["alpha", "beta"], timestamp=_ts(_now()))
        fp_b = _fp(session_id="b", topics=["gamma", "delta"], timestamp=_ts(_now()))
        score, overlap, _ = resonance_score(fp_a, fp_b)
        assert score == 0.0
        assert overlap == []

    def test_tension_echo_bonus_applied(self):
        now = _now()
        # Use partial overlap so base Jaccard < 1.0, leaving room for the echo bonus
        fp_a = _fp(
            session_id="a",
            topics=["governance", "alpha", "beta"],
            tension_keywords=["axiom"],
            timestamp=_ts(now),
        )
        fp_b_echo = _fp(
            session_id="b",
            topics=["governance", "gamma", "delta"],
            tension_keywords=["axiom"],
            timestamp=_ts(now),
        )
        fp_b_no = _fp(
            session_id="c",
            topics=["governance", "gamma", "delta"],
            tension_keywords=[],
            timestamp=_ts(now),
        )
        score_with_echo, _, echo = resonance_score(fp_a, fp_b_echo)
        score_no_echo, _, no_echo = resonance_score(fp_a, fp_b_no)
        assert echo is True
        assert no_echo is False
        assert score_with_echo > score_no_echo

    def test_old_match_scores_lower_than_recent(self):
        now = _now()
        topics = ["governance", "tension", "council"]
        fp_current = _fp(session_id="cur", topics=topics, timestamp=_ts(now))
        fp_recent = _fp(session_id="recent", topics=topics, timestamp=_ts(now - timedelta(days=3)))
        fp_old = _fp(session_id="old", topics=topics, timestamp=_ts(now - timedelta(days=120)))

        score_recent, _, _ = resonance_score(fp_current, fp_recent, now=now)
        score_old, _, _ = resonance_score(fp_current, fp_old, now=now)
        assert score_recent > score_old

    def test_topic_overlap_contains_shared_topics(self):
        fp_a = _fp(session_id="a", topics=["alpha", "beta", "gamma"])
        fp_b = _fp(session_id="b", topics=["beta", "gamma", "delta"])
        _, overlap, _ = resonance_score(fp_a, fp_b)
        assert set(overlap) == {"beta", "gamma"}

    def test_score_in_unit_interval(self):
        fp_a = _fp(session_id="a")
        fp_b = _fp(session_id="b")
        score, _, _ = resonance_score(fp_a, fp_b)
        assert 0.0 <= score <= 1.0

    def test_dual_high_drift_gives_bonus(self):
        now = _now()
        # Partial overlap so base < 1.0, leaving room for drift bonus
        fp_a = _fp(
            session_id="a",
            topics=["governance", "alpha", "beta"],
            drift_level=0.8,
            timestamp=_ts(now),
        )
        fp_b_high = _fp(
            session_id="b",
            topics=["governance", "gamma", "delta"],
            drift_level=0.9,
            timestamp=_ts(now),
        )
        fp_b_low = _fp(
            session_id="c",
            topics=["governance", "gamma", "delta"],
            drift_level=0.1,
            timestamp=_ts(now),
        )
        score_high, _, _ = resonance_score(fp_a, fp_b_high)
        score_low, _, _ = resonance_score(fp_a, fp_b_low)
        assert score_high > score_low


# ── find_resonances ───────────────────────────────────────────────────────────


class TestFindResonances:
    def _history(self, now, topics_list):
        return [
            _fp(session_id=f"h{i}", topics=t, timestamp=_ts(now - timedelta(days=i + 1)))
            for i, t in enumerate(topics_list)
        ]

    def test_returns_list_of_resonance_signals(self):
        now = _now()
        current = _fp(session_id="cur", topics=["governance"], timestamp=_ts(now))
        history = self._history(now, [["governance", "drift"]])
        result = find_resonances(current, history)
        assert all(isinstance(s, ResonanceSignal) for s in result)

    def test_excludes_current_session(self):
        now = _now()
        current = _fp(session_id="cur", timestamp=_ts(now))
        history = [current] + self._history(now, [["governance", "drift"]])
        result = find_resonances(current, history)
        assert all(s.matched_session_id != "cur" for s in result)

    def test_sorted_by_score_descending(self):
        now = _now()
        current = _fp(session_id="cur", topics=["governance", "tension"], timestamp=_ts(now))
        history = self._history(
            now,
            [
                ["governance", "tension", "council"],  # high overlap
                ["governance"],  # moderate
                ["unrelated", "topics"],  # no overlap
            ],
        )
        result = find_resonances(current, history, now=now)
        scores = [s.resonance_score for s in result]
        assert scores == sorted(scores, reverse=True)

    def test_threshold_filters_low_scores(self):
        now = _now()
        current = _fp(session_id="cur", topics=["alpha"], timestamp=_ts(now))
        history = self._history(now, [["beta", "gamma"]])  # no overlap
        result = find_resonances(current, history, threshold=0.1)
        assert len(result) == 0

    def test_empty_history_returns_empty(self):
        current = _fp(session_id="cur")
        assert find_resonances(current, []) == []

    def test_tension_echo_field_set(self):
        now = _now()
        current = _fp(
            session_id="cur", topics=["governance"], tension_keywords=["axiom"], timestamp=_ts(now)
        )
        history = [
            _fp(
                session_id="h1",
                topics=["governance"],
                tension_keywords=["axiom"],
                timestamp=_ts(now - timedelta(hours=1)),
            )
        ]
        result = find_resonances(current, history, threshold=0.0, now=now)
        if result:
            assert result[0].tension_echo is True

    def test_days_ago_populated(self):
        now = _now()
        current = _fp(session_id="cur", topics=["governance", "drift"], timestamp=_ts(now))
        past = _fp(
            session_id="h1", topics=["governance", "drift"], timestamp=_ts(now - timedelta(days=5))
        )
        result = find_resonances(current, [past], threshold=0.0, now=now)
        if result:
            assert abs(result[0].days_ago - 5.0) < 1.0

    def test_prior_outcome_from_matched_session(self):
        now = _now()
        current = _fp(session_id="cur", topics=["governance"], timestamp=_ts(now))
        history = [
            _fp(
                session_id="h1",
                topics=["governance"],
                verdict="block",
                timestamp=_ts(now - timedelta(hours=1)),
            )
        ]
        result = find_resonances(current, history, threshold=0.0, now=now)
        if result:
            assert result[0].prior_outcome == "block"


# ── extract_recurring_patterns ────────────────────────────────────────────────


class TestExtractRecurringPatterns:
    def test_returns_patterns(self):
        history = [
            _fp(session_id="s1", topics=["governance", "drift"]),
            _fp(session_id="s2", topics=["governance", "tension"]),
            _fp(session_id="s3", topics=["governance"]),
        ]
        patterns = extract_recurring_patterns(history)
        assert any(p.topic == "governance" for p in patterns)

    def test_single_occurrence_not_returned(self):
        history = [_fp(session_id="s1", topics=["unique_topic"])]
        patterns = extract_recurring_patterns(history, min_occurrences=2)
        assert not any(p.topic == "unique_topic" for p in patterns)

    def test_sorted_by_occurrences_descending(self):
        history = [
            _fp(session_id="s1", topics=["governance", "drift"]),
            _fp(session_id="s2", topics=["governance", "drift", "tension"]),
            _fp(session_id="s3", topics=["governance", "tension"]),
        ]
        patterns = extract_recurring_patterns(history)
        counts = [p.occurrences for p in patterns]
        assert counts == sorted(counts, reverse=True)

    def test_typical_outcome_is_most_common_verdict(self):
        history = [
            _fp(session_id="s1", topics=["topic"], verdict="approve"),
            _fp(session_id="s2", topics=["topic"], verdict="approve"),
            _fp(session_id="s3", topics=["topic"], verdict="block"),
        ]
        patterns = extract_recurring_patterns(history)
        topic_pattern = next((p for p in patterns if p.topic == "topic"), None)
        if topic_pattern:
            assert topic_pattern.typical_outcome == "approve"

    def test_unresolved_fraction_calculated(self):
        history = [
            _fp(session_id="s1", topics=["topic"], verdict="block"),
            _fp(session_id="s2", topics=["topic"], verdict="block"),
            _fp(session_id="s3", topics=["topic"], verdict="approve"),
        ]
        patterns = extract_recurring_patterns(history)
        topic_pattern = next((p for p in patterns if p.topic == "topic"), None)
        if topic_pattern:
            assert abs(topic_pattern.unresolved_fraction - 2 / 3) < 0.01

    def test_is_chronic_when_mostly_unresolved(self):
        history = [
            _fp(session_id=f"s{i}", topics=["chronic_issue"], verdict="block") for i in range(4)
        ]
        patterns = extract_recurring_patterns(history)
        chronic = next((p for p in patterns if p.topic == "chronic_issue"), None)
        if chronic:
            assert chronic.is_chronic is True

    def test_not_chronic_when_mostly_resolved(self):
        history = [_fp(session_id=f"s{i}", topics=["stable"], verdict="approve") for i in range(4)]
        patterns = extract_recurring_patterns(history)
        stable = next((p for p in patterns if p.topic == "stable"), None)
        if stable:
            assert stable.is_chronic is False

    def test_empty_history_returns_empty(self):
        assert extract_recurring_patterns([]) == []

    def test_session_ids_populated(self):
        history = [
            _fp(session_id="sess-a", topics=["recurring"]),
            _fp(session_id="sess-b", topics=["recurring"]),
        ]
        patterns = extract_recurring_patterns(history)
        p = next((p for p in patterns if p.topic == "recurring"), None)
        if p:
            assert "sess-a" in p.session_ids
            assert "sess-b" in p.session_ids

    def test_to_dict_has_required_keys(self):
        history = [_fp(session_id=f"s{i}", topics=["key_topic"]) for i in range(3)]
        patterns = extract_recurring_patterns(history)
        if patterns:
            d = patterns[0].to_dict()
            for key in (
                "topic",
                "occurrences",
                "session_ids",
                "typical_outcome",
                "unresolved_fraction",
                "is_chronic",
            ):
                assert key in d


# ── background_tension_from_resonance ─────────────────────────────────────────


class TestBackgroundTensionFromResonance:
    def test_no_signals_no_patterns_gives_zero(self):
        assert background_tension_from_resonance([], []) == 0.0

    def test_strong_signals_give_positive_tension(self):
        signals = [
            ResonanceSignal("c", "h1", _ts(_now()), ["governance"], True, "block", 0.8),
            ResonanceSignal("c", "h2", _ts(_now()), ["drift"], True, "refine", 0.7),
        ]
        delta = background_tension_from_resonance(signals, [])
        assert delta > 0.0

    def test_tension_echo_signals_score_higher(self):
        echo = ResonanceSignal("c", "h1", _ts(_now()), ["gov"], True, "block", 0.6)
        no_echo = ResonanceSignal("c", "h2", _ts(_now()), ["gov"], False, "block", 0.6)
        delta_echo = background_tension_from_resonance([echo], [])
        delta_no = background_tension_from_resonance([no_echo], [])
        assert delta_echo > delta_no

    def test_chronic_patterns_raise_tension(self):
        chronic = RecurringPattern(
            topic="governance",
            occurrences=5,
            session_ids=["a", "b", "c", "d", "e"],
            typical_outcome="block",
            unresolved_fraction=0.8,
            first_seen_at="",
            last_seen_at="",
        )
        delta_with = background_tension_from_resonance([], [chronic])
        delta_without = background_tension_from_resonance([], [])
        assert delta_with > delta_without

    def test_tension_capped_at_one(self):
        signals = [
            ResonanceSignal("c", f"h{i}", _ts(_now()), ["gov"], True, "block", 1.0)
            for i in range(100)
        ]
        delta = background_tension_from_resonance(signals, [])
        assert delta <= 1.0
