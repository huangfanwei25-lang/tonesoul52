import { NextResponse } from "next/server";
import {
    getBackendUrl,
    getConfiguredBackendUrl,
    isSameOriginMode,
    isVercelRuntime,
    validateVercelBackendConfig,
} from "../_shared/backendConfig";

const PROBE_TIMEOUT_ENV = "TONESOUL_BACKEND_HEALTH_TIMEOUT_MS";
const DEFAULT_PROBE_TIMEOUT_MS = 6000;
const SAME_ORIGIN_FORCE_MOCK_ENV = "TONESOUL_FORCE_SAME_ORIGIN_MOCK";

function resolveProbeTimeoutMs(): number {
    const raw = process.env[PROBE_TIMEOUT_ENV];
    if (!raw) return DEFAULT_PROBE_TIMEOUT_MS;
    const parsed = Number(raw);
    if (!Number.isFinite(parsed) || parsed <= 0) {
        return DEFAULT_PROBE_TIMEOUT_MS;
    }
    return Math.floor(parsed);
}

const PROBE_TIMEOUT_MS = resolveProbeTimeoutMs();

function envFlag(name: string, defaultValue = false): boolean {
    const raw = process.env[name];
    if (raw == null) {
        return defaultValue;
    }
    return ["1", "true", "yes", "on"].includes(raw.trim().toLowerCase());
}

type BackendProbeFailureReason =
    | "backend_health_timeout"
    | "backend_health_transport_error"
    | "backend_health_http_error";

type BackendProbeResult =
    | { ok: true; status: number }
    | { ok: false; reason: BackendProbeFailureReason; status?: number };

async function probeBackendHealth(backendUrl: string): Promise<BackendProbeResult> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), PROBE_TIMEOUT_MS);
    try {
        const response = await fetch(`${backendUrl}/api/health`, {
            method: "GET",
            headers: { Accept: "application/json" },
            signal: controller.signal,
            cache: "no-store",
        });

        if (!response.ok) {
            return { ok: false, reason: "backend_health_http_error", status: response.status };
        }

        return { ok: true, status: response.status };
    } catch (error) {
        if (error instanceof Error && error.name === "AbortError") {
            return { ok: false, reason: "backend_health_timeout" };
        }
        return { ok: false, reason: "backend_health_transport_error" };
    } finally {
        clearTimeout(timeout);
    }
}

export async function GET() {
    const sameOrigin = isSameOriginMode();
    const backendUrl = getBackendUrl();
    const configuredBackendUrl = getConfiguredBackendUrl();
    const checkedAt = new Date().toISOString();
    const forceSameOriginMock = sameOrigin && envFlag(SAME_ORIGIN_FORCE_MOCK_ENV, false);

    if (forceSameOriginMock) {
        return NextResponse.json({
            ok: true,
            backend_url: "same-origin",
            backend_mode: "same_origin",
            governance_capability: "mock_only",
            backend_status: 200,
            reason: "same_origin_forced_mock",
            checked_at: checkedAt,
        });
    }

    if (isVercelRuntime()) {
        const validation = validateVercelBackendConfig(backendUrl, configuredBackendUrl);
        if (!validation.valid) {
            return NextResponse.json(
                {
                    ok: false,
                    backend_url: backendUrl,
                    config_issue: validation.issue,
                    reason: "backend_config_invalid",
                    hint: "Set TONESOUL_BACKEND_URL to a reachable HTTPS backend endpoint.",
                },
                { status: 503 }
            );
        }
    }

    const probe = await probeBackendHealth(backendUrl);
    if (!probe.ok) {
        return NextResponse.json(
            {
                ok: false,
                backend_url: backendUrl,
                backend_mode: sameOrigin ? "same_origin" : "external_backend",
                reason: probe.reason,
                backend_status: probe.status ?? null,
                checked_at: checkedAt,
            },
            { status: 503 }
        );
    }

    return NextResponse.json({
        ok: true,
        backend_url: backendUrl,
        backend_mode: sameOrigin ? "same_origin" : "external_backend",
        governance_capability: "runtime_ready",
        backend_status: probe.status,
        checked_at: checkedAt,
    });
}
