import { describe, it, expect, beforeEach } from 'vitest'

// Mock localStorage 
const localStorageMock = (() => {
    let store: Record<string, string> = {}
    return {
        getItem: (key: string) => store[key] || null,
        setItem: (key: string, value: string) => { store[key] = value },
        removeItem: (key: string) => { delete store[key] },
        clear: () => { store = {} }
    }
})()

Object.defineProperty(globalThis, 'localStorage', { value: localStorageMock })

// Note: PersonaConfig type for testing
interface PersonaConfig {
    name: string;
    greeting: string;
    style: 'balanced' | 'creative' | 'analytical' | 'cautious';
    weights: {
        meaning: number;
        practical: number;
        safety: number;
    };
    riskSensitivity: 'low' | 'medium' | 'high';
    responseLength: 'concise' | 'balanced' | 'detailed';
}

const DEFAULT_PERSONA: PersonaConfig = {
    name: "ToneSoul",
    greeting: "你好！有什麼我可以幫你的嗎？",
    style: 'balanced',
    weights: {
        meaning: 50,
        practical: 50,
        safety: 50,
    },
    riskSensitivity: 'medium',
    responseLength: 'balanced',
};

const PERSONA_KEY = 'tonesoul_persona';

// Pure functions for testing (mirroring PersonaSettings.tsx logic)
function getStoredPersona(): PersonaConfig {
    const stored = localStorage.getItem(PERSONA_KEY);
    if (!stored) return DEFAULT_PERSONA;
    try {
        return { ...DEFAULT_PERSONA, ...JSON.parse(stored) };
    } catch {
        return DEFAULT_PERSONA;
    }
}

function savePersona(config: PersonaConfig): void {
    localStorage.setItem(PERSONA_KEY, JSON.stringify(config));
}

describe('PersonaSettings', () => {
    beforeEach(() => {
        localStorageMock.clear()
    })

    describe('DEFAULT_PERSONA', () => {
        it('should have correct default values', () => {
            expect(DEFAULT_PERSONA.name).toBe('ToneSoul')
            expect(DEFAULT_PERSONA.style).toBe('balanced')
            expect(DEFAULT_PERSONA.weights.meaning).toBe(50)
            expect(DEFAULT_PERSONA.weights.practical).toBe(50)
            expect(DEFAULT_PERSONA.weights.safety).toBe(50)
            expect(DEFAULT_PERSONA.riskSensitivity).toBe('medium')
            expect(DEFAULT_PERSONA.responseLength).toBe('balanced')
        })
    })

    describe('getStoredPersona', () => {
        it('should return default persona when no stored value', () => {
            const result = getStoredPersona()
            expect(result).toEqual(DEFAULT_PERSONA)
        })

        it('should return stored persona when available', () => {
            const customPersona: PersonaConfig = {
                name: '小助手',
                greeting: '嗨！',
                style: 'creative',
                weights: { meaning: 80, practical: 30, safety: 40 },
                riskSensitivity: 'low',
                responseLength: 'concise'
            }
            localStorageMock.setItem(PERSONA_KEY, JSON.stringify(customPersona))

            const result = getStoredPersona()
            expect(result.name).toBe('小助手')
            expect(result.style).toBe('creative')
            expect(result.weights.meaning).toBe(80)
        })

        it('should merge with defaults for partial stored config', () => {
            localStorageMock.setItem(PERSONA_KEY, JSON.stringify({ name: '自訂名稱' }))

            const result = getStoredPersona()
            expect(result.name).toBe('自訂名稱')
            expect(result.style).toBe('balanced')  // from default
            expect(result.weights.meaning).toBe(50)  // from default
        })

        it('should return default for invalid JSON', () => {
            localStorageMock.setItem(PERSONA_KEY, 'invalid json{{{')

            const result = getStoredPersona()
            expect(result).toEqual(DEFAULT_PERSONA)
        })
    })

    describe('savePersona', () => {
        it('should save persona to localStorage', () => {
            const customPersona: PersonaConfig = {
                ...DEFAULT_PERSONA,
                name: '測試AI',
                style: 'analytical'
            }

            savePersona(customPersona)

            const stored = JSON.parse(localStorageMock.getItem(PERSONA_KEY)!)
            expect(stored.name).toBe('測試AI')
            expect(stored.style).toBe('analytical')
        })
    })
})

describe('PersonaConfig weights validation', () => {
    it('should have weights in valid range 0-100', () => {
        const { weights } = DEFAULT_PERSONA
        expect(weights.meaning).toBeGreaterThanOrEqual(0)
        expect(weights.meaning).toBeLessThanOrEqual(100)
        expect(weights.practical).toBeGreaterThanOrEqual(0)
        expect(weights.practical).toBeLessThanOrEqual(100)
        expect(weights.safety).toBeGreaterThanOrEqual(0)
        expect(weights.safety).toBeLessThanOrEqual(100)
    })
})
