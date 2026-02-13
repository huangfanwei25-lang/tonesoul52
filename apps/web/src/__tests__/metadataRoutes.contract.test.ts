import { afterEach, describe, expect, it } from "vitest";

import robots from "../app/robots";
import sitemap from "../app/sitemap";

const originalEnv = { ...process.env };

afterEach(() => {
    process.env = { ...originalEnv };
});

describe("metadata routes contract", () => {
    it("sitemap includes root/docs/showcase and excludes notes", () => {
        process.env.NEXT_PUBLIC_SITE_URL = "https://example.com";
        process.env.VERCEL_ENV = "production";

        const entries = sitemap();
        const urls = new Set(entries.map((entry) => entry.url));

        expect(urls.has("https://example.com")).toBe(true);
        expect(urls.has("https://example.com/showcase")).toBe(true);
        expect(urls.has("https://example.com/docs")).toBe(true);
        expect(urls.has("https://example.com/notes")).toBe(false);
    });

    it("robots blocks all indexing in non-production", () => {
        process.env.VERCEL_ENV = "preview";

        const payload = robots();
        expect(payload.rules).toEqual([{ userAgent: "*", disallow: "/" }]);
    });

    it("robots allows public pages but disallows api and notes in production", () => {
        process.env.VERCEL_ENV = "production";
        process.env.NEXT_PUBLIC_SITE_URL = "https://example.com";

        const payload = robots();

        expect(payload.rules).toEqual([
            { userAgent: "*", allow: "/", disallow: ["/api/", "/notes"] },
        ]);
        expect(payload.sitemap).toBe("https://example.com/sitemap.xml");
    });
});
