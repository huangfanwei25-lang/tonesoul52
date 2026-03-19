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
    | "backend_governance_status_timeout"
    | "backend_governance_status_transport_error"
    | "backend_governance_status_http_error";

type BackendProbeResult =
    | { ok: true; status: number; payload: Record<string, unknown> }
    | { ok: false; reason: BackendProbeFailureReason; status?: number };

async function probeBackendGovernanceStatus(backendUrl: string): Promise<BackendProbeResult> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), PROBE_TIMEOUT_MS);
    try {
        const response = await fetch(`${backendUrl}/api/governance_status`, {
            method: "GET",
            headers: { Accept: "application/json" },
            signal: controller.signal,
            cache: "no-store",
        });

        if (!response.ok) {
            return {
                ok: false,
                reason: "backend_governance_status_http_error",
                status: response.status,
            };
        }

        const payload = (await response.json()) as Record<string, unknown>;
        return { ok: true, status: response.status, payload };
    } catch (error) {
        if (error instanceof Error && error.name === "AbortError") {
            return { ok: false, reason: "backend_governance_status_timeout" };
        }
        return { ok: false, reason: "backend_governance_status_transport_error" };
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
    const forceSameOriginMock = sameOrigin && envFlag(SAME_ORIGIN_FORCE_MOCK_ENV, false);

    if (forceSameOriginMock) {
        return NextResponse.json({
            status: "ok",
            backend_mode: "same_origin",
            governance_capability: "mock_only",
            deliberation_level: "mock",
            backend_status: 200,
            reason: "same_origin_forced_mock",
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

    const probe = await probeBackendGovernanceStatus(backendUrl);
    if (!probe.ok) {
        return NextResponse.json(
            {
                status: "degraded",
                backend_mode: sameOrigin ? "same_origin" : "external_backend",
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

    const backendPayload = probe.payload;
    const resolvedCapability =
        backendPayload.governance_capability === "runtime_ready"
            || backendPayload.governance_capability === "mock_only"
            ? (backendPayload.governance_capability as string)
            : "runtime_ready";

    return NextResponse.json({
        ...backendPayload,
        status: typeof backendPayload.status === "string" ? backendPayload.status : "ok",
        backend_mode: sameOrigin ? "same_origin" : "external_backend",
        governance_capability: resolvedCapability,
        deliberation_level: resolvedCapability === "runtime_ready" ? "runtime" : "mock",
        backend_status: probe.status,
        checked_at:
            typeof backendPayload.checked_at === "string" ? backendPayload.checked_at : checkedAt,
        elisa: buildElisaContract(resolvedCapability === "runtime_ready", checkedAt),
    });
}
