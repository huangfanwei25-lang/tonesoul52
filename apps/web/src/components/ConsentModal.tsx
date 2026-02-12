"use client";

import { Shield, Check, X } from "lucide-react";

interface ConsentModalProps {
    onAccept: (consentType: string) => void;
    onDecline: () => void;
}

export default function ConsentModal({ onAccept, onDecline }: ConsentModalProps) {
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 transition-all duration-300 bg-slate-900/60 backdrop-blur-sm">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg transform transition-all duration-500 scale-100 opacity-100">

                {/* Header */}
                <div className="p-6 border-b border-slate-100 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-t-2xl">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-white/20 rounded-xl">
                            <Shield className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold text-white">使用前須知</h2>
                            <p className="text-indigo-100 text-sm">Privacy & Consent</p>
                        </div>
                    </div>
                </div>

                {/* Content */}
                <div className="p-6 space-y-4">
                    <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                        <h3 className="font-semibold text-slate-800 mb-2">📊 我們收集什麼？</h3>
                        <ul className="text-sm text-slate-600 space-y-1">
                            <li>• 對話內容（用於改進 AI）</li>
                            <li>• 匿名 Session ID</li>
                            <li>• 時間戳記</li>
                        </ul>
                    </div>

                    <div className="bg-emerald-50 rounded-xl p-4 border border-emerald-200">
                        <h3 className="font-semibold text-emerald-800 mb-2">🔒 我們不收集</h3>
                        <ul className="text-sm text-emerald-700 space-y-1">
                            <li>• 真實姓名或電子郵件</li>
                            <li>• IP 地址（僅保留雜湊）</li>
                            <li>• 地理位置或設備識別碼</li>
                        </ul>
                    </div>

                    <div className="bg-amber-50 rounded-xl p-4 border border-amber-200">
                        <h3 className="font-semibold text-amber-800 mb-2">⚖️ 你的權利</h3>
                        <p className="text-sm text-amber-700">
                            你可以隨時撤回同意並刪除所有資料。詳見
                            <a href="/privacy" className="underline hover:text-amber-900"> 隱私政策</a>。
                        </p>
                    </div>
                </div>

                {/* Footer */}
                <div className="p-6 border-t border-slate-100 flex gap-3">
                    <button type="button"
                        onClick={onDecline}
                        className="flex-1 px-4 py-3 rounded-xl border border-slate-300 text-slate-600 font-medium hover:bg-slate-50 transition-colors flex items-center justify-center gap-2"
                    >
                        <X className="w-4 h-4" />
                        拒絕
                    </button>
                    <button type="button"
                        onClick={() => onAccept("research")}
                        className="flex-1 px-4 py-3 rounded-xl bg-indigo-600 text-white font-medium hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2 shadow-lg shadow-indigo-200"
                    >
                        <Check className="w-4 h-4" />
                        同意並繼續
                    </button>
                </div>
            </div>
        </div>
    );
}

