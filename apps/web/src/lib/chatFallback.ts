export type BackendFallbackReasonCode = "timeout" | "backend_unreachable" | "backend_error";

const TIMEOUT_PATTERNS = [
    "timeout",
    "timed out",
    "request timeout",
    "gateway timeout",
    "deadline exceeded",
    "abort",
    "aborted",
];
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
const BACKEND_DEGRADED_RESPONSE_PATTERNS = [
    "llm 服務不可用",
    "llm服務不可用",
    "llm service unavailable",
    "model service unavailable",
    "模型服務不可用",
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

export const isBackendDegradedResponse = (responseText: unknown): boolean => {
    if (typeof responseText !== "string") {
        return false;
    }

    const message = responseText.trim().toLowerCase();
    if (!message) {
        return false;
    }

    // Keep the heuristic conservative to avoid false positives on long normal answers.
    if (message.length > 220) {
        return false;
    }

    return BACKEND_DEGRADED_RESPONSE_PATTERNS.some(pattern => message.includes(pattern));
};
