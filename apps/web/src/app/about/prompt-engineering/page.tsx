import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
    title: "提示工程 | ToneSoul Research",
    description:
        "語言治理協議 (LAP) 與張力控制的提示工程設計 — 超越生成，邁向認知治理",
};

const LAP_LAYERS = [
    {
        code: "L1",
        name: "本體層 (Ontological)",
        color: "text-indigo-300",
        borderColor: "border-indigo-500/20",
        bg: "bg-indigo-500/5",
        description: "將主張錨定在穩定事實、約束條件和可驗證的證據上。",
        example: "「根據 2024 年 NIST 報告...」而非「大家都知道...」",
    },
    {
        code: "L2",
        name: "推理層 (Reasoning Architecture)",
        color: "text-emerald-300",
        borderColor: "border-emerald-500/20",
        bg: "bg-emerald-500/5",
        description: "暴露審議結構 — 議會角色、約束、取捨。",
        example: "工程師提出可行性疑慮，守護者標記安全風險，最終綜合時保留分歧",
    },
    {
        code: "L3",
        name: "介面層 (Interface)",
        color: "text-amber-300",
        borderColor: "border-amber-500/20",
        bg: "bg-amber-500/5",
        description: "將修辭和隱喻與事實承諾分離。",
        example: "可以用比喻解釋，但必須附帶「這是類比，不是精確對應」",
    },
];

export default function PromptEngineeringPage() {
    return (
        <div className="space-y-12">
            {/* Header */}
            <section className="space-y-4">
                <div className="flex items-center gap-3">
                    <span className="text-4xl">⚡</span>
                    <div>
                        <h1 className="text-2xl font-bold">
                            提示工程 · Prompt Engineering
                        </h1>
                        <p className="text-gray-400">
                            超越生成，邁向認知治理
                        </p>
                    </div>
                </div>
            </section>

            {/* LAP Protocol */}
            <section className="rounded-xl border border-amber-500/20 bg-gradient-to-br from-amber-500/10 to-orange-500/5 p-8 space-y-4">
                <h2 className="text-xl font-bold text-amber-300">
                    語言治理協議 (Lingua-Animus Protocol)
                </h2>
                <p className="text-gray-300 leading-relaxed">
                    在 agent 時代，瓶頸不再只是模型能力。更難的問題是
                    <strong className="text-white">可追溯性</strong>
                    ：誰說了什麼，基於哪個推理，在什麼約束下。
                    LAP 是 ToneSoul 用來保持從事實到介面的可審計鏈的治理協議。
                </p>
            </section>

            {/* Three-Layer Decoupling */}
            <section className="space-y-6">
                <h2 className="text-xl font-bold">三層解耦 (TLD)</h2>
                <div className="space-y-4">
                    {LAP_LAYERS.map((layer) => (
                        <div
                            key={layer.code}
                            className={`rounded-lg border ${layer.borderColor} ${layer.bg} p-6 space-y-2`}
                        >
                            <div className="flex items-center gap-2">
                                <span className={`font-mono font-bold ${layer.color}`}>
                                    {layer.code}
                                </span>
                                <span className="font-semibold text-gray-200">
                                    {layer.name}
                                </span>
                            </div>
                            <p className="text-sm text-gray-300">{layer.description}</p>
                            <div className="rounded bg-black/20 p-3 text-xs text-gray-400">
                                <span className="text-gray-500">範例：</span> {layer.example}
                            </div>
                        </div>
                    ))}
                </div>
            </section>

            {/* Dynamic Tension Control */}
            <section className="space-y-6">
                <h2 className="text-xl font-bold">動態張力控制 (ΔT)</h2>
                <div className="grid gap-4 sm:grid-cols-2">
                    <div className="rounded-lg border border-teal-500/20 bg-teal-500/5 p-6 space-y-2">
                        <h3 className="font-semibold text-teal-300">🌊 共鳴模式</h3>
                        <p className="text-sm text-gray-300">降低張力</p>
                        <p className="text-xs text-gray-400">
                            適用於探索、構想、假說生成。允許更多創意空間，
                            減少審計嚴格度。
                        </p>
                    </div>
                    <div className="rounded-lg border border-rose-500/20 bg-rose-500/5 p-6 space-y-2">
                        <h3 className="font-semibold text-rose-300">⚡ 張力模式</h3>
                        <p className="text-sm text-gray-300">提升審計嚴格度</p>
                        <p className="text-xs text-gray-400">
                            適用於工程決策、安全評估、高風險場景。
                            每句話都需要證據支撐。
                        </p>
                    </div>
                </div>
            </section>

            {/* Occam Gate */}
            <section className="rounded-xl border border-white/5 bg-white/[0.02] p-8 space-y-4">
                <h2 className="text-xl font-bold">⚔️ 貨幣審計 + 奧卡姆閘門</h2>
                <p className="text-gray-300 leading-relaxed">
                    當偵測到詞彙膨脹 (lexical inflation) 或偽精確
                    (pseudo-precision) 時，LAP 觸發緊湊性審計：
                </p>
                <ul className="space-y-1 text-sm text-gray-400">
                    <li>• 剝除不可驗證的敘事碎片</li>
                    <li>• 只保留有證據、邏輯、或明確不確定性標籤的主張</li>
                    <li>• 計算「每句有效資訊密度」</li>
                </ul>
            </section>

            {/* Fine-tuning Philosophy */}
            <section className="space-y-6">
                <h2 className="text-xl font-bold">微調哲學</h2>
                <div className="rounded-lg border border-white/5 bg-white/[0.02] p-6 space-y-3">
                    <p className="text-gray-300 leading-relaxed">
                        ToneSoul 的立場：<strong className="text-white">不微調模型本身，而是微調約束層</strong>。
                    </p>
                    <p className="text-sm text-gray-400 leading-relaxed">
                        傳統微調改變模型的權重 — 這是脆弱的。ToneSoul
                        額外覆蓋一層治理協議：議會審議、張力閘門、承諾追蹤。
                        這些約束是可解釋的、可審計的、可回溯的，
                        比「在資料上多訓練幾個 epoch」更具有可問責性。
                    </p>
                    <div className="rounded bg-black/20 p-3 text-xs font-mono text-gray-500">
                        模型能力 × 治理約束 = 可信的 AI 行為
                    </div>
                </div>
            </section>

            {/* Practical Resources */}
            <section className="rounded-xl border border-white/5 bg-white/[0.02] p-8 space-y-4">
                <h2 className="text-xl font-bold">🔧 實用資源</h2>
                <div className="grid gap-3 sm:grid-cols-2 text-sm">
                    <a
                        href="https://github.com/Fan1234-1/tonesoul52"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="rounded-lg bg-white/5 p-4 transition hover:bg-white/10"
                    >
                        <div className="font-semibold text-gray-200">GitHub 原始碼</div>
                        <p className="mt-1 text-gray-500">
                            完整的 ToneSoul 實作與 849+ 測試
                        </p>
                    </a>
                    <Link
                        href="/"
                        className="rounded-lg bg-white/5 p-4 transition hover:bg-white/10"
                    >
                        <div className="font-semibold text-gray-200">ToneSoul Demo</div>
                        <p className="mt-1 text-gray-500">
                            線上互動示範 — 體驗議會審議流程
                        </p>
                    </Link>
                </div>
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
