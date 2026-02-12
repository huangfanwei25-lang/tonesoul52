import { NextResponse } from "next/server";
import { getBackendUrl } from "../_shared/backendConfig";

export async function GET() {
    const backendUrl = getBackendUrl();
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 6000);

    try {
        const res = await fetch(`${backendUrl}/api/llm/models`, {
            method: "GET",
            headers: { Accept: "application/json" },
            signal: controller.signal,
            cache: "no-store",
        });
        const data = await res.json();
        return NextResponse.json(data);
    } catch {
        return NextResponse.json({ available: false, models: [], reason: "backend_unreachable" });
    } finally {
        clearTimeout(timeout);
    }
}
