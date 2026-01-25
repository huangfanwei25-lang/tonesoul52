import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "ToneSoul Integrity Framework | AI Governance Middleware",
  description: "ToneSoul is a governance middleware for auditable, self-correcting AI agents. Implements STREI vector analysis, entropy-based tension metrics, and cryptographic responsibility ledger.",
  keywords: ["ToneSoul", "AI Governance", "MGGI", "STREI Vector", "AI Audit", "LLM Safety"],
  authors: [{ name: "ToneSoul Team" }],
  openGraph: {
    title: "ToneSoul Integrity Framework",
    description: "Enterprise-grade architecture for auditable, governable AI agents.",
    type: "website",
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
