import { afterEach, describe, expect, it, vi } from "vitest";

import { GET as getGovernanceStatus } from "../app/api/governance-status/route";

afterEach(() => {
    vi.restoreAllMocks();
    delete process.env.TONESOUL_BACKEND_URL;
    delete process.env.TONESOUL_FORCE_SAME_ORIGIN_MOCK;
    delete process.env.VERCEL;
    delete process.env.VERCEL_URL;
});

describe("governance status route", () => {
    it("probes same-origin backend and returns runtime readiness on success", async () => {
        process.env.VERCEL = "1";
        process.env.VERCEL_URL = "tonesoul52-one.vercel.app";
        const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
            new Response(
                JSON.stringify({
                    status: "ok",
                    governance_capability: "runtime_ready",
                    recent_verdicts: [{ gate_decision: "approve", delta_t: 0.23 }],
                }),
                { status: 200 }
            )
        );

        const response = await getGovernanceStatus();
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(200);
        expect(payload.status).toBe("ok");
        expect(payload.backend_mode).toBe("same_origin");
        expect(payload.governance_capability).toBe("runtime_ready");
        expect(payload.deliberation_level).toBe("runtime");
        expect(payload.recent_verdicts).toEqual([{ gate_decision: "approve", delta_t: 0.23 }]);
        expect(payload.elisa).toMatchObject({
            integration_ready: true,
            contract_version: "phase108_p1",
        });
        expect(fetchMock).toHaveBeenCalledWith(
            "https://tonesoul52-one.vercel.app/api/_backend/api/governance_status",
            expect.objectContaining({ method: "GET" })
        );
    });

    it("allows forcing same-origin mock status via env flag", async () => {
        process.env.VERCEL = "1";
        process.env.VERCEL_URL = "tonesoul52-one.vercel.app";
        process.env.TONESOUL_FORCE_SAME_ORIGIN_MOCK = "1";
        const fetchMock = vi.spyOn(globalThis, "fetch");

        const response = await getGovernanceStatus();
        const payload = (await response.json()) as Record<string, unknown>;

        expect(response.status).toBe(200);
        expect(payload.backend_mode).toBe("same_origin");
        expect(payload.governance_capability).toBe("mock_only");
        expect(payload.deliberation_level).toBe("mock");
        expect(payload.reason).toBe("same_origin_forced_mock");
        expect(fetchMock).not.toHaveBeenCalled();
    });

    it("returns runtime governance status when backend health probe succeeds", async () => {
        process.env.TONESOUL_BACKEND_URL = "http://127.0.0.1:5000";
        const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
            new Response(
                JSON.stringify({ status: "ok", governance_capability: "runtime_ready" }),
                { status: 200 }
            )
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
            "http://127.0.0.1:5000/api/governance_status",
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
        expect(payload.reason).toBe("backend_governance_status_transport_error");
        expect(payload.elisa).toMatchObject({ integration_ready: false });
    });
});
