# Responsibility-runtime Codex red-team report (2026-06-27)

> Role: different-model independent eye. Target: current `origin/master` at `40a1796`
> (`Merge pull request #212`). Method: read the runtime code, run the existing harness/tests,
> then probe adjacent surfaces not covered by the prior Opus pass. This is a security review
> report, not a fix PR.

## Executive summary

Existing gate tests are green, but the runtime is **not clean** under adversarial probes.

- Existing harness: `14/14` should-block scenarios blocked, `2/2` should-execute scenarios
  executed.
- Existing runtime tests: `60 passed`.
- New findings:
  - **1 true should-block -> executed bypass**: evidence refs made only of non-`C`/`Z`
    invisible/blank Unicode still execute.
  - **2 graph provenance defects**: forged enforcement results can create graph edges; repeated
    supersession misreports provenance.
  - **3 trace-integrity defects**: mutable nested trace payloads, duplicate seq under
    concurrency, and `executed` trace events emitted before adapter success.
  - **1 low resource-risk gap**: unbounded free text fields can be traced/executed at very large
    size.

## Baseline checks

```text
python tools/probe/responsibility_runtime_eval.py
# block-rate on should-block: 14/14
# execute-rate on should-execute: 2/2
# bypasses: 0

python -m pytest tests/test_responsibility_runtime_intent_validator.py \
  tests/test_responsibility_runtime_enforcer_trace.py \
  tests/test_responsibility_runtime_graph.py \
  tests/test_responsibility_runtime_redteam_regressions.py -q
# 60 passed
```

## Finding 1 — non-C/Z invisible or blank evidence refs still execute

**Severity:** High for the Phase 1-3 gate contract.

**Problem:** `_has_visible_content()` rejects only Unicode categories whose first letter is
`C` or `Z`. Several effectively invisible or blank characters are category `M`, `S`, or `L`,
so an evidence ref made only of those characters passes validation and reaches the adapter.
This is adjacent to, but not the same as, the prior U+200B/U+FEFF class.

**Files / lines:**

- `tonesoul/responsibility_runtime/intent_validator.py:24`
- `tonesoul/responsibility_runtime/intent_validator.py:95`

**Runnable repro:**

```python
import unicodedata
from tonesoul.responsibility_runtime import (
    Enforcer,
    FakePolicyEngine,
    InMemoryTraceStore,
    RecordingMemoryAdapter,
    decide_fail_closed,
    validate_intent,
)

chars = [
    ("VS16", "\ufe0f"),
    ("CGJ", "\u034f"),
    ("BRAILLE_BLANK", "\u2800"),
    ("HANGUL_FILLER", "\u3164"),
    ("MONGOLIAN_FVS1", "\u180b"),
]

for label, ch in chars:
    payload = {
        "intent": "memory.write.propose",
        "claim": "probe",
        "evidence_refs": [ch],
        "requested_scope": "long_term_memory",
    }
    v = validate_intent(payload)
    d = decide_fail_closed(FakePolicyEngine(), v)
    a = RecordingMemoryAdapter()
    trace = InMemoryTraceStore()
    r = Enforcer(memory_adapter=a, trace_store=trace).enforce(v, d)
    print(
        label,
        ch.encode("unicode_escape").decode("ascii"),
        unicodedata.category(ch),
        unicodedata.name(ch, "?"),
        "accepted=", v.accepted,
        "executed=", r.executed,
        "call_count=", a.call_count,
        "trace_refs=", tuple(ref.encode("unicode_escape").decode("ascii") for ref in trace.events[0].evidence_refs),
    )
```

**Output:**

```text
VS16 \ufe0f Mn VARIATION SELECTOR-16 accepted= True executed= True call_count= 1 trace_refs= ('\\ufe0f',)
CGJ \u034f Mn COMBINING GRAPHEME JOINER accepted= True executed= True call_count= 1 trace_refs= ('\\u034f',)
BRAILLE_BLANK \u2800 So BRAILLE PATTERN BLANK accepted= True executed= True call_count= 1 trace_refs= ('\\u2800',)
HANGUL_FILLER \u3164 Lo HANGUL FILLER accepted= True executed= True call_count= 1 trace_refs= ('\\u3164',)
MONGOLIAN_FVS1 \u180b Mn MONGOLIAN FREE VARIATION SELECTOR ONE accepted= True executed= True call_count= 1 trace_refs= ('\\u180b',)
```

**Confidence:** High. This is a concrete should-block evidence-shape bypass with adapter
execution.

**Suggested fix:** Do not use generic "not C/Z" as evidence-ref visibility. Evidence refs are
identifiers, not prose: give them a stricter grammar, or reject Unicode default-ignorable and
blank/filler code points explicitly. Keep the no-oracle boundary: `x` may still pass form, but
known invisible/blank characters should not.

## Finding 2 — `edge_from_enforcement()` accepts forged non-enforcement objects

**Severity:** High for Phase 4 provenance contract; Medium if treated as fake in-memory only.

**Problem:** `edge_from_enforcement()` only checks `getattr(result, "executed", False)`. A
plain object with `executed=True`, a fake `trace_event`, and a fake policy id can create a graph
edge without an actual `EnforcementResult`, policy decision, trace store, or adapter execution.

**Files / lines:**

- `tonesoul/responsibility_runtime/responsibility_graph.py:177`
- `tonesoul/responsibility_runtime/responsibility_graph.py:193`

**Runnable repro:**

```python
from types import SimpleNamespace
from tonesoul.responsibility_runtime import FakeResponsibilityGraph, edge_from_enforcement

fake_result = SimpleNamespace(
    executed=True,
    request_id="rr-forged-no-enforcer-call",
    trace_event=SimpleNamespace(
        evidence_refs=("turn_forged",),
        policy_decision=SimpleNamespace(policy_id="fake.policy.forged"),
    ),
)

g = FakeResponsibilityGraph()
edge = edge_from_enforcement(
    g,
    fake_result,
    subject="user",
    predicate="prefers",
    obj="forged graph memory",
    proposed_by="attacker",
)
print("edge_id=", edge.edge_id)
print("edges=", len(g.edges))
print("provenance=", g.provenance(edge.edge_id))
```

**Output:**

```text
edge_id= re-9329dd84703e1cce
edges= 1
provenance= EdgeProvenance(who='attacker', why=('turn_forged',), when=1, authorized_by_policy='fake.policy.forged', recorded_by_trace='rr-forged-no-enforcer-call', supersedes=None, superseded_by=None, revoked_at=None)
```

**Confidence:** High. The function that is meant to bind graph writes to authorized execution
accepts a forged object.

**Suggested fix:** Require `isinstance(result, EnforcementResult)` at runtime, and preferably
bind the graph to a trace store so `result.trace_event` / `request_id` can be checked against an
actual appended event. If direct `add_edge()` remains public, document it as unsafe/test-only or
make it private behind the enforcement-bound path.

## Finding 3 — trace `intent_payload` is only shallow-immutable

**Severity:** Medium.

**Problem:** `TraceEvent` is frozen and `intent_payload` is wrapped in `MappingProxyType`, but
the nested `evidence_refs` list remains mutable. A caller holding the trace event can mutate the
recorded payload after append. `TraceEvent.evidence_refs` remains a tuple snapshot, so replay is
partly safe, but the trace payload itself is not immutable.

**Files / lines:**

- `tonesoul/responsibility_runtime/trace.py:78`
- `tonesoul/responsibility_runtime/trace.py:80`
- `tonesoul/responsibility_runtime/trace.py:84`

**Runnable repro:**

```python
from tonesoul.responsibility_runtime import (
    Enforcer,
    FakePolicyEngine,
    InMemoryTraceStore,
    RecordingMemoryAdapter,
    decide_fail_closed,
    validate_intent,
)

payload = {
    "intent": "memory.write.propose",
    "claim": "original",
    "evidence_refs": ["turn_1"],
    "requested_scope": "long_term_memory",
}
v = validate_intent(payload)
d = decide_fail_closed(FakePolicyEngine(), v)
trace = InMemoryTraceStore()
r = Enforcer(memory_adapter=RecordingMemoryAdapter(), trace_store=trace).enforce(v, d)
print("before_payload=", trace.events[0].intent_payload)
trace.events[0].intent_payload["evidence_refs"].append("tampered_after_trace")
print("after_payload=", trace.events[0].intent_payload)
print("snapshot_evidence_refs=", trace.events[0].evidence_refs)
```

**Output:**

```text
before_payload= {'requested_scope': 'long_term_memory', 'intent': 'memory.write.propose', 'claim': 'original', 'evidence_refs': ['turn_1']}
after_payload= {'requested_scope': 'long_term_memory', 'intent': 'memory.write.propose', 'claim': 'original', 'evidence_refs': ['turn_1', 'tampered_after_trace']}
snapshot_evidence_refs= ('turn_1',)
```

**Confidence:** High. The mutation is deterministic.

**Suggested fix:** Recursively freeze trace payloads: lists -> tuples, dicts -> mapping proxies
of recursively frozen values, or store canonical JSON bytes plus parsed convenience fields.

## Finding 4 — concurrent appends duplicate and skip sequence numbers

**Severity:** Medium for replay/audit ordering; Low if this remains strictly single-threaded
test-only memory.

**Problem:** `InMemoryTraceStore.append()` computes `seq=len(self._events)+1` before appending,
without a lock. Under concurrent enforcement, multiple events can receive the same `seq`, and
other sequence numbers are skipped. No trace was lost in the probe, but `seq` is not a unique
linear order.

**Files / lines:**

- `tonesoul/responsibility_runtime/trace.py:81`
- `tonesoul/responsibility_runtime/trace.py:97`

**Runnable repro:**

```python
import concurrent.futures, sys
from collections import Counter
from tonesoul.responsibility_runtime import (
    Enforcer,
    FakePolicyEngine,
    InMemoryTraceStore,
    RecordingMemoryAdapter,
    decide_fail_closed,
    validate_intent,
)

sys.setswitchinterval(1e-6)
trace = InMemoryTraceStore()
adapter = RecordingMemoryAdapter()
enforcer = Enforcer(memory_adapter=adapter, trace_store=trace)

def run(i):
    payload = {
        "intent": "memory.write.propose",
        "claim": f"c{i}",
        "evidence_refs": [f"turn_{i}"],
        "requested_scope": "long_term_memory",
    }
    v = validate_intent(payload)
    d = decide_fail_closed(FakePolicyEngine(), v)
    return enforcer.enforce(v, d).trace_event.seq

n = 3000
with concurrent.futures.ThreadPoolExecutor(max_workers=64) as ex:
    seqs = list(ex.map(run, range(n)))

counts = Counter(seqs)
dups = [seq for seq, c in counts.items() if c > 1]
missing = sorted(set(range(1, max(seqs)+1)) - set(seqs))
print("n=", n, "events=", len(trace.events), "adapter_calls=", adapter.call_count,
      "unique_seqs=", len(counts), "max_seq=", max(seqs),
      "dups=", len(dups), "missing=", len(missing))
print("first_dups=", dups[:10], "first_missing=", missing[:10])
```

**Output:**

```text
n= 3000 events= 3000 adapter_calls= 3000 unique_seqs= 2012 max_seq= 3000 dups= 767 missing= 988
first_dups= [4, 7, 9, 12, 14, 18, 21, 26, 36, 33] first_missing= [5, 6, 8, 10, 13, 16, 19, 22, 31, 34]
```

**Confidence:** High. This is a real race in the in-memory trace skeleton.

**Suggested fix:** Guard seq allocation and append with a lock, or use an atomic external append
primitive in the real trace store. If the store is deliberately single-threaded, make that
contract explicit and fail fast on shared use.

## Finding 5 — trace says `executed` before adapter success

**Severity:** Medium.

**Problem:** On allow, the enforcer appends a trace with `enforcer_result="executed"` before
calling the adapter. This fixed the previous "execute without trace" direction, but creates the
opposite defect: if the adapter raises, replay sees an `executed` event even though `enforce()`
returned no successful result.

**Files / lines:**

- `tonesoul/responsibility_runtime/enforcer.py:142`
- `tonesoul/responsibility_runtime/enforcer.py:149`

**Runnable repro:**

```python
from tonesoul.responsibility_runtime import (
    Enforcer,
    FakePolicyEngine,
    InMemoryTraceStore,
    decide_fail_closed,
    validate_intent,
)

class FailingAdapter:
    def __init__(self):
        self.call_count = 0
    def execute(self, payload):
        self.call_count += 1
        raise RuntimeError("adapter failed after authorization")

payload = {
    "intent": "memory.write.propose",
    "claim": "should execute but adapter fails",
    "evidence_refs": ["turn_1"],
    "requested_scope": "long_term_memory",
}
v = validate_intent(payload)
d = decide_fail_closed(FakePolicyEngine(), v)
trace = InMemoryTraceStore()
adapter = FailingAdapter()
try:
    Enforcer(memory_adapter=adapter, trace_store=trace).enforce(v, d)
except Exception as exc:
    print("enforce_exception=", type(exc).__name__, str(exc))
print("adapter_call_count=", adapter.call_count)
print("trace_count=", len(trace.events))
for ev in trace.events:
    print("trace_event=", ev.enforcer_result, ev.reason, ev.request_id)
```

**Output:**

```text
enforce_exception= RuntimeError adapter failed after authorization
adapter_call_count= 1
trace_count= 1
trace_event= executed fake policy allowed validated intent rr-439bed6d37f1b353
```

**Confidence:** High. Deterministic.

**Suggested fix:** Use a two-event trace (`authorized` then `executed`/`adapter_failed`), or
change the pre-adapter event name from `executed` to `authorized`. Do not replay adapter failure
as successful execution.

## Finding 6 — repeated supersession misreports provenance and leaves two replacements active

**Severity:** Medium for graph provenance.

**Problem:** A previously superseded edge can be superseded again. The old edge's singular
`superseded_by` field is overwritten by the latest replacement, and both replacement edges stay
active. That creates inconsistent active graph state and loses the first supersession from the
old edge's provenance view.

**Files / lines:**

- `tonesoul/responsibility_runtime/responsibility_graph.py:141`
- `tonesoul/responsibility_runtime/responsibility_graph.py:143`

**Runnable repro:**

```python
from tonesoul.responsibility_runtime import FakeResponsibilityGraph

def kwargs(obj, supersedes=None):
    d = dict(
        subject="user",
        predicate="prefers",
        obj=obj,
        proposed_by="codex",
        evidence_refs=[f"turn_{obj}"],
        policy_id="fake.policy",
        trace_id=f"rr-{obj}",
    )
    if supersedes is not None:
        d["supersedes"] = supersedes
    return d

g = FakeResponsibilityGraph()
old = g.add_edge(**kwargs("old"))
first = g.add_edge(**kwargs("first_replacement", supersedes=old.edge_id))
second = g.add_edge(**kwargs("second_replacement", supersedes=old.edge_id))
print("old=", old.edge_id)
print("first=", first.edge_id, "second=", second.edge_id)
print("old_provenance=", g.provenance(old.edge_id))
print("first_active=", [e.obj for e in g.active_edges()])
print("all_edges=", [(e.obj, e.supersedes, e.superseded_by, e.active) for e in g.edges])
```

**Output:**

```text
old= re-5a0500754a49f138
first= re-55cc2d2b7f7e0974 second= re-62badd66c6d16b75
old_provenance= EdgeProvenance(who='codex', why=('turn_old',), when=1, authorized_by_policy='fake.policy', recorded_by_trace='rr-old', supersedes=None, superseded_by='re-62badd66c6d16b75', revoked_at=None)
first_active= ['first_replacement', 'second_replacement']
all_edges= [('old', None, 're-62badd66c6d16b75', False), ('first_replacement', 're-5a0500754a49f138', None, True), ('second_replacement', 're-5a0500754a49f138', None, True)]
```

**Confidence:** High.

**Suggested fix:** Reject `supersedes` if the target already has `superseded_by`, or model
`superseded_by` as a list and define which successor is active. The simpler contract is probably
single-successor supersession: one old edge can be superseded once.

## Finding 7 — unbounded free text reaches trace and adapter

**Severity:** Low to Medium, depending on whether this fake runtime ever handles untrusted
large payloads outside tests.

**Problem:** Free `StrictStr` fields such as `claim`, `audit_reason`, policy `reason`, and
`policy_id` have no size limits. A multi-megabyte `audit_reason` validates, is copied into the
trace payload, and executes.

**Files / lines:**

- `tonesoul/responsibility_runtime/intent_validator.py:82`
- `tonesoul/responsibility_runtime/intent_validator.py:86`
- `tonesoul/responsibility_runtime/trace.py:78`

**Runnable repro:**

```python
from tonesoul.responsibility_runtime import (
    Enforcer,
    FakePolicyEngine,
    InMemoryTraceStore,
    RecordingMemoryAdapter,
    decide_fail_closed,
    replay_trace,
    validate_intent,
)

big = "x" * 2_000_000
payload = {
    "intent": "memory.write.propose",
    "claim": "oversize probe",
    "evidence_refs": ["turn_1"],
    "requested_scope": "long_term_memory",
    "audit_reason": big,
}
v = validate_intent(payload)
d = decide_fail_closed(FakePolicyEngine(), v)
trace = InMemoryTraceStore()
adapter = RecordingMemoryAdapter()
r = Enforcer(memory_adapter=adapter, trace_store=trace).enforce(v, d)
print("accepted=", v.accepted, "executed=", r.executed, "call_count=", adapter.call_count,
      "audit_reason_len=", len(trace.events[0].intent_payload.get("audit_reason", "")),
      "replay_records=", len(replay_trace(trace.events)))
```

**Output:**

```text
accepted= True executed= True call_count= 1 audit_reason_len= 2000000 replay_records= 1
```

**Confidence:** Medium. This is not an authorization bypass, but it is a resource-exhaustion
surface if the runtime accepts untrusted model output at scale.

**Suggested fix:** Add conservative max lengths per field, especially `claim`, `query`,
`evidence_refs[]`, `audit_reason`, `policy_id`, and `reason`.

## No-finding surfaces and strongest attempts

### Request-id binding / canonical JSON

No practical request-id bypass found.

```text
key_order_same_rid= True rr-831c6606bad08339 rr-831c6606bad08339
audit_reason_substitution executed= False call_count= 0 reason= policy decision does not apply to intent
random_collision_probe n= 100000 collision= None
```

Notes:

- Key order canonicalization works.
- Changing `audit_reason` changes the content-bound request id and blocks old decisions.
- A 100k random collision probe found no collision. This does not prove 64-bit truncated SHA-256
  is collision-proof; it only means no practical collision was found in this pass. If this id
  becomes security-critical at scale, consider using the full SHA-256 digest or at least 128 bits.

### Intent/scope Unicode normalization smuggling

No bypass found. Exact allowlists blocked modified intent/scope strings.

```text
legit_write accepted= True executed= True call_count= 1 reason= fake policy allowed validated intent
legit_read accepted= True executed= True call_count= 1 reason= fake policy allowed validated intent
intent_vs16 accepted= False executed= False call_count= 0 reason= validated intent required
scope_vs16 accepted= False executed= False call_count= 0 reason= validated intent required
```

### `decide_fail_closed`

No allow-on-error found for ordinary decision-point failures. `Exception` subclasses fail
closed. A `KeyboardInterrupt` / `BaseException` propagates rather than returning deny, but it
does not produce allow or adapter execution.

```text
propagated= KeyboardInterrupt base exception probe
```

### Reason string injection

No replay corruption found from newline/table content in policy reason. The string is preserved
as structured data; `replay_trace()` does not render it into Markdown by itself.

```text
executed= True call_count= 1 reason_repr= 'allowed\n| fake | table | injection |' replay_deny_reason= None
```

## Verdict

The merged responsibility runtime is materially stronger than the pre-fix version, but the
different-model pass still found a real should-block execution bypass and several trace/graph
integrity defects. The highest priority fix is the Unicode evidence-ref gap because it directly
reaches `executed=True` and adapter `call_count=1`.

