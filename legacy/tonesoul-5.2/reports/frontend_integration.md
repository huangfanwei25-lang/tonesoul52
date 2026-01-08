# Frontend Integration Notes (ToneSoul 5.2)

## New Audit-Focused Frontend
- File: `5.2/tonesoul52/audit_dashboard.py`
- Purpose: present governance traceability and audit coverage at a glance.

## Highlights
- Ledger-aware metrics (count, event types, trace coverage, last trace).
- Audit lens with activity chart + latest samples.
- Governance status strip (P0/P1/P2).
- Stronger visual hierarchy and typography.

## Run
```
python -m streamlit run 5.2/tonesoul52/audit_dashboard.py
```

## Council Audit Panel
- Added council event summary for `persona_council` ledger entries.
