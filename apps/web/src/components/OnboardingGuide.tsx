"use client";

import { useState } from "react";
import { Key, ArrowRight, ExternalLink, Shield, Info } from "lucide-react";

interface OnboardingGuideProps {
    isOpen: boolean;
    onComplete: () => void;
    onOpenSettings: () => void;
}

const ONBOARDING_KEY = 'tonesoul_onboarded';

export function hasCompletedOnboarding(): boolean {
    if (typeof window === 'undefined') return true;
    return localStorage.getItem(ONBOARDING_KEY) === 'true';
}

export function markOnboardingComplete(): void {
    localStorage.setItem(ONBOARDING_KEY, 'true');
}

export default function OnboardingGuide({ isOpen, onComplete, onOpenSettings }: OnboardingGuideProps) {
    const [step, setStep] = useState(1);

    if (!isOpen) return null;

    const handleGetStarted = () => {
        markOnboardingComplete();
        onComplete();
        onOpenSettings();
    };

    const handleSkip = () => {
        markOnboardingComplete();
        onComplete();
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/80 backdrop-blur-sm">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden">
                {/* Progress */}
                <div className="h-1 bg-slate-200">
                    <div
                        className="h-full bg-indigo-600 transition-all duration-300"
                        style={{ width: `${(step / 2) * 100}%` }}
                    />
                </div>

                {step === 1 && (
                    <div className="p-8 text-center">
                        <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-6">
                            <Shield className="w-8 h-8 text-indigo-600" />
                        </div>
                        <h2 className="text-2xl font-bold text-slate-800 mb-4">
                            歡迎使用 ToneSoul
                        </h2>
                        <p className="text-slate-600 mb-6">
                            ToneSoul 是一個<strong>本地優先</strong>的 AI 治理系統。
                            <br />
                            你的對話和設定都存在你自己的瀏覽器中，不會傳到我們的伺服器。
                        </p>
                        <div className="bg-slate-50 rounded-lg p-4 text-left text-sm text-slate-600 mb-6">
                            <div className="flex items-start gap-2">
                                <Info className="w-4 h-4 text-slate-400 mt-0.5" />
                                <div>
                                    <strong>隱私保證：</strong>
                                    <ul className="mt-1 space-y-1 text-slate-500">
                                        <li>• API Key 只存在你的瀏覽器</li>
                                        <li>• 對話直接傳到 Gemini/OpenAI，不經過我們</li>
                                        <li>• 所有數據存在 IndexedDB（本地）</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        <button type="button"
                            onClick={() => setStep(2)}
                            className="w-full py-3 bg-indigo-600 text-white rounded-lg font-bold hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2"
                        >
                            了解 <ArrowRight className="w-4 h-4" />
                        </button>
                    </div>
                )}

                {step === 2 && (
                    <div className="p-8 text-center">
                        <div className="w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-6">
                            <Key className="w-8 h-8 text-amber-600" />
                        </div>
                        <h2 className="text-2xl font-bold text-slate-800 mb-4">
                            設定你的 API Key
                        </h2>
                        <p className="text-slate-600 mb-6">
                            ToneSoul 需要你自己的 API Key 來運作。
                            <br />
                            推薦使用 <strong>Google Gemini</strong>（免費額度足夠個人使用）。
                        </p>
                        <a
                            href="https://aistudio.google.com/app/apikey"
                            target="_blank"
                            rel="noopener"
                            className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-800 mb-6"
                        >
                            取得 Gemini API Key <ExternalLink className="w-4 h-4" />
                        </a>
                        <div className="space-y-3">
                            <button type="button"
                                onClick={handleGetStarted}
                                className="w-full py-3 bg-indigo-600 text-white rounded-lg font-bold hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2"
                            >
                                <Key className="w-4 h-4" /> 前往設定 API Key
                            </button>
                            <button type="button"
                                onClick={handleSkip}
                                className="w-full py-2 text-slate-500 hover:text-slate-700 text-sm"
                            >
                                稍後再設定
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

