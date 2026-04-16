"""Redis key / channel constants shared across storage backends.

Extracted from store.py to break the circular dependency:
  store.py ↔ backends.redis_store

This module is a leaf — it imports nothing from tonesoul.
"""

# ── Governance ──────────────────────────────────────────────────────────
KEY_GOVERNANCE = "ts:governance"  # JSON string
KEY_ZONES = "ts:zones"  # JSON string
STREAM_TRACES = "ts:traces"  # Redis Stream (append-only)
CHANNEL_EVENTS = "ts:events"  # Pub/sub channel

# ── Locking ─────────────────────────────────────────────────────────────
LOCK_PREFIX = "ts:locks:"  # Per-task lock keys
COMMIT_LOCK_KEY = "ts:commit_lock"  # Canonical governance commit mutex

# ── Per-agent lanes ─────────────────────────────────────────────────────
PERSPECTIVE_PREFIX = "ts:perspectives:"  # Per-agent perspective lane
CHECKPOINT_PREFIX = "ts:checkpoints:"  # Mid-session checkpoint lane
OBSERVER_CURSOR_PREFIX = "ts:observer_cursors:"  # Per-agent since-last-seen cursor

# ── Non-canonical data lanes ────────────────────────────────────────────
KEY_COMPACTED = "ts:compacted"  # Non-canonical resumability/compaction lane
KEY_SUBJECT_SNAPSHOTS = "ts:subject_snapshots"  # Stable non-canonical subject snapshot lane
KEY_ROUTING_EVENTS = "ts:routing_events"  # Router adoption and ambiguity telemetry lane
KEY_COUNCIL_VERDICTS = "ts:council_verdicts"  # Bounded council verdict persistence lane
FIELD_KEY = "ts:field"  # Experimental semantic-field synthesis surface
