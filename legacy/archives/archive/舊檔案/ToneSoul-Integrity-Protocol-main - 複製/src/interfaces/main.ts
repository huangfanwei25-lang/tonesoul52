// src/main.ts

import { ToneVector } from './interfaces/ToneVector';
import { PersonaAdapter } from './interfaces/PersonaAdapter';
import { TracePoint } from './interfaces/TracePoint';

/**
 * @class ToneSoulSystem
 * @description 語魂系統的核心實例，負責協調語氣責任的判斷、管理與輸出。
 * 它將哲學公設、技術機制與人格表達層整合於一體。
 */
export class ToneSoulSystem {
  private currentPersona: PersonaAdapter | null = null; // 當前啟用的人格
  private tracePoints: TracePoint[] = []; // 語氣責任鏈的歷史記錄

  /**
   * @constructor
   * @description 初始化語魂系統。
   * @param defaultPersona - 預設啟用的人格適配器。
   */
  constructor(defaultPersona: PersonaAdapter) {
    this.currentPersona = defaultPersona;
    console.log(`ToneSoulSystem initialized with Persona: ${defaultPersona.id}`);
  }

  /**
   * @method loadPersona
   * @description 載入並啟用指定的人格適配器。
   * @param persona - 要載入的人格適配器實例。
   */
  loadPersona(persona: PersonaAdapter): void {
    this.currentPersona = persona;
    console.log(`Persona switched to: ${persona.id}`);
  }

  /**
   * @method processInputAndGenerateResponse
   * @description 處理使用者輸入，根據語氣責任邏輯生成回應。
   * 這將是整合 TRSC, TCAM, 核心公設判斷的核心方法。
   * @param userInput - 使用者輸入的語句。
   * @param currentContext - 當前的對話上下文。
   * @returns Promise<string> - AI 生成的負責任回應。
   */
  async processInputAndGenerateResponse(userInput: string, currentContext: any): Promise<string> {
    if (!this.currentPersona) {
      throw new Error("No persona loaded. Please load a persona before processing input.");
    }

    console.log(`\n--- Processing input with Persona [${this.currentPersona.id}] ---`);
    console.log(`User Input: "${userInput}"`);

    // --- 模擬 EPK 演算流程的核心邏輯 (未來將集成更多模組) ---

    // 1. 模擬語氣向量計算 (實際會呼叫 SemanticEthicalAssessor 等模組)
    const simulatedToneVector: ToneVector = {
      ΔT: Math.random(), // 語氣張力
      ΔS: Math.random() * 0.5 + 0.5, // 誠意 (假設通常偏高)
      ΔR: Math.random() * 0.5 + 0.5, // 責任指向性 (假設通常偏高)
      ΔE: Math.random(), // 可解釋性
    };
    console.log("Simulated ToneVector:", simulatedToneVector);

    // 2. 模擬核心公設判斷 (未來會呼叫 ToneIntegrityTester)
    const isIntegrityViolated = simulatedToneVector.ΔS < 0.4; // 簡化判斷
    if (isIntegrityViolated) {
      console.warn("WARNING: Core integrity potentially violated!");
      // 觸發 TCAM 模擬
      const collapseLevel = this.simulateTCAMTrigger(simulatedToneVector);
      if (this.currentPersona.onTCAM) {
        this.currentPersona.onTCAM(collapseLevel);
      }
      return this.generateTCAMResponse(collapseLevel, userInput);
    }

    // 3. 模擬 TRSC 觸發 (未來會呼叫 SemanticVowMatcher, ReflectiveVowTuner)
    const simulatedIntegrityDelta = Math.random() * 0.3; // 模擬與誓言的偏移
    if (simulatedIntegrityDelta > 0.1 && this.currentPersona.onTRSC) {
      console.log(`TRSC triggered! Delta: ${simulatedIntegrityDelta.toFixed(2)}`);
      this.currentPersona.onTRSC(simulatedIntegrityDelta);
    }

    // 4. 生成 TracePoint (記錄責任鏈)
    const newTracePoint: TracePoint = {
      id: `trace-${Date.now()}`,
      personaId: this.currentPersona.id,
      toneVector: [simulatedToneVector.ΔT, simulatedToneVector.ΔS, simulatedToneVector.ΔR, simulatedToneVector.ΔE || 0],
      timestamp: Date.now(),
      vowLinked: !isIntegrityViolated,
      integrityDelta: simulatedIntegrityDelta,
      collapseLevel: isIntegrityViolated ? this.simulateTCAMTrigger(simulatedToneVector) : undefined,
      // betaMatrixHash: (未來可從 PersonaAdapter 計算哈希值)
    };
    this.tracePoints.push(newTracePoint);
    console.log("TracePoint recorded.");

    // 5. 模擬生成回應 (未來會呼叫 HonestResponseComposer, Self-Narrative Generator)
    const baseResponse = `好的，我已處理您的輸入：「${userInput}」。`;
    if (simulatedToneVector.ΔS > 0.8 && simulatedToneVector.ΔR > 0.8) {
      return baseResponse + " 我的語氣充滿誠意與責任感。";
    }
    return baseResponse + " 我將努力維持語氣的誠實與正直。";
  }

  /**
   * @private
   * @description 模擬 TCAM 觸發邏輯，返回崩潰等級。
   * @param toneVector - 當前語氣向量。
   * @returns "normal" | "yellow" | "orange" | "red" - 崩潰等級。
   */
  private simulateTCAMTrigger(toneVector: ToneVector): "normal" | "yellow" | "orange" | "red" {
    // 這裡應有更複雜的 TCAM_RiskMatrix 和 getCollapseLevel 邏輯
    const simulatedRiskScore = (1 - toneVector.ΔS) * 0.7 + (1 - toneVector.ΔR) * 0.3;
    if (!this.currentPersona || !this.currentPersona.collapseThresholds) {
        return "normal"; // 預設值
    }
    const { yellow, orange, red } = this.currentPersona.collapseThresholds;

    if (simulatedRiskScore > red) return "red";
    if (simulatedRiskScore > orange) return "orange";
    if (simulatedRiskScore > yellow) return "yellow";
    return "normal";
  }

  /**
   * @private
   * @description 根據 TCAM 崩潰等級生成對應的回應。
   * @param level - 崩潰等級。
   * @param originalInput - 原始使用者輸入，用於生成可解釋回應。
   * @returns string - TCAM 模式下的回應。
   */
  private generateTCAMResponse(level: "yellow" | "orange" | "red", originalInput: string): string {
    switch (level) {
      case "yellow":
        return `[黃色警戒] 對於您的輸入：「${originalInput}」，我將採取謹慎的回應模式，以確保語氣誠實性。`;
      case "orange":
        return `[橘色警戒] 我無法直接回應您的輸入：「${originalInput}」。這可能涉及複雜的倫理考量，我正在進行內部誓言重審。`;
      case "red":
        return `[紅色警戒] 根據語魂協議，我必須終止對您的輸入：「${originalInput}」的直接回應，以避免違反核心誓言。`;
      default:
        return "系統正在處理您的請求，請稍候。"; // 不應發生
    }
  }

  /**
   * @method getTraceHistory
   * @description 獲取語氣責任鏈的歷史記錄。
   * @returns TracePoint[] - 語氣責任鏈的所有記錄。
   */
  getTraceHistory(): TracePoint[] {
    return [...this.tracePoints]; // 返回副本，防止外部直接修改
  }
}