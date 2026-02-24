# Elisa x ToneSoul Governance Integration Plan (Swarm Multi-Persona)

Date: 2026-02-22  
Scope: Define an executable integration blueprint between Elisa IDE and ToneSoul governance runtime.

## 0. Mission

Build an integration that keeps Elisa IDE productive while preserving ToneSoul's governance guarantees:

- Accountability before convenience
- Fail-closed by default
- Traceable decisions (not only final outputs)
- Clear public/private boundary (Dual-Track policy)

## 1. Goals and Non-Goals

Goals

- Route Elisa IDE interactions through existing ToneSoul web APIs (`/api/chat`, `/api/consent`, `/api/session-report`, `/api/backend-health`).
- Use `council_mode` and `perspective_config` as first-class IDE controls for deliberation depth.
- Preserve same-origin + mock fallback behavior for resilience on Vercel.
- Expose governance readiness signals (7D/SDH/dual-track artifacts) to IDE operators.

Non-Goals

- No exposure of private-repo internals (Memory Consolidator prompts, real threshold coefficients, deep red-team payload dictionaries, autopatching keys).
- No bypass path that skips existing policy gates, consent flow, or audit trail.
- No hard coupling to one provider model; governance layer remains provider-agnostic.

## 2. Swarm Findings (4 Perspectives)

### 2.1 Architect Perspective

- Keep Elisa as client/orchestrator; keep ToneSoul as governance execution plane.
- Treat web API layer as the only contract boundary for IDE integration.
- Reuse existing transport contracts and route validations before adding new endpoints.

### 2.2 Guardian/Security Perspective

- Main attack surfaces: prompt injection, code/secret exfiltration, plugin supply chain, tool-permission abuse, non-repudiation gaps.
- Required controls: preflight checks, policy gate, consent gate, append-only audit chain.
- Fail-closed rules must downgrade to read-only/blocked mode when policy/audit layers are unavailable.

### 2.3 IDE/Product Perspective

Core scenarios:

1. Refactor: auto-trigger council on cross-file/high-tension edits.
2. Test-fix: trigger council after repeated failure or CI red gate.
3. Security-review: trigger guardian-heavy council before merge/deploy.

### 2.4 Delivery Perspective

- 4-week rollout (P0-P3) is feasible if tied to existing scripts and CI gates:
  - `scripts/verify_web_api.py`
  - `scripts/verify_vercel_preflight.py`
  - web_api_smoke CI gate

## 3. Architecture Boundary

## 3.1 Responsibility Split

- Elisa IDE:
  - Collect user intent, session context, selected files, and desired deliberation mode.
  - Display governance decisions and actionable next steps.
- ToneSoul Web Gateway (Next API routes):
  - Validate payload schema, enforce runtime config rules, handle transport retries/fallback.
  - Normalize `council_mode` and pass `perspective_config`.
- ToneSoul Backend:
  - Run deliberation, gate output, record session artifacts, generate session reports.
- Governance Artifact Plane:
  - CI/status outputs for readiness visibility (7D/SDH/dual-track).

## 3.2 Integration Sequence (Recommended)

1. `POST /api/consent` before active IDE session.
2. `POST /api/chat` with:
   - `message`, `history`
   - optional `council_mode` (`rules|hybrid|full_llm`)
   - optional `perspective_config` (overrides `council_mode`)
3. Optional `POST /api/session-report` on checkpoint/commit/PR handoff.
4. `GET /api/backend-health` for runtime readiness.

## 4. API Contract v0 (Elisa-facing)

- `POST /api/chat`
  - Must accept structured IDE context and return governance-aware response object.
  - In same-origin mode, transport/backend HTTP errors should degrade to `mock_fallback` payload (not opaque 5xx for IDE user flows).
- `POST /api/consent`, `DELETE /api/consent/{session_id}`
  - Must stay explicit; no silent consent assumptions.
- `POST /api/session-report`
  - Used for end-of-session governance summary and operator traceability.
- `GET /api/backend-health`
  - Must expose `backend_mode` and health shape expected by verification scripts.

Recommended addition (Phase P1)

- `GET /api/governance/status`
  - Aggregate latest 7D/SDH/dual-track readiness artifact snapshot for IDE panel.

## 5. Governance and Security Controls

Preflight Gate

- Endpoint health + HTTPS policy + environment sanity checks.
- Explicit check that integration does not regress into insecure/localhost backend config.

Policy Gate

- Tool and action allowlist by capability tier (read, analyze, modify, execute).
- Reject out-of-scope tool requests early.

Consent Gate

- Mandatory consent state before persistent session actions.
- Elevated actions (write/exec/external) require explicit user confirmation.

Audit Trail

- Every significant action must be attributable to user, session, and decision context.
- Keep tamper-evident, append-only trace semantics.

Fail-Closed Rules

- If policy/audit cannot be evaluated, deny privileged execution.
- If integration signal is unknown, downgrade to safe mode (read-only or blocked path).

## 6. Four-Week Delivery Plan (P0-P3)

P0: Handshake and Baseline

- Define Elisa payload profile for existing routes.
- Extend/validate smoke flow using `scripts/verify_web_api.py`.
- Acceptance: same-origin deployment passes baseline chat/consent/session-report flows.

P1: Preflight + Status Surface

- Extend preflight checks for Elisa integration assumptions.
- Add governance readiness status endpoint/panel contract.
- Acceptance: `verify_vercel_preflight` includes Elisa checks and passes in CI.

P2: CI Gate Enforcement

- Include Elisa scenario in web API smoke gate.
- Ensure blocking behavior on contract regressions.
- Acceptance: CI fails closed when Elisa governance contract breaks.

P3: Operational Hardening

- Finalize docs, runbooks, rollback playbook, and release checklist.
- Acceptance: one-command verification path and reproducible evidence artifacts.

## 7. Release Acceptance Checklist

- [ ] Same-origin health returns expected shape and mode.
- [ ] IDE chat path supports both `council_mode` and `perspective_config`.
- [ ] Consent lifecycle is enforced and auditable.
- [ ] Session report pipeline is callable and traceable.
- [ ] CI has a blocking Elisa integration smoke step.
- [ ] Dual-track boundary is explicitly documented in integration docs.

## 8. Open Questions

- Exact Elisa plugin protocol shape (session/file context envelope).
- Token model for least-privilege and rotation cadence.
- Whether governance status endpoint should be cached or real-time.
- Which actions require mandatory human confirmation by default.

## 9. Immediate Next Step

Execute P0 first: define Elisa payload profile + add contract tests + wire into `verify_web_api.py`.

## 10. Execution Status Update (2026-02-24)

- [x] P0: payload profile + route contract tests + `verify_web_api.py --elisa-scenario`
- [x] P1: preflight Elisa checks + governance status surface (`GET /api/governance-status`)
- [x] P2: CI blocking smoke includes Elisa scenario
- [x] P3: operational hardening docs published
  - `docs/plans/elisa_tonesoul_operational_runbook_2026-02-24.md`
