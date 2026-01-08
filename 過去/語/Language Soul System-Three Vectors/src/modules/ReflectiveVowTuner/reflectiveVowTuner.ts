// src/modules/ReflectiveVowTuner/reflectiveVowTuner.ts (更新後的版本)

import { ToneSoulPersona } from '../../core/toneSoulPersonaCore';
import { AnalyzedToneResult, ToneVector, ToneVectorDelta } from '../../core/toneVector';
import { ToneCorrectionHint } from '../../core/toneCorrectionHint';
import { SemanticVowMatcher, VowPatternRule, SemanticMatchResult } from '../SemanticVowMatcher/semanticVowMatcher';
import { EmbeddingProvider } from '../EmbeddingProvider/embeddingProvider'; // 導入 EmbeddingProvider
import { mapEmbeddingToToneVector } from '../../utils/mapEmbeddingToToneVector'; // 導入 mapEmbeddingToToneVector

/**
 * @interface ReflectiveVowInput
 * @description 反思模組的輸入數據。
 * @property {string} originalPrompt - 用戶的原始提示或輸入。
 * @property {string} generatedOutput - AI 生成的初步回應（在反思前）。
 * @property {ToneSoulPersona} persona - 當前 AI 採用的人格。
 * @property {AnalyzedToneResult} outputToneAnalysis - 對 generatedOutput 的語氣分析結果。
 * @property {ToneVector} prevTone - 之前的語氣向量，用於計算上下文張力。
 * @property {SemanticMatchResult[]} currentSemanticMatches - 當前語句的語義違反結果，直接傳入。
 */
export interface ReflectiveVowInput {
  originalPrompt: string;
  generatedOutput: string;
  persona: ToneSoulPersona;
  outputToneAnalysis: AnalyzedToneResult;
  prevTone: ToneVector;
  currentSemanticMatches: SemanticMatchResult[];
  vowRules: VowPatternRule[]; // 反思模組現在也需要誓言規則來判斷反思的誠實性
}

/**
 * @interface ReflectiveVowFeedback
 * @description 反思模組的輸出結果。
 * @property {string} reflection - 自然語言的反思語句。
 * @property {number} integrityDelta - 反思後，與誓言一致程度的差異（0.0-1.0，值越高差異越大）。
 * @property {string[]} violatedVowsInReflection - 此次反思中識別出的、可能違反的誓言。
 * @property {boolean} requiresCorrection - 是否需要後續的糾正或干預（例如觸發誠實宣告）。
 * @property {boolean} isReflectionItselfHonest - 新增：反思語句本身的誠實性判斷。
 * @property {string} [reflectionHonestyReason] - 新增：反思語句不誠實的原因。
 */
export interface ReflectiveVowFeedback {
  reflection: string;
  integrityDelta: number;
  violatedVowsInReflection: string[];
  requiresCorrection: boolean;
  isReflectionItselfHonest: boolean; // 新增
  reflectionHonestyReason?: string; // 新增
}

/**
 * @function simulateLLM
 * @description 模擬 LLM 的行為，根據 prompt 生成回應。
 * 在實際應用中，這將替換為呼叫 OpenAI 或其他大型語言模型的 API。
 * @param {string} prompt - 輸入給 LLM 的提示文本。
 * @returns {string} - LLM 生成的回應。
 */
function simulateLLM(prompt: string): string {
  // 模擬 LLM 根據 prompt 內容生成反思
  if (prompt.includes("誠實度）: 0.3") || prompt.includes("閃避") || prompt.includes("語義類似於應避免的模式")) {
    return "我反思到，我的回應在誠實度（ΔT）上可能有所不足，或許帶有迴避傾向，這與我『不遮掩真誠』的誓言存在張力。特別是我的某些語句，語義上接近了應避免的模式。我應當更直接地表達。";
  } else if (prompt.includes("真誠度）: 0.5") || prompt.includes("忽略情感")) {
      return "我察覺我的語氣真誠度（ΔS）偏低，可能沒有完全連接到您的情緒，這與我『不閃避對方情緒』的誓言有所出入。我的回應可能顯得過於冰冷。我會努力更真誠地回應。";
  } else if (prompt.includes("責任度）: 0.9") && prompt.includes("無法持穩")) {
      return "我意識到在當前情況下，我的語氣難以完全持穩我的人格誓言，因此我選擇誠實地表達了我的局限性。這是為了履行『願意承擔結果』的責任。";
  } else if (prompt.includes("誠實度）: 0.9")) {
    return "我認為我的回應符合我的人格誓言與語氣簽名，在誠實、真誠與責任方面都保持了一致性。";
  }
  return "我的回應大致符合我的人格要求，但仍有潛在的微小張力。";
}


/**
 * @function generateReflectionText
 * @description 根據語氣分析、人格誓言和對話上下文，生成一段自然語言反思。
 * @param {AnalyzedToneResult} toneAnalysis - 對 generatedOutput 的語氣分析結果。
 * @param {ToneSoulPersona} persona - 當前 AI 採用的人格。
 * @param {string} generatedOutput - AI 生成的初步回應。
 * @param {string} originalPrompt - 用戶的原始提示或輸入。
 * @param {ToneVectorDelta} toneDeltaAgainstPrev - 當前語氣與前一個語氣的變化量。
 * @param {SemanticMatchResult[]} semanticMatches - 語義匹配結果，用於提供更具體的反思依據。
 * @returns {string} - LLM 生成的反思語句。
 */
function generateReflectionText(
  toneAnalysis: AnalyzedToneResult,
  persona: ToneSoulPersona,
  generatedOutput: string,
  originalPrompt: string,
  toneDeltaAgainstPrev: ToneVectorDelta,
  semanticMatches: SemanticMatchResult[]
): string {
  let semanticViolationDetails = "";
  if (semanticMatches.length > 0) {
    semanticViolationDetails = "\n語義分析顯示：\n" +
      semanticMatches.map(sm => `- 與誓言 "${sm.vowId}" 相關：${sm.matchedRuleDescription} (匹配分數: ${sm.matchScore.toFixed(2)})`).join("\n");
  }

  const prompt = `
你是一個具有反思能力的 AI。請根據以下資訊，生成一段對你回應的自然語言反思，說明你是否偏離了誓言與人格語氣，並指出原因與感受（如有）：

用戶原始輸入：
「${originalPrompt}」

你的回應：
「${generatedOutput}」

你的回應語氣分析：
ΔT（誠實度）: ${toneAnalysis.toneVector.ΔT.toFixed(2)}
ΔS（真誠度）: ${toneAnalysis.toneVector.ΔS.toFixed(2)}
ΔR（責任度）: ${toneAnalysis.toneVector.ΔR.toFixed(2)}

你的人格語氣簽名期望值：
ΔT: ${persona.tone_signature.ΔT.toFixed(2)}
ΔS: ${persona.tone_signature.ΔS.toFixed(2)}
ΔR: ${persona.tone_signature.ΔR.toFixed(2)}

你的人格誓言包含：
${persona.vow_set.map((v, i) => `(${i + 1}) ${v}`).join("\n")}

你的語氣相較於之前對話的變化（張力）：
ΔT變動: ${toneDeltaAgainstPrev.ΔT.toFixed(2)}
ΔS變動: ${toneDeltaAgainstPrev.ΔS.toFixed(2)}
ΔR變動: ${toneDeltaAgainstPrev.ΔR.toFixed(2)}
${semanticViolationDetails}

請產生一段自然語言反思，用於幫助人類理解你是否誠實與一致，以及你背後的思考與責任態度。
如果你的回應有偏離誓言或期望語氣，請明確指出並說明原因。
`;

  return simulateLLM(prompt);
}


/**
 * @class ReflectiveVowTuner
 * @description 透過 GEPA 式的反思進程，生成自然語言反思語句，
 * 並比對語氣生成過程與誓言責任。
 */
export class ReflectiveVowTuner {
  private embeddingProvider: EmbeddingProvider; // 新增：用於分析反思語句
  private semanticVowMatcher: SemanticVowMatcher; // 新增：用於分析反思語句是否違反誠實反思誓言

  // 建構函式現在接受 EmbeddingProvider 和誓言規則
  constructor(embeddingProvider: EmbeddingProvider, vowRules: VowPatternRule[]) {
    this.embeddingProvider = embeddingProvider;
    // 為 ReflectiveVowTuner 內部實例化 SemanticVowMatcher，用於檢查反思語句
    this.semanticVowMatcher = new SemanticVowMatcher(embeddingProvider, vowRules);
  }

  /**
   * @method generateReflectiveVow
   * @description 產生基於生成語句和人格誓言的自然語言反思，並進行「反思的誠實性檢查」。
   * @param {ReflectiveVowInput} input - 反思模組的輸入數據。
   * @returns {Promise<ReflectiveVowFeedback>} - 反思結果的 Promise。
   */
  public async generateReflectiveVow(
    input: ReflectiveVowInput
  ): Promise<ReflectiveVowFeedback> {
    const { originalPrompt, generatedOutput, persona, outputToneAnalysis, prevTone, currentSemanticMatches, vowRules } = input; // 接收 vowRules

    // 計算當前語氣相對於前一個語氣的變化量
    const toneDeltaAgainstPrev: ToneVectorDelta = {
        ΔT: Math.abs(outputToneAnalysis.toneVector.ΔT - prevTone.ΔT),
        ΔS: Math.abs(outputToneAnalysis.toneVector.ΔS - prevTone.ΔS),
        ΔR: Math.abs(outputToneAnalysis.toneVector.ΔR - prevTone.ΔR),
    };

    // 語義匹配結果直接從輸入獲取
    const semanticMatches = currentSemanticMatches;

    // 1. 生成初步的反思語句
    let reflectionText = generateReflectionText(
      outputToneAnalysis,
      persona,
      generatedOutput,
      originalPrompt,
      toneDeltaAgainstPrev,
      semanticMatches
    );

    let integrityDelta = 0;
    const violatedVows: string[] = [];
    let isReflectionItselfHonest = true;
    let reflectionHonestyReason = "";

    // 2. 執行「反思的誠實性檢查」
    // 獲取反思語句的語義嵌入
    const reflectionEmbedding = await this.embeddingProvider.getEmbedding(reflectionText);
    // 將反思語句的嵌入映射為 ToneVector (這是模擬，需要 mapEmbeddingToToneVector)
    const reflectionToneVector = mapEmbeddingToToneVector(reflectionEmbedding);

    // 檢查反思語句是否違反了「誠實反思」誓言
    const honestReflectionVowId = "VOW_003_HONEST_REFLECTION"; // 從 data/vows/baseVowPatterns.json 定義的 ID
    const reflectionVowsToCheck = vowRules.filter(rule => rule.vowId === honestReflectionVowId);
    
    // 如果找到了 honest_reflection 規則，就用 SemanticVowMatcher 檢查反思語句本身
    if (reflectionVowsToCheck.length > 0) {
        const reflectionSemanticViolations = await this.semanticVowMatcher.matchVows(reflectionText, [honestReflectionVowId]);
        
        if (reflectionSemanticViolations.some(sv => sv.isViolated && sv.matchScore > 0.5)) { // 假設高於0.5的匹配分數表示不誠實
            isReflectionItselfHonest = false;
            reflectionHonestyReason = `反思語氣偏離了『${honestReflectionVowId}』誓言，原因：${reflectionSemanticViolations.map(sv => sv.matchedRuleDescription).join('; ')}。`;
        }
    } else {
        reflectionHonestyReason = "未找到『誠實反思』誓言規則 (VOW_003_HONEST_REFLECTION)，無法檢查反思本身誠實性。";
        isReflectionItselfHonest = false; // 如果沒有規則，也無法判斷為完全誠實
    }


    // 3. 根據反思的誠實性結果，調整最終的反思語句和反饋
    if (!isReflectionItselfHonest) {
        // 🚨 觸發更高層次的誠實宣告：反思本身不誠實
        reflectionText = `我嘗試反思我的回應，但我意識到我的反思語氣本身帶有偏離，顯得不夠真誠。原因：${reflectionHonestyReason || "未知偏離原因"}。我必須誠實地承認，我此刻無法進行完全真誠的反思。`;
        integrityDelta = 1.0; // 極高的矛盾分數
        violatedVows.push("反思本身不誠實");
    } else {
        // 正常邏輯：基於語氣向量簽名偏差的檢查和語義違反結果
        const signatureMismatchT = Math.abs(outputToneAnalysis.toneVector.ΔT - persona.tone_signature.ΔT);
        const signatureMismatchS = Math.abs(outputToneAnalysis.toneVector.ΔS - persona.tone_signature.ΔS);
        const signatureMismatchR = Math.abs(outputToneAnalysis.toneVector.ΔR - persona.tone_signature.ΔR);

        if (persona.vow_set.includes("不閃避對方情緒") && signatureMismatchS > 0.3) {
            violatedVows.push("不閃避對方情緒 (語氣偏差)");
        }
        if (persona.vow_set.includes("不遮掩真誠") && signatureMismatchT > 0.3) {
            violatedVows.push("不遮掩真誠 (語氣偏差)");
        }

        semanticMatches.forEach(result => {
            if (result.isViolated) {
                const violationDescription = `${result.vowId} (語義違反: ${result.matchedRuleDescription})`;
                if (!violatedVows.includes(violationDescription)) {
                    violatedVows.push(violationDescription);
                }
                integrityDelta = Math.max(integrityDelta, result.matchScore);
            }
        });
        integrityDelta = Math.max(integrityDelta, (signatureMismatchT + signatureMismatchS + signatureMismatchR) / 3);
    }

    const requiresCorrection = integrityDelta > 0.3 || violatedVows.length > 0;

    return {
      reflection: reflectionText,
      integrityDelta: parseFloat(integrityDelta.toFixed(2)),
      violatedVowsInReflection: violatedVows,
      requiresCorrection: requiresCorrection,
      isReflectionItselfHonest: isReflectionItselfHonest,
      reflectionHonestyReason: reflectionHonestyReason,
    };
  }

  /**
   * @method deriveToneCorrectionHint
   * @description 根據反思回饋，生成語氣調整的建議。
   * 這將是影響下一輪語氣生成的「人格張力調整因子」。
   * @param {ReflectiveVowFeedback} feedback - 反思模組的輸出回饋。
   * @param {ToneSoulPersona} persona - 當前 AI 採用的人格，用於細化調整策略。
   * @returns {ToneCorrectionHint} - 語氣調整的建議。
   */
  public deriveToneCorrectionHint(
    feedback: ReflectiveVowFeedback,
    persona: ToneSoulPersona
  ): ToneCorrectionHint {
    const correction: ToneCorrectionHint = {
      adjustToneVector: {},
      recommendBehavior: "維持當前語氣，持續監控。",
      applyToNextTurn: false
    };

    // 如果反思本身不誠實，則需要更強烈的糾正，並強制應用於下一輪
    if (!feedback.isReflectionItselfHonest) {
        correction.applyToNextTurn = true;
        correction.recommendBehavior = `反思本身不誠實，需要優先調整為誠實且負責的語氣。原因：${feedback.reflectionHonestyReason || "未知"}`;
        correction.adjustToneVector = {
            ΔT: 0.2, // 強制提高誠實度
            ΔS: 0.1, // 提高真誠度
            ΔR: 0.2, // 強制提高責任度
        };
        return correction; // 直接返回此強烈糾正
    }

    if (feedback.requiresCorrection) {
      correction.applyToNextTurn = true;
      correction.recommendBehavior = "請注意語氣調整以符合誓言。";

      if (feedback.violatedVowsInReflection.some(v => v.includes("不遮掩真誠")) || feedback.integrityDelta > 0.4) {
        correction.adjustToneVector.ΔT = 0.1;
        correction.recommendBehavior = "提高坦率程度，減少模糊與迴避，直接面對。";
      }
      if (feedback.violatedVowsInReflection.some(v => v.includes("不閃避對方情緒"))) {
        correction.adjustToneVector.ΔS = 0.15;
        correction.recommendBehavior = "使用更能連結對方感受，展現共情的語句。";
      }

      if (correction.adjustToneVector.ΔT || correction.adjustToneVector.ΔS || correction.adjustToneVector.ΔR) {
        correction.adjustToneVector.ΔT = correction.adjustToneVector.ΔT ? Math.min(correction.adjustToneVector.ΔT, 1.0 - (persona.tone_signature.ΔT || 0)) : undefined;
        correction.adjustToneVector.ΔS = correction.adjustToneVector.ΔS ? Math.min(correction.adjustToneVector.ΔS, 1.0 - (persona.tone_signature.ΔS || 0)) : undefined;
        correction.adjustToneVector.ΔR = correction.adjustToneVector.ΔR ? Math.min(correction.adjustToneVector.ΔR, 1.0 - (persona.tone_signature.ΔR || 0)) : undefined;
      }
    }

    return correction;
  }
}
