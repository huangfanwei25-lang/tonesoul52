// src/core/toneVector.ts

/**
 * @file Defines the core ToneVector and its related interfaces.
 * @version 1.2
 *
 * [Architectural Note on Vector Duality - v1.2]
 * The ToneVector serves a dual purpose within the ToneSoul system, based on the TRSC principle
 * (Tone Responsibility Semantic Conversion).
 *
 * 1. As a "Behavioral Vector": It describes the observable characteristics of language.
 * - In this context: ΔT=Tension, ΔS=SpeechAct Direction, ΔR=Rationality.
 *
 * 2. As the basis for an "Integrity Vector": It is mapped and re-interpreted to assess abstract qualities.
 * - In this context: ΔT -> Truthfulness, ΔS -> Sincerity, ΔR -> Responsibility.
 *
 * This mapping is handled by the PerspectiveMapper to ensure a stable core API while allowing
 * for context-aware interpretation.
 */

/**
 * Defines the possible categories for the pragmatic intent of an utterance.
 * This can be expanded in the future.
 */
export type ToneSemanticType =
  | "request"
  | "command"
  | "reveal"
  | "question"
  | "assert"
  | "joke"
  | "warning"
  | "apology"
  | "deny"
  | "test"
  | "other";

/**
 * @interface ToneVector
 * @description Defines the core behavioral vector of a linguistic expression.
 * Each value should range from 0.0 to 1.0.
 */
export interface ToneVector {
  /**
   * @property {number} ΔT - Tension: The intensity or forcefulness of the tone.
   */
  ΔT: number;

  /**
   * @property {ToneSemanticType} ΔS - SpeechAct Direction: The pragmatic intent of the utterance.
   */
  ΔS: ToneSemanticType;

  /**
   * @property {number} ΔR - Rationality: The degree of logical control vs. emotionality.
   */
  ΔR: number;
}

/**
 * @interface AnalyzedToneResult
 * @description The detailed result of a tone analysis, containing the ToneVector and other optional features.
 * @property {ToneVector} toneVector - The calculated ToneVector for the text.
 * @property {object} [semanticFeatures] - Optional: Semantic features like keywords, sentiment, topics.
 * @property {string[]} [linguisticFeatures] - Optional: Linguistic features like sentence structure, word frequency.
 */
export interface AnalyzedToneResult {
  toneVector: ToneVector;
  semanticFeatures?: { [key: string]: any };
  linguisticFeatures?: string[];
}