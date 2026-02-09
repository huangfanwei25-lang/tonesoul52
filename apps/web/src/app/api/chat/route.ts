import { NextRequest, NextResponse } from "next/server";

const DEFAULT_BACKEND_URL = "http://127.0.0.1:5000";
const REQUEST_TIMEOUT_MS = 15000;
const MOCK_FALLBACK_ENV = "TONESOUL_ENABLE_CHAT_MOCK_FALLBACK";

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

function generateMockDeliberation(message: string) {
    const text = String(message || "");
    const isQuestion = text.includes("?") || text.includes("？");
    const isEmotional = /(sad|afraid|angry|anxious|失落|難過|焦慮|害怕)/i.test(text);

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
    if (/(sad|afraid|angry|anxious|失落|難過|焦慮|害怕)/i.test(text)) {
        return "I hear the emotional pressure in this. We can first stabilize, then decide the next concrete step together.";
    }
    if (text.includes("?") || text.includes("？")) {
        return "Good question. I will break this down into assumptions, constraints, and a direct recommendation.";
    }
    return "I understand. Let me respond with a clear and practical next-step proposal.";
}

async function forwardToBackend(body: unknown): Promise<Response> {
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
    let body: Record<string, unknown>;
    try {
        body = (await request.json()) as Record<string, unknown>;
    } catch {
        return NextResponse.json({ error: "Invalid JSON payload" }, { status: 400 });
    }

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
