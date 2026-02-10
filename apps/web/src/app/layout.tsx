import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { isVercelProduction, resolveSiteUrl } from "@/lib/siteUrl";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const siteUrl = resolveSiteUrl();
const allowIndexing = isVercelProduction();

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  alternates: {
    canonical: "/",
  },
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
