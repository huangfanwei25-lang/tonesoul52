import { describe, expect, it } from "vitest";

import { decryptJson, deriveAesGcmKey, encryptJson } from "@/lib/privateNotesCrypto";

describe("privateNotesCrypto", () => {
    it("roundtrips JSON values", async () => {
        const saltBase64 = "AAAAAAAAAAAAAAAAAAAAAA=="; // 16 zero bytes
        const key = await deriveAesGcmKey({
            passphrase: "correct horse battery staple",
            saltBase64,
            iterations: 1_000,
        });

        const value = {
            marker: "ToneSoul",
            n: 123,
            ok: true,
            nested: { a: [1, 2, 3], b: null as null },
        };

        const encrypted = await encryptJson(key, value);
        expect(encrypted.iv).toBeTypeOf("string");
        expect(encrypted.ct).toBeTypeOf("string");

        const decrypted = await decryptJson<typeof value>(key, encrypted);
        expect(decrypted).toEqual(value);
    });

    it("fails to decrypt with a wrong passphrase", async () => {
        const saltBase64 = "AAAAAAAAAAAAAAAAAAAAAA==";
        const good = await deriveAesGcmKey({ passphrase: "password-one", saltBase64, iterations: 1_000 });
        const bad = await deriveAesGcmKey({ passphrase: "password-two", saltBase64, iterations: 1_000 });

        const encrypted = await encryptJson(good, { secret: "data" });
        await expect(decryptJson(bad, encrypted)).rejects.toBeTruthy();
    });
});

