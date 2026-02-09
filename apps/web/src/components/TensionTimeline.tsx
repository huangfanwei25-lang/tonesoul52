'use client';

import React, { useMemo } from 'react';
import { Activity, TrendingUp, AlertCircle } from 'lucide-react';
import type { SoulState, SoulMode } from '@/lib/soulEngine';

interface TensionTimelineProps {
    soulState: SoulState;
    maxPoints?: number;
}

// 將張力歷史轉換為時間軸點
interface TimelinePoint {
    turn: number;
    tensionIntegral: number;
    entropy: number;
    mode: SoulMode;
    hasContradiction: boolean;
    timestamp: number;
}

// 張力區間配置
const ZONE_CONFIG = {
    echoChaber: { max: 0.3, color: 'bg-green-500/20', label: 'Echo Chamber' },
    healthyFriction: { min: 0.3, max: 0.7, color: 'bg-yellow-500/20', label: 'Healthy Friction' },
    chaos: { min: 0.7, color: 'bg-red-500/20', label: 'Chaos' },
};

// 簡易 SVG 線圖 (不依賴 Recharts，減少打包大小)
const MiniChart: React.FC<{ points: TimelinePoint[] }> = ({ points }) => {
    if (points.length < 2) return null;

    const width = 280;
    const height = 80;
    const padding = { top: 10, right: 10, bottom: 20, left: 30 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;

    // 計算 X/Y 座標
    const xScale = (i: number) => padding.left + (i / (points.length - 1)) * chartWidth;
    const yScale = (v: number) => padding.top + (1 - v) * chartHeight;

    // 生成路徑
    const linePath = points
        .map((p, i) => `${i === 0 ? 'M' : 'L'} ${xScale(i)} ${yScale(p.tensionIntegral)}`)
        .join(' ');

    // 填充區域路徑
    const areaPath = `${linePath} L ${xScale(points.length - 1)} ${yScale(0)} L ${xScale(0)} ${yScale(0)} Z`;

    return (
        <svg width={width} height={height} className="overflow-visible">
            {/* 區間背景 */}
            <rect
                x={padding.left}
                y={yScale(0.3)}
                width={chartWidth}
                height={yScale(0) - yScale(0.3)}
                className="fill-green-500/10"
            />
            <rect
                x={padding.left}
                y={yScale(0.7)}
                width={chartWidth}
                height={yScale(0.3) - yScale(0.7)}
                className="fill-yellow-500/10"
            />
            <rect
                x={padding.left}
                y={yScale(1)}
                width={chartWidth}
                height={yScale(0.7) - yScale(1)}
                className="fill-red-500/10"
            />

            {/* 區間分界線 */}
            <line
                x1={padding.left}
                y1={yScale(0.3)}
                x2={width - padding.right}
                y2={yScale(0.3)}
                className="stroke-gray-600"
                strokeDasharray="4 2"
                strokeWidth={0.5}
            />
            <line
                x1={padding.left}
                y1={yScale(0.7)}
                x2={width - padding.right}
                y2={yScale(0.7)}
                className="stroke-gray-600"
                strokeDasharray="4 2"
                strokeWidth={0.5}
            />

            {/* Y 軸標籤 */}
            <text x={padding.left - 5} y={yScale(0)} className="fill-gray-500 text-[8px]" textAnchor="end" dominantBaseline="middle">0</text>
            <text x={padding.left - 5} y={yScale(0.5)} className="fill-gray-500 text-[8px]" textAnchor="end" dominantBaseline="middle">0.5</text>
            <text x={padding.left - 5} y={yScale(1)} className="fill-gray-500 text-[8px]" textAnchor="end" dominantBaseline="middle">1</text>

            {/* 填充區域 */}
            <path
                d={areaPath}
                className="fill-purple-500/20"
            />

            {/* 主線 */}
            <path
                d={linePath}
                fill="none"
                className="stroke-purple-400"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
            />

            {/* 數據點 */}
            {points.map((p, i) => (
                <g key={i}>
                    <circle
                        cx={xScale(i)}
                        cy={yScale(p.tensionIntegral)}
                        r={p.hasContradiction ? 5 : 3}
                        className={p.hasContradiction ? 'fill-red-500' : 'fill-purple-400'}
                    />
                    {p.hasContradiction && (
                        <circle
                            cx={xScale(i)}
                            cy={yScale(p.tensionIntegral)}
                            r={7}
                            className="fill-red-500/30"
                        />
                    )}
                </g>
            ))}

            {/* X 軸標籤 */}
            {points.length <= 10 && points.map((_, i) => (
                <text
                    key={i}
                    x={xScale(i)}
                    y={height - 5}
                    className="fill-gray-500 text-[8px]"
                    textAnchor="middle"
                >
                    {i + 1}
                </text>
            ))}
            {points.length > 10 && (
                <>
                    <text x={xScale(0)} y={height - 5} className="fill-gray-500 text-[8px]" textAnchor="start">1</text>
                    <text x={xScale(points.length - 1)} y={height - 5} className="fill-gray-500 text-[8px]" textAnchor="end">{points.length}</text>
                </>
            )}
        </svg>
    );
};

export default function TensionTimeline({ soulState, maxPoints = 20 }: TensionTimelineProps) {
    // 從 tensionHistory 構建時間軸點
    const timelinePoints = useMemo<TimelinePoint[]>(() => {
        const { tensionHistory, contradictions, soulMode } = soulState;

        // 取最近的 N 筆記錄
        const recentHistory = tensionHistory.slice(-maxPoints);

        const alpha = 0.15;

        return recentHistory.map((record, index) => {
            // 簡化版的張力積分計算
            const tensionIntegral = recentHistory.slice(0, index + 1).reduce((sum, item, itemIndex) => {
                const decay = Math.exp(-alpha * (recentHistory.length - 1 - itemIndex));
                return sum + item.value * decay;
            }, 0);

            // 檢查這個時間點是否有矛盾
            const hasContradiction = contradictions.some(
                c => Math.abs(c.detectedAt - record.timestamp) < 60000 // 1分鐘內
            );

            return {
                turn: index + 1,
                tensionIntegral: Math.min(1, tensionIntegral),
                entropy: record.value,
                mode: soulMode,
                hasContradiction,
                timestamp: record.timestamp,
            };
        });
    }, [soulState, maxPoints]);

    // 統計數據
    const stats = useMemo(() => {
        if (timelinePoints.length === 0) return null;

        const values = timelinePoints.map(p => p.tensionIntegral);
        const avg = values.reduce((a, b) => a + b, 0) / values.length;
        const max = Math.max(...values);
        const min = Math.min(...values);
        const trend = values.length > 1
            ? values[values.length - 1] - values[0]
            : 0;

        return { avg, max, min, trend };
    }, [timelinePoints]);

    // 當前區間
    const currentZone = useMemo(() => {
        const current = soulState.tensionIntegral;
        if (current < 0.3) return { ...ZONE_CONFIG.echoChaber, value: current };
        if (current < 0.7) return { ...ZONE_CONFIG.healthyFriction, value: current };
        return { ...ZONE_CONFIG.chaos, value: current };
    }, [soulState.tensionIntegral]);

    if (timelinePoints.length < 2) {
        return (
            <div className="bg-gray-900/80 backdrop-blur border border-gray-700/50 rounded-xl p-4">
                <div className="flex items-center gap-2 mb-3">
                    <Activity className="w-4 h-4 text-purple-400" />
                    <span className="text-sm font-medium text-gray-300">張力時間軸</span>
                </div>
                <div className="text-center text-gray-500 text-xs py-4">
                    需要至少 2 輪對話才能顯示時間軸
                </div>
            </div>
        );
    }

    return (
        <div className="bg-gray-900/80 backdrop-blur border border-gray-700/50 rounded-xl p-4 space-y-3">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Activity className="w-4 h-4 text-purple-400" />
                    <span className="text-sm font-medium text-gray-300">張力時間軸</span>
                </div>
                <div className={`px-2 py-0.5 rounded text-[10px] font-medium ${currentZone.label === 'Echo Chamber' ? 'bg-green-900/50 text-green-400' :
                    currentZone.label === 'Healthy Friction' ? 'bg-yellow-900/50 text-yellow-400' :
                        'bg-red-900/50 text-red-400'
                    }`}>
                    {currentZone.label}
                </div>
            </div>

            {/* Chart */}
            <div className="flex justify-center">
                <MiniChart points={timelinePoints} />
            </div>

            {/* Stats Row */}
            {stats && (
                <div className="grid grid-cols-4 gap-2 text-center">
                    <div className="bg-gray-800/50 rounded px-2 py-1">
                        <div className="text-[10px] text-gray-500">平均</div>
                        <div className="text-xs font-medium text-gray-300">{(stats.avg * 100).toFixed(0)}%</div>
                    </div>
                    <div className="bg-gray-800/50 rounded px-2 py-1">
                        <div className="text-[10px] text-gray-500">最高</div>
                        <div className="text-xs font-medium text-red-400">{(stats.max * 100).toFixed(0)}%</div>
                    </div>
                    <div className="bg-gray-800/50 rounded px-2 py-1">
                        <div className="text-[10px] text-gray-500">最低</div>
                        <div className="text-xs font-medium text-green-400">{(stats.min * 100).toFixed(0)}%</div>
                    </div>
                    <div className="bg-gray-800/50 rounded px-2 py-1">
                        <div className="text-[10px] text-gray-500">趨勢</div>
                        <div className={`text-xs font-medium flex items-center justify-center gap-1 ${stats.trend > 0 ? 'text-red-400' : stats.trend < 0 ? 'text-green-400' : 'text-gray-400'
                            }`}>
                            <TrendingUp className={`w-3 h-3 ${stats.trend < 0 ? 'rotate-180' : ''}`} />
                            {Math.abs(stats.trend * 100).toFixed(0)}%
                        </div>
                    </div>
                </div>
            )}

            {/* Contradiction Warning */}
            {timelinePoints.some(p => p.hasContradiction) && (
                <div className="flex items-center gap-2 px-2 py-1.5 rounded bg-red-950/30 border border-red-800/30">
                    <AlertCircle className="w-3 h-3 text-red-400" />
                    <span className="text-[10px] text-red-300">
                        圖表中的紅點表示偵測到內在矛盾
                    </span>
                </div>
            )}
        </div>
    );
}

export { TensionTimeline };
