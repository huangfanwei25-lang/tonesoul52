import AboutLayout from "@/components/AboutLayout";
import type { ReactNode } from "react";
import type { Metadata } from "next";

export const metadata: Metadata = {
    title: "About | ToneSoul - AI Governance Research",
    description:
        "黃梵威的研究空間 — AI 倫理、感知力、提示工程與語魂系統。",
};

export default function Layout({ children }: { children: ReactNode }) {
    return <AboutLayout>{children}</AboutLayout>;
}
