"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { ChevronDown, Cloud, Monitor, Zap, XCircle, Brain, Loader2 } from "lucide-react";

type LlmMode = "cloud" | "local" | "auto" | "unavailable";

interface LlmStatus {
    mode: LlmMode;
    backend: string;
}

const MODE_CONFIG: Record<LlmMode, { icon: React.ReactNode; label: string; color: string; bg: string; border: string }> = {
    cloud: {
        icon: <Cloud className="w-3.5 h-3.5" />,
        label: "雲端 Cloud",
        color: "text-violet-400",
        bg: "bg-violet-500/20",
        border: "border-violet-500/30",
    },
    local: {
        icon: <Monitor className="w-3.5 h-3.5" />,
        label: "本地 Local",
        color: "text-emerald-400",
        bg: "bg-emerald-500/20",
        border: "border-emerald-500/30",
    },
    auto: {
        icon: <Zap className="w-3.5 h-3.5" />,
        label: "自動 Auto",
        color: "text-slate-400",
        bg: "bg-slate-500/20",
        border: "border-slate-500/30",
    },
    unavailable: {
        icon: <XCircle className="w-3.5 h-3.5" />,
        label: "不可用",
        color: "text-red-400",
        bg: "bg-red-500/20",
        border: "border-red-500/30",
    },
};

export default function LlmSwitcher() {
    const [status, setStatus] = useState<LlmStatus>({ mode: "auto", backend: "" });
    const [isOpen, setIsOpen] = useState(false);
    const [switching, setSwitching] = useState(false);
    const [localModels, setLocalModels] = useState<string[]>([]);
    const [localAvailable, setLocalAvailable] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    const fetchStatus = useCallback(async () => {
        try {
            const res = await fetch("/api/backend-health");
            if (!res.ok) {
                setStatus({ mode: "unavailable", backend: "unavailable" });
                return;
            }
            // Also try to get the LLM status from the backend's /api/status
            const statusRes = await fetch("/api/backend-health");
            const statusData = await statusRes.json();
            if (statusData.ok) {
                // Backend is healthy; try to get LLM mode info
                // We'll default to auto when we don't have explicit mode info
                setStatus({ mode: "auto", backend: "connected" });
            } else {
                setStatus({ mode: "unavailable", backend: "unavailable" });
            }
        } catch {
            setStatus({ mode: "unavailable", backend: "unavailable" });
        }
    }, []);

    const fetchLocalModels = useCallback(async () => {
        try {
            const res = await fetch("/api/llm-models");
            const data = await res.json();
            if (data.available && data.models?.length > 0) {
                setLocalModels(data.models);
                setLocalAvailable(true);
            } else {
                setLocalModels([]);
                setLocalAvailable(false);
            }
        } catch {
            setLocalModels([]);
            setLocalAvailable(false);
        }
    }, []);

    useEffect(() => {
        void fetchStatus();
    }, [fetchStatus]);

    useEffect(() => {
        if (isOpen) {
            void fetchLocalModels();
        }
    }, [isOpen, fetchLocalModels]);

    // Close on outside click
    useEffect(() => {
        function handleClickOutside(e: MouseEvent) {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
                setIsOpen(false);
            }
        }
        if (isOpen) {
            document.addEventListener("mousedown", handleClickOutside);
            return () => document.removeEventListener("mousedown", handleClickOutside);
        }
    }, [isOpen]);

    const handleSwitch = async (mode: "gemini" | "ollama", model?: string) => {
        if (mode === "ollama" && !localAvailable) return;
        setSwitching(true);
        setIsOpen(false);

        try {
            const body: Record<string, string> = { mode };
            if (model) body.model = model;

            const res = await fetch("/api/llm-switch", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body),
            });
            const data = await res.json();

            if (data.success) {
                setStatus({
                    mode: data.llm_mode as LlmMode,
                    backend: data.llm_backend || "",
                });
            }
        } catch {
            // silently fail
        } finally {
            setSwitching(false);
        }
    };

    const cfg = MODE_CONFIG[status.mode] || MODE_CONFIG.auto;

    return (
        <div ref={dropdownRef} className="relative">
            {/* Trigger Button */}
            <button
                type="button"
                onClick={() => setIsOpen(!isOpen)}
                disabled={switching}
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border transition-all hover:brightness-110 ${cfg.color} ${cfg.bg} ${cfg.border} ${switching ? "opacity-50" : ""}`}
                title={status.backend ? `Model: ${status.backend}` : "LLM Mode"}
            >
                {switching ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : cfg.icon}
                <span className="hidden sm:inline">{switching ? "切換中..." : cfg.label}</span>
                <ChevronDown className={`w-3 h-3 transition-transform ${isOpen ? "rotate-180" : ""}`} />
            </button>

            {/* Dropdown */}
            {isOpen && (
                <div className="absolute right-0 top-full mt-2 w-60 bg-slate-800 border border-slate-700 rounded-xl shadow-2xl z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
                    <div className="px-3 py-2 border-b border-slate-700">
                        <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                            選擇模式 Select Mode
                        </p>
                    </div>

                    {/* Cloud option */}
                    <button
                        type="button"
                        onClick={() => handleSwitch("gemini")}
                        className={`w-full flex items-center gap-3 px-3 py-2.5 text-left text-sm transition-colors hover:bg-slate-700/50 ${status.mode === "cloud" ? "text-violet-400 bg-violet-500/10" : "text-slate-300"}`}
                    >
                        <Cloud className="w-4 h-4" />
                        <div className="flex-1">
                            <div>雲端模式 Cloud</div>
                            <div className="text-[10px] text-slate-500">Gemini API</div>
                        </div>
                        {status.mode === "cloud" && <span className="text-emerald-400 text-sm">✓</span>}
                    </button>

                    {/* Local option */}
                    <button
                        type="button"
                        onClick={() => handleSwitch("ollama")}
                        disabled={!localAvailable}
                        className={`w-full flex items-center gap-3 px-3 py-2.5 text-left text-sm transition-colors ${!localAvailable ? "opacity-40 cursor-not-allowed" : "hover:bg-slate-700/50"} ${status.mode === "local" ? "text-emerald-400 bg-emerald-500/10" : "text-slate-300"}`}
                    >
                        <Monitor className="w-4 h-4" />
                        <div className="flex-1">
                            <div>本地模式 Local</div>
                            <div className="text-[10px] text-slate-500">
                                {localAvailable ? `Ollama · ${localModels.length} models` : "未偵測到 Not detected"}
                            </div>
                        </div>
                        {status.mode === "local" && <span className="text-emerald-400 text-sm">✓</span>}
                    </button>

                    {/* Local models list */}
                    {localAvailable && localModels.length > 0 && (
                        <>
                            <div className="h-px bg-slate-700" />
                            <div className="px-3 py-1.5">
                                <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                                    本地模型 Local Models
                                </p>
                            </div>
                            <div className="max-h-36 overflow-y-auto px-1.5 pb-1.5">
                                {localModels.map((m) => (
                                    <button
                                        key={m}
                                        type="button"
                                        onClick={() => handleSwitch("ollama", m)}
                                        className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs text-slate-400 hover:bg-emerald-500/10 hover:text-emerald-300 transition-colors text-left"
                                    >
                                        <Brain className="w-3.5 h-3.5" />
                                        <span className="truncate">{m}</span>
                                    </button>
                                ))}
                            </div>
                        </>
                    )}
                </div>
            )}
        </div>
    );
}
