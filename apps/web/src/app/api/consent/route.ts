import { NextRequest, NextResponse } from "next/server";

// Mock API - In production, this would call Python backend
const BACKEND_URL = process.env.TONESOUL_BACKEND_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { consent_type } = body;

        // Generate session ID
        const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

        // In production, call Python backend
        // const response = await fetch(`${BACKEND_URL}/api/consent`, {
        //   method: "POST",
        //   headers: { "Content-Type": "application/json" },
        //   body: JSON.stringify({ session_id: sessionId, consent_type }),
        // });

        return NextResponse.json({
            success: true,
            session_id: sessionId,
            consent_type: consent_type,
            consent_version: "1.0",
            timestamp: new Date().toISOString(),
        });
    } catch (error) {
        console.error("Consent API error:", error);
        return NextResponse.json(
            { error: "Failed to record consent" },
            { status: 500 }
        );
    }
}

export async function DELETE(request: NextRequest) {
    try {
        const body = await request.json();
        const { session_id } = body;

        // In production, call Python backend to delete data
        // await fetch(`${BACKEND_URL}/api/consent/${session_id}`, { method: "DELETE" });

        return NextResponse.json({
            success: true,
            message: "Consent withdrawn and data deleted",
        });
    } catch (error) {
        console.error("Withdraw consent error:", error);
        return NextResponse.json(
            { error: "Failed to withdraw consent" },
            { status: 500 }
        );
    }
}
