"""Fail-visible guarantees for the Aegis integrity layer (Reality Sync PR 4).

Failure history (2026-06-12 review + adversarial verification):
1. runtime_adapter wrapped the whole Aegis block in
   ``except ImportError: pass`` — without PyNaCl, content filtering,
   vetoes, hash chaining AND signing were all silently skipped
   (fail-open in the integrity layer).
2. ``audit()`` never compared the stored chain head against the log
   tail, so deleting the newest traces was undetectable — the textbook
   hash-chain truncation gap, observed locally as a real divergence
   (.aegis/chain_head.txt vs the trace log).
3. Entries without a ``_chain`` block were silently skipped by
   verify_chain — 31k+ unsigned ledger writes were invisible to audit.

These tests pin the repaired behavior: degradation must be explicit and
recorded, never silent.
"""

from __future__ import annotations

import sys

from tonesoul.aegis_shield import AegisShield, build_chain_entry, sign_trace
from tonesoul.memory.provenance_chain import IsnadNode


class _StubStore:
    """Minimal store stub: just enough for AegisShield.audit()."""

    def __init__(self, traces):
        self._traces = traces

    def get_traces(self, n=10000):
        return self._traces[:n]


def _chained(traces):
    """Build a valid chain over the given bare traces."""
    out = []
    head = ""
    for t in traces:
        entry = build_chain_entry(dict(t), head)
        head = entry["_chain"]["hash"]
        out.append(entry)
    return out, head


# ---------------------------------------------------------------------------
# 1. sign_trace without PyNaCl: explicit UNSIGNED marker, no exception
# ---------------------------------------------------------------------------


def test_sign_trace_without_pynacl_marks_unsigned(monkeypatch):
    # Block nacl imports for the duration of this test.
    monkeypatch.setitem(sys.modules, "nacl", None)
    monkeypatch.setitem(sys.modules, "nacl.signing", None)

    trace = {"agent": "test-agent", "payload": "x"}
    result = sign_trace(trace, "test-agent")

    sig = result.get("_signature")
    assert isinstance(sig, dict), "trace must carry an explicit signature block"
    assert sig.get("error") == "unsigned_pynacl_unavailable", (
        "without PyNaCl the trace must be explicitly marked unsigned — "
        "silent skipping is the fail-open this PR removed"
    )


# ---------------------------------------------------------------------------
# 2. audit(): chain head anchor mismatch is detected (truncation gap)
# ---------------------------------------------------------------------------


def test_audit_detects_head_tail_divergence():
    traces, true_head = _chained([{"agent": "a", "n": 1}, {"agent": "a", "n": 2}])

    # Shield believes a head that does not match the log tail —
    # e.g. the newest trace was deleted after commit.
    shield = AegisShield(chain_head="deadbeef" * 8)
    report = shield.audit(_StubStore(traces))

    assert report["head_matches_tail"] is False
    assert report["chain_tail"] == traces[-1]["_chain"]["hash"]
    assert report["integrity"] == "compromised"
    assert any("anchor mismatch" in e for e in report["chain_errors"])


def test_audit_intact_when_head_anchors_tail():
    traces, true_head = _chained([{"agent": "a", "n": 1}])
    # Unsigned traces fail signature verification by design (visible),
    # so give the entry a passing structure by checking fields directly.
    shield = AegisShield(chain_head=true_head)
    report = shield.audit(_StubStore(traces))

    assert report["head_matches_tail"] is True
    assert report["chain_valid"] is True
    assert report["chain_head"] == true_head


# ---------------------------------------------------------------------------
# 3. audit(): unchained entries are counted, not silently skipped
# ---------------------------------------------------------------------------


def test_audit_counts_unchained_entries():
    traces, head = _chained([{"agent": "a", "n": 1}])
    traces.append({"agent": "a", "n": 2})  # legacy/unchained entry
    traces.append({"agent": "a", "n": 3})  # another one

    shield = AegisShield(chain_head=head)
    report = shield.audit(_StubStore(traces))

    assert report["unchained_entries"] == 2, (
        "entries without _chain must be surfaced — verify_chain skipping "
        "them silently was audit blind spot #3"
    )


# ---------------------------------------------------------------------------
# 4. provenance placeholder tells the truth
# ---------------------------------------------------------------------------


def test_isnad_default_signature_is_unsigned():
    node = IsnadNode(agent_id="a1", role="WITNESS")
    assert node.signature == "UNSIGNED", (
        "the default must state that nothing was signed — "
        "'SIG_AUTO_GENERATED' implied a signature that never existed"
    )
