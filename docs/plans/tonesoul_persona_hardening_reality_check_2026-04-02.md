# ToneSoul Persona Hardening Reality Check (2026-04-02)

> Purpose: decide whether `tonesoul/tonebridge/personas.py::build_hardened_prompt()` is now safe for bounded working-style adoption.
> Authority: implementation planning note. Does not outrank runtime code, tests, or the live prompt-adoption matrix.

---

## Verdict

`defer_again`

This surface should remain deferred for now.

---

## Why It Is Still Deferred

### 1. It is voice-defining, not coordination-facing

`build_hardened_prompt()` is part of the `persona_and_voice` family.

Its job is to lock:

- resonance mode
- persona mode
- anti-loop persona behavior
- internal-monologue response shape

That is a much more voice-sensitive surface than the earlier working-style consumers.

### 2. There is no visible working-style playbook input path

Current signature:

```python
build_hardened_prompt(
    resonance_state: str,
    trajectory_context: Optional[list] = None,
    loop_detected: bool = False,
) -> str
```

Unlike `shared_edit_preflight`, this surface does not already receive:

- session-start bundle
- working-style playbook
- import posture
- receiver ladder

So "just adding working-style guidance" would first require a new cross-layer input path.

### 3. The ripple radius is larger than the bounded gain

`build_navigation_prompt()` calls `build_hardened_prompt()` directly.

Any new parameter or injected structure here would affect:

- persona hardening
- navigation prompt composition
- existing ToneBridge persona tests

That is no longer a small wave-2 consumer. It becomes a mini family review.

---

## What This Means

The real shortest board is not:

`rewrite persona hardening wording`

It is:

`design a cleaner tool / permission / hook chain for the next non-successor bucket`

So this surface stays explicitly deferred.

---

## Safe Conclusion

Keep:

- `shared_edit_preflight` as the real wave-2 working-style consumer
- `build_hardened_prompt()` in deferred status

Do not:

- thread working-style continuity into persona voice just because the file is high-frequency
- reopen the broader prompt-topology bucket under a "small adoption" label

---

## Successor Note

If a later agent wants to revisit this surface, the prerequisite is:

`one bounded, explicit working-style input path into ToneBridge persona composition`

Without that, further edits here are more likely to flatten voice than improve continuity.
