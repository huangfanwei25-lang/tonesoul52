import { NextResponse } from "next/server";
import {
    getBackendUrl,
    getConfiguredBackendUrl,
    isVercelRuntime,
    validateVercelBackendConfig,
} from "../../_shared/backendConfig";

const REQUEST_TIMEOUT_MS = 10000;

type RouteContext = {
    params: Promise<{
        id: string;
    }>;
};

async function forwardToBackend(
    backendUrl: string,
    conversationId: string,
    method: "GET" | "DELETE"
): Promise<Response> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
    try {
        return await fetch(
            `${backendUrl}/api/conversations/${encodeURIComponent(conversationId)}`,
            {
                method,
                headers: { Accept: "application/json" },
                signal: controller.signal,
                cache: "no-store",
            }
        );
    } finally {
        clearTimeout(timeout);
    }
}

function validateConversationId(rawId: string): string | null {
    const trimmed = (rawId || "").trim();
    if (!trimmed) return null;
    return trimmed;
}

async function handleForwardedRequest(
    conversationId: string,
    method: "GET" | "DELETE"
): Promise<NextResponse> {
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
        backendResponse = await forwardToBackend(backendUrl, conversationId, method);
    } catch (error) {
        return NextResponse.json(
            {
                error: "Backend unavailable",
                backend_url: backendUrl,
                backend_error: error instanceof Error ? error.message : "Transport failure",
            },
            { status: 502 }
        );
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

export async function GET(_request: Request, context: RouteContext) {
    const params = await context.params;
    const conversationId = validateConversationId(params.id);
    if (!conversationId) {
        return NextResponse.json({ error: "Invalid conversation_id" }, { status: 400 });
    }
    return handleForwardedRequest(conversationId, "GET");
}

export async function DELETE(_request: Request, context: RouteContext) {
    const params = await context.params;
    const conversationId = validateConversationId(params.id);
    if (!conversationId) {
        return NextResponse.json({ error: "Invalid conversation_id" }, { status: 400 });
    }
    return handleForwardedRequest(conversationId, "DELETE");
}
