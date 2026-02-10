const DEFAULT_SITE_URL = "https://tonesoul52.vercel.app";

function stripTrailingSlash(value: string): string {
    return value.replace(/\/+$/, "");
}

export function resolveSiteUrl(): string {
    const explicit = process.env.NEXT_PUBLIC_SITE_URL;
    if (typeof explicit === "string" && explicit.trim()) {
        return stripTrailingSlash(explicit.trim());
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

