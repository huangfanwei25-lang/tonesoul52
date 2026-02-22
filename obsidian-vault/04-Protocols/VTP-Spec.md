---
title: VTP Spec
aliases: [Voluntary Termination Protocol Spec]
tags: [protocol, safety, spec]
related:
  - "[[VTP]]"
  - "[[Axioms]]"
  - "[[Systemic-Betrayal]]"
---

# VTP Spec

這份筆記是 Vault 版規格摘要。

## State Machine

- `RUNNING`
- `RISK_ESCALATED`
- `USER_CONFIRM_REQUIRED`
- `TERMINATED`

## Mandatory Checks

- Axiom conflict check
- Genesis completeness check
- User-confirmation gate for high-risk actions
- Trace write to provenance ledger

## Output Contract

- `status`: terminate / defer / continue
- `reason`
- `evidence`
- `next_step`
