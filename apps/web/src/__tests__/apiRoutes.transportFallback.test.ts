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
        expect(payload.backend_mode).toBe("external_backend");
        expect(payload.deliberation_level).toBe("unavailable");
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
        expect(payload.backend_mode).toBe("external_backend");
        expect(payload.deliberation_level).toBe("unavailable");
    });

    it("consent DELETE route returns 502 by default on transport failure", async () => {
        process.env.TONESOUL_BACKEND_URL = "http://127.0.0.1:5999";
        vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("connect ECONNREFUSED"));

        const response = await deleteConsent(makeRequest({ session_id: "s1" }) as never);
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(502);
        expect(payload.error).toBe("Backend unavailable");
        expect(payload.backend_mode).toBe("external_backend");
        expect(payload.deliberation_level).toBe("unavailable");
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
        expect(payload.backend_mode).toBe("external_backend");
        expect(payload.deliberation_level).toBe("unavailable");
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

    it("routes use same-origin primary mocks on vercel when backend url is missing", async () => {
        process.env.VERCEL = "1";
        process.env.VERCEL_URL = "tonesoul52-one.vercel.app";
        // Conversation route now forwards to backend in same-origin mode.
        // Other routes (consent, session-report) still use their own same-origin mock.
        const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
            new Response(
                JSON.stringify({
                    success: true,
                    conversation_id: "conv_mock",
                    created_at: new Date().toISOString(),
                }),
                { status: 200 }
            )
        );

        const conversationResponse = await postConversation(makeRequest({ session_id: "s1" }) as never);
        const conversationPayload = (await conversationResponse.json()) as Record<string, unknown>;
        const consentPostResponse = await postConsent(
            makeRequest({ session_id: "s1", consent_type: "analysis" }) as never
        );
        const consentPostPayload = (await consentPostResponse.json()) as Record<string, unknown>;
        const consentDeleteResponse = await deleteConsent(makeRequest({ session_id: "s1" }) as never);
        const consentDeletePayload = (await consentDeleteResponse.json()) as Record<string, unknown>;
        const reportResponse = await postSessionReport(
            makeRequest({
                history: [
                    { role: "user", content: "hello" },
                    { role: "assistant", content: "hi" },
                ],
            }) as never
        );
        const reportPayload = (await reportResponse.json()) as Record<string, unknown>;

        // Conversation route now forwards to backend
        expect(conversationResponse.status).toBe(200);
        expect(conversationPayload.success).toBe(true);
        expect(conversationPayload.conversation_id).toBe("conv_mock");
        expect(conversationPayload.backend_mode).toBe("same_origin");
        expect(conversationPayload.deliberation_level).toBe("runtime");

        expect(consentPostResponse.status).toBe(200);
        expect(consentPostPayload.backend_mode).toBe("mock_fallback");
        expect(consentPostPayload.deliberation_level).toBe("mock");
        expect(consentPostPayload.fallback_reason).toBe("same_origin_primary");

        expect(consentDeleteResponse.status).toBe(200);
        expect(consentDeletePayload.backend_mode).toBe("mock_fallback");
        expect(consentDeletePayload.deliberation_level).toBe("mock");
        expect(consentDeletePayload.fallback_reason).toBe("same_origin_primary");

        expect(reportResponse.status).toBe(200);
        expect(reportPayload.backend_mode).toBe("mock_fallback");
        expect(reportPayload.deliberation_level).toBe("mock");
        expect(reportPayload.fallback_reason).toBe("same_origin_primary");
        expect(reportPayload.report).toBeTruthy();

        // fetch should have been called at least once (for conversation)
        expect(fetchMock).toHaveBeenCalled();
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
