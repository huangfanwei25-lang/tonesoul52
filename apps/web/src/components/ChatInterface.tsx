"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Send, Loader2, Brain, ChevronDown, ChevronUp, AlertTriangle, MessageSquare, MoveRight } from "lucide-react";
import { ApiSettings } from "./SettingsModal";
import { Message as DBMessage, DeliberationData, Conversation, saveConversation } from "@/lib/db";
import CouncilChamber from "./CouncilChamber";
import SoulStateMeter from "./SoulStateMeter";
import TacticalDashboard from "./TacticalDashboard";

interface Message extends Omit<DBMessage, 'timestamp'> {
    timestamp: Date;
}

interface ChatInterfaceProps {
    conversation: Conversation | null;
    apiSettings: ApiSettings | null;
    onConversationUpdate: (conv: Conversation) => void;
}

// ToneStream v2.5 完整版 Prompt
const INTERNAL_DELIBERATION_PROMPT = (userMessage: string, historyContext: string) => `
你是一個具備「內在審議」機制的 AI。你必須時刻監控自己的「認知張力 (Cognitive Tension)」。

【張力運算邏輯模型】:
E (Entropy) = w1 * |Philosopher - Engineer| + w2 * Guardian_Risk
- 若觀點一致，E < 0.3 (同溫層)
- 若觀點互補且有張力，E 在 0.3-0.7 (甜蜜點)
- 若邏輯互斥或倫理警告，E > 0.7 (混沌)

【歷史脈絡】:
${historyContext || "無"}

【當前輸入】:
"${userMessage}"

請執行：
1. **議會辯論**：三方觀點碰撞。內容請豐富一點，展現思考深度。
2. **熵值計算**：根據上述公式邏輯估算 E 值。
3. **戰術決策**：制定回應策略。

輸出 JSON (嚴格遵守格式，使用繁體中文):
{
  "council_chamber": {
    "philosopher": { "stance": "觀點...", "conflict_point": "與其他觀點的摩擦..." },
    "engineer": { "stance": "觀點...", "conflict_point": "與其他觀點的摩擦..." },
    "guardian": { "stance": "觀點...", "conflict_point": "潛在風險..." }
  },
  "entropy_meter": {
    "value": 0.5,
    "status": "Healthy Friction",
    "calculation_note": "簡述為何判定為此數值..."
  },
  "decision_matrix": {
    "user_hidden_intent": "用戶可能的潛台詞...",
    "ai_strategy_name": "執行戰術名稱...",
    "intended_effect": "預期達到的效果...",
    "tone_tag": "語氣標籤"
  },
  "final_synthesis": {
    "response_text": "最終綜合回應..."
  },
  "next_moves": [
    { "label": "選項A標籤", "text": "建議的跟進問題..." },
    { "label": "選項B標籤", "text": "另一個跟進問題..." }
  ]
}
`;

// 解析 LLM JSON 回應
const parseLLMResponse = (text: string): DeliberationData | null => {
    try {
        return JSON.parse(text);
    } catch {
        // 嘗試提取 JSON
        const jsonMatch = text.match(/```json\s*([\s\S]*?)\s*```/);
        if (jsonMatch?.[1]) {
            try {
                return JSON.parse(jsonMatch[1]);
            } catch {
                return null;
            }
        }
        // 直接嘗試
        const braceStart = text.indexOf('{');
        const braceEnd = text.lastIndexOf('}');
        if (braceStart !== -1 && braceEnd !== -1) {
            try {
                return JSON.parse(text.slice(braceStart, braceEnd + 1));
            } catch {
                return null;
            }
        }
        return null;
    }
};

export default function ChatInterface({ conversation, apiSettings, onConversationUpdate }: ChatInterfaceProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // 載入對話訊息
    useEffect(() => {
        if (conversation) {
            setMessages(conversation.messages.map(m => ({
                ...m,
                timestamp: new Date(m.timestamp)
            })));
        } else {
            setMessages([]);
        }
    }, [conversation?.id]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const toggleDeliberation = (nodeId: string) => {
        setExpandedNodes(prev => {
            const newSet = new Set(prev);
            if (newSet.has(nodeId)) {
                newSet.delete(nodeId);
            } else {
                newSet.add(nodeId);
            }
            return newSet;
        });
    };

    const getHistoryContext = () => {
        return messages.slice(-6).map(m => ({
            role: m.role,
            content: m.content.slice(0, 200)
        }));
    };

    const callGeminiWithDeliberation = async (userMessage: string): Promise<{ text: string; deliberation: DeliberationData | null }> => {
        if (!apiSettings?.apiKey) throw new Error("請先設定 API Key");

        const prompt = INTERNAL_DELIBERATION_PROMPT(userMessage, JSON.stringify(getHistoryContext()));

        const response = await fetch(
            `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiSettings.apiKey}`,
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    contents: [{ role: "user", parts: [{ text: prompt }] }],
                    generationConfig: { responseMimeType: "application/json" },
                }),
            }
        );

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error?.message || "API 錯誤");
        }

        const data = await response.json();
        const rawText = data.candidates?.[0]?.content?.parts?.[0]?.text || "{}";
        const deliberation = parseLLMResponse(rawText);

        return {
            text: deliberation?.final_synthesis?.response_text || "抱歉，我無法生成回應。",
            deliberation,
        };
    };

    const callOpenAIWithDeliberation = async (userMessage: string): Promise<{ text: string; deliberation: DeliberationData | null }> => {
        if (!apiSettings?.apiKey) throw new Error("請先設定 API Key");

        const prompt = INTERNAL_DELIBERATION_PROMPT(userMessage, JSON.stringify(getHistoryContext()));

        const response = await fetch("https://api.openai.com/v1/chat/completions", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${apiSettings.apiKey}`,
            },
            body: JSON.stringify({
                model: "gpt-4o-mini",
                messages: [{ role: "user", content: prompt }],
                response_format: { type: "json_object" },
            }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error?.message || "API 錯誤");
        }

        const data = await response.json();
        const rawText = data.choices?.[0]?.message?.content || "{}";
        const deliberation = parseLLMResponse(rawText);

        return {
            text: deliberation?.final_synthesis?.response_text || "抱歉，我無法生成回應。",
            deliberation,
        };
    };

    const sendMessage = useCallback(async () => {
        if (!input.trim() || isLoading || !conversation) return;

        const userMessage: Message = {
            id: `msg_${Date.now()}`,
            role: "user",
            content: input,
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);

        try {
            let result: { text: string; deliberation: DeliberationData | null };

            if (apiSettings?.apiKey) {
                if (apiSettings.provider === "gemini") {
                    result = await callGeminiWithDeliberation(userMessage.content);
                } else {
                    result = await callOpenAIWithDeliberation(userMessage.content);
                }
            } else {
                // Mock response
                result = {
                    text: "請先設定 API Key 才能使用 AI 對話功能。點擊右上角的設定按鈕。",
                    deliberation: null,
                };
            }

            const assistantMessage: Message = {
                id: `msg_${Date.now()}_ai`,
                role: "assistant",
                content: result.text,
                deliberation: result.deliberation || undefined,
                timestamp: new Date(),
            };

            const newMessages = [...messages, userMessage, assistantMessage];
            setMessages(newMessages.map(m => ({ ...m, timestamp: new Date(m.timestamp) })));

            // 儲存到 IndexedDB
            const updatedConversation: Conversation = {
                ...conversation,
                title: conversation.messages.length === 0
                    ? userMessage.content.slice(0, 50) + (userMessage.content.length > 50 ? '...' : '')
                    : conversation.title,
                updatedAt: Date.now(),
                messages: newMessages.map(m => ({
                    ...m,
                    timestamp: m.timestamp.getTime(),
                })),
            };
            await saveConversation(updatedConversation);
            onConversationUpdate(updatedConversation);

            // 自動展開最新的審議
            setExpandedNodes(prev => new Set(prev).add(assistantMessage.id));

        } catch (error) {
            console.error("Chat error:", error);
            const errorMessage: Message = {
                id: `msg_${Date.now()}_error`,
                role: "assistant",
                content: `錯誤：${error instanceof Error ? error.message : "連線失敗"}`,
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    }, [input, isLoading, conversation, apiSettings, messages, onConversationUpdate]);

    const handleSuggestionClick = (text: string) => {
        setInput(text);
    };

    if (!conversation) {
        return (
            <div className="flex flex-col h-full bg-slate-50 items-center justify-center text-slate-400">
                <MessageSquare className="w-16 h-16 mb-4 opacity-30" />
                <p className="text-lg font-medium">選擇或建立對話</p>
                <p className="text-sm">從左側選擇現有對話，或點擊「新對話」開始</p>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full bg-slate-50">
            {/* API Key 提醒 */}
            {!apiSettings?.apiKey && (
                <div className="bg-amber-50 border-b border-amber-200 px-4 py-2 flex items-center gap-2 text-sm text-amber-800">
                    <AlertTriangle className="w-4 h-4" />
                    <span>請先設定 API Key 才能使用 AI 對話。點擊右上角 ⚙️ 設定。</span>
                </div>
            )}

            {/* 訊息列表 */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-64 text-slate-400">
                        <Brain className="w-16 h-16 mb-4 opacity-30" />
                        <p className="text-lg font-medium">ToneSoul Navigator</p>
                        <p className="text-sm">開始對話，體驗內在審議...</p>
                    </div>
                )}

                {messages.map((message) => (
                    <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                        <div className={`max-w-[85%] rounded-2xl ${message.role === "user"
                                ? "bg-indigo-600 text-white p-4"
                                : "bg-white border border-slate-200 shadow-sm overflow-hidden"
                            }`}>
                            {message.role === "user" ? (
                                <p className="leading-relaxed">{message.content}</p>
                            ) : (
                                <>
                                    {/* AI 回應內容 */}
                                    <div className="p-5">
                                        <p className="text-slate-800 leading-relaxed text-lg">
                                            {message.content}
                                        </p>
                                    </div>

                                    {/* 內在審議展開區 */}
                                    {message.deliberation && (
                                        <>
                                            <div className="border-t border-slate-100">
                                                <button
                                                    onClick={() => toggleDeliberation(message.id)}
                                                    className="w-full px-5 py-3 flex items-center justify-between text-sm text-slate-500 hover:bg-slate-50 transition-colors"
                                                >
                                                    <span className="flex items-center gap-2">
                                                        <Brain className="w-4 h-4" />
                                                        內在審議 (Council Deliberation)
                                                    </span>
                                                    {expandedNodes.has(message.id) ? (
                                                        <ChevronUp className="w-4 h-4" />
                                                    ) : (
                                                        <ChevronDown className="w-4 h-4" />
                                                    )}
                                                </button>
                                            </div>

                                            {expandedNodes.has(message.id) && (
                                                <div className="bg-slate-50/50 border-t border-slate-100 p-5 space-y-4">
                                                    {/* 張力儀表 */}
                                                    {message.deliberation.entropy_meter && (
                                                        <SoulStateMeter
                                                            value={message.deliberation.entropy_meter.value}
                                                            calculationNote={message.deliberation.entropy_meter.calculation_note}
                                                        />
                                                    )}

                                                    {/* 議會廳 */}
                                                    {message.deliberation.council_chamber && (
                                                        <CouncilChamber
                                                            philosopher={message.deliberation.council_chamber.philosopher}
                                                            engineer={message.deliberation.council_chamber.engineer}
                                                            guardian={message.deliberation.council_chamber.guardian}
                                                        />
                                                    )}

                                                    {/* 戰術儀表板 */}
                                                    {message.deliberation.decision_matrix && (
                                                        <TacticalDashboard matrix={{
                                                            user_hidden_intent: message.deliberation.decision_matrix.user_hidden_intent,
                                                            ai_strategy_name: message.deliberation.decision_matrix.ai_strategy_name,
                                                            intended_effect: message.deliberation.decision_matrix.intended_effect,
                                                            tone_tag: message.deliberation.decision_matrix.tone_tag,
                                                        }} />
                                                    )}
                                                </div>
                                            )}

                                            {/* 建議跟進 */}
                                            {message.deliberation.next_moves && message.deliberation.next_moves.length > 0 && (
                                                <div className="px-5 pb-4 flex flex-wrap gap-2 border-t border-slate-100 pt-3">
                                                    {message.deliberation.next_moves.map((move, idx) => (
                                                        <button
                                                            key={idx}
                                                            onClick={() => handleSuggestionClick(move.text)}
                                                            className="text-xs flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-50 hover:bg-indigo-50 text-slate-600 hover:text-indigo-600 transition-colors border border-slate-200 hover:border-indigo-200 group"
                                                        >
                                                            <span className="font-bold text-indigo-400 group-hover:text-indigo-600">
                                                                {move.label}
                                                            </span>
                                                            <MoveRight className="w-3 h-3 opacity-30 group-hover:opacity-100" />
                                                            <span>{move.text}</span>
                                                        </button>
                                                    ))}
                                                </div>
                                            )}
                                        </>
                                    )}
                                </>
                            )}
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm flex items-center gap-3">
                            <div className="flex gap-1">
                                <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                                <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                                <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                            </div>
                            <span className="text-sm text-purple-600 font-medium">議會審議中...</span>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* 輸入區 */}
            <div className="p-4 border-t border-slate-200 bg-white">
                <div className="flex gap-3">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
                        placeholder="輸入訊息以啟動議會..."
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
