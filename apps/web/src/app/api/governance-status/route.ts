import { NextResponse } from "next/server";
import {
    getBackendUrl,
    getConfiguredBackendUrl,
    isSameOriginMode,
    isVercelRuntime,
    validateVercelBackendConfig,
} from "../_shared/backendConfig";

const PROBE_TIMEOUT_ENV = "TONESOUL_GOVERNANCE_STATUS_TIMEOUT_MS";
const DEFAULT_PROBE_TIMEOUT_MS = 6000;

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

function buildElisaContract(readiness: boolean, checkedAt: string) {
    return {
        integration_ready: readiness,
        contract_version: "phase108_p1",
        payload_profile: "elisa_chat_v0",
        smoke_command: "python scripts/verify_web_api.py --elisa-scenario",
        checked_at: checkedAt,
    };
}

export async function GET() {
    const checkedAt = new Date().toISOString();
    const sameOrigin = isSameOriginMode();
    const backendUrl = getBackendUrl();
    const configuredBackendUrl = getConfiguredBackendUrl();

    if (sameOrigin) {
        return NextResponse.json({
            status: "ok",
            backend_mode: "same_origin",
            governance_capability: "mock_only",
            deliberation_level: "mock",
            backend_status: 200,
            checked_at: checkedAt,
            elisa: buildElisaContract(true, checkedAt),
        });
    }

    if (isVercelRuntime()) {
        const validation = validateVercelBackendConfig(backendUrl, configuredBackendUrl);
        if (!validation.valid) {
            return NextResponse.json(
                {
                    status: "degraded",
                    backend_mode: "external_backend",
                    governance_capability: "unavailable",
                    deliberation_level: "unavailable",
                    backend_status: null,
                    reason: "backend_config_invalid",
                    config_issue: validation.issue,
                    checked_at: checkedAt,
                    elisa: buildElisaContract(false, checkedAt),
                },
                { status: 503 }
            );
        }
    }

    const probe = await probeBackendHealth(backendUrl);
    if (!probe.ok) {
        return NextResponse.json(
            {
                status: "degraded",
                backend_mode: "external_backend",
                governance_capability: "unavailable",
                deliberation_level: "unavailable",
                backend_status: probe.status ?? null,
                reason: probe.reason,
                checked_at: checkedAt,
                elisa: buildElisaContract(false, checkedAt),
            },
            { status: 503 }
        );
    }

    return NextResponse.json({
        status: "ok",
        backend_mode: "external_backend",
        governance_capability: "runtime_ready",
        deliberation_level: "runtime",
        backend_status: probe.status,
        checked_at: checkedAt,
        elisa: buildElisaContract(true, checkedAt),
    });
}
