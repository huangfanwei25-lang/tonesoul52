// src/interfaces/TracePoint.ts

import { ToneVector } from './ToneVector'; // 引入 ToneVector 介面

/**
 * @interface TracePoint
 * @description 定義語氣責任鏈上的單一追溯點。
 * 每個 TracePoint 代表 AI 在特定時間點的一次語氣輸出，
 * 記錄了語氣的關鍵參數、所屬人格，以及與誓言一致性的相關指標。
 * 這些點共同構成了可追溯的「責任鏈」。
 */
export interface TracePoint {
  /**
   * @property id
   * @description 唯一識別碼，用於追蹤單一語氣輸出。
   */
  id: string;

  /**
   * @property personaId
   * @description 產生此語氣的人格 ID。這對於多人格共享記憶時，避免責任歸屬污染至關重要。
   */
  personaId: string;

  /**
   * @property toneVector
   * @description 此次語氣輸出的 ToneVector 值 ([ΔT, ΔS, ΔR, ΔE])。
   */
  toneVector: [number, number, number, number];

  /**
   * @property timestamp
   * @description 語氣生成的時間戳記 (Unix 時間，毫秒)。
   */
  timestamp: number;

  /**
   * @property vowLinked
   * @description 標示此次語氣輸出是否與核心誓言成功連結。
   * (例如，經過 VowMatcher 判斷為對齊)。
   */
  vowLinked: boolean;

  /**
   * @property integrityDelta (Optional)
   * @description 此次語氣與期望誓言之間的完整性偏移程度。
   * 用於衡量語氣的「誠實性誤差」。
   */
  integrityDelta?: number;

  /**
   * @property betaMatrixHash (Optional)
   * @description 此次輸出時所使用的人格 betaMatrix 的哈希值。
   * 用於確保責任追溯時，能復原當時的權重配置。
   */
  betaMatrixHash?: string;

  /**
   * @property collapseLevel (Optional)
   * @description 如果此次輸出觸發了 TCAM，記錄當時的崩潰等級。
   */
  collapseLevel?: "normal" | "yellow" | "orange" | "red";
}