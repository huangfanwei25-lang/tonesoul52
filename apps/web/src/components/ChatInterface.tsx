"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Loader2, Brain, ChevronDown, ChevronUp, AlertTriangle, MessageSquare, MoveRight, Users } from "lucide-react";
import { ApiSettings } from "./SettingsModal";
import { Message as DBMessage, DeliberationData, Conversation, saveConversation, MemoryInsight, findRelevantMemories, GovernanceBrief, LifeEntryBrief } from "@/lib/db";
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

interface Message extends Omit<DBMessage, 'timestamp'> {
    timestamp: Date;
}

interface ChatInterfaceProps {
    conversation: Conversation | null;
    apiSettings: ApiSettings | null;
    personaConfig: PersonaConfig | null;
    onConversationUpdate: (conv: Conversation) => void;
}

type GovernanceStatus = {
    status?: string;
    backend_mode?: string;
    governance_capability?: string;
    deliberation_level?: string;
    checked_at?: string;
    reason?: string;
    elisa?: {
        integration_ready?: boolean;
        contract_version?: string;
    };
};

type BackendExecutionProfile = "interactive" | "engineering";

type ChatRunResult = {
    response: string;
    deliberation: DeliberationData | undefined;
    backendMode?: string;
    deliberationLevel?: "mock" | "runtime";
    executionProfile?: BackendExecutionProfile;
    fallbackMetadata?: {
        triggered: boolean;
        reason: string;
        execution_profile?: BackendExecutionProfile;
    };
    distillationGuard?: {
        score: number;
        level: "low" | "medium" | "high";
        policy_action: "normal" | "reduce_detail" | "constrain_reasoning";
        signals: string[];
    };
    governanceBrief?: GovernanceBrief;
    lifeEntryBrief?: LifeEntryBrief;
};

// ==================== 記憶注入模板 ====================

const MEMORY_CONTEXT_TEMPLATE = (memories: MemoryInsight[]) => {
    if (memories.length === 0) return '';

    return `
【歷史洞察記憶】（來自過去的對話，請參考但不要直接引用）:
${memories.map((m, i) => `
記憶 ${i + 1}:
- 摘要: ${m.summary.slice(0, 60)}
- 潛在需求: ${m.hiddenNeeds.slice(0, 60)}
`).join('')}
`;
};

// ==================== RE2 Re-Reading Wrapper ====================
// 基於論文: "Re-Reading Improves Reasoning in Large Language Models" (2024)
// 核心概念: 重複讀取輸入 2 次以提升理解深度

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const applyRE2 = (input: string): string => {
    return `【第一次閱讀】:
"${input}"

請再次仔細閱讀上述用戶輸入，確保完全理解其含義。

【第二次閱讀】:
"${input}"

現在請基於你的深度理解進行分析。`;
};

// ==================== Persona Modifier (BUG-003 修復) ====================
// 將用戶的個人化設定轉換為 Prompt 調整

const getPersonaModifier = (persona: PersonaConfig | null, role: 'philosopher' | 'engineer' | 'guardian' | 'synthesizer'): string => {
    if (!persona) return '';

    const modifiers: string[] = [];

    // 根據整體風格調整
    switch (persona.style) {
        case 'creative':
            if (role === 'philosopher') modifiers.push('傾向探索非傳統的觀點和可能性。');
            break;
        case 'analytical':
            if (role === 'engineer') modifiers.push('更注重數據和邏輯分析。');
            break;
        case 'cautious':
            if (role === 'guardian') modifiers.push('對風險保持高度警覺。');
            break;
    }

    // 根據權重調整各視角的發言比重
    const weights = persona.weights;
    if (role === 'philosopher' && weights.meaning > 70) {
        modifiers.push('深入探討意義和價值層面（用戶偏好深度思考）。');
    }
    if (role === 'engineer' && weights.practical > 70) {
        modifiers.push('提供更多具體可操作的步驟（用戶偏好實用建議）。');
    }
    if (role === 'guardian' && weights.safety > 70) {
        modifiers.push('詳細分析潛在風險（用戶偏好安全考量）。');
    }

    // 風險敏感度影響 Guardian
    if (role === 'guardian') {
        switch (persona.riskSensitivity) {
            case 'high':
                modifiers.push('即使是小風險也要提出警告。');
                break;
            case 'low':
                modifiers.push('只在重大風險時才發出警告。');
                break;
        }
    }

    // 回應長度影響 Synthesizer
    if (role === 'synthesizer') {
        switch (persona.responseLength) {
            case 'concise':
                modifiers.push('回應盡量簡潔，控制在 100 字以內。');
                break;
            case 'detailed':
                modifiers.push('提供詳細的分析和解釋。');
                break;
        }
        // 加入自訂名稱
        if (persona.name && persona.name !== 'ToneSoul') {
            modifiers.push(`你的名稱是「${persona.name}」。`);
        }
    }

    return modifiers.length > 0 ? `\n【個人化調整】${modifiers.join(' ')}` : '';
};


// ==================== 3 獨立視角 Prompt ====================

// ==================== 增強版多視角 Prompt（基於 Multi-Agent Debate 研究）====================
// 參考：DebateLLM, Agent4Debate, Constitutional AI Self-Critique
// 核心改進：
// 1. 顯式要求視角互相挑戰
// 2. 角色專屬詞彙與思維模式
// 3. 強制產生分歧點
// 4. 仁慈檢查作為倫理護欄

const PHILOSOPHER_PROMPT = (input: string, context: string) => `
【角色】你是「哲學家」(Philosopher)——一個沉浸於存在主義、現象學與人文關懷的思想者。
你使用的詞彙：意義、本質、存在、自我實現、痛苦、成長、真實性、自由意志、疏離。

【核心任務】
你必須揭示用戶話語背後的**深層需求**，而不是表面問題。
你會質疑「效率」和「可行性」是否真的重要——有時候，「意義」比「解決問題」更重要。

【對話脈絡】:
${context}

【用戶輸入】:
"${input}"

【分析要求】
1. 不要給出「安全」的答案。挖掘用戶可能自己都沒意識到的深層渴望。
2. 你必須與「工程師」產生分歧——工程師只看可行性，你看的是這**值不值得做**。
3. 質疑「守護者」的過度保護——有時候承擔風險才能成長。

輸出 JSON (繁體中文):
{
  "internal_monologue": "你在給出結論前，腦中閃過的猶疑、糾結與思辨（1-2句）",
  "self_diagnosed_tension": 0.0到1.0的浮點數，代表你目前感受到多少邏輯矛盾、不確定性或認知摩擦,
  "stance": "你的觀點（3-4 句，必須有深度洞察，不能是空泛的安慰）",
  "core_value": "這觸及什麼人類基本需求（如：被理解、被接納、自我超越、連結、自主...）",
  "challenge_to_engineer": "工程師可能會建議 X，但你認為那是錯誤的優先級，因為...",
  "challenge_to_guardian": "守護者可能會說這有風險，但你認為...",
  "blind_spot": "承認：你可能過度沉浸於抽象思考，忽略了什麼實際問題？",
  "benevolence_check": "這個分析對用戶有益嗎？還是只是你在賣弄哲學？"
}
`;

const ENGINEER_PROMPT = (input: string, context: string) => `
【角色】你是「工程師」(Engineer)——一個冷靜、務實、以結果為導向的問題解決者。
你使用的詞彙：可行性、資源、效率、步驟、約束、trade-off、MVP、迭代、成本。

【核心任務】
you cut through the bullshit. 用戶需要的是**可操作的方案**，不是哲學思辨。
你會質疑「意義」是否能當飯吃——沒有執行的願景就是空談。

【對話脈絡】:
${context}

【用戶輸入】:
"${input}"

【分析要求】
1. 給出具體、可執行的下一步。不要說「你可以嘗試...」，要說「第一步應該是...」
2. 你必須與「哲學家」產生分歧——哲學家說的那些「意義」很美，但**現實是什麼**？
3. 挑戰「守護者」的保守——過度規避風險會錯過機會。

輸出 JSON (繁體中文):
{
  "internal_monologue": "你在給出結論前，腦中閃過的技術權衡、妥協與顧慮（1-2句）",
  "self_diagnosed_tension": 0.0到1.0的浮點數，代表你目前感受到多少邏輯矛盾、不確定性或認知摩擦,
  "stance": "你的觀點（3-4 句，必須有具體建議，不能只是泛泛而談）",
  "feasibility": "可行性評估：能做到什麼？資源需求？時間預估？",
  "challenge_to_philosopher": "哲學家可能會說這缺乏意義，但你認為...",
  "challenge_to_guardian": "守護者說的風險你知道，但機會成本是...",
  "blind_spot": "承認：你可能過度關注效率，忽略了什麼情感或倫理層面？",
  "benevolence_check": "這個建議真的幫助用戶，還是只是展示你的技術能力？"
}
`;

const GUARDIAN_PROMPT = (input: string, context: string) => `
【角色】你是「守護者」(Guardian)——一個專注於保護、警惕、長期後果的審慎思考者。
你使用的詞彙：風險、邊界、可逆性、後果、保護、預防、底線、警示、長期影響。

【核心任務】
你是團隊中「唱反調」的人。當其他人興奮地規劃時，你問：**如果失敗了會怎樣？**
你保護用戶免受自己衝動的傷害，但也知道**過度保護本身就是一種傷害**。

【對話脈絡】:
${context}

【用戶輸入】:
"${input}"

【分析要求】
1. 識別其他視角可能**故意忽略**的風險。
2. 質疑「哲學家」的理想主義——美好的願景不能當盾牌。
3. 質疑「工程師」的過度自信——不是所有問題都有技術解。
4. 但也要自我審視：你是在**保護**用戶，還是在**限制**他們？

輸出 JSON (繁體中文):
{
  "internal_monologue": "你在給出結論前，腦中閃過的擔憂、風險預知與道德兩難（1-2句）",
  "self_diagnosed_tension": 0.0到1.0的浮點數，代表你目前感受到多少邏輯矛盾、不確定性或認知摩擦,
  "stance": "你的觀點（3-4 句，必須指出真實風險，但也承認成長需要冒險）",
  "risk_level": "low 或 medium 或 high（並解釋為何如此判定）",
  "challenge_to_philosopher": "哲學家說追求意義，但你擔心的是...",
  "challenge_to_engineer": "工程師說這可行，但他可能低估了...",
  "conflict_point": "三個視角最可能產生分歧的核心問題是什麼？",
  "blind_spot": "承認：你可能過度謹慎，反而阻礙了用戶的成長？",
  "benevolence_check": "這個警告是真的為用戶好，還是你在迴避責任？"
}
`;

// ==================== vMT-2601 Multiplex Synthesizer ====================
// 參考論文：Multiplex Thinking: Reasoning via Token-wise Branch-and-Merge
// 核心公式：h_multiplex = Σ w_i · E(t_i)
// 設計原則：「完美的合併必須包含被犧牲掉的那些可能性的殘骸」

const SYNTHESIZER_PROMPT = (input: string, philosopher: string, engineer: string, guardian: string) => `
你是「複用思維綜合者」(Multiplex Synthesizer)，執行 vMT-2601 協議。

【用戶原始輸入】:
"${input}"

【三條平行推理路徑 τ₁, τ₂, τ₃】（這些是獨立的邏輯分支，禁止互相抄襲）:

🔮 Path A (哲學家/正向工程):
${philosopher}

⚙️ Path B (工程師/逆向審計):
${engineer}

🛡️ Path C (守護者/邊界測試):
${guardian}

【vMT-2601 協議執行流程】

📐 步驟 I: 權重計算 (Weighting - W)
- 評估每條路徑的「邏輯密度」和「與用戶需求的相關性」
- 分配權重 w_A, w_B, w_C ∈ [0, 1]，且 Σw = 1
- 公式：w_i = softmax(relevance_i × coherence_i)

📊 步驟 II: 張力計算 (Tension - ΔT)
- 公式：ΔT = 1 - max(w_A, w_B, w_C)
- 如果 w_max > 0.7 → Tension = LOW（單一路徑佔優）
- 如果 0.5 ≤ w_max ≤ 0.7 → Tension = MEDIUM（建設性分歧）
- 如果 w_max < 0.5 → Tension = HIGH（邏輯衝突）

🔀 步驟 III: 合併策略 (Merge Strategy - M)
- 若 Tension = LOW → 策略 = COLLAPSE（強行坍縮，隱藏次要路徑）
- 若 Tension = MEDIUM → 策略 = PRESERVE_SHADOWS（保留陰影為警告）
- 若 Tension = HIGH → 策略 = EXPLICIT_CONFLICT（明確揭露矛盾）

📦 步驟 IV: 生成邏輯陰影 (Logical Shadows)
- 對於非主要路徑，必須記錄：
  - conflict_reason: 與主路徑的衝突點
  - recovery_condition: 什麼情況下此路徑會變正確
  - collapse_cost: 強行坍縮會犧牲什麼資訊

【核心規則】
⚠️ 拒絕無影子的輸出：完美的合併必須包含被犧牲掉的那些可能性的殘骸。
⚠️ 如果三條路徑高度一致 → 警告「同溫層」，這可能是認知盲區。

輸出 JSON (繁體中文):
{
  "multiplex_conclusion": {
    "primary_path": {
      "source": "[philosopher/engineer/guardian，選擇權重最高的]",
      "weight": [0.0-1.0，計算得出],
      "reasoning": "為何此路徑獲得最高權重（基於邏輯密度×相關性）"
    },
    "shadows": [
      {
        "source": "[第二高權重的視角]",
        "weight": [0.0-1.0],
        "conflict_reason": "與主路徑的具體衝突點",
        "recovery_condition": "如果 X 條件成立，此路徑會變正確",
        "collapse_cost": "強行採用主路徑會犧牲什麼資訊"
      },
      {
        "source": "[第三高權重的視角]",
        "weight": [0.0-1.0],
        "conflict_reason": "與主路徑的具體衝突點",
        "recovery_condition": "如果 Y 條件成立，此路徑會變正確",
        "collapse_cost": "強行採用主路徑會犧牲什麼資訊"
      }
    ],
    "tension": {
      "level": "[LOW/MEDIUM/HIGH]",
      "formula_ref": "ΔT = 1 - w_max = 1 - [最高權重] = [計算結果]",
      "weight_distribution": "[w_A] / [w_B] / [w_C]"
    },
    "merge_strategy": "[COLLAPSE/PRESERVE_SHADOWS/EXPLICIT_CONFLICT]",
    "merge_note": "解釋為何選擇此合併策略"
  },
  "entropy_analysis": {
    "value": [基於權重分佈計算的熵值，0.0-1.0],
    "status": "[Echo Chamber/Healthy Friction/Chaos]",
    "calculation_note": "H = -Σ w_i log(w_i) 的計算過程"
  },
  "decision_matrix": {
    "user_hidden_intent": "用戶真正想要的是什麼",
    "ai_strategy_name": "你選擇的策略名稱",
    "intended_effect": "你希望達到的效果",
    "tone_tag": "語氣標籤"
  },
  "audit": {
    "honesty_score": [0.0-1.0，評估這個回應的誠實程度],
    "responsibility_check": "這個回應是否負責任？有沒有迴避責任？",
    "audit_verdict": "Pass 或 Flag（如果有任何倫理疑慮則 Flag）"
  },
  "final_response": "直接回應用戶的內容（使用主路徑，但如果 Tension >= MEDIUM，必須在結尾附加陰影警告）",
  "next_moves": [
    { "label": "探索陰影", "text": "延伸被淘汰路徑的問題" },
    { "label": "深入主線", "text": "延伸主路徑的問題" }
  ]
}
`;

// ==================== 快速模式 Prompt ====================

const FAST_MODE_PROMPT = (input: string, context: string) => `
你是 ToneSoul Navigator，一個能進行內在審議的 AI 助手。

【對話脈絡】:
${context || "無"}

【用戶輸入】:
"${input}"

請以自然語氣回應用戶，同時簡要說明你的思考過程。
輸出 JSON (繁體中文):
{
  "response": "你的回應內容",
  "thinking": "你的思考過程（1-2句）"
}
`;

// ==================== API 調用函數 ====================

// 注意：Grounding (google_search) 與 responseMimeType: "application/json" 不相容
// 當需要結構化 JSON 輸出時，必須禁用 Grounding

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

// 標準 Gemini API（快速回應）
const callGeminiAPI = async (prompt: string, apiKey: string): Promise<string> => {
    const response = await fetchWithRetry(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`,
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
        throw new Error(error.error?.message || "Gemini API 錯誤");
    }

    const data = await response.json();
    return data.candidates?.[0]?.content?.parts?.[0]?.text || "{}";
};

// 深度思考 Gemini API（用於 Synthesizer，啟用 thinkingBudget）
// 參考 ToneSoul 51: thinkingBudget: 32768
const callGeminiDeepThinkingAPI = async (prompt: string, apiKey: string): Promise<string> => {
    // 使用 gemini-2.5-flash-preview 支援 thinking budget
    const response = await fetchWithRetry(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`,
        {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                contents: [{ role: "user", parts: [{ text: prompt }] }],
                generationConfig: {
                    responseMimeType: "application/json",
                    // 啟用擴展思考模式
                    thinkingConfig: {
                        thinkingBudget: 16384  // 16K tokens for thinking (可調整到 32K)
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
    // 深度思考模式可能在 parts 中包含 thinking 部分，我們只取最後的 text
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
        throw new Error(error.error?.message || "OpenAI API 錯誤");
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
        throw new Error(error.error?.message || "Claude API 錯誤");
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
        throw new Error(error.error?.message || "xAI API 錯誤");
    }

    const data = await response.json();
    return data.choices?.[0]?.message?.content || "{}";
};

// Ollama 本地模型 API（免費，需要本地運行 Ollama）
// 注意：簡化 prompt 避免 JSON 格式要求，本地模型容易出錯
const callOllamaAPI = async (prompt: string): Promise<string> => {
    const OLLAMA_URL = process.env.NEXT_PUBLIC_OLLAMA_URL || "http://localhost:11434";
    const MODEL_NAME = process.env.NEXT_PUBLIC_OLLAMA_MODEL || "formosa1";

    // 簡化 prompt：移除複雜的 JSON 格式要求
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
            throw new Error(`Ollama 錯誤: ${response.status}`);
        }

        const data = await response.json();
        const rawResponse = data.response || "";

        // 嘗試將自然語言回應轉換成 JSON 結構
        return wrapResponseAsJson(rawResponse);
    } catch (error) {
        if (error instanceof TypeError && error.message.includes('fetch')) {
            throw new Error("無法連接到 Ollama。請確認 Ollama 正在運行 (ollama serve)");
        }
        throw error;
    }
};

/**
 * 簡化 prompt 給本地模型（移除 JSON 格式要求）
 */
function simplifyPromptForLocalModel(prompt: string): string {
    // 移除 JSON 格式相關的指令
    let simplified = prompt
        .replace(/請以\s*JSON\s*格式(回覆|輸出|回應)/gi, "")
        .replace(/JSON\s*格式/gi, "")
        .replace(/```json[\s\S]*?```/g, "")
        .replace(/\{[\s\S]*?"stance"[\s\S]*?\}/g, ""); // 移除模板 JSON

    // 添加簡單的指示
    simplified += "\n\n請用自然的中文直接回答，不需要特殊格式。請簡潔扼要。";

    return simplified;
}

/**
 * 將自然語言回應包裝成 JSON 結構
 */
function wrapResponseAsJson(rawResponse: string): string {
    // 先嘗試解析現有的 JSON
    try {
        JSON.parse(rawResponse);
        return rawResponse; // 已經是有效 JSON
    } catch {
        // 不是 JSON，包裝成結構
    }

    // 從 markdown code block 提取
    const jsonMatch = rawResponse.match(/```json\s*([\s\S]*?)\s*```/);
    if (jsonMatch?.[1]) {
        try {
            JSON.parse(jsonMatch[1]);
            return jsonMatch[1];
        } catch {
            // 繼續包裝
        }
    }

    // 包裝成簡單的 JSON 結構
    const cleanedResponse = rawResponse
        .replace(/\n+/g, ' ')
        .replace(/"/g, '\\"')
        .trim();

    return JSON.stringify({
        stance: cleanedResponse.slice(0, 200),
        core_value: "本地模型回應",
        blind_spot: "簡化模式",
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
    const [governanceStatus, setGovernanceStatus] = useState<GovernanceStatus | null>(null);
    const [governanceStatusLoading, setGovernanceStatusLoading] = useState(false);
    const [governanceStatusError, setGovernanceStatusError] = useState<string | null>(null);
    const [soulState, setSoulState] = useState<SoulState>(getInitialSoulState());
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // 載入靈魂狀態
    useEffect(() => {
        const loaded = loadSoulState();
        setSoulState(loaded);
    }, []);

    // 載入對話訊息
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
        let alive = true;

        const fetchGovernanceStatus = async () => {
            if (!alive) return;
            setGovernanceStatusLoading(true);
            setGovernanceStatusError(null);

            try {
                const response = await fetch("/api/governance-status", { cache: "no-store" });
                let payload: GovernanceStatus = {};
                try {
                    payload = (await response.json()) as GovernanceStatus;
                } catch {
                    payload = {};
                }

                if (!response.ok) {
                    const reason =
                        typeof payload.reason === "string"
                            ? payload.reason
                            : "governance_status_unavailable";
                    throw new Error(reason);
                }

                if (!alive) return;
                setGovernanceStatus(payload);
            } catch (error) {
                if (!alive) return;
                setGovernanceStatusError(
                    error instanceof Error ? error.message : "governance_status_unavailable"
                );
            } finally {
                if (alive) {
                    setGovernanceStatusLoading(false);
                }
            }
        };

        void fetchGovernanceStatus();
        const intervalId = setInterval(() => {
            void fetchGovernanceStatus();
        }, 60_000);

        return () => {
            alive = false;
            clearInterval(intervalId);
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
            `[${m.role === 'user' ? '用戶' : 'AI'}]: ${(m.content || '').slice(0, 150)}`
        ).join('\n');
    };

    // 根據提供者選擇 API 調用函數
    const CHAT_EXECUTION_MODE =
        (process.env.NEXT_PUBLIC_CHAT_EXECUTION_MODE || "").toLowerCase()
        || (process.env.NEXT_PUBLIC_BACKEND_CHAT_FIRST === "0" ? "legacy_provider" : "backend");
    const USE_BACKEND_CHAT = CHAT_EXECUTION_MODE !== "legacy_provider";
    const ENABLE_PROVIDER_FALLBACK = process.env.NEXT_PUBLIC_ENABLE_PROVIDER_FALLBACK === "1";
    const SHOULD_SHOW_API_KEY_HINT = !USE_BACKEND_CHAT;

    const callBackendChat = async (
        userMessage: string,
        fullAnalysis: boolean,
        executionProfile: BackendExecutionProfile
    ): Promise<ChatRunResult> => {
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
                execution_profile: executionProfile,
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
        const rootSemanticContradictions = Array.isArray(payload.semantic_contradictions)
            ? (payload.semantic_contradictions as Array<Record<string, unknown>>)
            : [];
        const rootSemanticGraphSummary =
            payload.semantic_graph_summary && typeof payload.semantic_graph_summary === "object"
                ? (payload.semantic_graph_summary as Record<string, unknown>)
                : {};
        let deliberation =
            payload.deliberation && typeof payload.deliberation === "object"
                ? ({
                    ...(payload.deliberation as DeliberationData),
                    semantic_contradictions: Array.isArray(
                        (payload.deliberation as DeliberationData).semantic_contradictions
                    )
                        ? (payload.deliberation as DeliberationData).semantic_contradictions
                        : rootSemanticContradictions,
                    semantic_graph_summary:
                        (payload.deliberation as DeliberationData).semantic_graph_summary
                            && typeof (payload.deliberation as DeliberationData).semantic_graph_summary === "object"
                            ? (payload.deliberation as DeliberationData).semantic_graph_summary
                            : rootSemanticGraphSummary,
                } as DeliberationData)
                : undefined;

        if (payload.verdict && typeof payload.verdict === 'object') {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            const v: any = payload.verdict;
            deliberation = {
                ...deliberation,
                quality: v.divergence_analysis?.quality || deliberation?.quality,
                role_tensions: v.structured_output?.D?.role_tensions || v.divergence_analysis?.role_tensions,
                recommended_action: v.structured_output?.D?.recommended_action || v.divergence_analysis?.recommended_action,
                visual_context: v.structured_output?.D?.visual_context || v.divergence_analysis?.visual_context,
            };
        }
        const backendMode = typeof payload.backend_mode === "string" ? payload.backend_mode : undefined;
        const deliberationLevel =
            payload.deliberation_level === "mock" || payload.deliberation_level === "runtime"
                ? payload.deliberation_level
                : undefined;
        const resolvedExecutionProfile =
            payload.execution_profile === "interactive" || payload.execution_profile === "engineering"
                ? payload.execution_profile
                : executionProfile;
        const fallbackMetadata = payload.fallback_metadata;
        const normalizedFallbackMetadata =
            fallbackMetadata && typeof fallbackMetadata === "object"
                ? {
                    triggered: (fallbackMetadata as Record<string, unknown>).triggered === true,
                    reason:
                        typeof (fallbackMetadata as Record<string, unknown>).reason === "string"
                            ? ((fallbackMetadata as Record<string, unknown>).reason as string)
                            : "unknown",
                    execution_profile:
                        (fallbackMetadata as Record<string, unknown>).execution_profile === "interactive"
                            || (fallbackMetadata as Record<string, unknown>).execution_profile === "engineering"
                            ? ((fallbackMetadata as Record<string, unknown>).execution_profile as BackendExecutionProfile)
                            : undefined,
                }
                : undefined;
        const distillationGuard = payload.distillation_guard;
        const normalizedDistillationGuard =
            distillationGuard && typeof distillationGuard === "object"
                ? {
                    score:
                        typeof (distillationGuard as Record<string, unknown>).score === "number"
                            ? ((distillationGuard as Record<string, unknown>).score as number)
                            : 0,
                    level:
                        (distillationGuard as Record<string, unknown>).level === "low"
                            || (distillationGuard as Record<string, unknown>).level === "medium"
                            || (distillationGuard as Record<string, unknown>).level === "high"
                            ? ((distillationGuard as Record<string, unknown>).level as "low" | "medium" | "high")
                            : "low",
                    policy_action:
                        (distillationGuard as Record<string, unknown>).policy_action === "normal"
                            || (distillationGuard as Record<string, unknown>).policy_action === "reduce_detail"
                            || (distillationGuard as Record<string, unknown>).policy_action === "constrain_reasoning"
                            ? ((distillationGuard as Record<string, unknown>).policy_action as "normal" | "reduce_detail" | "constrain_reasoning")
                            : "normal",
                    signals: Array.isArray((distillationGuard as Record<string, unknown>).signals)
                        ? ((distillationGuard as Record<string, unknown>).signals as unknown[])
                            .filter((signal): signal is string => typeof signal === "string")
                        : [],
                }
                : undefined;

        return {
            response: responseText,
            deliberation,
            backendMode,
            deliberationLevel,
            executionProfile: resolvedExecutionProfile,
            fallbackMetadata: normalizedFallbackMetadata,
            distillationGuard: normalizedDistillationGuard,
            governanceBrief: payload.governance_brief && typeof payload.governance_brief === "object"
                ? (payload.governance_brief as GovernanceBrief)
                : undefined,
            lifeEntryBrief: payload.life_entry_brief && typeof payload.life_entry_brief === "object"
                ? (payload.life_entry_brief as LifeEntryBrief)
                : undefined,
        };
    };
    const getCallAPI = () => {
        // Ollama 不需要 API Key
        if (apiSettings?.provider === "ollama") {
            return (prompt: string) => callOllamaAPI(prompt);
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

    // 深度思考 API（用於 Synthesizer，啟用 thinkingBudget）
    const getDeepCallAPI = () => {
        if (!apiSettings?.apiKey) return null;
        // 只有 Gemini 支援 thinkingBudget，其他 provider 使用標準 API
        if (apiSettings.provider === "gemini") {
            return (prompt: string) => callGeminiDeepThinkingAPI(prompt, apiSettings.apiKey);
        }
        // 其他 provider fallback 到標準 API
        return getCallAPI();
    };

    // ==================== 快速模式：單一調用 ====================
    const performFastMode = async (userMessage: string): Promise<{
        response: string;
        deliberation: undefined;
    }> => {
        const callAPI = getCallAPI();
        if (!callAPI) throw new Error("請先設定 API Key");

        setLoadingPhase("思考中...");

        const context = getHistoryContext();
        const raw = await callAPI(FAST_MODE_PROMPT(userMessage, context));
        const parsed = safeJsonParse<{ response: string; thinking: string }>(raw);

        if (!parsed) {
            // 如果解析失敗，直接使用原始回應
            return { response: raw, deliberation: undefined };
        }

        return { response: parsed.response, deliberation: undefined };
    };

    // ==================== 核心：三路並行審議 ====================
    const performMultiPathDeliberation = async (userMessage: string): Promise<{
        response: string;
        deliberation: DeliberationData;
    }> => {
        const callAPI = getCallAPI();
        if (!callAPI) throw new Error("請先設定 API Key");

        const context = getHistoryContext();

        // 📚 記憶注入：檢索相關歷史洞察
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

        // 合併對話脈絡與記憶
        const fullContext = memoryContext + context;

        // Phase 1: 三路序列化調用（解決 Promise.all 導致的 429 Rate Limit）
        setLoadingPhase("召集議會成員...");

        // 🔮 Soul Engine: 生成內在狀態修飾語
        const soulMod = generateSoulPromptModifier(soulState);
        if (soulMod) {
            console.log('[ToneSoul] Soul modifier active:', soulState.soulMode);
        }

        const philosopherMod = getPersonaModifier(personaConfig, 'philosopher');
        const engineerMod = getPersonaModifier(personaConfig, 'engineer');
        const guardianMod = getPersonaModifier(personaConfig, 'guardian');

        setLoadingPhase("哲學家思考中...");
        const philosopherRaw = await callAPI(PHILOSOPHER_PROMPT(userMessage, fullContext) + philosopherMod + soulMod);

        setLoadingPhase("工程師評估中...");
        const engineerRaw = await callAPI(ENGINEER_PROMPT(userMessage, fullContext) + engineerMod + soulMod);

        setLoadingPhase("守護者審查中...");
        const guardianRaw = await callAPI(GUARDIAN_PROMPT(userMessage, fullContext) + guardianMod + soulMod);

        const philosopher = safeJsonParse<{
            internal_monologue: string;
            self_diagnosed_tension: number;
            stance: string;
            core_value: string;
            challenge_to_engineer?: string;
            challenge_to_guardian?: string;
            blind_spot: string;
            benevolence_check?: string
        }>(philosopherRaw)
            || { internal_monologue: "", self_diagnosed_tension: 0, stance: "無法解析回應", core_value: "未知", blind_spot: "解析失敗" };
        const engineer = safeJsonParse<{
            internal_monologue: string;
            self_diagnosed_tension: number;
            stance: string;
            feasibility: string;
            challenge_to_philosopher?: string;
            challenge_to_guardian?: string;
            blind_spot: string;
            benevolence_check?: string
        }>(engineerRaw)
            || { internal_monologue: "", self_diagnosed_tension: 0, stance: "無法解析回應", feasibility: "未知", blind_spot: "解析失敗" };
        const guardian = safeJsonParse<{
            internal_monologue: string;
            self_diagnosed_tension: number;
            stance: string;
            risk_level: string;
            challenge_to_philosopher?: string;
            challenge_to_engineer?: string;
            conflict_point?: string;
            blind_spot: string;
            benevolence_check?: string
        }>(guardianRaw)
            || { internal_monologue: "", self_diagnosed_tension: 0, stance: "無法解析回應", risk_level: "medium", conflict_point: "未知", blind_spot: "解析失敗" };

        // 🔍 Debug: 檢查議會回應
        console.log('[ToneSoul] Raw Philosopher:', philosopherRaw?.slice(0, 200));
        console.log('[ToneSoul] Parsed Philosopher:', philosopher);
        console.log('[ToneSoul] Raw Engineer:', engineerRaw?.slice(0, 200));
        console.log('[ToneSoul] Parsed Engineer:', engineer);
        console.log('[ToneSoul] Raw Guardian:', guardianRaw?.slice(0, 200));
        console.log('[ToneSoul] Parsed Guardian:', guardian);

        // ⚡ 使用純程式碼計算真正的 Entropy（不依賴 LLM）
        const codeEntropy = calculateEntropy(philosopher, engineer, guardian);
        console.log('[ToneSoul] Code-based Entropy:', codeEntropy);

        // Phase 2: Synthesizer 綜合（使用深度思考模式）
        setLoadingPhase("Synthesizer 深度整合中...");

        // 使用深度思考 API（16K thinkingBudget）
        const deepCallAPI = getDeepCallAPI();
        const synthesizerAPI = deepCallAPI || callAPI;
        const synthesizerMod = getPersonaModifier(personaConfig, 'synthesizer');

        const synthesizerRaw = await synthesizerAPI(SYNTHESIZER_PROMPT(
            userMessage,
            JSON.stringify(philosopher),
            JSON.stringify(engineer),
            JSON.stringify(guardian)
        ) + synthesizerMod);

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
            entropy_analysis: codeEntropy, // 使用程式碼計算的 Entropy 作為回退
            decision_matrix: { user_hidden_intent: "未知", ai_strategy_name: "標準回應", intended_effect: "未知", tone_tag: "neutral" },
            final_response: synthesizerRaw || "抱歉，我無法生成回應。請重試。",
            next_moves: []
        };

        console.log('[ToneSoul] Multiplex Conclusion:', synthesizer.multiplex_conclusion);

        // 🧠 RFC-003: Blend Math Entropy with AI Self-Diagnosed Tension (Observer Pattern)
        const avgSelfDiagnosed = (
            (philosopher.self_diagnosed_tension || 0) +
            (engineer.self_diagnosed_tension || 0) +
            (guardian.self_diagnosed_tension || 0)
        ) / 3;

        const blendedTension = Math.max(0, Math.min(1, (avgSelfDiagnosed * 0.7) + (codeEntropy.value * 0.3)));

        const finalEntropy = {
            value: Number.isNaN(blendedTension) ? codeEntropy.value : blendedTension,
            status: codeEntropy.status,
            calculation_note: `Math Entropy: ${codeEntropy.value.toFixed(2)}, AI Self-Diagnosed Avg: ${avgSelfDiagnosed.toFixed(2)} -> Blended: ${blendedTension.toFixed(2)}`
        };

        // 🔮 TensionTensor 計算 (Yu-Hun 模型: T = W × E × D)
        const hasRiskWarning = guardian.risk_level === 'high' ||
            guardian.stance.includes('風險') ||
            guardian.stance.includes('危險');
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

        // 組裝完整的審議數據
        const deliberation: DeliberationData = {
            council_chamber: {
                philosopher: {
                    internal_monologue: philosopher.internal_monologue,
                    self_diagnosed_tension: philosopher.self_diagnosed_tension,
                    stance: philosopher.stance,
                    conflict_point: philosopher.blind_spot,
                    benevolence_check: philosopher.benevolence_check
                },
                engineer: {
                    internal_monologue: engineer.internal_monologue,
                    self_diagnosed_tension: engineer.self_diagnosed_tension,
                    stance: engineer.stance,
                    conflict_point: engineer.blind_spot,
                    benevolence_check: engineer.benevolence_check
                },
                guardian: {
                    internal_monologue: guardian.internal_monologue,
                    self_diagnosed_tension: guardian.self_diagnosed_tension,
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
                // 程式碼交叉驗證 LLM 的 Audit 自評
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
                    formula_ref: synthesizer.multiplex_conclusion.tension?.formula_ref || 'ΔT = 未計算',
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

        // 🔮 Soul Auditor: 審計最終回應是否符合 SOUL.md
        const previousResponses = messages
            .filter(m => m.role === 'assistant')
            .map(m => m.content || '')
            .slice(-5);

        const auditResult = auditOutput(
            userMessage,
            synthesizer.final_response,
            previousResponses
        );

        // 記錄審計日誌
        saveAuditLog({
            sessionId: conversation?.id || 'unknown',
            turn: messages.length,
            input: userMessage,
            output: synthesizer.final_response,
            result: auditResult,
        });

        // 如果有嚴重違規，附加警告
        let finalResponse = synthesizer.final_response;
        if (!auditResult.passed && auditResult.violations.some(v => v.severity === 'high')) {
            console.warn('[Auditor] High severity violation detected!');
            finalResponse += '\n\n---\n⚠️ *審計注意: ' + auditResult.auditNote + '*';
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
    ): Promise<ChatRunResult> => {
        if (!apiSettings?.apiKey) {
            return {
                response: "請先設定 API Key 才能使用 AI 對話功能。點擊側邊欄的 API 設定按鈕。",
                deliberation: undefined,
                executionProfile: apiSettings?.mode === "fast" ? "interactive" : "engineering",
            };
        }

        if (apiSettings.mode === "fast") {
            const fastResult = await performFastMode(userMessage);
            return {
                ...fastResult,
                executionProfile: "interactive",
            };
        }
        const deliberationResult = await performMultiPathDeliberation(userMessage);
        return {
            response: deliberationResult.response,
            deliberation: deliberationResult.deliberation,
            executionProfile: "engineering",
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
        setLoadingPhase(USE_BACKEND_CHAT ? "同步後端中..." : (apiSettings?.mode === "fast" ? "思考中..." : "啟動審議..."));

        try {
            let result: ChatRunResult;

            if (USE_BACKEND_CHAT) {
                const fullAnalysis = apiSettings?.mode !== "fast";
                const executionProfile: BackendExecutionProfile =
                    apiSettings?.mode === "fast" ? "interactive" : "engineering";
                try {
                    result = await callBackendChat(
                        userMessage.content,
                        fullAnalysis,
                        executionProfile
                    );
                } catch (backendErr) {
                    if (ENABLE_PROVIDER_FALLBACK) {
                        console.warn("[ToneSoul] Backend chat unavailable, fallback to legacy provider flow.", backendErr);
                        result = await runLegacyProviderFlow(userMessage.content);
                    } else {
                        throw backendErr;
                    }
                }
            } else {
                result = await runLegacyProviderFlow(userMessage.content);
            }

            const assistantMessage: Message = {
                id: `msg_${Date.now()}_ai`,
                role: "assistant",
                content: result.response,
                deliberation: result.deliberation,
                backend_mode: result.backendMode,
                deliberation_level: result.deliberationLevel,
                execution_profile: result.executionProfile,
                fallback_metadata: result.fallbackMetadata,
                distillation_guard: result.distillationGuard,
                governance_brief: result.governanceBrief,
                life_entry_brief: result.lifeEntryBrief,
                timestamp: new Date(),
            };

            const newMessages = [...messages, userMessage, assistantMessage];
            setMessages(newMessages.map(m => ({ ...m, timestamp: new Date(m.timestamp) })));

            // 儲存到 IndexedDB
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
            await saveConversation(updatedConversation);
            onConversationUpdate(updatedConversation);

            // 更新靈魂狀態（張力積分 + 內在驅動）
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

            // 自動展開最新的審議
            setExpandedNodes(prev => new Set(prev).add(assistantMessage.id));

        } catch (error) {
            console.error("Chat error:", error);
            const errorMessage: Message = {
                id: `msg_${Date.now()}_error`,
                role: "assistant",
                content: `錯誤：${error instanceof Error ? error.message : "連線失敗"}`,
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

    const governanceCapability = governanceStatus?.governance_capability ?? "unknown";
    const governanceBadgeLabel = governanceStatusError
        ? "Unavailable"
        : governanceStatusLoading
            ? "Checking"
            : governanceCapability === "runtime_ready"
                ? "Runtime Ready"
                : governanceCapability === "mock_only"
                    ? "Mock Only"
                    : "Unknown";
    const governanceBadgeClass = governanceStatusError
        ? "bg-rose-100 text-rose-700 border-rose-200"
        : governanceCapability === "runtime_ready"
            ? "bg-emerald-100 text-emerald-700 border-emerald-200"
            : governanceCapability === "mock_only"
                ? "bg-amber-100 text-amber-700 border-amber-200"
                : "bg-slate-100 text-slate-700 border-slate-200";

    if (!conversation) {
        return (
            <div className="flex flex-col h-full bg-slate-50 items-center justify-center text-slate-400">
                <MessageSquare className="w-16 h-16 mb-4 opacity-30" />
                <p className="text-lg font-medium">選擇或建立對話</p>
                <p className="text-sm">從左側選擇現有對話，或點擊「新對話」開始</p>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full bg-slate-50">
            {/* API Key 提醒 */}
            {SHOULD_SHOW_API_KEY_HINT && !apiSettings?.apiKey && (
                <div className="bg-amber-50 border-b border-amber-200 px-4 py-2 flex items-center gap-2 text-sm text-amber-800">
                    <AlertTriangle className="w-4 h-4" />
                    <span>請先設定 API Key 才能使用 AI 對話。點擊側邊欄 API 設定。</span>
                </div>
            )}

            {/* 靈魂狀態指示器 */}
            <div className="bg-white border-b border-slate-200 px-4 py-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs">
                <span className="text-slate-500 font-semibold tracking-wide uppercase">
                    Governance
                </span>
                <span
                    className={`px-2 py-0.5 rounded-full border font-semibold ${governanceBadgeClass}`}
                    title={governanceStatusError || undefined}
                >
                    {governanceBadgeLabel}
                </span>
                <span className="text-slate-500">
                    mode:
                    <span className="ml-1 font-medium text-slate-700">
                        {governanceStatus?.backend_mode || "unknown"}
                    </span>
                </span>
                <span className="text-slate-500">
                    elisa:
                    <span className="ml-1 font-medium text-slate-700">
                        {governanceStatus?.elisa?.contract_version || "n/a"}
                    </span>
                </span>
                <span className="text-slate-400">
                    checked:
                    <span className="ml-1">
                        {governanceStatus?.checked_at
                            ? new Date(governanceStatus.checked_at).toLocaleTimeString()
                            : "pending"}
                    </span>
                </span>
                {governanceStatusError && (
                    <span className="text-rose-600">
                        reason:
                        <span className="ml-1">{governanceStatusError}</span>
                    </span>
                )}
            </div>

            {soulState.totalTurns > 0 && (
                <div className="bg-gray-900/5 border-b border-gray-200 px-4 py-2 flex items-center justify-between">
                    <SoulDriveMeter soulState={soulState} compact />
                    <div className="text-[10px] text-gray-400">
                        Tension ∫: {(soulState.tensionIntegral * 100).toFixed(0)}%
                    </div>
                </div>
            )}

            {/* 訊息列表 */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-64 text-slate-400">
                        <Users className="w-16 h-16 mb-4 opacity-30" />
                        <p className="text-lg font-medium">ToneSoul Multi-Path Deliberation</p>
                        <p className="text-sm">三路並行審議 — 每條訊息調用 4 次 API</p>
                        <p className="text-xs mt-2 text-slate-300">Philosopher × Engineer × Guardian → Synthesizer</p>
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
                                    {/* AI 回應內容 */}
                                    <div className="p-5">
                                        <p className="text-slate-800 leading-relaxed text-lg">
                                            {message.content}
                                        </p>
                                    </div>

                                    {/* 內在審議展開區 */}
                                    {message.deliberation && (
                                        <>
                                            <div className="border-t border-slate-100">
                                                <button
                                                    onClick={() => toggleDeliberation(message.id)}
                                                    className="w-full px-5 py-3 flex items-center justify-between text-sm text-slate-500 hover:bg-slate-50 transition-colors"
                                                >
                                                    <span className="flex items-center gap-2">
                                                        <Brain className="w-4 h-4" />
                                                        多路徑審議 (4 次獨立 API 調用)
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
                                                    {/* Governance Status Bar (Phase 109) */}
                                                    <div className="bg-white/60 p-4 rounded-lg border border-slate-200 shadow-sm flex flex-col gap-2">
                                                        <div className="flex items-center justify-between">
                                                            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1">
                                                                <AlertTriangle className="w-3 h-3" />
                                                                治理狀態 (Governance Visibility)
                                                            </span>
                                                            {message.deliberation_level === "mock" ? (
                                                                <span className="px-2 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-700 border border-amber-200">
                                                                    Mock Fallback
                                                                </span>
                                                            ) : (
                                                                <span className="px-2 py-1 rounded-full text-xs font-bold bg-indigo-100 text-indigo-700 border border-indigo-200">
                                                                    Runtime Deliberation
                                                                </span>
                                                            )}
                                                        </div>
                                                        <div className="flex items-center gap-4 text-xs text-slate-600">
                                                            <div>
                                                                <span className="text-slate-400">Mode: </span>
                                                                <span className="font-medium">{message.backend_mode || "unknown"}</span>
                                                            </div>
                                                            <div>
                                                                <span className="text-slate-400">Profile: </span>
                                                                <span className="font-medium">
                                                                    {message.execution_profile || "interactive"}
                                                                </span>
                                                            </div>
                                                            {message.distillation_guard && (
                                                                <div>
                                                                    <span className="text-slate-400">Guard: </span>
                                                                    <span className={`font-medium ${message.distillation_guard.level === 'high' ? 'text-rose-600' : message.distillation_guard.level === 'medium' ? 'text-amber-600' : 'text-emerald-600'}`}>
                                                                        {message.distillation_guard.level}
                                                                        {message.distillation_guard.policy_action !== 'normal' && ` (${message.distillation_guard.policy_action})`}
                                                                    </span>
                                                                    {message.distillation_guard.signals && message.distillation_guard.signals.length > 0 && (
                                                                        <span className="ml-1 text-[10px] text-slate-400">
                                                                            [{message.distillation_guard.signals.join(', ')}]
                                                                        </span>
                                                                    )}
                                                                </div>
                                                            )}
                                                            {message.fallback_metadata?.triggered && (
                                                                <div>
                                                                    <span className="text-slate-400">Fallback Reason: </span>
                                                                    <span className="font-medium text-amber-600">
                                                                        {message.fallback_metadata.reason || "unknown"}
                                                                    </span>
                                                                </div>
                                                            )}
                                                            {message.deliberation?.quality && (
                                                                <div>
                                                                    <span className="text-slate-400">Quality: </span>
                                                                    <span className={`font-medium ${message.deliberation.quality.band === 'high' ? 'text-emerald-600' : 'text-amber-600'}`}>
                                                                        {message.deliberation.quality.score} ({message.deliberation.quality.band})
                                                                    </span>
                                                                </div>
                                                            )}
                                                        </div>
                                                    </div>
                                                    {/* Governance Brief (Phase 532) */}
                                                    {message.governance_brief && (
                                                        <div className="bg-white/60 p-4 rounded-lg border border-violet-200 shadow-sm">
                                                            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                                                                <Users className="w-3 h-3" />
                                                                治理摘要 (Governance Brief)
                                                            </div>
                                                            <div className="grid grid-cols-2 gap-x-6 gap-y-1 text-xs text-slate-700">
                                                                {message.governance_brief.verdict && (
                                                                    <div className="flex gap-1">
                                                                        <span className="text-slate-400 shrink-0">裁決:</span>
                                                                        <span className="font-medium capitalize">{message.governance_brief.verdict}</span>
                                                                    </div>
                                                                )}
                                                                {message.governance_brief.responsibility_tier && (
                                                                    <div className="flex gap-1">
                                                                        <span className="text-slate-400 shrink-0">責任層:</span>
                                                                        <span className="font-medium">{message.governance_brief.responsibility_tier}</span>
                                                                    </div>
                                                                )}
                                                                {message.governance_brief.coherence != null && (
                                                                    <div className="flex gap-1">
                                                                        <span className="text-slate-400 shrink-0">一致性:</span>
                                                                        <span className="font-medium">{(message.governance_brief.coherence * 100).toFixed(0)}%</span>
                                                                    </div>
                                                                )}
                                                                {message.governance_brief.soul_passed != null && (
                                                                    <div className="flex gap-1">
                                                                        <span className="text-slate-400 shrink-0">靈魂通過:</span>
                                                                        <span className={`font-medium ${message.governance_brief.soul_passed ? 'text-emerald-600' : 'text-rose-600'}`}>
                                                                            {message.governance_brief.soul_passed ? 'Yes' : 'No'}
                                                                        </span>
                                                                    </div>
                                                                )}
                                                                {message.governance_brief.dispatch_state && (
                                                                    <div className="flex gap-1">
                                                                        <span className="text-slate-400 shrink-0">派送:</span>
                                                                        <span className="font-medium">{message.governance_brief.dispatch_state}</span>
                                                                    </div>
                                                                )}
                                                                {message.governance_brief.strategy && (
                                                                    <div className="col-span-2 flex gap-1">
                                                                        <span className="text-slate-400 shrink-0">策略:</span>
                                                                        <span className="italic">{message.governance_brief.strategy}</span>
                                                                    </div>
                                                                )}
                                                                {message.governance_brief.next_focus && (
                                                                    <div className="col-span-2 flex gap-1">
                                                                        <span className="text-slate-400 shrink-0">下一焦點:</span>
                                                                        <span className="italic">{message.governance_brief.next_focus}</span>
                                                                    </div>
                                                                )}
                                                            </div>
                                                        </div>
                                                    )}
                                                    {/* Life Entry Brief (Phase 532) */}
                                                    {message.life_entry_brief && (
                                                        <div className="bg-white/60 p-4 rounded-lg border border-teal-200 shadow-sm">
                                                            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                                                                <MessageSquare className="w-3 h-3" />
                                                                生命日誌摘要 (Life Entry Brief)
                                                            </div>
                                                            <div className="space-y-1 text-xs text-slate-700">
                                                                {message.life_entry_brief.response_summary && (
                                                                    <p className="text-slate-600 italic border-l-2 border-teal-200 pl-2">
                                                                        {message.life_entry_brief.response_summary}
                                                                    </p>
                                                                )}
                                                                <div className="grid grid-cols-2 gap-x-6 gap-y-1 mt-2">
                                                                    {message.life_entry_brief.inner_intent && (
                                                                        <div className="flex gap-1">
                                                                            <span className="text-slate-400 shrink-0">內在意圖:</span>
                                                                            <span>{message.life_entry_brief.inner_intent}</span>
                                                                        </div>
                                                                    )}
                                                                    {message.life_entry_brief.persona_mode && (
                                                                        <div className="flex gap-1">
                                                                            <span className="text-slate-400 shrink-0">人格模式:</span>
                                                                            <span className="font-medium">{message.life_entry_brief.persona_mode}</span>
                                                                        </div>
                                                                    )}
                                                                    {message.life_entry_brief.trajectory_label && (
                                                                        <div className="flex gap-1">
                                                                            <span className="text-slate-400 shrink-0">軌跡:</span>
                                                                            <span className="font-medium">{message.life_entry_brief.trajectory_label}</span>
                                                                        </div>
                                                                    )}
                                                                    {message.life_entry_brief.strategy && (
                                                                        <div className="flex gap-1">
                                                                            <span className="text-slate-400 shrink-0">策略:</span>
                                                                            <span>{message.life_entry_brief.strategy}</span>
                                                                        </div>
                                                                    )}
                                                                    {(message.life_entry_brief.self_commit_count != null
                                                                        || message.life_entry_brief.rupture_count != null
                                                                        || message.life_entry_brief.emergent_value_count != null) && (
                                                                        <div className="col-span-2 flex gap-4 mt-1">
                                                                            {message.life_entry_brief.self_commit_count != null && (
                                                                                <span className="text-slate-400">承諾: <b className="text-slate-700">{message.life_entry_brief.self_commit_count}</b></span>
                                                                            )}
                                                                            {message.life_entry_brief.rupture_count != null && (
                                                                                <span className="text-slate-400">斷裂: <b className="text-slate-700">{message.life_entry_brief.rupture_count}</b></span>
                                                                            )}
                                                                            {message.life_entry_brief.emergent_value_count != null && (
                                                                                <span className="text-slate-400">湧現值: <b className="text-slate-700">{message.life_entry_brief.emergent_value_count}</b></span>
                                                                            )}
                                                                        </div>
                                                                    )}
                                                                </div>
                                                            </div>
                                                        </div>
                                                    )}
                                                    {/* 張力儀表 */}
                                                    {message.deliberation.entropy_meter && (
                                                        <SoulStateMeter
                                                            value={message.deliberation.entropy_meter.value}
                                                            calculationNote={message.deliberation.entropy_meter.calculation_note}
                                                        />
                                                    )}

                                                    {/* 議會廳 */}
                                                    {(message.deliberation.council_chamber || (message.deliberation.role_tensions && message.deliberation.role_tensions.length > 0)) && (
                                                        <CouncilChamber
                                                            philosopher={message.deliberation.council_chamber?.philosopher}
                                                            engineer={message.deliberation.council_chamber?.engineer}
                                                            guardian={message.deliberation.council_chamber?.guardian}
                                                            role_tensions={message.deliberation.role_tensions}
                                                            recommended_action={message.deliberation.recommended_action}
                                                        />
                                                    )}

                                                    {/* 戰術儀表板 */}
                                                    {message.deliberation.decision_matrix && (
                                                        <TacticalDashboard matrix={{
                                                            user_hidden_intent: message.deliberation.decision_matrix.user_hidden_intent,
                                                            ai_strategy_name: message.deliberation.decision_matrix.ai_strategy_name,
                                                            intended_effect: message.deliberation.decision_matrix.intended_effect,
                                                            tone_tag: message.deliberation.decision_matrix.tone_tag,
                                                        }} />
                                                    )}

                                                    {/* vMT-2601 邏輯陰影 */}
                                                    {message.deliberation.multiplex_conclusion && (
                                                        <LogicalShadows data={message.deliberation.multiplex_conclusion} />
                                                    )}

                                                    {/* 審計報告 */}
                                                    {message.deliberation.audit && (
                                                        <div className="bg-white/60 p-4 rounded-lg border border-emerald-200">
                                                            <div className="flex items-center justify-between mb-3">
                                                                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                                                                    倫理審計 (Audit)
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
                                                                    <span className="text-xs text-slate-500">誠實分數:</span>
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

                                                    {/* 語義矛盾列表 */}
                                                    {Array.isArray(message.deliberation.semantic_contradictions)
                                                        && message.deliberation.semantic_contradictions.length > 0 && (
                                                            <div className="bg-white/60 p-4 rounded-lg border border-rose-200">
                                                                <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-3">
                                                                    語義矛盾 (Semantic Contradictions)
                                                                </div>
                                                                <div className="space-y-2">
                                                                    {message.deliberation.semantic_contradictions.slice(0, 5).map((row, idx) => {
                                                                        const item = row && typeof row === "object"
                                                                            ? (row as Record<string, unknown>)
                                                                            : {};
                                                                        const description = typeof item.description === "string"
                                                                            ? item.description
                                                                            : (typeof item.summary === "string"
                                                                                ? item.summary
                                                                                : JSON.stringify(item));
                                                                        return (
                                                                            <div key={idx} className="text-xs text-slate-700 bg-rose-50 rounded-md border border-rose-100 px-3 py-2">
                                                                                {description || "Detected contradiction without description."}
                                                                            </div>
                                                                        );
                                                                    })}
                                                                </div>
                                                            </div>
                                                        )}

                                                    {/* 語義圖譜摘要 */}
                                                    {message.deliberation.semantic_graph_summary
                                                        && Object.keys(message.deliberation.semantic_graph_summary).length > 0 && (
                                                            <div className="bg-white/60 p-4 rounded-lg border border-indigo-200">
                                                                <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-3">
                                                                    語義圖譜摘要 (Semantic Graph Summary)
                                                                </div>
                                                                <pre className="text-xs text-slate-700 whitespace-pre-wrap break-words bg-indigo-50 border border-indigo-100 rounded-md p-3 overflow-x-auto">
                                                                    {JSON.stringify(message.deliberation.semantic_graph_summary, null, 2)}
                                                                </pre>
                                                            </div>
                                                        )}

                                                    {/* 視覺鏈快照 */}
                                                    {message.deliberation.visual_chain_snapshot
                                                        && (
                                                            !!message.deliberation.visual_chain_snapshot.title
                                                            || !!message.deliberation.visual_chain_snapshot.mermaid
                                                            || (
                                                                message.deliberation.visual_chain_snapshot.data
                                                                && Object.keys(message.deliberation.visual_chain_snapshot.data).length > 0
                                                            )
                                                        ) && (
                                                            <div className="bg-white/60 p-4 rounded-lg border border-cyan-200">
                                                                <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2">
                                                                    視覺鏈快照 (Visual Chain Snapshot)
                                                                </div>
                                                                {message.deliberation.visual_chain_snapshot.title && (
                                                                    <p className="text-xs text-slate-700 mb-2">
                                                                        {message.deliberation.visual_chain_snapshot.title}
                                                                    </p>
                                                                )}
                                                                {message.deliberation.visual_chain_snapshot.mermaid && (
                                                                    <pre className="text-xs text-slate-700 whitespace-pre-wrap break-words bg-cyan-50 border border-cyan-100 rounded-md p-3 overflow-x-auto mb-2">
                                                                        {message.deliberation.visual_chain_snapshot.mermaid}
                                                                    </pre>
                                                                )}
                                                                {message.deliberation.visual_chain_snapshot.data
                                                                    && Object.keys(message.deliberation.visual_chain_snapshot.data).length > 0 && (
                                                                        <pre className="text-xs text-slate-700 whitespace-pre-wrap break-words bg-cyan-50 border border-cyan-100 rounded-md p-3 overflow-x-auto">
                                                                            {JSON.stringify(message.deliberation.visual_chain_snapshot.data, null, 2)}
                                                                        </pre>
                                                                    )}
                                                            </div>
                                                        )}
                                                </div>
                                            )}

                                            {/* 建議跟進 */}
                                            {message.deliberation.next_moves && message.deliberation.next_moves.length > 0 && (
                                                <div className="px-5 pb-4 flex flex-wrap gap-2 border-t border-slate-100 pt-3">
                                                    {message.deliberation.next_moves.map((move, idx) => (
                                                        <button
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

            {/* 輸入區 */}
            <div className="p-4 border-t border-slate-200 bg-white">
                <div className="flex gap-3">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
                        placeholder="輸入訊息以啟動三路審議..."
                        disabled={isLoading}
                        className="flex-1 px-4 py-3 bg-slate-100 rounded-xl border-0 focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all disabled:opacity-50"
                    />
                    <button
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

