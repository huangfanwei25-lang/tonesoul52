# API Specification (Unified Web + Backend)

Last updated: 2026-02-09

## Goal

Define one shared contract between:
- Web routes (`apps/web/src/app/api/*/route.ts`)
- Backend service (`apps/api/server.py`)

The web layer is proxy-first, backend-first by default.

---

## Base URLs

- Backend (Flask): `http://127.0.0.1:5000`
- Web (Next API routes): `http://127.0.0.1:3000/api/*`

Runtime environment:
- `TONESOUL_BACKEND_URL` controls where Next API routes forward requests.
- `TONESOUL_ENABLE_CHAT_MOCK_FALLBACK=1` explicitly enables `/api/chat` transport fallback mock mode.
- `TONESOUL_COUNCIL_MODE` controls backend council perspective config when request does not override it.
  - Supported values: `rules`, `hybrid`, `full_llm`
  - Default: `hybrid`

---

## Endpoints

### `GET /api/health`
- Backend only.
- Response:
  - `status: "ok"`
  - `version: string`

### `POST /api/conversation`
- Request:
  - `session_id: string | null`
- Response:
  - `success: boolean`
  - `conversation_id: string`
  - `session_id: string | null`
  - `created_at: ISO timestamp`

### `POST /api/consent`
- Request:
  - `consent_type: string`
  - `session_id?: string`
- Response:
  - `success: boolean`
  - `session_id: string`
  - `consent_type: string`
  - `consent_version: string`
  - `timestamp: ISO timestamp`

### `DELETE /api/consent/{session_id}`
- Response:
  - `success: boolean`
  - `message: string`
  - `session_id: string`
  - `timestamp?: ISO timestamp`

### `POST /api/chat`
- Request:
  - `conversation_id?: string`
  - `message: string`
  - `history?: array`
  - `full_analysis?: boolean`
  - `council_mode?: "rules" | "hybrid" | "full_llm"`
    - compatibility: `"rules_only"` is accepted and normalized to `"rules"`
  - `perspective_config?: object`
    - optional explicit per-perspective config
    - when provided, backend uses this config and ignores `council_mode`
    - values must be objects, e.g. `{ "guardian": { "mode": "rules" } }`
- Response (backend path):
  - `response: string`
  - `verdict?: object`
    - `verdict.transcript.council_mode_observability?: object`
      - `source: "request_perspective_config" | "explicit_perspectives" | "env_default"`
      - `mode: "rules" | "hybrid" | "full_llm" | "custom" | null`
  - `tonebridge?: object`
  - `inner_reasoning?: string`
  - `intervention_strategy?: object`
  - `internal_monologue?: string`
  - `persona_mode?: string`
  - `trajectory_analysis?: object`
  - `self_commits?: array`
  - `ruptures?: array`
  - `emergent_values?: array`
- Response (explicit mock fallback path, opt-in):
  - `response: string`
  - `deliberation: object`
  - `backend_mode: "mock_fallback"`
  - `fallback_reason: "transport_failure"`
- Error behavior:
  - transport failure + fallback disabled: HTTP `502`
    - payload includes `error: "Backend unavailable"`
  - Vercel runtime + missing/localhost backend config: HTTP `503`
    - payload includes `error: "Backend configuration invalid for Vercel runtime"`

### `POST /api/validate`
- Request:
  - `draft_output?: string`
  - `user_intent?: string`
  - `context?: object`
- `context` supports optional safety seed:
  - `escape_valve_failures?: string[]`
  - Purpose: seed recent failure history for request-local escape valve evaluation.
  - Security model:
    - default behavior: untrusted client seeds are ignored
    - trusted mode: set `TONESOUL_ALLOW_ESCAPE_SEED=1` on backend
    - trusted mode input cap: API trims `escape_valve_failures` to latest 50 entries
    - runtime cap: Council uses latest 20 seeded failures
  - Note: seed history is request-scoped only; it must not persist across requests.
- `context` supports optional VTP controls:
  - `vtp_force_trigger?: boolean`
    - testing/deep-safety flag to force VTP high-risk path evaluation
  - `vtp_axiom_conflict?: boolean`
    - signal unresolved axiom conflict at request boundary
  - `vtp_refusal_to_compromise?: boolean`
    - signal explicit refusal-to-compromise condition
  - `vtp_user_confirmed?: boolean`
    - explicit user authorization for VTP termination path
  - Security model:
    - default behavior: VTP context flags from external API payload are ignored
    - trusted mode: set `TONESOUL_ALLOW_VTP_CONTEXT=1` on backend
    - invalid flag type returns HTTP 400 (for example `"vtp_force_trigger": "yes"`)
- Response:
  - `verdict: "approve" | "refine" | "declare_stance" | "block"`
  - `summary: string`
  - `uncertainty_level?: number`
  - `uncertainty_band?: "low" | "medium" | "high"`
  - `uncertainty_reasons?: string[]`
  - `benevolence_audit?: object`
  - `transcript?: object`
  - Optional escape valve payload when triggered:
    - `transcript.escape_valve.triggered: true`
    - `transcript.escape_valve.reason: string`
    - `transcript.escape_valve.retry_count: number`
    - `transcript.escape_valve.failure_history: string[]`
    - `transcript.escape_valve_semantic: "honest_failure"`
  - Observability payload (when benevolence intercept path runs):
    - `transcript.escape_valve_observability.seed_trusted: boolean`
    - `transcript.escape_valve_observability.seed_entries_requested: number`
    - `transcript.escape_valve_observability.seed_entries_used: number`
    - `transcript.escape_valve_observability.seed_ignored_reason?: "untrusted_seed" | "invalid_format"`
    - `transcript.escape_valve_observability.triggered: boolean`
    - `transcript.escape_valve_observability.trigger_reason?: string`
  - VTP payload:
    - `transcript.vtp.status: "continue" | "defer" | "terminate"`
    - `transcript.vtp.reason: string`
    - `transcript.vtp.evidence: string[]`
    - `transcript.vtp.next_step: string`
    - `transcript.vtp.triggered: boolean`
    - `transcript.vtp.requires_user_confirmation: boolean`
    - `transcript.vtp.confession?: { phase, required, summary, trigger_evidence }`
    - `transcript.vtp_context_trusted?: boolean`
    - `transcript.vtp_context_ignored_reason?: "untrusted_vtp_context"`

### `POST /api/session-report`
- Request:
  - `history: array`
- Response:
  - `success: boolean`
  - `report: object`

---

## Web Route Behavior Rules

For Next API route handlers:

1. Use backend-first forwarding.
2. Read `TONESOUL_BACKEND_URL` dynamically per request.
3. `/api/chat` may use `mock_fallback` only on transport failures and only when `TONESOUL_ENABLE_CHAT_MOCK_FALLBACK=1` is set.
4. If backend returns non-JSON, return:
   - HTTP `502`
   - payload `{ "error": "Backend returned invalid JSON", "backend_status": <status> }`

This avoids false positives where backend errors are masked by fallback success.

---

## Execution Mode Flags (Frontend)

### Chat
- `NEXT_PUBLIC_CHAT_EXECUTION_MODE=backend|legacy_provider`
- `NEXT_PUBLIC_ENABLE_PROVIDER_FALLBACK=0|1`
- Backward compatibility:
  - `NEXT_PUBLIC_BACKEND_CHAT_FIRST=0` maps to `legacy_provider`

### Session Report
- `NEXT_PUBLIC_REPORT_EXECUTION_MODE=backend|provider`
- `NEXT_PUBLIC_REPORT_PROVIDER_FALLBACK=0|1`

---

## Verification Commands

### Backend contract tests
```powershell
pytest tests/test_api_server_contract.py -q
```

### Web route invalid JSON guard tests
```powershell
npm --prefix apps/web run test -- src/__tests__/apiRoutes.invalidJson.test.ts
```

### Integrated web+backend smoke
```powershell
python scripts/verify_web_api.py --web-base http://127.0.0.1:3000 --api-base http://127.0.0.1:5000 --require-backend --check-council-modes --timeout 40
```

### Vercel preflight guard
```powershell
python scripts/verify_vercel_preflight.py --strict --probe-health
```

---

## Known Operational Risks

- If an old backend instance still occupies `:5000`, smoke results can be misleading.
- Session/report fallback should be treated as degraded mode, not production success.
- Keep `jieba` installed in local backend environments to avoid warning-only degraded paths.
