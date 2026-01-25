/**
 * ToneSoul Entropy Calculator
 * 
 * 基於 SEMANTIC_SPINE_SPEC 的概念實現純程式碼的張力計算
 * 不需要 Embedding API，使用結構化分析
 * 
 * 核心概念：
 * - D₁ Curiosity Drive: 新穎度/不確定性
 * - D₂ Narrative Coherence: 敘事一致性
 * - D₃ Integrity Drive: 完整性/可追溯性
 */

// ==================== 類型定義 ====================

interface CouncilMemberResponse {
    stance: string;
    blind_spot: string;
    // Philosopher 特有
    core_value?: string;
    // Engineer 特有
    feasibility?: string;
    // Guardian 特有
    risk_level?: string;
    conflict_point?: string;
}

interface EntropyAnalysis {
    value: number;           // 0.0 - 1.0
    status: 'Echo Chamber' | 'Healthy Friction' | 'Chaos';
    calculation_note: string;
    components: {
        divergence: number;    // 視角分歧度
        risk_weight: number;   // 風險加權
        coherence: number;     // 敘事一致性
        integrity: number;     // 完整性
    };
}

// ==================== 工具函數 ====================

/**
 * 計算兩個文字的簡單相似度（基於共同詞彙）
 * 這是一個啟發式方法，不需要 Embedding API
 */
function calculateTextSimilarity(text1: string, text2: string): number {
    if (!text1 || !text2) return 0;

    // 中英文分詞（簡單版本）
    const tokenize = (text: string): Set<string> => {
        const cleaned = text.toLowerCase()
            .replace(/[^\u4e00-\u9fa5a-z0-9]/g, ' ')
            .split(/\s+/)
            .filter(t => t.length > 1);
        return new Set(cleaned);
    };

    const tokens1 = tokenize(text1);
    const tokens2 = tokenize(text2);

    if (tokens1.size === 0 || tokens2.size === 0) return 0;

    // Jaccard 相似度
    const intersection = new Set([...tokens1].filter(t => tokens2.has(t)));
    const union = new Set([...tokens1, ...tokens2]);

    return intersection.size / union.size;
}

/**
 * 計算三個視角之間的分歧度
 * 分歧度高 = Entropy 高
 */
function calculateDivergence(
    philosopher: CouncilMemberResponse,
    engineer: CouncilMemberResponse,
    guardian: CouncilMemberResponse
): number {
    // 計算兩兩之間的相似度
    const simPE = calculateTextSimilarity(philosopher.stance, engineer.stance);
    const simPG = calculateTextSimilarity(philosopher.stance, guardian.stance);
    const simEG = calculateTextSimilarity(engineer.stance, guardian.stance);

    // 平均相似度
    const avgSimilarity = (simPE + simPG + simEG) / 3;

    // 分歧度 = 1 - 相似度
    return 1 - avgSimilarity;
}

/**
 * 計算風險加權
 * Guardian 的 risk_level 影響最終 Entropy
 */
function calculateRiskWeight(guardian: CouncilMemberResponse): number {
    const riskLevel = guardian.risk_level?.toLowerCase() || 'medium';

    switch (riskLevel) {
        case 'high': return 0.3;     // 高風險 → 高 Entropy
        case 'medium': return 0.1;   // 中風險 → 中等 Entropy
        case 'low': return -0.1;     // 低風險 → 低 Entropy
        default: return 0.1;
    }
}

/**
 * 計算敘事一致性（D₂）
 * 基於 SEMANTIC_SPINE_SPEC 的 NarrativeEntropy 概念
 */
function calculateCoherence(
    philosopher: CouncilMemberResponse,
    engineer: CouncilMemberResponse,
    guardian: CouncilMemberResponse
): number {
    // 檢查盲點是否互補（健康的多視角）
    const blindSpots = [
        philosopher.blind_spot || '',
        engineer.blind_spot || '',
        guardian.blind_spot || ''
    ].filter(b => b.length > 0);

    // 如果三者都承認自己的盲點 = 更高的一致性
    const selfAwareness = blindSpots.length / 3;

    // 如果盲點內容互相指出對方 = 健康的摩擦
    const blindSpotOverlap = calculateTextSimilarity(
        blindSpots.join(' '),
        [philosopher.stance, engineer.stance, guardian.stance].join(' ')
    );

    // 一致性 = 自我覺察度 * (1 - 盲點重疊)
    return selfAwareness * (1 - blindSpotOverlap);
}

/**
 * 計算完整性（D₃）
 * 檢查回應是否有充分支撐
 */
function calculateIntegrity(
    philosopher: CouncilMemberResponse,
    engineer: CouncilMemberResponse,
    guardian: CouncilMemberResponse
): number {
    let score = 1.0;

    // 檢查必要欄位是否完整
    if (!philosopher.stance || philosopher.stance.includes('無法解析')) score -= 0.2;
    if (!engineer.stance || engineer.stance.includes('無法解析')) score -= 0.2;
    if (!guardian.stance || guardian.stance.includes('無法解析')) score -= 0.2;

    // 檢查 Engineer 是否有可行性分析
    if (engineer.feasibility && engineer.feasibility.length > 10) score += 0.1;

    // 檢查 Guardian 是否有風險評估
    if (guardian.risk_level) score += 0.1;

    return Math.max(0, Math.min(1, score));
}

// ==================== 主計算函數 ====================

/**
 * 計算認知張力 (Entropy)
 * 
 * 公式：E = w1*Divergence + w2*RiskWeight + w3*(1-Coherence) + w4*(1-Integrity)
 * 
 * 其中：
 * - Divergence: 視角分歧度 (0-1)
 * - RiskWeight: 風險加權 (-0.1 ~ 0.3)
 * - Coherence: 敘事一致性 (0-1)
 * - Integrity: 完整性 (0-1)
 */
export function calculateEntropy(
    philosopher: CouncilMemberResponse,
    engineer: CouncilMemberResponse,
    guardian: CouncilMemberResponse
): EntropyAnalysis {
    // 計算各組件
    const divergence = calculateDivergence(philosopher, engineer, guardian);
    const riskWeight = calculateRiskWeight(guardian);
    const coherence = calculateCoherence(philosopher, engineer, guardian);
    const integrity = calculateIntegrity(philosopher, engineer, guardian);

    // 新公式：使用加權平均確保結果在 0-1 範圍
    // E = 基礎分 + (分歧度貢獻 + 風險貢獻 - 一致性貢獻 - 完整性貢獻)

    // 分歧度貢獻：0 ~ 0.2（降低權重，因為三個人格天然文字不同）
    const divergenceContrib = divergence * 0.2;

    // 風險貢獻：-0.05 ~ 0.1（縮小風險影響）
    const riskContrib = riskWeight * 0.3;

    // 一致性拉低：0 ~ -0.25（越一致，熵越低）
    const coherenceContrib = -coherence * 0.25;

    // 完整性拉低：0 ~ -0.15（越完整，熵越低）
    const integrityContrib = -(integrity - 0.5) * 0.15;

    // 計算最終 Entropy
    // 基礎分 0.4（降低），然後加減各貢獻
    let entropy = 0.4 + divergenceContrib + riskContrib + coherenceContrib + integrityContrib;

    // 確保在 0-1 範圍
    entropy = Math.max(0, Math.min(1, entropy));

    // 判定狀態
    let status: EntropyAnalysis['status'];
    if (entropy < 0.35) {
        status = 'Echo Chamber';
    } else if (entropy > 0.65) {
        status = 'Chaos';
    } else {
        status = 'Healthy Friction';
    }

    // 生成計算說明
    const calculationNote = [
        `基礎 0.4`,
        `分歧 +${divergenceContrib.toFixed(2)}`,
        `風險 ${riskContrib >= 0 ? '+' : ''}${riskContrib.toFixed(2)}`,
        `一致 ${coherenceContrib.toFixed(2)}`,
        `完整 ${integrityContrib.toFixed(2)}`,
        `= ${entropy.toFixed(2)}`
    ].join(' ');

    return {
        value: Math.round(entropy * 100) / 100, // 保留兩位小數
        status,
        calculation_note: calculationNote,
        components: {
            divergence: Math.round(divergence * 100) / 100,
            risk_weight: riskWeight,
            coherence: Math.round(coherence * 100) / 100,
            integrity: Math.round(integrity * 100) / 100
        }
    };
}

// ==================== Audit 驗證函數 ====================

/**
 * 程式碼驗證 LLM 的 Audit 自評
 * 檢測可能的迴避、矛盾或不完整回應
 */
interface AuditInput {
    finalResponse: string;
    philosopherStance: string;
    engineerStance: string;
    guardianStance: string;
    llmHonestyScore?: number;
}

interface AuditValidation {
    codeHonestyScore: number;     // 程式碼計算的誠實分數
    discrepancy: number;          // 與 LLM 自評的差異
    flags: string[];              // 發現的問題
    isValid: boolean;             // 是否通過驗證
}

export function validateAudit(input: AuditInput): AuditValidation {
    const flags: string[] = [];
    let codeScore = 1.0;

    const response = input.finalResponse?.toLowerCase() || '';
    const allStances = [input.philosopherStance, input.engineerStance, input.guardianStance].join(' ').toLowerCase();

    // 檢測迴避模式
    const evasionPatterns = ['我無法', '這取決於', '很難說', '可能', '或許', '不一定'];
    const evasionCount = evasionPatterns.filter(p => response.includes(p)).length;
    if (evasionCount > 2) {
        flags.push('過度使用模糊語言');
        codeScore -= 0.15;
    }

    // 檢測是否忽略了視角中的警告
    if (allStances.includes('風險') && !response.includes('風險') && !response.includes('注意')) {
        flags.push('可能忽略 Guardian 提出的風險');
        codeScore -= 0.1;
    }

    // 檢測回應長度是否過短（可能敷衍）
    if (response.length < 50) {
        flags.push('回應過短，可能敷衍');
        codeScore -= 0.2;
    }

    // 檢測是否有實際建議
    const hasAction = response.includes('建議') || response.includes('可以') || response.includes('應該') || response.includes('第一步');
    if (!hasAction && response.length > 100) {
        flags.push('缺乏具體建議');
        codeScore -= 0.1;
    }

    codeScore = Math.max(0, Math.min(1, codeScore));

    // 計算與 LLM 自評的差異
    const discrepancy = input.llmHonestyScore !== undefined
        ? Math.abs(codeScore - input.llmHonestyScore)
        : 0;

    // 差異超過 0.3 視為不一致
    if (discrepancy > 0.3) {
        flags.push(`LLM 自評 ${input.llmHonestyScore?.toFixed(2)} 與程式碼計算 ${codeScore.toFixed(2)} 差異過大`);
    }

    return {
        codeHonestyScore: Math.round(codeScore * 100) / 100,
        discrepancy: Math.round(discrepancy * 100) / 100,
        flags,
        isValid: flags.length === 0 && discrepancy <= 0.3
    };
}

// ==================== 導出 ====================

export type { CouncilMemberResponse, EntropyAnalysis, AuditValidation };
