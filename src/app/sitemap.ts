import type { MetadataRoute } from "next";
import { siteConfig } from "@/config";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = siteConfig.url;
  const now = new Date();
  return [
    { url: base, lastModified: now, changeFrequency: "weekly", priority: 1 },
    { url: `${base}/#courses`, lastModified: now, changeFrequency: "weekly", priority: 0.9 },
    { url: `${base}/#store`, lastModified: now, changeFrequency: "monthly", priority: 0.7 },
    { url: `${base}/#why`, lastModified: now, changeFrequency: "monthly", priority: 0.6 },
    { url: `${base}/#telegram`, lastModified: now, changeFrequency: "monthly", priority: 0.5 },
    { url: `${base}/#faq`, lastModified: now, changeFrequency: "monthly", priority: 0.6 },
  ];
}
