import { NextRequest, NextResponse } from "next/server";

const DEFAULT_BACKEND_URL = "http://127.0.0.1:5000";
const REQUEST_TIMEOUT_MS = 10000;
const MOCK_FALLBACK_ENV = "TONESOUL_ENABLE_CONVERSATION_MOCK_FALLBACK";

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

async function forwardToBackend(body: unknown): Promise<Response> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
    try {
        return await fetch(`${getBackendUrl()}/api/conversation`, {
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

        const sessionId = typeof body.session_id === "string" ? body.session_id : null;
        const conversationId = `conv_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;

        return NextResponse.json({
            success: true,
            conversation_id: conversationId,
            session_id: sessionId,
            created_at: new Date().toISOString(),
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
