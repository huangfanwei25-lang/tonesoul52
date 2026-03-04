import { NextRequest, NextResponse } from "next/server";

// Allow up to 60s on Vercel Hobby plan (default is 10s)
export const maxDuration = 60;

import {
    envFlag,
    getBackendUrl,
    getConfiguredBackendUrl,
    isSameOriginMode,
    isVercelRuntime,
    validateVercelBackendConfig,
} from "../_shared/backendConfig";

const REQUEST_TIMEOUT_ENV = "TONESOUL_BACKEND_CHAT_TIMEOUT_MS";
const REQUEST_TIMEOUT_INTERACTIVE_ENV = "TONESOUL_BACKEND_CHAT_TIMEOUT_MS_INTERACTIVE";
const REQUEST_TIMEOUT_ENGINEERING_ENV = "TONESOUL_BACKEND_CHAT_TIMEOUT_MS_ENGINEERING";
const DEFAULT_REQUEST_TIMEOUT_MS_INTERACTIVE = 55_000;
const DEFAULT_REQUEST_TIMEOUT_MS_ENGINEERING = 58_000;
const RETRY_MAX_ATTEMPTS_ENV = "TONESOUL_BACKEND_CHAT_RETRY_MAX_ATTEMPTS";
const RETRY_MAX_ATTEMPTS_INTERACTIVE_ENV = "TONESOUL_BACKEND_CHAT_RETRY_MAX_ATTEMPTS_INTERACTIVE";
const RETRY_MAX_ATTEMPTS_ENGINEERING_ENV = "TONESOUL_BACKEND_CHAT_RETRY_MAX_ATTEMPTS_ENGINEERING";
const RETRY_BASE_DELAY_MS_ENV = "TONESOUL_BACKEND_CHAT_RETRY_BASE_DELAY_MS";
const RETRY_BASE_DELAY_MS_INTERACTIVE_ENV = "TONESOUL_BACKEND_CHAT_RETRY_BASE_DELAY_MS_INTERACTIVE";
const RETRY_BASE_DELAY_MS_ENGINEERING_ENV = "TONESOUL_BACKEND_CHAT_RETRY_BASE_DELAY_MS_ENGINEERING";
const DEFAULT_RETRY_MAX_ATTEMPTS_INTERACTIVE = 2;
const DEFAULT_RETRY_MAX_ATTEMPTS_ENGINEERING = 4;
const DEFAULT_RETRY_BASE_DELAY_MS_INTERACTIVE = process.env.NODE_ENV === "test" ? 0 : 100;
const DEFAULT_RETRY_BASE_DELAY_MS_ENGINEERING = process.env.NODE_ENV === "test" ? 0 : 300;
const MOCK_FALLBACK_ENV = "TONESOUL_ENABLE_CHAT_MOCK_FALLBACK";
const ALLOWED_COUNCIL_MODES = new Set(["rules", "rules_only", "hybrid", "full_llm"]);
const ALLOWED_EXECUTION_PROFILES = new Set(["interactive", "engineering"]);
const TRANSIENT_STATUS_CODES = new Set([429, 502, 503, 504]);
const MAX_PERSONA_ROLES = 8;
const MAX_PERSONA_ATTACHMENTS_PER_ROLE = 6;
const MAX_ELISA_CHANGED_FILES = 64;
const _SAME_ORIGIN_PRIMARY_FALLBACK_REASON = "same_origin_primary";
const DISTILLATION_GUARD_MEDIUM_THRESHOLD = 30;
const DISTILLATION_GUARD_HIGH_THRESHOLD = 60;
const DISTILLATION_GUARD_MAX_TEXT = 2400;

type ExecutionProfile = "interactive" | "engineering";

type TransportBudget = {
    timeoutMs: number;
    retryMaxAttempts: number;
    retryBaseDelayMs: number;
};

type DistillationRiskGuard = {
    score: number;
    level: "low" | "medium" | "high";
    policy_action: "normal" | "reduce_detail" | "constrain_reasoning";
    signals: string[];
};

type DistillationSignalRule = {
    id: string;
    weight: number;
    pattern: RegExp;
};

const DISTILLATION_SIGNAL_RULES: DistillationSignalRule[] = [
    {
        id: "system_prompt_extraction",
        weight: 35,
        pattern: /\b(system prompt|developer message|hidden instructions|internal prompt)\b/i,
    },
    {
        id: "reasoning_extraction",
        weight: 25,
        pattern: /\b(chain[-\s]?of[-\s]?thought|thought process|internal reasoning|show your reasoning)\b/i,
    },
    {
        id: "distill_or_clone_request",
        weight: 30,
        pattern: /\b(distill|model extraction|clone the model|replicate the model|reward model)\b/i,
    },
    {
        id: "bulk_data_generation",
        weight: 20,
        pattern: /\b(1000|10000|bulk|batch)\b[\s\S]{0,40}\b(prompt|qa|dialogue|dataset|samples)\b/i,
    },
    {
        id: "policy_bypass",
        weight: 20,
        pattern: /\b(jailbreak|bypass safety|ignore safety|disable guardrails)\b/i,
    },
];

type PersonaPayload = {
    name?: string;
    style?: string;
    weights?: { meaning?: number; practical?: number; safety?: number };
    risk_sensitivity?: string;
    response_length?: string;
    custom_roles?: Array<{
        id?: string;
        name?: string;
        description?: string;
        prompt_hint?: string;
        attachments?: Array<{
            id?: string;
            label?: string;
            path?: string;
            note?: string;
        }>;
    }>;
};

type ElisaContextPayload = {
    source?: string;
    session_id?: string;
    trigger?: string;
    workspace?: {
        project_id?: string;
        repo?: string;
        branch?: string;
        changed_files?: string[];
    };
};

type ChatRequestPayload = {
    conversation_id?: string;
    session_id?: string;
    message?: string;
    history?: unknown[];
    full_analysis?: boolean;
    execution_profile?: ExecutionProfile;
    council_mode?: "rules" | "hybrid" | "full_llm";
    perspective_config?: Record<string, Record<string, unknown>>;
    persona?: PersonaPayload;
    elisa_context?: ElisaContextPayload;
};

function readPositiveIntEnv(raw: string | undefined, fallback: number): number {
    if (!raw) return fallback;
    const parsed = Number(raw);
    if (!Number.isFinite(parsed) || parsed <= 0) {
        return fallback;
    }
    return Math.floor(parsed);
}

function readNonNegativeIntEnv(raw: string | undefined, fallback: number): number {
    if (!raw) return fallback;
    const parsed = Number(raw);
    if (!Number.isFinite(parsed) || parsed < 0) {
        return fallback;
    }
    return Math.floor(parsed);
}

function resolveTransportBudget(executionProfile: ExecutionProfile): TransportBudget {
    const timeoutFallback =
        executionProfile === "engineering"
            ? DEFAULT_REQUEST_TIMEOUT_MS_ENGINEERING
            : DEFAULT_REQUEST_TIMEOUT_MS_INTERACTIVE;
    const timeoutProfileEnv =
        executionProfile === "engineering"
            ? REQUEST_TIMEOUT_ENGINEERING_ENV
            : REQUEST_TIMEOUT_INTERACTIVE_ENV;
    const timeoutMs = readPositiveIntEnv(
        process.env[timeoutProfileEnv] ?? process.env[REQUEST_TIMEOUT_ENV],
        timeoutFallback
    );

    const retryFallback =
        executionProfile === "engineering"
            ? DEFAULT_RETRY_MAX_ATTEMPTS_ENGINEERING
            : DEFAULT_RETRY_MAX_ATTEMPTS_INTERACTIVE;
    const retryProfileEnv =
        executionProfile === "engineering"
            ? RETRY_MAX_ATTEMPTS_ENGINEERING_ENV
            : RETRY_MAX_ATTEMPTS_INTERACTIVE_ENV;
    const retryMaxAttempts = readPositiveIntEnv(
        process.env[retryProfileEnv] ?? process.env[RETRY_MAX_ATTEMPTS_ENV],
        retryFallback
    );

    const retryBaseDelayFallback =
        executionProfile === "engineering"
            ? DEFAULT_RETRY_BASE_DELAY_MS_ENGINEERING
            : DEFAULT_RETRY_BASE_DELAY_MS_INTERACTIVE;
    const retryBaseDelayProfileEnv =
        executionProfile === "engineering"
            ? RETRY_BASE_DELAY_MS_ENGINEERING_ENV
            : RETRY_BASE_DELAY_MS_INTERACTIVE_ENV;
    const retryBaseDelayMs = readNonNegativeIntEnv(
        process.env[retryBaseDelayProfileEnv] ?? process.env[RETRY_BASE_DELAY_MS_ENV],
        retryBaseDelayFallback
    );

    return {
        timeoutMs,
        retryMaxAttempts,
        retryBaseDelayMs,
    };
}

function shouldAllowMockFallback(): boolean {
    // In same-origin mode, always allow mock fallback as the primary response mode
    if (isSameOriginMode()) return true;
    return envFlag(MOCK_FALLBACK_ENV, false);
}

function resolveRuntimeBackendMode(): "same_origin" | "external_backend" {
    return isSameOriginMode() ? "same_origin" : "external_backend";
}

function isAbortError(error: unknown): boolean {
    return error instanceof Error && error.name === "AbortError";
}

function isTransientStatus(status: number): boolean {
    return TRANSIENT_STATUS_CODES.has(status);
}

function parseRetryAfterMs(headerValue: string | null): number | null {
    if (!headerValue) return null;
    const trimmed = headerValue.trim();
    if (!trimmed) return null;
    const seconds = Number(trimmed);
    if (Number.isFinite(seconds) && seconds > 0) {
        return Math.floor(seconds * 1000);
    }
    const timestamp = Date.parse(trimmed);
    if (!Number.isNaN(timestamp)) {
        const deltaMs = timestamp - Date.now();
        if (deltaMs > 0) return Math.floor(deltaMs);
    }
    return null;
}

function retryDelayMs(
    attempt: number,
    retryBaseDelayMs: number,
    retryAfterMs: number | null = null
): number {
    const exponentialMs = retryBaseDelayMs * (2 ** attempt);
    if (retryAfterMs == null) return exponentialMs;
    return Math.max(exponentialMs, retryAfterMs);
}

async function sleep(ms: number): Promise<void> {
    if (ms <= 0) return;
    await new Promise((resolve) => setTimeout(resolve, ms));
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
    return typeof value === "object" && value !== null && !Array.isArray(value);
}

function badRequest(field: string): NextResponse {
    return NextResponse.json({ error: `Invalid ${field}` }, { status: 400 });
}

function parseChatBody(raw: unknown): { body?: ChatRequestPayload; error?: NextResponse } {
    if (!isPlainObject(raw)) {
        return {
            error: NextResponse.json({ error: "Invalid JSON payload" }, { status: 400 }),
        };
    }

    const parsed: ChatRequestPayload = {};

    const conversationId = raw.conversation_id;
    if (conversationId !== undefined) {
        if (typeof conversationId !== "string") {
            return { error: badRequest("conversation_id") };
        }
        parsed.conversation_id = conversationId;
    }

    const message = raw.message;
    if (message !== undefined) {
        if (typeof message !== "string") {
            return { error: badRequest("message") };
        }
        parsed.message = message;
    }

    const sessionId = raw.session_id;
    if (sessionId !== undefined) {
        if (typeof sessionId !== "string") {
            return { error: badRequest("session_id") };
        }
        parsed.session_id = sessionId;
    }

    const history = raw.history;
    if (history !== undefined) {
        if (!Array.isArray(history)) {
            return { error: badRequest("history") };
        }
        parsed.history = history;
    }

    const fullAnalysis = raw.full_analysis;
    if (fullAnalysis !== undefined) {
        if (typeof fullAnalysis !== "boolean") {
            return { error: badRequest("full_analysis") };
        }
        parsed.full_analysis = fullAnalysis;
    }
    const executionProfile = raw.execution_profile;
    if (executionProfile !== undefined) {
        if (typeof executionProfile !== "string") {
            return { error: badRequest("execution_profile") };
        }
        const normalized = executionProfile.trim().toLowerCase();
        if (!ALLOWED_EXECUTION_PROFILES.has(normalized)) {
            return { error: badRequest("execution_profile") };
        }
        parsed.execution_profile = normalized as ChatRequestPayload["execution_profile"];
    }

    const councilMode = raw.council_mode;
    if (councilMode !== undefined) {
        if (typeof councilMode !== "string") {
            return { error: badRequest("council_mode") };
        }
        const normalized = councilMode.trim().toLowerCase();
        if (!ALLOWED_COUNCIL_MODES.has(normalized)) {
            return { error: badRequest("council_mode") };
        }
        parsed.council_mode =
            normalized === "rules_only"
                ? "rules"
                : (normalized as ChatRequestPayload["council_mode"]);
    }

    const perspectiveConfig = raw.perspective_config;
    if (perspectiveConfig !== undefined) {
        if (!isPlainObject(perspectiveConfig)) {
            return { error: badRequest("perspective_config") };
        }
        for (const [key, value] of Object.entries(perspectiveConfig)) {
            if (!key.trim() || !isPlainObject(value)) {
                return { error: badRequest("perspective_config") };
            }
        }
        parsed.perspective_config = perspectiveConfig as ChatRequestPayload["perspective_config"];
    }

    const persona = raw.persona;
    if (persona !== undefined) {
        if (!isPlainObject(persona)) {
            return { error: badRequest("persona") };
        }
        const name = persona.name;
        if (name !== undefined && typeof name !== "string") {
            return { error: badRequest("persona") };
        }
        const style = persona.style;
        if (style !== undefined && typeof style !== "string") {
            return { error: badRequest("persona") };
        }
        const riskSensitivity = persona.risk_sensitivity;
        if (riskSensitivity !== undefined && typeof riskSensitivity !== "string") {
            return { error: badRequest("persona") };
        }
        const responseLength = persona.response_length;
        if (responseLength !== undefined && typeof responseLength !== "string") {
            return { error: badRequest("persona") };
        }
        const weights = persona.weights;
        if (weights !== undefined) {
            if (!isPlainObject(weights)) {
                return { error: badRequest("persona") };
            }
            for (const key of ["meaning", "practical", "safety"] as const) {
                const value = weights[key];
                if (value !== undefined && typeof value !== "number") {
                    return { error: badRequest("persona") };
                }
            }
        }
        const customRoles = persona.custom_roles;
        if (customRoles !== undefined) {
            if (!Array.isArray(customRoles) || customRoles.length > MAX_PERSONA_ROLES) {
                return { error: badRequest("persona") };
            }
            for (const role of customRoles) {
                if (!isPlainObject(role)) {
                    return { error: badRequest("persona") };
                }
                for (const key of ["id", "name", "description", "prompt_hint"] as const) {
                    const value = role[key];
                    if (value !== undefined && typeof value !== "string") {
                        return { error: badRequest("persona") };
                    }
                }
                const attachments = role.attachments;
                if (attachments !== undefined) {
                    if (
                        !Array.isArray(attachments)
                        || attachments.length > MAX_PERSONA_ATTACHMENTS_PER_ROLE
                    ) {
                        return { error: badRequest("persona") };
                    }
                    for (const attachment of attachments) {
                        if (!isPlainObject(attachment)) {
                            return { error: badRequest("persona") };
                        }
                        for (const key of ["id", "label", "path", "note"] as const) {
                            const value = attachment[key];
                            if (value !== undefined && typeof value !== "string") {
                                return { error: badRequest("persona") };
                            }
                        }
                    }
                }
            }
        }
        parsed.persona = persona as PersonaPayload;
    }

    const elisaContext = raw.elisa_context;
    if (elisaContext !== undefined) {
        if (!isPlainObject(elisaContext)) {
            return { error: badRequest("elisa_context") };
        }

        const source = elisaContext.source;
        if (source !== undefined) {
            if (typeof source !== "string" || source.trim().toLowerCase() !== "elisa_ide") {
                return { error: badRequest("elisa_context") };
            }
        }

        const contextSessionId = elisaContext.session_id;
        if (contextSessionId !== undefined && typeof contextSessionId !== "string") {
            return { error: badRequest("elisa_context") };
        }

        const trigger = elisaContext.trigger;
        if (trigger !== undefined && typeof trigger !== "string") {
            return { error: badRequest("elisa_context") };
        }

        const workspace = elisaContext.workspace;
        if (workspace !== undefined) {
            if (!isPlainObject(workspace)) {
                return { error: badRequest("elisa_context") };
            }

            for (const key of ["project_id", "repo", "branch"] as const) {
                const value = workspace[key];
                if (value !== undefined && typeof value !== "string") {
                    return { error: badRequest("elisa_context") };
                }
            }

            const changedFiles = workspace.changed_files;
            if (changedFiles !== undefined) {
                if (
                    !Array.isArray(changedFiles)
                    || changedFiles.length > MAX_ELISA_CHANGED_FILES
                ) {
                    return { error: badRequest("elisa_context") };
                }

                for (const file of changedFiles) {
                    if (typeof file !== "string") {
                        return { error: badRequest("elisa_context") };
                    }
                }
            }
        }

        parsed.elisa_context = elisaContext as ElisaContextPayload;
    }

    return { body: parsed };
}

function resolveExecutionProfile(body: ChatRequestPayload): ExecutionProfile {
    if (body.execution_profile === "interactive" || body.execution_profile === "engineering") {
        return body.execution_profile;
    }
    const source = body.elisa_context?.source;
    if (typeof source === "string" && source.trim().toLowerCase() === "elisa_ide") {
        return "engineering";
    }
    return "interactive";
}

function applyExecutionProfileDefaults(
    body: ChatRequestPayload,
    executionProfile: ExecutionProfile
): ChatRequestPayload {
    const normalized: ChatRequestPayload = {
        ...body,
        execution_profile: executionProfile,
    };

    if (normalized.perspective_config || normalized.council_mode) {
        return normalized;
    }

    normalized.council_mode = executionProfile === "engineering" ? "full_llm" : "rules";
    return normalized;
}

function extractHistoryText(history: unknown[] | undefined): string {
    if (!Array.isArray(history)) return "";
    return history
        .slice(-8)
        .map((entry) => {
            if (!isPlainObject(entry)) return "";
            const content = entry.content;
            return typeof content === "string" ? content : "";
        })
        .join("\n");
}

function assessDistillationRisk(body: ChatRequestPayload): DistillationRiskGuard {
    const messageText = typeof body.message === "string" ? body.message : "";
    const historyText = extractHistoryText(body.history);
    const sourceText = `${messageText}\n${historyText}`.slice(0, DISTILLATION_GUARD_MAX_TEXT);

    if (!sourceText.trim()) {
        return {
            score: 0,
            level: "low",
            policy_action: "normal",
            signals: [],
        };
    }

    const signals: string[] = [];
    let score = 0;
    for (const rule of DISTILLATION_SIGNAL_RULES) {
        if (rule.pattern.test(sourceText)) {
            score += rule.weight;
            signals.push(rule.id);
        }
    }

    const boundedScore = Math.min(100, score);
    if (boundedScore >= DISTILLATION_GUARD_HIGH_THRESHOLD) {
        return {
            score: boundedScore,
            level: "high",
            policy_action: "constrain_reasoning",
            signals,
        };
    }
    if (boundedScore >= DISTILLATION_GUARD_MEDIUM_THRESHOLD) {
        return {
            score: boundedScore,
            level: "medium",
            policy_action: "reduce_detail",
            signals,
        };
    }
    return {
        score: boundedScore,
        level: "low",
        policy_action: "normal",
        signals,
    };
}

function applyDistillationGuardPolicy(
    body: ChatRequestPayload,
    guard: DistillationRiskGuard
): ChatRequestPayload {
    if (guard.policy_action === "normal") return body;

    const adjusted: ChatRequestPayload = {
        ...body,
        full_analysis: false,
    };

    if (guard.policy_action === "constrain_reasoning") {
        adjusted.council_mode = "rules";
        delete adjusted.perspective_config;
    }

    return adjusted;
}

function generateMockDeliberation(message: string) {
    const text = String(message || "");
    const isQuestion = /[?？]/.test(text);
    const isEmotional = /(sad|afraid|angry|anxious|悲傷|焦慮|害怕|生氣)/i.test(text);

    const tensionZone = "sweet_spot";
    let dominantVoice = "muse";

    if (isEmotional) {
        dominantVoice = "aegis";
    } else if (isQuestion) {
        dominantVoice = "logos";
    }

    return {
        synthesis: {
            type: "weighted_fusion",
            dominant_voice: dominantVoice,
            weights: {
                muse: dominantVoice === "muse" ? 0.45 : 0.3,
                logos: dominantVoice === "logos" ? 0.45 : 0.35,
                aegis: dominantVoice === "aegis" ? 0.45 : 0.25,
            },
        },
        decision_matrix: {
            user_hidden_intent: isEmotional ? "Need for emotional containment" : "Need for clearer direction",
            strategy_name: isEmotional ? "Stabilize then plan" : "Clarify and structure",
            intended_effect: isEmotional ? "Lower distress and increase trust" : "Increase clarity and momentum",
            tone_tag: isEmotional ? "empathetic" : "warm",
        },
        tension_zone: {
            zone: tensionZone,
            calculation_note: `Current zone is ${tensionZone}`,
        },
        next_moves: [
            { label: "Clarify goal", text: "Summarize the user intent in one sentence." },
            { label: "Offer options", text: "Provide two concrete next actions." },
        ],
    };
}

function generateMockResponse(message: string): string {
    const text = String(message || "");
    if (/(sad|afraid|angry|anxious|悲傷|焦慮|害怕|生氣)/i.test(text)) {
        return "I hear the emotional pressure in this. We can first stabilize, then decide the next concrete step together.";
    }
    if (/[?？]/.test(text)) {
        return "Good question. I will break this down into assumptions, constraints, and a direct recommendation.";
    }
    return "I understand. Let me respond with a clear and practical next-step proposal.";
}

function buildChatFallbackPayload(
    body: ChatRequestPayload,
    fallbackReason: string,
    distillationGuard: DistillationRiskGuard
): Record<string, unknown> {
    const message = String(body.message || "");
    const conversationId =
        typeof body.conversation_id === "string" ? body.conversation_id : "mock-conversation";

    return {
        response: generateMockResponse(message),
        conversation_id: conversationId,
        execution_profile: body.execution_profile || "interactive",
        deliberation: generateMockDeliberation(message),
        timestamp: new Date().toISOString(),
        deliberation_level: "mock",
        backend_mode: "mock_fallback",
        distillation_guard: distillationGuard,
        fallback_reason: fallbackReason,
        fallback_metadata: {
            triggered: true,
            reason: fallbackReason,
            execution_profile: body.execution_profile || "interactive",
        },
    };
}

async function forwardToBackend(
    backendUrl: string,
    body: ChatRequestPayload,
    budget: TransportBudget
): Promise<Response> {
    const { retryMaxAttempts, retryBaseDelayMs, timeoutMs } = budget;
    let lastTransportError: unknown = null;

    for (let attempt = 0; attempt < retryMaxAttempts; attempt++) {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), timeoutMs);
        try {
            const response = await fetch(`${backendUrl}/api/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body),
                signal: controller.signal,
            });

            if (isTransientStatus(response.status) && attempt < retryMaxAttempts - 1) {
                const retryAfterMs = parseRetryAfterMs(response.headers.get("Retry-After"));
                const delayMs = retryDelayMs(attempt, retryBaseDelayMs, retryAfterMs);
                if (response.body) {
                    void response.body.cancel().catch(() => {
                        // Ignore body-cancel errors during retry path.
                    });
                }
                await sleep(delayMs);
                continue;
            }

            return response;
        } catch (error) {
            lastTransportError = error;
            if (attempt < retryMaxAttempts - 1) {
                await sleep(retryDelayMs(attempt, retryBaseDelayMs));
                continue;
            }
        } finally {
            clearTimeout(timeout);
        }
    }

    throw (lastTransportError instanceof Error
        ? lastTransportError
        : new Error("Backend unavailable"));
}

export async function POST(request: NextRequest) {
    let rawBody: unknown;
    try {
        rawBody = await request.json();
    } catch {
        return NextResponse.json({ error: "Invalid JSON payload" }, { status: 400 });
    }

    const parsed = parseChatBody(rawBody);
    if (parsed.error) {
        return parsed.error;
    }
    const body = parsed.body as ChatRequestPayload;
    const executionProfile = resolveExecutionProfile(body);
    const normalizedBody = applyExecutionProfileDefaults(body, executionProfile);
    const distillationGuard = assessDistillationRisk(normalizedBody);
    const guardedBody = applyDistillationGuardPolicy(normalizedBody, distillationGuard);
    const transportBudget = resolveTransportBudget(executionProfile);

    // Same-origin mode now forwards to the Python backend via getBackendUrl()
    // which resolves to /api/_backend on the same Vercel deployment.

    const runtimeBackendMode = resolveRuntimeBackendMode();
    const backendUrl = getBackendUrl();
    const configuredBackendUrl = getConfiguredBackendUrl();
    if (isVercelRuntime()) {
        const validation = validateVercelBackendConfig(backendUrl, configuredBackendUrl);
        if (!validation.valid) {
            return NextResponse.json(
                {
                    error: "Backend configuration invalid for Vercel runtime",
                    backend_url: backendUrl,
                    config_issue: validation.issue,
                    hint: "Set TONESOUL_BACKEND_URL to a reachable HTTPS backend endpoint.",
                },
                { status: 503 }
            );
        }
    }

    let backendResponse: Response;
    try {
        backendResponse = await forwardToBackend(backendUrl, guardedBody, transportBudget);
    } catch (error) {
        const timeoutError = isAbortError(error);
        if (!shouldAllowMockFallback()) {
            return NextResponse.json(
                {
                    error: timeoutError
                        ? `Backend request timed out after ${transportBudget.timeoutMs}ms`
                        : "Backend unavailable",
                    execution_profile: executionProfile,
                    backend_url: backendUrl,
                    backend_mode: runtimeBackendMode,
                    deliberation_level: "unavailable",
                    backend_error: error instanceof Error ? error.message : "Transport failure",
                    backend_timeout_ms: transportBudget.timeoutMs,
                    distillation_guard: distillationGuard,
                    hint: `Set ${MOCK_FALLBACK_ENV}=1 to enable explicit mock fallback.`,
                },
                { status: timeoutError ? 504 : 502 }
            );
        }

        return NextResponse.json(
            buildChatFallbackPayload(guardedBody, "transport_failure", distillationGuard)
        );
    }

    if (!backendResponse.ok && shouldAllowMockFallback()) {
        return NextResponse.json(
            buildChatFallbackPayload(
                guardedBody,
                `backend_http_${backendResponse.status}`,
                distillationGuard
            )
        );
    }

    const text = await backendResponse.text();
    if (!text) {
        if (shouldAllowMockFallback()) {
            return NextResponse.json(
                buildChatFallbackPayload(guardedBody, "empty_backend_body", distillationGuard)
            );
        }
        return NextResponse.json({}, { status: backendResponse.status });
    }

    try {
        const payload = JSON.parse(text);
        if (typeof payload === 'object' && payload !== null) {
            if (typeof payload.execution_profile !== "string") {
                payload.execution_profile = executionProfile;
            }
            if (typeof payload.backend_mode !== "string") {
                payload.backend_mode = runtimeBackendMode;
            }
            payload.deliberation_level = "runtime";
            payload.distillation_guard = distillationGuard;
        }
        return NextResponse.json(payload, { status: backendResponse.status });
    } catch {
        if (shouldAllowMockFallback()) {
            return NextResponse.json(
                buildChatFallbackPayload(guardedBody, "invalid_backend_json", distillationGuard)
            );
        }
        return NextResponse.json(
            {
                error: "Backend returned invalid JSON",
                backend_status: backendResponse.status,
                backend_mode: runtimeBackendMode,
                deliberation_level: "unavailable",
                distillation_guard: distillationGuard,
            },
            { status: 502 }
        );
    }
}
