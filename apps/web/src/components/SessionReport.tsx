"use client";

import { useState } from "react";
import { FileText, X, Lightbulb, Shield, TrendingUp, Heart, Activity } from "lucide-react";
import { Message, DeliberationData } from "@/lib/db";
import { ApiSettings } from "./SettingsModal";

interface SessionReportProps {
    isOpen: boolean;
    onClose: () => void;
    messages: Message[];
    apiSettings: ApiSettings | null;
}

interface ReportData {
    emotional_arc: string;
    key_insights: string[];
    hidden_needs: string;
    navigator_rating: {
        connection_score: number;
        growth_score: number;
    };
    closing_advice: string;
}

const SESSION_REPORT_PROMPT = (history: { user: string; ai: string; entropy?: number }[]) => `
你是一個心理動力學專家與數據分析師。請分析這段對話紀錄，生成一份「深度洞察報告」。

【完整對話紀錄】:
${JSON.stringify(history, null, 2)}

請輸出以下 JSON 結構 (繁體中文):
{
  "emotional_arc": "描述整場對話的情緒流變，從開始到結束的轉折",
  "key_insights": ["洞察點 1: ...", "洞察點 2: ...", "洞察點 3: ..."],
  "hidden_needs": "分析使用者未說出口的潛在心理需求或動機",
  "navigator_rating": {
    "connection_score": 7.5,
    "growth_score": 8.0
  },
  "closing_advice": "給使用者的最終建議，基於整場對話的分析"
}
`;

export default function SessionReport({ isOpen, onClose, messages, apiSettings }: SessionReportProps) {
    const [isLoading, setIsLoading] = useState(false);
    const [reportData, setReportData] = useState<ReportData | null>(null);
    const [error, setError] = useState<string | null>(null);

    const generateReport = async () => {
        if (!apiSettings?.apiKey) {
            setError("請先設定 API Key");
            return;
        }

        if (messages.length < 2) {
            setError("對話太短，無法生成報告（至少需要 2 則訊息）");
            return;
        }

        setIsLoading(true);
        setError(null);
        setReportData(null);

        try {
            const history = messages.map(m => ({
                user: m.role === "user" ? m.content : "",
                ai: m.role === "assistant" ? m.content : "",
                entropy: m.deliberation?.entropy_meter?.value,
            })).filter(h => h.user || h.ai);

            const prompt = SESSION_REPORT_PROMPT(history);

            let responseText: string;

            if (apiSettings.provider === "gemini") {
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
                    const err = await response.json();
                    throw new Error(err.error?.message || "Gemini API 錯誤");
                }

                const data = await response.json();
                responseText = data.candidates?.[0]?.content?.parts?.[0]?.text || "{}";
            } else {
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
                    const err = await response.json();
                    throw new Error(err.error?.message || "OpenAI API 錯誤");
                }

                const data = await response.json();
                responseText = data.choices?.[0]?.message?.content || "{}";
            }

            const parsed = JSON.parse(responseText) as ReportData;
            setReportData(parsed);
        } catch (err) {
            console.error("Report generation error:", err);
            setError(err instanceof Error ? err.message : "生成報告失敗");
        } finally {
            setIsLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto flex flex-col">
                {/* Header */}
                <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50 sticky top-0">
                    <div className="flex items-center gap-2">
                        <FileText className="w-5 h-5 text-indigo-600" />
                        <h2 className="text-xl font-bold text-slate-800">深度洞察報告</h2>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-slate-200 rounded-full transition-colors">
                        <X className="w-5 h-5 text-slate-500" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 md:p-8 space-y-6">
                    {!reportData && !isLoading && !error && (
                        <div className="text-center py-8">
                            <Activity className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                            <p className="text-slate-500 mb-4">分析 {messages.length} 則訊息的對話模式</p>
                            <button
                                onClick={generateReport}
                                disabled={messages.length < 2}
                                className="px-6 py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                生成洞察報告
                            </button>
                        </div>
                    )}

                    {isLoading && (
                        <div className="flex flex-col items-center justify-center py-12 space-y-4">
                            <div className="w-10 h-10 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
                            <p className="text-slate-500 animate-pulse">正在回溯對話軌跡...</p>
                        </div>
                    )}

                    {error && (
                        <div className="text-center py-8">
                            <p className="text-red-500 mb-4">{error}</p>
                            <button
                                onClick={generateReport}
                                className="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors"
                            >
                                重試
                            </button>
                        </div>
                    )}

                    {reportData && (
                        <>
                            {/* Emotional Arc */}
                            <div className="bg-indigo-50 p-4 rounded-xl border border-indigo-100">
                                <h3 className="text-sm font-bold text-indigo-900 mb-2 uppercase tracking-wide flex items-center gap-2">
                                    <TrendingUp className="w-4 h-4" />
                                    情緒流變 (Emotional Arc)
                                </h3>
                                <p className="text-indigo-800 leading-relaxed">{reportData.emotional_arc}</p>
                            </div>

                            {/* Scores */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                                    <h3 className="text-sm font-bold text-slate-700 mb-2 flex items-center gap-2">
                                        <Heart className="w-4 h-4 text-emerald-500" />
                                        連結深度
                                    </h3>
                                    <div className="flex items-end gap-2">
                                        <span className="text-3xl font-bold text-emerald-500">
                                            {reportData.navigator_rating?.connection_score || "N/A"}
                                        </span>
                                        <span className="text-sm text-slate-400 mb-1">/ 10</span>
                                    </div>
                                </div>
                                <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                                    <h3 className="text-sm font-bold text-slate-700 mb-2 flex items-center gap-2">
                                        <TrendingUp className="w-4 h-4 text-blue-500" />
                                        成長潛力
                                    </h3>
                                    <div className="flex items-end gap-2">
                                        <span className="text-3xl font-bold text-blue-500">
                                            {reportData.navigator_rating?.growth_score || "N/A"}
                                        </span>
                                        <span className="text-sm text-slate-400 mb-1">/ 10</span>
                                    </div>
                                </div>
                            </div>

                            {/* Key Insights */}
                            <div>
                                <h3 className="text-lg font-bold text-slate-800 mb-3 flex items-center gap-2">
                                    <Lightbulb className="w-5 h-5 text-amber-500" />
                                    關鍵洞察
                                </h3>
                                <ul className="space-y-3">
                                    {reportData.key_insights?.map((insight, i) => (
                                        <li key={i} className="flex gap-3 text-slate-700 bg-slate-50 p-3 rounded-lg">
                                            <span className="font-mono text-indigo-400 font-bold">0{i + 1}</span>
                                            <span>{insight}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            {/* Hidden Needs */}
                            <div>
                                <h3 className="text-lg font-bold text-slate-800 mb-3">潛在需求</h3>
                                <p className="text-slate-600 bg-slate-50 p-4 rounded-lg italic border-l-4 border-slate-300">
                                    "{reportData.hidden_needs}"
                                </p>
                            </div>

                            {/* Closing Advice */}
                            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-6 rounded-xl text-white shadow-lg">
                                <h3 className="font-bold mb-2 flex items-center gap-2">
                                    <Shield className="w-5 h-5" />
                                    Navigator 的最終建議
                                </h3>
                                <p className="opacity-90 leading-relaxed">{reportData.closing_advice}</p>
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}
