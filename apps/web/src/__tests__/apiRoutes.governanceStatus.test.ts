import { afterEach, describe, expect, it, vi } from "vitest";

import { GET as getGovernanceStatus } from "../app/api/governance-status/route";

afterEach(() => {
    vi.restoreAllMocks();
    delete process.env.TONESOUL_BACKEND_URL;
    delete process.env.VERCEL;
    delete process.env.VERCEL_URL;
});

describe("governance status route", () => {
    it("returns same-origin governance status on vercel when backend url is missing", async () => {
        process.env.VERCEL = "1";
        process.env.VERCEL_URL = "tonesoul52-one.vercel.app";
        const fetchMock = vi.spyOn(globalThis, "fetch");

        const response = await getGovernanceStatus();
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(200);
        expect(payload.status).toBe("ok");
        expect(payload.backend_mode).toBe("same_origin");
        expect(payload.governance_capability).toBe("mock_only");
        expect(payload.deliberation_level).toBe("mock");
        expect(payload.elisa).toMatchObject({
            integration_ready: true,
            contract_version: "phase108_p1",
        });
        expect(fetchMock).not.toHaveBeenCalled();
    });

    it("returns runtime governance status when backend health probe succeeds", async () => {
        process.env.TONESOUL_BACKEND_URL = "http://127.0.0.1:5000";
        const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
            new Response(JSON.stringify({ status: "ok" }), { status: 200 })
        );

        const response = await getGovernanceStatus();
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(200);
        expect(payload.status).toBe("ok");
        expect(payload.backend_mode).toBe("external_backend");
        expect(payload.governance_capability).toBe("runtime_ready");
        expect(payload.deliberation_level).toBe("runtime");
        expect(payload.elisa).toMatchObject({ integration_ready: true });
        expect(fetchMock).toHaveBeenCalledWith(
            "http://127.0.0.1:5000/api/health",
            expect.objectContaining({ method: "GET" })
        );
    });

    it("returns degraded governance status when backend transport fails", async () => {
        process.env.TONESOUL_BACKEND_URL = "http://127.0.0.1:5999";
        vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("connect ECONNREFUSED"));

        const response = await getGovernanceStatus();
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(503);
        expect(payload.status).toBe("degraded");
        expect(payload.governance_capability).toBe("unavailable");
        expect(payload.reason).toBe("backend_health_transport_error");
        expect(payload.elisa).toMatchObject({ integration_ready: false });
    });
});
