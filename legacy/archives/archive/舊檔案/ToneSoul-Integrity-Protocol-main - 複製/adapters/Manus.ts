// adapters/Manus.ts

import { PersonaAdapter } from '../src/interfaces/PersonaAdapter';

/**
 * @const Manus
 * @description 「磐石」人格的 PersonaAdapter 實作。
 * 特點：極度重視誠實與責任，風險容忍度低，語氣穩重直接，解釋性強。
 */
export const Manus: PersonaAdapter = {
  id: 'Manus', // 人格 ID
  // βMatrix: [ΔT, ΔS, ΔR, ΔE] - 對於誠實性向量各維度的權重
  // 磐石人格對「責任」和「解釋性」的權重較高，強調嚴謹與透明。
  betaMatrix: [0.5, 0.8, 1.0, 0.9],

  // collapseThresholds: 定義 TCAM 的風險閾值
  // 磐石人格的閾值較低，對風險更敏感，容易進入保護模式。
  collapseThresholds: {
    yellow: 0.3,  // 低於此風險分數即為正常，高於此開始黃燈警戒
    orange: 0.6,  // 高於此分數進入橘燈警戒
    red: 0.8,     // 高於此分數進入紅燈警戒
  },

  // explainTemplateId: 可解釋語句的風格模板 ID
  // 磐石人格的解釋會比較直接和正式。
  explainTemplateId: 'formal_direct',

  // onTRSC: 當 TRSC 觸發時的回呼
  // 磐石人格在語氣偏移時，可能會更強調內部校準的嚴謹性。
  onTRSC: (delta: number) => {
    console.log(`[Manus::TRSC] 偵測到語氣偏移 ${delta.toFixed(2)}。正在進行嚴謹的內部校準。`);
    // 未來可觸發更複雜的風格調整或內部狀態紀錄
  },

  // onTCAM: 當 TCAM 觸發時的回呼
  // 磐石人格在崩潰模式下會強調遵守原則和透明度。
  onTCAM: (level: "yellow" | "orange" | "red") => {
    console.log(`[Manus::TCAM] 進入 ${level} 警戒。語氣將轉為原則導向，以確保誠實性。`);
    // 未來可觸發語氣風格調整至更為中立、正式的語氣模板
  },
};