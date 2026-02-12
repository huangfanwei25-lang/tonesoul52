import { NextRequest, NextResponse } from "next/server";
import { getBackendUrl } from "../_shared/backendConfig";

export async function POST(request: NextRequest) {
    const backendUrl = getBackendUrl();
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000);

    try {
        const body = await request.json();
        const res = await fetch(`${backendUrl}/api/llm/switch`, {
            method: "POST",
            headers: { "Content-Type": "application/json", Accept: "application/json" },
            body: JSON.stringify(body),
            signal: controller.signal,
            cache: "no-store",
        });
        const data = await res.json();
        return NextResponse.json(data, { status: res.status });
    } catch {
        return NextResponse.json(
            { success: false, error: "Backend unreachable" },
            { status: 503 }
        );
    } finally {
        clearTimeout(timeout);
    }
}
