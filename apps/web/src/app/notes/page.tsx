import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

import PrivateNotes from "@/components/PrivateNotes";

export const metadata: Metadata = {
    title: "Private Notes | ToneSoul",
    robots: { index: false, follow: false },
};

export default function NotesPage() {
    return (
        <div className="min-h-screen bg-[#0a0e27] text-slate-100">
            {/* Background */}
            <div className="pointer-events-none fixed inset-0 -z-10">
                <div className="absolute inset-0 bg-[radial-gradient(1200px_circle_at_20%_10%,rgba(56,189,248,0.22),transparent_55%),radial-gradient(900px_circle_at_80%_30%,rgba(244,63,94,0.18),transparent_60%),radial-gradient(700px_circle_at_50%_90%,rgba(99,102,241,0.14),transparent_55%)]" />
                <div className="absolute inset-0 opacity-35 bg-[radial-gradient(rgba(148,163,184,0.12)_1px,transparent_1px)] [background-size:22px_22px]" />
                <div className="absolute inset-0 bg-gradient-to-b from-transparent via-black/10 to-black/35" />
            </div>

            <main className="max-w-3xl mx-auto px-5 py-10 space-y-6">
                <div className="flex items-center justify-between gap-4">
                    <Link
                        href="/"
                        className="inline-flex items-center gap-2 text-sm text-slate-300 hover:text-white transition-colors"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        Back to App
                    </Link>
                    <Link
                        href="/docs"
                        className="text-sm text-slate-300 hover:text-white transition-colors"
                    >
                        Docs
                    </Link>
                </div>

                <PrivateNotes />
            </main>
        </div>
    );
}
