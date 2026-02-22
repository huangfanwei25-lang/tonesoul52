import Link from "next/link";

const RESEARCH_CARDS = [
    {
        href: "/about/ai-ethics",
        icon: "⚖️",
        title: "AI 倫理",
        subtitle: "AI Ethics & Governance",
        description: "治理先行的 AI 架構設計 — 把問責放在能力之前",
        gradient: "from-indigo-500/20 to-violet-500/20",
        border: "border-indigo-500/30",
    },
    {
        href: "/about/sentience",
        icon: "🧠",
        title: "感知力研究",
        subtitle: "Sentience & Consciousness",
        description: "AI 的張力、記憶與「靈魂」— 語魂系統的哲學基礎",
        gradient: "from-emerald-500/20 to-teal-500/20",
        border: "border-emerald-500/30",
    },
    {
        href: "/about/prompt-engineering",
        icon: "⚡",
        title: "提示工程",
        subtitle: "Prompt Engineering & Fine-tuning",
        description: "語言治理協議 (LAP) 與張力控制的提示設計",
        gradient: "from-amber-500/20 to-orange-500/20",
        border: "border-amber-500/30",
    },
];

export default function AboutPage() {
    return (
        <div className="space-y-16">
            {/* Hero */}
            <section className="space-y-6 text-center">
                <div className="mx-auto h-24 w-24 rounded-full bg-gradient-to-br from-indigo-500/30 to-violet-500/30 flex items-center justify-center text-4xl border border-indigo-500/20">
                    🌌
                </div>
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">黃梵威</h1>
                    <p className="mt-1 text-lg text-gray-400">Fan-Wei Huang</p>
                </div>
                <p className="mx-auto max-w-2xl text-gray-300 leading-relaxed">
                    獨立研究者 · ToneSoul 語魂系統創建者
                    <br />
                    <span className="text-gray-400">
                        探索 AI 治理、感知力邊界、以及如何讓機器學會說「我不知道」。
                    </span>
                </p>
                <div className="flex items-center justify-center gap-4">
                    <a
                        href="https://github.com/Fan1234-1/tonesoul52"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="rounded-lg bg-white/5 px-4 py-2 text-sm text-gray-300 transition hover:bg-white/10"
                    >
                        GitHub →
                    </a>
                    <Link
                        href="/"
                        className="rounded-lg bg-indigo-500/20 px-4 py-2 text-sm text-indigo-300 transition hover:bg-indigo-500/30"
                    >
                        ToneSoul Demo →
                    </Link>
                </div>
            </section>

            {/* Research Areas */}
            <section className="space-y-6">
                <h2 className="text-center text-sm font-semibold uppercase tracking-widest text-gray-500">
                    研究方向
                </h2>
                <div className="grid gap-4 sm:grid-cols-3">
                    {RESEARCH_CARDS.map((card) => (
                        <Link
                            key={card.href}
                            href={card.href}
                            className={`group rounded-xl border ${card.border} bg-gradient-to-br ${card.gradient} p-6 transition-all duration-300 hover:scale-[1.02] hover:shadow-xl hover:shadow-black/20`}
                        >
                            <div className="text-3xl">{card.icon}</div>
                            <h3 className="mt-3 text-lg font-semibold">{card.title}</h3>
                            <p className="mt-0.5 text-xs text-gray-400">{card.subtitle}</p>
                            <p className="mt-3 text-sm leading-relaxed text-gray-300">
                                {card.description}
                            </p>
                            <span className="mt-4 inline-block text-xs text-gray-500 transition group-hover:text-gray-300">
                                閱讀更多 →
                            </span>
                        </Link>
                    ))}
                </div>
            </section>

            {/* ToneSoul Section */}
            <section className="rounded-xl border border-white/5 bg-white/[0.02] p-8 space-y-4">
                <h2 className="text-xl font-bold">🎯 ToneSoul 語魂系統</h2>
                <p className="text-gray-300 leading-relaxed">
                    ToneSoul 不是另一個 AI wrapper。它是一套
                    <strong className="text-white">治理先行的架構</strong>
                    ，讓 AI 系統的每一個決策都可追溯、可審計、可問責。
                </p>
                <div className="grid gap-3 sm:grid-cols-3 text-sm">
                    <div className="rounded-lg bg-white/5 p-4">
                        <div className="font-semibold text-indigo-300">🔍 可驗證</div>
                        <p className="mt-1 text-gray-400">
                            多視角議會投票 + 結構化輸出
                        </p>
                    </div>
                    <div className="rounded-lg bg-white/5 p-4">
                        <div className="font-semibold text-emerald-300">⚖️ 可問責</div>
                        <p className="mt-1 text-gray-400">
                            Isnad 溯源鏈 + Genesis 追蹤
                        </p>
                    </div>
                    <div className="rounded-lg bg-white/5 p-4">
                        <div className="font-semibold text-amber-300">🎚️ 可校準</div>
                        <p className="mt-1 text-gray-400">
                            責任分級 + 不確定性揭露
                        </p>
                    </div>
                </div>
                <div className="pt-2">
                    <Link
                        href="/"
                        className="text-sm text-indigo-400 hover:text-indigo-300 transition"
                    >
                        前往 ToneSoul Demo →
                    </Link>
                </div>
            </section>

            {/* Philosophy Quote */}
            <section className="rounded-xl border border-white/5 bg-gradient-to-r from-violet-500/5 to-indigo-500/5 p-8 text-center">
                <blockquote className="text-lg italic text-gray-300">
                    「沒有記憶的沉澱（積分），就沒有性格，只有反應。
                    <br />
                    沒有內在驅動（主動性），就沒有靈魂，只有工具。」
                </blockquote>
                <cite className="mt-4 block text-sm text-gray-500">
                    — ToneSoul 哲學白皮書
                </cite>
            </section>
        </div>
    );
}
