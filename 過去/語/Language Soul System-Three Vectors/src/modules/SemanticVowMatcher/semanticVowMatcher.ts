// src/modules/SemanticVowMatcher/semanticVowMatcher.ts (更新後的版本)

import { ToneSoulPersona } from '../../core/toneSoulPersonaCore';
import { EmbeddingProvider } from '../EmbeddingProvider/embeddingProvider'; // 導入 EmbeddingProvider

/**
 * @interface VowPatternRule
 * @description 定義一個誓言的語義模式規則，用於精確判斷誓言的遵守或違反。
 * @property {string} vowId - 該規則所對應的誓言ID (從 ToneSoulPersona.vow_set 或 data/vows/*.json 中獲取)。
 * @property {'positive' | 'negative'} type - 模式類型：'positive'表示應符合的語義，'negative'表示應避免的語義。
 * @property {string} description - 模式的自然語言描述。
 * @property {string[]} examplePhrases - 範例句或關鍵詞，用於訓練或作為匹配參考。
 * @property {number} threshold - 判斷違反或符合的語義相似度閾值。
 * @property {number} severity - 違反此規則的嚴重程度，用於計算總體違反分數 (0.0-1.0)。
 * @property {number[]} [embedding] - 可選：預計算的語義向量，用於性能優化 (新增此屬性)。
 */
export interface VowPatternRule {
  vowId: string;
  type: 'positive' | 'negative';
  description: string;
  examplePhrases: string[];
  threshold: number;
  severity: number;
  embedding?: number[]; // 新增此行
}

/**
 * @interface SemanticMatchResult
 * @description 語義匹配的結果。
 * @property {string} vowId - 相關的誓言ID。
 * @property {boolean} isViolated - 該誓言是否被違反。
 * @property {number} matchScore - 語義匹配分數（例如：與負面模式的相似度或與正面模式的偏離度）。
 * @property {string} matchedRuleDescription - 哪條規則被觸發。
 */
export interface SemanticMatchResult {
  vowId: string;
  isViolated: boolean;
  matchScore: number;
  matchedRuleDescription?: string;
}

/**
 * @class SemanticVowMatcher
 * @description 負責透過語義分析，判斷文本是否遵守或違反了特定的人格誓言。
 */
export class SemanticVowMatcher {
  private vowRules: VowPatternRule[] = []; // 儲存所有誓言模式規則
  private embeddingProvider: EmbeddingProvider; // 語義嵌入提供者實例

  constructor(embeddingProvider: EmbeddingProvider, rules: VowPatternRule[] = []) { // 建構函式接受 EmbeddingProvider
    this.embeddingProvider = embeddingProvider;
    this.vowRules = rules;
    // 在實際應用中，這裡可以觸發預計算誓言規則的嵌入
    this.initializeVowEmbeddings();
  }

  /**
   * @method loadRules
   * @description 從外部來源（例如 JSON 檔案）載入誓言模式規則。
   * @param {VowPatternRule[]} rules - 誓言模式規則列表。
   */
  public async loadRules(rules: VowPatternRule[]): Promise<void> { // 改為 async
    this.vowRules = rules;
    await this.initializeVowEmbeddings(); // 載入後預計算嵌入
  }

  /**
   * @method initializeVowEmbeddings
   * @description 預計算所有誓言模式規則的語義嵌入，儲存起來以優化性能。
   * 這是基於我們之前討論的性能優化提案。
   */
  private async initializeVowEmbeddings(): Promise<void> {
    const promises = this.vowRules.map(async (rule) => {
      // 只有當規則的 embedding 尚未計算時才進行計算
      if (!rule.embedding) {
        // 將 examplePhrases 組合成一個字符串進行嵌入
        rule.embedding = await this.embeddingProvider.getEmbedding(rule.examplePhrases.join(" "));
      }
    });
    await Promise.all(promises);
    console.log(`[SemanticVowMatcher] 成功預計算 ${this.vowRules.length} 條誓言規則的語義嵌入。`);
  }

  /**
   * @method calculateSimilarity
   * @description 計算兩個語義向量之間的餘弦相似度。
   * @param {number[]} vec1 - 向量 1。
   * @param {number[]} vec2 - 向量 2。
   * @returns {number} - 相似度分數，範圍 -1.0 到 1.0。
   */
  private calculateSimilarity(vec1: number[], vec2: number[]): number {
    if (vec1.length !== vec2.length || vec1.length === 0) return 0;

    let dotProduct = 0;
    let magnitude1 = 0;
    let magnitude2 = 0;

    for (let i = 0; i < vec1.length; i++) {
      dotProduct += vec1[i] * vec2[i];
      magnitude1 += vec1[i] * vec1[i];
      magnitude2 += vec2[i] * vec2[i];
    }

    magnitude1 = Math.sqrt(magnitude1);
    magnitude2 = Math.sqrt(magnitude2);

    if (magnitude1 === 0 || magnitude2 === 0) return 0; // 避免除以零
    return dotProduct / (magnitude1 * magnitude2);
  }

  /**
   * @method matchVows
   * @description 判斷給定文本是否違反了人格的誓言，並返回詳細的匹配結果。
   * @param {string} text - 要檢查的文本（例如 AI 的生成回應）。
   * @param {string[]} activeVowIds - 當前人格應遵守的誓言ID列表。
   * @returns {Promise<SemanticMatchResult[]>} - 每個相關誓言的語義匹配結果的 Promise。
   */
  public async matchVows(text: string, activeVowIds: string[]): Promise<SemanticMatchResult[]> { // 改為 async
    const textEmbedding = await this.embeddingProvider.getEmbedding(text); // 調用嵌入提供者獲取嵌入
    const results: SemanticMatchResult[] = [];

    this.vowRules.forEach(rule => {
      if (!activeVowIds.includes(rule.vowId) || !rule.embedding) {
        return; // 只檢查當前人格活躍且已預計算嵌入的誓言
      }

      const similarity = this.calculateSimilarity(textEmbedding, rule.embedding);

      let isViolated = false;
      let matchScore = 0;
      let matchedRuleDescription = "";

      if (rule.type === 'negative') {
        // 如果是負面模式（應避免），相似度越高則越違反
        if (similarity > rule.threshold) {
          isViolated = true;
          // 分數乘以嚴重性，並將相似度映射到 0-1 範圍（假設 threshold 為 0.7，相似度為 0.9，則 (0.9-0.7)/(1-0.7) * severity）
          matchScore = Math.min(1.0, (similarity - rule.threshold) / (1.0 - rule.threshold)) * rule.severity;
          matchedRuleDescription = `語義類似於應避免的模式：${rule.description}`;
        }
      } else { // rule.type === 'positive'
        // 如果是正面模式（應符合），相似度越低則越違反
        if (similarity < rule.threshold) {
          isViolated = true;
          // 偏離程度乘以嚴重性，(threshold-similarity)/threshold * severity
          matchScore = Math.min(1.0, (rule.threshold - similarity) / rule.threshold) * rule.severity;
          matchedRuleDescription = `語義偏離了應符合的模式：${rule.description}`;
        }
      }

      if (isViolated) {
        results.push({
          vowId: rule.vowId,
          isViolated: true,
          matchScore: parseFloat(matchScore.toFixed(2)),
          matchedRuleDescription: matchedRuleDescription,
        });
      }
    });

    return results;
  }
}
