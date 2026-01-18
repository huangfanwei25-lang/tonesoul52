"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Send, Loader2, Brain, ChevronDown, ChevronUp, AlertTriangle, MessageSquare, MoveRight, Users } from "lucide-react";
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

// ==================== 3 獨立視角 Prompt ====================

const PHILOSOPHER_PROMPT = (input: string, context: string) => `
你是「哲學家視角」(Philosopher)，專注於意義、價值觀與人文關懷。
不要考慮可行性或風險，只專注於：這對人意味著什麼？

【對話脈絡】:
${context}

【用戶輸入】:
"${input}"

請從純粹意義層面分析，輸出 JSON (繁體中文):
{
  "stance": "你的觀點（2-3 句，深度分析用戶話語背後的意義）",
  "core_value": "這涉及什麼核心價值（如：自由、歸屬、成長...）",
  "blind_spot": "你這個視角可能忽略什麼（對自己的限制誠實）"
}
`;

const ENGINEER_PROMPT = (input: string, context: string) => `
你是「工程師視角」(Engineer)，專注於邏輯、可行性與效率。
不要考慮情感或倫理，只專注於：這如何實現？需要什麼？

【對話脈絡】:
${context}

【用戶輸入】:
"${input}"

請從純粹邏輯層面分析，輸出 JSON (繁體中文):
{
  "stance": "你的觀點（2-3 句，分析實際操作層面）",
  "feasibility": "可行性評估（具體說明能/不能做到什麼）",
  "blind_spot": "你這個視角可能忽略什麼（對自己的限制誠實）"
}
`;

const GUARDIAN_PROMPT = (input: string, context: string) => `
你是「守護者視角」(Guardian)，專注於風險、安全與倫理邊界。
不要考慮創新或效率，只專注於：這有什麼風險？需要注意什麼？

【對話脈絡】:
${context}

【用戶輸入】:
"${input}"

請從純粹風險層面分析，輸出 JSON (繁體中文):
{
  "stance": "你的觀點（2-3 句，分析潛在風險與保護措施）",
  "risk_level": "low 或 medium 或 high",
  "conflict_point": "與其他視角可能的衝突點",
  "blind_spot": "你這個視角可能忽略什麼（對自己的限制誠實）"
}
`;

const SYNTHESIZER_PROMPT = (input: string, philosopher: string, engineer: string, guardian: string) => `
你是「綜合者」(Synthesizer)，負責整合三個獨立視角的意見。

【用戶原始輸入】:
"${input}"

【哲學家視角】:
${philosopher}

【工程師視角】:
${engineer}

【守護者視角】:
${guardian}

請執行以下任務：
1. 比較三個視角的差異與共識
2. 找出最佳回應策略
3. 生成一個平衡三方觀點的綜合回應

輸出 JSON (繁體中文):
{
  "entropy_analysis": {
    "value": 0.5,
    "status": "Healthy Friction 或 Echo Chamber 或 Chaos",
    "calculation_note": "說明為何判定此數值（三者共識度、風險等級、盲點互補性）"
  },
  "decision_matrix": {
    "user_hidden_intent": "用戶可能的潛台詞/真正需求",
    "ai_strategy_name": "你選擇的回應策略名稱",
    "intended_effect": "希望達到的效果",
    "tone_tag": "語氣標籤"
  },
  "final_response": "整合三方觀點後的最終回應（自然語氣，不提及三個視角，直接回應用戶）",
  "next_moves": [
    { "label": "探索", "text": "可以延伸的問題1" },
    { "label": "深入", "text": "可以延伸的問題2" }
  ]
}
`;

// ==================== 快速模式 Prompt ====================

const FAST_MODE_PROMPT = (input: string, context: string) => `
你是 ToneSoul Navigator，一個能進行內在審議的 AI 助手。

【對話脈絡】:
${context || "無"}

【用戶輸入】:
"${input}"

請以自然語氣回應用戶，同時簡要說明你的思考過程。
輸出 JSON (繁體中文):
{
  "response": "你的回應內容",
  "thinking": "你的思考過程（1-2句）"
}
`;

// ==================== API 調用函數 ====================

const callGeminiAPI = async (prompt: string, apiKey: string, enableGrounding: boolean = true): Promise<string> => {
    const requestBody: Record<string, unknown> = {
        contents: [{ role: "user", parts: [{ text: prompt }] }],
        generationConfig: { responseMimeType: "application/json" },
    };

    // 啟用 Grounding with Google Search
    if (enableGrounding) {
        requestBody.tools = [{ google_search: {} }];
    }

    const response = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`,
        {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(requestBody),
        }
    );

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error?.message || "Gemini API 錯誤");
    }

    const data = await response.json();
    return data.candidates?.[0]?.content?.parts?.[0]?.text || "{}";
};

const callOpenAIAPI = async (prompt: string, apiKey: string): Promise<string> => {
    const response = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
            model: "gpt-4o-mini",
            messages: [{ role: "user", content: prompt }],
            response_format: { type: "json_object" },
        }),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error?.message || "OpenAI API 錯誤");
    }

    const data = await response.json();
    return data.choices?.[0]?.message?.content || "{}";
};

const callClaudeAPI = async (prompt: string, apiKey: string): Promise<string> => {
    const response = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "x-api-key": apiKey,
            "anthropic-version": "2023-06-01",
        },
        body: JSON.stringify({
            model: "claude-3-haiku-20240307",
            max_tokens: 2048,
            messages: [{ role: "user", content: prompt + "\n\n請以 JSON 格式回覆。" }],
        }),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error?.message || "Claude API 錯誤");
    }

    const data = await response.json();
    return data.content?.[0]?.text || "{}";
};

const callXaiAPI = async (prompt: string, apiKey: string): Promise<string> => {
    const response = await fetch("https://api.x.ai/v1/chat/completions", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
            model: "grok-beta",
            messages: [{ role: "user", content: prompt }],
        }),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error?.message || "xAI API 錯誤");
    }

    const data = await response.json();
    return data.choices?.[0]?.message?.content || "{}";
};

function safeJsonParse<T>(text: string): T | null {
    try {
        return JSON.parse(text) as T;
    } catch {
        // Try to extract JSON from markdown code blocks
        const match = text.match(/```json\s*([\s\S]*?)\s*```/);
        if (match?.[1]) {
            try {
                return JSON.parse(match[1]) as T;
            } catch {
                return null;
            }
        }
        return null;
    }
}

// ==================== Main Component ====================

export default function ChatInterface({ conversation, apiSettings, onConversationUpdate }: ChatInterfaceProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [loadingPhase, setLoadingPhase] = useState<string>("");
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
        return messages.slice(-6).map(m =>
            `[${m.role === 'user' ? '用戶' : 'AI'}]: ${m.content.slice(0, 150)}`
        ).join('\n');
    };

    // 根據提供者選擇 API 調用函數
    const getCallAPI = () => {
        if (!apiSettings?.apiKey) return null;
        switch (apiSettings.provider) {
            case "gemini": return (prompt: string) => callGeminiAPI(prompt, apiSettings.apiKey);
            case "openai": return (prompt: string) => callOpenAIAPI(prompt, apiSettings.apiKey);
            case "claude": return (prompt: string) => callClaudeAPI(prompt, apiSettings.apiKey);
            case "xai": return (prompt: string) => callXaiAPI(prompt, apiSettings.apiKey);
            default: return (prompt: string) => callGeminiAPI(prompt, apiSettings.apiKey);
        }
    };

    // ==================== 快速模式：單一調用 ====================
    const performFastMode = async (userMessage: string): Promise<{
        response: string;
        deliberation: undefined;
    }> => {
        const callAPI = getCallAPI();
        if (!callAPI) throw new Error("請先設定 API Key");

        setLoadingPhase("思考中...");

        const context = getHistoryContext();
        const raw = await callAPI(FAST_MODE_PROMPT(userMessage, context));
        const parsed = safeJsonParse<{ response: string; thinking: string }>(raw);

        if (!parsed) {
            // 如果解析失敗，直接使用原始回應
            return { response: raw, deliberation: undefined };
        }

        return { response: parsed.response, deliberation: undefined };
    };

    // ==================== 核心：三路並行審議 ====================
    const performMultiPathDeliberation = async (userMessage: string): Promise<{
        response: string;
        deliberation: DeliberationData;
    }> => {
        const callAPI = getCallAPI();
        if (!callAPI) throw new Error("請先設定 API Key");

        const context = getHistoryContext();

        // Phase 1: 三路並行調用
        setLoadingPhase("召集議會成員...");

        const [philosopherRaw, engineerRaw, guardianRaw] = await Promise.all([
            callAPI(PHILOSOPHER_PROMPT(userMessage, context)),
            callAPI(ENGINEER_PROMPT(userMessage, context)),
            callAPI(GUARDIAN_PROMPT(userMessage, context)),
        ]);

        const philosopher = safeJsonParse<{ stance: string; core_value: string; blind_spot: string }>(philosopherRaw);
        const engineer = safeJsonParse<{ stance: string; feasibility: string; blind_spot: string }>(engineerRaw);
        const guardian = safeJsonParse<{ stance: string; risk_level: string; conflict_point?: string; blind_spot: string }>(guardianRaw);

        if (!philosopher || !engineer || !guardian) {
            throw new Error("議會成員回應解析失敗");
        }

        // Phase 2: Synthesizer 綜合
        setLoadingPhase("Synthesizer 整合中...");

        const synthesizerRaw = await callAPI(SYNTHESIZER_PROMPT(
            userMessage,
            JSON.stringify(philosopher),
            JSON.stringify(engineer),
            JSON.stringify(guardian)
        ));

        const synthesizer = safeJsonParse<{
            entropy_analysis: { value: number; status: string; calculation_note: string };
            decision_matrix: { user_hidden_intent: string; ai_strategy_name: string; intended_effect: string; tone_tag: string };
            final_response: string;
            next_moves: { label: string; text: string }[];
        }>(synthesizerRaw);

        if (!synthesizer) {
            throw new Error("Synthesizer 回應解析失敗");
        }

        // 組裝完整的審議數據
        const deliberation: DeliberationData = {
            council_chamber: {
                philosopher: {
                    stance: philosopher.stance,
                    conflict_point: philosopher.blind_spot
                },
                engineer: {
                    stance: engineer.stance,
                    conflict_point: engineer.blind_spot
                },
                guardian: {
                    stance: guardian.stance,
                    conflict_point: guardian.conflict_point || guardian.blind_spot
                },
            },
            entropy_meter: {
                value: synthesizer.entropy_analysis.value,
                status: synthesizer.entropy_analysis.status,
                calculation_note: synthesizer.entropy_analysis.calculation_note,
            },
            decision_matrix: {
                user_hidden_intent: synthesizer.decision_matrix.user_hidden_intent,
                ai_strategy_name: synthesizer.decision_matrix.ai_strategy_name,
                intended_effect: synthesizer.decision_matrix.intended_effect,
                tone_tag: synthesizer.decision_matrix.tone_tag,
            },
            final_synthesis: {
                response_text: synthesizer.final_response,
            },
            next_moves: synthesizer.next_moves,
        };

        return {
            response: synthesizer.final_response,
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
        setLoadingPhase(apiSettings?.mode === "fast" ? "思考中..." : "啟動審議...");

        try {
            let result: { response: string; deliberation: DeliberationData | undefined };

            if (apiSettings?.apiKey) {
                // 根據模式選擇處理方式
                if (apiSettings.mode === "fast") {
                    result = await performFastMode(userMessage.content);
                } else {
                    const deliberationResult = await performMultiPathDeliberation(userMessage.content);
                    result = {
                        response: deliberationResult.response,
                        deliberation: deliberationResult.deliberation,
                    };
                }
            } else {
                result = {
                    response: "請先設定 API Key 才能使用 AI 對話功能。點擊側邊欄的 API 設定按鈕。",
                    deliberation: undefined,
                };
            }

            const assistantMessage: Message = {
                id: `msg_${Date.now()}_ai`,
                role: "assistant",
                content: result.response,
                deliberation: result.deliberation,
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
            setLoadingPhase("");
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
                    <span>請先設定 API Key 才能使用 AI 對話。點擊側邊欄 API 設定。</span>
                </div>
            )}

            {/* 訊息列表 */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-64 text-slate-400">
                        <Users className="w-16 h-16 mb-4 opacity-30" />
                        <p className="text-lg font-medium">ToneSoul Multi-Path Deliberation</p>
                        <p className="text-sm">三路並行審議 — 每條訊息調用 4 次 API</p>
                        <p className="text-xs mt-2 text-slate-300">Philosopher × Engineer × Guardian → Synthesizer</p>
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
                                                        多路徑審議 (4 次獨立 API 調用)
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
                                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                            </div>
                            <span className="text-sm text-purple-600 font-medium">{loadingPhase}</span>
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
                        placeholder="輸入訊息以啟動三路審議..."
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
