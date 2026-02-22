import { NextRequest, NextResponse } from "next/server";
import {
    envFlag,
    getBackendUrl,
    getConfiguredBackendUrl,
    isSameOriginMode,
    isVercelRuntime,
    validateVercelBackendConfig,
} from "../_shared/backendConfig";

const REQUEST_TIMEOUT_ENV = "TONESOUL_BACKEND_CHAT_TIMEOUT_MS";
const DEFAULT_REQUEST_TIMEOUT_MS = 25000;
const RETRY_MAX_ATTEMPTS_ENV = "TONESOUL_BACKEND_CHAT_RETRY_MAX_ATTEMPTS";
const RETRY_BASE_DELAY_MS_ENV = "TONESOUL_BACKEND_CHAT_RETRY_BASE_DELAY_MS";
const DEFAULT_RETRY_MAX_ATTEMPTS = 3;
const DEFAULT_RETRY_BASE_DELAY_MS = process.env.NODE_ENV === "test" ? 0 : 300;
const MOCK_FALLBACK_ENV = "TONESOUL_ENABLE_CHAT_MOCK_FALLBACK";
const ALLOWED_COUNCIL_MODES = new Set(["rules", "rules_only", "hybrid", "full_llm"]);
const TRANSIENT_STATUS_CODES = new Set([429, 502, 503, 504]);
const MAX_PERSONA_ROLES = 8;
const MAX_PERSONA_ATTACHMENTS_PER_ROLE = 6;

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

type ChatRequestPayload = {
    conversation_id?: string;
    message?: string;
    history?: unknown[];
    full_analysis?: boolean;
    council_mode?: "rules" | "hybrid" | "full_llm";
    perspective_config?: Record<string, Record<string, unknown>>;
    persona?: PersonaPayload;
};

function resolveRequestTimeoutMs(): number {
    const raw = process.env[REQUEST_TIMEOUT_ENV];
    if (!raw) return DEFAULT_REQUEST_TIMEOUT_MS;

    const parsed = Number(raw);
    if (!Number.isFinite(parsed) || parsed <= 0) {
        return DEFAULT_REQUEST_TIMEOUT_MS;
    }

    return Math.floor(parsed);
}

const REQUEST_TIMEOUT_MS = resolveRequestTimeoutMs();

function resolveRetryMaxAttempts(): number {
    const raw = process.env[RETRY_MAX_ATTEMPTS_ENV];
    if (!raw) return DEFAULT_RETRY_MAX_ATTEMPTS;
    const parsed = Number(raw);
    if (!Number.isFinite(parsed) || parsed < 1) {
        return DEFAULT_RETRY_MAX_ATTEMPTS;
    }
    return Math.floor(parsed);
}

function resolveRetryBaseDelayMs(): number {
    const raw = process.env[RETRY_BASE_DELAY_MS_ENV];
    if (!raw) return DEFAULT_RETRY_BASE_DELAY_MS;
    const parsed = Number(raw);
    if (!Number.isFinite(parsed) || parsed < 0) {
        return DEFAULT_RETRY_BASE_DELAY_MS;
    }
    return Math.floor(parsed);
}

function shouldAllowMockFallback(): boolean {
    // In same-origin mode, always allow mock fallback as the primary response mode
    if (isSameOriginMode()) return true;
    return envFlag(MOCK_FALLBACK_ENV, false);
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

    return { body: parsed };
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

async function forwardToBackend(backendUrl: string, body: ChatRequestPayload): Promise<Response> {
    const retryMaxAttempts = resolveRetryMaxAttempts();
    const retryBaseDelayMs = resolveRetryBaseDelayMs();
    let lastTransportError: unknown = null;

    for (let attempt = 0; attempt < retryMaxAttempts; attempt++) {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
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
        backendResponse = await forwardToBackend(backendUrl, body);
    } catch (error) {
        const timeoutError = isAbortError(error);
        if (!shouldAllowMockFallback()) {
            return NextResponse.json(
                {
                    error: timeoutError
                        ? `Backend request timed out after ${REQUEST_TIMEOUT_MS}ms`
                        : "Backend unavailable",
                    backend_url: backendUrl,
                    backend_error: error instanceof Error ? error.message : "Transport failure",
                    backend_timeout_ms: REQUEST_TIMEOUT_MS,
                    hint: `Set ${MOCK_FALLBACK_ENV}=1 to enable explicit mock fallback.`,
                },
                { status: timeoutError ? 504 : 502 }
            );
        }

        const message = String(body.message || "");
        const conversationId =
            typeof body.conversation_id === "string" ? body.conversation_id : "mock-conversation";

        const mockResponse = generateMockResponse(message);
        const mockDeliberation = generateMockDeliberation(message);

        return NextResponse.json({
            response: mockResponse,
            conversation_id: conversationId,
            deliberation: mockDeliberation,
            timestamp: new Date().toISOString(),
            backend_mode: "mock_fallback",
            fallback_reason: "transport_failure",
        });
    }

    const text = await backendResponse.text();
    if (!text) {
        return NextResponse.json({}, { status: backendResponse.status });
    }

    try {
        const payload = JSON.parse(text);
        return NextResponse.json(payload, { status: backendResponse.status });
    } catch {
        return NextResponse.json(
            { error: "Backend returned invalid JSON", backend_status: backendResponse.status },
            { status: 502 }
        );
    }
}
