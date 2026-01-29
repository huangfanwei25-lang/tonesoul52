'use client';

import React from 'react';
import { Brain, Compass, Scale, AlertCircle, Gauge, Shield, Lightbulb, BookOpen } from 'lucide-react';
import type { SoulState, SoulMode, TensionTensor } from '@/lib/soulEngine';

interface SoulDriveMeterProps {
    soulState: SoulState;
    tensionTensor?: TensionTensor;
    compact?: boolean;
}

const getModeConfig = (mode: SoulMode) => {
    switch (mode) {
        case 'dormant':
            return { icon: '💤', label: '休眠', color: 'text-gray-400', bg: 'bg-gray-800/50' };
        case 'responsive':
            return { icon: '✨', label: '響應', color: 'text-blue-400', bg: 'bg-blue-900/30' };
        case 'seeking':
            return { icon: '🔍', label: '探索', color: 'text-cyan-400', bg: 'bg-cyan-900/30' };
        case 'conflicted':
            return { icon: '⚡', label: '內省', color: 'text-amber-400', bg: 'bg-amber-900/30' };
        default:
            return { icon: '🔮', label: mode, color: 'text-purple-400', bg: 'bg-purple-900/30' };
    }
};

const DriveBar: React.FC<{
    value: number;
    label: string;
    icon: React.ReactNode;
    color: string;
}> = ({ value, label, icon, color }) => (
    <div className="flex items-center gap-2">
        <div className={`w-5 h-5 flex items-center justify-center ${color}`}>
            {icon}
        </div>
        <span className="w-14 text-[10px] text-gray-400 uppercase tracking-wide">{label}</span>
        <div className="flex-1 h-1.5 bg-gray-700/50 rounded-full overflow-hidden">
            <div
                className={`h-full transition-all duration-700 ease-out rounded-full`}
                style={{
                    width: `${Math.max(3, value * 100)}%`,
                    background: `linear-gradient(90deg, ${color.replace('text-', 'rgb(var(--')}, transparent)`,
                }}
            />
        </div>
        <span className="w-7 text-[10px] text-gray-500 text-right">
            {(value * 100).toFixed(0)}%
        </span>
    </div>
);

export default function SoulDriveMeter({ soulState, tensionTensor, compact = false }: SoulDriveMeterProps) {
    const { tensionIntegral, intrinsicDrive, soulMode, contradictions, totalTurns } = soulState;
    const modeConfig = getModeConfig(soulMode);
    const unresolvedContradictions = contradictions.filter(c => !c.resolved).length;

    if (compact) {
        return (
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg ${modeConfig.bg}`}>
                <span className="text-sm">{modeConfig.icon}</span>
                <span className={`text-xs font-medium ${modeConfig.color}`}>
                    {modeConfig.label}
                </span>
                <span className="text-[10px] text-gray-500">
                    S:{(tensionIntegral * 100).toFixed(0)}
                </span>
            </div>
        );
    }

    return (
        <div className="bg-gray-900/80 backdrop-blur border border-gray-700/50 rounded-xl p-4 space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <span className="text-xl">{modeConfig.icon}</span>
                    <div>
                        <div className="text-sm font-medium text-gray-200">靈魂狀態</div>
                        <div className={`text-[10px] ${modeConfig.color}`}>
                            {modeConfig.label} Mode
                        </div>
                    </div>
                </div>
                <div className="text-right">
                    <div className="text-xs text-gray-500">Turn {totalTurns}</div>
                    <div className="text-lg font-bold text-purple-400">
                        {(tensionIntegral * 100).toFixed(0)}
                        <span className="text-xs text-gray-500 ml-1">殘留</span>
                    </div>
                </div>
            </div>

            {/* Tension Integral Bar */}
            <div className="relative">
                <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                    <div
                        className="h-full bg-gradient-to-r from-purple-600 to-purple-400 transition-all duration-700"
                        style={{ width: `${tensionIntegral * 100}%` }}
                    />
                </div>
                <div className="absolute -top-0.5 left-0 w-full h-3 flex">
                    {/* Zone markers */}
                    <div className="w-[30%] border-r border-gray-600/50" />
                    <div className="w-[40%] border-r border-gray-600/50" />
                    <div className="w-[30%]" />
                </div>
            </div>

            {/* Divider */}
            <div className="flex items-center gap-2 text-[10px] text-gray-500 uppercase tracking-wider">
                <div className="flex-1 h-px bg-gray-700" />
                <span>內在驅動</span>
                <div className="flex-1 h-px bg-gray-700" />
            </div>

            {/* Intrinsic Drive Bars */}
            <div className="space-y-2">
                <DriveBar
                    value={intrinsicDrive.curiosity}
                    label="好奇心"
                    icon={<Compass className="w-3.5 h-3.5" />}
                    color="text-cyan-400"
                />
                <DriveBar
                    value={intrinsicDrive.coherence}
                    label="一致性"
                    icon={<Scale className="w-3.5 h-3.5" />}
                    color="text-amber-400"
                />
                <DriveBar
                    value={intrinsicDrive.integrity}
                    label="完整性"
                    icon={<Brain className="w-3.5 h-3.5" />}
                    color="text-emerald-400"
                />
            </div>

            {/* TensionTensor 阻力向量 (Yu-Hun Model) */}
            {tensionTensor && (
                <>
                    <div className="flex items-center gap-2 text-[10px] text-gray-500 uppercase tracking-wider">
                        <div className="flex-1 h-px bg-gray-700" />
                        <span>阻力向量 D</span>
                        <div className="flex-1 h-px bg-gray-700" />
                    </div>

                    <div className="space-y-2">
                        <DriveBar
                            value={tensionTensor.D_resistance.fact}
                            label="事實"
                            icon={<BookOpen className="w-3.5 h-3.5" />}
                            color="text-blue-400"
                        />
                        <DriveBar
                            value={tensionTensor.D_resistance.logic}
                            label="邏輯"
                            icon={<Lightbulb className="w-3.5 h-3.5" />}
                            color="text-yellow-400"
                        />
                        <DriveBar
                            value={tensionTensor.D_resistance.ethics}
                            label="倫理"
                            icon={<Shield className="w-3.5 h-3.5" />}
                            color="text-red-400"
                        />
                    </div>

                    {/* Tensor Status */}
                    <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-gray-800/50">
                        <div className="flex items-center gap-2">
                            <Gauge className="w-4 h-4 text-purple-400" />
                            <span className="text-xs text-gray-300">T = {tensionTensor.total_T.toFixed(2)}</span>
                        </div>
                        <span className={`text-xs font-medium ${tensionTensor.status === 'Echo Chamber' ? 'text-gray-400' :
                                tensionTensor.status === 'Healthy Friction' ? 'text-green-400' :
                                    'text-red-400'
                            }`}>
                            {tensionTensor.status}
                        </span>
                    </div>
                </>
            )}

            {/* Contradictions Warning */}
            {unresolvedContradictions > 0 && (
                <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-amber-950/30 border border-amber-800/30">
                    <AlertCircle className="w-4 h-4 text-amber-400" />
                    <span className="text-xs text-amber-300">
                        {unresolvedContradictions} 個內在張力待解決
                    </span>
                </div>
            )}
        </div>
    );
}

export { SoulDriveMeter };
