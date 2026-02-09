import { afterEach, describe, expect, it, vi } from "vitest";

import { POST as postChat } from "../app/api/chat/route";

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
    delete process.env.TONESOUL_ENABLE_CHAT_MOCK_FALLBACK;
    delete process.env.VERCEL;
    delete process.env.VERCEL_URL;
});

describe("chat route transport fallback behavior", () => {
    it("returns 502 when backend transport fails and mock fallback is disabled", async () => {
        process.env.TONESOUL_BACKEND_URL = "http://127.0.0.1:5999";
        vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("connect ECONNREFUSED"));

        const response = await postChat(
            makeRequest({
                conversation_id: "c1",
                message: "hello",
                history: [{ role: "user", content: "hello" }],
                full_analysis: false,
            }) as never
        );
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(502);
        expect(payload.error).toBe("Backend unavailable");
        expect(payload.backend_mode).toBeUndefined();
    });

    it("returns mock fallback only when explicitly enabled", async () => {
        process.env.TONESOUL_BACKEND_URL = "http://127.0.0.1:5999";
        process.env.TONESOUL_ENABLE_CHAT_MOCK_FALLBACK = "1";
        vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("timeout"));

        const response = await postChat(
            makeRequest({
                conversation_id: "c1",
                message: "hello",
                history: [{ role: "user", content: "hello" }],
                full_analysis: false,
            }) as never
        );
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(200);
        expect(payload.backend_mode).toBe("mock_fallback");
        expect(payload.fallback_reason).toBe("transport_failure");
        expect(typeof payload.response).toBe("string");
    });

    it("returns 503 on vercel when backend url is missing or localhost", async () => {
        process.env.VERCEL = "1";

        const fetchMock = vi.spyOn(globalThis, "fetch");
        const response = await postChat(
            makeRequest({
                conversation_id: "c1",
                message: "hello",
                history: [{ role: "user", content: "hello" }],
                full_analysis: false,
            }) as never
        );
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(503);
        expect(payload.error).toBe("Backend configuration invalid for Vercel runtime");
        expect(fetchMock).not.toHaveBeenCalled();
    });

    it("returns 503 on vercel when backend url is malformed", async () => {
        process.env.VERCEL = "1";
        process.env.TONESOUL_BACKEND_URL = "mock";

        const fetchMock = vi.spyOn(globalThis, "fetch");
        const response = await postChat(
            makeRequest({
                conversation_id: "c1",
                message: "hello",
                history: [{ role: "user", content: "hello" }],
                full_analysis: false,
            }) as never
        );
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(503);
        expect(payload.error).toBe("Backend configuration invalid for Vercel runtime");
        expect(payload.config_issue).toBe("invalid_url");
        expect(fetchMock).not.toHaveBeenCalled();
    });

    it("normalizes rules_only council_mode before forwarding", async () => {
        process.env.TONESOUL_BACKEND_URL = "http://127.0.0.1:5000";
        const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
            new Response(JSON.stringify({ response: "ok" }), { status: 200 })
        );

        const response = await postChat(
            makeRequest({
                conversation_id: "c1",
                message: "hello",
                history: [],
                full_analysis: false,
                council_mode: "rules_only",
            }) as never
        );
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(200);
        expect(payload.response).toBe("ok");
        expect(fetchMock).toHaveBeenCalledTimes(1);
        const [, requestInit] = fetchMock.mock.calls[0] as [string, RequestInit];
        const parsedBody = JSON.parse(String(requestInit.body)) as Record<string, unknown>;
        expect(parsedBody.council_mode).toBe("rules");
    });
});
