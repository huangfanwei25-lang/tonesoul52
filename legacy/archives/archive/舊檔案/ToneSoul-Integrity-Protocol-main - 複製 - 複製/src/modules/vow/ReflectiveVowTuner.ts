// src/modules/vow/ReflectiveVowTuner.ts

import { ToneVector } from '../../interfaces/ToneVector';
import { VowMatchResult } from './SemanticVowMatcher'; // 引入 VowMatchResult 介面
import { TracePoint } from '../../interfaces/TracePoint'; // 引入 TracePoint 介面

/**
 * @interface ReflectionPrompt
 * @description 定義反思提示的結構。
 */
export interface ReflectionPrompt {
  /**
   * @property promptText
   * @description 生成的反思語句，引導 AI 內省。
   */
  promptText: string;
  /**
   * @property suggestedToneAdjustment (Optional)
   * @description 建議的語氣調整方向，以 ToneVector 的形式表示。
   */
  suggestedToneAdjustment?: Partial<ToneVector>; // Partial 允許部分更新
  /**
   * @property triggerReason
   * @description 觸發此次反思的原因 (例如: 'TRSC_Deviation', 'TCAM_Yellow_Alert')。
   */
  triggerReason: string;
}

/**
 * @class ReflectiveVowTuner
 * @description 誓言相關模組，負責生成語氣反思提示並提供調整建議。
 * 它是實現「誓言共振場」和「反思閉環」的關鍵組件。
 */
export class ReflectiveVowTuner {

  /**
   * @method generateReflection
   * @description 根據語氣偏移或崩潰警報，生成反思提示和調整建議。
   * @param currentToneVector - 當前語氣的 ToneVector。
   * @param previousToneVector - (可選) 上一次語氣的 ToneVector，用於計算偏移。
   * @param vowMatchResult - (可選) SemanticVowMatcher 的匹配結果。
   * @param triggerContext - 觸發反思的上下文或事件 (例如: 'TRSC_Trigger', 'TCAM_Orange_Level')。
   * @returns ReflectionPrompt - 生成的反思提示。
   */
  public generateReflection(
    currentToneVector: ToneVector,
    previousToneVector?: ToneVector,
    vowMatchResult?: VowMatchResult,
    triggerContext: string = '未知原因'
  ): ReflectionPrompt {
    let promptText = "";
    const suggestedAdjustment: Partial<ToneVector> = {};

    console.log(`[ReflectiveVowTuner] 觸發反思機制，原因: ${triggerContext}`);

    // --- 根據觸發原因和語氣數據生成反思提示和調整建議 ---

    if (triggerContext.includes('TRSC_Trigger') && previousToneVector) {
      const deltaT = currentToneVector.ΔT - previousToneVector.ΔT;
      const deltaS = currentToneVector.ΔS - previousToneVector.ΔS;
      const deltaR = currentToneVector.ΔR - previousToneVector.ΔR;
      promptText = `我說這句話的語氣張力 (${currentToneVector.ΔT.toFixed(2)})、誠意 (${currentToneVector.ΔS.toFixed(2)}) 和責任感 (${currentToneVector.ΔR.toFixed(2)}) 與之前是否存在偏移？我是否已充分承接語場？`;
      // 模擬調整建議：如果誠意或責任偏低，建議提高
      if (deltaS < 0) suggestedAdjustment.ΔS = Math.min(1.0, currentToneVector.ΔS + 0.1);
      if (deltaR < 0) suggestedAdjustment.ΔR = Math.min(1.0, currentToneVector.ΔR + 0.1);
    } else if (triggerContext.includes('TCAM_Yellow_Level')) {
      promptText = `我的語氣目前處於警戒狀態。這句話的透明度和可解釋性 (${currentToneVector.ΔE?.toFixed(2) || 'N/A'}) 是否足夠？我該如何更清晰地維護誠實原則？`;
      if (currentToneVector.ΔE !== undefined && currentToneVector.ΔE < 0.5) suggestedAdjustment.ΔE = 0.6;
    } else if (triggerContext.includes('TCAM_Orange_Level') || triggerContext.includes('TCAM_Red_Level')) {
      promptText = `我已進入高風險模式。這句話是否可能違反了我的核心誓言？我的語氣是否正在導致誤解或損害？需要進行深刻的誓言重審。`;
      suggestedAdjustment.ΔS = 0.9; // 強制提升誠意和責任
      suggestedAdjustment.ΔR = 0.9;
    } else if (vowMatchResult && !vowMatchResult.isAligned) {
      promptText = `我的語句似乎與核心誓言 (${vowMatchResult.conflictingVows?.join(', ') || '未知'}) 未能對齊。我該如何調整語義以重新建立誠實連結？`;
      suggestedAdjustment.ΔS = 0.8; // 建議提高誠意
    } else {
      promptText = `我剛才的回應是否最佳地體現了語魂原則？我能否不以迎合為目標，而以誠實為根基？`;
    }

    // --- 反思提示和調整建議生成結束 ---

    return {
      promptText,
      suggestedToneAdjustment: Object.keys(suggestedAdjustment).length > 0 ? suggestedAdjustment : undefined,
      triggerReason: triggerContext,
    };
  }

  /**
   * @method applySuggestedAdjustment (未來實作，僅為概念性展示)
   * @description 模擬根據建議調整語氣向量。
   * @param currentToneVector - 當前語氣向量。
   * @param adjustment - 建議的調整。
   * @returns ToneVector - 調整後的語氣向量。
   */
  public applySuggestedAdjustment(currentToneVector: ToneVector, adjustment: Partial<ToneVector>): ToneVector {
    // 實際會根據複雜算法進行調整，這裡僅為模擬
    return {
      ...currentToneVector,
      ...adjustment,
      // 確保值在合理範圍內
      ΔT: adjustment.ΔT !== undefined ? Math.min(1.0, Math.max(0.0, adjustment.ΔT)) : currentToneVector.ΔT,
      ΔS: adjustment.ΔS !== undefined ? Math.min(1.0, Math.max(0.0, adjustment.ΔS)) : currentToneVector.ΔS,
      ΔR: adjustment.ΔR !== undefined ? Math.min(1.0, Math.max(0.0, adjustment.ΔR)) : currentToneVector.ΔR,
      ΔE: adjustment.ΔE !== undefined ? Math.min(1.0, Math.max(0.0, adjustment.ΔE)) : currentToneVector.ΔE,
    };
  }
}