import Link from "next/link";
import { Brain, Mail, Github, ExternalLink, BookOpen, Shield, BarChart3, FileText, Lightbulb, Heart } from "lucide-react";
import SevenDimensionCards from "@/components/SevenDimensionCards";
import SevenParadoxCards from "@/components/SevenParadoxCards";
import TierModelPublicCue from "@/components/TierModelPublicCue";

// Schema.org JSON-LD for AI Search Optimization
const jsonLd = {
    "@context": "https://schema.org",
    "@type": "SoftwareSourceCode",
    "name": "ToneSoul Integrity Framework",
    "alternateName": ["語魂系統", "ToneSoul", "TSAP", "ToneSoul-Audit Protocol"],
    "description": "A governance middleware for auditable, self-correcting AI agents. Implements STREI vector analysis, multi-perspective deliberation, and entropy-based tension metrics.",
    "codeRepository": "https://github.com/Fan1234-1/tonesoul52",
    "programmingLanguage": ["TypeScript", "Python"],
    "applicationCategory": "AI Governance",
    "license": "https://opensource.org/licenses/Apache-2.0",
    "author": {
        "@type": "Person",
        "name": "Fan1234-1",
        "email": "xsw123zaq@gmail.com"
    }
};

// 相關論文（已驗證連結）
const researchPapers = [
    {
        title: "Multiplex Thinking: Reasoning via Token-wise Branch-and-Merge",
        url: "https://arxiv.org/abs/2505.17125",
        relevance: "vMT-2601 Protocol 的理論基礎",
        year: 2025
    },
    {
        title: "Re-Reading Improves Reasoning in Large Language Models",
        url: "https://arxiv.org/abs/2309.06275",
        relevance: "RE2 技術的來源",
        year: 2024
    },
    {
        title: "Constitutional AI: Harmlessness from AI Feedback",
        url: "https://arxiv.org/abs/2212.08073",
        relevance: "自我批評機制的靈感",
        year: 2022
    },
    {
        title: "Debate Helps Supervising AI Agents",
        url: "https://arxiv.org/abs/2305.14859",
        relevance: "多視角審議的設計參考",
        year: 2023
    }
];

export default function DocsPage() {
    return (
        <>
            <script
                type="application/ld+json"
                dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
            />
            <div className="min-h-screen bg-[#0a0e27] text-white">
                {/* Background */}
                <div className="pointer-events-none fixed inset-0 -z-10">
                    <div className="absolute inset-0 bg-[radial-gradient(1200px_circle_at_20%_10%,rgba(56,189,248,0.22),transparent_55%),radial-gradient(900px_circle_at_80%_30%,rgba(244,63,94,0.18),transparent_60%),radial-gradient(700px_circle_at_50%_90%,rgba(99,102,241,0.14),transparent_55%)]" />
                    <div className="absolute inset-0 opacity-35 bg-[radial-gradient(rgba(148,163,184,0.12)_1px,transparent_1px)] [background-size:22px_22px]" />
                    <div className="absolute inset-0 bg-gradient-to-b from-transparent via-black/10 to-black/35" />
                </div>

                {/* Header */}
                <header className="border-b border-slate-700/40 backdrop-blur sticky top-0 z-50 bg-[#0a0e27]/70">
                    <div className="max-w-5xl mx-auto px-5 py-4 flex justify-between items-center gap-4">
                        <div className="flex items-center gap-3">
                            <Brain className="w-7 h-7 text-sky-300" />
                            <span className="text-xl font-bold">ToneSoul</span>
                        </div>
                        <nav className="flex items-center gap-5 text-sm">
                            <div className="hidden lg:flex items-center gap-5 text-slate-300">
                                <a href="#paradoxes" className="hover:text-white transition-colors">Paradoxes</a>
                                <a href="#protocols" className="hover:text-white transition-colors">Protocols</a>
                                <a href="#audit" className="hover:text-white transition-colors">7D</a>
                                <a href="#research" className="hover:text-white transition-colors">Research</a>
                            </div>
                            <Link href="/showcase" className="hidden sm:inline text-slate-300 hover:text-white transition-colors">
                                Showcase
                            </Link>
                            <Link href="/" className="text-slate-300 hover:text-white transition-colors">
                                App
                            </Link>
                            <a
                                href="https://github.com/Fan1234-1/tonesoul52"
                                target="_blank"
                                rel="noopener"
                                className="flex items-center gap-1 text-slate-300 hover:text-white"
                            >
                                <Github className="w-4 h-4" /> GitHub
                            </a>
                        </nav>
                    </div>
                </header>

                <main className="max-w-5xl mx-auto px-5 py-12 space-y-16">

                    {/* Hero */}
                    <section className="text-center py-8">
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-slate-700/50 bg-slate-900/30 text-xs tracking-widest text-slate-300">
                            AI GOVERNANCE MIDDLEWARE
                        </div>
                        <h1 className="text-4xl md:text-5xl font-bold mb-4 mt-6 bg-gradient-to-r from-sky-300 via-slate-200 to-rose-300 bg-clip-text text-transparent">
                            ToneSoul Integrity Framework
                        </h1>
                        <p className="text-xl text-slate-300 mb-2">語魂系統 — AI 治理中介層</p>
                        <p className="text-slate-400">A governance middleware for auditable, self-correcting AI agents.</p>
                        <div className="mt-7 flex flex-wrap justify-center gap-3">
                            <Link
                                href="/"
                                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-sky-500/15 border border-sky-400/30 hover:bg-sky-500/20 transition-colors text-sm"
                            >
                                Open App →
                            </Link>
                            <Link
                                href="/showcase"
                                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-700/55 bg-slate-900/25 hover:bg-slate-900/35 transition-colors text-sm text-slate-200"
                            >
                                View Showcase →
                            </Link>
                        </div>
                    </section>

                    <TierModelPublicCue variant="full" />

                    {/* Getting Started */}
                    <section id="getting-started" className="scroll-mt-28 bg-gradient-to-r from-sky-500/10 to-rose-500/10 border border-slate-700/45 rounded-2xl p-8">
                        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                            Getting Started | 快速開始
                        </h2>
                        <div className="grid md:grid-cols-3 gap-6">
                            <div className="bg-slate-900/50 rounded-xl p-5">
                                <div className="text-3xl font-bold text-sky-300 mb-2">1</div>
                                <h3 className="font-bold mb-2">選配：設定 API Key</h3>
                                <p className="text-sm text-slate-400 mb-3">取得 Gemini API Key，以便後端不可用時啟用 fallback（可選）</p>
                                <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noopener" className="text-xs text-sky-300 hover:underline">
                                    aistudio.google.com →
                                </a>
                            </div>
                            <div className="bg-slate-900/50 rounded-xl p-5">
                                <div className="text-3xl font-bold text-sky-300 mb-2">2</div>
                                <h3 className="font-bold mb-2">開啟 App</h3>
                                <p className="text-sm text-slate-400 mb-3">訪問 ToneSoul Web App；可在設定中輸入 API Key（選配）</p>
                                <Link href="/" className="text-xs text-sky-300 hover:underline">
                                    開啟 App →
                                </Link>
                            </div>
                            <div className="bg-slate-900/50 rounded-xl p-5">
                                <div className="text-3xl font-bold text-sky-300 mb-2">3</div>
                                <h3 className="font-bold mb-2">開始對話</h3>
                                <p className="text-sm text-slate-400 mb-3">建立新對話，體驗多視角審議和熵值計算</p>
                                <span className="text-xs text-slate-500">右上角會顯示 Backend / Fallback 狀態</span>
                            </div>
                        </div>
                        <div className="mt-6 p-4 bg-slate-900/30 rounded-lg border border-slate-700/60">
                            <p className="text-sm text-slate-400">
                                <strong className="text-white">🔒 隱私說明：</strong>
                                對話清單與歷史會儲存在你的瀏覽器（IndexedDB）。產生回覆時，訊息會送到 ToneSoul 後端（Council）或在後端不可用時改由你提供的 Gemini API Key 直接呼叫供應商。請避免輸入高度敏感資訊。
                            </p>
                        </div>
                    </section>

                    {/* About Author */}
                    <section id="about" className="scroll-mt-28 bg-slate-900/25 border border-slate-700/45 rounded-2xl p-8">
                        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                            <Heart className="w-6 h-6 text-rose-300" />
                            About | 關於作者
                        </h2>
                        <div className="space-y-4 text-slate-300">
                            <p>
                                我是一個對 AI 責任性和透明度有執著的開發者。ToneSoul 不是一個聊天機器人——它是一個讓 AI
                                <strong className="text-white">「對自己說過的話負責」</strong>的治理框架。
                            </p>
                            <p>
                                I&apos;m a developer obsessed with AI accountability and transparency. ToneSoul is not a chatbot—it&apos;s a governance framework that makes AI
                                <strong className="text-white"> accountable for what it says</strong>.
                            </p>
                        </div>
                        <div className="mt-6 flex flex-wrap gap-4">
                            <a href="mailto:xsw123zaq@gmail.com" className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors">
                                <Mail className="w-4 h-4" /> xsw123zaq@gmail.com
                            </a>
                            <a href="https://github.com/Fan1234-1/tonesoul52" target="_blank" rel="noopener" className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors">
                                <Github className="w-4 h-4" /> GitHub Repository
                            </a>
                        </div>
                    </section>

                    {/* Why */}
                    <section id="why" className="scroll-mt-28 bg-slate-900/25 border border-slate-700/45 rounded-2xl p-8">
                        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                            <Lightbulb className="w-6 h-6 text-sky-300" />
                            Why ToneSoul? | 為什麼要做這套系統？
                        </h2>
                        <blockquote className="border-l-4 border-sky-400 pl-4 italic text-slate-200 mb-6">
                            「AI 是否能對自己說過的話負責？」
                            <br />
                            <span className="text-slate-500">— 這個問題催生了 ToneSoul 的核心概念：語義責任</span>
                        </blockquote>
                        <div className="space-y-4 text-slate-300">
                            <p>
                                大多數 AI 系統是<strong className="text-white">黑盒輸出</strong>——你不知道它為什麼這樣回答。
                                ToneSoul 強制讓思考過程透明：
                            </p>
                            <ul className="list-disc list-inside space-y-2 ml-4">
                                <li>三個視角（哲學家、工程師、守護者）同時審議</li>
                                <li>熵值計算顯示思考的「張力」程度</li>
                                <li>每個決策都有可追溯的公式</li>
                                <li>被犧牲的選項（邏輯陰影）也被保留</li>
                            </ul>
                        </div>
                    </section>

                    {/* Philosophy - Three Axioms */}
                    <section id="philosophy" className="scroll-mt-28 bg-gradient-to-r from-sky-500/10 to-rose-500/10 border border-slate-700/45 rounded-2xl p-8">
                        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                            <BookOpen className="w-6 h-6 text-sky-300" />
                            Philosophy | 哲學宣言
                        </h2>
                        <blockquote className="border-l-4 border-rose-400 pl-4 italic text-slate-200 mb-6">
                            「輸出即事件，語詞一旦釋出便不可撤回——<br />
                            語義責任始於此。」
                        </blockquote>
                        <h3 className="font-bold text-lg mb-4 text-sky-200">Three Axioms of Semantic Responsibility | 語義責任三公理</h3>
                        <div className="grid md:grid-cols-3 gap-4 mb-8">
                            <div className="bg-slate-900/35 border border-slate-700/55 rounded-xl p-5">
                                <div className="text-2xl font-bold text-sky-300 mb-2">α</div>
                                <h4 className="font-bold mb-1">Output is Event</h4>
                                <p className="text-sm text-slate-400">輸出即事件。AI 的每一句話都是不可撤回的行為，而非可編輯的訊息。</p>
                            </div>
                            <div className="bg-slate-900/35 border border-slate-700/55 rounded-xl p-5">
                                <div className="text-2xl font-bold text-sky-300 mb-2">β</div>
                                <h4 className="font-bold mb-1">Freedom is Selectability</h4>
                                <p className="text-sm text-slate-400">自由即可選擇性。AI 的「自由」不是無限生成，而是受約束的選擇空間。</p>
                            </div>
                            <div className="bg-slate-900/35 border border-slate-700/55 rounded-xl p-5">
                                <div className="text-2xl font-bold text-sky-300 mb-2">γ</div>
                                <h4 className="font-bold mb-1">Temporal Inescapability</h4>
                                <p className="text-sm text-slate-400">時間不可逃避。一旦生成，就存在於時間中，有後果、有責任。</p>
                            </div>
                        </div>
                        <h3 className="font-bold text-lg mb-4 text-sky-200">Seven Principles | 語義責任七原則</h3>
                        <div className="grid md:grid-cols-2 gap-3">
                            {[
                                { num: "I", title: "語義責任", desc: "AI 對其輸出造成的語義影響負責" },
                                { num: "II", title: "不可撤回性", desc: "輸出一旦被接收，影響已經發生" },
                                { num: "III", title: "歸因義務", desc: "每個決策必須可追溯至其來源" },
                                { num: "IV", title: "透明義務", desc: "推理過程不得被隱藏" },
                                { num: "V", title: "γ·Honesty > β·Helpfulness", desc: "誠實優先於討好" },
                                { num: "VI", title: "傷害預防", desc: "P0 約束：防止傷害高於一切" },
                                { num: "VII", title: "語義場守恆", desc: "系統不得污染語義環境" },
                            ].map((p, i) => (
                                <div key={i} className="flex items-start gap-3 bg-slate-900/30 rounded-lg p-3 border border-slate-700/45">
                                    <span className="text-sky-300 font-bold text-sm mt-0.5 shrink-0 w-6">{p.num}</span>
                                    <div>
                                        <span className="font-bold text-white text-sm">{p.title}</span>
                                        <p className="text-xs text-slate-400 mt-0.5">{p.desc}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>

                    {/* Seven Paradoxes Answered */}
                    <div id="paradoxes" className="scroll-mt-28">
                        <SevenParadoxCards />
                    </div>

                    {/* Core Protocols */}
                    <details id="protocols" className="scroll-mt-28 group border border-slate-700/60 rounded-2xl overflow-hidden bg-slate-900/20">
                        <summary className="list-none cursor-pointer p-8 flex items-center justify-between hover:bg-slate-800/40 transition-colors">
                            <h2 className="text-2xl font-bold flex items-center gap-2">
                                <Shield className="w-6 h-6 text-sky-300" />
                                Core Protocols | 核心協議
                            </h2>
                            <span className="text-slate-500 group-open:rotate-180 transition-transform">▼</span>
                        </summary>
                        <div className="p-8 pt-0">
                            <div className="grid md:grid-cols-2 gap-4">
                                <div className="bg-slate-900/30 border border-slate-700/55 rounded-xl p-6">
                                    <div className="flex items-center gap-2 mb-3">
                                        <BarChart3 className="w-5 h-5 text-sky-300" />
                                        <h3 className="font-bold">ToneSoul Entropy Protocol</h3>
                                    </div>
                                    <p className="text-sm text-slate-400 mb-3">熵值協議 — 認知張力指標</p>
                                    <code className="block text-xs bg-slate-950/60 p-2 rounded text-sky-200">
                                        E = 0.4 + div + risk - coh - int
                                    </code>
                                </div>
                                <div className="bg-slate-900/30 border border-slate-700/55 rounded-xl p-6">
                                    <div className="flex items-center gap-2 mb-3">
                                        <FileText className="w-5 h-5 text-rose-300" />
                                        <h3 className="font-bold">ToneSoul-Audit Protocol (TSAP)</h3>
                                    </div>
                                    <p className="text-sm text-slate-400 mb-3">審計協議 — LLM 自評交叉驗證</p>
                                    <code className="block text-xs bg-slate-950/60 p-2 rounded text-rose-200">
                                        discrepancy = |code - llm|
                                    </code>
                                </div>
                                <div className="bg-slate-900/30 border border-slate-700/55 rounded-xl p-6">
                                    <div className="flex items-center gap-2 mb-3">
                                        <Brain className="w-5 h-5 text-sky-300" />
                                        <h3 className="font-bold">STREI Governance Vector</h3>
                                    </div>
                                    <p className="text-sm text-slate-400 mb-3">治理向量 — 五維分析</p>
                                    <code className="block text-xs bg-slate-950/60 p-2 rounded text-sky-200">
                                        V ∈ ℝ⁵: if R &gt; 0.6 → BLOCK
                                    </code>
                                </div>
                                <div className="bg-slate-900/30 border border-slate-700/55 rounded-xl p-6">
                                    <div className="flex items-center gap-2 mb-3">
                                        <Lightbulb className="w-5 h-5 text-rose-300" />
                                        <h3 className="font-bold">vMT-2601 Multiplex Thinking</h3>
                                    </div>
                                    <p className="text-sm text-slate-400 mb-3">複用思維 — 邏輯陰影保留</p>
                                    <code className="block text-xs bg-slate-950/60 p-2 rounded text-rose-200">
                                        h = Σ wᵢ · E(tᵢ) + shadows
                                    </code>
                                </div>
                            </div>
                        </div>
                    </details>

                    {/* 7D Audit Framework */}
                    <div id="audit" className="scroll-mt-28">
                        <SevenDimensionCards />
                    </div>

                    {/* Research Papers */}
                    <section id="research" className="scroll-mt-28 bg-slate-900/25 border border-slate-700/45 rounded-2xl p-8">
                        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                            <BookOpen className="w-6 h-6 text-sky-300" />
                            Research Foundation | 研究基礎
                        </h2>
                        <p className="text-slate-400 mb-6">ToneSoul 的設計參考了以下學術研究：</p>
                        <div className="space-y-4">
                            {researchPapers.map((paper, i) => (
                                <a
                                    key={i}
                                    href={paper.url}
                                    target="_blank"
                                    rel="noopener"
                                    className="block bg-slate-900/40 border border-slate-700/55 rounded-lg p-4 hover:border-sky-400/50 transition-colors"
                                >
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <h3 className="font-bold text-white flex items-center gap-2">
                                                {paper.title}
                                                <ExternalLink className="w-3 h-3 text-slate-500" />
                                            </h3>
                                            <p className="text-sm text-sky-300 mt-1">{paper.relevance}</p>
                                        </div>
                                        <span className="text-xs text-slate-500">{paper.year}</span>
                                    </div>
                                </a>
                            ))}
                        </div>
                    </section>

                    {/* Architecture Quick View */}
                    <details id="architecture" className="scroll-mt-28 group border border-slate-700/60 rounded-2xl overflow-hidden bg-slate-900/20">
                        <summary className="list-none cursor-pointer p-8 flex items-center justify-between hover:bg-slate-800/40 transition-colors">
                            <h2 className="text-2xl font-bold">Architecture | 架構概覽</h2>
                            <span className="text-slate-500 group-open:rotate-180 transition-transform">▼</span>
                        </summary>
                        <div className="p-8 pt-0">
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm">
                                    <thead>
                                        <tr className="border-b border-slate-600">
                                            <th className="py-2 px-3 text-left text-slate-400">Layer</th>
                                            <th className="py-2 px-3 text-left text-slate-400">Component</th>
                                            <th className="py-2 px-3 text-left text-slate-400">Function</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr className="border-b border-slate-700/50"><td className="py-2 px-3 font-mono text-sky-300">L0</td><td className="py-2 px-3">Law (法)</td><td className="py-2 px-3 text-slate-300">Immutable axioms</td></tr>
                                        <tr className="border-b border-slate-700/50"><td className="py-2 px-3 font-mono text-sky-300">L1</td><td className="py-2 px-3">Spine (脊)</td><td className="py-2 px-3 text-slate-300">State orchestration</td></tr>
                                        <tr className="border-b border-slate-700/50"><td className="py-2 px-3 font-mono text-sky-300">L2</td><td className="py-2 px-3">Brain (腦)</td><td className="py-2 px-3 text-slate-300">LLM integration</td></tr>
                                        <tr className="border-b border-slate-700/50"><td className="py-2 px-3 font-mono text-sky-300">L3</td><td className="py-2 px-3">Sensor (感)</td><td className="py-2 px-3 text-slate-300">STREI telemetry</td></tr>
                                        <tr className="border-b border-slate-700/50"><td className="py-2 px-3 font-mono text-sky-300">L4</td><td className="py-2 px-3">Ledger (帳)</td><td className="py-2 px-3 text-slate-300">Audit log</td></tr>
                                        <tr><td className="py-2 px-3 font-mono text-sky-300">L5</td><td className="py-2 px-3">Body (體)</td><td className="py-2 px-3 text-slate-300">I/O interface</td></tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </details>

                    {/* Engineering Terminology Mapping */}
                    <details id="mapping" className="scroll-mt-28 group border border-slate-700/60 rounded-2xl overflow-hidden bg-slate-900/20">
                        <summary className="list-none cursor-pointer p-8 flex items-center justify-between hover:bg-slate-800/40 transition-colors">
                            <h2 className="text-2xl font-bold">Engineering Mapping | 工程術語對照</h2>
                            <span className="text-slate-500 group-open:rotate-180 transition-transform">▼</span>
                        </summary>
                        <div className="p-8 pt-0">
                            <p className="text-slate-400 mb-6">ToneSoul 的概念如何對應到現代 AI/ML 技術標準：</p>
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm">
                                    <thead>
                                        <tr className="border-b border-slate-700/60">
                                            <th className="py-3 px-3 text-left text-sky-200">ToneSoul 術語</th>
                                            <th className="py-3 px-3 text-left text-sky-200">AI/ML 標準術語</th>
                                            <th className="py-3 px-3 text-left text-sky-200">說明</th>
                                        </tr>
                                    </thead>
                                    <tbody className="text-slate-300">
                                        <tr className="border-b border-slate-700/50">
                                            <td className="py-3 px-3 font-bold text-white">Council (議會)</td>
                                            <td className="py-3 px-3 text-sky-300">Multi-Agent Debate / Ensemble</td>
                                            <td className="py-3 px-3 text-sm">多代理辯論系統，類似 Mixture of Experts (MoE)</td>
                                        </tr>
                                        <tr className="border-b border-slate-700/50">
                                            <td className="py-3 px-3 font-bold text-white">Entropy (熵值)</td>
                                            <td className="py-3 px-3 text-sky-300">Cognitive Uncertainty / Disagreement Score</td>
                                            <td className="py-3 px-3 text-sm">認知不確定性度量，類似 Calibration Error</td>
                                        </tr>
                                        <tr className="border-b border-slate-700/50">
                                            <td className="py-3 px-3 font-bold text-white">Logical Shadows (邏輯陰影)</td>
                                            <td className="py-3 px-3 text-sky-300">Beam Search Alternatives / Rejected Paths</td>
                                            <td className="py-3 px-3 text-sm">被淘汰的推理路徑，保留以供追溯</td>
                                        </tr>
                                        <tr className="border-b border-slate-700/50">
                                            <td className="py-3 px-3 font-bold text-white">STREI Vector</td>
                                            <td className="py-3 px-3 text-sky-300">Multi-Dimensional Safety Score</td>
                                            <td className="py-3 px-3 text-sm">5D 治理向量，類似 Reward Model Outputs</td>
                                        </tr>
                                        <tr className="border-b border-slate-700/50">
                                            <td className="py-3 px-3 font-bold text-white">RE2 (重複閱讀)</td>
                                            <td className="py-3 px-3 text-sky-300">Self-Consistency / Re-Reading</td>
                                            <td className="py-3 px-3 text-sm">基於 arXiv:2309.06275 的推理增強技術</td>
                                        </tr>
                                        <tr className="border-b border-slate-700/50">
                                            <td className="py-3 px-3 font-bold text-white">Synthesizer (綜合者)</td>
                                            <td className="py-3 px-3 text-sky-300">Aggregator / MetaLearner</td>
                                            <td className="py-3 px-3 text-sm">整合多視角輸出的 Meta 模型</td>
                                        </tr>
                                        <tr className="border-b border-slate-700/50">
                                            <td className="py-3 px-3 font-bold text-white">TSAP (審計協議)</td>
                                            <td className="py-3 px-3 text-sky-300">Self-Critique / Constitutional AI</td>
                                            <td className="py-3 px-3 text-sm">LLM 自評與程式碼驗證的交叉檢查</td>
                                        </tr>
                                        <tr>
                                            <td className="py-3 px-3 font-bold text-white">vMT-2601</td>
                                            <td className="py-3 px-3 text-sky-300">Multiplex Thinking / Branch-Merge</td>
                                            <td className="py-3 px-3 text-sm">基於 arXiv:2505.17125 的並行推理協議</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </details>

                </main>

                {/* Footer */}
                <footer className="border-t border-slate-700 py-8 mt-16">
                    <div className="max-w-4xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-slate-400">
                        <div className="flex items-center gap-2">
                            <Brain className="w-5 h-5" />
                            <span>ToneSoul Integrity Framework</span>
                        </div>
                        <div className="flex gap-6">
                            <a href="mailto:xsw123zaq@gmail.com" className="hover:text-white flex items-center gap-1">
                                <Mail className="w-4 h-4" /> Contact
                            </a>
                            <a href="https://github.com/Fan1234-1/tonesoul52" target="_blank" rel="noopener" className="hover:text-white flex items-center gap-1">
                                <Github className="w-4 h-4" /> GitHub
                            </a>
                            <span>Apache 2.0</span>
                        </div>
                    </div>
                </footer>
            </div>
        </>
    );
}
