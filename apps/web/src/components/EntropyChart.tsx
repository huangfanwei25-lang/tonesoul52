"use client";

import { useMemo } from "react";
import { XAxis, YAxis, ReferenceLine, ResponsiveContainer, Tooltip, Area, AreaChart } from "recharts";
import { Activity } from "lucide-react";
import { Conversation } from "@/lib/db";

interface EntropyChartProps {
    conversation: Conversation | null;
}

// 張力區間定義
const ZONES = {
    ecoChamber: { max: 0.3, color: "#3b82f6", label: "同溫層" },
    sweetSpot: { min: 0.3, max: 0.7, color: "#a855f7", label: "甜蜜點" },
    chaos: { min: 0.7, color: "#ef4444", label: "混沌" },
};

export default function EntropyChart({ conversation }: EntropyChartProps) {
    const chartData = useMemo(() => {
        if (!conversation) return [];

        return conversation.messages
            .filter(m => m.role === "assistant" && m.deliberation?.entropy_meter?.value !== undefined)
            .map((m, idx) => ({
                index: idx + 1,
                entropy: m.deliberation?.entropy_meter?.value || 0,
                status: m.deliberation?.entropy_meter?.status || "",
            }));
    }, [conversation]);

    const averageEntropy = useMemo(() => {
        if (chartData.length === 0) return 0;
        return chartData.reduce((acc, d) => acc + d.entropy, 0) / chartData.length;
    }, [chartData]);

    const getZoneLabel = (value: number) => {
        if (value < 0.3) return ZONES.ecoChamber.label;
        if (value < 0.7) return ZONES.sweetSpot.label;
        return ZONES.chaos.label;
    };

    const getZoneColor = (value: number) => {
        if (value < 0.3) return ZONES.ecoChamber.color;
        if (value < 0.7) return ZONES.sweetSpot.color;
        return ZONES.chaos.color;
    };

    if (!conversation || chartData.length === 0) {
        return (
            <div className="p-4 text-center text-slate-500 text-sm">
                <Activity className="w-6 h-6 mx-auto mb-2 opacity-30" />
                <p>對話後顯示張力圖表</p>
            </div>
        );
    }

    return (
        <div className="p-3 space-y-3">
            <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                    認知張力軌跡
                </span>
                <div className="flex items-center gap-1">
                    <span
                        className="text-xs font-bold px-2 py-0.5 rounded-full"
                        style={{
                            backgroundColor: `${getZoneColor(averageEntropy)}20`,
                            color: getZoneColor(averageEntropy)
                        }}
                    >
                        平均: {averageEntropy.toFixed(2)}
                    </span>
                </div>
            </div>

            {/* 圖表 */}
            <div className="h-24 bg-slate-800 rounded-lg p-2">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={chartData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                        {/* 區間背景 */}
                        <defs>
                            <linearGradient id="entropyGradient" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stopColor="#a855f7" stopOpacity={0.6} />
                                <stop offset="100%" stopColor="#a855f7" stopOpacity={0.1} />
                            </linearGradient>
                        </defs>

                        <XAxis
                            dataKey="index"
                            tick={{ fill: '#64748b', fontSize: 10 }}
                            axisLine={{ stroke: '#334155' }}
                            tickLine={false}
                        />
                        <YAxis
                            domain={[0, 1]}
                            tick={{ fill: '#64748b', fontSize: 10 }}
                            axisLine={{ stroke: '#334155' }}
                            tickLine={false}
                            ticks={[0, 0.3, 0.7, 1]}
                        />

                        {/* 區間參考線 */}
                        <ReferenceLine y={0.3} stroke="#3b82f6" strokeDasharray="3 3" strokeOpacity={0.5} />
                        <ReferenceLine y={0.7} stroke="#ef4444" strokeDasharray="3 3" strokeOpacity={0.5} />

                        <Tooltip
                            content={({ active, payload }) => {
                                if (active && payload && payload.length) {
                                    const value = payload[0].value as number;
                                    return (
                                        <div className="bg-slate-900 px-2 py-1 rounded text-xs border border-slate-700">
                                            <span style={{ color: getZoneColor(value) }}>
                                                E = {value.toFixed(2)} ({getZoneLabel(value)})
                                            </span>
                                        </div>
                                    );
                                }
                                return null;
                            }}
                        />

                        <Area
                            type="monotone"
                            dataKey="entropy"
                            stroke="#a855f7"
                            fill="url(#entropyGradient)"
                            strokeWidth={2}
                            dot={{ fill: '#a855f7', strokeWidth: 0, r: 3 }}
                            activeDot={{ r: 5, fill: '#a855f7' }}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>

            {/* 圖例 */}
            <div className="flex justify-center gap-3 text-[10px]">
                <div className="flex items-center gap-1">
                    <div className="w-2 h-2 rounded-full bg-blue-500" />
                    <span className="text-slate-500">同溫層 &lt;0.3</span>
                </div>
                <div className="flex items-center gap-1">
                    <div className="w-2 h-2 rounded-full bg-purple-500" />
                    <span className="text-slate-500">甜蜜點 0.3-0.7</span>
                </div>
                <div className="flex items-center gap-1">
                    <div className="w-2 h-2 rounded-full bg-red-500" />
                    <span className="text-slate-500">混沌 &gt;0.7</span>
                </div>
            </div>
        </div>
    );
}
