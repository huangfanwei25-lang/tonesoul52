import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.TONESOUL_BACKEND_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { session_id } = body;

        // Generate conversation ID
        const conversationId = `conv_${Date.now()}_${Math.random().toString(36).substr(2, 8)}`;

        // In production, call Python backend
        // const response = await fetch(`${BACKEND_URL}/api/conversation`, {
        //   method: "POST",
        //   headers: { "Content-Type": "application/json" },
        //   body: JSON.stringify({ session_id }),
        // });

        return NextResponse.json({
            success: true,
            conversation_id: conversationId,
            session_id: session_id,
            created_at: new Date().toISOString(),
        });
    } catch (error) {
        console.error("Conversation API error:", error);
        return NextResponse.json(
            { error: "Failed to create conversation" },
            { status: 500 }
        );
    }
}
