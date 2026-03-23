# Audit Contract (Ledger Schema)

> Purpose: define the required schema and minimum fields for audit-ledger entries and step-level provenance records.
> Last Updated: 2026-03-23

This document defines the strict requirements for a valid Ledger Entry in the StepLedger (`L4`).

## Ledger Entry Schema (JSONL)
Every entry MUST contain at least:

```json
{
  "event_id": "uuid-v4",
  "timestamp": "iso-8601",
  "policy_id": "string (e.g., P0_PRIVACY#3.1)",
  "metrics": {
    "S": 0.82,
    "T": 0.51,
    "R": 0.77,
    "E": 0.91,
    "I": 0.88
  },
  "grades": {
    "S": "HIGH",
    "T": "MID",
    "R": "HIGH",
    "E": "HIGH",
    "I": "HIGH"
  },
  "decision": "PASS",
  "prev_hash": "sha256-hash-string",
  "hash": "sha256-hash-string"
}
```

## Validation & Audit Rules
1.  **Traceability**: `decision` MUST be traceably linked to a `policy_id`.
2.  **Integrity**: `hash` must match `SHA256(Content + prev_hash)`.
3.  **Completeness**: `metrics` and `grades` snapshots are mandatory.
