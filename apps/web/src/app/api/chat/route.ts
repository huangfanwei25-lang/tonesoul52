import { NextRequest, NextResponse } from "next/server";

const DEFAULT_BACKEND_URL = "http://127.0.0.1:5000";
const REQUEST_TIMEOUT_MS = 15000;
const MOCK_FALLBACK_ENV = "TONESOUL_ENABLE_CHAT_MOCK_FALLBACK";
const ALLOWED_COUNCIL_MODES = new Set(["rules", "rules_only", "hybrid", "full_llm"]);

type ChatRequestPayload = {
    conversation_id?: string;
    message?: string;
    history?: unknown[];
    full_analysis?: boolean;
    council_mode?: "rules" | "hybrid" | "full_llm";
    perspective_config?: Record<string, Record<string, unknown>>;
};

function getConfiguredBackendUrl(): string | null {
    const url = process.env["TONESOUL_BACKEND_URL"];
    if (typeof url === "string" && url.trim()) {
        return url.trim();
    }
    return null;
}

function getBackendUrl(): string {
    return getConfiguredBackendUrl() ?? DEFAULT_BACKEND_URL;
}

function envFlag(name: string, defaultValue = false): boolean {
    const raw = process.env[name];
    if (raw == null) {
        return defaultValue;
    }
    return ["1", "true", "yes", "on"].includes(raw.trim().toLowerCase());
}

function isVercelRuntime(): boolean {
    return envFlag("VERCEL", false) || Boolean(process.env["VERCEL_URL"]);
}

function isLocalBackendUrl(url: string): boolean {
    try {
        const parsed = new URL(url);
        return ["127.0.0.1", "localhost", "::1"].includes(parsed.hostname);
    } catch {
        return false;
    }
}

function shouldAllowMockFallback(): boolean {
    return envFlag(MOCK_FALLBACK_ENV, false);
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

async function forwardToBackend(body: ChatRequestPayload): Promise<Response> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
    const backendUrl = getBackendUrl();
    try {
        return await fetch(`${backendUrl}/api/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
            signal: controller.signal,
        });
    } finally {
        clearTimeout(timeout);
    }
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
    if (isVercelRuntime() && (!configuredBackendUrl || isLocalBackendUrl(backendUrl))) {
        return NextResponse.json(
            {
                error: "Backend configuration invalid for Vercel runtime",
                backend_url: backendUrl,
                hint: "Set TONESOUL_BACKEND_URL to a reachable HTTPS backend endpoint.",
            },
            { status: 503 }
        );
    }

    let backendResponse: Response;
    try {
        backendResponse = await forwardToBackend(body);
    } catch (error) {
        if (!shouldAllowMockFallback()) {
            return NextResponse.json(
                {
                    error: "Backend unavailable",
                    backend_url: backendUrl,
                    backend_error: error instanceof Error ? error.message : "Transport failure",
                    hint: `Set ${MOCK_FALLBACK_ENV}=1 to enable explicit mock fallback.`,
                },
                { status: 502 }
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
