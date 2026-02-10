export type BackendFallbackReasonCode = "timeout" | "backend_unreachable" | "backend_error";

const TIMEOUT_PATTERNS = ["timeout", "timed out", "abort", "aborted"];
const UNREACHABLE_PATTERNS = [
    "failed to fetch",
    "network",
    "transport",
    "econnrefused",
    "enotfound",
    "unavailable",
    "unreachable",
    "connection refused",
];

export const BACKEND_FALLBACK_REASON_LABEL: Record<BackendFallbackReasonCode, string> = {
    timeout: "Backend timeout",
    backend_unreachable: "Backend unreachable",
    backend_error: "Backend error",
};

export const classifyBackendFallbackReason = (error: unknown): BackendFallbackReasonCode => {
    const message = String(error instanceof Error ? error.message : error ?? "").toLowerCase();

    if (TIMEOUT_PATTERNS.some(pattern => message.includes(pattern))) {
        return "timeout";
    }

    if (UNREACHABLE_PATTERNS.some(pattern => message.includes(pattern))) {
        return "backend_unreachable";
    }

    return "backend_error";
};
