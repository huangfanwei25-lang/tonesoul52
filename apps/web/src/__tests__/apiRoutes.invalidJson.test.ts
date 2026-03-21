import { afterEach, describe, expect, it, vi } from "vitest";

import { POST as postChat } from "../app/api/chat/route";
import { POST as postConsent, DELETE as deleteConsent } from "../app/api/consent/route";
import { POST as postConversation } from "../app/api/conversation/route";
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
});

describe("API route handlers return 502 for invalid backend JSON", () => {
    it("conversation route returns 502 without mock fallback", async () => {
        process.env.TONESOUL_BACKEND_URL = "http://127.0.0.1:5999";
        const fetchMock = vi
            .spyOn(globalThis, "fetch")
            .mockResolvedValue(new Response("not-json", { status: 201 }));

        const response = await postConversation(makeRequest({ session_id: "s1" }) as never);
        const payload = (await response.json()) as Record<string, unknown>;

        expect(fetchMock).toHaveBeenCalledTimes(1);
        expect(fetchMock).toHaveBeenCalledWith(
            "http://127.0.0.1:5999/api/conversation",
            expect.objectContaining({ method: "POST" })
        );
        expect(response.status).toBe(502);
        expect(payload.error).toBe("Backend returned invalid JSON");
        expect(payload.backend_status).toBe(201);
        expect(payload.backend_mode).toBe("external_backend");
        expect(payload.deliberation_level).toBe("unavailable");
    });

    it("consent POST route returns 502 without mock fallback", async () => {
        process.env.TONESOUL_BACKEND_URL = "http://127.0.0.1:5999";
        vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response("still-not-json", { status: 200 }));

        const response = await postConsent(
            makeRequest({ session_id: "s2", consent_type: "analysis" }) as never
        );
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(502);
        expect(payload.error).toBe("Backend returned invalid JSON");
        expect(payload.backend_status).toBe(200);
        expect(payload.backend_mode).toBe("external_backend");
        expect(payload.deliberation_level).toBe("unavailable");
    });

    it("consent DELETE route returns 502 without mock fallback", async () => {
        process.env.TONESOUL_BACKEND_URL = "http://127.0.0.1:5999";
        vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response("invalid", { status: 200 }));

        const response = await deleteConsent(makeRequest({ session_id: "s3" }) as never);
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(502);
        expect(payload.error).toBe("Backend returned invalid JSON");
        expect(payload.backend_status).toBe(200);
        expect(payload.backend_mode).toBe("external_backend");
        expect(payload.deliberation_level).toBe("unavailable");
    });

    it("chat route returns 502 without mock fallback", async () => {
        process.env.TONESOUL_BACKEND_URL = "http://127.0.0.1:5999";
        vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response("invalid-chat-json", { status: 200 }));

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
        expect(payload.error).toBe("Backend returned invalid JSON");
        expect(payload.backend_status).toBe(200);
        expect(payload.backend_mode).toBe("external_backend");
        expect(payload.deliberation_level).toBe("unavailable");
    });

    it("chat route rejects invalid council_mode type with 400", async () => {
        const fetchMock = vi.spyOn(globalThis, "fetch");
        const response = await postChat(
            makeRequest({
                message: "hello",
                council_mode: { mode: "rules" },
            }) as never
        );
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(400);
        expect(payload.error).toBe("Invalid council_mode");
        expect(fetchMock).not.toHaveBeenCalled();
    });

    it("chat route rejects invalid perspective_config shape with 400", async () => {
        const fetchMock = vi.spyOn(globalThis, "fetch");
        const response = await postChat(
            makeRequest({
                message: "hello",
                perspective_config: { guardian: "rules" },
            }) as never
        );
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(400);
        expect(payload.error).toBe("Invalid perspective_config");
        expect(fetchMock).not.toHaveBeenCalled();
    });

    it("chat route rejects invalid execution_profile with 400", async () => {
        const fetchMock = vi.spyOn(globalThis, "fetch");
        const response = await postChat(
            makeRequest({
                message: "hello",
                execution_profile: "fast_mode",
            }) as never
        );
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(400);
        expect(payload.error).toBe("Invalid execution_profile");
        expect(fetchMock).not.toHaveBeenCalled();
    });

    it("chat route rejects invalid persona custom_roles type with 400", async () => {
        const fetchMock = vi.spyOn(globalThis, "fetch");
        const response = await postChat(
            makeRequest({
                message: "hello",
                persona: {
                    custom_roles: "invalid",
                },
            }) as never
        );
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(400);
        expect(payload.error).toBe("Invalid persona");
        expect(fetchMock).not.toHaveBeenCalled();
    });

    it("chat route rejects non-object elisa_context with 400", async () => {
        const fetchMock = vi.spyOn(globalThis, "fetch");
        const response = await postChat(
            makeRequest({
                message: "hello",
                elisa_context: "elisa_ide",
            }) as never
        );
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(400);
        expect(payload.error).toBe("Invalid elisa_context");
        expect(fetchMock).not.toHaveBeenCalled();
    });

    it("chat route rejects invalid elisa_context workspace.changed_files with 400", async () => {
        const fetchMock = vi.spyOn(globalThis, "fetch");
        const response = await postChat(
            makeRequest({
                message: "hello",
                elisa_context: {
                    source: "elisa_ide",
                    workspace: {
                        changed_files: ["apps/web/src/app/api/chat/route.ts", 123],
                    },
                },
            }) as never
        );
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(400);
        expect(payload.error).toBe("Invalid elisa_context");
        expect(fetchMock).not.toHaveBeenCalled();
    });

    it("chat route rejects elisa_context workspace.changed_files larger than 64 with 400", async () => {
        const fetchMock = vi.spyOn(globalThis, "fetch");
        const response = await postChat(
            makeRequest({
                message: "hello",
                elisa_context: {
                    source: "elisa_ide",
                    workspace: {
                        changed_files: Array.from(
                            { length: 65 },
                            (_, index) => `apps/web/src/file-${index}.ts`
                        ),
                    },
                },
            }) as never
        );
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(400);
        expect(payload.error).toBe("Invalid elisa_context");
        expect(fetchMock).not.toHaveBeenCalled();
    });

    it("session-report route returns 502 without mock fallback", async () => {
        process.env.TONESOUL_BACKEND_URL = "http://127.0.0.1:5999";
        vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response("invalid-report-json", { status: 200 }));

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
        expect(payload.error).toBe("Backend returned invalid JSON");
        expect(payload.backend_status).toBe(200);
        expect(payload.backend_mode).toBe("external_backend");
        expect(payload.deliberation_level).toBe("unavailable");
    });
});
