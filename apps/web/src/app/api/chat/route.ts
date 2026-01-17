import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.TONESOUL_BACKEND_URL || "http://localhost:8000";

// Mock deliberation response for demo
function generateMockDeliberation(message: string) {
    const isQuestion = message.includes("?") || message.includes("？");
    const isEmotional = /[煩累難過不開心憂傷焦慮]/.test(message);

    let tensionZone = "sweet_spot";
    let dominantVoice = "muse";

    if (isEmotional) {
        tensionZone = "sweet_spot";
        dominantVoice = "aegis";
    } else if (isQuestion) {
        dominantVoice = "logos";
    }

    return {
        synthesis: {
            type: "weighted_fusion",
            dominant_voice: dominantVoice,
            weights: {
                muse: dominantVoice === "muse" ? 0.45 : 0.30,
                logos: dominantVoice === "logos" ? 0.45 : 0.35,
                aegis: dominantVoice === "aegis" ? 0.45 : 0.25,
            },
        },
        decision_matrix: {
            user_hidden_intent: isEmotional ? "情緒抒發，需要陪伴" : "探索性對話",
            strategy_name: isEmotional ? "張力緩解策略" : "深度連結策略",
            intended_effect: isEmotional ? "降低情緒張力，建立理解" : "建立有意義的深層對話",
            tone_tag: isEmotional ? "empathetic" : "warm",
        },
        tension_zone: {
            zone: tensionZone,
            calculation_note: `張力值計算中，觀點${tensionZone === "sweet_spot" ? "適度摩擦" : "過於一致"}`,
        },
        next_moves: [
            { label: "深入探索", text: "可以再多說一點嗎？" },
            { label: "換個角度", text: "如果從另一個角度來看呢？" },
        ],
    };
}

// Mock AI response
function generateMockResponse(message: string): string {
    const responses: { [key: string]: string } = {
        default: "我理解你的想法。能讓我更深入了解一下你的思考嗎？",
        question: "這是一個很好的問題。讓我從幾個角度來思考...",
        emotional: "我聽到了你的感受。在這種時刻，最重要的是先讓自己安定下來。",
    };

    const isQuestion = message.includes("?") || message.includes("？");
    const isEmotional = /[煩累難過不開心憂傷焦慮]/.test(message);

    if (isEmotional) return responses.emotional;
    if (isQuestion) return responses.question;
    return responses.default;
}

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { conversation_id, message } = body;

        // In production, call Python backend
        // const response = await fetch(`${BACKEND_URL}/api/chat`, {
        //   method: "POST",
        //   headers: { "Content-Type": "application/json" },
        //   body: JSON.stringify({ conversation_id, message }),
        // });
        // return NextResponse.json(await response.json());

        // Mock response for demo
        const mockResponse = generateMockResponse(message);
        const mockDeliberation = generateMockDeliberation(message);

        // Simulate processing delay
        await new Promise((resolve) => setTimeout(resolve, 500 + Math.random() * 1000));

        return NextResponse.json({
            response: mockResponse,
            conversation_id: conversation_id,
            deliberation: mockDeliberation,
            timestamp: new Date().toISOString(),
        });
    } catch (error) {
        console.error("Chat API error:", error);
        return NextResponse.json(
            { error: "Failed to process message" },
            { status: 500 }
        );
    }
}
