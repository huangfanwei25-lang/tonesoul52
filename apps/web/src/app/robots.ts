import type { MetadataRoute } from "next";

import { isVercelProduction, resolveSiteUrl } from "@/lib/siteUrl";

export default function robots(): MetadataRoute.Robots {
    // Prevent accidental indexing of preview deployments.
    if (!isVercelProduction()) {
        return {
            rules: [{ userAgent: "*", disallow: "/" }],
        };
    }

    const siteUrl = resolveSiteUrl();
    return {
        rules: [{ userAgent: "*", allow: "/", disallow: ["/api/", "/notes"] }],
        sitemap: `${siteUrl}/sitemap.xml`,
    };
}
