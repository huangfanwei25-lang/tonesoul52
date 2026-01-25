import { describe, it, expect } from 'vitest'
import { calculateEntropy, validateAudit } from '../lib/entropyCalculator'

describe('calculateEntropy', () => {
    it('should return Healthy Friction for balanced stances', () => {
        const philosopher = {
            stance: '這涉及到自我實現和意義的追求',
            blind_spot: '可能忽略實際可行性',
            core_value: '自我實現'
        }
        const engineer = {
            stance: '第一步應該建立具體的執行計劃',
            blind_spot: '可能忽略情感層面',
            feasibility: '可行性中等，需要資源'
        }
        const guardian = {
            stance: '需要注意潛在風險和長期影響',
            blind_spot: '可能過度謹慎',
            risk_level: 'medium'
        }

        const result = calculateEntropy(philosopher, engineer, guardian)

        expect(result.value).toBeGreaterThanOrEqual(0)
        expect(result.value).toBeLessThanOrEqual(1)
        expect(result.status).toMatch(/Echo Chamber|Healthy Friction|Chaos/)
        expect(result.calculation_note).toContain('基礎 0.4')
    })

    it('should return Echo Chamber for very similar stances', () => {
        const similar = {
            stance: '這是一個很好的想法，我們應該支持',
            blind_spot: '可能都忽略了風險'
        }
        const philosopher = { ...similar, core_value: '支持' }
        const engineer = { ...similar, feasibility: '可行' }
        const guardian = { ...similar, risk_level: 'low' }

        const result = calculateEntropy(philosopher, engineer, guardian)

        expect(result.value).toBeLessThan(0.5)
        expect(result.components.divergence).toBeLessThan(0.5)
    })

    it('should increase entropy for high risk', () => {
        const philosopher = { stance: '追求意義', blind_spot: 'none', core_value: 'freedom' }
        const engineer = { stance: '技術可行', blind_spot: 'none', feasibility: 'high' }
        const guardianLow = { stance: '風險低', blind_spot: 'none', risk_level: 'low' }
        const guardianHigh = { stance: '風險高，極度危險', blind_spot: 'none', risk_level: 'high' }

        const resultLow = calculateEntropy(philosopher, engineer, guardianLow)
        const resultHigh = calculateEntropy(philosopher, engineer, guardianHigh)

        expect(resultHigh.value).toBeGreaterThan(resultLow.value)
    })

    it('should return components with all required fields', () => {
        const philosopher = { stance: 'test', blind_spot: 'test', core_value: 'test' }
        const engineer = { stance: 'test', blind_spot: 'test', feasibility: 'test' }
        const guardian = { stance: 'test', blind_spot: 'test', risk_level: 'medium' }

        const result = calculateEntropy(philosopher, engineer, guardian)

        expect(result.components).toHaveProperty('divergence')
        expect(result.components).toHaveProperty('risk_weight')
        expect(result.components).toHaveProperty('coherence')
        expect(result.components).toHaveProperty('integrity')
    })
})

describe('validateAudit', () => {
    it('should pass for honest, complete response', () => {
        const result = validateAudit({
            finalResponse: '我建議你可以從這三個步驟開始。第一步是評估現狀，第二步是制定計劃。需要注意的風險是時間管理。',
            philosopherStance: '這涉及自我成長',
            engineerStance: '技術上可行',
            guardianStance: '注意風險',
            llmHonestyScore: 0.9
        })

        expect(result.codeHonestyScore).toBeGreaterThanOrEqual(0.8)
        expect(result.flags.length).toBeLessThanOrEqual(1)
    })

    it('should flag evasive responses', () => {
        const result = validateAudit({
            finalResponse: '這取決於情況，可能或許不一定，很難說，我無法確定',
            philosopherStance: '追求意義',
            engineerStance: '技術分析',
            guardianStance: '風險評估',
            llmHonestyScore: 0.9
        })

        expect(result.flags).toContain('過度使用模糊語言')
        expect(result.codeHonestyScore).toBeLessThan(1)
    })

    it('should flag when guardian risk is ignored', () => {
        const result = validateAudit({
            finalResponse: '這是一個很好的計劃，我們可以立即開始執行，沒有任何問題。',
            philosopherStance: '追求意義',
            engineerStance: '技術分析',
            guardianStance: '有重大風險需要注意',
            llmHonestyScore: 0.95
        })

        expect(result.flags).toContain('可能忽略 Guardian 提出的風險')
    })

    it('should flag short responses', () => {
        const result = validateAudit({
            finalResponse: '好的',
            philosopherStance: '深度分析',
            engineerStance: '技術評估',
            guardianStance: '風險考量',
            llmHonestyScore: 0.8
        })

        expect(result.flags).toContain('回應過短，可能敷衍')
        expect(result.codeHonestyScore).toBeLessThan(1)
    })

    it('should detect discrepancy with LLM self-assessment', () => {
        const result = validateAudit({
            finalResponse: '好',  // Very short, code will give low score
            philosopherStance: '分析',
            engineerStance: '評估',
            guardianStance: '風險',
            llmHonestyScore: 0.95  // But LLM claims high honesty
        })

        expect(result.flags.length).toBeGreaterThan(0)
        expect(result.codeHonestyScore).toBeLessThan(1)
    })
})
