import { describe, expect, it } from "vitest";

import {
    BACKEND_FALLBACK_REASON_LABEL,
    classifyBackendFallbackReason,
} from "../lib/chatFallback";

describe("classifyBackendFallbackReason", () => {
    it("classifies timeout-like errors", () => {
        expect(classifyBackendFallbackReason(new Error("Request timed out"))).toBe("timeout");
        expect(classifyBackendFallbackReason(new Error("AbortError"))).toBe("timeout");
    });

    it("classifies transport errors as unreachable", () => {
        expect(classifyBackendFallbackReason(new Error("Failed to fetch"))).toBe("backend_unreachable");
        expect(classifyBackendFallbackReason(new Error("connect ECONNREFUSED"))).toBe("backend_unreachable");
        expect(classifyBackendFallbackReason("backend_health_transport_error")).toBe("backend_unreachable");
    });

    it("falls back to backend_error for unknown failures", () => {
        expect(classifyBackendFallbackReason(new Error("500 internal exception"))).toBe("backend_error");
        expect(classifyBackendFallbackReason("unexpected")).toBe("backend_error");
    });
});

describe("BACKEND_FALLBACK_REASON_LABEL", () => {
    it("contains display labels for all supported reason codes", () => {
        expect(BACKEND_FALLBACK_REASON_LABEL.timeout).toBeTruthy();
        expect(BACKEND_FALLBACK_REASON_LABEL.backend_unreachable).toBeTruthy();
        expect(BACKEND_FALLBACK_REASON_LABEL.backend_error).toBeTruthy();
    });
});
