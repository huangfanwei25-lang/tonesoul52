const DEFAULT_SITE_URL = "https://tonesoul52.vercel.app";

export const PUBLIC_CURRENT_URL =
    "https://huangfanwei25-lang.github.io/tonesoul52/current/";
export const CANONICAL_REPOSITORY_URL =
    "https://github.com/huangfanwei25-lang/tonesoul52";

function stripTrailingSlash(value: string): string {
    return value.replace(/\/+$/, "");
}

export function resolveSiteUrl(): string {
    const explicit = process.env.NEXT_PUBLIC_SITE_URL;
    if (typeof explicit === "string" && explicit.trim()) {
        return stripTrailingSlash(explicit.trim());
    }

    // In production, prefer the stable public domain over per-deployment URLs
    // so canonical/robots/sitemap always point to a single indexable origin.
    if (process.env.VERCEL_ENV === "production") {
        return DEFAULT_SITE_URL;
    }

    const vercelUrl = process.env.VERCEL_URL;
    if (typeof vercelUrl === "string" && vercelUrl.trim()) {
        return `https://${stripTrailingSlash(vercelUrl.trim())}`;
    }

    return DEFAULT_SITE_URL;
}

export function isVercelProduction(): boolean {
    return process.env.VERCEL_ENV === "production";
}
