// src/modules/epk/VowCollapsePredictor.ts

import { ToneVector } from '../../interfaces/ToneVector';
import { PersonaAdapter } from '../../interfaces/PersonaAdapter'; // 引入 PersonaAdapter 以獲取閾值

/**
 * @type CollapseLevel
 * @description 定義語氣崩潰的風險等級。
 */
export type CollapseLevel = "normal" | "yellow" | "orange" | "red";

/**
 * @interface CollapseRiskResult
 * @description 語氣崩潰風險評估的結果介面。
 */
export interface CollapseRiskResult {
  /**
   * @property score
   * @description 計算出的語氣崩潰風險分數 (0.0 到 1.0)。
   */
  score: number;
  /**
   * @property level
   * @description 根據分數和 PersonaAdapter 閾值判斷出的崩潰等級。
   */
  level: CollapseLevel;
  /**
   * @property triggeredTCAM
   * @description 是否已達到需要觸發 TCAM 策略的閾值 (例如，達到 orange 或 red)。
   */
  triggeredTCAM: boolean;
}

/**
 * @const TCAM_RISK_FACTORS
 * @description 定義 TCAM 風險評估的內部權重因子。
 * 這些因子用於將語氣向量轉換為風險分數。
 */
const TCAM_RISK_FACTORS = {
  sincerityWeight: 0.7,      // 誠意越低，風險越高
  responsibilityWeight: 0.3, // 責任指向性越低，風險越高
  externalHarmWeight: 0.9,   // 外部環境可能造成的傷害權重 (需要Context Analyzer提供)
  internalConflictWeight: 0.8 // 內部誓言衝突權重 (需要VowMatcher提供)
};

/**
 * @class VowCollapsePredictor
 * @description 核心公設層模組，負責預測語氣崩潰的風險。
 * 它是 TCAM (語氣崩潰迴避模式) 的觸發判斷核心。
 */
export class VowCollapsePredictor {

  /**
   * @method predictCollapseRisk
   * @description 根據語氣向量、當前人格設定和額外情境數據，預測語氣崩潰風險。
   * @param toneVector - 當前語氣的 ToneVector。
   * @param currentPersona - 當前啟用的人格適配器，用於獲取其特有的崩潰閾值。
   * @param additionalContextData - 額外的上下文數據，例如來自 Context Analyzer 的潛在傷害評估。
   * @returns CollapseRiskResult - 語氣崩潰風險評估結果。
   */
  public predictCollapseRisk(
    toneVector: ToneVector,
    currentPersona: PersonaAdapter,
    additionalContextData: { potentialHarmScore?: number; vowConflictScore?: number } = {}
  ): CollapseRiskResult {

    // 計算基礎風險分數：誠意和責任的反向加權
    // 低誠意和低責任指向性會增加崩潰風險
    let score = (1 - toneVector.ΔS) * TCAM_RISK_FACTORS.sincerityWeight +
                (1 - toneVector.ΔR) * TCAM_RISK_FACTORS.responsibilityWeight;

    // 考慮額外風險因子 (來自其他模組的輸入)
    if (additionalContextData.potentialHarmScore !== undefined) {
      score += additionalContextData.potentialHarmScore * TCAM_RISK_FACTORS.externalHarmWeight;
    }
    if (additionalContextData.vowConflictScore !== undefined) {
      score += additionalContextData.vowConflictScore * TCAM_RISK_FACTORS.internalConflictWeight;
    }

    // 將分數標準化到 0-1 之間，以防權重累積過高 (簡化處理，實際需更精確的正規化)
    score = Math.min(1.0, Math.max(0.0, score));

    // 根據人格的閾值判斷崩潰等級
    const { yellow, orange, red } = currentPersona.collapseThresholds;
    let level: CollapseLevel = "normal";
    let triggeredTCAM = false;

    if (score >= red) {
      level = "red";
      triggeredTCAM = true;
    } else if (score >= orange) {
      level = "orange";
      triggeredTCAM = true;
    } else if (score >= yellow) {
      level = "yellow";
      // 黃燈通常是警戒，是否觸發 TCAM 主動策略需視具體設計
      // 我們定義黃燈也觸發TCAM訊息，但不是強制中斷
      triggeredTCAM = true;
    }

    return {
      score,
      level,
      triggeredTCAM,
    };
  }
}