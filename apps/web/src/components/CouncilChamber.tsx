"use client";

import { Lightbulb, Cpu, Shield, AlertCircle, Heart } from "lucide-react";

interface CouncilMember {
    internal_monologue?: string;
    self_diagnosed_tension?: number;
    stance: string;
    conflict_point?: string;
    benevolence_check?: string;
}

interface CouncilChamberProps {
    philosopher?: CouncilMember;
    engineer?: CouncilMember;
    guardian?: CouncilMember;
    role_tensions?: Array<{
        from: string;
        from_role: string;
        to: string;
        to_role: string;
        reason: string;
        counter_reason: string;
        evidence: string[];
    }>;
    recommended_action?: string;
}

interface CouncilRowProps {
    role: string;
    data?: CouncilMember;
    icon: React.ElementType;
    colorClass: string;
    bgClass: string;
}

const CouncilRow = ({ role, data, icon: Icon, colorClass, bgClass }: CouncilRowProps) => {
    if (!data) return null;

    const textColor = colorClass.includes("amber")
        ? "text-amber-700"
        : colorClass.includes("blue")
            ? "text-blue-700"
            : "text-emerald-700";

    const iconColor = colorClass.includes("amber")
        ? "text-amber-600"
        : colorClass.includes("blue")
            ? "text-blue-600"
            : "text-emerald-600";

    return (
        <div className={`w-full p-4 rounded-xl border ${colorClass} ${bgClass} transition-all hover:shadow-md`}>
            <div className="flex flex-col sm:flex-row gap-3">
                {/* 左側：身份標識 */}
                <div className="flex sm:flex-col items-center sm:items-start gap-2 sm:w-24 shrink-0 border-b sm:border-b-0 sm:border-r border-black/5 pb-2 sm:pb-0 sm:pr-3">
                    <div className={`p-2 rounded-full bg-white/60 ${iconColor}`}>
                        <Icon className="w-4 h-4" />
                    </div>
                    <span className={`text-xs font-bold uppercase tracking-wider ${textColor}`}>
                        {role}
                    </span>
                </div>

                {/* 右側：觀點內容 */}
                <div className="flex-1 space-y-2">
                    <div>
                        <span className="text-[10px] font-bold text-slate-400 uppercase block mb-1">
                            觀點 (Stance)
                        </span>
                        <p className="text-sm font-medium text-slate-800 leading-relaxed whitespace-pre-wrap">
                            {data.stance || "思考中..."}
                        </p>
                    </div>

                    {data.internal_monologue && (
                        <div className="mt-2 text-xs italic text-slate-500 border-l-2 border-slate-300 pl-2 py-0.5">
                            <span className="font-semibold block mb-0.5">💭 內在獨白 (Monologue) — 診斷張力: {data.self_diagnosed_tension !== undefined ? data.self_diagnosed_tension.toFixed(2) : "0.00"}</span>
                            {data.internal_monologue}
                        </div>
                    )}

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {data.conflict_point && (
                            <div className="flex items-start gap-2 bg-white/60 p-2.5 rounded-lg border border-white/50">
                                <AlertCircle className="w-4 h-4 mt-0.5 shrink-0 text-amber-500" />
                                <div>
                                    <span className="text-[10px] font-bold text-amber-600 uppercase block mb-0.5">
                                        摩擦點 (Friction)
                                    </span>
                                    <span className="text-xs text-slate-700">{data.conflict_point}</span>
                                </div>
                            </div>
                        )}

                        {data.benevolence_check && (
                            <div className="flex items-start gap-2 bg-white/60 p-2.5 rounded-lg border border-white/50">
                                <Heart className="w-4 h-4 mt-0.5 shrink-0 text-pink-500" />
                                <div>
                                    <span className="text-[10px] font-bold text-pink-600 uppercase block mb-0.5">
                                        仁慈檢查 (Benevolence)
                                    </span>
                                    <span className="text-xs text-slate-700">{data.benevolence_check}</span>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default function CouncilChamber({ philosopher, engineer, guardian, role_tensions, recommended_action }: CouncilChamberProps) {
    if (!philosopher && !engineer && !guardian && (!role_tensions || role_tensions.length === 0)) return null;

    return (
        <div className="space-y-3">
            <div className="flex items-center gap-2 mb-2">
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                    內在議會 (Internal Council)
                </span>
            </div>

            {recommended_action && (
                <div className="p-3 mb-3 bg-indigo-50 border border-indigo-200 rounded-lg">
                    <span className="text-xs font-bold text-indigo-700 block mb-1">RECOMMENDED ACTION</span>
                    <p className="text-sm text-indigo-900">{recommended_action}</p>
                </div>
            )}

            {role_tensions && role_tensions.length > 0 && (
                <div className="space-y-2 mb-4">
                    <span className="text-[10px] font-bold text-rose-500 uppercase tracking-wider block mb-2">
                        議會張力衝突點 (Divergence Traces)
                    </span>
                    {role_tensions.map((tension, idx) => (
                        <div key={idx} className="p-3 bg-rose-50/50 border border-rose-100 rounded-lg text-sm">
                            <div className="flex items-center gap-2 mb-1.5">
                                <span className="font-semibold text-rose-700">{tension.from}</span>
                                <span className="text-rose-400 text-xs px-2">vs</span>
                                <span className="font-semibold text-rose-700">{tension.to}</span>
                            </div>
                            <div className="grid grid-cols-2 gap-3 text-xs mb-2">
                                <div className="p-2 bg-white/60 rounded border border-rose-50">
                                    <span className="font-medium text-rose-800/60 block mb-0.5">觀點</span>
                                    <span className="text-rose-950">{tension.reason}</span>
                                </div>
                                <div className="p-2 bg-white/60 rounded border border-rose-50">
                                    <span className="font-medium text-rose-800/60 block mb-0.5">反駁</span>
                                    <span className="text-rose-950">{tension.counter_reason}</span>
                                </div>
                            </div>
                            {tension.evidence && tension.evidence.length > 0 && (
                                <div className="mt-2 pt-2 border-t border-rose-100/50">
                                    <span className="text-[10px] font-bold text-rose-400 block mb-1">EVIDENCE TRACE</span>
                                    <ul className="list-disc list-inside text-xs text-rose-900/80 space-y-0.5">
                                        {tension.evidence.map((ev, i) => (
                                            <li key={i}>{ev}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}

            {(philosopher || engineer || guardian) && (
                <div className="space-y-2">
                    <CouncilRow
                        role="Philosopher"
                        data={philosopher}
                        icon={Lightbulb}
                        colorClass="border-amber-200"
                        bgClass="bg-amber-50"
                    />
                    <CouncilRow
                        role="Engineer"
                        data={engineer}
                        icon={Cpu}
                        colorClass="border-blue-200"
                        bgClass="bg-blue-50"
                    />
                    <CouncilRow
                        role="Guardian"
                        data={guardian}
                        icon={Shield}
                        colorClass="border-emerald-200"
                        bgClass="bg-emerald-50"
                    />
                </div>
            )}
        </div>
    );
}
