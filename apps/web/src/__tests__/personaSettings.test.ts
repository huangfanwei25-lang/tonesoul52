import { beforeEach, describe, expect, it } from "vitest";

import {
    DEFAULT_PERSONA,
    getStoredPersona,
    normalizePersonaConfig,
    savePersona,
    type PersonaConfig,
} from "../components/PersonaSettings";

const localStorageMock = (() => {
    let store: Record<string, string> = {};
    return {
        getItem: (key: string) => store[key] || null,
        setItem: (key: string, value: string) => {
            store[key] = value;
        },
        removeItem: (key: string) => {
            delete store[key];
        },
        clear: () => {
            store = {};
        },
    };
})();

Object.defineProperty(globalThis, "localStorage", { value: localStorageMock });
Object.defineProperty(globalThis, "window", {
    value: { localStorage: localStorageMock },
    configurable: true,
});

const PERSONA_KEY = "tonesoul_persona";

describe("PersonaSettings storage", () => {
    beforeEach(() => {
        localStorageMock.clear();
    });

    it("keeps default persona shape with customRoles", () => {
        expect(DEFAULT_PERSONA.name).toBe("ToneSoul");
        expect(DEFAULT_PERSONA.customRoles).toEqual([]);
    });

    it("returns defaults when storage is empty", () => {
        const result = getStoredPersona();
        expect(result).toEqual(DEFAULT_PERSONA);
    });

    it("normalizes stored payload and keeps custom roles", () => {
        localStorageMock.setItem(
            PERSONA_KEY,
            JSON.stringify({
                name: "Custom",
                weights: { meaning: 101, practical: -1, safety: 66 },
                customRoles: [
                    {
                        name: "Risk Auditor",
                        description: "Find failure paths",
                        promptHint: "Fail closed first",
                        attachments: [{ label: "policy", path: "docs/policy.md", note: "baseline" }],
                    },
                ],
            })
        );

        const result = getStoredPersona();
        expect(result.name).toBe("Custom");
        expect(result.weights.meaning).toBe(100);
        expect(result.weights.practical).toBe(0);
        expect(result.weights.safety).toBe(66);
        expect(result.customRoles).toHaveLength(1);
        expect(result.customRoles[0].name).toBe("Risk Auditor");
        expect(result.customRoles[0].attachments[0].path).toBe("docs/policy.md");
    });

    it("returns default payload on invalid JSON", () => {
        localStorageMock.setItem(PERSONA_KEY, "not-json");
        const result = getStoredPersona();
        expect(result).toEqual(DEFAULT_PERSONA);
    });

    it("savePersona persists normalized config", () => {
        const payload: PersonaConfig = {
            ...DEFAULT_PERSONA,
            name: "Persona-X",
            customRoles: [
                {
                    id: "r1",
                    name: "Planner",
                    description: "Action oriented",
                    promptHint: "Sequence by risk",
                    attachments: [
                        { id: "a1", label: "task", path: "task.md", note: "main queue" },
                    ],
                },
            ],
        };
        savePersona(payload);
        const raw = JSON.parse(String(localStorageMock.getItem(PERSONA_KEY)));
        expect(raw.name).toBe("Persona-X");
        expect(raw.customRoles[0].attachments[0].path).toBe("task.md");
    });

    it("normalizePersonaConfig drops empty custom roles", () => {
        const result = normalizePersonaConfig({
            ...DEFAULT_PERSONA,
            customRoles: [{ name: "", description: "", promptHint: "", attachments: [] }],
        });
        expect(result.customRoles).toEqual([]);
    });
});
