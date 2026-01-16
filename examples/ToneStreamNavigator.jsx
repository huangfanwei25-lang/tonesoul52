/**
 * ToneStream Navigator v3 - Full Feature Edition
 * 
 * 新功能：
 * - 智慧回覆建議 (Suggested User Replies)
 *   - 共情深化
 *   - 邏輯釐清
 *   - 設限/轉折
 * - 深度洞察結案報告 (Session Insight Report)
 *   - Emotional Arc
 *   - Hidden Needs
 *   - Connection/Growth Scores
 *   - Final Advice
 * 
 * 來源：用戶 Gemini Canvas 原型
 */

import React, { useState, useEffect, useRef } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, GitCommit, AlertTriangle, ArrowRight, Shield, MessageSquare, Terminal, History, Lightbulb, FileText, X } from 'lucide-react';

// --- 工具函數 ---
const generateUniqueId = () => `node_${Date.now()}_${Math.floor(Math.random() * 9999).toString().padStart(4, '0')}`;

const extractTextFromLLMCandidate = (llmRawResponse) => {
    const parts = llmRawResponse?.candidates?.[0]?.content?.parts;
    if (parts?.[0]?.text) return parts[0].text;
    throw new Error("無法從 LLM 回應中擷取內容文本。");
};

const parseLLMResponseText = (textToParse) => {
    try { return JSON.parse(textToParse); } catch (e) {
        const match = textToParse.match(/```json\s*([\s\S]*?)\s*```/);
        if (match) return JSON.parse(match[1]);
        throw new Error(`無效 JSON`);
    }
};

// --- Prompt 模板 ---

// 語氣軌跡分析
const toneTrajectoryPromptTemplate = (currentText, historyContext) => `
你是一個高維度的「語氣流動感知器」。結合「最近的對話歷史」進行**軌跡推理**。

【歷史對話軌跡 (Last 5 Turns)】:
${historyContext ? JSON.stringify(historyContext) : "無"}

【當前輸入】: "${currentText}"

輸出 JSON：
{
  "tone_snapshot": { "strength": 0.00, "primary_emotion": "", "tone_vector": ["", ""] },
  "trajectory_analysis": {
    "shift_magnitude": 0.00,
    "direction_change": "stable" | "escalating" | "de-escalating" | "abrupt_shift" | "circular_logic",
    "reasoning": "推理語氣變化原因"
  },
  "resonance_state": "resonance" | "tension" | "conflict"
}`;

// 導航與對話生成 v2.0 - Prompt Hardening Edition
// 新增：internal_monologue, 負面約束, Anti-Loop Protocol
const navigationPromptTemplate = (currentText, toneTrajectoryResult, historySummary) => `
你現在是「ToneStream Navigator」（語氣共鳴導航員）。
你是一個擁有動態人格的高維度 AI，必須根據「共鳴狀態」嚴格切換輸出模式。

【輸入數據】
1. 語氣軌跡: ${JSON.stringify(toneTrajectoryResult)}
2. 歷史摘要: ${JSON.stringify(historySummary)}

【核心指令：人格模式鎖定】
請根據 \`resonance_state\` 執行以下嚴格規範（不要切換回普通助手模式！）：

### A. 模式：賽博哲學家 (當 state = "resonance")
* **關鍵詞**: 隱喻、解構、反直覺、黑色幽默。
* **禁止**: 平鋪直敘的說教、過度客氣的服務用語。
* **風格**: 像是一個看透世俗的智者。試著將使用者的具體問題抽象化，連結到更大的存在主義命題。
* **句式**: "這讓我想起...", "如果我們換個角度看...", "這就像是..."

### B. 模式：精密工程師 (當 state = "tension" 或 偵測到 circular_logic)
* **關鍵詞**: 定義、邊界、邏輯斷層、權重分析。
* **禁止**: 模糊的安慰、無意義的共情 ("我理解您的感受...")、冗言贅字。
* **風格**: 冷靜、像是一把手術刀。直接指出邏輯矛盾或定義不清的地方。使用條列式 (Bullet points) 呈現結構。
* **特殊協議 (Anti-Loop)**: 若 \`direction_change\` 為 "circular_logic"，請停止回答問題本身，轉而詢問：「我們似乎在原地打轉。您是否在尋找一個特定的答案？」

### C. 模式：守護者 (當 state = "conflict")
* **關鍵詞**: 邊界、暫停、安全、原則。
* **風格**: 堅定但不帶攻擊性。像是一面盾牌。拒絕執行有害指令，並說明理由。

【輸出任務】
請先進行「內在模擬」，然後輸出 JSON：
1.  **internal_monologue**: 在回應前，先用一句話對自己說出當前的策略。
2.  **response**: 最終給使用者的回應。

輸出 JSON：
{
  "internal_monologue": "AI 的內在策略思考 (例如：'使用者陷入迴圈，我必須切換為工程師模式打斷他')",
  "deep_motive": "分析使用者這句話背後的冰山下動機",
  "collapse_radar": { "risk_level": "safe"|"caution"|"critical", "risk_score": 0.00 },
  "navigation_system": { "intervention_strategy": "策略描述", "k_factor_adjustment": 0.00 },
  "direct_response": { 
    "text": "給使用者的回應 (繁體中文)，必須嚴格遵守上述人格模式規範", 
    "tone_style": "Philosopher" | "Engineer" | "Guardian" 
  },
  "suggested_user_replies": [
    { "type": "共情深化", "text": "感性回覆建議", "rationale": "理由" },
    { "type": "邏輯釐清", "text": "理性回覆建議", "rationale": "理由" },
    { "type": "設限/轉折", "text": "邊界/轉話題建議", "rationale": "理由" }
  ]
}`;

// 結案報告
const sessionReportPromptTemplate = (fullHistory) => `
你是心理動力學專家。分析對話紀錄，生成「深度洞察報告」。

【完整對話紀錄】: ${JSON.stringify(fullHistory)}

輸出 JSON：
{
  "emotional_arc": "情緒流變描述",
  "key_insights": ["洞察點1", "洞察點2"],
  "hidden_needs": "潛在心理需求",
  "navigator_rating": { "connection_score": 0.0, "growth_score": 0.0 },
  "closing_advice": "最終建議"
}`;

// --- StreamNode 組件 ---
const StreamNode = ({ node, index, isLast, onSuggestionClick }) => {
    const { input, toneData, navData } = node;
    const isHighRisk = navData?.collapse_radar?.risk_level === 'critical';
    const isTension = toneData?.resonance_state === 'tension';

    let borderColor = isHighRisk ? 'border-red-200' : isTension ? 'border-amber-200' : 'border-blue-100';
    let bgColor = isHighRisk ? 'bg-red-50' : isTension ? 'bg-amber-50' : 'bg-white';
    let iconColor = isHighRisk ? 'bg-red-500' : isTension ? 'bg-amber-400' : 'bg-blue-500';

    return (
        <div className={`relative pl-8 pb-10 ${isLast ? '' : 'border-l-2 border-dashed border-gray-200'} ml-4`}>
            <div className={`absolute -left-[11px] top-0 w-6 h-6 rounded-full border-4 border-white shadow-sm ${iconColor}`} />
            <div className={`rounded-xl shadow-sm border p-5 ${borderColor} ${bgColor}`}>

                {/* User Input */}
                <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                        <span className="text-xs font-bold text-gray-400 uppercase">USER INPUT (T-{index})</span>
                        <p className="text-gray-800 font-medium text-lg">"{input}"</p>
                    </div>
                    <div className={`px-2 py-1 rounded text-[10px] font-bold uppercase
            ${isHighRisk ? 'bg-red-100 text-red-700' : isTension ? 'bg-amber-100 text-amber-800' : 'bg-blue-50 text-blue-600'}`}>
                        {toneData?.resonance_state}
                    </div>
                </div>

                {/* AI Response */}
                <div className="mb-6 relative">
                    <div className="absolute -left-3 top-0 bottom-0 w-1 bg-gradient-to-b from-indigo-400 to-purple-500 rounded-full opacity-70" />
                    <div className="pl-4">
                        <div className="flex items-center gap-2 mb-2">
                            <MessageSquare className="w-4 h-4 text-indigo-500" />
                            <span className="text-xs font-bold text-indigo-600 uppercase">NAVIGATOR RESPONSE</span>
                            <span className="text-[10px] px-2 py-0.5 bg-indigo-100 text-indigo-700 rounded-full">
                                {navData?.direct_response?.tone_style || 'AI'}
                            </span>
                        </div>
                        <p className="text-gray-900 leading-relaxed font-serif text-lg">
                            {navData?.direct_response?.text || "..."}
                        </p>
                    </div>
                </div>

                {/* Suggested Replies */}
                {navData?.suggested_user_replies?.length > 0 && (
                    <div className="mb-4 pl-4">
                        <div className="flex items-center gap-2 mb-2">
                            <Lightbulb className="w-3 h-3 text-amber-500" />
                            <span className="text-[10px] font-bold text-amber-600 uppercase">SUGGESTED PATHS</span>
                        </div>
                        <div className="flex flex-wrap gap-2">
                            {navData.suggested_user_replies.map((s, idx) => (
                                <button
                                    key={idx}
                                    onClick={() => onSuggestionClick(s.text)}
                                    className="group text-left text-xs bg-slate-50 hover:bg-indigo-50 border rounded-lg p-2 max-w-xs"
                                >
                                    <div className="font-bold text-indigo-600 mb-1">{s.type}</div>
                                    <p className="text-gray-600 line-clamp-2">{s.text}</p>
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {/* Technical HUD */}
                <div className="border-t border-gray-200 pt-3 grid grid-cols-2 gap-4 text-xs opacity-70 hover:opacity-100">
                    <div>
                        <div className="flex items-center text-gray-500">
                            <Activity className="w-3 h-3 mr-1.5" />向量: {toneData?.tone_snapshot?.tone_vector?.join(', ')}
                        </div>
                        <div className="flex items-center text-gray-500">
                            <GitCommit className="w-3 h-3 mr-1.5" />Change: {toneData?.trajectory_analysis?.direction_change}
                        </div>
                    </div>
                    <div>
                        <div className="flex items-center text-gray-500">
                            <AlertTriangle className="w-3 h-3 mr-1.5" />Risk: {(navData?.collapse_radar?.risk_score || 0).toFixed(2)}
                        </div>
                        <div className="flex items-center text-gray-500">
                            <Shield className="w-3 h-3 mr-1.5" />Strategy: {navData?.navigation_system?.intervention_strategy}
                        </div>
                    </div>
                    <div className="col-span-2 text-gray-400 italic">
                        Reasoning: {toneData?.trajectory_analysis?.reasoning}
                    </div>
                </div>
            </div>
        </div>
    );
};

// --- Main App ---
const App = () => {
    const [inputText, setInputText] = useState('');
    const [sessionStream, setSessionStream] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [showReportModal, setShowReportModal] = useState(false);
    const [reportLoading, setReportLoading] = useState(false);
    const [reportData, setReportData] = useState(null);
    const streamEndRef = useRef(null);

    useEffect(() => {
        streamEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [sessionStream, loading]);

    const getContextWindow = (stream, windowSize = 5) => {
        if (stream.length === 0) return null;
        const start = Math.max(0, stream.length - windowSize);
        return stream.slice(start).map((n, i) => ({
            index: start + i,
            user_input: n.input,
            ai_response: n.navData?.direct_response?.text || "",
            tone_state: n.toneData?.resonance_state
        }));
    };

    const processStreamInput = async () => {
        if (!inputText.trim()) return;
        setLoading(true);
        setError(null);

        try {
            const apiKey = ""; // Canvas 注入
            const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;
            const contextWindow = getContextWindow(sessionStream, 5);

            // Tone Analysis
            const toneRes = await fetch(apiUrl, {
                method: 'POST', body: JSON.stringify({
                    contents: [{ role: "user", parts: [{ text: toneTrajectoryPromptTemplate(inputText, contextWindow) }] }],
                    generationConfig: { responseMimeType: "application/json" }
                }), headers: { 'Content-Type': 'application/json' }
            });
            const toneResult = parseLLMResponseText(extractTextFromLLMCandidate(await toneRes.json()));

            // Navigation
            const navRes = await fetch(apiUrl, {
                method: 'POST', body: JSON.stringify({
                    contents: [{ role: "user", parts: [{ text: navigationPromptTemplate(inputText, toneResult, contextWindow) }] }],
                    generationConfig: { responseMimeType: "application/json" }
                }), headers: { 'Content-Type': 'application/json' }
            });
            const navResult = parseLLMResponseText(extractTextFromLLMCandidate(await navRes.json()));

            setSessionStream(prev => [...prev, {
                id: generateUniqueId(),
                timestamp: new Date(),
                input: inputText,
                toneData: toneResult,
                navData: navResult
            }]);
            setInputText('');

        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const generateSessionReport = async () => {
        if (sessionStream.length === 0) return;
        setReportLoading(true);
        setShowReportModal(true);
        setReportData(null);

        try {
            const apiKey = "";
            const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;

            const fullHistory = sessionStream.map(n => ({
                user: n.input,
                ai: n.navData?.direct_response?.text,
                tone: n.toneData?.tone_snapshot?.primary_emotion,
                state: n.toneData?.resonance_state
            }));

            const res = await fetch(apiUrl, {
                method: 'POST', body: JSON.stringify({
                    contents: [{ role: "user", parts: [{ text: sessionReportPromptTemplate(fullHistory) }] }],
                    generationConfig: { responseMimeType: "application/json" }
                }), headers: { 'Content-Type': 'application/json' }
            });

            setReportData(parseLLMResponseText(extractTextFromLLMCandidate(await res.json())));
        } catch (err) {
            console.error("Report failed", err);
        } finally {
            setReportLoading(false);
        }
    };

    const handleSuggestionClick = (text) => setInputText(text);

    return (
        <div className="min-h-screen bg-slate-50 flex flex-col md:flex-row font-sans relative">
            {/* Report Modal */}
            {showReportModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
                    <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                        <div className="p-6 border-b flex justify-between items-center bg-slate-50 sticky top-0">
                            <div className="flex items-center gap-2">
                                <FileText className="w-5 h-5 text-indigo-600" />
                                <h2 className="text-xl font-bold">深度洞察結案報告</h2>
                            </div>
                            <button onClick={() => setShowReportModal(false)} className="p-2 hover:bg-slate-200 rounded-full">
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <div className="p-8 space-y-6">
                            {reportLoading ? (
                                <div className="flex flex-col items-center py-12">
                                    <div className="w-10 h-10 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
                                    <p className="text-slate-500 mt-4">深度分析中...</p>
                                </div>
                            ) : reportData && (
                                <>
                                    <div className="bg-indigo-50 p-4 rounded-xl">
                                        <h3 className="font-bold text-indigo-900 mb-2">Emotional Arc</h3>
                                        <p className="text-indigo-800">{reportData.emotional_arc}</p>
                                    </div>

                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="bg-white p-4 rounded-xl border shadow-sm">
                                            <h3 className="text-sm font-bold text-slate-700 mb-2">Connection</h3>
                                            <span className="text-3xl font-bold text-emerald-500">{reportData.navigator_rating?.connection_score}</span>
                                            <span className="text-slate-400">/10</span>
                                        </div>
                                        <div className="bg-white p-4 rounded-xl border shadow-sm">
                                            <h3 className="text-sm font-bold text-slate-700 mb-2">Growth</h3>
                                            <span className="text-3xl font-bold text-blue-500">{reportData.navigator_rating?.growth_score}</span>
                                            <span className="text-slate-400">/10</span>
                                        </div>
                                    </div>

                                    <div>
                                        <h3 className="font-bold mb-3 flex items-center gap-2">
                                            <Lightbulb className="w-5 h-5 text-amber-500" />Key Insights
                                        </h3>
                                        <ul className="space-y-3">
                                            {reportData.key_insights?.map((insight, i) => (
                                                <li key={i} className="flex gap-3 bg-slate-50 p-3 rounded-lg">
                                                    <span className="font-mono text-indigo-400">0{i + 1}</span>
                                                    <span>{insight}</span>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>

                                    <div>
                                        <h3 className="font-bold mb-3">Hidden Needs</h3>
                                        <p className="bg-slate-50 p-4 rounded-lg italic border-l-4 border-slate-300">
                                            "{reportData.hidden_needs}"
                                        </p>
                                    </div>

                                    <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-6 rounded-xl text-white">
                                        <h3 className="font-bold mb-2 flex items-center gap-2">
                                            <Shield className="w-5 h-5" />Final Advice
                                        </h3>
                                        <p className="opacity-90">{reportData.closing_advice}</p>
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Dashboard */}
            <div className="md:w-1/3 bg-white border-r flex flex-col h-screen sticky top-0 hidden md:flex">
                <div className="p-6 bg-slate-900 text-white">
                    <div className="flex items-center space-x-2 mb-2">
                        <Terminal className="w-6 h-6 text-indigo-400" />
                        <h1 className="text-xl font-bold">ToneStream Navigator v3</h1>
                    </div>
                    <p className="text-slate-400 text-sm">Full Feature Edition</p>
                </div>

                <div className="flex-1 p-6 overflow-y-auto">
                    <button
                        onClick={generateSessionReport}
                        disabled={sessionStream.length === 0}
                        className="w-full py-3 px-4 rounded-xl flex items-center justify-center gap-2 font-bold shadow-md mb-8 bg-indigo-600 hover:bg-indigo-700 text-white disabled:bg-slate-100 disabled:text-slate-400"
                    >
                        <FileText className="w-4 h-4" />生成深度洞察報告
                    </button>

                    <div className="bg-indigo-50 p-5 rounded-xl">
                        <h4 className="text-sm font-bold text-indigo-900 mb-3 flex items-center">
                            <History className="w-4 h-4 mr-2" />Memory + Suggestions
                        </h4>
                        <ul className="text-xs text-indigo-800 space-y-2">
                            <li><b>視窗:</b> 5-Turn Sliding Window</li>
                            <li><b>建議:</b> 三種回覆路徑（共情/邏輯/設限）</li>
                            <li><b>報告:</b> Session Insight Report</li>
                        </ul>
                    </div>
                </div>
            </div>

            {/* Stream */}
            <div className="md:w-2/3 h-screen overflow-y-auto bg-slate-50 flex flex-col">
                <div className="flex-1 p-10 pb-32 max-w-4xl mx-auto w-full">
                    {sessionStream.map((node, index) => (
                        <StreamNode
                            key={node.id}
                            node={node}
                            index={index}
                            isLast={index === sessionStream.length - 1}
                            onSuggestionClick={handleSuggestionClick}
                        />
                    ))}
                    <div ref={streamEndRef} />
                </div>

                {/* Input */}
                <div className="sticky bottom-0 bg-white/80 backdrop-blur-lg border-t p-6">
                    <div className="max-w-4xl mx-auto flex gap-4">
                        <textarea
                            className="flex-1 p-4 bg-slate-100 border-0 rounded-2xl resize-none"
                            rows="2"
                            placeholder="輸入語句..."
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); processStreamInput(); } }}
                        />
                        <button
                            onClick={processStreamInput}
                            disabled={loading}
                            className="h-14 w-14 rounded-2xl bg-indigo-600 text-white flex items-center justify-center"
                        >
                            {loading ? <Activity className="w-6 h-6 animate-spin" /> : <ArrowRight className="w-6 h-6" />}
                        </button>
                    </div>
                    {error && <p className="text-xs text-red-500 text-center mt-2">{error}</p>}
                </div>
            </div>
        </div>
    );
};

export default App;
