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
    "llm service unavailable",
    "model service unavailable",
    "llm unavailable",
    "llm 服務不可用",
    "llm服务不可用",
    "模型服務不可用",
    "模型服务不可用",
    "模型不可用",
    "抱歉 llm 服務不可用",
    "抱歉 llm服务不可用",
    "抱歉 模型服務不可用",
    "抱歉 模型服务不可用",
];

const BACKEND_DEGRADED_RESPONSE_REGEXES = [
    /\bllm\b.*\b(service|model)?\s*unavailable\b/i,
    /\bmodel\b.*\bservice\b.*\bunavailable\b/i,
    /\bllm\b.*(不可用|無法使用|无法使用)/i,
    /(模型|model).*(服務|服务|service).*(不可用|無法使用|无法使用|unavailable)/i,
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

    const rawMessage = responseText.trim();
    if (!rawMessage) {
        return false;
    }

    const message = rawMessage.toLowerCase();
    const normalized = message.replace(/[，。,.!?！？:：\s]+/g, " ").trim();

    // Keep the heuristic conservative to avoid false positives on long normal answers.
    if (normalized.length > 220) {
        return false;
    }

    if (BACKEND_DEGRADED_RESPONSE_PATTERNS.some(pattern => normalized.includes(pattern))) {
        return true;
    }

    return BACKEND_DEGRADED_RESPONSE_REGEXES.some(regex => regex.test(normalized));
};
