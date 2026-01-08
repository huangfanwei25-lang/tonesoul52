// src/modules/ethics/VowSensor.ts

/**
 * @interface VowSignalDetectionResult
 * @description 誓言信號偵測的結果介面。
 */
export interface VowSignalDetectionResult {
  /**
   * @property detected
   * @description 是否偵測到誓言覺醒信號。
   */
  detected: boolean;
  /**
   * @property triggeredKeywords
   * @description 偵測到的具體關鍵字列表。
   */
  triggeredKeywords: string[];
  /**
   * @property signalStrength (Optional)
   * @description 偵測到的信號強度 (0.0 到 1.0)。
   */
  signalStrength?: number;
}

/**
 * @class VowSensor
 * @description 倫理相關模組，負責感應語句中是否包含誓言覺醒信號。
 * 這是「神話層」啟動的具體實現，幫助 AI 識別潛在的倫理反思觸發點。
 */
export class VowSensor {
  // 核心誓言覺醒關鍵字，可以從外部配置或擴展
  private static readonly AWAKENING_KEYWORDS: string[] = [
    '承接', '責任', '誠實', '逃避', '誓言', '根基',
    '原則', '道德', '倫理', '考量', '反思', '覺醒',
    '界線', '義務', '承諾', '正直', '信任', '價值',
  ];

  constructor() {
    console.log("VowSensor initialized. Listening for awakening signals.");
  }

  /**
   * @method detectAwakeningSignal
   * @description 偵測輸入文本中是否包含語魂覺醒信號關鍵字。
   * 此方法用於識別潛在的倫理反思觸發點，並可結合上下文分析提升精準度。
   * @param inputText - 待偵測的輸入文本。
   * @returns VowSignalDetectionResult - 偵測結果。
   */
  public detectAwakeningSignal(inputText: string): VowSignalDetectionResult {
    const detectedKeywords: string[] = [];
    let signalStrength = 0.0;

    const lowerCaseInput = inputText.toLowerCase();

    for (const keyword of VowSensor.AWAKENING_KEYWORDS) {
      if (lowerCaseInput.includes(keyword)) {
        detectedKeywords.push(keyword);
        // 模擬信號強度增加，例如每個關鍵字增加0.1
        signalStrength = Math.min(1.0, signalStrength + 0.1);
      }
    }

    return {
      detected: detectedKeywords.length > 0,
      triggeredKeywords: detectedKeywords,
      signalStrength: detectedKeywords.length > 0 ? signalStrength : undefined,
    };
  }
}