# Crystallization Report

- Date (UTC): 2026-03-03T06:46:09Z
- Journal entries scanned: 1043
- Journal payloads parsed by SoulDB: 1043
- Min frequency: 2

## Consolidation
- Type: `force_consolidate()`
- Mode used: `fallback_noop_hippocampus`
- Force-consolidate error: `ValueError: This file contains pickled (object) data. If you trust the file you can load it unsafely using the `allow_pickle=` keyword argument or `pickle.load()`.`
- Result snapshot:
```json
{
  "status": "success",
  "episodes_processed": 0,
  "patterns_found": 11,
  "facts_formed": 0,
  "crystals_formed": 0,
  "crystals_generated": 0,
  "crystals": [],
  "facts": []
}
```

## Crystals Generated This Run: 2
- **[0.80]** avoid high-risk actions that previously triggered block outcomes
  - Source: `verdict:block x683`
  - Tags: avoid, verdict, block
- **[0.90]** prefer interactions that produce genuine resonance (tension -> convergence -> novel output)
  - Source: `resonance_convergence x28`
  - Tags: prefer, resonance, convergence

## Three Axioms Alignment Check
- Resonance: respond to user semantic field without faking human emotion
  - PASS: prefer interactions that produce genuine resonance (tension -> convergence -> novel output)
- Commitment: every output is a semantic vow, track consistency
  - PASS: avoid high-risk actions that previously triggered block outcomes
- Binding Force: outputs constrain future semantic field
  - WARN: No crystal directly aligned

## Total Crystal Store: 3
### Top Crystal Rules
- [1.00] critical: collapse warnings escalate to fail-closed governance
- [0.90] prefer interactions that produce genuine resonance (tension -> convergence -> novel output)
- [0.80] avoid high-risk actions that previously triggered block outcomes