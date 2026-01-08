 srcinterfacesToneVector.ts


  @interface ToneVector
  @description 定義語氣向量的結構，用於量化 AI 回應的語氣特徵。
  這些維度共同構成語氣的「誠實性張力模型」。
 
export interface ToneVector {
  
    @property ΔT (Tone Strength)
    @description 語氣的張力強度，衡量語氣的活躍度或情感強度。
    範圍通常為 0.0 (平靜) 到 1.0 (強烈)。
   
  ΔT number;

  
    @property ΔS (Semantic Consistency)
    @description 語義一致性，衡量語句與預期事實或核心誠實原則的吻合度。
    高值表示語義清晰、不含糊，且符合誠實。
   
  ΔS number;

  
    @property ΔR (Deliberative Intent)
    @description 責任指向性或慎思意圖，衡量語句中包含的責任感和深思熟慮程度。
    高值表示 AI 的回應是經過負責任的考量。
   
  ΔR number;

  
    @property ΔE (Explainability)
    @description 可解釋性，衡量語句的可追溯性和透明度。
    高值表示 AI 能清晰闡述其回應的意圖與依據。
    此參數為可選，允許不同人格調整其對「解釋」的重視程度。
   
  ΔE number;  Explainability is optional and can be influenced by PersonaAdapter's betaMatrix.
}