"use client";

import { Lightbulb, Cpu, Shield, AlertCircle } from "lucide-react";

interface CouncilMember {
    stance: string;
    conflict_point?: string;
}

interface CouncilChamberProps {
    philosopher?: CouncilMember;
    engineer?: CouncilMember;
    guardian?: CouncilMember;
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
                </div>
            </div>
        </div>
    );
};

export default function CouncilChamber({ philosopher, engineer, guardian }: CouncilChamberProps) {
    if (!philosopher && !engineer && !guardian) return null;

    return (
        <div className="space-y-3">
            <div className="flex items-center gap-2 mb-2">
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                    內在議會 (Internal Council)
                </span>
            </div>

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
        </div>
    );
}
