import { NextRequest, NextResponse } from "next/server";
import {
    getBackendUrl,
    getConfiguredBackendUrl,
    isVercelRuntime,
    validateVercelBackendConfig,
} from "../_shared/backendConfig";

const REQUEST_TIMEOUT_MS = 10000;

async function forwardToBackend(backendUrl: string, search: string): Promise<Response> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
    const query = search || "";
    try {
        return await fetch(`${backendUrl}/api/conversations${query}`, {
            method: "GET",
            headers: { Accept: "application/json" },
            signal: controller.signal,
            cache: "no-store",
        });
    } finally {
        clearTimeout(timeout);
    }
}

export async function GET(request: NextRequest) {
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
        backendResponse = await forwardToBackend(backendUrl, request.nextUrl.search);
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
