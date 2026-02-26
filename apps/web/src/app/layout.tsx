import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { resolveSiteUrl } from "@/lib/siteUrl";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const siteUrl = resolveSiteUrl();
// 強制開啟索引，以便 Google 可以爬取（如果需要針對特定環境，可以加回 VERCEL_ENV 判斷）
const allowIndexing = true;

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: "ToneSoul Integrity Framework | AI Governance Middleware",
  description: "ToneSoul is a governance middleware for auditable, self-correcting AI agents. Implements STREI vector analysis, entropy-based tension metrics, and cryptographic responsibility ledger.",
  keywords: ["ToneSoul", "AI Governance", "MGGI", "STREI Vector", "AI Audit", "LLM Safety"],
  authors: [{ name: "ToneSoul Team" }],
  robots: {
    index: allowIndexing,
    follow: allowIndexing,
  },
  openGraph: {
    title: "ToneSoul Integrity Framework",
    description: "Enterprise-grade architecture for auditable, governable AI agents.",
    type: "website",
    url: siteUrl,
    siteName: "ToneSoul",
  },
  verification: {
    // 這裡替換成你的 Google Search Console 驗證碼
    google: "填入你的_google_site_verification_碼",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
