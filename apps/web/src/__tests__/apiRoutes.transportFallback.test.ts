import { afterEach, describe, expect, it, vi } from "vitest";

import { POST as postConversation } from "../app/api/conversation/route";
import { POST as postConsent, DELETE as deleteConsent } from "../app/api/consent/route";
import { POST as postSessionReport } from "../app/api/session-report/route";

type JsonRequest = {
    json: () => Promise<unknown>;
};

function makeRequest(body: unknown): JsonRequest {
    return {
        json: async () => body,
    };
}

afterEach(() => {
    vi.restoreAllMocks();
    delete process.env.TONESOUL_BACKEND_URL;
    delete process.env.TONESOUL_ENABLE_CONVERSATION_MOCK_FALLBACK;
    delete process.env.TONESOUL_ENABLE_CONSENT_MOCK_FALLBACK;
    delete process.env.TONESOUL_ENABLE_SESSION_REPORT_MOCK_FALLBACK;
    delete process.env.VERCEL;
    delete process.env.VERCEL_URL;
});

describe("route transport fallback policy", () => {
    it("conversation route returns 502 by default on transport failure", async () => {
        process.env.TONESOUL_BACKEND_URL = "http://127.0.0.1:5999";
        vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("connect ECONNREFUSED"));

        const response = await postConversation(makeRequest({ session_id: "s1" }) as never);
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(502);
        expect(payload.error).toBe("Backend unavailable");
        expect(payload.backend_mode).toBeUndefined();
    });

    it("conversation route allows fallback only when env is enabled", async () => {
        process.env.TONESOUL_BACKEND_URL = "http://127.0.0.1:5999";
        process.env.TONESOUL_ENABLE_CONVERSATION_MOCK_FALLBACK = "1";
        vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("timeout"));

        const response = await postConversation(makeRequest({ session_id: "s1" }) as never);
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(200);
        expect(payload.backend_mode).toBe("mock_fallback");
        expect(payload.fallback_reason).toBe("transport_failure");
    });

    it("consent POST route returns 502 by default on transport failure", async () => {
        process.env.TONESOUL_BACKEND_URL = "http://127.0.0.1:5999";
        vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("connect ECONNREFUSED"));

        const response = await postConsent(makeRequest({ consent_type: "research" }) as never);
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(502);
        expect(payload.error).toBe("Backend unavailable");
        expect(payload.backend_mode).toBeUndefined();
    });

    it("consent DELETE route returns 502 by default on transport failure", async () => {
        process.env.TONESOUL_BACKEND_URL = "http://127.0.0.1:5999";
        vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("connect ECONNREFUSED"));

        const response = await deleteConsent(makeRequest({ session_id: "s1" }) as never);
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(502);
        expect(payload.error).toBe("Backend unavailable");
        expect(payload.backend_mode).toBeUndefined();
    });

    it("consent route allows fallback only when env is enabled", async () => {
        process.env.TONESOUL_BACKEND_URL = "http://127.0.0.1:5999";
        process.env.TONESOUL_ENABLE_CONSENT_MOCK_FALLBACK = "1";
        vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("timeout"));

        const response = await postConsent(makeRequest({ consent_type: "research" }) as never);
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(200);
        expect(payload.backend_mode).toBe("mock_fallback");
        expect(payload.fallback_reason).toBe("transport_failure");
    });

    it("session-report route returns 502 by default on transport failure", async () => {
        process.env.TONESOUL_BACKEND_URL = "http://127.0.0.1:5999";
        vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("connect ECONNREFUSED"));

        const response = await postSessionReport(
            makeRequest({
                history: [
                    { role: "user", content: "hello" },
                    { role: "assistant", content: "hi" },
                ],
            }) as never
        );
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(502);
        expect(payload.error).toBe("Backend unavailable");
        expect(payload.backend_mode).toBeUndefined();
    });

    it("session-report route allows fallback only when env is enabled", async () => {
        process.env.TONESOUL_BACKEND_URL = "http://127.0.0.1:5999";
        process.env.TONESOUL_ENABLE_SESSION_REPORT_MOCK_FALLBACK = "1";
        vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("timeout"));

        const response = await postSessionReport(
            makeRequest({
                history: [
                    { role: "user", content: "hello" },
                    { role: "assistant", content: "hi" },
                ],
            }) as never
        );
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(200);
        expect(payload.backend_mode).toBe("mock_fallback");
        expect(payload.fallback_reason).toBe("transport_failure");
        expect(payload.report).toBeTruthy();
    });

    it("routes use same-origin backend on vercel when backend url is missing", async () => {
        process.env.VERCEL = "1";
        process.env.VERCEL_URL = "tonesoul52-one.vercel.app";
        const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
            new Response(
                JSON.stringify({
                    success: true,
                    conversation_id: "conv_same_origin",
                    session_id: "s1",
                }),
                { status: 200 }
            )
        );

        const response = await postConversation(makeRequest({ session_id: "s1" }) as never);
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(200);
        expect(payload.success).toBe(true);
        expect(fetchMock).toHaveBeenCalledTimes(1);
        expect(fetchMock.mock.calls[0]?.[0]).toBe(
            "https://tonesoul52-one.vercel.app/api/_backend/api/conversation"
        );
    });

    it("routes return 503 on vercel when backend points to localhost", async () => {
        process.env.VERCEL = "1";
        process.env.TONESOUL_BACKEND_URL = "http://127.0.0.1:5000";
        const fetchMock = vi.spyOn(globalThis, "fetch");

        const response = await postConversation(makeRequest({ session_id: "s1" }) as never);
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(503);
        expect(payload.error).toBe("Backend configuration invalid for Vercel runtime");
        expect(payload.config_issue).toBe("local_address");
        expect(fetchMock).not.toHaveBeenCalled();
    });

    it("routes return 503 on vercel when backend url is malformed", async () => {
        process.env.VERCEL = "1";
        process.env.TONESOUL_BACKEND_URL = "mock";
        const fetchMock = vi.spyOn(globalThis, "fetch");

        const response = await postConversation(makeRequest({ session_id: "s1" }) as never);
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(503);
        expect(payload.error).toBe("Backend configuration invalid for Vercel runtime");
        expect(payload.config_issue).toBe("invalid_url");
        expect(fetchMock).not.toHaveBeenCalled();
    });
});
