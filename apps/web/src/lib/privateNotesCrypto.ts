type JsonValue = null | boolean | number | string | JsonValue[] | { [key: string]: JsonValue };

export type EncryptedPayload = {
    iv: string; // base64
    ct: string; // base64
};

const encoder = new TextEncoder();
const decoder = new TextDecoder();

function bytesToBase64(bytes: Uint8Array): string {
    // Node.js (tests) and some bundlers provide Buffer; browsers may not.
    if (typeof Buffer !== "undefined") {
        return Buffer.from(bytes).toString("base64");
    }

    let binary = "";
    for (const b of bytes) {
        binary += String.fromCharCode(b);
    }
    return btoa(binary);
}

function base64ToBytes(base64: string): Uint8Array<ArrayBuffer> {
    if (typeof Buffer !== "undefined") {
        // `crypto.subtle` types in TS expect an `ArrayBuffer`-backed view, not `ArrayBufferLike`.
        // Copy into a fresh `Uint8Array<ArrayBuffer>` to satisfy `BufferSource` typing.
        const buf = Buffer.from(base64, "base64");
        const out = new Uint8Array(buf.length);
        out.set(buf);
        return out;
    }

    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
    }
    return bytes;
}

export function randomBytesBase64(length: number): string {
    const bytes = new Uint8Array(length);
    crypto.getRandomValues(bytes);
    return bytesToBase64(bytes);
}

export async function deriveAesGcmKey(params: {
    passphrase: string;
    saltBase64: string;
    iterations: number;
}): Promise<CryptoKey> {
    const passphrase = params.passphrase.normalize("NFKC");
    const material = await crypto.subtle.importKey(
        "raw",
        encoder.encode(passphrase),
        "PBKDF2",
        false,
        ["deriveKey"]
    );

    const salt = base64ToBytes(params.saltBase64);
    return crypto.subtle.deriveKey(
        { name: "PBKDF2", salt, iterations: params.iterations, hash: "SHA-256" },
        material,
        { name: "AES-GCM", length: 256 },
        false,
        ["encrypt", "decrypt"]
    );
}

export async function encryptJson(key: CryptoKey, value: JsonValue): Promise<EncryptedPayload> {
    const ivBytes = new Uint8Array(12);
    crypto.getRandomValues(ivBytes);

    const plaintext = encoder.encode(JSON.stringify(value));
    const ciphertext = await crypto.subtle.encrypt({ name: "AES-GCM", iv: ivBytes }, key, plaintext);

    return {
        iv: bytesToBase64(ivBytes),
        ct: bytesToBase64(new Uint8Array(ciphertext)),
    };
}

export async function decryptJson<T>(key: CryptoKey, payload: EncryptedPayload): Promise<T> {
    const ivBytes = base64ToBytes(payload.iv);
    const ciphertextBytes = base64ToBytes(payload.ct);

    const plaintext = await crypto.subtle.decrypt(
        { name: "AES-GCM", iv: ivBytes },
        key,
        ciphertextBytes
    );
    const text = decoder.decode(new Uint8Array(plaintext));
    return JSON.parse(text) as T;
}
