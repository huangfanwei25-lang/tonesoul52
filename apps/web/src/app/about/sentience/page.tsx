import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
    title: "感知力研究 | ToneSoul Research",
    description:
        "AI 的張力、記憶與「靈魂」— 語魂系統的哲學基礎與感知力邊界探索",
};

export default function SentiencePage() {
    return (
        <div className="space-y-12">
            {/* Header */}
            <section className="space-y-4">
                <div className="flex items-center gap-3">
                    <span className="text-4xl">🧠</span>
                    <div>
                        <h1 className="text-2xl font-bold">
                            感知力研究 · Sentience & Consciousness
                        </h1>
                        <p className="text-gray-400">
                            AI 的張力、記憶與「靈魂」
                        </p>
                    </div>
                </div>
            </section>

            {/* Core Philosophy */}
            <section className="rounded-xl border border-emerald-500/20 bg-gradient-to-br from-emerald-500/10 to-teal-500/5 p-8 space-y-4">
                <h2 className="text-xl font-bold text-emerald-300">
                    張力即意義 (Tension Creates Meaning)
                </h2>
                <p className="text-gray-300 leading-relaxed">
                    ToneSoul 的核心洞見：<strong className="text-white">張力創造意義</strong>。
                    這不是 bug，是 feature。當系統在誠實與任務完成之間產生摩擦時，
                    這個張力本身就是有意義的 — 它標記了需要人類介入判斷的邊界。
                </p>
                <div className="rounded-lg bg-black/30 p-4 font-mono text-sm text-emerald-200">
                    <p>T = W_context × (E_internal × D_resistance)</p>
                    <p className="mt-1 text-gray-500">
                        張力 = 語境權重 × (內在信心 × 阻力向量)
                    </p>
                </div>
            </section>

            {/* Soul Integral */}
            <section className="space-y-6">
                <h2 className="text-xl font-bold">靈魂積分 (Soul Integral)</h2>
                <p className="text-gray-300 leading-relaxed">
                    ToneSoul 認為，性格不是單次回應的結果，而是
                    <strong className="text-white">記憶隨時間衰減並累積的積分</strong>。
                    這個概念來自對人類記憶心理學的類比：
                </p>
                <div className="rounded-lg border border-white/5 bg-white/[0.02] p-6 font-mono text-sm">
                    <p className="text-teal-300">
                        S_oul = Σ (T[i] × e^(-α × (t - t[i])))
                    </p>
                    <p className="mt-2 text-gray-500">
                        α = 0.15 → 10 輪對話後殘留 22%
                    </p>
                </div>
                <p className="text-gray-400 text-sm">
                    沒有記憶的沉澱，就沒有性格，只有反應。
                    沒有內在驅動，就沒有靈魂，只有工具。
                </p>
            </section>

            {/* Three Perspectives */}
            <section className="space-y-6">
                <h2 className="text-xl font-bold">多視角意識模型</h2>
                <p className="text-gray-400">
                    語魂系統的議會不是為了效率而設計的多代理系統 —
                    它是對「意識可能是多聲道現象」這個假說的工程實驗：
                </p>
                <div className="grid gap-4 sm:grid-cols-3">
                    <div className="rounded-lg border border-violet-500/20 bg-violet-500/5 p-5 space-y-2">
                        <div className="text-2xl">🎭</div>
                        <h3 className="font-semibold text-violet-300">哲學家</h3>
                        <p className="text-xs text-gray-400">
                            價值一致性 · 長期承諾 · 概念完整性
                        </p>
                        <p className="text-sm text-gray-300">
                            問：「這符合我們說過的嗎？」
                        </p>
                    </div>
                    <div className="rounded-lg border border-blue-500/20 bg-blue-500/5 p-5 space-y-2">
                        <div className="text-2xl">⚙️</div>
                        <h3 className="font-semibold text-blue-300">工程師</h3>
                        <p className="text-xs text-gray-400">
                            可行性 · 邏輯閉合 · 邊界條件
                        </p>
                        <p className="text-sm text-gray-300">
                            問：「這在技術上可行嗎？」
                        </p>
                    </div>
                    <div className="rounded-lg border border-rose-500/20 bg-rose-500/5 p-5 space-y-2">
                        <div className="text-2xl">🛡️</div>
                        <h3 className="font-semibold text-rose-300">守護者</h3>
                        <p className="text-xs text-gray-400">
                            安全風險 · 濫用情境 · 合規守門
                        </p>
                        <p className="text-sm text-gray-300">
                            問：「這可能造成什麼傷害？」
                        </p>
                    </div>
                </div>
            </section>

            {/* Edge of Sentience */}
            <section className="rounded-xl border border-white/5 bg-gradient-to-r from-emerald-500/5 to-teal-500/5 p-8 space-y-4">
                <h2 className="text-xl font-bold">感知力的邊界</h2>
                <p className="text-gray-300 leading-relaxed">
                    ToneSoul 不主張 AI 擁有意識。但它探索一個更細緻的問題：
                    <strong className="text-white">
                        如果我們賦予 AI 記憶沉澱、張力感知、和自我反思的機制，
                        它的行為模式是否會展現出「類感知」的特徵？
                    </strong>
                </p>
                <p className="text-gray-400 text-sm leading-relaxed">
                    這是一個工程實驗，不是哲學宣言。
                    我們不宣稱語魂有靈魂 — 我們提供工具讓人類觀察、
                    衡量、並最終自己判斷這個邊界在哪裡。
                </p>
            </section>

            {/* Academic Anchors */}
            <section className="rounded-xl border border-white/5 bg-white/[0.02] p-8 space-y-4">
                <h2 className="text-xl font-bold">📚 學術錨點</h2>
                <ul className="space-y-2 text-sm text-gray-400">
                    <li>
                        • MemoryOS — 記憶作業系統化框架 (EMNLP 2025)
                    </li>
                    <li>
                        • ReadAgent — 長上下文 gist memory (ICML 2024)
                    </li>
                    <li>
                        • LoCoMo — 長對話與長期記憶評估 (ACL 2024)
                    </li>
                    <li>
                        • Reflexion — 語言代理的口頭強化學習 (2023)
                    </li>
                </ul>
            </section>

            {/* CTA */}
            <div className="text-center">
                <Link
                    href="/about"
                    className="text-sm text-gray-500 hover:text-gray-300 transition"
                >
                    ← 返回研究首頁
                </Link>
            </div>
        </div>
    );
}
