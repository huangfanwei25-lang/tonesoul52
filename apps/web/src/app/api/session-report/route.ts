import { NextRequest, NextResponse } from "next/server";

const DEFAULT_BACKEND_URL = "http://127.0.0.1:5000";
const REQUEST_TIMEOUT_MS = 12000;
const MOCK_FALLBACK_ENV = "TONESOUL_ENABLE_SESSION_REPORT_MOCK_FALLBACK";

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

type Turn = {
    role?: string;
    content?: string;
    user?: string;
    ai?: string;
    entropy?: number;
};

type SessionReport = {
    emotional_arc: string;
    key_insights: string[];
    hidden_needs: string;
    navigator_rating: {
        connection_score: number;
        growth_score: number;
    };
    closing_advice: string;
};

async function forwardToBackend(history: Turn[]): Promise<Response> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
    try {
        return await fetch(`${getBackendUrl()}/api/session-report`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ history }),
            signal: controller.signal,
        });
    } finally {
        clearTimeout(timeout);
    }
}

function buildFallbackReport(history: Turn[]): SessionReport {
    const turns = history.length;
    const avgEntropy =
        turns > 0
            ? history.reduce((sum, turn) => sum + (typeof turn.entropy === "number" ? turn.entropy : 0), 0) /
              turns
            : 0;

    let entropyBand = "stable";
    if (avgEntropy >= 0.66) {
        entropyBand = "high_tension";
    } else if (avgEntropy >= 0.33) {
        entropyBand = "medium_tension";
    }

    return {
        emotional_arc: `Conversation has ${turns} turns and sits in ${entropyBand} range.`,
        key_insights: [
            "The user prefers concrete and testable suggestions.",
            "The interaction pattern values transparency and accountability.",
            "A small-step execution loop is needed to keep momentum.",
        ],
        hidden_needs: "Reduce decision uncertainty while maintaining practical progress.",
        navigator_rating: {
            connection_score: 7.6,
            growth_score: 7.8,
        },
        closing_advice:
            "Pick the next smallest verifiable step, execute it, then write a short memory update and rerun checks.",
    };
}

export async function POST(request: NextRequest) {
    let body: Record<string, unknown>;
    try {
        body = (await request.json()) as Record<string, unknown>;
    } catch {
        return NextResponse.json({ error: "Invalid JSON payload" }, { status: 400 });
    }

    const history = Array.isArray(body.history) ? (body.history as Turn[]) : [];
    if (history.length === 0) {
        return NextResponse.json({ error: "Missing conversation history" }, { status: 400 });
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
        backendResponse = await forwardToBackend(history);
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

        const report = buildFallbackReport(history);
        return NextResponse.json({
            success: true,
            report,
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
