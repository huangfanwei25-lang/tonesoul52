const LOCAL_FALLBACK_URL = "http://127.0.0.1:5000";
const LOCAL_HOSTS = new Set(["127.0.0.1", "localhost", "::1"]);
const SAME_ORIGIN_MARKERS = new Set(["", "self", "same-origin"]);
const SAME_ORIGIN_BACKEND_PREFIX = "/api/_backend";

export type VercelBackendConfigIssue =
    | "missing"
    | "invalid_url"
    | "local_address"
    | "insecure_protocol";

type VercelBackendConfigValidation =
    | { valid: true }
    | { valid: false; issue: VercelBackendConfigIssue };

export function getConfiguredBackendUrl(): string | null {
    const url = process.env["TONESOUL_BACKEND_URL"];
    if (typeof url === "string" && url.trim()) {
        return url.trim();
    }
    return null;
}

/**
 * Whether the backend is configured for same-origin mode.
 * This means the Python serverless functions live alongside
 * the Next.js app on the same Vercel deployment.
 *
 * Same-origin triggers when:
 * - TONESOUL_BACKEND_URL is unset, empty, "self", or "same-origin"
 * - AND we are running on Vercel
 */
export function isSameOriginMode(): boolean {
    if (!isVercelRuntime()) return false;
    const configured = getConfiguredBackendUrl();
    if (configured === null) return true;
    return SAME_ORIGIN_MARKERS.has(configured.trim().toLowerCase());
}

/**
 * Resolve the backend URL.
 * - On Vercel with same-origin mode: prefer project production URL + backend prefix
 * - With explicit TONESOUL_BACKEND_URL: use that
 * - Local development fallback: http://127.0.0.1:5000
 */
export function getBackendUrl(): string {
    if (isSameOriginMode()) {
        const productionUrl = (process.env["VERCEL_PROJECT_PRODUCTION_URL"] || "").trim();
        if (productionUrl) {
            return `https://${productionUrl}${SAME_ORIGIN_BACKEND_PREFIX}`;
        }
        const vercelUrl = (process.env["VERCEL_URL"] || "").trim();
        if (vercelUrl) {
            return `https://${vercelUrl}${SAME_ORIGIN_BACKEND_PREFIX}`;
        }
        return SAME_ORIGIN_BACKEND_PREFIX;
    }
    return getConfiguredBackendUrl() ?? LOCAL_FALLBACK_URL;
}

export function envFlag(name: string, defaultValue = false): boolean {
    const raw = process.env[name];
    if (raw == null) {
        return defaultValue;
    }
    return ["1", "true", "yes", "on"].includes(raw.trim().toLowerCase());
}

export function isVercelRuntime(): boolean {
    return envFlag("VERCEL", false) || Boolean(process.env["VERCEL_URL"]);
}

export function validateVercelBackendConfig(
    backendUrl: string,
    configuredBackendUrl: string | null
): VercelBackendConfigValidation {
    // Same-origin mode is always valid — backend is self
    if (isSameOriginMode()) {
        return { valid: true };
    }

    if (!configuredBackendUrl) {
        return { valid: false, issue: "missing" };
    }

    let parsed: URL;
    try {
        parsed = new URL(backendUrl);
    } catch {
        return { valid: false, issue: "invalid_url" };
    }

    if (LOCAL_HOSTS.has(parsed.hostname.toLowerCase())) {
        return { valid: false, issue: "local_address" };
    }

    if (parsed.protocol !== "https:") {
        return { valid: false, issue: "insecure_protocol" };
    }

    return { valid: true };
}
