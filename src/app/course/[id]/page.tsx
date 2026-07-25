import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import {
  ArrowLeft,
  BadgeCheck,
  BookOpen,
  Check,
  Download,
  Globe2,
  GraduationCap,
  Layers,
  ListChecks,
  MessageCircle,
  ShieldCheck,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Navbar } from "@/components/sections/Navbar";
import { Footer } from "@/components/sections/Footer";
import { CourseBuy } from "@/components/sections/CourseBuy";
import { I18nProvider } from "@/components/providers/I18nProvider";
import { SiteConfigProvider } from "@/components/providers/SiteConfigProvider";
import { categories, getProduct, products, recommendationsFor, type Product } from "@/catalog";
import { siteConfig, links } from "@/config";
import { getEffectiveConfig } from "@/lib/site-settings";
import { getCurrentLocale } from "@/lib/locale";
import { getDictionary } from "@/i18n/dictionaries";
import { dirFor } from "@/i18n/config";
import { isLemonConfigured } from "@/lib/lemonsqueezy";
import { discountPercent, formatUSD } from "@/lib/utils";

/** One indexable, shareable page per product — the SEO surface of the store. */
export function generateStaticParams() {
  return products.map((p) => ({ id: p.id }));
}

const LANG_LABEL: Record<string, string> = { en: "English", ar: "العربية", tr: "Türkçe" };
const languagesOf = (p: Product) => Object.keys(p.files).map((l) => LANG_LABEL[l] ?? l);

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;
  const p = getProduct(id);
  if (!p) return { title: "Course not found" };
  const title = `${p.title} — ${p.subtitle}`;
  const path = `/course/${p.id}`;
  return {
    title,
    description: p.description,
    keywords: [p.title, ...(p.tags ?? []), "E-tqan", "premium course"],
    alternates: { canonical: path },
    openGraph: {
      type: "article",
      title: `${title} | ${siteConfig.name}`,
      description: p.description,
      url: `${siteConfig.url}${path}`,
      siteName: siteConfig.name,
    },
    twitter: { card: "summary_large_image", title, description: p.description },
  };
}

export default async function CoursePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const p = getProduct(id);
  if (!p) notFound();

  const [eff, locale] = await Promise.all([getEffectiveConfig(), getCurrentLocale()]);
  const dict = getDictionary(locale);
  const category = categories.find((c) => c.id === p.category);
  const included = (p.includes ?? []).map((i) => getProduct(i)).filter(Boolean) as Product[];
  const related = recommendationsFor(p.id, 3);
  const saving = discountPercent(p.originalPrice, p.offerPrice);
  const accent: "gold" | "emerald" = p.accent === "emerald" ? "emerald" : "gold";

  const jsonLd = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Course",
        name: p.title,
        description: p.description,
        url: `${siteConfig.url}/course/${p.id}`,
        inLanguage: Object.keys(p.files),
        educationalLevel: p.level,
        provider: { "@type": "Organization", name: siteConfig.name, url: siteConfig.url },
        offers: {
          "@type": "Offer",
          price: p.offerPrice.toFixed(2),
          priceCurrency: "USD",
          availability: "https://schema.org/InStock",
          url: `${siteConfig.url}/course/${p.id}`,
        },
        hasCourseInstance: {
          "@type": "CourseInstance",
          courseMode: "online",
          courseWorkload: "PT10H",
        },
      },
      {
        "@type": "BreadcrumbList",
        itemListElement: [
          { "@type": "ListItem", position: 1, name: "Home", item: siteConfig.url },
          { "@type": "ListItem", position: 2, name: category?.label ?? "Courses", item: `${siteConfig.url}/#courses` },
          { "@type": "ListItem", position: 3, name: p.title, item: `${siteConfig.url}/course/${p.id}` },
        ],
      },
    ],
  };

  return (
    <I18nProvider value={{ t: dict, locale, dir: dirFor(locale) }}>
      <SiteConfigProvider
        value={{
          books: eff.books,
          offerEndsAt: eff.offerEndsAt,
          telegramUrl: eff.telegramUrl,
          paymentUrl: eff.paymentUrl,
        }}
      >
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
        <Navbar />

        <main className="mx-auto max-w-6xl px-6 pb-24 pt-28 sm:pt-32">
          {/* breadcrumb */}
          <nav aria-label="Breadcrumb" className="mb-8 flex items-center gap-2 text-[13px] text-soft/50">
            <Link href="/" className="transition-colors hover:text-gold-light">
              Home
            </Link>
            <span aria-hidden>/</span>
            <Link href="/#courses" className="transition-colors hover:text-gold-light">
              {category?.label ?? "Courses"}
            </Link>
            <span aria-hidden>/</span>
            <span className="text-soft/80">{p.title}</span>
          </nav>

          <div className="grid gap-10 lg:grid-cols-[1.6fr_1fr]">
            {/* ── main column ── */}
            <div>
              <div className="flex flex-wrap items-center gap-2">
                {p.badge && <Badge variant="gold">{p.badge}</Badge>}
                <Badge variant="muted">{p.level}</Badge>
                {p.type === "bundle" && <Badge variant="emerald">{included.length} courses</Badge>}
              </div>

              <h1 className="mt-4 font-display text-4xl font-semibold tracking-tight text-soft sm:text-5xl">
                {p.title}
              </h1>
              <p className="mt-3 text-xl text-gold-light">{p.subtitle}</p>
              <p className="mt-6 max-w-2xl text-base leading-relaxed text-soft/65">{p.description}</p>

              <div className="mt-6 flex flex-wrap items-center gap-x-6 gap-y-3 text-[13px] text-soft/55">
                <span className="inline-flex items-center gap-2">
                  <Globe2 className="h-4 w-4 text-gold-light" />
                  {languagesOf(p).join(" · ")}
                </span>
                <span className="inline-flex items-center gap-2">
                  <Download className="h-4 w-4 text-gold-light" />
                  Instant PDF download
                </span>
                <span className="inline-flex items-center gap-2">
                  <ShieldCheck className="h-4 w-4 text-gold-light" />
                  Encrypted, private delivery
                </span>
              </div>

              {/* what you'll learn */}
              <section className="mt-12">
                <h2 className="flex items-center gap-2 font-display text-2xl font-semibold text-soft">
                  <ListChecks className="h-5 w-5 text-gold-light" /> What you&apos;ll learn
                </h2>
                <ul className="mt-5 grid gap-3 sm:grid-cols-2">
                  {p.highlights.map((h) => (
                    <li
                      key={h}
                      className="flex items-start gap-2.5 rounded-xl border border-white/10 bg-white/[0.03] p-4 text-sm leading-relaxed text-soft/75"
                    >
                      <Check className="mt-0.5 h-4 w-4 shrink-0 text-emerald-light" />
                      {h}
                    </li>
                  ))}
                </ul>
              </section>

              {/* what's inside every book */}
              <section className="mt-12">
                <h2 className="flex items-center gap-2 font-display text-2xl font-semibold text-soft">
                  <BookOpen className="h-5 w-5 text-gold-light" /> Inside every E-tqan book
                </h2>
                <ul className="mt-5 grid gap-x-6 gap-y-2.5 sm:grid-cols-2">
                  {[
                    "Premium cover and typeset layout",
                    "Clickable table of contents + PDF bookmarks",
                    "Diagrams, flowcharts and comparison tables",
                    "Modern, syntax-highlighted code examples",
                    "Exercises and quizzes with answer keys",
                    "Mini projects and professional projects",
                    "Real-world case studies",
                    "Printable cheat sheet",
                    "Full glossary of terms",
                    "Staged learning roadmap",
                    "References and further reading",
                    "Lifetime access to the files you buy",
                  ].map((f) => (
                    <li key={f} className="flex items-start gap-2 text-[14px] text-soft/70">
                      <BadgeCheck className="mt-0.5 h-4 w-4 shrink-0 text-gold-light" />
                      {f}
                    </li>
                  ))}
                </ul>
              </section>

              {/* bundle contents */}
              {included.length > 0 && (
                <section className="mt-12">
                  <h2 className="flex items-center gap-2 font-display text-2xl font-semibold text-soft">
                    <Layers className="h-5 w-5 text-gold-light" /> What&apos;s included
                  </h2>
                  <div className="mt-5 grid gap-3 sm:grid-cols-2">
                    {included.map((c) => (
                      <Link
                        key={c.id}
                        href={`/course/${c.id}`}
                        className="group rounded-xl border border-white/10 bg-white/[0.03] p-4 transition-colors hover:border-gold/40"
                      >
                        <div className="flex items-center justify-between gap-3">
                          <span className="font-display text-base font-semibold text-soft">{c.title}</span>
                          <span className="font-mono text-xs text-soft/40 line-through">
                            {formatUSD(c.originalPrice)}
                          </span>
                        </div>
                        <p className="mt-1 text-[13px] text-soft/55 group-hover:text-soft/70">{c.subtitle}</p>
                      </Link>
                    ))}
                  </div>
                </section>
              )}

              {/* related */}
              {related.length > 0 && (
                <section className="mt-12">
                  <h2 className="flex items-center gap-2 font-display text-2xl font-semibold text-soft">
                    <GraduationCap className="h-5 w-5 text-gold-light" /> Learners also take
                  </h2>
                  <div className="mt-5 grid gap-3 sm:grid-cols-3">
                    {related.map((r) => (
                      <Link
                        key={r.id}
                        href={`/course/${r.id}`}
                        className="rounded-xl border border-white/10 bg-white/[0.03] p-4 transition-colors hover:border-gold/40"
                      >
                        <span className="font-display text-base font-semibold text-soft">{r.title}</span>
                        <p className="mt-1 text-[13px] text-soft/55">{r.subtitle}</p>
                        <span className="mt-2 block font-mono text-sm text-gold-light">
                          {formatUSD(r.offerPrice)}
                        </span>
                      </Link>
                    ))}
                  </div>
                </section>
              )}
            </div>

            {/* ── sticky purchase panel ── */}
            <aside className="lg:sticky lg:top-28 lg:self-start">
              <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-6 backdrop-blur-xl">
                <div className="flex items-end gap-3">
                  <span className="font-display text-4xl font-semibold text-soft">
                    {formatUSD(p.offerPrice)}
                  </span>
                  {p.offerPrice < p.originalPrice && (
                    <>
                      <span className="mb-1 font-mono text-base text-soft/40 line-through">
                        {formatUSD(p.originalPrice)}
                      </span>
                      <Badge variant="emerald" className="mb-1">
                        -{saving}%
                      </Badge>
                    </>
                  )}
                </div>
                <p className="mt-1 text-[13px] text-soft/50">One-time payment · yours forever</p>

                <div className="mt-5">
                  <CourseBuy productId={p.id} accent={accent} cardEnabled={isLemonConfigured()} />
                </div>

                <ul className="mt-6 space-y-2 border-t border-white/10 pt-5 text-[13px] text-soft/60">
                  <li className="flex items-center gap-2">
                    <Check className="h-4 w-4 text-emerald-light" />
                    {languagesOf(p).length} language editions included
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="h-4 w-4 text-emerald-light" />
                    Download link emailed to you
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="h-4 w-4 text-emerald-light" />
                    Free updates to this edition
                  </li>
                </ul>

                <Button asChild variant="glass" size="md" className="mt-5 w-full">
                  <a href={links.telegramUrl} target="_blank" rel="noopener noreferrer">
                    <MessageCircle className="h-4 w-4" />
                    Ask a question first
                  </a>
                </Button>
              </div>

              <Link
                href="/#courses"
                className="mt-4 inline-flex items-center gap-2 text-[13px] text-soft/50 transition-colors hover:text-gold-light"
              >
                <ArrowLeft className="h-4 w-4" />
                Back to the full library
              </Link>
            </aside>
          </div>
        </main>

        <Footer />
      </SiteConfigProvider>
    </I18nProvider>
  );
}
