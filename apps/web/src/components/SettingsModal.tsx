"use client";

import { useState, useEffect } from "react";
import { Settings, X, Key, Check, AlertCircle } from "lucide-react";

export type ApiProvider = "gemini" | "openai";

export interface ApiSettings {
    provider: ApiProvider;
    apiKey: string;
}

interface SettingsModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSave: (settings: ApiSettings) => void;
    currentSettings: ApiSettings | null;
}

const STORAGE_KEY = "tonesoul_api_settings";

export function getStoredSettings(): ApiSettings | null {
    if (typeof window === "undefined") return null;
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return null;
    try {
        return JSON.parse(stored);
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
    const [provider, setProvider] = useState<ApiProvider>(
        currentSettings?.provider || "gemini"
    );
    const [apiKey, setApiKey] = useState(currentSettings?.apiKey || "");
    const [showKey, setShowKey] = useState(false);
    const [testStatus, setTestStatus] = useState<"idle" | "testing" | "success" | "error">("idle");

    useEffect(() => {
        if (currentSettings) {
            setProvider(currentSettings.provider);
            setApiKey(currentSettings.apiKey);
        }
    }, [currentSettings]);

    const handleSave = () => {
        const settings: ApiSettings = { provider, apiKey };
        saveSettings(settings);
        onSave(settings);
        onClose();
    };

    const handleTest = async () => {
        if (!apiKey.trim()) return;
        setTestStatus("testing");

        try {
            let isSuccess = false;

            if (provider === "gemini") {
                try {
                    const response = await fetch(
                        `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`,
                        {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({
                                contents: [{ parts: [{ text: "Say hello in 5 words or less." }] }],
                            }),
                        }
                    );
                    isSuccess = response.ok;
                } catch (fetchError) {
                    console.error("Gemini test fetch error:", fetchError);
                    isSuccess = false;
                }
            } else if (provider === "openai") {
                try {
                    const response = await fetch("https://api.openai.com/v1/models", {
                        headers: { Authorization: `Bearer ${apiKey}` },
                    });
                    isSuccess = response.ok;
                } catch (fetchError) {
                    console.error("OpenAI test fetch error:", fetchError);
                    isSuccess = false;
                }
            }

            setTestStatus(isSuccess ? "success" : "error");
        } catch (error) {
            console.error("Test connection error:", error);
            setTestStatus("error");
        }

        // Reset after 3 seconds
        setTimeout(() => setTestStatus("idle"), 3000);
    };

    const handleClear = () => {
        clearSettings();
        setApiKey("");
        setProvider("gemini");
        onSave({ provider: "gemini", apiKey: "" });
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md">
                {/* Header */}
                <div className="p-6 border-b border-slate-100 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-indigo-100 rounded-xl">
                            <Settings className="w-5 h-5 text-indigo-600" />
                        </div>
                        <h2 className="text-lg font-bold text-slate-800">API 設定</h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                    >
                        <X className="w-5 h-5 text-slate-500" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-5">
                    {/* Provider Selection */}
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">
                            API 提供者
                        </label>
                        <div className="grid grid-cols-2 gap-3">
                            <button
                                onClick={() => setProvider("gemini")}
                                className={`p-3 rounded-xl border-2 transition-all ${provider === "gemini"
                                    ? "border-indigo-500 bg-indigo-50"
                                    : "border-slate-200 hover:border-slate-300"
                                    }`}
                            >
                                <div className="text-lg font-bold">🔷 Gemini</div>
                                <div className="text-xs text-slate-500">Google AI</div>
                            </button>
                            <button
                                onClick={() => setProvider("openai")}
                                className={`p-3 rounded-xl border-2 transition-all ${provider === "openai"
                                    ? "border-indigo-500 bg-indigo-50"
                                    : "border-slate-200 hover:border-slate-300"
                                    }`}
                            >
                                <div className="text-lg font-bold">🟢 OpenAI</div>
                                <div className="text-xs text-slate-500">GPT-4o</div>
                            </button>
                        </div>
                    </div>

                    {/* API Key Input */}
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">
                            <Key className="w-4 h-4 inline mr-1" />
                            API Key
                        </label>
                        <div className="relative">
                            <input
                                type={showKey ? "text" : "password"}
                                value={apiKey}
                                onChange={(e) => setApiKey(e.target.value)}
                                placeholder={
                                    provider === "gemini"
                                        ? "AIzaSy..."
                                        : "sk-..."
                                }
                                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 pr-20"
                            />
                            <button
                                onClick={() => setShowKey(!showKey)}
                                className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-500 hover:text-slate-700"
                            >
                                {showKey ? "隱藏" : "顯示"}
                            </button>
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

                    {/* Test Button */}
                    {apiKey && (
                        <button
                            onClick={handleTest}
                            disabled={testStatus === "testing"}
                            className={`w-full py-2 rounded-xl text-sm font-medium transition-colors ${testStatus === "success"
                                ? "bg-emerald-100 text-emerald-700"
                                : testStatus === "error"
                                    ? "bg-red-100 text-red-700"
                                    : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                                }`}
                        >
                            {testStatus === "testing" && "測試中..."}
                            {testStatus === "success" && "✓ 連接成功！"}
                            {testStatus === "error" && "✗ 連接失敗，請檢查 Key"}
                            {testStatus === "idle" && "測試連接"}
                        </button>
                    )}
                </div>

                {/* Footer */}
                <div className="p-6 border-t border-slate-100 flex gap-3">
                    <button
                        onClick={handleClear}
                        className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                    >
                        清除設定
                    </button>
                    <div className="flex-1" />
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                    >
                        取消
                    </button>
                    <button
                        onClick={handleSave}
                        disabled={!apiKey}
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
