"use client";

import { useState } from "react";
import { Settings, X, Key, Check, AlertCircle, Zap, Users } from "lucide-react";

export type ApiProvider = "gemini" | "openai" | "claude" | "xai" | "ollama";
export type DeliberationMode = "fast" | "multipath";

export interface ApiSettings {
    provider: ApiProvider;
    apiKey: string;
    mode: DeliberationMode;
}

interface SettingsModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSave: (settings: ApiSettings) => void;
    currentSettings: ApiSettings | null;
}

const STORAGE_KEY = "tonesoul_api_settings";

export function isApiKeyRequired(provider: ApiProvider): boolean {
    return provider !== "ollama";
}

const PROVIDERS = [
    { id: "gemini" as ApiProvider, name: "Gemini", icon: "🔷", desc: "Google AI" },
    { id: "openai" as ApiProvider, name: "OpenAI", icon: "🟢", desc: "GPT-4o" },
    { id: "claude" as ApiProvider, name: "Claude", icon: "🟠", desc: "Anthropic" },
    { id: "xai" as ApiProvider, name: "xAI", icon: "⚡", desc: "Grok" },
    { id: "ollama" as ApiProvider, name: "Ollama", icon: "🦙", desc: "本地模型 (免費)" },
];

export function getStoredSettings(): ApiSettings | null {
    if (typeof window === "undefined") return null;
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return null;
    try {
        const parsed = JSON.parse(stored);
        // 向下兼容：如果沒有 mode，預設為 multipath
        if (!parsed.mode) parsed.mode = "multipath";
        return parsed;
    } catch {
        return null;
    }
}

export function saveSettings(settings: ApiSettings): void {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
}

export function clearSettings(): void {
    localStorage.removeItem(STORAGE_KEY);
}

export default function SettingsModal({
    isOpen,
    onClose,
    onSave,
    currentSettings,
}: SettingsModalProps) {
    const initialProvider = currentSettings?.provider || "gemini";
    const initialApiKey = currentSettings?.apiKey || "";
    const initialMode = currentSettings?.mode || "multipath";
    const [provider, setProvider] = useState<ApiProvider>(initialProvider);
    const [apiKey, setApiKey] = useState(initialApiKey);
    const [mode, setMode] = useState<DeliberationMode>(initialMode);
    const [showKey, setShowKey] = useState(false);
    const shouldShowTestInfo = isApiKeyRequired(provider) ? apiKey.trim().length > 0 : true;

    const handleSave = () => {
        const normalizedApiKey = apiKey.trim();
        const settings: ApiSettings = { provider, apiKey: normalizedApiKey, mode };
        saveSettings(settings);
        onSave(settings);
        onClose();
    };

    const handleClear = () => {
        clearSettings();
        setApiKey("");
        setProvider("gemini");
        setMode("multipath");
        onSave({ provider: "gemini", apiKey: "", mode: "multipath" });
    };

    const getPlaceholder = () => {
        switch (provider) {
            case "gemini": return "AIzaSy...";
            case "openai": return "sk-...";
            case "claude": return "sk-ant-...";
            case "xai": return "xai-...";
            case "ollama": return "Ollama 不需要 API Key";
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-y-auto">
                {/* Header */}
                <div className="p-6 border-b border-slate-100 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-indigo-100 rounded-xl">
                            <Settings className="w-5 h-5 text-indigo-600" />
                        </div>
                        <h2 className="text-lg font-bold text-slate-800">API 設定</h2>
                    </div>
                    <button type="button"
                        onClick={onClose}
                        className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                    >
                        <X className="w-5 h-5 text-slate-500" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-5">
                    {/* Mode Selection */}
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">
                            審議模式
                        </label>
                        <div className="grid grid-cols-2 gap-3">
                            <button type="button"
                                onClick={() => setMode("fast")}
                                className={`p-3 rounded-xl border-2 transition-all ${mode === "fast"
                                    ? "border-emerald-500 bg-emerald-50"
                                    : "border-slate-200 hover:border-slate-300"
                                    }`}
                            >
                                <div className="flex items-center gap-2 mb-1">
                                    <Zap className="w-4 h-4 text-emerald-500" />
                                    <span className="font-bold">快速模式</span>
                                </div>
                                <div className="text-xs text-slate-500">1 次 API 調用</div>
                            </button>
                            <button type="button"
                                onClick={() => setMode("multipath")}
                                className={`p-3 rounded-xl border-2 transition-all ${mode === "multipath"
                                    ? "border-purple-500 bg-purple-50"
                                    : "border-slate-200 hover:border-slate-300"
                                    }`}
                            >
                                <div className="flex items-center gap-2 mb-1">
                                    <Users className="w-4 h-4 text-purple-500" />
                                    <span className="font-bold">多路徑審議</span>
                                </div>
                                <div className="text-xs text-slate-500">4 次 API 調用</div>
                            </button>
                        </div>
                    </div>

                    {/* Backend Mode Notice */}
                    {process.env.NEXT_PUBLIC_CHAT_EXECUTION_MODE === "backend" && (
                        <div className="bg-sky-50 border border-sky-200 rounded-xl p-4">
                            <div className="flex items-start gap-2">
                                <span className="text-sky-600 mt-0.5 flex-shrink-0">🔗</span>
                                <div className="text-sm text-sky-800">
                                    <strong>目前連線後端伺服器。</strong>
                                    <br />
                                    下方 API 提供者設定僅在後端不可用時作為備用。
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Provider Selection */}
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">
                            API 提供者
                        </label>
                        <div className="grid grid-cols-2 gap-2">
                            {PROVIDERS.map((p) => (
                                <button type="button"
                                    key={p.id}
                                    onClick={() => setProvider(p.id)}
                                    className={`p-3 rounded-xl border-2 transition-all ${provider === p.id
                                        ? "border-indigo-500 bg-indigo-50"
                                        : "border-slate-200 hover:border-slate-300"
                                        }`}
                                >
                                    <div className="text-lg font-bold">{p.icon} {p.name}</div>
                                    <div className="text-xs text-slate-500">{p.desc}</div>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* API Key Input */}
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">
                            <Key className="w-4 h-4 inline mr-1" />
                            API Key {isApiKeyRequired(provider) ? "" : "(選填)"}
                        </label>
                        <div className="relative">
                            <input
                                type={showKey ? "text" : "password"}
                                value={apiKey}
                                onChange={(e) => setApiKey(e.target.value)}
                                placeholder={getPlaceholder()}
                                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 pr-20"
                            />
                            <button type="button"
                                onClick={() => setShowKey(!showKey)}
                                className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-500 hover:text-slate-700"
                            >
                                {showKey ? "隱藏" : "顯示"}
                            </button>
                        </div>
                    </div>

                    {/* Mode Info */}
                    <div className={`rounded-xl p-4 border ${mode === "multipath" ? "bg-purple-50 border-purple-200" : "bg-emerald-50 border-emerald-200"}`}>
                        <div className="flex items-start gap-2">
                            {mode === "multipath" ? (
                                <Users className="w-4 h-4 text-purple-600 mt-0.5 flex-shrink-0" />
                            ) : (
                                <Zap className="w-4 h-4 text-emerald-600 mt-0.5 flex-shrink-0" />
                            )}
                            <div className={`text-sm ${mode === "multipath" ? "text-purple-800" : "text-emerald-800"}`}>
                                {mode === "multipath" ? (
                                    <>
                                        <strong>多路徑模式：</strong>每條訊息 4 次 API 調用
                                        <br />
                                        Philosopher → Engineer → Guardian → Synthesizer
                                    </>
                                ) : (
                                    <>
                                        <strong>快速模式：</strong>每條訊息 1 次 API 調用
                                        <br />
                                        省錢/快速，但只有單一視角
                                    </>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Security Notice */}
                    <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
                        <div className="flex items-start gap-2">
                            <AlertCircle className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
                            <div className="text-sm text-amber-800">
                                <strong>安全提示：</strong>你的 API Key 只會儲存在你的瀏覽器中（localStorage），
                                不會傳送到我們的伺服器。
                            </div>
                        </div>
                    </div>

                    {/* Test Info */}
                    {shouldShowTestInfo ? (
                        <div className="bg-blue-50 border border-blue-200 rounded-xl p-3 text-sm text-blue-700">
                            {isApiKeyRequired(provider)
                                ? "💡 儲存後，傳送任何訊息即可測試 API Key 是否有效。"
                                : "💡 Ollama 使用本機服務（預設 http://localhost:11434），不需要 API Key。"}
                        </div>
                    ) : null}
                </div>

                {/* Footer */}
                <div className="p-6 border-t border-slate-100 flex gap-3">
                    <button type="button"
                        onClick={handleClear}
                        className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                    >
                        清除設定
                    </button>
                    <div className="flex-1" />
                    <button type="button"
                        onClick={onClose}
                        className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                    >
                        取消
                    </button>
                    <button type="button"
                        onClick={handleSave}
                        disabled={isApiKeyRequired(provider) && !apiKey.trim()}
                        className="px-6 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                        <Check className="w-4 h-4" />
                        儲存
                    </button>
                </div>
            </div>
        </div>
    );
}

