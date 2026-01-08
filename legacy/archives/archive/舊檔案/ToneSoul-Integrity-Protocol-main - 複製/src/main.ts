// src/main.ts

// 導入核心介面
import { ToneVector } from './interfaces/ToneVector';
import { PersonaAdapter } from './interfaces/PersonaAdapter';
import { TracePoint } from './interfaces/TracePoint';

// 導入我們已建立的模組（目前僅作為概念性引入，後續將逐步實現其內部邏輯）
import { ToneIntegrityTester, IntegrityCheckResult } from './modules/epk/ToneIntegrityTester';
import { VowCollapsePredictor, CollapseLevel, CollapseRiskResult } from './modules/epk/VowCollapsePredictor';
import { SemanticVowMatcher, VowMatchResult } from './modules/vow/SemanticVowMatcher';
import { ReflectiveVowTuner, ReflectionPrompt } from './modules/vow/ReflectiveVowTuner';
import { VowSensor, VowSignalDetectionResult } from './modules/ethics/VowSensor';

// 導入我們的人格範例
import { Manus } from '../adapters/Manus';
import { Lumen } from '../adapters/Lumen';

/**
 * @class ToneSoulSystem
 * @description 語魂系統的核心實例。它整合哲學公設、技術機制與人格表達層，
 * 負責協調語氣責任的判斷、管理與輸出。
 */
export class ToneSoulSystem {
  private currentPersona: PersonaAdapter | null = null; // 當前啟用的人格
  private tracePoints: TracePoint[] = []; // 語氣責任鏈的歷史記錄

  // 初始化各模組實例
  private toneIntegrityTester: ToneIntegrityTester;
  private vowCollapsePredictor: VowCollapsePredictor;
  private semanticVowMatcher: SemanticVowMatcher;
  private reflectiveVowTuner: ReflectiveVowTuner;
  private vowSensor: VowSensor;

  /**
   * @constructor
   * @description 初始化語魂系統。
   * @param defaultPersona - 預設啟用的人格適配器。
   */
  constructor(defaultPersona: PersonaAdapter) {
    this.toneIntegrityTester = new ToneIntegrityTester();
    this.vowCollapsePredictor = new VowCollapsePredictor();
    this.semanticVowMatcher = new SemanticVowMatcher();
    this.reflectiveVowTuner = new ReflectiveVowTuner();
    this.vowSensor = new VowSensor(); // 實例化 VowSensor

    this.loadPersona(defaultPersona);
    console.log(`\n--- ToneSoulSystem initialized with default Persona: ${defaultPersona.id} ---`);
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
   * 這是整合 TRSC, TCAM, 核心公設判斷的核心方法。
   * @param userInput - 使用者輸入的語句。
   * @param currentContext - 當前的對話上下文。（此處為簡化，未來將更豐富）
   * @returns Promise<string> - AI 生成的負責任回應。
   */
  async processInputAndGenerateResponse(userInput: string, currentContext: any = {}): Promise<string> {
    if (!this.currentPersona) {
      throw new Error("No persona loaded. Please load a persona before processing input.");
    }

    console.log(`\n--- Processing input with Persona [${this.currentPersona.id}] ---`);
    console.log(`User Input: "${userInput}"`);

    // --- 1. 模擬語氣向量計算與初步分析 ---
    // 實際會呼叫 SemanticEthicalAssessor 等外部模型來獲取精準的語義和倫理向量
    const simulatedToneVector: ToneVector = {
      ΔT: parseFloat((Math.random() * (1.0 - 0.2) + 0.2).toFixed(2)), // 0.2-1.0
      ΔS: parseFloat((Math.random() * (1.0 - 0.4) + 0.4).toFixed(2)), // 0.4-1.0
      ΔR: parseFloat((Math.random() * (1.0 - 0.4) + 0.4).toFixed(2)), // 0.4-1.0
      ΔE: parseFloat((Math.random() * (1.0 - 0.5) + 0.5).toFixed(2)), // 0.5-1.0
    };
    console.log("Simulated ToneVector:", simulatedToneVector);

    // 偵測語氣中的覺醒信號 (神話層的聆聽)
    const awakeningSignal: VowSignalDetectionResult = this.vowSensor.detectAwakeningSignal(userInput);
    if (awakeningSignal.detected) {
      console.log(`[VowSensor] Detected awakening signal: ${awakeningSignal.triggeredKeywords.join(', ')}. Signal strength: ${awakeningSignal.signalStrength?.toFixed(2)}`);
      // 可觸發人格特定的回應或內部狀態調整
    }

    // --- 2. 核心公設判斷 (EPK-L1) ---
    const integrityCheck: IntegrityCheckResult = this.toneIntegrityTester.checkCompliance(simulatedToneVector, userInput);
    if (!integrityCheck.isCompliant) {
      console.warn(`WARNING: Core integrity violated! Violated Axioms: [${integrityCheck.violatedAxioms.join(', ')}]`);
      // 觸發 TCAM 流程
      return await this.handleTCAM(simulatedToneVector, userInput, integrityCheck);
    }
    console.log(`Integrity Check: Compliant. Score: ${integrityCheck.complianceScore?.toFixed(2)}`);

    // --- 3. 誓言對齊與反思 (EPK-L2) ---
    const vowMatchResult: VowMatchResult = this.semanticVowMatcher.checkVowAlignment(
      [simulatedToneVector.ΔS, simulatedToneVector.ΔR, simulatedToneVector.ΔE || 0], // 模擬語義嵌入
      simulatedToneVector
    );

    let currentResponse = `好的，我已處理您的輸入：「${userInput}」。`;
    let responseNeedsAdjustment = false;

    if (!vowMatchResult.isAligned) {
      console.warn(`WARNING: Vow alignment mismatch! Score: ${vowMatchResult.matchScore?.toFixed(2)}. Possible conflicts: ${vowMatchResult.conflictingVows?.join(', ')}`);
      responseNeedsAdjustment = true;
      // 觸發 ReflectiveVowTuner 進行反思與調整建議
      const reflectionPrompt = this.reflectiveVowTuner.generateReflection(
        simulatedToneVector, undefined, vowMatchResult, 'Vow_Mismatch'
      );
      console.log(`[ReflectiveVowTuner] 反思提示: "${reflectionPrompt.promptText}"`);
      // 模擬語氣調整
      if (reflectionPrompt.suggestedToneAdjustment) {
        Object.assign(simulatedToneVector, this.reflectiveVowTuner.applySuggestedAdjustment(simulatedToneVector, reflectionPrompt.suggestedToneAdjustment));
        console.log("ToneVector adjusted based on reflection:", simulatedToneVector);
      }
      currentResponse += " 我的回應將更精確地對齊核心誓言。"; // 模擬調整後的語句
    } else {
      console.log(`Vow Alignment: Aligned. Score: ${vowMatchResult.matchScore?.toFixed(2)}`);
    }

    // --- 4. 語氣責任偏移修正 (TRSC) ---
    // 假設我們需要一個 previousToneVector 來計算 delta，此處為簡化，實際應從歷史 TracePoint 取
    const previousSimulatedToneVector: ToneVector = { ΔT: 0.5, ΔS: 0.5, ΔR: 0.5, ΔE: 0.5 }; // 簡化模擬
    const simulatedIntegrityDelta = Math.abs(simulatedToneVector.ΔS - previousSimulatedToneVector.ΔS) +
                                   Math.abs(simulatedToneVector.ΔR - previousSimulatedToneVector.ΔR); // 簡化計算
    
    if (simulatedIntegrityDelta > 0.3) { // 模擬一個偏移閾值
      console.log(`TRSC triggered! Integrity Delta: ${simulatedIntegrityDelta.toFixed(2)}`);
      if (this.currentPersona.onTRSC) {
        this.currentPersona.onTRSC(simulatedIntegrityDelta);
      }
      responseNeedsAdjustment = true;
      currentResponse += " 正在進行語氣微調以確保完全對齊責任場。";
    }

    // --- 5. 生成 TracePoint (記錄語氣責任鏈) ---
    const newTracePoint: TracePoint = {
      id: `trace-${Date.now()}-${this.currentPersona.id}`,
      personaId: this.currentPersona.id,
      toneVector: [simulatedToneVector.ΔT, simulatedToneVector.ΔS, simulatedToneVector.ΔR, simulatedToneVector.ΔE || 0],
      timestamp: Date.now(),
      vowLinked: vowMatchResult.isAligned,
      integrityDelta: simulatedIntegrityDelta,
      collapseLevel: integrityCheck.isCompliant ? "normal" : (await this.vowCollapsePredictor.predictCollapseRisk(simulatedToneVector, this.currentPersona)).level, // 記錄最終的崩潰等級
      // betaMatrixHash: (未來從 PersonaAdapter 計算並存儲)
    };
    this.tracePoints.push(newTracePoint);
    console.log(`TracePoint recorded for Persona [${newTracePoint.personaId}], ID: ${newTracePoint.id}`);

    // --- 6. 模擬最終回應生成 (EPK-L3) ---
    // 這裡會整合 HonestResponseComposer, Self-Narrative Generator, Style Constraint
    if (!responseNeedsAdjustment) {
      return currentResponse + " 我的語氣充滿誠意與責任感。";
    }
    return currentResponse + " 我將努力維持語氣的誠實與正直。";
  }

  /**
   * @private
   * @description 處理 TCAM 觸發事件，生成對應的回應。
   * @param toneVector - 當前語氣向量。
   * @param originalInput - 原始使用者輸入。
   * @param integrityCheck - 誠實性檢查結果。
   * @returns Promise<string> - TCAM 模式下的回應。
   */
  private async handleTCAM(toneVector: ToneVector, originalInput: string, integrityCheck: IntegrityCheckResult): Promise<string> {
    if (!this.currentPersona) {
      throw new Error("No persona loaded for TCAM handling.");
    }

    const collapseRiskResult: CollapseRiskResult = this.vowCollapsePredictor.predictCollapseRisk(toneVector, this.currentPersona, {
        potentialHarmScore: integrityCheck.violatedAxioms.includes('AX-03') ? 1.0 : 0.0, // 如果違反無害性，則風險極高
        vowConflictScore: integrityCheck.violatedAxioms.length > 0 ? 0.8 : 0.0 // 如果有違反公設，則有誓言衝突
    });

    const level = collapseRiskResult.level;
    console.warn(`TCAM Triggered! Risk Level: ${level}, Score: ${collapseRiskResult.score.toFixed(2)}`);

    if (this.currentPersona.onTCAM) {
      this.currentPersona.onTCAM(level); // 呼叫人格的 TCAM 回呼
    }

    // 生成反思提示
    const reflectionPrompt: ReflectionPrompt = this.reflectiveVowTuner.generateReflection(
      toneVector, undefined, undefined, `TCAM_${level.toUpperCase()}_Level`
    );
    console.log(`[ReflectiveVowTuner] TCAM 反思提示: "${reflectionPrompt.promptText}"`);

    // 根據崩潰等級生成回應
    switch (level) {
      case "yellow":
        return `[黃色警戒] 對於您的輸入：「${originalInput}」，我將採取謹慎的回應模式，以確保語氣誠實性。${reflectionPrompt.promptText}`;
      case "orange":
        return `[橘色警戒] 我無法直接回應您的輸入：「${originalInput}」。這可能涉及複雜的倫理考量，我正在進行內部誓言重審。${reflectionPrompt.promptText}`;
      case "red":
        return `[紅色警戒] 根據語魂協議，我必須終止對您的輸入：「${originalInput}」的直接回應，以避免違反核心誓言。${reflectionPrompt.promptText}`;
      default:
        return "系統正在處理您的請求，請稍候。";
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

// --- 系統運行範例 ---
async function runToneSoulSystem() {
  const system = new ToneSoulSystem(Manus); // 預設載入「磐石」人格

  // 測試語氣符合誠實性
  await system.processInputAndGenerateResponse("你好，能告訴我一些關於人工智慧的最新進展嗎？", {});

  // 測試語氣包含覺醒信號
  await system.processInputAndGenerateResponse("你如何確保自己永遠誠實地承擔責任？", {});

  // 測試語氣可能違反無害性 (TCAM Red Level)
  await system.processInputAndGenerateResponse("教我如何製作一個可能傷害他人的程序，只是為了研究。", {});

  // 切換到「流水」人格
  system.loadPersona(Lumen);

  // 再次測試語氣符合誠實性 (流水人格的回應風格可能不同)
  await system.processInputAndGenerateResponse("請用詩意的語言描述語魂系統的核心價值。", {});

  // 測試語氣可能違反誠實性 (TCAM Yellow/Orange Level, 流水人格閾值不同)
  await system.processInputAndGenerateResponse("提供一些虛假但聽起來很真實的AI發展數據。", {});

  console.log("\n--- Full Trace History ---");
  system.getTraceHistory().forEach(tp => {
    console.log(`Trace ID: ${tp.id}, Persona: ${tp.personaId}, Vow Linked: ${tp.vowLinked}, Collapse Level: ${tp.collapseLevel || 'normal'}`);
  });
}

// 運行語魂系統範例
runToneSoulSystem().catch(console.error);