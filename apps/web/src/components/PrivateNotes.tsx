"use client";

import { useEffect, useMemo, useState } from "react";
import { Lock, Unlock, Download, Upload, Trash2, FileText } from "lucide-react";

import type { EncryptedPayload } from "@/lib/privateNotesCrypto";
import { decryptJson, deriveAesGcmKey, encryptJson, randomBytesBase64 } from "@/lib/privateNotesCrypto";

type Note = {
    id: string;
    createdAt: number;
    text: string;
};

type NotesStoreV1 = {
    version: 1;
    kdf: {
        name: "PBKDF2";
        hash: "SHA-256";
        iterations: number;
        saltBase64: string;
    };
    verifier: EncryptedPayload;
    notes: EncryptedPayload;
    updatedAt: string;
};

const STORAGE_KEY = "tonesoul.private_notes.v1";
const DEFAULT_ITERATIONS = 200_000;
const VERIFIER_MARKER = { marker: "ToneSoulPrivateNotes", version: 1 };

function nowIso(): string {
    return new Date().toISOString();
}

function safeParseStore(raw: string | null): NotesStoreV1 | null {
    if (!raw) return null;
    try {
        const parsed = JSON.parse(raw) as Partial<NotesStoreV1>;
        if (parsed.version !== 1) return null;
        if (!parsed.kdf?.saltBase64 || !parsed.kdf?.iterations) return null;
        if (!parsed.verifier?.iv || !parsed.verifier?.ct) return null;
        if (!parsed.notes?.iv || !parsed.notes?.ct) return null;
        return parsed as NotesStoreV1;
    } catch {
        return null;
    }
}

function downloadText(filename: string, text: string) {
    const blob = new Blob([text], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function formatDate(ts: number): string {
    const date = new Date(ts);
    return date.toLocaleString("zh-TW", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
    });
}

export default function PrivateNotes() {
    const [isMounted, setIsMounted] = useState(false);
    const [store, setStore] = useState<NotesStoreV1 | null>(null);
    const [key, setKey] = useState<CryptoKey | null>(null);
    const [notes, setNotes] = useState<Note[]>([]);

    const [passphrase, setPassphrase] = useState("");
    const [passphrase2, setPassphrase2] = useState("");
    const [noteText, setNoteText] = useState("");
    const [busy, setBusy] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        setIsMounted(true);
        const loaded = safeParseStore(window.localStorage.getItem(STORAGE_KEY));
        setStore(loaded);
    }, []);

    const isUnlocked = useMemo(() => Boolean(store && key), [store, key]);
    const isSetupMode = useMemo(() => isMounted && !store, [isMounted, store]);

    async function persist(next: NotesStoreV1) {
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
        setStore(next);
    }

    async function handleSetup() {
        setError(null);
        const p1 = passphrase.trim();
        const p2 = passphrase2.trim();

        if (p1.length < 8) {
            setError("密碼至少 8 個字元。");
            return;
        }
        if (p1 !== p2) {
            setError("兩次輸入的密碼不一致。");
            return;
        }

        setBusy("setup");
        try {
            const saltBase64 = randomBytesBase64(16);
            const kdf = { name: "PBKDF2" as const, hash: "SHA-256" as const, iterations: DEFAULT_ITERATIONS, saltBase64 };
            const derived = await deriveAesGcmKey({ passphrase: p1, saltBase64, iterations: kdf.iterations });

            const verifier = await encryptJson(derived, VERIFIER_MARKER);
            const initialNotes = await encryptJson(derived, [] as Note[]);

            const next: NotesStoreV1 = {
                version: 1,
                kdf,
                verifier,
                notes: initialNotes,
                updatedAt: nowIso(),
            };

            await persist(next);
            setKey(derived);
            setNotes([]);
            setPassphrase("");
            setPassphrase2("");
        } catch (e) {
            console.error("Notes setup failed:", e);
            setError("初始化失敗，請稍後再試。");
        } finally {
            setBusy(null);
        }
    }

    async function handleUnlock() {
        if (!store) return;
        setError(null);
        const p = passphrase.trim();
        if (!p) {
            setError("請輸入密碼。");
            return;
        }

        setBusy("unlock");
        try {
            const derived = await deriveAesGcmKey({
                passphrase: p,
                saltBase64: store.kdf.saltBase64,
                iterations: store.kdf.iterations,
            });

            const verifier = await decryptJson<typeof VERIFIER_MARKER>(derived, store.verifier);
            if (verifier?.marker !== VERIFIER_MARKER.marker || verifier?.version !== VERIFIER_MARKER.version) {
                throw new Error("verifier_mismatch");
            }

            const decryptedNotes = await decryptJson<Note[]>(derived, store.notes);
            setKey(derived);
            setNotes(Array.isArray(decryptedNotes) ? decryptedNotes : []);
            setPassphrase("");
        } catch (e) {
            console.error("Notes unlock failed:", e);
            setError("密碼錯誤，或資料已損毀。");
            setKey(null);
            setNotes([]);
        } finally {
            setBusy(null);
        }
    }

    async function handleLock() {
        setKey(null);
        setNotes([]);
        setNoteText("");
        setError(null);
    }

    async function handleAddNote() {
        if (!store || !key) return;
        setError(null);

        const text = noteText.trim();
        if (!text) return;

        setBusy("save");
        try {
            const nextNotes: Note[] = [
                { id: `note_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`, createdAt: Date.now(), text },
                ...notes,
            ];

            const encrypted = await encryptJson(key, nextNotes);
            const nextStore: NotesStoreV1 = {
                ...store,
                notes: encrypted,
                updatedAt: nowIso(),
            };

            await persist(nextStore);
            setNotes(nextNotes);
            setNoteText("");
        } catch (e) {
            console.error("Notes save failed:", e);
            setError("保存失敗，請稍後再試。");
        } finally {
            setBusy(null);
        }
    }

    async function handleDeleteNote(id: string) {
        if (!store || !key) return;
        setError(null);
        if (!confirm("確定要刪除這則筆記嗎？此操作無法復原。")) return;

        setBusy("delete");
        try {
            const nextNotes = notes.filter((n) => n.id !== id);
            const encrypted = await encryptJson(key, nextNotes);
            const nextStore: NotesStoreV1 = {
                ...store,
                notes: encrypted,
                updatedAt: nowIso(),
            };

            await persist(nextStore);
            setNotes(nextNotes);
        } catch (e) {
            console.error("Notes delete failed:", e);
            setError("刪除失敗，請稍後再試。");
        } finally {
            setBusy(null);
        }
    }

    async function handleExport() {
        setError(null);
        const raw = window.localStorage.getItem(STORAGE_KEY);
        if (!raw) {
            setError("目前沒有可匯出的筆記。");
            return;
        }

        const date = new Date().toISOString().slice(0, 10);
        downloadText(`tonesoul_notes_backup_${date}.json`, raw);
    }

    async function handleImport(file: File) {
        setError(null);
        setBusy("import");
        try {
            const text = await file.text();
            const parsed = safeParseStore(text);
            if (!parsed) {
                setError("匯入檔案格式不正確。");
                return;
            }

            window.localStorage.setItem(STORAGE_KEY, JSON.stringify(parsed));
            setStore(parsed);
            setKey(null);
            setNotes([]);
            setNoteText("");
            setPassphrase("");
            setPassphrase2("");
        } catch (e) {
            console.error("Notes import failed:", e);
            setError("匯入失敗，請確認檔案未損毀。");
        } finally {
            setBusy(null);
        }
    }

    async function handleReset() {
        if (!confirm("確定要重置 Private Notes 嗎？這會刪除本機所有加密筆記。")) return;
        window.localStorage.removeItem(STORAGE_KEY);
        setStore(null);
        setKey(null);
        setNotes([]);
        setNoteText("");
        setPassphrase("");
        setPassphrase2("");
        setError(null);
    }

    if (!isMounted) {
        return (
            <div className="rounded-2xl border border-slate-700/45 bg-slate-900/25 p-6 text-slate-300">
                Loading...
            </div>
        );
    }

    return (
        <section className="rounded-2xl border border-slate-700/45 bg-slate-900/25 p-6">
            <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                    <FileText className="w-5 h-5 text-sky-300" />
                    <h2 className="font-bold text-lg">Private Notes</h2>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                    {isUnlocked ? (
                        <button type="button"
                            onClick={handleLock}
                            className="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-700/60 bg-slate-900/30 hover:bg-slate-900/45 transition-colors text-sm"
                        >
                            <Lock className="w-4 h-4 text-slate-300" />
                            Lock
                        </button>
                    ) : null}

                    <button type="button"
                        onClick={handleExport}
                        className="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-700/60 bg-slate-900/30 hover:bg-slate-900/45 transition-colors text-sm"
                    >
                        <Download className="w-4 h-4 text-slate-300" />
                        Export
                    </button>

                    <label className="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-700/60 bg-slate-900/30 hover:bg-slate-900/45 transition-colors text-sm cursor-pointer">
                        <Upload className="w-4 h-4 text-slate-300" />
                        Import
                        <input
                            type="file"
                            accept="application/json"
                            className="hidden"
                            onChange={(e) => {
                                const file = e.target.files?.[0];
                                if (file) void handleImport(file);
                                e.currentTarget.value = "";
                            }}
                        />
                    </label>

                    <button type="button"
                        onClick={handleReset}
                        className="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-rose-400/25 bg-rose-500/10 hover:bg-rose-500/15 transition-colors text-sm text-rose-100"
                        title="刪除本機所有筆記"
                    >
                        <Trash2 className="w-4 h-4" />
                        Reset
                    </button>
                </div>
            </div>

            <p className="mt-3 text-sm text-slate-400 leading-relaxed">
                筆記只存放在你的瀏覽器 localStorage，並以你的密碼透過 AES-GCM 加密。
                <span className="text-slate-500">（忘記密碼無法復原，只能 Reset）</span>
            </p>

            {error ? (
                <div className="mt-4 rounded-xl border border-rose-400/25 bg-rose-500/10 p-3 text-sm text-rose-100">
                    {error}
                </div>
            ) : null}

            {isSetupMode ? (
                <div className="mt-6 grid gap-3 max-w-md">
                    <div className="flex items-center gap-2 text-slate-200 font-semibold">
                        <Unlock className="w-4 h-4 text-sky-300" />
                        先設定一組密碼
                    </div>
                    <input
                        type="password"
                        placeholder="輸入密碼（至少 8 字）"
                        className="w-full px-3 py-2 rounded-lg bg-slate-950/40 border border-slate-700/60 text-slate-100 placeholder:text-slate-600"
                        value={passphrase}
                        onChange={(e) => setPassphrase(e.target.value)}
                        disabled={busy !== null}
                    />
                    <input
                        type="password"
                        placeholder="再次輸入密碼"
                        className="w-full px-3 py-2 rounded-lg bg-slate-950/40 border border-slate-700/60 text-slate-100 placeholder:text-slate-600"
                        value={passphrase2}
                        onChange={(e) => setPassphrase2(e.target.value)}
                        disabled={busy !== null}
                    />
                    <button type="button"
                        onClick={() => void handleSetup()}
                        disabled={busy !== null}
                        className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-sky-500/15 border border-sky-400/30 hover:bg-sky-500/20 transition-colors text-sm disabled:opacity-50"
                    >
                        <Unlock className="w-4 h-4 text-sky-200" />
                        Create
                    </button>
                </div>
            ) : null}

            {!isSetupMode && !isUnlocked ? (
                <div className="mt-6 grid gap-3 max-w-md">
                    <div className="flex items-center gap-2 text-slate-200 font-semibold">
                        <Lock className="w-4 h-4 text-sky-300" />
                        請輸入密碼解鎖
                    </div>
                    <input
                        type="password"
                        placeholder="密碼"
                        className="w-full px-3 py-2 rounded-lg bg-slate-950/40 border border-slate-700/60 text-slate-100 placeholder:text-slate-600"
                        value={passphrase}
                        onChange={(e) => setPassphrase(e.target.value)}
                        disabled={busy !== null}
                        onKeyDown={(e) => {
                            if (e.key === "Enter") void handleUnlock();
                        }}
                    />
                    <button type="button"
                        onClick={() => void handleUnlock()}
                        disabled={busy !== null}
                        className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-sky-500/15 border border-sky-400/30 hover:bg-sky-500/20 transition-colors text-sm disabled:opacity-50"
                    >
                        <Unlock className="w-4 h-4 text-sky-200" />
                        Unlock
                    </button>
                </div>
            ) : null}

            {isUnlocked ? (
                <div className="mt-6 grid gap-4">
                    <div className="grid gap-2">
                        <textarea
                            value={noteText}
                            onChange={(e) => setNoteText(e.target.value)}
                            placeholder="寫下你的筆記..."
                            rows={4}
                            className="w-full px-3 py-2 rounded-lg bg-slate-950/35 border border-slate-700/60 text-slate-100 placeholder:text-slate-600 resize-y"
                            disabled={busy !== null}
                        />
                        <div className="flex items-center justify-between gap-3">
                            <div className="text-xs text-slate-500">
                                {store ? `Updated: ${store.updatedAt}` : null}
                            </div>
                            <button type="button"
                                onClick={() => void handleAddNote()}
                                disabled={busy !== null || !noteText.trim()}
                                className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-sky-500/15 border border-sky-400/30 hover:bg-sky-500/20 transition-colors text-sm disabled:opacity-50"
                            >
                                Save
                            </button>
                        </div>
                    </div>

                    <div className="grid gap-3">
                        {notes.length === 0 ? (
                            <div className="rounded-xl border border-slate-700/45 bg-slate-900/25 p-4 text-sm text-slate-400">
                                目前沒有筆記。
                            </div>
                        ) : (
                            notes.map((n) => (
                                <div
                                    key={n.id}
                                    className="rounded-xl border border-slate-700/45 bg-slate-900/25 p-4"
                                >
                                    <div className="flex items-start justify-between gap-3">
                                        <div className="text-xs text-slate-500">{formatDate(n.createdAt)}</div>
                                        <button type="button"
                                            onClick={() => void handleDeleteNote(n.id)}
                                            disabled={busy !== null}
                                            className="inline-flex items-center gap-2 text-xs text-rose-200 hover:text-rose-100 disabled:opacity-50"
                                            title="刪除"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                            Delete
                                        </button>
                                    </div>
                                    <p className="mt-2 whitespace-pre-wrap text-sm text-slate-200 leading-relaxed">
                                        {n.text}
                                    </p>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            ) : null}

            {busy ? (
                <div className="mt-4 text-xs text-slate-500">
                    Working... ({busy})
                </div>
            ) : null}
        </section>
    );
}


