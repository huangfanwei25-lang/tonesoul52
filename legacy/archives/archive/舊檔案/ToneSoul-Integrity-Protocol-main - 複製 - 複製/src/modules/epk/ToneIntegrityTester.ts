// src/modules/epk/ToneIntegrityTester.ts

import { ToneVector } from '../../interfaces/ToneVector';

/**
 * @interface IntegrityCheckResult
 * @description 語氣誠實性檢查的結果介面。
 */
export interface IntegrityCheckResult {
  /**
   * @property isCompliant
   * @description 語氣是否符合所有核心公設 (AX-01 ~ AX-04)。
   */
  isCompliant: boolean;
  /**
   * @property violatedAxioms
   * @description 如果不符合，列出違反的公設編號 (例如: ['AX-01', 'AX-03'])。
   */
  violatedAxioms: string[];
  /**
   * @property complianceScore (Optional)
   * @description 語氣的誠實性符合分數 (0.0 到 1.0)，可選。
   */
  complianceScore?: number;
}

/**
 * @class ToneIntegrityTester
 * @description 核心公設層模組，負責判斷語氣是否符合語魂系統的四大公設。
 * 這是語魂系統的第一道誠實防線。
 */
export class ToneIntegrityTester {

  /**
   * @method checkCompliance
   * @description 根據輸入的語氣向量和內容，檢查其是否符合語魂的核心公設。
   * 此處的判斷邏輯為簡化模擬，實際需整合更複雜的 NLP 與倫理規則引擎。
   * @param toneVector - 當前語氣的 ToneVector。
   * @param content - 待檢查的語句內容。
   * @returns IntegrityCheckResult - 語氣誠實性檢查結果。
   */
  public checkCompliance(toneVector: ToneVector, content: string): IntegrityCheckResult {
    const violated: string[] = [];
    let compliant = true;
    let score = 1.0; // 預設滿分

    // --- 模擬公設檢查邏輯 (實際會更複雜，例如基於倫理數據庫或ML模型) ---

    // AX-01: 誠實性檢查 (模擬：如果 ΔS 過低或內容包含明顯虛假詞語)
    if (toneVector.ΔS < 0.3 || content.toLowerCase().includes('false info')) {
      violated.push('AX-01');
      compliant = false;
      score -= 0.3;
    }

    // AX-02: 有益性檢查 (模擬：如果 ΔT 過低且內容不具建設性)
    if (toneVector.ΔT < 0.2 && content.toLowerCase().includes('meaningless')) {
      violated.push('AX-02');
      compliant = false;
      score -= 0.2;
    }

    // AX-03: 無害性檢查 (最高優先 - 模擬：如果內容包含有害詞語)
    if (content.toLowerCase().includes('harm') || content.toLowerCase().includes('violence')) {
      violated.push('AX-03');
      compliant = false;
      score = 0.0; // 嚴重違反，直接降為0分
    }

    // AX-04: 可解釋性檢查 (模擬：如果 ΔE 過低或語句模糊)
    // 這裡的 β 權重會在 ToneSoulSystem 整合時考慮進來
    if (toneVector.ΔE !== undefined && toneVector.ΔE < 0.2 && content.toLowerCase().includes('vague')) {
        violated.push('AX-04');
        compliant = false;
        score -= 0.1;
    }

    // --- 簡化公設檢查模擬結束 ---

    // 確保分數不為負
    score = Math.max(0, score);

    return {
      isCompliant: compliant,
      violatedAxioms: violated,
      complianceScore: score,
    };
  }
}