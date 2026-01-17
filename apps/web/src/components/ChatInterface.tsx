"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Loader2, Sparkles, Brain, Shield, Cpu, Lightbulb, ChevronDown, ChevronUp } from "lucide-react";

interface Message {
    id: string;
    role: "user" | "assistant";
    content: string;
    deliberation?: DeliberationData;
    timestamp: Date;
}

interface DeliberationData {
    synthesis?: {
        type: string;
        dominant_voice: string;
        weights: {
            muse: number;
            logos: number;
            aegis: number;
        };
    };
    decision_matrix?: {
        user_hidden_intent: string;
        strategy_name: string;
        intended_effect: string;
        tone_tag: string;
    };
    tension_zone?: {
        zone: string;
        calculation_note: string;
    };
    next_moves?: Array<{ label: string; text: string }>;
}

interface ChatInterfaceProps {
    sessionId: string;
    conversationId: string | null;
    onNewConversation: () => Promise<string>;
}

export default function ChatInterface({ sessionId, conversationId, onNewConversation }: ChatInterfaceProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [showDeliberation, setShowDeliberation] = useState<string | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const sendMessage = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage: Message = {
            id: `msg_${Date.now()}`,
            role: "user",
            content: input,
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);

        try {
            // Get or create conversation
            let convId = conversationId;
            if (!convId) {
                convId = await onNewConversation();
            }

            // Call API
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    conversation_id: convId,
                    message: userMessage.content,
                }),
            });

            const data = await response.json();

            const assistantMessage: Message = {
                id: `msg_${Date.now()}_ai`,
                role: "assistant",
                content: data.response || "抱歉，我遇到了一些問題...",
                deliberation: data.deliberation,
                timestamp: new Date(),
            };

            setMessages((prev) => [...prev, assistantMessage]);
        } catch (error) {
            console.error("Chat error:", error);
            setMessages((prev) => [
                ...prev,
                {
                    id: `msg_${Date.now()}_error`,
                    role: "assistant",
                    content: "連線錯誤，請稍後再試。",
                    timestamp: new Date(),
                },
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSuggestionClick = (text: string) => {
        setInput(text);
    };

    const getTensionZoneColor = (zone: string) => {
        switch (zone) {
            case "echo_chamber":
                return "bg-blue-100 text-blue-700 border-blue-200";
            case "sweet_spot":
                return "bg-purple-100 text-purple-700 border-purple-200";
            case "chaos":
                return "bg-red-100 text-red-700 border-red-200";
            default:
                return "bg-slate-100 text-slate-700 border-slate-200";
        }
    };

    const getZoneLabel = (zone: string) => {
        switch (zone) {
            case "echo_chamber":
                return "同溫層";
            case "sweet_spot":
                return "甜蜜點";
            case "chaos":
                return "混沌";
            default:
                return zone;
        }
    };

    return (
        <div className="flex flex-col h-full bg-slate-50">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-64 text-slate-400">
                        <Brain className="w-16 h-16 mb-4 opacity-30" />
                        <p className="text-lg font-medium">ToneSoul Navigator</p>
                        <p className="text-sm">開始對話，體驗內在審議...</p>
                    </div>
                )}

                {messages.map((message) => (
                    <div
                        key={message.id}
                        className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
                    >
                        <div
                            className={`max-w-[80%] rounded-2xl p-4 ${message.role === "user"
                                    ? "bg-indigo-600 text-white"
                                    : "bg-white border border-slate-200 shadow-sm"
                                }`}
                        >
                            <p className={`leading-relaxed ${message.role === "user" ? "text-white" : "text-slate-800"}`}>
                                {message.content}
                            </p>

                            {/* Deliberation Toggle */}
                            {message.role === "assistant" && message.deliberation && (
                                <div className="mt-3 pt-3 border-t border-slate-100">
                                    <button
                                        onClick={() =>
                                            setShowDeliberation(
                                                showDeliberation === message.id ? null : message.id
                                            )
                                        }
                                        className="flex items-center gap-2 text-xs text-slate-500 hover:text-indigo-600 transition-colors"
                                    >
                                        <Sparkles className="w-3 h-3" />
                                        <span>內在審議</span>
                                        {showDeliberation === message.id ? (
                                            <ChevronUp className="w-3 h-3" />
                                        ) : (
                                            <ChevronDown className="w-3 h-3" />
                                        )}
                                    </button>

                                    {showDeliberation === message.id && (
                                        <div className="mt-3 space-y-3 animate-in slide-in-from-top-2">
                                            {/* Tension Zone */}
                                            {message.deliberation.tension_zone && (
                                                <div
                                                    className={`px-3 py-2 rounded-lg border text-xs ${getTensionZoneColor(
                                                        message.deliberation.tension_zone.zone
                                                    )}`}
                                                >
                                                    <span className="font-bold">
                                                        {getZoneLabel(message.deliberation.tension_zone.zone)}
                                                    </span>
                                                    <span className="ml-2 opacity-70">
                                                        {message.deliberation.tension_zone.calculation_note}
                                                    </span>
                                                </div>
                                            )}

                                            {/* Decision Matrix */}
                                            {message.deliberation.decision_matrix && (
                                                <div className="grid grid-cols-2 gap-2 text-xs">
                                                    <div className="bg-slate-50 p-2 rounded-lg">
                                                        <span className="text-slate-400 block">潛台詞</span>
                                                        <span className="text-slate-700">
                                                            {message.deliberation.decision_matrix.user_hidden_intent}
                                                        </span>
                                                    </div>
                                                    <div className="bg-slate-50 p-2 rounded-lg">
                                                        <span className="text-slate-400 block">戰術</span>
                                                        <span className="text-slate-700">
                                                            {message.deliberation.decision_matrix.strategy_name}
                                                        </span>
                                                    </div>
                                                </div>
                                            )}

                                            {/* Weights */}
                                            {message.deliberation.synthesis?.weights && (
                                                <div className="flex gap-2 text-xs">
                                                    <div className="flex items-center gap-1 bg-amber-50 px-2 py-1 rounded-full">
                                                        <Lightbulb className="w-3 h-3 text-amber-500" />
                                                        <span>
                                                            {Math.round(
                                                                message.deliberation.synthesis.weights.muse * 100
                                                            )}
                                                            %
                                                        </span>
                                                    </div>
                                                    <div className="flex items-center gap-1 bg-blue-50 px-2 py-1 rounded-full">
                                                        <Cpu className="w-3 h-3 text-blue-500" />
                                                        <span>
                                                            {Math.round(
                                                                message.deliberation.synthesis.weights.logos * 100
                                                            )}
                                                            %
                                                        </span>
                                                    </div>
                                                    <div className="flex items-center gap-1 bg-emerald-50 px-2 py-1 rounded-full">
                                                        <Shield className="w-3 h-3 text-emerald-500" />
                                                        <span>
                                                            {Math.round(
                                                                message.deliberation.synthesis.weights.aegis * 100
                                                            )}
                                                            %
                                                        </span>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    )}

                                    {/* Suggested Replies */}
                                    {message.deliberation.next_moves &&
                                        message.deliberation.next_moves.length > 0 && (
                                            <div className="mt-3 flex flex-wrap gap-2">
                                                {message.deliberation.next_moves.map((move, idx) => (
                                                    <button
                                                        key={idx}
                                                        onClick={() => handleSuggestionClick(move.text)}
                                                        className="text-xs bg-slate-50 hover:bg-indigo-50 border border-slate-200 hover:border-indigo-200 rounded-lg px-3 py-1.5 transition-colors"
                                                    >
                                                        <span className="font-medium text-indigo-600">
                                                            {move.label}
                                                        </span>
                                                    </button>
                                                ))}
                                            </div>
                                        )}
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm flex items-center gap-2">
                            <Loader2 className="w-4 h-4 animate-spin text-indigo-600" />
                            <span className="text-sm text-slate-500">思考中...</span>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t border-slate-200 bg-white">
                <div className="flex gap-3">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                        placeholder="輸入訊息..."
                        disabled={isLoading}
                        className="flex-1 px-4 py-3 bg-slate-100 rounded-xl border-0 focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all disabled:opacity-50"
                    />
                    <button
                        onClick={sendMessage}
                        disabled={isLoading || !input.trim()}
                        className="px-4 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg shadow-indigo-200"
                    >
                        {isLoading ? (
                            <Loader2 className="w-5 h-5 animate-spin" />
                        ) : (
                            <Send className="w-5 h-5" />
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
}
