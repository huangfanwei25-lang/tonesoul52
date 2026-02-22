import { NextResponse } from "next/server";
import {
    getBackendUrl,
    getConfiguredBackendUrl,
    isVercelRuntime,
    validateVercelBackendConfig,
} from "../_shared/backendConfig";

const REQUEST_TIMEOUT_MS = 8000;

async function fetchBackendHealth(backendUrl: string): Promise<Response> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
    try {
        return await fetch(`${backendUrl}/api/health`, {
            method: "GET",
            headers: { Accept: "application/json" },
            signal: controller.signal,
            cache: "no-store",
        });
    } finally {
        clearTimeout(timeout);
    }
}

function parseJsonPayload(text: string): Record<string, unknown> | null {
    if (!text.trim()) return {};
    try {
        const parsed = JSON.parse(text);
        if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
            return parsed as Record<string, unknown>;
        }
        return {};
    } catch {
        return null;
    }
}

export async function GET() {
    const backendUrl = getBackendUrl();
    const configuredBackendUrl = getConfiguredBackendUrl();

    if (isVercelRuntime()) {
        const validation = validateVercelBackendConfig(backendUrl, configuredBackendUrl);
        if (!validation.valid) {
            return NextResponse.json(
                {
                    status: "degraded",
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
        backendResponse = await fetchBackendHealth(backendUrl);
    } catch (error) {
        return NextResponse.json(
            {
                status: "degraded",
                error: "Backend health check failed",
                backend_url: backendUrl,
                backend_error: error instanceof Error ? error.message : "Transport failure",
            },
            { status: 503 }
        );
    }

    const payloadText = await backendResponse.text();
    const payload = parseJsonPayload(payloadText);
    if (payload === null) {
        return NextResponse.json(
            {
                status: "degraded",
                error: "Backend returned invalid JSON",
                backend_status: backendResponse.status,
            },
            { status: 502 }
        );
    }

    if (!backendResponse.ok) {
        return NextResponse.json(
            {
                ...payload,
                status: "degraded",
                backend_status: backendResponse.status,
                backend_url: backendUrl,
            },
            { status: 503 }
        );
    }

    if (typeof payload.status !== "string") {
        payload.status = "ok";
    }
    return NextResponse.json(payload, { status: 200 });
}
