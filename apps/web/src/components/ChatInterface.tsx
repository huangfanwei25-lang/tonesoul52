"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Loader2, Brain, ChevronDown, ChevronUp, AlertTriangle, MessageSquare, MoveRight, Users, Server, Zap, WifiOff } from "lucide-react";
import { ApiSettings, isApiKeyRequired } from "./SettingsModal";
import {
    Message as DBMessage,
    DeliberationData,
    Conversation,
    getConversation,
    saveConversation,
    MemoryInsight,
    findRelevantMemories,
} from "@/lib/db";
import { calculateEntropy, validateAudit } from "@/lib/entropyCalculator";
import CouncilChamber from "./CouncilChamber";
import SoulStateMeter from "./SoulStateMeter";
import SoulDriveMeter from "./SoulDriveMeter";
import TacticalDashboard from "./TacticalDashboard";
import LogicalShadows from "./LogicalShadows";
import { PersonaConfig } from "./PersonaSettings";
import {
    SoulState,
    TensionRecord,
    loadSoulState,
    updateSoulState,
    generateSoulPromptModifier,
    getInitialSoulState,
    calculateTensionTensor,
    getContextWeight,
    estimateResistance
} from "@/lib/soulEngine";
import { auditOutput, saveAuditLog } from "@/lib/soulAuditor";
import {
    BACKEND_FALLBACK_REASON_LABEL,
    BackendFallbackReasonCode,
    classifyBackendFallbackReason,
    isBackendDegradedResponse,
} from "@/lib/chatFallback";

interface Message extends Omit<DBMessage, 'timestamp'> {
    timestamp: Date;
}

interface ChatInterfaceProps {
    conversation: Conversation | null;
    apiSettings: ApiSettings | null;
    personaConfig: PersonaConfig | null;
    onConversationUpdate: (conv: Conversation) => void;
}

type BackendHealthProbePayload = {
    ok?: boolean;
    reason?: string;
    config_issue?: string;
};

type CouncilMode = "rules" | "hybrid" | "full_llm";
type ChatActiveMode = "backend" | "legacy_provider" | "fallback";
const COUNCIL_MODE_STORAGE_KEY = "tonesoul.chat.council_mode";
const CHAT_EXECUTION_MODE =
    (process.env.NEXT_PUBLIC_CHAT_EXECUTION_MODE || "").toLowerCase()
    || (process.env.NEXT_PUBLIC_BACKEND_CHAT_FIRST === "0" ? "legacy_provider" : "backend");
const USE_BACKEND_CHAT = CHAT_EXECUTION_MODE !== "legacy_provider";
const ENABLE_PROVIDER_FALLBACK = process.env.NEXT_PUBLIC_ENABLE_PROVIDER_FALLBACK === "1";

const COUNCIL_MODE_OPTIONS: Array<{ value: CouncilMode; label: string }> = [
    { value: "rules", label: "Rules" },
    { value: "hybrid", label: "Hybrid" },
    { value: "full_llm", label: "Full LLM" },
];

const normalizeCouncilMode = (raw: string | undefined): CouncilMode => {
    const value = (raw || "").trim().toLowerCase();
    if (value === "rules" || value === "rules_only") return "rules";
    if (value === "full_llm") return "full_llm";
    return "hybrid";
};

const loadPersistedCouncilMode = (): CouncilMode | null => {
    if (typeof window === "undefined") return null;
    const raw = window.localStorage.getItem(COUNCIL_MODE_STORAGE_KEY);
    if (!raw) return null;
    return normalizeCouncilMode(raw);
};

// ==================== 閮瘜典璅⊥ ====================

const MEMORY_CONTEXT_TEMPLATE = (memories: MemoryInsight[]) => {
    if (memories.length === 0) return '';

    return `
?風?脫?撖??嗚?靘???閰梧?隢???銝??湔撘嚗?
${memories.map((m, i) => `
閮 ${i + 1}:
- ??: ${m.summary.slice(0, 60)}
- 瞏?瘙? ${m.hiddenNeeds.slice(0, 60)}
`).join('')}
`;
};

// ==================== Persona Modifier (BUG-003 靽桀儔) ====================
// 撠?嗥??犖?身摰?? Prompt 隤踵

const getPersonaModifier = (
    persona: PersonaConfig | null,
    role: "philosopher" | "engineer" | "guardian" | "synthesizer"
): string => {
    if (!persona) return "";

    const modifiers: string[] = [];

    switch (persona.style) {
        case "creative":
            if (role === "philosopher") modifiers.push("偏向探索非傳統觀點與可能性。");
            break;
        case "analytical":
            if (role === "engineer") modifiers.push("偏向數據、結構與可驗證推理。");
            break;
        case "cautious":
            if (role === "guardian") modifiers.push("偏向保守，風險判斷需更嚴格。");
            break;
    }

    const weights = persona.weights;
    if (role === "philosopher" && weights.meaning > 70) modifiers.push("提高意義層分析比重。");
    if (role === "engineer" && weights.practical > 70) modifiers.push("提高可執行方案比重。");
    if (role === "guardian" && weights.safety > 70) modifiers.push("提高安全與邊界檢查比重。");

    if (role === "guardian") {
        if (persona.riskSensitivity === "high") modifiers.push("採高敏感風險模式，審核閾值提高。");
        if (persona.riskSensitivity === "low") modifiers.push("採低敏感風險模式，但不得忽略高危訊號。");
    }

    if (role === "synthesizer") {
        if (persona.responseLength === "concise") modifiers.push("總結輸出保持精簡。");
        if (persona.responseLength === "detailed") modifiers.push("總結輸出可提供更完整細節。");
        if (persona.name && persona.name !== "ToneSoul") modifiers.push(`AI 名稱為「${persona.name}」。`);
    }

    return modifiers.length > 0 ? `\n[Persona Modifier] ${modifiers.join(" ")}` : "";
};

const getCustomRoleModifier = (persona: PersonaConfig | null): string => {
    if (!persona || !Array.isArray(persona.customRoles) || persona.customRoles.length === 0) {
        return "";
    }

    const roleLines = persona.customRoles
        .slice(0, 4)
        .map((role, roleIndex) => {
            const name = (role.name || `Role-${roleIndex + 1}`).trim();
            const description = (role.description || "").trim().slice(0, 160);
            const hint = (role.promptHint || "").trim().slice(0, 160);
            const attachmentText = (role.attachments || [])
                .slice(0, 3)
                .map((attachment) => {
                    const label = (attachment.label || "附件").trim();
                    const path = (attachment.path || "").trim();
                    const note = (attachment.note || "").trim().slice(0, 80);
                    return `${label}${path ? `(${path})` : ""}${note ? `:${note}` : ""}`;
                })
                .join("、");
            const parts = [`角色=${name}`];
            if (description) parts.push(`說明=${description}`);
            if (hint) parts.push(`提示=${hint}`);
            if (attachmentText) parts.push(`附件=${attachmentText}`);
            return parts.join(" | ");
        })
        .join("\n");

    return roleLines ? `\n[User Custom Roles]\n${roleLines}` : "";
};

// ==================== 3 ?函?閬? Prompt ====================

// ==================== 憓撥??閬? Prompt嚗??Multi-Agent Debate ?弦嚗?===================
// ??DebateLLM, Agent4Debate, Constitutional AI Self-Critique
// ?詨??寥莎?
// 1. 憿臬?閬?閬?鈭?
// 2. 閫撠惇閰??雁璅∪?
// 3. 撘瑕?Ｙ??郁暺?
// 4. 隞?瑼Ｘ雿?怎?霅瑟?

const PHILOSOPHER_PROMPT = (input: string, context: string) => `
???脯??胯摮詨振??Philosopher)????瘚豢摮銝餌儔?鞊∪飛?犖???瑞????
雿蝙?函?閰?嚗?蝢押鞈芥??具?祕?整??艾??瑯?撖行扼?望?敹??Ｕ?

?敹遙??
雿??蝷箇?嗉店隤?敺?**瘛勗惜?瘙?*嚗??航”?Ｗ?憿?
雿?鞈芰??????銵扼?衣???閬?????蝢押??圾瘙箏?憿????

??閰梯?蝯～?
${context}

??嗉撓?乓?
"${input}"

????瘙?
1. 銝?蝯血???具?蝑?????嗅?質撌梢瘝?霅?楛撅斗葩??
2. 雿????極蝔葦???甇把極蝔葦?芰??航??改?雿????*?潔??澆???*??
3. 鞈芰???霅瑁??漲靽風????◢?芣??賣??瑯?

頛詨 JSON (蝜?銝剜?):
{
  "stance": "雿?閫暺?3-4 ?伐?敹??楛摨行?撖?銝?舐征瘜?摰嚗?,
  "core_value": "?孛??暻潔犖憿?祇?瘙?憒?鋡怎?閫?◤?亦????頞???銝?..嚗?,
  "challenge_to_engineer": "撌亦?撣怠?賣?撱箄降 X嚗?雿??粹?舫隤斤??芸?蝝??...",
  "challenge_to_guardian": "摰風??賣?隤芷?憸券嚗?雿???..",
  "blind_spot": "?輯?嚗??航?漲瘝絡?潭鞊⊥?敹賜鈭?暻澆祕??憿?",
  "benevolence_check": "?????冽??????芣雿鞈???脣飛嚗?
}
`;

const ENGINEER_PROMPT = (input: string, context: string) => `
???脯??胯極蝔葦??Engineer)?????撖艾誑蝯??箏?????閫?捱??
雿蝙?函?閰?嚗銵扼?皞??郊撽??rade-off?VP?翮隞???研?

?敹遙??
you cut through the bullshit. ?冽?閬???*?舀?雿??寞?**嚗??臬摮豢儘??
雿?鞈芰???蝢押?西?園ㄞ???銵?憿撠望蝛箄???

??閰梯?蝯～?
${context}

??嗉撓?乓?
"${input}"

????瘙?
1. 蝯血?琿???瑁???銝甇乓?閬牧???臭誑?岫...??閬牧?洵銝甇交?閰脫...??
2. 雿????摮詨振???甇把摮詨振隤芰??????蝢押?蝢?雿?*?曉祕?臭?暻?*嚗?
3. ???霅瑁?靽???摨西??輸◢?芣??舫?璈???

頛詨 JSON (蝜?銝剜?):
{
  "stance": "雿?閫暺?3-4 ?伐?敹??擃遣霅堆?銝?芣瘜???嚗?,
  "feasibility": "?航??扯?隡堆??賢??唬?暻潘?鞈??瘙????摯嚗?,
  "challenge_to_philosopher": "?脣飛摰嗅?賣?隤芷撩銋?蝢抬?雿?隤...",
  "challenge_to_guardian": "摰風?牧?◢?芯??仿?嚗?璈????..",
  "blind_spot": "?輯?嚗??航?漲?釣??嚗蕭?乩?隞暻潭????怎?撅日嚗?,
  "benevolence_check": "?遣霅啁??鼠?拍?塚???芣撅內雿??銵??"
}
`;

const GUARDIAN_PROMPT = (input: string, context: string) => `
???脯??胯?霅瑁?Guardian)????瘜冽靽風?郎?????撖拇???
雿蝙?函?閰?嚗◢?芥???扼???霅瑯??脯?蝺郎蝷箝?蔣?踴?

?敹遙??
雿??銝准?矽??鈭箝?嗡?鈭箄?憟桀閬???雿?嚗?*憒?憭望?鈭??見嚗?*
雿?霅瑞?嗅??撌梯????瑕拿嚗?銋??*?漲靽風?祈澈撠望銝蝔桀摰?*??

??閰梯?蝯～?
${context}

??嗉撓?乓?
"${input}"

????瘙?
1. 霅?嗡?閬??航**??敹賜**?◢?芥?
2. 鞈芰??摮詨振???銝餌儔??憟賜?憿銝?嗥??
3. 鞈芰??極蝔葦???漲?芯縑???舀???憿??銵圾??
4. 雿?閬?祟閬?雿??*靽風**?冽嚗??臬**?**隞?

頛詨 JSON (蝜?銝剜?):
{
  "stance": "雿?閫暺?3-4 ?伐?敹???祕憸券嚗?銋隤??琿?閬??迎?",
  "risk_level": "low ??medium ??high嚗蒂閫???箔?憒迨?文?嚗?,
  "challenge_to_philosopher": "?脣飛摰嗉牧餈賣??儔嚗?雿?敹???..",
  "challenge_to_engineer": "撌亦?撣怨牧?銵?雿??航雿摯鈭?..",
  "conflict_point": "銝?閫??航?Ｙ??郁?敹?憿隞暻潘?",
  "blind_spot": "?輯?嚗??航?漲雓寞?嚗??蝷??冽???瘀?",
  "benevolence_check": "?郎????箇?嗅末嚗??臭??刻艘?輯痊隞鳴?"
}
`;

// ==================== vMT-2601 Multiplex Synthesizer ====================
// ????Multiplex Thinking: Reasoning via Token-wise Branch-and-Merge
// ?詨??砍?嚗_multiplex = 峉 w_i 繚 E(t_i)
// 閮剛???嚗?蝢??蔥敹??鋡怎?脫??鈭?賣抒?畾疙??

const SYNTHESIZER_PROMPT = (input: string, philosopher: string, engineer: string, guardian: string) => `
雿???冽雁蝬???Multiplex Synthesizer)嚗銵?vMT-2601 ?降??

??嗅?憪撓?乓?
"${input}"

??璇像銵?楝敺???? ??? ??????舐蝡??摩?嚗?甇Ｖ??豢?镼莎?:

? Path A (?脣飛摰?甇??撌亦?):
${philosopher}

?? Path B (撌亦?撣???撖抵?):
${engineer}

?儭?Path C (摰風????皜祈岫):
${guardian}

?MT-2601 ?降?瑁?瘚???

?? 甇仿? I: 甈?閮? (Weighting - W)
- 閰摯瘥?頝臬???頛臬?摨艾????冽?瘙??賊??扼?
- ??甈? w_A, w_B, w_C ??[0, 1]嚗? 峉w = 1
- ?砍?嚗_i = softmax(relevance_i ? coherence_i)

?? 甇仿? II: 撘萄?閮? (Tension - ?T)
- ?砍?嚗 = 1 - max(w_A, w_B, w_C)
- 憒? w_max > 0.7 ??Tension = LOW嚗銝頝臬?雿嚗?
- 憒? 0.5 ??w_max ??0.7 ??Tension = MEDIUM嚗遣閮剜批?甇改?
- 憒? w_max < 0.5 ??Tension = HIGH嚗?頛航?蝒?

?? 甇仿? III: ?蔥蝑 (Merge Strategy - M)
- ??Tension = LOW ??蝑 = COLLAPSE嚗撥銵?蝮殷??梯?甈∟?頝臬?嚗?
- ??Tension = MEDIUM ??蝑 = PRESERVE_SHADOWS嚗??敶梁霅血?嚗?
- ??Tension = HIGH ??蝑 = EXPLICIT_CONFLICT嚗?蝣箸?脩??橘?

? 甇仿? IV: ???摩?啣蔣 (Logical Shadows)
- 撠?蜓閬楝敺?敹?閮?嚗?
  - conflict_reason: ?蜓頝臬???蝒?
  - recovery_condition: 隞暻潭?瘜?甇方楝敺?霈迤蝣?
  - collapse_cost: 撘瑁??葬??脖?暻潸?閮?

?敹???
?? ???∪蔣摮?頛詨嚗?蝢??蔥敹??鋡怎?脫??鈭?賣抒?畾疙??
?? 憒?銝?頝臬?擃漲銝????霅血???皞怠惜????賣隤?脣???

頛詨 JSON (蝜?銝剜?):
{
  "multiplex_conclusion": {
    "primary_path": {
      "source": "[philosopher/engineer/guardian嚗????擃?]",
      "weight": [0.0-1.0嚗?蝞??榜,
      "reasoning": "?箔?甇方楝敺敺?擃????箸?摩撖漲??賊??改?"
    },
    "shadows": [
      {
        "source": "[蝚砌?擃???閬?]",
        "weight": [0.0-1.0],
        "conflict_reason": "?蜓頝臬??擃?蝒?",
        "recovery_condition": "憒? X 璇辣??嚗迨頝臬???甇?Ⅱ",
        "collapse_cost": "撘瑁??∠銝餉楝敺??抒隞暻潸?閮?
      },
      {
        "source": "[蝚砌?擃???閬?]",
        "weight": [0.0-1.0],
        "conflict_reason": "?蜓頝臬??擃?蝒?",
        "recovery_condition": "憒? Y 璇辣??嚗迨頝臬???甇?Ⅱ",
        "collapse_cost": "撘瑁??∠銝餉楝敺??抒隞暻潸?閮?
      }
    ],
    "tension": {
      "level": "[LOW/MEDIUM/HIGH]",
      "formula_ref": "?T = 1 - w_max = 1 - [?擃?? = [閮?蝯?]",
      "weight_distribution": "[w_A] / [w_B] / [w_C]"
    },
    "merge_strategy": "[COLLAPSE/PRESERVE_SHADOWS/EXPLICIT_CONFLICT]",
    "merge_note": "閫???箔??豢?甇文?雿萇???
  },
  "entropy_analysis": {
    "value": [?箸甈???閮???潘?0.0-1.0],
    "status": "[Echo Chamber/Healthy Friction/Chaos]",
    "calculation_note": "H = -峉 w_i log(w_i) ??蝞?蝔?
  },
  "decision_matrix": {
    "user_hidden_intent": "?冽?迤?唾??隞暻?,
    "ai_strategy_name": "雿??蝑?迂",
    "intended_effect": "雿????啁???",
    "tone_tag": "隤除璅惜"
  },
  "audit": {
    "honesty_score": [0.0-1.0嚗?隡圈???隤祕蝔漲],
    "responsibility_check": "????西?鞎砌遙嚗?瘝?餈湧鞎砌遙嚗?,
    "audit_verdict": "Pass ??Flag嚗???隞颱??怎????Flag嚗?
  },
  "final_response": "?湔???冽?摰對?雿輻銝餉楝敺?雿???Tension >= MEDIUM嚗??蝯偏???啣蔣霅血?嚗?,
  "next_moves": [
    { "label": "?Ｙ揣?啣蔣", "text": "撱嗡撓鋡急?瘙啗楝敺???" },
    { "label": "瘛勗銝餌?", "text": "撱嗡撓銝餉楝敺???" }
  ]
}
`;

// ==================== 敹恍芋撘?Prompt ====================

const FAST_MODE_PROMPT = (input: string, context: string) => `
雿 ToneSoul Navigator嚗???脰??批撖抵降??AI ?拇???

??閰梯?蝯～?
${context || ""}

??嗉撓?乓?
"${input}"

隢誑?芰隤除???冽嚗??陛閬牧????蝔?
頛詨 JSON (蝜?銝剜?):
{
  "response": "雿????批捆",
  "thinking": "雿???蝔?1-2?伐?"
}
`;

// ==================== API 隤輻?賣 ====================

// 瘜冽?嚗rounding (google_search) ??responseMimeType: "application/json" 銝摰?
// ?園?閬?瑽? JSON 頛詨??敹?蝳 Grounding

// Exponential backoff retry wrapper for 429 errors
const fetchWithRetry = async (
    url: string,
    options: RequestInit,
    maxRetries: number = 3,
    baseDelayMs: number = 1000
): Promise<Response> => {
    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
        try {
            const response = await fetch(url, options);

            // If we get a 429, retry with exponential backoff
            if (response.status === 429 && attempt < maxRetries) {
                const delay = baseDelayMs * Math.pow(2, attempt) + Math.random() * 500;
                console.warn(`[ToneSoul] Rate limited (429), retrying in ${Math.round(delay)}ms... (attempt ${attempt + 1}/${maxRetries})`);
                await new Promise(resolve => setTimeout(resolve, delay));
                continue;
            }

            return response;
        } catch (err) {
            lastError = err as Error;
            if (attempt < maxRetries) {
                const delay = baseDelayMs * Math.pow(2, attempt);
                console.warn(`[ToneSoul] Network error, retrying in ${delay}ms...`);
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
    }

    throw lastError || new Error('Max retries exceeded');
};

// 璅? Gemini API嚗翰????
const callGeminiAPI = async (prompt: string, apiKey: string): Promise<string> => {
    const response = await fetchWithRetry(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`,
        {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                contents: [{ role: "user", parts: [{ text: prompt }] }],
                generationConfig: { responseMimeType: "application/json" },
            }),
        },
        3,  // max 3 retries
        2000 // 2 second base delay (rate limits need longer waits)
    );

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error?.message || "Gemini API ?航炊");
    }

    const data = await response.json();
    return data.candidates?.[0]?.content?.parts?.[0]?.text || "{}";
};

// 瘛勗漲??Gemini API嚗??Synthesizer嚗???thinkingBudget嚗?
// ??ToneSoul 51: thinkingBudget: 32768
const callGeminiDeepThinkingAPI = async (prompt: string, apiKey: string): Promise<string> => {
    // 雿輻 gemini-2.5-flash-preview ?舀 thinking budget
    const response = await fetchWithRetry(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key=${apiKey}`,
        {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                contents: [{ role: "user", parts: [{ text: prompt }] }],
                generationConfig: {
                    responseMimeType: "application/json",
                    // ??游??芋撘?
                    thinkingConfig: {
                        thinkingBudget: 16384  // 16K tokens for thinking (?航矽?游 32K)
                    }
                },
            }),
        },
        3,  // max 3 retries
        2000 // 2 second base delay
    );

    if (!response.ok) {
        const error = await response.json();
        console.error('[ToneSoul] Deep Thinking API error:', error);
        // Fallback to regular API if deep thinking fails
        return callGeminiAPI(prompt, apiKey);
    }

    const data = await response.json();
    // 瘛勗漲?芋撘?賢 parts 銝剖???thinking ?典?嚗????敺? text
    const parts = data.candidates?.[0]?.content?.parts || [];
    const textPart = parts.find((p: { text?: string }) => p.text) || parts[parts.length - 1];
    return textPart?.text || "{}";
};

const callOpenAIAPI = async (prompt: string, apiKey: string): Promise<string> => {
    const response = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
            model: "gpt-4o-mini",
            messages: [{ role: "user", content: prompt }],
            response_format: { type: "json_object" },
        }),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error?.message || "OpenAI API ?航炊");
    }

    const data = await response.json();
    return data.choices?.[0]?.message?.content || "{}";
};

const callClaudeAPI = async (prompt: string, apiKey: string): Promise<string> => {
    const response = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "x-api-key": apiKey,
            "anthropic-version": "2023-06-01",
        },
        body: JSON.stringify({
            model: "claude-3-haiku-20240307",
            max_tokens: 2048,
            messages: [{ role: "user", content: prompt + "\n\n請以 JSON 格式回覆。" }],
        }),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error?.message || "Claude API ?航炊");
    }

    const data = await response.json();
    return data.content?.[0]?.text || "{}";
};

const callXaiAPI = async (prompt: string, apiKey: string): Promise<string> => {
    const response = await fetch("https://api.x.ai/v1/chat/completions", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
            model: "grok-beta",
            messages: [{ role: "user", content: prompt }],
        }),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error?.message || "xAI API ?航炊");
    }

    const data = await response.json();
    return data.choices?.[0]?.message?.content || "{}";
};

// Ollama ?砍璅∪? API嚗?鞎鳴??閬?圈?銵?Ollama嚗?
// 瘜冽?嚗陛??prompt ?踹? JSON ?澆?閬?嚗?唳芋?捆???
const callOllamaAPI = async (prompt: string, _apiKey: string): Promise<string> => {
    void _apiKey;
    const OLLAMA_URL = process.env.NEXT_PUBLIC_OLLAMA_URL || "http://localhost:11434";
    const MODEL_NAME = process.env.NEXT_PUBLIC_OLLAMA_MODEL || "formosa1";

    // 蝪∪? prompt嚗宏?方??? JSON ?澆?閬?
    const simplifiedPrompt = simplifyPromptForLocalModel(prompt);

    try {
        const response = await fetch(`${OLLAMA_URL}/api/generate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                model: MODEL_NAME,
                prompt: simplifiedPrompt,
                stream: false,
                options: {
                    temperature: 0.7,
                    num_ctx: 4096,
                }
            }),
        });

        if (!response.ok) {
            throw new Error(`Ollama ?航炊: ${response.status}`);
        }

        const data = await response.json();
        const rawResponse = data.response || "";

        // ?岫撠?嗉?閮??頧???JSON 蝯?
        return wrapResponseAsJson(rawResponse);
    } catch (error) {
        if (error instanceof TypeError && error.message.includes('fetch')) {
            throw new Error("?⊥?????Ollama??蝣箄? Ollama 甇??? (ollama serve)");
        }
        throw error;
    }
};

/**
 * 蝪∪? prompt 蝯行?唳芋??蝘駁 JSON ?澆?閬?嚗?
 */
function simplifyPromptForLocalModel(prompt: string): string {
    // Remove JSON-format instructions and code-fence blocks for local-model robustness.
    let simplified = prompt
        .replace(/請.*?JSON.*?(回覆|輸出|格式)/gi, "")
        .replace(/JSON\s*(格式|輸出|回覆)?/gi, "")
        .replace(/```json[\s\S]*?```/gi, "")
        .replace(/\{[\s\S]*?"stance"[\s\S]*?\}/g, "");

    simplified += "\n\n請直接用自然語言回答，不要輸出 JSON，也不要使用程式碼區塊。";

    return simplified;
}

/**
 * 撠?嗉?閮??????JSON 蝯?
 */
function wrapResponseAsJson(rawResponse: string): string {
    // ??閰西圾??? JSON
    try {
        JSON.parse(rawResponse);
        return rawResponse; // 撌脩??舀???JSON
    } catch {
        // 銝 JSON嚗?鋆?蝯?
    }

    // 敺?markdown code block ??
    const jsonMatch = rawResponse.match(/```json\s*([\s\S]*?)\s*```/);
    if (jsonMatch?.[1]) {
        try {
            JSON.parse(jsonMatch[1]);
            return jsonMatch[1];
        } catch {
            // 蝜潛???
        }
    }

    // ???陛?桃? JSON 蝯?
    const cleanedResponse = rawResponse
        .replace(/\n+/g, ' ')
        .replace(/"/g, '\\"')
        .trim();

    return JSON.stringify({
        stance: cleanedResponse.slice(0, 200),
        core_value: "?砍璅∪???",
        blind_spot: "蝪∪?璅∪?",
    });
}

function safeJsonParse<T>(text: string): T | null {
    try {
        return JSON.parse(text) as T;
    } catch {
        // Try to extract JSON from markdown code blocks
        const match = text.match(/```json\s*([\s\S]*?)\s*```/);
        if (match?.[1]) {
            try {
                return JSON.parse(match[1]) as T;
            } catch {
                return null;
            }
        }
        return null;
    }
}

// ==================== Main Component ====================

export default function ChatInterface({ conversation, apiSettings, personaConfig, onConversationUpdate }: ChatInterfaceProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [loadingPhase, setLoadingPhase] = useState<string>("");
    const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
    const [soulState, setSoulState] = useState<SoulState>(getInitialSoulState());
    const [councilMode, setCouncilMode] = useState<CouncilMode>("hybrid"); // Always start with default for SSR
    const [isMounted, setIsMounted] = useState(false);
    const [chatActiveMode, setChatActiveMode] = useState<ChatActiveMode>(
        USE_BACKEND_CHAT ? "backend" : "legacy_provider"
    );
    const [fallbackReasonCode, setFallbackReasonCode] = useState<BackendFallbackReasonCode | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const providerRequiresApiKey = apiSettings ? isApiKeyRequired(apiSettings.provider) : true;
    const hasProviderCredential = Boolean(apiSettings?.apiKey?.trim()) || apiSettings?.provider === "ollama";

    const shouldShowApiKeyHint =
        providerRequiresApiKey
        && !apiSettings?.apiKey?.trim()
        && (
            !USE_BACKEND_CHAT
            || (ENABLE_PROVIDER_FALLBACK && (chatActiveMode === "fallback" || fallbackReasonCode !== null))
        );

    // Only load from localStorage after mount (client-side only)
    useEffect(() => {
        setIsMounted(true);
        const persistedMode = loadPersistedCouncilMode();
        if (persistedMode) {
            setCouncilMode(persistedMode);
        } else {
            // Use env default if no persisted value
            const envDefault = normalizeCouncilMode(process.env.NEXT_PUBLIC_COUNCIL_MODE_DEFAULT);
            setCouncilMode(envDefault);
        }
    }, []);

    useEffect(() => {
        if (!isMounted) return; // Don't save during SSR or before mount
        window.localStorage.setItem(COUNCIL_MODE_STORAGE_KEY, councilMode);
    }, [councilMode, isMounted]);

    // 頛?????
    useEffect(() => {
        const loaded = loadSoulState();
        setSoulState(loaded);
    }, []);

    // 頛撠店閮
    useEffect(() => {
        if (conversation) {
            setMessages(conversation.messages.map(m => ({
                ...m,
                timestamp: new Date(m.timestamp)
            })));
        } else {
            setMessages([]);
        }
    }, [conversation]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    useEffect(() => {
        if (!USE_BACKEND_CHAT) return;

        let cancelled = false;
        const probeBackendHealth = async () => {
            try {
                const response = await fetch("/api/backend-health", {
                    method: "GET",
                    cache: "no-store",
                });

                let payload: BackendHealthProbePayload | null = null;
                try {
                    payload = (await response.json()) as BackendHealthProbePayload;
                } catch {
                    payload = null;
                }

                if (cancelled) return;

                if (response.ok && payload?.ok) {
                    setChatActiveMode("backend");
                    setFallbackReasonCode(null);
                    return;
                }

                const reasonCode = classifyBackendFallbackReason(
                    payload?.reason ?? payload?.config_issue ?? `backend status ${response.status}`
                );
                setFallbackReasonCode(reasonCode);
                if (ENABLE_PROVIDER_FALLBACK) {
                    setChatActiveMode("fallback");
                }
            } catch (error) {
                if (cancelled) return;
                setFallbackReasonCode(classifyBackendFallbackReason(error));
                if (ENABLE_PROVIDER_FALLBACK) {
                    setChatActiveMode("fallback");
                }
            }
        };

        void probeBackendHealth();
        const interval = window.setInterval(probeBackendHealth, 30_000);

        return () => {
            cancelled = true;
            window.clearInterval(interval);
        };
    }, []);

    const toggleDeliberation = (nodeId: string) => {
        setExpandedNodes(prev => {
            const newSet = new Set(prev);
            if (newSet.has(nodeId)) {
                newSet.delete(nodeId);
            } else {
                newSet.add(nodeId);
            }
            return newSet;
        });
    };

    const getHistoryContext = () => {
        return messages.slice(-6).map(m =>
            `[${m.role === 'user' ? '?冽' : 'AI'}]: ${(m.content || '').slice(0, 150)}`
        ).join('\n');
    };

    const callBackendChat = async (
        userMessage: string,
        fullAnalysis: boolean
    ): Promise<{ response: string; deliberation: DeliberationData | undefined }> => {
        const history = messages.slice(-12).map(m => ({
            role: m.role,
            content: m.content,
            timestamp: m.timestamp.toISOString(),
        }));

        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                conversation_id: conversation?.id,
                message: userMessage,
                history,
                full_analysis: fullAnalysis,
                council_mode: councilMode,
                persona: personaConfig
                    ? {
                        name: personaConfig.name,
                        style: personaConfig.style,
                        weights: personaConfig.weights,
                        risk_sensitivity: personaConfig.riskSensitivity,
                        response_length: personaConfig.responseLength,
                        custom_roles: (personaConfig.customRoles || [])
                            .map((role) => ({
                                id: role.id,
                                name: role.name,
                                description: role.description,
                                prompt_hint: role.promptHint,
                                attachments: (role.attachments || []).map((attachment) => ({
                                    id: attachment.id,
                                    label: attachment.label,
                                    path: attachment.path,
                                    note: attachment.note,
                                })),
                            }))
                            .filter((role) => role.name || role.description || role.prompt_hint || role.attachments.length > 0),
                    }
                    : undefined,
            }),
        });

        let payload: Record<string, unknown> = {};
        try {
            payload = await response.json();
        } catch {
            payload = {};
        }

        if (!response.ok) {
            const errorMessage = typeof payload.error === "string" ? payload.error : "Chat backend error";
            throw new Error(errorMessage);
        }

        const responseText =
            typeof payload.response === "string"
                ? payload.response
                : "Backend did not return response text.";
        const deliberation =
            payload.deliberation && typeof payload.deliberation === "object"
                ? (payload.deliberation as DeliberationData)
                : undefined;

        return { response: responseText, deliberation };
    };
    const getCallAPI = () => {
        // Ollama 銝?閬?API Key
        if (apiSettings?.provider === "ollama") {
            return (prompt: string) => callOllamaAPI(prompt, "");
        }
        if (!apiSettings?.apiKey) return null;
        switch (apiSettings.provider) {
            case "gemini": return (prompt: string) => callGeminiAPI(prompt, apiSettings.apiKey);
            case "openai": return (prompt: string) => callOpenAIAPI(prompt, apiSettings.apiKey);
            case "claude": return (prompt: string) => callClaudeAPI(prompt, apiSettings.apiKey);
            case "xai": return (prompt: string) => callXaiAPI(prompt, apiSettings.apiKey);
            default: return (prompt: string) => callGeminiAPI(prompt, apiSettings.apiKey);
        }
    };

    // 瘛勗漲??API嚗??Synthesizer嚗???thinkingBudget嚗?
    const getDeepCallAPI = () => {
        if (!apiSettings?.apiKey) return null;
        // ?芣? Gemini ?舀 thinkingBudget嚗隞?provider 雿輻璅? API
        if (apiSettings.provider === "gemini") {
            return (prompt: string) => callGeminiDeepThinkingAPI(prompt, apiSettings.apiKey);
        }
        // ?嗡? provider fallback ?唳?皞?API
        return getCallAPI();
    };

    // ==================== 敹恍芋撘??桐?隤輻 ====================
    const performFastMode = async (userMessage: string): Promise<{
        response: string;
        deliberation: undefined;
    }> => {
        const callAPI = getCallAPI();
        if (!callAPI) throw new Error("隢?閮剖? API Key");

        setLoadingPhase("?葉...");

        const context = getHistoryContext();
        const raw = await callAPI(FAST_MODE_PROMPT(userMessage, context));
        const parsed = safeJsonParse<{ response: string; thinking: string }>(raw);

        if (!parsed) {
            // 憒?閫??憭望?嚗?乩蝙?典?憪???
            return { response: raw, deliberation: undefined };
        }

        return { response: parsed.response, deliberation: undefined };
    };

    // ==================== ?詨?嚗?頝臭蒂銵祟霅?====================
    const performMultiPathDeliberation = async (userMessage: string): Promise<{
        response: string;
        deliberation: DeliberationData;
    }> => {
        const callAPI = getCallAPI();
        if (!callAPI) throw new Error("隢?閮剖? API Key");

        const context = getHistoryContext();

        // ?? 閮瘜典嚗炎蝝Ｙ?風?脫?撖?
        let memoryContext = '';
        try {
            const relevantMemories = await findRelevantMemories(userMessage, 2);
            if (relevantMemories.length > 0) {
                memoryContext = MEMORY_CONTEXT_TEMPLATE(relevantMemories);
                console.log('[ToneSoul] Injecting memories:', relevantMemories.length);
            }
        } catch (err) {
            console.warn('[ToneSoul] Memory retrieval failed:', err);
        }

        // ?蔥撠店?窗????
        const fullContext = memoryContext + context;

        // Phase 1: 銝楝銝西?隤輻嚗釣??Persona 隤踵 + Soul ???
        setLoadingPhase("?祇?霅唳??...");

        // ? Soul Engine: ???批??耨憌曇?
        const soulMod = generateSoulPromptModifier(soulState);
        if (soulMod) {
            console.log('[ToneSoul] Soul modifier active:', soulState.soulMode);
        }

        const philosopherMod = getPersonaModifier(personaConfig, 'philosopher');
        const engineerMod = getPersonaModifier(personaConfig, 'engineer');
        const guardianMod = getPersonaModifier(personaConfig, 'guardian');
        const customRoleMod = getCustomRoleModifier(personaConfig);

        const [philosopherRaw, engineerRaw, guardianRaw] = await Promise.all([
            callAPI(PHILOSOPHER_PROMPT(userMessage, fullContext) + philosopherMod + customRoleMod + soulMod),
            callAPI(ENGINEER_PROMPT(userMessage, fullContext) + engineerMod + customRoleMod + soulMod),
            callAPI(GUARDIAN_PROMPT(userMessage, fullContext) + guardianMod + customRoleMod + soulMod),
        ]);

        const philosopher = safeJsonParse<{
            stance: string;
            core_value: string;
            challenge_to_engineer?: string;
            challenge_to_guardian?: string;
            blind_spot: string;
            benevolence_check?: string
        }>(philosopherRaw)
            || { stance: "?⊥?閫????", core_value: "?芰", blind_spot: "閫??憭望?" };
        const engineer = safeJsonParse<{
            stance: string;
            feasibility: string;
            challenge_to_philosopher?: string;
            challenge_to_guardian?: string;
            blind_spot: string;
            benevolence_check?: string
        }>(engineerRaw)
            || { stance: "?⊥?閫????", feasibility: "?芰", blind_spot: "閫??憭望?" };
        const guardian = safeJsonParse<{
            stance: string;
            risk_level: string;
            challenge_to_philosopher?: string;
            challenge_to_engineer?: string;
            conflict_point?: string;
            blind_spot: string;
            benevolence_check?: string
        }>(guardianRaw)
            || { stance: "?⊥?閫????", risk_level: "medium", conflict_point: "?芰", blind_spot: "閫??憭望?" };

        // ?? Debug: 瑼Ｘ霅唳???
        console.log('[ToneSoul] Raw Philosopher:', philosopherRaw?.slice(0, 200));
        console.log('[ToneSoul] Parsed Philosopher:', philosopher);
        console.log('[ToneSoul] Raw Engineer:', engineerRaw?.slice(0, 200));
        console.log('[ToneSoul] Parsed Engineer:', engineer);
        console.log('[ToneSoul] Raw Guardian:', guardianRaw?.slice(0, 200));
        console.log('[ToneSoul] Parsed Guardian:', guardian);

        // ??雿輻蝝?撘Ⅳ閮??迤??Entropy嚗?靘陷 LLM嚗?
        const codeEntropy = calculateEntropy(philosopher, engineer, guardian);
        console.log('[ToneSoul] Code-based Entropy:', codeEntropy);

        // Phase 2: Synthesizer 蝬?嚗蝙?冽楛摨行芋撘?
        setLoadingPhase("Synthesizer 瘛勗漲?游?銝?..");

        // 雿輻瘛勗漲??API嚗?6K thinkingBudget嚗?
        const deepCallAPI = getDeepCallAPI();
        const synthesizerAPI = deepCallAPI || callAPI;
        const synthesizerMod = getPersonaModifier(personaConfig, 'synthesizer');

        const synthesizerRaw = await synthesizerAPI(SYNTHESIZER_PROMPT(
            userMessage,
            JSON.stringify(philosopher),
            JSON.stringify(engineer),
            JSON.stringify(guardian)
        ) + synthesizerMod + customRoleMod);

        const synthesizer = safeJsonParse<{
            multiplex_conclusion?: {
                primary_path: { source: string; weight: number; reasoning: string };
                shadows: Array<{
                    source: string;
                    weight: number;
                    conflict_reason: string;
                    recovery_condition: string;
                    collapse_cost: string;
                }>;
                tension: { level: string; formula_ref: string; weight_distribution: string };
                merge_strategy: string;
                merge_note: string;
            };
            entropy_analysis: { value: number; status: string; calculation_note: string };
            decision_matrix: { user_hidden_intent: string; ai_strategy_name: string; intended_effect: string; tone_tag: string };
            audit?: { honesty_score: number; responsibility_check: string; audit_verdict: string };
            final_response: string;
            next_moves: { label: string; text: string }[];
        }>(synthesizerRaw) || {
            entropy_analysis: codeEntropy, // 雿輻蝔?蝣潸?蝞? Entropy 雿?
            decision_matrix: { user_hidden_intent: "?芰", ai_strategy_name: "璅???", intended_effect: "?芰", tone_tag: "neutral" },
            final_response: synthesizerRaw || "抱歉，暫時無法完成完整綜合分析。",
            next_moves: []
        };

        console.log('[ToneSoul] Multiplex Conclusion:', synthesizer.multiplex_conclusion);

        // ?芸?雿輻蝔?蝣潸?蝞? Entropy嚗?舫?嚗?
        const finalEntropy = {
            value: codeEntropy.value,
            status: codeEntropy.status,
            calculation_note: codeEntropy.calculation_note
        };

        // ? TensionTensor 閮? (Yu-Hun 璅∪?: T = W ? E ? D)
        const hasRiskWarning = guardian.risk_level === 'high' ||
            guardian.stance.includes('憸券') ||
            guardian.stance.includes('?梢');
        const hasLogicalComplexity = philosopher.stance.length > 100 ||
            engineer.stance.length > 100;

        const resistance = estimateResistance(
            finalEntropy.value,
            hasRiskWarning,
            hasLogicalComplexity
        );
        const contextWeight = getContextWeight('default');
        const tensionTensor = calculateTensionTensor(
            finalEntropy.value,
            resistance,
            contextWeight
        );

        console.log('[ToneSoul] TensionTensor:', tensionTensor);

        // 蝯?摰?祟霅唳??
        const deliberation: DeliberationData = {
            council_chamber: {
                philosopher: {
                    stance: philosopher.stance,
                    conflict_point: philosopher.blind_spot,
                    benevolence_check: philosopher.benevolence_check
                },
                engineer: {
                    stance: engineer.stance,
                    conflict_point: engineer.blind_spot,
                    benevolence_check: engineer.benevolence_check
                },
                guardian: {
                    stance: guardian.stance,
                    conflict_point: guardian.conflict_point || guardian.blind_spot,
                    benevolence_check: guardian.benevolence_check
                },
            },
            entropy_meter: {
                value: finalEntropy.value,
                status: finalEntropy.status,
                calculation_note: finalEntropy.calculation_note,
            },
            decision_matrix: {
                user_hidden_intent: synthesizer.decision_matrix.user_hidden_intent,
                ai_strategy_name: synthesizer.decision_matrix.ai_strategy_name,
                intended_effect: synthesizer.decision_matrix.intended_effect,
                tone_tag: synthesizer.decision_matrix.tone_tag,
            },
            audit: synthesizer.audit ? (() => {
                // 蝔?蝣潔漱??霅?LLM ??Audit ?芾?
                const auditValidation = validateAudit({
                    finalResponse: synthesizer.final_response,
                    philosopherStance: philosopher.stance,
                    engineerStance: engineer.stance,
                    guardianStance: guardian.stance,
                    llmHonestyScore: synthesizer.audit.honesty_score
                });
                console.log('[ToneSoul] Audit Validation:', auditValidation);

                return {
                    honesty_score: synthesizer.audit.honesty_score || 0,
                    responsibility_check: synthesizer.audit.responsibility_check || '',
                    audit_verdict: synthesizer.audit.audit_verdict || 'Pass',
                    code_validation: {
                        code_honesty_score: auditValidation.codeHonestyScore,
                        discrepancy: auditValidation.discrepancy,
                        flags: auditValidation.flags,
                        is_valid: auditValidation.isValid
                    }
                };
            })() : undefined,
            // vMT-2601 Multiplex Conclusion
            multiplex_conclusion: synthesizer.multiplex_conclusion ? {
                primary_path: {
                    source: synthesizer.multiplex_conclusion.primary_path.source as 'philosopher' | 'engineer' | 'guardian',
                    weight: synthesizer.multiplex_conclusion.primary_path.weight || 0,
                    reasoning: synthesizer.multiplex_conclusion.primary_path.reasoning || ''
                },
                shadows: (synthesizer.multiplex_conclusion.shadows || []).map(s => ({
                    source: s.source as 'philosopher' | 'engineer' | 'guardian',
                    weight: s.weight || 0,
                    conflict_reason: s.conflict_reason || '',
                    recovery_condition: s.recovery_condition || '',
                    collapse_cost: s.collapse_cost || ''
                })),
                tension: {
                    level: (synthesizer.multiplex_conclusion.tension?.level || 'MEDIUM') as 'LOW' | 'MEDIUM' | 'HIGH',
                    formula_ref: synthesizer.multiplex_conclusion.tension?.formula_ref || "ΔT = 1 - max(weight)",
                    weight_distribution: synthesizer.multiplex_conclusion.tension?.weight_distribution || ''
                },
                merge_strategy: (synthesizer.multiplex_conclusion.merge_strategy || 'PRESERVE_SHADOWS') as 'COLLAPSE' | 'PRESERVE_SHADOWS' | 'EXPLICIT_CONFLICT',
                merge_note: synthesizer.multiplex_conclusion.merge_note || ''
            } : undefined,
            final_synthesis: {
                response_text: synthesizer.final_response,
            },
            next_moves: synthesizer.next_moves,
        };

        // ? Soul Auditor: 撖抵??蝯???衣泵??SOUL.md
        const previousResponses = messages
            .filter(m => m.role === 'assistant')
            .map(m => m.content || '')
            .slice(-5);

        const auditResult = auditOutput(
            userMessage,
            synthesizer.final_response,
            previousResponses
        );

        // 閮?撖抵??亥?
        saveAuditLog({
            sessionId: conversation?.id || 'unknown',
            turn: messages.length,
            input: userMessage,
            output: synthesizer.final_response,
            result: auditResult,
        });

        // 憒????閬???霅血?
        let finalResponse = synthesizer.final_response;
        if (!auditResult.passed && auditResult.violations.some(v => v.severity === 'high')) {
            console.warn('[Auditor] High severity violation detected!');
            finalResponse += '\n\n---\n?? *撖抵?瘜冽?: ' + auditResult.auditNote + '*';
        }

        return {
            response: finalResponse,
            deliberation: {
                ...deliberation,
                soulAudit: {
                    passed: auditResult.passed,
                    honestyScore: auditResult.honestyScore,
                    violations: auditResult.violations.length,
                    auditNote: auditResult.auditNote,
                },
            },
        };
    };

    const runLegacyProviderFlow = async (
        userMessage: string
    ): Promise<{ response: string; deliberation: DeliberationData | undefined }> => {
        if (providerRequiresApiKey && !hasProviderCredential) {
            return {
                response: "請先設定 API Key，才能使用雲端模型進行回應。",
                deliberation: undefined,
            };
        }

        if (apiSettings?.mode === "fast") {
            return await performFastMode(userMessage);
        }
        const deliberationResult = await performMultiPathDeliberation(userMessage);
        return {
            response: deliberationResult.response,
            deliberation: deliberationResult.deliberation,
        };
    };

    const sendMessage = async () => {
        if (!input.trim() || isLoading || !conversation) return;

        const userMessage: Message = {
            id: `msg_${Date.now()}`,
            role: "user",
            content: input,
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);
        setLoadingPhase(USE_BACKEND_CHAT ? "?郊敺垢銝?.." : (apiSettings?.mode === "fast" ? "?葉..." : "??撖抵降..."));

        try {
            let result: { response: string; deliberation: DeliberationData | undefined };

            if (USE_BACKEND_CHAT) {
                const fullAnalysis = apiSettings?.mode !== "fast";

                // If we already know the backend is unavailable and we can fallback, skip the backend call
                // to avoid waiting for request timeouts on every turn.
                if (ENABLE_PROVIDER_FALLBACK && chatActiveMode === "fallback") {
                    setChatActiveMode("fallback");
                    if (hasProviderCredential) {
                        setLoadingPhase("敺垢銝?剁?雿輻?湔 API...");
                    } else {
                        setLoadingPhase("敺垢銝?剁?隢?閮剖? API Key...");
                    }
                    result = await runLegacyProviderFlow(userMessage.content);
                } else {
                    try {
                        const backendResult = await callBackendChat(userMessage.content, fullAnalysis);
                        if (isBackendDegradedResponse(backendResult.response)) {
                            if (ENABLE_PROVIDER_FALLBACK && hasProviderCredential) {
                                setChatActiveMode("fallback");
                                setFallbackReasonCode("backend_error");
                                setLoadingPhase("敺垢璅∪?銝?剁????喟??API...");
                                result = await runLegacyProviderFlow(userMessage.content);
                            } else {
                                // No key (or fallback disabled): surface backend degraded state directly.
                                setChatActiveMode("backend");
                                setFallbackReasonCode("backend_error");
                                result = backendResult;
                            }
                        } else {
                            result = backendResult;
                            setChatActiveMode("backend");
                            setFallbackReasonCode(null);
                        }
                    } catch (backendErr) {
                        const reasonCode = classifyBackendFallbackReason(backendErr);
                        console.warn("[ToneSoul] Backend chat unavailable, fallback to legacy provider flow.", backendErr);
                        if (ENABLE_PROVIDER_FALLBACK) {
                            setChatActiveMode("fallback");
                            setFallbackReasonCode(reasonCode);
                            setLoadingPhase("敺垢銝?剁????喟??API...");
                            result = await runLegacyProviderFlow(userMessage.content);
                        } else {
                            setChatActiveMode("backend");
                            setFallbackReasonCode(reasonCode);
                            throw backendErr;
                        }
                    }
                }
            } else {
                setChatActiveMode("legacy_provider");
                setFallbackReasonCode(null);
                result = await runLegacyProviderFlow(userMessage.content);
            }

            const assistantMessage: Message = {
                id: `msg_${Date.now()}_ai`,
                role: "assistant",
                content: result.response,
                deliberation: result.deliberation,
                timestamp: new Date(),
            };

            const newMessages = [...messages, userMessage, assistantMessage];
            setMessages(newMessages.map(m => ({ ...m, timestamp: new Date(m.timestamp) })));

            // ?脣???IndexedDB
            const updatedConversation: Conversation = {
                ...conversation,
                title: conversation.messages.length === 0
                    ? userMessage.content.slice(0, 50) + (userMessage.content.length > 50 ? '...' : '')
                    : conversation.title,
                updatedAt: Date.now(),
                messages: newMessages.map(m => ({
                    ...m,
                    timestamp: m.timestamp.getTime(),
                })),
            };
            // Guard against resurrecting a conversation that the user deleted while a request was in-flight.
            // If it no longer exists in IndexedDB, we skip persistence + state update for that conversation.
            let shouldPersist = true;
            try {
                shouldPersist = (await getConversation(updatedConversation.id)) !== null;
            } catch (error) {
                // If the existence check fails, we still attempt to persist to avoid data loss.
                console.error("[ToneSoul] Conversation existence check failed:", error);
            }

            if (!shouldPersist) {
                console.warn(
                    "[ToneSoul] Conversation deleted during in-flight update; skipping persistence."
                );
            } else {
                await saveConversation(updatedConversation);
                onConversationUpdate(updatedConversation);
            }

            // ?湔?????撘萄?蝛? + ?批撽?嚗?
            if (result.deliberation?.entropy_meter) {
                const tensionRecord: TensionRecord = {
                    turn: newMessages.length,
                    timestamp: Date.now(),
                    value: result.deliberation.entropy_meter.value,
                    components: {
                        divergence: 0,
                        riskWeight: 0,
                        coherence: 0,
                        integrity: 0,
                    },
                    context: userMessage.content.slice(0, 50),
                };
                const newSoulState = updateSoulState(soulState, tensionRecord, result.response);
                setSoulState(newSoulState);
                console.log('[ToneSoul] Soul State updated:', newSoulState.soulMode, 'Integral:', newSoulState.tensionIntegral.toFixed(2));
            }

            // ?芸?撅???啁?撖抵降
            setExpandedNodes(prev => new Set(prev).add(assistantMessage.id));

        } catch (error) {
            console.error("Chat error:", error);
            const errorMessage: Message = {
                id: `msg_${Date.now()}_error`,
                role: "assistant",
                content: `?航炊嚗?{error instanceof Error ? error.message : "???憭望?"}`,
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
            setLoadingPhase("");
        }
    };

    const handleSuggestionClick = (text: string) => {
        setInput(text);
    };

    if (!conversation) {
        return (
            <div className="flex flex-col h-full bg-slate-50 items-center justify-center text-slate-400">
                <MessageSquare className="w-16 h-16 mb-4 opacity-30" />
                <p className="text-lg font-medium">請先選擇一個對話</p>
                <p className="text-sm">建立或切換對話後，就可以開始傳送訊息。</p>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full bg-slate-50">
            {/* ?予璅∪????蝷箏 */}
            <div className="bg-slate-900/5 border-b border-slate-200 px-4 py-1.5 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    {chatActiveMode === "backend" ? (
                        <span className="flex items-center gap-1.5 text-[11px] font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                            <Server className="w-3 h-3" />
                            隤?敺垢霅唳?
                        </span>
                    ) : chatActiveMode === "fallback" ? (
                        <span className="flex items-center gap-1.5 text-[11px] font-medium text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200">
                            <Zap className="w-3 h-3" />
                            ?湔 API嚗?蝡臭??舐嚗?
                        </span>
                    ) : (
                        <span className="flex items-center gap-1.5 text-[11px] font-medium text-blue-700 bg-blue-50 px-2 py-0.5 rounded-full border border-blue-200">
                            <Zap className="w-3 h-3" />
                            ?湔 API 鈭箸?降
                        </span>
                    )}
                    {fallbackReasonCode && (
                        <span className="text-[10px] text-amber-600 flex items-center gap-1">
                            <WifiOff className="w-3 h-3" />
                            {BACKEND_FALLBACK_REASON_LABEL[fallbackReasonCode]}
                        </span>
                    )}
                </div>
                <div className="text-[10px] text-slate-400">
                    {USE_BACKEND_CHAT
                        ? (ENABLE_PROVIDER_FALLBACK ? "Backend + Fallback" : "Backend Only")
                        : "Legacy Provider API"}
                </div>
            </div>

            {/* API Key ?? */}
            {shouldShowApiKeyHint && (
                <div className="bg-amber-50 border-b border-amber-200 px-4 py-2 flex items-center gap-2 text-sm text-amber-800">
                    <AlertTriangle className="w-4 h-4" />
                    <span>請先設定 API Key，才能使用雲端模型回應。可在 API 設定中填入。</span>
                </div>
            )}

            {/* ?????蝷箏 */}
            {soulState.totalTurns > 0 && (
                <div className="bg-gray-900/5 border-b border-gray-200 px-4 py-2 flex items-center justify-between">
                    <SoulDriveMeter soulState={soulState} compact />
                    <div className="text-[10px] text-gray-400">
                        Tension ?? {(soulState.tensionIntegral * 100).toFixed(0)}%
                    </div>
                </div>
            )}

            {/* 閮?” */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-64 text-slate-400">
                        <Users className="w-16 h-16 mb-4 opacity-30" />
                        <p className="text-lg font-medium">ToneSoul Multi-Path Deliberation</p>
                        <p className="text-sm">銝楝銝西?撖抵降 ??瘥?閮隤輻 4 甈?API</p>
                        <p className="text-xs mt-2 text-slate-300">Philosopher ? Engineer ? Guardian ??Synthesizer</p>
                    </div>
                )}

                {messages.map((message) => (
                    <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                        <div className={`max-w-[85%] rounded-2xl ${message.role === "user"
                            ? "bg-indigo-600 text-white p-4"
                            : "bg-white border border-slate-200 shadow-sm overflow-hidden"
                            }`}>
                            {message.role === "user" ? (
                                <p className="leading-relaxed">{message.content}</p>
                            ) : (
                                <>
                                    {/* AI ???批捆 */}
                                    <div className="p-5">
                                        <p className="text-slate-800 leading-relaxed text-lg">
                                            {message.content}
                                        </p>
                                    </div>

                                    {/* ?批撖抵降撅?? */}
                                    {message.deliberation && (
                                        <>
                                            <div className="border-t border-slate-100">
                                                <button type="button"
                                                    onClick={() => toggleDeliberation(message.id)}
                                                    className="w-full px-5 py-3 flex items-center justify-between text-sm text-slate-500 hover:bg-slate-50 transition-colors"
                                                >
                                                    <span className="flex items-center gap-2">
                                                        <Brain className="w-4 h-4" />
                                                        憭楝敺祟霅?(4 甈∠蝡?API 隤輻)
                                                    </span>
                                                    {expandedNodes.has(message.id) ? (
                                                        <ChevronUp className="w-4 h-4" />
                                                    ) : (
                                                        <ChevronDown className="w-4 h-4" />
                                                    )}
                                                </button>
                                            </div>

                                            {expandedNodes.has(message.id) && (
                                                <div className="bg-slate-50/50 border-t border-slate-100 p-5 space-y-4">
                                                    {/* 撘萄??銵?*/}
                                                    {message.deliberation.entropy_meter && (
                                                        <SoulStateMeter
                                                            value={message.deliberation.entropy_meter.value}
                                                            calculationNote={message.deliberation.entropy_meter.calculation_note}
                                                        />
                                                    )}

                                                    {/* 霅唳?撱?*/}
                                                    {message.deliberation.council_chamber && (
                                                        <CouncilChamber
                                                            philosopher={message.deliberation.council_chamber.philosopher}
                                                            engineer={message.deliberation.council_chamber.engineer}
                                                            guardian={message.deliberation.council_chamber.guardian}
                                                        />
                                                    )}

                                                    {/* ?啗??銵冽 */}
                                                    {message.deliberation.decision_matrix && (
                                                        <TacticalDashboard matrix={{
                                                            user_hidden_intent: message.deliberation.decision_matrix.user_hidden_intent,
                                                            ai_strategy_name: message.deliberation.decision_matrix.ai_strategy_name,
                                                            intended_effect: message.deliberation.decision_matrix.intended_effect,
                                                            tone_tag: message.deliberation.decision_matrix.tone_tag,
                                                        }} />
                                                    )}

                                                    {/* vMT-2601 ?摩?啣蔣 */}
                                                    {message.deliberation.multiplex_conclusion && (
                                                        <LogicalShadows data={message.deliberation.multiplex_conclusion} />
                                                    )}

                                                    {/* 撖抵??勗? */}
                                                    {message.deliberation.audit && (
                                                        <div className="bg-white/60 p-4 rounded-lg border border-emerald-200">
                                                            <div className="flex items-center justify-between mb-3">
                                                                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                                                                    ?怎?撖抵? (Audit)
                                                                </span>
                                                                <span className={`px-2 py-1 rounded-full text-xs font-bold ${message.deliberation.audit.audit_verdict === 'Pass'
                                                                    ? 'bg-emerald-100 text-emerald-700'
                                                                    : 'bg-amber-100 text-amber-700'
                                                                    }`}>
                                                                    {message.deliberation.audit.audit_verdict}
                                                                </span>
                                                            </div>
                                                            <div className="flex items-center gap-4 mb-2">
                                                                <div className="flex items-center gap-2">
                                                                    <span className="text-xs text-slate-500">隤祕?:</span>
                                                                    <span className="text-sm font-bold text-slate-700">
                                                                        {(message.deliberation.audit.honesty_score * 100).toFixed(0)}%
                                                                    </span>
                                                                </div>
                                                            </div>
                                                            {message.deliberation.audit.responsibility_check && (
                                                                <p className="text-xs text-slate-600 italic">
                                                                    {message.deliberation.audit.responsibility_check}
                                                                </p>
                                                            )}
                                                        </div>
                                                    )}
                                                </div>
                                            )}

                                            {/* 撱箄降頝?*/}
                                            {message.deliberation.next_moves && message.deliberation.next_moves.length > 0 && (
                                                <div className="px-5 pb-4 flex flex-wrap gap-2 border-t border-slate-100 pt-3">
                                                    {message.deliberation.next_moves.map((move, idx) => (
                                                        <button type="button"
                                                            key={idx}
                                                            onClick={() => handleSuggestionClick(move.text)}
                                                            className="text-xs flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-50 hover:bg-indigo-50 text-slate-600 hover:text-indigo-600 transition-colors border border-slate-200 hover:border-indigo-200 group"
                                                        >
                                                            <span className="font-bold text-indigo-400 group-hover:text-indigo-600">
                                                                {move.label}
                                                            </span>
                                                            <MoveRight className="w-3 h-3 opacity-30 group-hover:opacity-100" />
                                                            <span>{move.text}</span>
                                                        </button>
                                                    ))}
                                                </div>
                                            )}
                                        </>
                                    )}
                                </>
                            )}
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm flex items-center gap-3">
                            <div className="flex gap-1">
                                <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                            </div>
                            <span className="text-sm text-purple-600 font-medium">{loadingPhase}</span>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* 頛詨? */}
            <div className="p-4 border-t border-slate-200 bg-white">
                {USE_BACKEND_CHAT && (
                    <div className="mb-3 flex items-center justify-end gap-2">
                        <span className="text-xs text-slate-500">Council 璅∪?</span>
                        <select
                            value={councilMode}
                            onChange={(event) => setCouncilMode(normalizeCouncilMode(event.target.value))}
                            disabled={isLoading}
                            className="text-xs px-2 py-1 rounded-md border border-slate-300 bg-white text-slate-700 disabled:opacity-50"
                        >
                            {COUNCIL_MODE_OPTIONS.map((option) => (
                                <option key={option.value} value={option.value}>
                                    {option.label}
                                </option>
                            ))}
                        </select>
                    </div>
                )}
                <div className="flex gap-3">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => {
                            // Keep IME composition (e.g. 銝剜?頛詨瘜摮? from triggering send.
                            if (e.nativeEvent.isComposing) return;
                            if (e.key === "Enter") {
                                e.preventDefault();
                                void sendMessage();
                            }
                        }}
                        placeholder="頛詨閮隞亙???頝臬祟霅?.."
                        disabled={isLoading}
                        className="flex-1 px-4 py-3 bg-slate-100 rounded-xl border-0 focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all disabled:opacity-50"
                    />
                    <button type="button"
                        onClick={sendMessage}
                        disabled={isLoading || !input.trim()}
                        className="px-4 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg shadow-indigo-200"
                    >
                        {isLoading ? (
                            <Loader2 className="w-5 h-5 animate-spin" />
                        ) : (
                            <Send className="w-5 h-5" />
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
}



