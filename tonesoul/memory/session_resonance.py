"""Session Resonance — detecting when the same tension returns in a different form.

A system that never recognises its own recurring patterns is not learning.
It is cycling.

The difference between a recurring pattern and a fresh problem:
  Fresh problem   → new topics, new tensions, no prior history
  Recurring       → the same underlying question, dressed in different words

Resonance is not similarity. Two sessions can discuss the same words and
have nothing to do with each other. Two sessions can use completely different
words and be wrestling with the exact same tension. Resonance lives in the
structural relationship between what was unresolved before and what is
unresolved now.

What we detect:
  1. Topic overlap          — Jaccard similarity of extracted topic sets
  2. Tension echo           — both sessions had unresolved tension on a shared keyword
  3. Outcome pattern        — what happened last time this configuration arose
  4. Drift correlation      — both sessions showed elevated drift

What we do NOT do:
  - Semantic embedding (no model required, no GPU)
  - Cross-session causal claims ("X caused Y")
  - Prescribe action ("you should do Z")

The output is purely observational. The governance layer decides what to do
with the observation. This module is advisory, like WorldSense.

Relationship to other modules:
  session_digest.py    → produces the session trace we fingerprint from
  memory/aaak.py       → produces the Keys we search for topic signals in
  memory/freshness.py  → resonance score decays over time, same λ
  yuhun/world_sense.py → recurring patterns raise background tension_delta
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

__ts_layer__ = "memory"
__ts_purpose__ = (
    "Session resonance: detect when the same structural tension recurs across "
    "sessions, surfacing recurring patterns for governance awareness."
)

# Minimum Jaccard similarity to consider two sessions resonant
DEFAULT_RESONANCE_THRESHOLD: float = 0.25

# Time decay: resonance from an old session is less urgent than a recent one
# Same λ as freshness.py (half-life 7 days)
_HALF_LIFE_DAYS: float = 30.0   # longer window for cross-session patterns
_LAMBDA: float = math.log(2) / _HALF_LIFE_DAYS

# How many sessions constitute a "recurring" pattern
MIN_OCCURRENCES_FOR_PATTERN: int = 2

# Maximum fingerprint topics to extract
_MAX_TOPICS: int = 12

# Verdicts that count as "unresolved" outcomes
_UNRESOLVED_VERDICTS = frozenset({"block", "refine", "declare_stance"})


# ── Data structures ───────────────────────────────────────────────────────────


@dataclass
class SessionFingerprint:
    """Compressed structural signature of a session.

    Extracted from session traces, AAAK blocks, or handoff JSON.
    Does not contain full content — only the signals needed for resonance detection.
    """

    session_id: str
    topics: List[str]              # normalised topic keywords
    tension_keywords: List[str]    # keywords from unresolved tension events
    verdict: str                   # final council verdict (or "unknown")
    drift_level: float             # peak drift during session (0.0–1.0)
    timestamp: str                 # ISO-8601 of session end
    agent_id: str = ""

    @property
    def is_unresolved(self) -> bool:
        return self.verdict in _UNRESOLVED_VERDICTS

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "topics": self.topics,
            "tension_keywords": self.tension_keywords,
            "verdict": self.verdict,
            "drift_level": round(self.drift_level, 4),
            "timestamp": self.timestamp,
            "agent_id": self.agent_id,
        }


@dataclass
class ResonanceSignal:
    """A detected echo between the current session and a historical one."""

    current_session_id: str
    matched_session_id: str
    matched_timestamp: str
    topic_overlap: List[str]        # topics shared between both sessions
    tension_echo: bool              # both had unresolved tension on a shared keyword
    prior_outcome: str              # what happened in the matched session
    resonance_score: float          # 0.0 (no echo) → 1.0 (strong echo)
    days_ago: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_session_id": self.current_session_id,
            "matched_session_id": self.matched_session_id,
            "matched_timestamp": self.matched_timestamp,
            "topic_overlap": self.topic_overlap,
            "tension_echo": self.tension_echo,
            "prior_outcome": self.prior_outcome,
            "resonance_score": round(self.resonance_score, 4),
            "days_ago": round(self.days_ago, 1),
        }


@dataclass
class RecurringPattern:
    """A structural tension that has appeared across multiple sessions."""

    topic: str
    occurrences: int
    session_ids: List[str]
    typical_outcome: str            # most common verdict across these sessions
    unresolved_fraction: float      # fraction of occurrences with unresolved verdict
    first_seen_at: str
    last_seen_at: str

    @property
    def is_chronic(self) -> bool:
        """True when this pattern keeps ending unresolved."""
        return self.unresolved_fraction >= 0.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "occurrences": self.occurrences,
            "session_ids": self.session_ids,
            "typical_outcome": self.typical_outcome,
            "unresolved_fraction": round(self.unresolved_fraction, 4),
            "first_seen_at": self.first_seen_at,
            "last_seen_at": self.last_seen_at,
            "is_chronic": self.is_chronic,
        }


# ── Fingerprint extraction ────────────────────────────────────────────────────


_STOP_WORDS = frozenset({
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "this", "that", "it", "its",
    "we", "i", "you", "he", "she", "they", "their", "our", "your",
    "from", "by", "as", "not", "no", "so", "if", "then", "also",
})


def _tokenise(text: str) -> List[str]:
    """Split text into lowercase alpha tokens, filtering stop words."""
    return [
        t for t in re.findall(r"[a-zA-Z一-鿿]{2,}", text.lower())
        if t not in _STOP_WORDS
    ]


def _top_tokens(texts: List[str], limit: int = _MAX_TOPICS) -> List[str]:
    tokens: List[str] = []
    for t in texts:
        tokens.extend(_tokenise(t))
    counts = Counter(tokens)
    return [tok for tok, _ in counts.most_common(limit)]


def fingerprint_session(
    trace: Dict[str, Any],
    *,
    session_id: str = "",
) -> SessionFingerprint:
    """Extract a SessionFingerprint from a session trace dict.

    Works with raw traces, AAAK dicts, handoff JSON, or session_digest output.
    Missing keys are silently ignored.
    """
    sid = session_id or str(trace.get("session_id", ""))
    agent_id = str(trace.get("agent", ""))
    timestamp = str(trace.get("timestamp", "") or trace.get("compressed_at", ""))
    if not timestamp:
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # Collect text sources for topic extraction
    text_sources: List[str] = []
    for key in ("topics", "learnings", "keys", "anchors", "arcs"):
        val = trace.get(key)
        if isinstance(val, list):
            text_sources.extend(str(v) for v in val if v)
        elif isinstance(val, str) and val:
            text_sources.append(val)

    summary = str(trace.get("summary") or trace.get("task_track_hint") or "")
    if summary:
        text_sources.append(summary)

    topics = _top_tokens(text_sources)

    # Extract tension keywords from unresolved tension events
    tension_keywords: List[str] = []
    for event in trace.get("tension_events") or []:
        if isinstance(event, dict) and not event.get("resolution"):
            topic_text = str(event.get("topic") or event.get("description") or "")
            tension_keywords.extend(_tokenise(topic_text))
    # Also from anomalies (AAAK format)
    for anomaly in trace.get("anomalies") or []:
        tension_keywords.extend(_tokenise(str(anomaly)))

    tension_keywords = list(dict.fromkeys(tension_keywords))[:_MAX_TOPICS]

    # Verdict
    verdict = str(trace.get("verdict", "") or trace.get("council_verdict", "") or "unknown")

    # Drift
    drift_level = 0.0
    ts = trace.get("tension_summary")
    if isinstance(ts, dict):
        drift_level = float(ts.get("max_severity", 0.0))
    else:
        drift_level = float(trace.get("drift_level", 0.0) or 0.0)
    drift_level = max(0.0, min(1.0, drift_level))

    return SessionFingerprint(
        session_id=sid,
        topics=topics,
        tension_keywords=tension_keywords,
        verdict=verdict,
        drift_level=drift_level,
        timestamp=timestamp,
        agent_id=agent_id,
    )


# ── Resonance scoring ─────────────────────────────────────────────────────────


def _parse_iso(ts: str) -> Optional[datetime]:
    text = str(ts or "").strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
        return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)
    except ValueError:
        return None


def _days_between(ts_a: str, ts_b: str) -> float:
    a, b = _parse_iso(ts_a), _parse_iso(ts_b)
    if a is None or b is None:
        return 0.0
    return abs((a - b).total_seconds()) / 86400.0


def _time_decay(days: float) -> float:
    """Fresher resonance is more urgent. Same exponential as freshness.py."""
    return math.exp(-_LAMBDA * days)


def _jaccard(set_a: List[str], set_b: List[str]) -> float:
    if not set_a or not set_b:
        return 0.0
    a, b = set(set_a), set(set_b)
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union > 0 else 0.0


def resonance_score(
    current: SessionFingerprint,
    historical: SessionFingerprint,
    *,
    now: Optional[datetime] = None,
) -> Tuple[float, List[str], bool]:
    """Compute resonance score between two session fingerprints.

    Returns:
        (score, topic_overlap, tension_echo)
        score        — 0.0 to 1.0
        topic_overlap — shared topic keywords
        tension_echo  — True if both had tension on a shared keyword
    """
    topic_jaccard = _jaccard(current.topics, historical.topics)
    topic_overlap = list(set(current.topics) & set(historical.topics))

    # Tension echo: shared unresolved tension keyword
    tension_echo = bool(
        set(current.tension_keywords) & set(historical.tension_keywords)
    )

    # Drift correlation bonus: both sessions showed elevated drift
    drift_bonus = 0.0
    if current.drift_level >= 0.5 and historical.drift_level >= 0.5:
        drift_bonus = 0.1

    # Time decay
    ref_ts = now.isoformat().replace("+00:00", "Z") if now else current.timestamp
    days = _days_between(ref_ts, historical.timestamp)
    decay = _time_decay(days)

    # Base score
    base = topic_jaccard + (0.15 if tension_echo else 0.0) + drift_bonus
    score = min(1.0, base * decay)

    return round(score, 4), topic_overlap, tension_echo


# ── Public API ────────────────────────────────────────────────────────────────


def find_resonances(
    current: SessionFingerprint,
    history: List[SessionFingerprint],
    *,
    threshold: float = DEFAULT_RESONANCE_THRESHOLD,
    now: Optional[datetime] = None,
) -> List[ResonanceSignal]:
    """Find historical sessions that resonate with the current one.

    Returns a list of ResonanceSignals sorted by score descending.
    Excludes the current session itself (matched by session_id).
    """
    signals: List[ResonanceSignal] = []

    for hist in history:
        if hist.session_id == current.session_id:
            continue

        score, overlap, echo = resonance_score(current, hist, now=now)
        if score < threshold:
            continue

        ref_ts = now.isoformat().replace("+00:00", "Z") if now else current.timestamp
        days = _days_between(ref_ts, hist.timestamp)

        signals.append(
            ResonanceSignal(
                current_session_id=current.session_id,
                matched_session_id=hist.session_id,
                matched_timestamp=hist.timestamp,
                topic_overlap=overlap,
                tension_echo=echo,
                prior_outcome=hist.verdict,
                resonance_score=score,
                days_ago=round(days, 1),
            )
        )

    return sorted(signals, key=lambda s: s.resonance_score, reverse=True)


def extract_recurring_patterns(
    history: List[SessionFingerprint],
    *,
    min_occurrences: int = MIN_OCCURRENCES_FOR_PATTERN,
) -> List[RecurringPattern]:
    """Find topics that appear across multiple sessions.

    Returns patterns sorted by occurrence count (most frequent first).
    Only includes topics that appear in at least ``min_occurrences`` sessions.
    """
    # Count which sessions each topic appears in
    topic_sessions: Dict[str, List[SessionFingerprint]] = {}
    for fp in history:
        seen = set()
        for topic in fp.topics:
            if topic not in seen:
                seen.add(topic)
                if topic not in topic_sessions:
                    topic_sessions[topic] = []
                topic_sessions[topic].append(fp)

    patterns: List[RecurringPattern] = []
    for topic, sessions in topic_sessions.items():
        if len(sessions) < min_occurrences:
            continue

        verdicts = [s.verdict for s in sessions]
        typical = Counter(verdicts).most_common(1)[0][0] if verdicts else "unknown"
        unresolved = sum(1 for v in verdicts if v in _UNRESOLVED_VERDICTS)

        timestamps = sorted(s.timestamp for s in sessions if s.timestamp)
        first_seen = timestamps[0] if timestamps else ""
        last_seen = timestamps[-1] if timestamps else ""

        patterns.append(
            RecurringPattern(
                topic=topic,
                occurrences=len(sessions),
                session_ids=[s.session_id for s in sessions],
                typical_outcome=typical,
                unresolved_fraction=round(unresolved / len(sessions), 4),
                first_seen_at=first_seen,
                last_seen_at=last_seen,
            )
        )

    return sorted(patterns, key=lambda p: p.occurrences, reverse=True)


def background_tension_from_resonance(
    signals: List[ResonanceSignal],
    patterns: List[RecurringPattern],
) -> float:
    """Estimate how much resonance raises the system's background tension.

    High score = many strong echoes of unresolved past tensions → worth surfacing
    as a DreamCandidate (analogous to freshness.background_tension_delta).
    """
    if not signals and not patterns:
        return 0.0

    signal_contribution = sum(
        s.resonance_score * (1.5 if s.tension_echo else 1.0)
        for s in signals
    ) / max(1, len(signals))

    chronic_patterns = [p for p in patterns if p.is_chronic]
    pattern_contribution = min(1.0, len(chronic_patterns) * 0.1)

    return round(min(1.0, signal_contribution * 0.7 + pattern_contribution * 0.3), 4)
