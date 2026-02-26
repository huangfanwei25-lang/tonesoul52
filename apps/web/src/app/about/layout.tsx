import AboutLayout from "@/components/AboutLayout";
import type { ReactNode } from "react";
import type { Metadata } from "next";

export const metadata: Metadata = {
    title: "About | 黃梵威 Fan-Wei Huang - ToneSoul AI",
    description: "黃梵威 (Fan-Wei Huang) 的研究空間 — 專注於 AI 倫理、感知力、提示工程與語魂系統治理架構。",
    keywords: ["黃梵威", "Fan-Wei Huang", "ToneSoul", "AI 倫理", "AI Governance", "Prompt Engineering"],
    robots: {
        index: true,
        follow: true,
    },
    openGraph: {
        title: "About | 黃梵威 Fan-Wei Huang",
        description: "獨立研究者，探索 AI 治理、感知力與語魂系統。",
    }
};

export default function Layout({ children }: { children: ReactNode }) {
    return <AboutLayout>{children}</AboutLayout>;
}
