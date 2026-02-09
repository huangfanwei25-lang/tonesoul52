"use client";

import { useState } from "react";
import { Sliders, X, Save, RotateCcw, User, Shield, Lightbulb, Wrench } from "lucide-react";

// ==================== 人格設定介面 ====================

export interface PersonaConfig {
    name: string;                    // AI 名稱
    greeting: string;                // 開場語
    style: 'balanced' | 'creative' | 'analytical' | 'cautious';  // 整體風格
    // 三視角權重 (總和不需要 = 1，只是相對比例)
    weights: {
        meaning: number;             // 意義探索 (0-100)
        practical: number;           // 實用導向 (0-100)
        safety: number;              // 安全考量 (0-100)
    };
    riskSensitivity: 'low' | 'medium' | 'high';  // 風險敏感度
    responseLength: 'concise' | 'balanced' | 'detailed';  // 回應長度傾向
}

// 預設設定
export const DEFAULT_PERSONA: PersonaConfig = {
    name: "ToneSoul",
    greeting: "你好！有什麼我可以幫你的嗎？",
    style: 'balanced',
    weights: {
        meaning: 50,
        practical: 50,
        safety: 50,
    },
    riskSensitivity: 'medium',
    responseLength: 'balanced',
};

// localStorage 存取
const PERSONA_KEY = 'tonesoul_persona';

export function getStoredPersona(): PersonaConfig {
    if (typeof window === 'undefined') return DEFAULT_PERSONA;
    const stored = localStorage.getItem(PERSONA_KEY);
    if (!stored) return DEFAULT_PERSONA;
    try {
        return { ...DEFAULT_PERSONA, ...JSON.parse(stored) };
    } catch {
        return DEFAULT_PERSONA;
    }
}

export function savePersona(config: PersonaConfig): void {
    localStorage.setItem(PERSONA_KEY, JSON.stringify(config));
}

// ==================== 設定元件 ====================

interface PersonaSettingsProps {
    isOpen: boolean;
    onClose: () => void;
    onSave: (config: PersonaConfig) => void;
}

export default function PersonaSettings({ isOpen, onClose, onSave }: PersonaSettingsProps) {
    const [config, setConfig] = useState<PersonaConfig>(() => getStoredPersona());

    const handleSave = () => {
        savePersona(config);
        onSave(config);
        onClose();
    };

    const handleReset = () => {
        setConfig(DEFAULT_PERSONA);
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
                {/* Header */}
                <div className="p-6 border-b border-slate-100 flex justify-between items-center sticky top-0 bg-white z-10">
                    <div className="flex items-center gap-2">
                        <Sliders className="w-5 h-5 text-indigo-600" />
                        <h2 className="text-xl font-bold text-slate-800">AI 個人化設定</h2>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-slate-100 rounded-full transition-colors">
                        <X className="w-5 h-5 text-slate-500" />
                    </button>
                </div>

                <div className="p-6 space-y-6">
                    {/* 名稱與開場語 */}
                    <div className="space-y-4">
                        <div>
                            <label className="flex items-center gap-2 text-sm font-bold text-slate-700 mb-2">
                                <User className="w-4 h-4" />
                                AI 名稱
                            </label>
                            <input
                                type="text"
                                value={config.name}
                                onChange={(e) => setConfig({ ...config, name: e.target.value })}
                                className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                                placeholder="例如：小助手"
                            />
                        </div>
                        <div>
                            <label className="text-sm font-bold text-slate-700 mb-2 block">開場語</label>
                            <input
                                type="text"
                                value={config.greeting}
                                onChange={(e) => setConfig({ ...config, greeting: e.target.value })}
                                className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                                placeholder="例如：嗨！有什麼需要幫忙的嗎？"
                            />
                        </div>
                    </div>

                    {/* 整體風格 */}
                    <div>
                        <label className="text-sm font-bold text-slate-700 mb-3 block">回應風格</label>
                        <div className="grid grid-cols-2 gap-2">
                            {[
                                { value: 'balanced', label: '均衡', desc: '各方面平衡考量' },
                                { value: 'creative', label: '創意', desc: '更多想像與可能性' },
                                { value: 'analytical', label: '分析', desc: '邏輯與數據導向' },
                                { value: 'cautious', label: '謹慎', desc: '更注重風險提醒' },
                            ].map(({ value, label, desc }) => (
                                <button
                                    key={value}
                                    onClick={() => setConfig({ ...config, style: value as PersonaConfig['style'] })}
                                    className={`p-3 rounded-lg border-2 text-left transition-all ${config.style === value
                                            ? 'border-indigo-500 bg-indigo-50'
                                            : 'border-slate-200 hover:border-slate-300'
                                        }`}
                                >
                                    <div className="font-bold text-slate-800">{label}</div>
                                    <div className="text-xs text-slate-500">{desc}</div>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* 三視角權重 */}
                    <div className="space-y-4">
                        <label className="text-sm font-bold text-slate-700 block">思考傾向調整</label>

                        <div className="space-y-3">
                            <div>
                                <div className="flex items-center justify-between mb-1">
                                    <span className="flex items-center gap-2 text-sm text-slate-600">
                                        <Lightbulb className="w-4 h-4 text-purple-500" />
                                        探索意義
                                    </span>
                                    <span className="text-sm font-mono text-purple-600">{config.weights.meaning}%</span>
                                </div>
                                <input
                                    type="range"
                                    min="0"
                                    max="100"
                                    value={config.weights.meaning}
                                    onChange={(e) => setConfig({
                                        ...config,
                                        weights: { ...config.weights, meaning: Number(e.target.value) }
                                    })}
                                    className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-purple-500"
                                />
                                <p className="text-xs text-slate-400 mt-1">較高：更多深度思考與價值探討</p>
                            </div>

                            <div>
                                <div className="flex items-center justify-between mb-1">
                                    <span className="flex items-center gap-2 text-sm text-slate-600">
                                        <Wrench className="w-4 h-4 text-blue-500" />
                                        實用導向
                                    </span>
                                    <span className="text-sm font-mono text-blue-600">{config.weights.practical}%</span>
                                </div>
                                <input
                                    type="range"
                                    min="0"
                                    max="100"
                                    value={config.weights.practical}
                                    onChange={(e) => setConfig({
                                        ...config,
                                        weights: { ...config.weights, practical: Number(e.target.value) }
                                    })}
                                    className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-500"
                                />
                                <p className="text-xs text-slate-400 mt-1">較高：更多可行性分析與步驟建議</p>
                            </div>

                            <div>
                                <div className="flex items-center justify-between mb-1">
                                    <span className="flex items-center gap-2 text-sm text-slate-600">
                                        <Shield className="w-4 h-4 text-amber-500" />
                                        安全考量
                                    </span>
                                    <span className="text-sm font-mono text-amber-600">{config.weights.safety}%</span>
                                </div>
                                <input
                                    type="range"
                                    min="0"
                                    max="100"
                                    value={config.weights.safety}
                                    onChange={(e) => setConfig({
                                        ...config,
                                        weights: { ...config.weights, safety: Number(e.target.value) }
                                    })}
                                    className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-amber-500"
                                />
                                <p className="text-xs text-slate-400 mt-1">較高：更多風險提醒與邊界考量</p>
                            </div>
                        </div>
                    </div>

                    {/* 風險敏感度 */}
                    <div>
                        <label className="text-sm font-bold text-slate-700 mb-3 block">風險提醒敏感度</label>
                        <div className="flex gap-2">
                            {[
                                { value: 'low', label: '低', color: 'bg-green-100 text-green-700 border-green-300' },
                                { value: 'medium', label: '中', color: 'bg-amber-100 text-amber-700 border-amber-300' },
                                { value: 'high', label: '高', color: 'bg-red-100 text-red-700 border-red-300' },
                            ].map(({ value, label, color }) => (
                                <button
                                    key={value}
                                    onClick={() => setConfig({ ...config, riskSensitivity: value as PersonaConfig['riskSensitivity'] })}
                                    className={`flex-1 py-2 px-4 rounded-lg border-2 font-bold transition-all ${config.riskSensitivity === value
                                            ? color
                                            : 'border-slate-200 text-slate-500 hover:border-slate-300'
                                        }`}
                                >
                                    {label}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* 回應長度 */}
                    <div>
                        <label className="text-sm font-bold text-slate-700 mb-3 block">回應長度偏好</label>
                        <div className="flex gap-2">
                            {[
                                { value: 'concise', label: '簡潔' },
                                { value: 'balanced', label: '適中' },
                                { value: 'detailed', label: '詳細' },
                            ].map(({ value, label }) => (
                                <button
                                    key={value}
                                    onClick={() => setConfig({ ...config, responseLength: value as PersonaConfig['responseLength'] })}
                                    className={`flex-1 py-2 px-4 rounded-lg border-2 font-bold transition-all ${config.responseLength === value
                                            ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                                            : 'border-slate-200 text-slate-500 hover:border-slate-300'
                                        }`}
                                >
                                    {label}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="p-6 border-t border-slate-100 flex justify-between sticky bottom-0 bg-white">
                    <button
                        onClick={handleReset}
                        className="flex items-center gap-2 px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                    >
                        <RotateCcw className="w-4 h-4" />
                        重設預設
                    </button>
                    <button
                        onClick={handleSave}
                        className="flex items-center gap-2 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-bold"
                    >
                        <Save className="w-4 h-4" />
                        儲存設定
                    </button>
                </div>
            </div>
        </div>
    );
}
