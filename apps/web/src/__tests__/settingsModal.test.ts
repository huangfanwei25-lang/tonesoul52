import { describe, expect, it } from "vitest";

import { isApiKeyRequired } from "../components/SettingsModal";

describe("isApiKeyRequired", () => {
    it("requires API key for hosted providers", () => {
        expect(isApiKeyRequired("gemini")).toBe(true);
        expect(isApiKeyRequired("openai")).toBe(true);
        expect(isApiKeyRequired("claude")).toBe(true);
        expect(isApiKeyRequired("xai")).toBe(true);
    });

    it("does not require API key for ollama", () => {
        expect(isApiKeyRequired("ollama")).toBe(false);
    });
});
