const DEFAULT_BACKEND_URL = "http://127.0.0.1:5000";
const LOCAL_HOSTS = new Set(["127.0.0.1", "localhost", "::1"]);

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

export function getBackendUrl(): string {
    return getConfiguredBackendUrl() ?? DEFAULT_BACKEND_URL;
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
