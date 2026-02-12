"use client";

import { useState } from "react";
import { Ghost, ChevronDown, ChevronUp, AlertTriangle, Zap, Equal, Info, Target } from "lucide-react";

interface Shadow {
    source: 'philosopher' | 'engineer' | 'guardian';
    weight: number;
    conflict_reason: string;
    recovery_condition: string;
    collapse_cost: string;
}

interface MultiplexData {
    primary_path: {
        source: 'philosopher' | 'engineer' | 'guardian';
        weight: number;
        reasoning: string;
    };
    shadows: Shadow[];
    tension: {
        level: 'LOW' | 'MEDIUM' | 'HIGH';
        formula_ref: string;
        weight_distribution: string;
    };
    merge_strategy: 'COLLAPSE' | 'PRESERVE_SHADOWS' | 'EXPLICIT_CONFLICT';
    merge_note: string;
}

interface LogicalShadowsProps {
    data: MultiplexData;
}

// 公式說明模態框
const FormulaTooltip = ({ formula, explanation }: { formula: string; explanation: string }) => {
    const [show, setShow] = useState(false);

    return (
        <span className="relative inline-block">
            <button type="button"
                onClick={() => setShow(!show)}
                className="text-purple-400 hover:text-purple-300 underline decoration-dotted cursor-help text-[10px] font-mono"
            >
                {formula}
            </button>
            {show && (
                <div className="absolute bottom-full left-0 mb-2 p-3 bg-slate-900 border border-purple-500/50 rounded-lg shadow-xl z-50 w-64">
                    <div className="flex items-start gap-2">
                        <Info className="w-4 h-4 text-purple-400 flex-shrink-0 mt-0.5" />
                        <div>
                            <p className="text-[10px] font-mono text-purple-300 mb-1">{formula}</p>
                            <p className="text-[11px] text-slate-300">{explanation}</p>
                        </div>
                    </div>
                    <button type="button"
                        onClick={() => setShow(false)}
                        className="absolute top-1 right-1 text-slate-500 hover:text-slate-300"
                    >
                        ×
                    </button>
                </div>
            )}
        </span>
    );
};

// Source 標籤
const SourceBadge = ({ source }: { source: string }) => {
    const config: Record<string, { emoji: string; color: string }> = {
        philosopher: { emoji: '🔮', color: 'bg-purple-500/20 text-purple-300 border-purple-500/30' },
        engineer: { emoji: '⚙️', color: 'bg-blue-500/20 text-blue-300 border-blue-500/30' },
        guardian: { emoji: '🛡️', color: 'bg-amber-500/20 text-amber-300 border-amber-500/30' }
    };
    const { emoji, color } = config[source] || config.engineer;

    return (
        <span className={`px-2 py-0.5 rounded-full text-[10px] border ${color}`}>
            {emoji} {source}
        </span>
    );
};

// 張力等級指示器
const TensionIndicator = ({ level }: { level: string }) => {
    const config: Record<string, { color: string; label: string; icon: typeof Zap }> = {
        LOW: { color: 'text-green-400 bg-green-500/20', label: '低張力', icon: Equal },
        MEDIUM: { color: 'text-amber-400 bg-amber-500/20', label: '中張力', icon: Zap },
        HIGH: { color: 'text-red-400 bg-red-500/20', label: '高張力', icon: AlertTriangle }
    };
    const { color, label, icon: Icon } = config[level] || config.MEDIUM;

    return (
        <div className={`flex items-center gap-1 px-2 py-1 rounded-lg ${color}`}>
            <Icon className="w-3 h-3" />
            <span className="text-[10px] font-bold">{label}</span>
        </div>
    );
};

export default function LogicalShadows({ data }: LogicalShadowsProps) {
    const [expanded, setExpanded] = useState(false);

    return (
        <div className="mt-3 border border-slate-700 rounded-xl overflow-hidden bg-slate-800/50">
            {/* Header */}
            <button type="button"
                onClick={() => setExpanded(!expanded)}
                className="w-full px-4 py-3 flex items-center justify-between bg-gradient-to-r from-purple-900/30 to-slate-800/50 hover:from-purple-900/40 transition-colors"
            >
                <div className="flex items-center gap-2">
                    <Ghost className="w-4 h-4 text-purple-400" />
                    <span className="text-sm font-bold text-purple-300">vMT-2601 邏輯陰影</span>
                    <TensionIndicator level={data.tension.level} />
                </div>
                {expanded ? (
                    <ChevronUp className="w-4 h-4 text-slate-400" />
                ) : (
                    <ChevronDown className="w-4 h-4 text-slate-400" />
                )}
            </button>

            {expanded && (
                <div className="p-4 space-y-4">
                    {/* Primary Path */}
                    <div className="p-3 bg-green-500/10 border border-green-500/30 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                                <Target className="w-4 h-4 text-green-400" />
                                <span className="text-xs font-bold text-green-300">主路徑 (Primary)</span>
                            </div>
                            <SourceBadge source={data.primary_path.source} />
                        </div>
                        <div className="flex items-center gap-2 mb-2">
                            <FormulaTooltip
                                formula={`w = ${data.primary_path.weight.toFixed(2)}`}
                                explanation="此路徑的權重，基於邏輯密度 × 相關性計算。範圍 0-1，越高表示越符合用戶需求。"
                            />
                        </div>
                        <p className="text-xs text-slate-300">{data.primary_path.reasoning}</p>
                    </div>

                    {/* Shadows */}
                    {data.shadows.length > 0 && (
                        <div className="space-y-3">
                            <div className="flex items-center gap-2">
                                <Ghost className="w-4 h-4 text-slate-400" />
                                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                                    邏輯陰影 (Logical Shadows)
                                </span>
                            </div>

                            {data.shadows.map((shadow, i) => (
                                <div
                                    key={i}
                                    className="p-3 bg-slate-700/50 border border-slate-600 rounded-lg"
                                >
                                    <div className="flex items-center justify-between mb-2">
                                        <SourceBadge source={shadow.source} />
                                        <FormulaTooltip
                                            formula={`w = ${shadow.weight.toFixed(2)}`}
                                            explanation="此被淘汰路徑的權重。雖然未被採用，但其資訊被保留為「陰影」。"
                                        />
                                    </div>

                                    <div className="space-y-2 text-[11px]">
                                        <div>
                                            <span className="text-red-400 font-bold">⚔️ 衝突點：</span>
                                            <span className="text-slate-300 ml-1">{shadow.conflict_reason}</span>
                                        </div>
                                        <div>
                                            <span className="text-amber-400 font-bold">🔄 恢復條件：</span>
                                            <span className="text-slate-300 ml-1">{shadow.recovery_condition}</span>
                                        </div>
                                        <div>
                                            <span className="text-purple-400 font-bold">💀 坍縮代價：</span>
                                            <span className="text-slate-300 ml-1">{shadow.collapse_cost}</span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Tension Analysis */}
                    <div className="p-3 bg-slate-700/30 border border-slate-600 rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                            <Zap className="w-4 h-4 text-purple-400" />
                            <span className="text-xs font-bold text-purple-300">張力分析</span>
                        </div>
                        <div className="space-y-2 text-[11px]">
                            <div>
                                <span className="text-slate-400">權重分佈：</span>
                                <span className="text-purple-300 font-mono ml-1">{data.tension.weight_distribution}</span>
                            </div>
                            <div>
                                <span className="text-slate-400">計算公式：</span>
                                <FormulaTooltip
                                    formula={data.tension.formula_ref}
                                    explanation="ΔT = 1 - w_max。w_max 越接近 1，張力越低；三個權重越平均，張力越高。"
                                />
                            </div>
                            <div>
                                <span className="text-slate-400">合併策略：</span>
                                <span className={`font-bold ml-1 ${data.merge_strategy === 'COLLAPSE' ? 'text-green-400' :
                                        data.merge_strategy === 'PRESERVE_SHADOWS' ? 'text-amber-400' :
                                            'text-red-400'
                                    }`}>
                                    {data.merge_strategy}
                                </span>
                            </div>
                            {data.merge_note && (
                                <p className="text-slate-400 italic mt-2">{data.merge_note}</p>
                            )}
                        </div>
                    </div>

                    {/* Formula Reference */}
                    <div className="text-[10px] text-slate-500 border-t border-slate-700 pt-3">
                        <p className="font-mono">
                            📐 vMT-2601 協議：h_multiplex = Σ w_i · E(t_i)
                            <FormulaTooltip
                                formula="查看公式說明"
                                explanation="Multiplex Thinking 核心公式。將 K 個 Token 的 Embedding 根據權重加權平均，合成一個包含所有路徑資訊的複用 Token。在 ToneSoul 中，我們在語意層模擬此運算。"
                            />
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
}

