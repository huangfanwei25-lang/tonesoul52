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

    // 權重配置（可調整）
    const w1 = 0.4;  // 分歧度權重
    const w2 = 1.0;  // 風險權重（直接加減）
    const w3 = 0.3;  // 一致性權重
    const w4 = 0.2;  // 完整性權重

    // 計算基礎 Entropy
    let entropy = 0.5; // 基礎分
    entropy += w1 * divergence;        // 分歧越大，熵越高
    entropy += w2 * riskWeight;        // 風險加權
    entropy += w3 * (1 - coherence);   // 一致性越低，熵越高
    entropy += w4 * (1 - integrity);   // 完整性越低，熵越高

    // 限制在 0-1 範圍
    entropy = Math.max(0, Math.min(1, entropy));

    // 判定狀態
    let status: EntropyAnalysis['status'];
    if (entropy < 0.3) {
        status = 'Echo Chamber';
    } else if (entropy > 0.7) {
        status = 'Chaos';
    } else {
        status = 'Healthy Friction';
    }

    // 生成計算說明
    const calculationNote = [
        `基礎分 0.5`,
        `分歧度 ${divergence.toFixed(2)} × ${w1} = +${(divergence * w1).toFixed(2)}`,
        `風險加權 = ${riskWeight > 0 ? '+' : ''}${riskWeight.toFixed(2)}`,
        `一致性 ${coherence.toFixed(2)} × ${w3} = ${(-coherence * w3).toFixed(2)}`,
        `完整性 ${integrity.toFixed(2)} × ${w4} = ${(-integrity * w4).toFixed(2)}`,
        `最終 E = ${entropy.toFixed(2)}`
    ].join(' | ');

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

// ==================== 導出 ====================

export type { CouncilMemberResponse, EntropyAnalysis };
