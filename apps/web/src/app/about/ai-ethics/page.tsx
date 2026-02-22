import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
    title: "AI 倫理 | ToneSoul Research",
    description:
        "治理先行的 AI 架構設計 — ToneSoul 的 7D 審計框架與 AI 倫理研究",
};

const AUDIT_DIMENSIONS = [
    { code: "TDD", name: "測試驅動", question: "它能正確運作嗎？", icon: "✅" },
    { code: "RDD", name: "紅隊驅動", question: "它能被攻擊嗎？", icon: "🔴" },
    { code: "DDD", name: "數據驅動", question: "數據乾淨嗎？", icon: "📊" },
    { code: "XDD", name: "解釋驅動", question: "推理透明嗎？", icon: "🔍" },
    { code: "GDD", name: "治理驅動", question: "誰有權限？", icon: "🏛️" },
    { code: "CDD", name: "一致驅動", question: "立場一致嗎？", icon: "🎯" },
    { code: "SDH", name: "系統健康", question: "系統穩定嗎？", icon: "💚" },
];

export default function AIEthicsPage() {
    return (
        <div className="space-y-12">
            {/* Header */}
            <section className="space-y-4">
                <div className="flex items-center gap-3">
                    <span className="text-4xl">⚖️</span>
                    <div>
                        <h1 className="text-2xl font-bold">AI 倫理 · AI Ethics</h1>
                        <p className="text-gray-400">治理先行的 AI 架構設計</p>
                    </div>
                </div>
            </section>

            {/* Core thesis */}
            <section className="rounded-xl border border-indigo-500/20 bg-gradient-to-br from-indigo-500/10 to-violet-500/5 p-8 space-y-4">
                <h2 className="text-xl font-bold text-indigo-300">核心命題</h2>
                <blockquote className="border-l-2 border-indigo-500/50 pl-4 text-gray-300 italic">
                    「多數 AI 系統優化的是『聽起來正確』。ToneSoul 優化的是
                    『對自己不知道的事保持誠實』。」
                </blockquote>
                <p className="text-gray-300 leading-relaxed">
                    傳統 AI 面臨一個不可能的抉擇：誠實就完不成任務，完成任務就要犧牲真相。
                    ToneSoul 的解法是
                    <strong className="text-white">承諾更新協議 (Commitment Update Protocol)</strong>
                    — 當過去的承諾與現在的事實衝突時，系統會明確說明衝突、
                    解釋為何舊承諾不再成立、並等待使用者確認。
                </p>
            </section>

            {/* 7D Audit */}
            <section className="space-y-6">
                <h2 className="text-xl font-bold">🛡️ 七維審計框架 (7D Audit)</h2>
                <p className="text-gray-400">
                    每個維度回答一個關於 AI 系統可信度的根本問題：
                </p>
                <div className="grid gap-3 sm:grid-cols-2">
                    {AUDIT_DIMENSIONS.map((dim) => (
                        <div
                            key={dim.code}
                            className="rounded-lg border border-white/5 bg-white/[0.02] p-4 transition hover:bg-white/[0.04]"
                        >
                            <div className="flex items-center gap-2">
                                <span>{dim.icon}</span>
                                <span className="font-mono text-sm font-bold text-gray-300">
                                    {dim.code}
                                </span>
                                <span className="text-sm text-gray-500">{dim.name}</span>
                            </div>
                            <p className="mt-2 text-sm text-gray-400">{dim.question}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* Governance Principles */}
            <section className="space-y-6">
                <h2 className="text-xl font-bold">治理原則</h2>
                <div className="space-y-4">
                    <div className="rounded-lg border border-white/5 bg-white/[0.02] p-6">
                        <h3 className="font-semibold text-amber-300">
                            🔍 可驗證性 (Verifiability)
                        </h3>
                        <p className="mt-2 text-sm text-gray-300 leading-relaxed">
                            每一個輸出都可以被審計。ToneSoul 的議會系統
                            (Philosopher/Engineer/Guardian)
                            從三個視角審議每個回應，投票結果和推理過程全部記錄在案。
                        </p>
                    </div>
                    <div className="rounded-lg border border-white/5 bg-white/[0.02] p-6">
                        <h3 className="font-semibold text-emerald-300">
                            ⚖️ 可問責性 (Accountability)
                        </h3>
                        <p className="mt-2 text-sm text-gray-300 leading-relaxed">
                            決策可追溯到原因。Isnad 溯源鏈記錄每個決定的來源，
                            Genesis 追蹤器標記每一條資訊的起源和責任歸屬。
                        </p>
                    </div>
                    <div className="rounded-lg border border-white/5 bg-white/[0.02] p-6">
                        <h3 className="font-semibold text-indigo-300">
                            🎚️ 可校準性 (Calibratability)
                        </h3>
                        <p className="mt-2 text-sm text-gray-300 leading-relaxed">
                            不確定性是顯式的，而不是被隱藏的。責任分級系統明確標記
                            AI 的確信程度，讓使用者知道何時該額外求證。
                        </p>
                    </div>
                </div>
            </section>

            {/* Academic References */}
            <section className="rounded-xl border border-white/5 bg-white/[0.02] p-8 space-y-4">
                <h2 className="text-xl font-bold">📚 相關研究</h2>
                <ul className="space-y-2 text-sm text-gray-400">
                    <li>
                        • EU AI Act — 歐盟人工智慧法案的風險分級框架
                    </li>
                    <li>
                        • NIST AI Risk Management Framework — 美國標準的 AI 風險管理
                    </li>
                    <li>
                        • Mixture-of-Agents — 多代理協作的增益與限制
                    </li>
                    <li>
                        • Threat-Model-Based Red Teaming — 系統化紅隊攻防框架
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
