import type { MetadataRoute } from "next";

import { isVercelProduction, resolveSiteUrl } from "@/lib/siteUrl";

export default function sitemap(): MetadataRoute.Sitemap {
    const siteUrl = resolveSiteUrl();
    const lastModified = new Date();

    // Keep this explicit for now; we only expose two public pages.
    // Add more routes here when they become stable public entry points.
    const entries: MetadataRoute.Sitemap = [
        {
            url: siteUrl,
            lastModified,
            changeFrequency: "weekly",
            priority: 1,
        },
        {
            url: `${siteUrl}/showcase`,
            lastModified,
            changeFrequency: "monthly",
            priority: 0.7,
        },
        {
            url: `${siteUrl}/docs`,
            lastModified,
            changeFrequency: "monthly",
            priority: 0.8,
        },
        // Personal Pages
        {
            url: `${siteUrl}/about`,
            lastModified,
            changeFrequency: "weekly",
            priority: 0.9,
        },
        {
            url: `${siteUrl}/about/ai-ethics`,
            lastModified,
            changeFrequency: "monthly",
            priority: 0.8,
        },
        {
            url: `${siteUrl}/about/sentience`,
            lastModified,
            changeFrequency: "monthly",
            priority: 0.8,
        },
        {
            url: `${siteUrl}/about/prompt-engineering`,
            lastModified,
            changeFrequency: "monthly",
            priority: 0.8,
        },
    ];

    // In non-production environments, we still return a sitemap for tooling,
    // but robots.txt blocks indexing, so it won't be crawled by default.
    if (!isVercelProduction()) {
        return entries;
    }

    return entries;
}
