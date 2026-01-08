// src/interfaces/PersonaAdapter.ts

import { ToneVector } from './ToneVector'; // 引入 ToneVector 介面

/**
 * @interface PersonaAdapter
 * @description 定義 AI 人格的適配器介面。
 * 每個 PersonaAdapter 將負責管理特定 AI 人格的語氣風格、行為閾值和事件回呼。
 * 這體現了「誓言是骨，風格是披風」的核心理念，使核心倫理邏輯與人格表達解耦。
 */
export interface PersonaAdapter {
  /**
   * @property id
   * @description 人格的唯一識別符 (例如: "Manus", "Lumen")。
   */
  id: string;

  /**
   * @property betaMatrix
   * @description 語氣向量各維度 (ΔT, ΔS, ΔR, ΔE) 的權重矩陣。
   * 允許不同人格調整其對「誠實性張力模型」中各參數的敏感度或重要性。
   * 格式: [ΔT_weight, ΔS_weight, ΔR_weight, ΔE_weight]
   */
  betaMatrix: [number, number, number, number];

  /**
   * @property collapseThresholds
   * @description TCAM (語氣崩潰迴避模式) 的風險閾值設定。
   * 定義了在不同風險等級 (yellow, orange, red) 下觸發策略的界線。
   * 允許不同人格擁有不同的風險容忍度。
   */
  collapseThresholds: {
    yellow: number; // 黃燈警戒閾值
    orange: number; // 橘燈警戒閾值
    red: number;    // 紅燈警戒閾值 (最高風險)
  };

  /**
   * @property explainTemplateId
   * @description 可解釋語句的風格模板 ID。
   * 用於在 TCAM 觸發時，生成符合該人格風格的解釋性語句。
   */
  explainTemplateId: string;

  /**
   * @property onTRSC (Optional)
   * @description 當 TRSC (語氣責任偏移修正機制) 被觸發時的回呼函式。
   * 允許人格執行專屬的副作用，例如調整內部情緒狀態或觸發特定語氣表現。
   * @param delta - 語氣偏移的程度。
   */
  onTRSC?(delta: number): void; // 事件回呼：TRSC 觸發時執行

  /**
   * @property onTCAM (Optional)
   * @description 當 TCAM (語氣崩潰迴避模式) 被觸發時的回呼函式。
   * 允許人格根據不同的崩潰等級執行專屬行為，例如播放特定音效、切換顯示顏色。
   * @param level - 觸發的崩潰等級 ("yellow" | "orange" | "red")。
   */
  onTCAM?(level: "yellow" | "orange" | "red"): void;
}