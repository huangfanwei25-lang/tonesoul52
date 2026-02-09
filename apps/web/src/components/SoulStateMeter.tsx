"use client";

import { CloudRain, Zap, AlertTriangle, FunctionSquare } from "lucide-react";

const TENSION_ZONES = [
    {
        range: [0.0, 0.3],
        status: "同溫層 (Echo Chamber)",
        feeling: "夢遊 (Dreamwalking)",
        description: "舒適但危險。缺乏觀點摩擦，僅順從偏見。",
        color: "#3b82f6",
        bg: "bg-blue-50",
        border: "border-blue-200",
        text: "text-blue-700",
        icon: CloudRain,
    },
    {
        range: [0.3, 0.7],
        status: "良性摩擦 (Healthy Friction)",
        feeling: "甜蜜點 (The Sweet Spot)",
        description: "創新的最佳區間。邏輯與意義正在激烈整合。",
        color: "#a855f7",
        bg: "bg-purple-50",
        border: "border-purple-200",
        text: "text-purple-700",
        icon: Zap,
    },
    {
        range: [0.7, 1.0],
        status: "系統混沌 (Chaos)",
        feeling: "認知失調 (Mental Knot)",
        description: "高風險區。內在邏輯斷裂，需強制冷卻。",
        color: "#ef4444",
        bg: "bg-red-50",
        border: "border-red-200",
        text: "text-red-700",
        icon: AlertTriangle,
    },
];

const getTensionZone = (entropy: number) => {
    return TENSION_ZONES.find(
        (z) => entropy >= z.range[0] && entropy <= z.range[1]
    ) || TENSION_ZONES[1];
};

interface SoulStateMeterProps {
    value: number;
    calculationNote?: string;
}

export default function SoulStateMeter({ value, calculationNote }: SoulStateMeterProps) {
    const zone = getTensionZone(value);
    const Icon = zone.icon;
    const percentage = Math.min(Math.max(value * 100, 0), 100);

    return (
        <div className="w-full">
            {/* 進度條 */}
            <div className="flex items-center gap-2 mb-2">
                <div className="text-[10px] font-bold uppercase text-slate-400 w-12 text-right">
                    張力
                </div>
                <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden relative">
                    <div
                        className={`h-full transition-all duration-700 ease-out ${percentage < 30 ? "bg-blue-500" : percentage < 70 ? "bg-purple-500" : "bg-red-500"
                            }`}
                        style={{ width: `${percentage}%` }}
                    />
                    {/* 區間標記 */}
                    <div className="absolute top-0 bottom-0 w-[1px] bg-slate-300 left-[30%]" />
                    <div className="absolute top-0 bottom-0 w-[1px] bg-slate-300 left-[70%]" />
                </div>
                <div className={`text-[10px] font-bold w-12 text-right ${zone.text}`}>
                    {value.toFixed(2)}
                </div>
            </div>

            {/* 狀態說明 */}
            <div className={`flex items-start gap-3 p-3 rounded-lg border ${zone.border} ${zone.bg} transition-colors duration-500`}>
                <div className={`p-2 rounded-full bg-white/50 ${zone.text}`}>
                    <Icon className="w-4 h-4" />
                </div>
                <div className="flex-1">
                    <div className={`text-xs font-bold uppercase mb-0.5 ${zone.text}`}>
                        {zone.status}
                    </div>
                    <p className="text-[11px] text-slate-600 leading-relaxed font-medium">
                        {zone.description}
                    </p>
                    {calculationNote && (
                        <div className="mt-2 pt-2 border-t border-black/5 text-[10px] text-slate-500 italic flex items-start gap-1">
                            <FunctionSquare className="w-3 h-3 mt-0.5 shrink-0" />
                            Logic: {calculationNote}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

// 導出張力區間資料供其他組件使用 (例如圖表)
export { TENSION_ZONES, getTensionZone };
