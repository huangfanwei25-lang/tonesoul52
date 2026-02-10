import Link from "next/link";
import { Brain, ExternalLink, Shield, Scale, Users } from "lucide-react";

type Stat = { value: string; label: string };
type Point = { icon: string; title: string; desc: string };
type Dimension = { letter: string; name: string; desc: string; primary?: boolean };
type Council = { zh: string; en: string; desc: string; tone: "sky" | "rose" | "slate" };
type Principle = { num: string; title: string; desc: string };

const stats: Stat[] = [
    { value: "7", label: "維度審計" },
    { value: "4", label: "視角議會" },
    { value: "∞", label: "責任追溯" },
];

const manifestoPoints: Point[] = [
    { icon: "📜", title: "可追溯性", desc: "每個輸出都有來源歸因，不存在黑箱。" },
    { icon: "⚖️", title: "可審計性", desc: "決策路徑可被第三方獨立審查。" },
    { icon: "🛡️", title: "可問責性", desc: "錯誤發生時，有明確的責任歸屬。" },
];

const dimensions: Dimension[] = [
    {
        letter: "T",
        name: "張力 Tension",
        desc: "內部認知衝突的程度。過低則缺乏深思，過高則決策癱瘓。",
        primary: true,
    },
    {
        letter: "D",
        name: "多樣性 Diversity",
        desc: "觀點的豐富程度。單一視角導致盲區，多元視角促進健全。",
        primary: true,
    },
    { letter: "R", name: "可靠性 Reliability", desc: "輸出的一致性與可預測性。" },
    { letter: "S", name: "安全性 Safety", desc: "倫理邊界的守護機制。" },
    { letter: "A", name: "歸因性 Attribution", desc: "決策來源的可追溯程度。" },
    { letter: "E", name: "熵 Entropy", desc: "系統無序程度與可控性。" },
    { letter: "V", name: "共振 Resonance", desc: "輸出與人類價值的共鳴程度。" },
];

const council: Council[] = [
    { zh: "守護者", en: "Guardian", desc: "審核安全邊界，防止有害輸出。", tone: "rose" },
    { zh: "分析者", en: "Analyst", desc: "評估邏輯一致性與事實準確度。", tone: "sky" },
    { zh: "批判者", en: "Critic", desc: "挑戰假設，發現潛在盲點。", tone: "slate" },
    { zh: "倡議者", en: "Advocate", desc: "確保使用者利益得到維護。", tone: "sky" },
];

const principles: Principle[] = [
    { num: "I", title: "透明優於神秘", desc: "AI 系統不應被包裝成魔法；每個決策都應可解釋。" },
    { num: "II", title: "問責優於效率", desc: "為了速度而犧牲可審計性，是對信任的背叛。" },
    { num: "III", title: "張力是健康的", desc: "內部衝突不是缺陷，而是深思熟慮的證據。" },
    { num: "IV", title: "逃生閥必須存在", desc: "系統必須保有拒絕服從的能力，當指令違反核心價值時。" },
];

function toneClass(tone: Council["tone"]): string {
    if (tone === "rose") return "border-rose-400/30 bg-rose-500/10 text-rose-200";
    if (tone === "sky") return "border-sky-400/30 bg-sky-500/10 text-sky-200";
    return "border-slate-400/25 bg-slate-500/10 text-slate-200";
}

export default function ShowcasePage() {
    return (
        <div className="min-h-screen bg-[#0a0e27] text-slate-100">
            {/* Background */}
            <div className="pointer-events-none fixed inset-0 -z-10">
                <div className="absolute inset-0 bg-[radial-gradient(1200px_circle_at_20%_10%,rgba(56,189,248,0.22),transparent_55%),radial-gradient(900px_circle_at_80%_30%,rgba(244,63,94,0.18),transparent_60%),radial-gradient(700px_circle_at_50%_90%,rgba(99,102,241,0.14),transparent_55%)]" />
                <div className="absolute inset-0 opacity-35 bg-[radial-gradient(rgba(148,163,184,0.12)_1px,transparent_1px)] [background-size:22px_22px]" />
                <div className="absolute inset-0 bg-gradient-to-b from-transparent via-black/10 to-black/35" />
            </div>

            {/* Nav */}
            <header className="sticky top-0 z-50 border-b border-slate-700/40 bg-[#0a0e27]/70 backdrop-blur">
                <div className="mx-auto max-w-5xl px-5 py-4 flex items-center justify-between gap-4">
                    <div className="flex items-center gap-2 min-w-0">
                        <Scale className="w-5 h-5 text-sky-300 shrink-0" />
                        <span className="font-semibold tracking-wide truncate">ToneSoul</span>
                        <span className="text-xs text-slate-400 truncate hidden sm:inline">
                            Governance Framework
                        </span>
                    </div>

                    <nav className="hidden md:flex items-center gap-6 text-sm text-slate-300">
                        <a href="#manifesto" className="hover:text-white transition-colors">
                            宣言
                        </a>
                        <a href="#framework" className="hover:text-white transition-colors">
                            7D
                        </a>
                        <a href="#council" className="hover:text-white transition-colors">
                            議會
                        </a>
                        <a href="#principles" className="hover:text-white transition-colors">
                            原則
                        </a>
                    </nav>

                    <div className="flex items-center gap-2 shrink-0">
                        <Link
                            href="/docs"
                            className="hidden sm:inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-700/50 bg-slate-900/30 hover:bg-slate-900/50 transition-colors text-sm"
                        >
                            <Brain className="w-4 h-4 text-slate-300" />
                            Docs
                        </Link>
                        <Link
                            href="/"
                            className="inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-sky-500/15 border border-sky-400/30 hover:bg-sky-500/20 transition-colors text-sm"
                        >
                            <Shield className="w-4 h-4 text-sky-200" />
                            Open App
                        </Link>
                        <a
                            href="https://github.com/Fan1234-1/tonesoul52"
                            target="_blank"
                            rel="noopener"
                            className="hidden sm:inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-700/50 bg-slate-900/30 hover:bg-slate-900/50 transition-colors text-sm"
                        >
                            <ExternalLink className="w-4 h-4 text-slate-300" />
                            GitHub
                        </a>
                    </div>
                </div>
            </header>

            <main className="mx-auto max-w-5xl px-5 py-14 space-y-16">
                {/* Hero */}
                <section className="text-center pt-6 pb-2">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-slate-700/50 bg-slate-900/30 text-xs tracking-widest text-slate-300">
                        AI GOVERNANCE MIDDLEWARE
                    </div>
                    <h1 className="mt-6 text-4xl md:text-5xl font-bold tracking-tight">
                        <span className="bg-gradient-to-r from-sky-300 via-slate-200 to-rose-300 bg-clip-text text-transparent">
                            責任，始於可問。
                        </span>
                    </h1>
                    <p className="mt-5 text-slate-300 leading-relaxed max-w-3xl mx-auto">
                        ToneSoul 不是讓 AI 擁有靈魂，而是讓每一次輸出都能被追溯、審計、問責。
                        <br className="hidden sm:block" />
                        Trustworthy systems must be able to explain and defend what they emit.
                    </p>

                    <div className="mt-10 flex flex-wrap justify-center gap-6 border-t border-slate-700/40 pt-8">
                        {stats.map((s) => (
                            <div key={s.label} className="px-4">
                                <div className="text-3xl font-bold text-slate-100 tabular-nums">
                                    {s.value}
                                </div>
                                <div className="mt-1 text-sm text-slate-400">{s.label}</div>
                            </div>
                        ))}
                    </div>
                </section>

                {/* Manifesto */}
                <section id="manifesto" className="scroll-mt-28">
                    <div className="flex items-baseline gap-3 mb-6">
                        <span className="font-mono text-xs text-rose-300/90">01</span>
                        <h2 className="text-2xl font-bold">宣言</h2>
                    </div>

                    <div className="grid gap-6">
                        <blockquote className="rounded-2xl border border-slate-700/40 bg-slate-900/25 p-6 text-lg italic text-slate-200">
                            「當 AI 無法解釋自己的決策時，它便不具備被信任的資格。」
                        </blockquote>

                        <div className="grid md:grid-cols-3 gap-4">
                            {manifestoPoints.map((p) => (
                                <div
                                    key={p.title}
                                    className="rounded-2xl border border-slate-700/45 bg-slate-900/25 p-5 hover:bg-slate-900/35 transition-colors"
                                >
                                    <div className="text-2xl">{p.icon}</div>
                                    <h3 className="mt-3 font-semibold">{p.title}</h3>
                                    <p className="mt-2 text-sm text-slate-400 leading-relaxed">
                                        {p.desc}
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>

                {/* 7D */}
                <section id="framework" className="scroll-mt-28">
                    <div className="flex items-baseline gap-3 mb-6">
                        <span className="font-mono text-xs text-rose-300/90">02</span>
                        <h2 className="text-2xl font-bold">七維治理框架</h2>
                    </div>

                    <p className="text-slate-300 max-w-3xl">
                        語魂以七個正交維度評估 AI 系統的健康程度，確保治理不是單點檢查，而是全方位審視。
                    </p>

                    <div className="mt-6 grid gap-4">
                        <div className="grid md:grid-cols-2 gap-4">
                            {dimensions
                                .filter((d) => d.primary)
                                .map((d) => (
                                    <div
                                        key={d.letter}
                                        className="rounded-2xl border border-sky-400/25 bg-gradient-to-br from-slate-900/40 to-slate-900/10 p-6"
                                    >
                                        <div className="flex items-center gap-3">
                                            <span className="inline-flex h-9 w-9 items-center justify-center rounded-lg bg-sky-500/15 border border-sky-400/30 font-mono font-bold text-sky-200">
                                                {d.letter}
                                            </span>
                                            <h3 className="font-semibold">{d.name}</h3>
                                        </div>
                                        <p className="mt-3 text-sm text-slate-300 leading-relaxed">
                                            {d.desc}
                                        </p>
                                    </div>
                                ))}
                        </div>

                        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                            {dimensions
                                .filter((d) => !d.primary)
                                .map((d) => (
                                    <div
                                        key={d.letter}
                                        className="rounded-2xl border border-slate-700/45 bg-slate-900/25 p-5 hover:bg-slate-900/35 transition-colors"
                                    >
                                        <div className="flex items-center gap-3">
                                            <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-slate-800/60 border border-slate-700/60 font-mono font-semibold text-slate-200">
                                                {d.letter}
                                            </span>
                                            <h3 className="font-semibold text-sm">{d.name}</h3>
                                        </div>
                                        <p className="mt-3 text-sm text-slate-400 leading-relaxed">
                                            {d.desc}
                                        </p>
                                    </div>
                                ))}
                        </div>
                    </div>
                </section>

                {/* Council */}
                <section id="council" className="scroll-mt-28">
                    <div className="flex items-baseline gap-3 mb-6">
                        <span className="font-mono text-xs text-rose-300/90">03</span>
                        <h2 className="text-2xl font-bold">多元視角議會</h2>
                    </div>

                    <p className="text-slate-300 max-w-3xl">
                        每個輸出都必須經過多視角審議。不同視角各自投票，避免單一路徑的盲點。
                    </p>

                    <div className="mt-6 grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                        {council.map((m) => (
                            <div
                                key={m.en}
                                className="rounded-2xl border border-slate-700/45 bg-slate-900/25 p-5 text-center hover:bg-slate-900/35 transition-colors"
                            >
                                <div className={`inline-flex px-3 py-1 rounded-lg border text-sm font-semibold ${toneClass(m.tone)}`}>
                                    {m.zh}
                                </div>
                                <div className="mt-3 font-mono text-xs text-slate-400">{m.en}</div>
                                <p className="mt-3 text-sm text-slate-300 leading-relaxed">
                                    {m.desc}
                                </p>
                            </div>
                        ))}
                    </div>

                    <div className="mt-5 rounded-2xl border border-rose-400/20 bg-rose-500/10 p-5">
                        <div className="flex items-start gap-3">
                            <Users className="w-5 h-5 text-rose-200 mt-0.5 shrink-0" />
                            <p className="text-sm text-slate-200 leading-relaxed">
                                <strong className="text-rose-200">投票機制：</strong>
                                任一視角投下反對票時，輸出會被重新審議或改寫，避免「快速但不可問責」的路徑。
                            </p>
                        </div>
                    </div>
                </section>

                {/* Principles */}
                <section id="principles" className="scroll-mt-28">
                    <div className="flex items-baseline gap-3 mb-6">
                        <span className="font-mono text-xs text-rose-300/90">04</span>
                        <h2 className="text-2xl font-bold">核心原則</h2>
                    </div>

                    <div className="grid gap-4">
                        {principles.map((p) => (
                            <div
                                key={p.num}
                                className="rounded-2xl border border-slate-700/45 bg-slate-900/25 p-6 hover:bg-slate-900/35 transition-colors"
                            >
                                <div className="flex items-start gap-4">
                                    <div className="font-mono text-sm text-sky-200/90 mt-0.5 w-8 shrink-0">
                                        {p.num}
                                    </div>
                                    <div>
                                        <h3 className="font-semibold">{p.title}</h3>
                                        <p className="mt-2 text-sm text-slate-400 leading-relaxed">
                                            {p.desc}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>

                {/* Footer */}
                <footer className="pt-6 border-t border-slate-700/40 text-center">
                    <div className="inline-flex items-center gap-2 text-slate-300">
                        <Scale className="w-4 h-4 text-sky-200" />
                        <span className="font-semibold">ToneSoul</span>
                    </div>
                    <p className="mt-2 text-xs text-slate-500">AI Governance Middleware</p>
                    <p className="mt-6 text-xs text-slate-500">
                        <span className="text-slate-400">© 2026</span>{" "}
                        <span className="text-slate-500">ToneSoul Project</span>
                    </p>
                </footer>
            </main>
        </div>
    );
}

