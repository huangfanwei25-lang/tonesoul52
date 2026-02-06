import { NextRequest, NextResponse } from "next/server";

const DEFAULT_BACKEND_URL = "http://127.0.0.1:5000";
const REQUEST_TIMEOUT_MS = 10000;

function getBackendUrl(): string {
    const url = process.env["TONESOUL_BACKEND_URL"];
    return typeof url === "string" && url.trim() ? url.trim() : DEFAULT_BACKEND_URL;
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

    let backendResponse: Response;
    try {
        backendResponse = await forwardToBackend(body);
    } catch {
        const sessionId = typeof body.session_id === "string" ? body.session_id : null;
        const conversationId = `conv_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;

        return NextResponse.json({
            success: true,
            conversation_id: conversationId,
            session_id: sessionId,
            created_at: new Date().toISOString(),
            backend_mode: "mock_fallback",
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
