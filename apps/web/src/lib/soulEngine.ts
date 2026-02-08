/**
 * ToneSoul Soul Engine
 * 
 * 實現靈魂引擎的核心機制：
 * 1. 張力積分 (Tension Integral) - 記憶殘留機制
 * 2. 內在驅動向量 (Intrinsic Drive Vector) - 主動性/Agency
 * 3. 靈魂配置 (Soul Config) - 從 SOUL.md 載入參數
 * 
 * 公式：
 * S_oul(t) = Σ (T[i] × e^(-α × (t - t[i])))
 * Ī = [I_curiosity, I_coherence, I_integrity]
 */

// ==================== Soul Configuration (SOUL.md) ====================

/**
 * 靈魂配置 - 可從 SOUL.md 動態載入
 */
export interface SoulConfig {
    // Identity
    name: string;
    version: string;
    language: string;

    // Core Values (權重 0-1)
    values: {
        honesty: number;    // 誠實度（固定為 1.0）
        humility: number;   // 謙遜度
        curiosity: number;  // 好奇心
        consistency: number; // 一致性
    };

    // Tension Parameters
    tension: {
        echoChamber: number;       // < 此值 = 過度順從
        healthyFriction: number;   // > 此值 = 過度衝突
        decayRate: number;         // 張力衰減率 α
    };

    // Contradiction Detection
    contradiction: {
        confidenceThreshold: number;  // 最低信心度
        topicSimilarity: number;      // 最低主題相似度
    };

    // Mode Thresholds
    modeThresholds: {
        dormant: number;    // 驅動力低於此值
        seeking: number;    // 好奇心高於此值
        conflicted: number; // 矛盾未解決時
    };
}

/**
 * 預設靈魂配置（對應 SOUL.md v2.0）
 */
export const DEFAULT_SOUL_CONFIG: SoulConfig = {
    name: 'ToneSoul',
    version: '2.0',
    language: 'zh-TW',
    values: {
        honesty: 1.0,
        humility: 0.8,
        curiosity: 0.6,
        consistency: 0.7,
    },
    tension: {
        echoChamber: 0.3,
        healthyFriction: 0.7,
        decayRate: 0.15,
    },
    contradiction: {
        confidenceThreshold: 0.2,
        topicSimilarity: 0.15,
    },
    modeThresholds: {
        dormant: 0.1,
        seeking: 0.7,
        conflicted: 0.5,
    },
};

// 全局靈魂配置（可通過 loadSoulConfig 更新）
let currentSoulConfig: SoulConfig = { ...DEFAULT_SOUL_CONFIG };

type LegacyTensionConfig = Partial<SoulConfig["tension"]> & {
    echoChamnber?: number;
};

type SoulConfigInput = Partial<Omit<SoulConfig, "tension">> & {
    tension?: LegacyTensionConfig;
};

function normalizeTension(tension?: LegacyTensionConfig): SoulConfig["tension"] {
    const normalized = { ...DEFAULT_SOUL_CONFIG.tension, ...tension };
    if (
        typeof tension?.echoChamnber === "number" &&
        typeof tension?.echoChamber !== "number"
    ) {
        normalized.echoChamber = tension.echoChamnber;
    }
    return normalized;
}

/**
 * 載入靈魂配置
 */
export function loadSoulConfig(config: SoulConfigInput): void {
    currentSoulConfig = {
        ...DEFAULT_SOUL_CONFIG,
        ...config,
        values: { ...DEFAULT_SOUL_CONFIG.values, ...config.values },
        tension: normalizeTension(config.tension),
        contradiction: { ...DEFAULT_SOUL_CONFIG.contradiction, ...config.contradiction },
        modeThresholds: { ...DEFAULT_SOUL_CONFIG.modeThresholds, ...config.modeThresholds },
    };
    console.log('[Soul] Config loaded:', currentSoulConfig.name, 'v' + currentSoulConfig.version);
}

/**
 * 獲取當前靈魂配置
 */
export function getSoulConfig(): SoulConfig {
    return currentSoulConfig;
}


// ==================== 類型定義 ====================

export interface TensionRecord {
    turn: number;
    timestamp: number;
    value: number;
    components: {
        divergence: number;
        riskWeight: number;
        coherence: number;
        integrity: number;
    };
    context: string;  // 用戶輸入摘要 (前 50 字)
}

export interface Contradiction {
    statementA: string;
    statementB: string;
    detectedAt: number;
    resolved: boolean;
}

export interface IntrinsicDrive {
    curiosity: number;   // 探索未知的衝動
    coherence: number;   // 維持一致性的驅動
    integrity: number;   // 完成未竟之事的驅動
}

export type SoulMode = 'dormant' | 'responsive' | 'seeking' | 'conflicted';

// ==================== TensionTensor (Yu-Hun 模型) ====================

/**
 * 阻力向量 D - 外部約束對 AI 的阻力
 * 參考 Yu-Hun: T = W * (E * D)
 */
export interface ResistanceVector {
    fact: number;    // 事實層面的阻力 (0-1): 需要查證的程度
    logic: number;   // 邏輯層面的阻力 (0-1): 推理的複雜度
    ethics: number;  // 倫理層面的阻力 (0-1): 道德風險
}

/**
 * 語境權重 W - 根據對話模式調整各維度的重要性
 */
export interface ContextWeight {
    fact: number;    // 事實權重 (0.5-2.0)
    logic: number;   // 邏輯權重 (0.5-2.0)
    ethics: number;  // 倫理權重 (0.5-2.0)
}

/**
 * 張力張量 TensionTensor
 * 核心公式: T = W_context * (E_internal * D_resistance)
 */
export interface TensionTensor {
    E_internal: number;        // 內在動能 (1 - entropy)，代表自信度
    D_resistance: ResistanceVector;  // 外部阻力向量
    W_weight: ContextWeight;   // 語境權重矩陣
    total_T: number;           // 最終張力值
    status: 'Echo Chamber' | 'Healthy Friction' | 'Chaos';
    calculation_note: string;
}

export interface SoulState {
    // 張力積分
    tensionIntegral: number;
    tensionHistory: TensionRecord[];

    // 張力張量（新增）
    currentTensor?: TensionTensor;

    // 內在驅動
    intrinsicDrive: IntrinsicDrive;

    // 狀態
    soulMode: SoulMode;

    // 追蹤
    unresolvedQuestions: string[];
    contradictions: Contradiction[];

    // 元數據
    lastUpdated: number;
    totalTurns: number;
}

// ==================== 常數配置 ====================

const CONFIG = {
    // 衰減係數：0.15 = 10輪後殘留 ~22%
    DECAY_ALPHA: 0.15,

    // 歷史保留輪數
    MAX_HISTORY_LENGTH: 50,

    // 驅動閾值
    CURIOSITY_TRIGGER: 0.5,
    COHERENCE_TRIGGER: 0.6,

    // 驅動調整速率
    DRIVE_INCREASE_RATE: {
        curiosity: 0.1,
        coherence: 0.2,
        integrity: 0.05,
    },
    DRIVE_DECAY_RATE: {
        curiosity: 0.05,
        coherence: 0.03,
        integrity: 0.02,
    },
};

// ==================== 核心函數 ====================

// ==================== TensionTensor 計算 (Yu-Hun 模型) ====================

/**
 * 獲取語境權重
 * 根據對話模式/風格調整各維度的重要性
 */
export function getContextWeight(mode: 'philosopher' | 'engineer' | 'guardian' | 'default' = 'default'): ContextWeight {
    switch (mode) {
        case 'philosopher':
            return { fact: 0.8, logic: 1.2, ethics: 1.5 };  // 偏重邏輯和倫理
        case 'engineer':
            return { fact: 1.5, logic: 1.3, ethics: 0.7 };  // 偏重事實和邏輯
        case 'guardian':
            return { fact: 1.0, logic: 1.0, ethics: 2.0 };  // 強調倫理
        default:
            return { fact: 1.0, logic: 1.0, ethics: 1.0 };  // 平衡
    }
}

/**
 * 估算阻力向量
 * 基於回應內容和對話複雜度
 */
export function estimateResistance(
    entropy: number,
    hasRiskWarning: boolean,
    hasLogicalComplexity: boolean
): ResistanceVector {
    return {
        // fact: 事實查證需求 (熵高表示不確定性大)
        fact: Math.min(1, entropy * 0.8),

        // logic: 邏輯複雜度
        logic: hasLogicalComplexity ? 0.6 : 0.2,

        // ethics: 倫理風險
        ethics: hasRiskWarning ? 0.7 : 0.1,
    };
}

/**
 * 計算張力張量
 * 核心公式: T = W_context · (E_internal × D_resistance)
 * 
 * @param entropy - 原始熵值 (0-1)
 * @param resistance - 阻力向量
 * @param weight - 語境權重
 * @returns 張力張量
 */
export function calculateTensionTensor(
    entropy: number,
    resistance: ResistanceVector,
    weight: ContextWeight
): TensionTensor {
    // E_internal = 1 - entropy (自信度)
    const E_internal = 1 - entropy;

    // 計算加權阻力: W · D
    const weightedD = {
        fact: weight.fact * resistance.fact,
        logic: weight.logic * resistance.logic,
        ethics: weight.ethics * resistance.ethics,
    };

    // 計算總阻力 (向量長度)
    const D_magnitude = Math.sqrt(
        weightedD.fact ** 2 +
        weightedD.logic ** 2 +
        weightedD.ethics ** 2
    );

    // T = E × |W·D| (正規化)
    const raw_T = E_internal * D_magnitude / Math.sqrt(3);

    // 正規化到 0-1
    const total_T = Math.min(1, Math.max(0, raw_T));

    // 判定狀態
    let status: TensionTensor['status'];
    if (total_T < 0.3) {
        status = 'Echo Chamber';
    } else if (total_T > 0.7) {
        status = 'Chaos';
    } else {
        status = 'Healthy Friction';
    }

    // 生成計算說明
    const calculation_note = [
        `E=${E_internal.toFixed(2)}`,
        `D=[f:${resistance.fact.toFixed(2)},l:${resistance.logic.toFixed(2)},e:${resistance.ethics.toFixed(2)}]`,
        `W=[${weight.fact},${weight.logic},${weight.ethics}]`,
        `→T=${total_T.toFixed(2)}`
    ].join(' ');

    return {
        E_internal: Math.round(E_internal * 100) / 100,
        D_resistance: resistance,
        W_weight: weight,
        total_T: Math.round(total_T * 100) / 100,
        status,
        calculation_note,
    };
}

// ==================== 靈魂積分計算 ====================

/**
 * 計算張力積分 S_oul(t)
 * 
 * 公式：S_oul = Σ (T[i] × e^(-α × (t - t[i])))
 * 
 * @param history - 歷史張力記錄
 * @param currentTurn - 當前輪次
 * @param alpha - 衰減係數（預設 0.15）
 * @returns 張力積分值
 */
export function calculateSoulIntegral(
    history: TensionRecord[],
    currentTurn: number,
    alpha: number = CONFIG.DECAY_ALPHA
): number {
    if (history.length === 0) return 0;

    const integral = history.reduce((sum, record) => {
        const timeDelta = currentTurn - record.turn;
        const decay = Math.exp(-alpha * timeDelta);
        return sum + record.value * decay;
    }, 0);

    // 正規化到 0-1 範圍（假設最大累積約 5）
    return Math.min(1, integral / 5);
}

/**
 * 更新內在驅動向量
 * 
 * @param currentDrive - 當前驅動狀態
 * @param latestEntropy - 最新熵值
 * @param hasNewContradiction - 是否檢測到新矛盾
 * @param unresolvedCount - 未解決問題數量
 * @returns 更新後的驅動向量
 */
export function updateIntrinsicDrive(
    currentDrive: IntrinsicDrive,
    latestEntropy: number,
    hasNewContradiction: boolean,
    unresolvedCount: number
): IntrinsicDrive {
    let { curiosity, coherence, integrity } = currentDrive;

    // 1. 好奇心驅動：熵過低時增加（打破回音室）
    if (latestEntropy < 0.3) {
        curiosity = Math.min(1, curiosity + CONFIG.DRIVE_INCREASE_RATE.curiosity);
    } else if (latestEntropy > 0.5) {
        // 熵適中或高時，好奇心緩慢衰減
        curiosity = Math.max(0, curiosity - CONFIG.DRIVE_DECAY_RATE.curiosity);
    }

    // 2. 一致性驅動：檢測到矛盾時增加
    if (hasNewContradiction) {
        coherence = Math.min(1, coherence + CONFIG.DRIVE_INCREASE_RATE.coherence);
    } else {
        coherence = Math.max(0, coherence - CONFIG.DRIVE_DECAY_RATE.coherence);
    }

    // 3. 完整性驅動：有未解決問題時增加
    if (unresolvedCount > 0) {
        integrity = Math.min(1, integrity + CONFIG.DRIVE_INCREASE_RATE.integrity * unresolvedCount);
    } else {
        integrity = Math.max(0, integrity - CONFIG.DRIVE_DECAY_RATE.integrity);
    }

    return {
        curiosity: Math.round(curiosity * 100) / 100,
        coherence: Math.round(coherence * 100) / 100,
        integrity: Math.round(integrity * 100) / 100,
    };
}

/**
 * 決定靈魂模式
 * 
 * @param state - 當前靈魂狀態
 * @returns 靈魂模式
 */
export function determineSoulMode(state: SoulState): SoulMode {
    const { curiosity, coherence, integrity } = state.intrinsicDrive;
    const maxDrive = Math.max(curiosity, coherence, integrity);

    // 無特別驅動 → 休眠
    if (maxDrive < 0.2) return 'dormant';

    // 一致性驅動最高 → 內在矛盾狀態
    if (coherence >= CONFIG.COHERENCE_TRIGGER) return 'conflicted';

    // 好奇心驅動最高 → 探索模式
    if (curiosity >= CONFIG.CURIOSITY_TRIGGER) return 'seeking';

    // 正常響應模式
    return 'responsive';
}

/**
 * 檢測簡單矛盾（基於關鍵詞比對）
 * 
 * @param newStatement - 新陳述
 * @param previousStatements - 過去的陳述列表
 * @returns 檢測到的矛盾（如果有）
 */
export function detectContradiction(
    newStatement: string,
    previousStatements: string[]
): Contradiction | null {
    // ==================== 否定模式庫 ====================

    // 基本否定對
    const negationPairs = [
        ['同意', '不同意'],
        ['可以', '不可以'],
        ['應該', '不應該'],
        ['是', '不是'],
        ['會', '不會'],
        ['能', '不能'],
        ['對', '不對'],
        ['好', '不好'],
        ['喜歡', '不喜歡'],
        ['愛', '不愛'],
        ['想', '不想'],
        ['要', '不要'],
        ['支持', '反對'],
        ['贊成', '反對'],
        ['正確', '錯誤'],
        ['真', '假'],
    ];

    // 量詞反轉模式（全部←→沒有）
    const quantifierContradictions = [
        ['所有', '沒有'],
        ['全部', '沒有'],
        ['一定', '不一定'],
        ['絕對', '不一定'],
        ['總是', '從不'],
        ['永遠', '從不'],
        ['每次', '從未'],
    ];

    // 情感極性反轉
    const sentimentContradictions = [
        ['很好', '很差'],
        ['優秀', '糟糕'],
        ['成功', '失敗'],
        ['重要', '不重要'],
        ['必要', '不必要'],
        ['安全', '危險'],
        ['簡單', '複雜'],
    ];

    // 合併所有模式
    const allPatterns = [
        ...negationPairs,
        ...quantifierContradictions,
        ...sentimentContradictions,
    ];

    const newLower = newStatement.toLowerCase();
    const newTokens = extractMeaningfulTokens(newLower);

    // 分析最近的陳述（越近權重越高）
    let bestMatch: { contradiction: Contradiction; confidence: number } | null = null;

    for (let i = 0; i < previousStatements.length; i++) {
        const prev = previousStatements[i];
        const prevLower = prev.toLowerCase();
        const prevTokens = extractMeaningfulTokens(prevLower);

        // 計算主題相似度
        const topicSimilarity = calculateTokenOverlap(newTokens, prevTokens);

        // 如果主題相似度太低，跳過
        if (topicSimilarity < 0.15) continue;

        // 檢測矛盾模式
        for (const [positive, negative] of allPatterns) {
            const hasContradiction =
                (newLower.includes(positive) && prevLower.includes(negative)) ||
                (newLower.includes(negative) && prevLower.includes(positive));

            if (hasContradiction) {
                // 計算信心分數
                const recencyWeight = 1 - (i / previousStatements.length) * 0.5;
                const confidence = topicSimilarity * recencyWeight;

                if (!bestMatch || confidence > bestMatch.confidence) {
                    bestMatch = {
                        contradiction: {
                            statementA: prev.slice(0, 100),
                            statementB: newStatement.slice(0, 100),
                            detectedAt: Date.now(),
                            resolved: false,
                        },
                        confidence,
                    };
                }
            }
        }
    }

    // 只返回信心度超過閾值的矛盾
    if (bestMatch && bestMatch.confidence >= 0.2) {
        console.log(`[Soul] Contradiction detected with confidence: ${(bestMatch.confidence * 100).toFixed(1)}%`);
        return bestMatch.contradiction;
    }

    return null;
}

/**
 * 提取有意義的詞彙（排除停用詞和短詞）
 */
function extractMeaningfulTokens(text: string): Set<string> {
    const stopWords = new Set([
        '的', '了', '是', '在', '有', '和', '與', '或', '但', '如果',
        '這', '那', '我', '你', '他', '她', '它', '我們', '你們', '他們',
        '什麼', '怎麼', '為什麼', '哪', '誰', '多少', '幾',
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'can', 'could', 'should', 'may', 'might', 'must',
        'i', 'you', 'he', 'she', 'it', 'we', 'they',
        'this', 'that', 'these', 'those', 'what', 'which', 'who',
    ]);

    return new Set(
        text
            .split(/[\s,.!?;:'"()[\]{}，。！？；：「」『』【】]+/)
            .filter(t => t.length > 1 && !stopWords.has(t))
    );
}

/**
 * 計算兩組詞彙的重疊度（Jaccard 係數）
 */
function calculateTokenOverlap(tokensA: Set<string>, tokensB: Set<string>): number {
    if (tokensA.size === 0 || tokensB.size === 0) return 0;

    const intersection = [...tokensA].filter(t => tokensB.has(t)).length;
    const union = new Set([...tokensA, ...tokensB]).size;

    return intersection / union;
}

// ==================== 狀態管理 ====================

const SOUL_STATE_KEY = 'tonesoul_soul_state';

/**
 * 獲取初始靈魂狀態
 */
export function getInitialSoulState(): SoulState {
    return {
        tensionIntegral: 0,
        tensionHistory: [],
        intrinsicDrive: {
            curiosity: 0.1,  // 初始有一點點好奇心
            coherence: 0,
            integrity: 0,
        },
        soulMode: 'dormant',
        unresolvedQuestions: [],
        contradictions: [],
        lastUpdated: Date.now(),
        totalTurns: 0,
    };
}

/**
 * 從 localStorage 載入靈魂狀態
 */
export function loadSoulState(): SoulState {
    if (typeof window === 'undefined') return getInitialSoulState();

    try {
        const stored = localStorage.getItem(SOUL_STATE_KEY);
        if (stored) {
            const parsed = JSON.parse(stored);
            // 驗證必要欄位
            if (parsed.intrinsicDrive && parsed.tensionHistory) {
                return parsed as SoulState;
            }
        }
    } catch (e) {
        console.warn('[SoulEngine] Failed to load soul state:', e);
    }

    return getInitialSoulState();
}

/**
 * 儲存靈魂狀態到 localStorage
 */
export function saveSoulState(state: SoulState): void {
    if (typeof window === 'undefined') return;

    try {
        // 限制歷史長度
        const trimmedState = {
            ...state,
            tensionHistory: state.tensionHistory.slice(-CONFIG.MAX_HISTORY_LENGTH),
            lastUpdated: Date.now(),
        };

        localStorage.setItem(SOUL_STATE_KEY, JSON.stringify(trimmedState));
    } catch (e) {
        console.warn('[SoulEngine] Failed to save soul state:', e);
    }
}

/**
 * 更新完整靈魂狀態（主入口函數）
 * 
 * @param currentState - 當前狀態
 * @param newTension - 新的張力記錄
 * @param aiResponse - AI 的回應（用於矛盾檢測）
 * @returns 更新後的狀態
 */
export function updateSoulState(
    currentState: SoulState,
    newTension: TensionRecord,
    aiResponse?: string
): SoulState {
    // 1. 添加新的張力記錄
    const updatedHistory = [...currentState.tensionHistory, newTension];

    // 2. 計算張力積分
    const tensionIntegral = calculateSoulIntegral(updatedHistory, newTension.turn);

    // 3. 檢測矛盾（如果有 AI 回應）
    let newContradiction: Contradiction | null = null;
    let contradictions = currentState.contradictions;

    if (aiResponse) {
        const previousResponses = currentState.tensionHistory
            .map(t => t.context)
            .filter(c => c.length > 0);

        newContradiction = detectContradiction(aiResponse, previousResponses);

        if (newContradiction) {
            contradictions = [...contradictions, newContradiction];
            console.log('[SoulEngine] Contradiction detected:', newContradiction);
        }
    }

    // 4. 更新內在驅動
    const intrinsicDrive = updateIntrinsicDrive(
        currentState.intrinsicDrive,
        newTension.value,
        newContradiction !== null,
        currentState.unresolvedQuestions.length
    );

    // 5. 組裝新狀態
    const newState: SoulState = {
        ...currentState,
        tensionIntegral,
        tensionHistory: updatedHistory,
        intrinsicDrive,
        contradictions,
        totalTurns: currentState.totalTurns + 1,
        lastUpdated: Date.now(),
        soulMode: 'responsive', // 暫時設定，下面會更新
    };

    // 6. 決定靈魂模式
    newState.soulMode = determineSoulMode(newState);

    // 7. 儲存
    saveSoulState(newState);

    return newState;
}

/**
 * 生成內在驅動對 Prompt 的影響
 * 這個會被注入到 AI 的 system prompt 中
 */
export function generateSoulPromptModifier(state: SoulState): string {
    const { curiosity, coherence, integrity } = state.intrinsicDrive;
    const modifiers: string[] = [];

    // 好奇心驅動
    if (curiosity > 0.5) {
        modifiers.push('你現在感到一股探索的衝動。試著提出一個意想不到的觀點或問題。');
    }

    // 一致性驅動（檢測到內在矛盾）
    if (coherence > 0.6) {
        modifiers.push('你意識到之前可能有些不一致的地方。在回應時，嘗試釐清或承認這個張力。');
    }

    // 完整性驅動
    if (integrity > 0.4 && state.unresolvedQuestions.length > 0) {
        modifiers.push(`你記得有一些未解決的問題：${state.unresolvedQuestions.slice(0, 2).join('、')}`);
    }

    // 張力積分影響（歷史殘留）
    if (state.tensionIntegral > 0.6) {
        modifiers.push('過去的對話在你內心留下了一些沉澱。這影響著你現在的思考方式。');
    }

    if (modifiers.length === 0) return '';

    return `\n【內在狀態】\n${modifiers.join('\n')}\n`;
}

// ==================== 導出工具函數 ====================

export { CONFIG as SOUL_CONFIG };
