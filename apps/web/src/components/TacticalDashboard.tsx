"use client";

import { Eye, Target, Sparkles } from "lucide-react";

interface DecisionMatrix {
    user_hidden_intent: string;
    ai_strategy_name: string;
    intended_effect: string;
    tone_tag: string;
}

interface TacticalDashboardProps {
    matrix?: DecisionMatrix;
}

export default function TacticalDashboard({ matrix }: TacticalDashboardProps) {
    if (!matrix) return null;

    return (
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-3 grid grid-cols-1 md:grid-cols-3 gap-3">
            {/* 潛台詞偵測 */}
            <div className="flex flex-col gap-1">
                <div className="flex items-center gap-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                    <Eye className="w-3 h-3 text-indigo-400" />
                    潛台詞偵測
                </div>
                <div className="text-xs text-slate-700 font-medium bg-white px-2 py-1.5 rounded border border-slate-100 shadow-sm h-full flex items-center">
                    {matrix.user_hidden_intent || "分析中..."}
                </div>
            </div>

            {/* 執行戰術 */}
            <div className="flex flex-col gap-1">
                <div className="flex items-center gap-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                    <Target className="w-3 h-3 text-emerald-400" />
                    執行戰術
                </div>
                <div className="text-xs text-emerald-700 font-bold bg-emerald-50 px-2 py-1.5 rounded border border-emerald-100 h-full flex items-center">
                    {matrix.ai_strategy_name || "決策中..."}
                </div>
            </div>

            {/* 預期效果 */}
            <div className="flex flex-col gap-1">
                <div className="flex items-center gap-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                    <Sparkles className="w-3 h-3 text-amber-400" />
                    預期效果
                </div>
                <div className="text-xs text-slate-600 bg-white px-2 py-1.5 rounded border border-slate-100 shadow-sm h-full flex items-center">
                    {matrix.intended_effect || "評估中..."}
                </div>
            </div>
        </div>
    );
}
