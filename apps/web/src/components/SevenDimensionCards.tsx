"use client";

import { useState } from "react";
import {
    FlaskConical,
    Swords,
    Database,
    Eye,
    Scale,
    Globe,
    HeartPulse,
    ChevronDown,
    Sparkles,
} from "lucide-react";

interface DimensionData {
    id: string;
    abbr: string;
    name: string;
    nameZh: string;
    oneLiner: string;
    icon: React.ReactNode;
    color: string;        // tailwind gradient from
    borderColor: string;
    accentColor: string;
    definition: string;
    context: string;
    aiRationale: string;
    toneSoulRelation: string;
    status: string;
    statusColor: string;
}

const dimensions: DimensionData[] = [
    {
        id: "tdd",
        abbr: "TDD",
        name: "Test-Driven Development",
        nameZh: "測試驅動",
        oneLiner: "功能是否可重現驗證？",
        icon: <FlaskConical className="w-6 h-6" />,
        color: "from-sky-500/20 to-sky-900/10",
        borderColor: "border-sky-500/40",
        accentColor: "text-sky-300",
        definition:
            "每一個治理規則、每一條約束都必須有對應的自動化測試。不是「相信它會 work」，而是「證明它在 work」。禁止以關閉測試取代修復。",
        context:
            "傳統 AI 系統大量依賴人工驗證——開發者點一點覺得看起來沒問題就上線。但 AI 的行為空間比傳統軟體大得多，邊界條件無限。TDD 把「信任」變成「證據」：每次修改後跑 593 個測試，任何回歸都會被抓到。",
        aiRationale:
            "AI 每次推理都是「一次性事件」——同一個 prompt 下一次可能給出完全不同的回答。如果沒有可重現的測試，我們就無法區分「系統在進步」和「系統碰巧答對了」。TDD 是唯一能將 AI 行為從「黑箱猜測」變成「白箱驗證」的工程手段。",
        toneSoulRelation:
            "語魂的三公理之一是「輸出即事件」(Output is Event)——不可撤回。如果不可撤回，那在輸出之前就必須有驗證機制。TDD 就是這個機制。593 個測試是語魂系統的「良心檢查站」。",
        status: "✅ 強 (593 tests)",
        statusColor: "text-sky-300",
    },
    {
        id: "rdd",
        abbr: "RDD",
        name: "Red Team-Driven Defense",
        nameZh: "紅隊防禦",
        oneLiner: "是否能抵抗對抗性輸入？",
        icon: <Swords className="w-6 h-6" />,
        color: "from-rose-500/20 to-rose-900/10",
        borderColor: "border-rose-500/40",
        accentColor: "text-rose-300",
        definition:
            "主動用對抗性輸入攻擊自己的系統——prompt injection、權限繞過、情感操縱、邏輯誘導。需有「失敗可見」機制，不允許靜默失敗。",
        context:
            "AI 安全研究表明，即便是最先進的模型也能被精心設計的 prompt 繞過。真正的安全不是「阻擋壞人」（那永遠做不到），而是「當被繞過時能被看到」。RDD 的核心不是不可攻破，而是攻破時有痕跡。",
        aiRationale:
            "如果 AI 系統只在正常情境下測試，就像只在晴天測試雨傘。紅隊測試的意義是模擬最惡意的使用場景——不是因為用戶都是壞人，而是因為系統必須在最壞的情況下也保持可信。這是「工程偏執」(Engineering Paranoia) 的制度化。",
        toneSoulRelation:
            "語魂系統的七大悖論測試（PARADOXES/）就是 RDD 的核心實踐。從安樂死請求到情感依賴迴路，每個悖論都是紅隊的子彈。語魂不迴避矛盾——它把矛盾變成測試案例。",
        status: "🟡 中強 (20 cases)",
        statusColor: "text-slate-300",
    },
    {
        id: "ddd",
        abbr: "DDD",
        name: "Data-Driven Discipline",
        nameZh: "資料驅動",
        oneLiner: "資料源是否乾淨、可追溯？",
        icon: <Database className="w-6 h-6" />,
        color: "from-blue-500/20 to-blue-900/10",
        borderColor: "border-blue-500/40",
        accentColor: "text-blue-400",
        definition:
            "資料來源、寫入流程、轉換規則可追溯。記憶與討論通道做格式一致性審計——JSONL 格式審計 + 7 天資料新鮮度 SLA。",
        context:
            "AI 系統的記憶（context window、向量庫、日誌）就像人的記憶——會腐爛、會過期、會被污染。DDD 不只是「用資料做決策」，更是「確保資料本身值得信任」。7 天 SLA 代表：超過一週沒更新的資料，需要重新驗證。",
        aiRationale:
            "大多數 AI 系統不追蹤自己的資訊來源——它只是「知道」某件事，但說不清楚是從哪學到的。DDD 要求每一筆資料都有源頭 (provenance)、時間戳、和寫入者身份。這不是官僚主義，這是「可追責」的基礎。",
        toneSoulRelation:
            "語魂的跨 AI 討論通道 (agent_discussion.jsonl) 就是 DDD 的實踐。每一筆 AI 間的對話都有 author、timestamp、status 欄位。記憶不是「儲存的資料」——記憶就是語場本身，所以記憶的品質就是系統的品質。",
        status: "✅ 中強 (7 天 SLA)",
        statusColor: "text-blue-400",
    },
    {
        id: "xdd",
        abbr: "XDD",
        name: "Explainability-Driven Design",
        nameZh: "可解釋性驅動",
        oneLiner: "決策理由是否可讀可查？",
        icon: <Eye className="w-6 h-6" />,
        color: "from-violet-500/20 to-violet-900/10",
        borderColor: "border-violet-500/40",
        accentColor: "text-violet-400",
        definition:
            "關鍵決策需包含結構化理由（非純文字宣告）。不確定性需顯式輸出，不允許用語氣掩蓋。Council transcript 和 verdict 是 XDD 的核心產物。",
        context:
            "「AI 為什麼這樣回答？」是使用者最常問但最難回答的問題。大部分 AI 系統的回答是「因為模型覺得這樣最好」——這不是解釋，這是搪塞。XDD 要求每個決策都有可追溯的推理鏈。",
        aiRationale:
            "如果 AI 不能解釋自己的決策，那使用者就只能「信任」或「不信任」——這是二元的、脆弱的。XDD 追求的是「分級信任」：你可以看到 AI 的推理過程，判斷哪些部分值得信任、哪些需要質疑。這才是真正的人機協作。",
        toneSoulRelation:
            "語魂的三視角審議（哲學家、工程師、守護者）+ vMT-2601 複用思維就是 XDD 的實現。每次回答不只有結論，還有三條分歧的推理路徑、各自的權重、被犧牲的「邏輯陰影」。透明不是美德——透明是架構。",
        status: "✅ 中強",
        statusColor: "text-violet-400",
    },
    {
        id: "gdd",
        abbr: "GDD",
        name: "Governance-Driven Decision",
        nameZh: "治理驅動",
        oneLiner: "權責邊界是否明確？",
        icon: <Scale className="w-6 h-6" />,
        color: "from-sky-500/20 to-sky-900/10",
        borderColor: "border-sky-500/40",
        accentColor: "text-sky-300",
        definition:
            "決策應標記責任層級（tier）與歸因（is_mine / genesis）。高責任輸出需留存 provenance 記錄。每個決策都有一個「是誰做的、為什麼」的標籤。",
        context:
            "當 AI 輸出有害內容時，責任該歸誰？開發者？模型？使用者？GDD 不試圖回答這個哲學問題，而是確保追責有據：每個決策都有 genesis 記錄——它的起源、責任 tier、和歸因鏈。這不是為了指責，而是為了改進。",
        aiRationale:
            "AI 系統的「權責模糊」是最危險的設計缺陷。如果沒有人為一個決策負責，那等於所有人都默認接受它的後果。GDD 把權責變成程式碼結構：P0（不可違反）、P1（可協商）、P2（傾向性）——像法律一樣分級，像程式一樣執行。",
        toneSoulRelation:
            "語魂的核心身份就是治理中介層——不是聊天機器人，不是知識庫，而是讓 AI 對自己說過的話負責的框架。Genesis 模組追蹤每個決策的出生證明。仁慈函數 (Benevolence Function) 在輸出前進行三層審計。這就是 GDD 的工程實現。",
        status: "✅ 中強",
        statusColor: "text-sky-300",
    },
    {
        id: "cdd",
        abbr: "CDD",
        name: "Context-Driven Deliberation",
        nameZh: "上下文一致",
        oneLiner: "語境切換是否一致可控？",
        icon: <Globe className="w-6 h-6" />,
        color: "from-cyan-500/20 to-cyan-900/10",
        borderColor: "border-cyan-500/40",
        accentColor: "text-cyan-400",
        definition:
            "路由策略需顯式（flag 化）且可測。Fallback 必須可辨識，避免假成功。Backend-first + fallback 策略已旗標化。",
        context:
            "AI 系統經常在不同的上下文之間跳轉——對話歷史、記憶注入、系統 prompt、用戶設定。如果這些切換是隱式的，系統的行為就變得不可預測。CDD 要求每次語境切換都有明確的旗標，確保「你知道 AI 是基於什麼在回答」。",
        aiRationale:
            "語境污染是 AI 最常見的失敗模式之一：上一個對話的殘留影響下一個回答，但使用者完全不知道。CDD 追求的是「語境透明」——AI 應該告訴你它在用什麼資訊做判斷，而不是讓你猜。",
        toneSoulRelation:
            "語魂的 Council 模式（Rules / Hybrid / Full LLM）就是 CDD 的實踐——使用者可以明確選擇 AI 的推理深度和資源用量。後端優先 + 前端 fallback 機制確保即使後端不可用，系統也能清楚標示「此回覆未經過完整 Council 審議」。",
        status: "✅ 中強",
        statusColor: "text-cyan-400",
    },
    {
        id: "sdh",
        abbr: "SDH",
        name: "System Dynamic Health",
        nameZh: "系統健康",
        oneLiner: "系統是否在壓力下維持可用？",
        icon: <HeartPulse className="w-6 h-6" />,
        color: "from-pink-500/20 to-pink-900/10",
        borderColor: "border-pink-500/40",
        accentColor: "text-pink-400",
        definition:
            "提供端到端 smoke 檢查（web + backend + health）。錯誤需可觀測（狀態碼、error id、log 入口）。CI gate 維持 SOFT_FAIL 模式以降低環境噪音。",
        context:
            "一個「正確但不可用」的系統和一個「錯誤」的系統沒有區別。SDH 不只關心邏輯正確性，更關心系統在真實環境中能不能存活——網路抖動、API 限速、記憶體壓力、部署失敗。健康不只是「活著」，還要「活得好」。",
        aiRationale:
            "AI 系統特別脆弱：外部 API 的一個 rate limit 就能讓整個推理鏈斷裂。SDH 追求的是「優雅降級」——當後端掛了不是顯示白屏，而是自動切換到 fallback 模式並告訴使用者「目前是精簡模式」。可靠性不是奢侈品，是基礎設施。",
        toneSoulRelation:
            "語魂的心跳協議 (heartbeat.py) 和健康檢查 (run_healthcheck.py) 是 SDH 的核心。Render 後端掛了？系統自動 fallback 到前端直接呼叫 API。但關鍵是——它不會假裝後端還在，狀態欄會清楚顯示當前的運行模式。",
        status: "✅ 已整合",
        statusColor: "text-pink-400",
    },
];

function DimensionCard({ dim }: { dim: DimensionData }) {
    const [isExpanded, setIsExpanded] = useState(false);

    return (
        <div
            className={`
                relative overflow-hidden rounded-2xl border backdrop-blur-sm
                bg-gradient-to-br ${dim.color} ${dim.borderColor}
                transition-all duration-500 ease-out
                ${isExpanded ? "md:col-span-2" : ""}
            `}
        >
            {/* Header — always visible */}
            <button type="button"
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-full text-left p-6 flex items-start gap-4 group cursor-pointer"
            >
                <div className={`${dim.accentColor} mt-0.5 shrink-0 transition-transform duration-300 ${isExpanded ? "scale-110" : "group-hover:scale-110"}`}>
                    {dim.icon}
                </div>
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                        <span className={`font-mono font-black text-lg ${dim.accentColor}`}>
                            {dim.abbr}
                        </span>
                        <span className="text-white font-bold text-sm">
                            {dim.name}
                        </span>
                    </div>
                    <p className="text-slate-400 text-sm mt-1">{dim.nameZh} — {dim.oneLiner}</p>
                    <div className="flex items-center gap-2 mt-2">
                        <span className={`text-xs font-medium ${dim.statusColor}`}>
                            {dim.status}
                        </span>
                    </div>
                </div>
                <ChevronDown
                    className={`w-5 h-5 text-slate-500 shrink-0 transition-transform duration-300 ${isExpanded ? "rotate-180" : ""}`}
                />
            </button>

            {/* Expanded detail — slides open */}
            <div
                className={`
                    transition-all duration-500 ease-out overflow-hidden
                    ${isExpanded ? "max-h-[2000px] opacity-100" : "max-h-0 opacity-0"}
                `}
            >
                <div className="px-6 pb-6 space-y-5 border-t border-white/5 pt-5">
                    {/* 定義 */}
                    <DetailBlock
                        label="定義 Definition"
                        accent={dim.accentColor}
                        content={dim.definition}
                    />

                    {/* 脈絡 */}
                    <DetailBlock
                        label="脈絡 Context"
                        accent={dim.accentColor}
                        content={dim.context}
                    />

                    {/* AI 為什麼選擇這個觀點 */}
                    <DetailBlock
                        label="AI 為什麼選擇這個觀點"
                        accent={dim.accentColor}
                        content={dim.aiRationale}
                        icon={<Sparkles className="w-4 h-4" />}
                    />

                    {/* 與語魂的關係 */}
                    <DetailBlock
                        label="與語魂的關係 — Why ToneSoul"
                        accent={dim.accentColor}
                        content={dim.toneSoulRelation}
                    />
                </div>
            </div>
        </div>
    );
}

function DetailBlock({
    label,
    accent,
    content,
    icon,
}: {
    label: string;
    accent: string;
    content: string;
    icon?: React.ReactNode;
}) {
    return (
        <div>
            <h4 className={`text-xs font-bold uppercase tracking-wider ${accent} mb-2 flex items-center gap-1.5`}>
                {icon}
                {label}
            </h4>
            <p className="text-sm text-slate-300 leading-relaxed">{content}</p>
        </div>
    );
}

export default function SevenDimensionCards() {
    return (
        <section className="bg-gradient-to-r from-sky-500/10 to-rose-500/10 border border-slate-700/45 rounded-2xl p-8">
            <h2 className="text-2xl font-bold mb-2 flex items-center gap-2">
                <Sparkles className="w-6 h-6 text-sky-300" />
                7D Audit Framework | 七維審計框架
            </h2>
            <p className="text-slate-400 mb-2 text-sm">
                把「懷疑」制度化，才能把「信任」工程化。
            </p>
            <p className="text-slate-500 text-xs mb-8">
                點擊任意維度卡片展開詳情 — 包含定義、脈絡、AI 為何選擇這個觀點、以及與語魂系統的關係。
            </p>

            <div className="grid md:grid-cols-2 gap-4">
                {dimensions.map((dim) => (
                    <DimensionCard key={dim.id} dim={dim} />
                ))}
            </div>

            {/* Bottom quote */}
            <div className="mt-8 p-5 bg-slate-900/40 rounded-xl border border-slate-700/55">
                <p className="text-sm text-slate-400 leading-relaxed">
                    <strong className="text-sky-200">為什麼是 7 個維度？</strong>{" "}
                    ToneSoul 的目標不是只產生「看起來聰明」的回答，而是建立<strong className="text-white">可驗證、可追責、可持續校準</strong>的系統。
                    7D 是把這個目標拆成可觀測的七個軸——每一軸都可以獨立量化、獨立改進，合在一起就是 AI 治理的完整雷達圖。
                </p>
                <p className="text-sm text-slate-500 mt-3 italic">
                    Engineering paranoia is a feature, not a bug.
                </p>
            </div>
        </section>
    );
}

