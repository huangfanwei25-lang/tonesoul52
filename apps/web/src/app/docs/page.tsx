import Link from "next/link";
import { Brain, Mail, Github, ExternalLink, BookOpen, Shield, BarChart3, FileText, Lightbulb, Heart } from "lucide-react";

// Schema.org JSON-LD for AI Search Optimization
const jsonLd = {
    "@context": "https://schema.org",
    "@type": "SoftwareSourceCode",
    "name": "ToneSoul Integrity Framework",
    "alternateName": ["語魂系統", "ToneSoul", "TSAP", "ToneSoul-Audit Protocol"],
    "description": "A governance middleware for auditable, self-correcting AI agents. Implements STREI vector analysis, multi-perspective deliberation, and entropy-based tension metrics.",
    "codeRepository": "https://github.com/Fan1234-1/ToneSoul-Architecture-Engine",
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
    },
    {
        title: "Chain-of-Thought Prompting Elicits Reasoning",
        url: "https://arxiv.org/abs/2201.11903",
        relevance: "思維鏈的基礎研究",
        year: 2022
    }
];

export default function DocsPage() {
    return (
        <>
            <script
                type="application/ld+json"
                dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
            />
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-900 text-white">
                {/* Header */}
                <header className="border-b border-slate-700/50 backdrop-blur-sm sticky top-0 z-50 bg-slate-900/80">
                    <div className="max-w-4xl mx-auto px-6 py-4 flex justify-between items-center">
                        <div className="flex items-center gap-3">
                            <Brain className="w-8 h-8 text-indigo-400" />
                            <span className="text-xl font-bold">ToneSoul</span>
                        </div>
                        <nav className="flex gap-6 text-sm">
                            <Link href="/" className="text-slate-300 hover:text-white transition-colors">App</Link>
                            <a href="https://github.com/Fan1234-1/ToneSoul-Architecture-Engine" target="_blank" rel="noopener" className="flex items-center gap-1 text-slate-300 hover:text-white">
                                <Github className="w-4 h-4" /> GitHub
                            </a>
                        </nav>
                    </div>
                </header>

                <main className="max-w-4xl mx-auto px-6 py-12 space-y-16">

                    {/* Hero */}
                    <section className="text-center py-8">
                        <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                            ToneSoul Integrity Framework
                        </h1>
                        <p className="text-xl text-slate-300 mb-2">語魂系統 — AI 治理中介層</p>
                        <p className="text-slate-400">A governance middleware for auditable, self-correcting AI agents.</p>
                    </section>

                    {/* Getting Started */}
                    <section className="bg-gradient-to-r from-emerald-900/30 to-teal-900/30 border border-emerald-700/50 rounded-2xl p-8">
                        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                            🚀 Getting Started | 快速開始
                        </h2>
                        <div className="grid md:grid-cols-3 gap-6">
                            <div className="bg-slate-900/50 rounded-xl p-5">
                                <div className="text-3xl font-bold text-emerald-400 mb-2">1</div>
                                <h3 className="font-bold mb-2">取得 API Key</h3>
                                <p className="text-sm text-slate-400 mb-3">前往 Google AI Studio 取得免費的 Gemini API Key</p>
                                <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noopener" className="text-xs text-emerald-400 hover:underline">
                                    aistudio.google.com →
                                </a>
                            </div>
                            <div className="bg-slate-900/50 rounded-xl p-5">
                                <div className="text-3xl font-bold text-emerald-400 mb-2">2</div>
                                <h3 className="font-bold mb-2">開啟 App</h3>
                                <p className="text-sm text-slate-400 mb-3">訪問 ToneSoul Web App，在設定中輸入你的 API Key</p>
                                <Link href="/" className="text-xs text-emerald-400 hover:underline">
                                    開啟 App →
                                </Link>
                            </div>
                            <div className="bg-slate-900/50 rounded-xl p-5">
                                <div className="text-3xl font-bold text-emerald-400 mb-2">3</div>
                                <h3 className="font-bold mb-2">開始對話</h3>
                                <p className="text-sm text-slate-400 mb-3">建立新對話，體驗多視角審議和熵值計算</p>
                                <span className="text-xs text-slate-500">你的數據只存在你的瀏覽器</span>
                            </div>
                        </div>
                        <div className="mt-6 p-4 bg-slate-900/30 rounded-lg border border-slate-700">
                            <p className="text-sm text-slate-400">
                                <strong className="text-white">🔒 隱私承諾：</strong>
                                ToneSoul 不收集任何用戶數據。API Key 和對話記錄只存在你的瀏覽器 localStorage 和 IndexedDB 中。
                            </p>
                        </div>
                    </section>

                    {/* About Author */}
                    <section className="bg-slate-800/50 border border-slate-700 rounded-2xl p-8">
                        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                            <Heart className="w-6 h-6 text-pink-400" />
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
                            <a href="https://github.com/Fan1234-1/ToneSoul-Architecture-Engine" target="_blank" rel="noopener" className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors">
                                <Github className="w-4 h-4" /> GitHub Repository
                            </a>
                        </div>
                    </section>

                    {/* Why */}
                    <section className="bg-slate-800/50 border border-slate-700 rounded-2xl p-8">
                        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                            <Lightbulb className="w-6 h-6 text-amber-400" />
                            Why ToneSoul? | 為什麼要做這套系統？
                        </h2>
                        <blockquote className="border-l-4 border-indigo-500 pl-4 italic text-slate-300 mb-6">
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

                    {/* Core Protocols */}
                    <section>
                        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                            <Shield className="w-6 h-6 text-indigo-400" />
                            Core Protocols | 核心協議
                        </h2>
                        <div className="grid md:grid-cols-2 gap-4">
                            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                                <div className="flex items-center gap-2 mb-3">
                                    <BarChart3 className="w-5 h-5 text-purple-400" />
                                    <h3 className="font-bold">ToneSoul Entropy Protocol</h3>
                                </div>
                                <p className="text-sm text-slate-400 mb-3">熵值協議 — 認知張力指標</p>
                                <code className="block text-xs bg-slate-900 p-2 rounded text-purple-300">
                                    E = 0.4 + div + risk - coh - int
                                </code>
                            </div>
                            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                                <div className="flex items-center gap-2 mb-3">
                                    <FileText className="w-5 h-5 text-amber-400" />
                                    <h3 className="font-bold">ToneSoul-Audit Protocol (TSAP)</h3>
                                </div>
                                <p className="text-sm text-slate-400 mb-3">審計協議 — LLM 自評交叉驗證</p>
                                <code className="block text-xs bg-slate-900 p-2 rounded text-amber-300">
                                    discrepancy = |code - llm|
                                </code>
                            </div>
                            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                                <div className="flex items-center gap-2 mb-3">
                                    <Brain className="w-5 h-5 text-indigo-400" />
                                    <h3 className="font-bold">STREI Governance Vector</h3>
                                </div>
                                <p className="text-sm text-slate-400 mb-3">治理向量 — 五維分析</p>
                                <code className="block text-xs bg-slate-900 p-2 rounded text-indigo-300">
                                    V ∈ ℝ⁵: if R &gt; 0.6 → BLOCK
                                </code>
                            </div>
                            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                                <div className="flex items-center gap-2 mb-3">
                                    <Lightbulb className="w-5 h-5 text-pink-400" />
                                    <h3 className="font-bold">vMT-2601 Multiplex Thinking</h3>
                                </div>
                                <p className="text-sm text-slate-400 mb-3">複用思維 — 邏輯陰影保留</p>
                                <code className="block text-xs bg-slate-900 p-2 rounded text-pink-300">
                                    h = Σ wᵢ · E(tᵢ) + shadows
                                </code>
                            </div>
                        </div>
                    </section>

                    {/* Research Papers */}
                    <section className="bg-slate-800/50 border border-slate-700 rounded-2xl p-8">
                        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                            <BookOpen className="w-6 h-6 text-green-400" />
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
                                    className="block bg-slate-900/50 border border-slate-700 rounded-lg p-4 hover:border-green-500/50 transition-colors"
                                >
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <h3 className="font-bold text-white flex items-center gap-2">
                                                {paper.title}
                                                <ExternalLink className="w-3 h-3 text-slate-500" />
                                            </h3>
                                            <p className="text-sm text-green-400 mt-1">{paper.relevance}</p>
                                        </div>
                                        <span className="text-xs text-slate-500">{paper.year}</span>
                                    </div>
                                </a>
                            ))}
                        </div>
                    </section>

                    {/* Architecture Quick View */}
                    <section className="bg-slate-800/50 border border-slate-700 rounded-2xl p-8">
                        <h2 className="text-2xl font-bold mb-6">Architecture | 架構概覽</h2>
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
                                    <tr className="border-b border-slate-700/50"><td className="py-2 px-3 font-mono text-indigo-400">L0</td><td className="py-2 px-3">Law (法)</td><td className="py-2 px-3 text-slate-300">Immutable axioms</td></tr>
                                    <tr className="border-b border-slate-700/50"><td className="py-2 px-3 font-mono text-indigo-400">L1</td><td className="py-2 px-3">Spine (脊)</td><td className="py-2 px-3 text-slate-300">State orchestration</td></tr>
                                    <tr className="border-b border-slate-700/50"><td className="py-2 px-3 font-mono text-indigo-400">L2</td><td className="py-2 px-3">Brain (腦)</td><td className="py-2 px-3 text-slate-300">LLM integration</td></tr>
                                    <tr className="border-b border-slate-700/50"><td className="py-2 px-3 font-mono text-indigo-400">L3</td><td className="py-2 px-3">Sensor (感)</td><td className="py-2 px-3 text-slate-300">STREI telemetry</td></tr>
                                    <tr className="border-b border-slate-700/50"><td className="py-2 px-3 font-mono text-indigo-400">L4</td><td className="py-2 px-3">Ledger (帳)</td><td className="py-2 px-3 text-slate-300">Audit log</td></tr>
                                    <tr><td className="py-2 px-3 font-mono text-indigo-400">L5</td><td className="py-2 px-3">Body (體)</td><td className="py-2 px-3 text-slate-300">I/O interface</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </section>

                    {/* Engineering Terminology Mapping */}
                    <section className="bg-gradient-to-br from-indigo-900/30 to-purple-900/30 border border-indigo-700/50 rounded-2xl p-8">
                        <h2 className="text-2xl font-bold mb-6">Engineering Mapping | 工程術語對照</h2>
                        <p className="text-slate-400 mb-6">ToneSoul 的概念如何對應到現代 AI/ML 技術標準：</p>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="border-b border-indigo-600/50">
                                        <th className="py-3 px-3 text-left text-indigo-300">ToneSoul 術語</th>
                                        <th className="py-3 px-3 text-left text-indigo-300">AI/ML 標準術語</th>
                                        <th className="py-3 px-3 text-left text-indigo-300">說明</th>
                                    </tr>
                                </thead>
                                <tbody className="text-slate-300">
                                    <tr className="border-b border-slate-700/50">
                                        <td className="py-3 px-3 font-bold text-white">Council (議會)</td>
                                        <td className="py-3 px-3 text-cyan-400">Multi-Agent Debate / Ensemble</td>
                                        <td className="py-3 px-3 text-sm">多代理辯論系統，類似 Mixture of Experts (MoE)</td>
                                    </tr>
                                    <tr className="border-b border-slate-700/50">
                                        <td className="py-3 px-3 font-bold text-white">Entropy (熵值)</td>
                                        <td className="py-3 px-3 text-cyan-400">Cognitive Uncertainty / Disagreement Score</td>
                                        <td className="py-3 px-3 text-sm">認知不確定性度量，類似 Calibration Error</td>
                                    </tr>
                                    <tr className="border-b border-slate-700/50">
                                        <td className="py-3 px-3 font-bold text-white">Logical Shadows (邏輯陰影)</td>
                                        <td className="py-3 px-3 text-cyan-400">Beam Search Alternatives / Rejected Paths</td>
                                        <td className="py-3 px-3 text-sm">被淘汰的推理路徑，保留以供追溯</td>
                                    </tr>
                                    <tr className="border-b border-slate-700/50">
                                        <td className="py-3 px-3 font-bold text-white">STREI Vector</td>
                                        <td className="py-3 px-3 text-cyan-400">Multi-Dimensional Safety Score</td>
                                        <td className="py-3 px-3 text-sm">5D 治理向量，類似 Reward Model Outputs</td>
                                    </tr>
                                    <tr className="border-b border-slate-700/50">
                                        <td className="py-3 px-3 font-bold text-white">RE2 (重複閱讀)</td>
                                        <td className="py-3 px-3 text-cyan-400">Self-Consistency / Re-Reading</td>
                                        <td className="py-3 px-3 text-sm">基於 arXiv:2309.06275 的推理增強技術</td>
                                    </tr>
                                    <tr className="border-b border-slate-700/50">
                                        <td className="py-3 px-3 font-bold text-white">Synthesizer (綜合者)</td>
                                        <td className="py-3 px-3 text-cyan-400">Aggregator / MetaLearner</td>
                                        <td className="py-3 px-3 text-sm">整合多視角輸出的 Meta 模型</td>
                                    </tr>
                                    <tr className="border-b border-slate-700/50">
                                        <td className="py-3 px-3 font-bold text-white">TSAP (審計協議)</td>
                                        <td className="py-3 px-3 text-cyan-400">Self-Critique / Constitutional AI</td>
                                        <td className="py-3 px-3 text-sm">LLM 自評與程式碼驗證的交叉檢查</td>
                                    </tr>
                                    <tr>
                                        <td className="py-3 px-3 font-bold text-white">vMT-2601</td>
                                        <td className="py-3 px-3 text-cyan-400">Multiplex Thinking / Branch-Merge</td>
                                        <td className="py-3 px-3 text-sm">基於 arXiv:2505.17125 的並行推理協議</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </section>

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
                            <a href="https://github.com/Fan1234-1/ToneSoul-Architecture-Engine" target="_blank" rel="noopener" className="hover:text-white flex items-center gap-1">
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
