"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode } from "react";

const NAV_ITEMS = [
    { href: "/about", label: "關於", icon: "👤" },
    { href: "/about/ai-ethics", label: "AI 倫理", icon: "⚖️" },
    { href: "/about/sentience", label: "感知力", icon: "🧠" },
    { href: "/about/prompt-engineering", label: "提示工程", icon: "⚡" },
];

export default function AboutLayout({ children }: { children: ReactNode }) {
    const pathname = usePathname();

    return (
        <div className="min-h-screen bg-[#0a0b14] text-gray-100">
            {/* Header */}
            <header className="sticky top-0 z-50 border-b border-white/5 bg-[#0a0b14]/80 backdrop-blur-xl">
                <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
                    <Link
                        href="/"
                        className="flex items-center gap-2 text-sm text-gray-400 transition-colors hover:text-white"
                    >
                        <span className="text-lg">🌌</span>
                        <span className="font-mono">ToneSoul</span>
                    </Link>

                    <nav className="flex items-center gap-1">
                        {NAV_ITEMS.map((item) => {
                            const isActive =
                                pathname === item.href ||
                                (item.href !== "/about" && pathname?.startsWith(item.href));
                            return (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    className={`rounded-lg px-3 py-2 text-sm transition-all duration-200 ${isActive
                                            ? "bg-white/10 text-white"
                                            : "text-gray-400 hover:bg-white/5 hover:text-gray-200"
                                        }`}
                                >
                                    <span className="mr-1.5">{item.icon}</span>
                                    {item.label}
                                </Link>
                            );
                        })}
                    </nav>
                </div>
            </header>

            {/* Main */}
            <main className="mx-auto max-w-4xl px-6 py-12">{children}</main>

            {/* Footer */}
            <footer className="border-t border-white/5 py-8 text-center text-xs text-gray-500">
                <p>
                    © 2025–2026 黃梵威 (Fan-Wei Huang) · Built with{" "}
                    <Link href="/" className="text-indigo-400 hover:text-indigo-300">
                        ToneSoul
                    </Link>
                </p>
            </footer>
        </div>
    );
}
