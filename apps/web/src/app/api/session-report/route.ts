import { NextRequest, NextResponse } from "next/server";
import {
    envFlag,
    getBackendUrl,
    getConfiguredBackendUrl,
    isSameOriginMode,
    isVercelRuntime,
    validateVercelBackendConfig,
} from "../_shared/backendConfig";

const REQUEST_TIMEOUT_MS = 12000;
const MOCK_FALLBACK_ENV = "TONESOUL_ENABLE_SESSION_REPORT_MOCK_FALLBACK";
const SAME_ORIGIN_PRIMARY_FALLBACK_REASON = "same_origin_primary";

function shouldAllowMockFallback(): boolean {
    if (isSameOriginMode()) return true;
    return envFlag(MOCK_FALLBACK_ENV, false);
}

function resolveRuntimeBackendMode(): "same_origin" | "external_backend" {
    return isSameOriginMode() ? "same_origin" : "external_backend";
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

async function forwardToBackend(backendUrl: string, history: Turn[]): Promise<Response> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
    try {
        return await fetch(`${backendUrl}/api/session-report`, {
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

    if (isSameOriginMode()) {
        return NextResponse.json({
            success: true,
            report: buildFallbackReport(history),
            backend_mode: "mock_fallback",
            deliberation_level: "mock",
            fallback_reason: SAME_ORIGIN_PRIMARY_FALLBACK_REASON,
        });
    }

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
        backendResponse = await forwardToBackend(backendUrl, history);
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

        const report = buildFallbackReport(history);
        return NextResponse.json({
            success: true,
            report,
            backend_mode: "mock_fallback",
            deliberation_level: "mock",
            fallback_reason: "transport_failure",
        });
    }

    if (!backendResponse.ok && shouldAllowMockFallback()) {
        const report = buildFallbackReport(history);
        return NextResponse.json({
            success: true,
            report,
            backend_mode: "mock_fallback",
            deliberation_level: "mock",
            fallback_reason: `backend_http_${backendResponse.status}`,
        });
    }

    const text = await backendResponse.text();
    if (!text) {
        return NextResponse.json({}, { status: backendResponse.status });
    }

    try {
        const payload = JSON.parse(text);
        if (typeof payload === "object" && payload !== null) {
            if (typeof payload.backend_mode !== "string") {
                payload.backend_mode = runtimeBackendMode;
            }
            if (typeof payload.deliberation_level !== "string") {
                payload.deliberation_level = "runtime";
            }
        }
        return NextResponse.json(payload, { status: backendResponse.status });
    } catch {
        if (shouldAllowMockFallback()) {
            const report = buildFallbackReport(history);
            return NextResponse.json({
                success: true,
                report,
                backend_mode: "mock_fallback",
                deliberation_level: "mock",
                fallback_reason: "invalid_backend_json",
            });
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
