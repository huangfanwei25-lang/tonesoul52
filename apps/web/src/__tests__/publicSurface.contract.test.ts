import fs from "node:fs";
import path from "node:path";

import { describe, expect, it } from "vitest";

function readAppFile(relativePath: string): string {
    const filePath = path.resolve(process.cwd(), "src", "app", relativePath);
    return fs.readFileSync(filePath, "utf-8");
}

describe("public surface contract", () => {
    it("docs page keeps required section anchors and cards", () => {
        const docsPage = readAppFile(path.join("docs", "page.tsx"));

        for (const anchor of ["paradoxes", "protocols", "audit", "research"]) {
            expect(docsPage).toContain(`id="${anchor}"`);
        }

        expect(docsPage).toContain("SevenParadoxCards");
        expect(docsPage).toContain("SevenDimensionCards");
    });

    it("showcase page keeps primary sections", () => {
        const showcasePage = readAppFile(path.join("showcase", "page.tsx"));

        for (const anchor of ["manifesto", "framework", "council", "principles"]) {
            expect(showcasePage).toContain(`id="${anchor}"`);
        }

        expect(showcasePage).toContain('href="/docs"');
        expect(showcasePage).toContain('href="/"');
    });

    it("notes page exports noindex metadata", async () => {
        const notesPageModule = await import("../app/notes/page");
        const metadata = notesPageModule.metadata as {
            robots?: { index?: boolean; follow?: boolean };
        };
        expect(metadata.robots).toEqual({ index: false, follow: false });
    });
});
