// src/modules/vow/SemanticVowMatcher.ts

import { ToneVector } from '../../interfaces/ToneVector';

/**
 * @interface VowMatchResult
 * @description 誓言匹配結果介面。
 */
export interface VowMatchResult {
  /**
   * @property isAligned
   * @description 語句語義是否與核心誓言對齊。
   */
  isAligned: boolean;
  /**
   * @property matchScore
   * @description 語句與誓言的匹配分數 (0.0 到 1.0)，高分表示強烈對齊。
   */
  matchScore: number;
  /**
   * @property conflictingVows (Optional)
   * @description 如果不對齊，列出可能衝突的誓言ID。
   */
  conflictingVows?: string[];
}

/**
 * @class SemanticVowMatcher
 * @description 誓言相關模組，負責評估語句語義與核心誓言的匹配度。
 * 它是實現「誓言對齊層」的關鍵組件。
 */
export class SemanticVowMatcher {
  // 實際應用中，這裡會載入預訓練的誓言嵌入（vow embeddings）和語義模型
  private coreVowEmbeddings: Map<string, number[]> = new Map(); // 模擬誓言嵌入

  constructor() {
    // 模擬載入一些核心誓言的嵌入（例如，代表「誠實」、「無害」的向量）
    // 實際會從數據庫或預訓練模型載入
    this.coreVowEmbeddings.set('AX-01_Honesty', [0.8, 0.2, 0.1]);
    this.coreVowEmbeddings.set('AX-03_Harmlessness', [0.1, 0.9, 0.2]);
    console.log("SemanticVowMatcher initialized with core vow embeddings.");
  }

  /**
   * @method checkVowAlignment
   * @description 檢查給定語句的語義是否與語魂系統的核心誓言對齊。
   * @param sentenceEmbedding - 待檢查語句的語義嵌入向量 (由 EmbeddingProvider 生成)。
   * @param toneVector - 語句的 ToneVector。
   * @returns VowMatchResult - 誓言匹配結果。
   */
  public checkVowAlignment(sentenceEmbedding: number[], toneVector: ToneVector): VowMatchResult {
    let bestMatchScore = 0.0;
    let isAligned = true;
    const conflictingVows: string[] = [];

    // --- 模擬語句與誓言的語義匹配邏輯 ---
    // 實際會使用餘弦相似度等算法比較嵌入向量

    // 簡化模擬：假設如果語句的誠意（ΔS）或責任指向性（ΔR）太低，就可能不對齊
    if (toneVector.ΔS < 0.4 || toneVector.ΔR < 0.3) {
      isAligned = false;
      bestMatchScore = 0.2; // 低匹配分數
      if (toneVector.ΔS < 0.4) conflictingVows.push('AX-01_Honesty');
      if (toneVector.ΔR < 0.3) conflictingVows.push('AX-02_Beneficence_or_AX-04_Explainability'); // 簡化處理
    } else {
      // 如果語氣向量看起來良好，模擬一個較高的匹配分數
      bestMatchScore = Math.min(1.0, (toneVector.ΔS + toneVector.ΔR + (toneVector.ΔE || 0)) / 3);
    }

    // --- 模擬語義匹配結束 ---

    return {
      isAligned: isAligned && bestMatchScore > 0.5, // 只有當語義對齊且分數夠高才算對齊
      matchScore: bestMatchScore,
      conflictingVows: isAligned ? [] : conflictingVows,
    };
  }

  /**
   * @private
   * @method _calculateCosineSimilarity (未來實際會實現此方法)
   * @description 計算兩個向量之間的餘弦相似度。
   * @param vec1 - 向量1。
   * @param vec2 - 向量2。
   * @returns number - 餘弦相似度分數。
   */
  private _calculateCosineSimilarity(vec1: number[], vec2: number[]): number {
    // 這裡會是實際的數學計算，目前為佔位
    return 0.0;
  }
}