import { NextRequest, NextResponse } from "next/server";
import {
    envFlag,
    getBackendUrl,
    getConfiguredBackendUrl,
    isSameOriginMode,
    isVercelRuntime,
    validateVercelBackendConfig,
} from "../_shared/backendConfig";

const REQUEST_TIMEOUT_MS = 10000;
const MOCK_FALLBACK_ENV = "TONESOUL_ENABLE_CONVERSATION_MOCK_FALLBACK";
const _SAME_ORIGIN_PRIMARY_FALLBACK_REASON = "same_origin_primary";

function shouldAllowMockFallback(): boolean {
    if (isSameOriginMode()) return true;
    return envFlag(MOCK_FALLBACK_ENV, false);
}

function resolveRuntimeBackendMode(): "same_origin" | "external_backend" {
    return isSameOriginMode() ? "same_origin" : "external_backend";
}

function buildConversationFallback(
    body: Record<string, unknown>,
    fallbackReason: string
): Record<string, unknown> {
    const sessionId = typeof body.session_id === "string" ? body.session_id : null;
    const conversationId = `conv_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;

    return {
        success: true,
        conversation_id: conversationId,
        session_id: sessionId,
        created_at: new Date().toISOString(),
        deliberation_level: "mock",
        backend_mode: "mock_fallback",
        fallback_reason: fallbackReason,
        fallback_metadata: {
            triggered: true,
            reason: fallbackReason,
        },
    };
}

async function forwardToBackend(backendUrl: string, body: unknown): Promise<Response> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
    try {
        return await fetch(`${backendUrl}/api/conversation`, {
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

    // Same-origin mode forwards to Python backend via getBackendUrl()

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
        backendResponse = await forwardToBackend(backendUrl, body);
    } catch (error) {
        if (!shouldAllowMockFallback()) {
            return NextResponse.json(
                {
                    error: "Backend unavailable",
                    backend_url: backendUrl,
                    backend_mode: runtimeBackendMode,
                    deliberation_level: "unavailable",
                    backend_error: error instanceof Error ? error.message : "Transport failure",
                    hint: `Set ${MOCK_FALLBACK_ENV}=1 to enable explicit mock fallback.`,
                },
                { status: 502 }
            );
        }

        return NextResponse.json(buildConversationFallback(body, "transport_failure"));
    }

    if (!backendResponse.ok && shouldAllowMockFallback()) {
        return NextResponse.json(
            buildConversationFallback(body, `backend_http_${backendResponse.status}`)
        );
    }

    const text = await backendResponse.text();
    if (!text) {
        return NextResponse.json({}, { status: backendResponse.status });
    }

    try {
        const payload = JSON.parse(text);
        if (typeof payload === 'object' && payload !== null) {
            if (typeof payload.backend_mode !== "string") {
                payload.backend_mode = runtimeBackendMode;
            }
            payload.deliberation_level = "runtime";
        }
        return NextResponse.json(payload, { status: backendResponse.status });
    } catch {
        if (shouldAllowMockFallback()) {
            return NextResponse.json(buildConversationFallback(body, "invalid_backend_json"));
        }
        return NextResponse.json(
            {
                error: "Backend returned invalid JSON",
                backend_status: backendResponse.status,
                backend_mode: runtimeBackendMode,
                deliberation_level: "unavailable",
            },
            { status: 502 }
        );
    }
}
