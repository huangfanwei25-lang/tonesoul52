import { afterEach, describe, expect, it, vi } from "vitest";

import { GET as getBackendHealth } from "../app/api/backend-health/route";

afterEach(() => {
    vi.restoreAllMocks();
    delete process.env.TONESOUL_BACKEND_URL;
    delete process.env.VERCEL;
    delete process.env.VERCEL_URL;
});

describe("backend health route", () => {
    it("returns 200 when backend health probe succeeds", async () => {
        process.env.TONESOUL_BACKEND_URL = "http://127.0.0.1:5000";
        const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
            new Response(JSON.stringify({ status: "ok" }), { status: 200 })
        );

        const response = await getBackendHealth();
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(200);
        expect(payload.ok).toBe(true);
        expect(payload.backend_status).toBe(200);
        expect(fetchMock).toHaveBeenCalledTimes(1);
        expect(fetchMock).toHaveBeenCalledWith(
            "http://127.0.0.1:5000/api/health",
            expect.objectContaining({ method: "GET" })
        );
    });

    it("returns 503 when backend transport fails", async () => {
        process.env.TONESOUL_BACKEND_URL = "http://127.0.0.1:5999";
        vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("connect ECONNREFUSED"));

        const response = await getBackendHealth();
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(503);
        expect(payload.ok).toBe(false);
        expect(payload.reason).toBe("backend_health_transport_error");
    });

    it("returns 503 on Vercel when backend url is missing", async () => {
        process.env.VERCEL = "1";
        const fetchMock = vi.spyOn(globalThis, "fetch");

        const response = await getBackendHealth();
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(503);
        expect(payload.ok).toBe(false);
        expect(payload.config_issue).toBe("missing");
        expect(fetchMock).not.toHaveBeenCalled();
    });

    it("returns 503 when backend health endpoint is not ok", async () => {
        process.env.TONESOUL_BACKEND_URL = "http://127.0.0.1:5000";
        vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response("down", { status: 500 }));

        const response = await getBackendHealth();
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(503);
        expect(payload.ok).toBe(false);
        expect(payload.reason).toBe("backend_health_http_error");
        expect(payload.backend_status).toBe(500);
    });
});
