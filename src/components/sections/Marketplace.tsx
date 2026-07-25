"use client";

import * as React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Code, Sparkles, LayoutGrid, Table, Palette, Layers,
  Check, Loader2, ShoppingCart, Lock, Star, Search, Heart, X,
  type LucideIcon,
} from "lucide-react";
import { SectionHeading } from "@/components/ui/section-heading";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useOfferActive } from "@/hooks/useOfferActive";
import { useWishlist } from "@/hooks/useWishlist";
import { formatUSD, discountPercent, cn } from "@/lib/utils";
import {
  categories, products, searchProducts, recommendationsFor,
  type Product, type Accent,
} from "@/catalog";

const CAT_ICON: Record<string, LucideIcon> = {
  code: Code, sparkles: Sparkles, layout: LayoutGrid, table: Table, palette: Palette, layers: Layers,
};

const ACCENT: Record<Accent, { text: string; ring: string; grad: string; chip: string }> = {
  gold: { text: "text-gold-light", ring: "hover:border-gold/40", grad: "from-gold/20", chip: "border-gold/30 bg-gold/10 text-gold-light" },
  emerald: { text: "text-emerald-light", ring: "hover:border-emerald/40", grad: "from-emerald/20", chip: "border-emerald/30 bg-emerald/10 text-emerald-light" },
  royal: { text: "text-royal-light", ring: "hover:border-royal/40", grad: "from-royal/20", chip: "border-royal/30 bg-royal/10 text-royal-light" },
  violet: { text: "text-[#c4b5fd]", ring: "hover:border-[#8b5cf6]/40", grad: "from-[#8b5cf6]/20", chip: "border-[#8b5cf6]/30 bg-[#8b5cf6]/10 text-[#c4b5fd]" },
  cyan: { text: "text-[#67e8f9]", ring: "hover:border-[#22d3ee]/40", grad: "from-[#22d3ee]/20", chip: "border-[#22d3ee]/30 bg-[#22d3ee]/10 text-[#67e8f9]" },
};

function ProductCard({ p, onOpen }: { p: Product; onOpen: (id: string) => void }) {
  const { active, ready } = useOfferActive();
  const showOffer = (!ready || active) && p.offerPrice < p.originalPrice;
  const a = ACCENT[p.accent];
  const [state, setState] = React.useState<"idle" | "loading" | "unavailable">("idle");
  const { has, toggle } = useWishlist();
  const saved = has(p.id);

  async function buy() {
    if (state === "loading") return;
    setState("loading");
    try {
      const res = await fetch("/api/payment", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bookId: p.id }),
      });
      if (res.ok) {
        const d = (await res.json()) as { checkoutUrl?: string };
        if (d.checkoutUrl) { window.location.href = d.checkoutUrl; return; }
      }
    } catch { /* fall through */ }
    setState("unavailable"); setTimeout(() => setState("idle"), 3500);
  }

  return (
    <motion.article
      id={`course-${p.id}`}
      initial={{ opacity: 0, y: 22 }} whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-60px" }} transition={{ duration: 0.5 }}
      className={cn(
        "group relative flex scroll-mt-28 flex-col overflow-hidden rounded-2xl border border-white/10 bg-white/[0.03] backdrop-blur-xl transition-colors",
        a.ring
      )}
    >
      {/* cover */}
      <div className={cn("relative h-36 overflow-hidden bg-gradient-to-br to-night-900", a.grad)}>
        <div className="absolute inset-0 grid-bg opacity-30" />
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={cn("font-display text-3xl font-bold tracking-tight", a.text)}>{p.title}</span>
        </div>
        {p.badge && (
          <span className={cn("absolute left-3 top-3 rounded-full border px-2.5 py-0.5 text-[10px] font-medium", a.chip)}>
            {p.badge}
          </span>
        )}
        <button
          onClick={() => toggle(p.id)}
          aria-label={saved ? `Remove ${p.title} from wishlist` : `Save ${p.title} to wishlist`}
          aria-pressed={saved}
          className="absolute right-3 top-3 flex h-8 w-8 items-center justify-center rounded-full border border-white/15 bg-black/40 text-soft/70 transition-colors hover:text-gold-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gold/60"
        >
          <Heart className={cn("h-4 w-4", saved && "fill-gold-light text-gold-light")} />
        </button>
      </div>

      <div className="flex flex-1 flex-col p-5">
        <div className="flex items-center gap-2 text-[11px] text-soft/45">
          <span>{p.level}</span>
          {p.includes && <span>· {p.includes.length} courses</span>}
        </div>
        <h3 className="mt-1 font-display text-lg font-semibold text-soft">{p.title}</h3>
        <p className={cn("text-sm", a.text)}>{p.subtitle}</p>
        <p className="mt-2 line-clamp-3 text-[13px] leading-relaxed text-soft/55">{p.description}</p>

        <ul className="mt-3 space-y-1.5">
          {p.highlights.slice(0, 3).map((h) => (
            <li key={h} className="flex items-start gap-2 text-[12px] text-soft/70">
              <Check className="mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-light" />{h}
            </li>
          ))}
        </ul>

        <div className="mt-4 flex items-end justify-between border-t border-white/10 pt-4">
          <div className="flex items-end gap-2">
            <span className="font-display text-2xl font-semibold text-soft">
              {formatUSD(showOffer ? p.offerPrice : p.originalPrice)}
            </span>
            {showOffer && (
              <span className="mb-0.5 font-mono text-sm text-soft/40 line-through">{formatUSD(p.originalPrice)}</span>
            )}
          </div>
          {showOffer && (
            <Badge variant="emerald">-{discountPercent(p.originalPrice, p.offerPrice)}%</Badge>
          )}
        </div>

        <Button
          variant={p.accent === "emerald" ? "emerald" : "gold"}
          size="md" onClick={buy} disabled={state === "loading"}
          className="mt-3 w-full"
          aria-label={`Get ${p.title}`}
        >
          {state === "loading"
            ? <><Loader2 className="h-4 w-4 animate-spin" /> Opening…</>
            : <><ShoppingCart className="h-4 w-4" /> Get this course</>}
        </Button>

        <Link
          href={`/course/${p.id}`}
          className="mt-2 block text-center text-[12px] text-soft/55 underline-offset-2 transition-colors hover:text-gold-light hover:underline"
        >
          View full details
        </Link>

        {/* recommendations */}
        {(() => {
          const recs = recommendationsFor(p.id, 2);
          if (!recs.length) return null;
          return (
            <p className="mt-3 text-[11px] text-soft/45">
              Pairs well with{" "}
              {recs.map((r, i) => (
                <React.Fragment key={r.id}>
                  {i > 0 && " · "}
                  <button
                    onClick={() => onOpen(r.id)}
                    className="text-gold-light underline-offset-2 hover:underline"
                  >
                    {r.title}
                  </button>
                </React.Fragment>
              ))}
            </p>
          );
        })()}

        <p className="mt-2 flex items-center justify-center gap-1.5 text-center text-[11px] text-soft/45">
          <Lock className="h-3 w-3" />
          {state === "unavailable" ? "Checkout opens soon" : "Secure crypto checkout · instant download"}
        </p>
      </div>
    </motion.article>
  );
}

export function Marketplace() {
  const [cat, setCat] = React.useState<string>("all");
  const [query, setQuery] = React.useState("");
  const [onlySaved, setOnlySaved] = React.useState(false);
  const { ids: savedIds, count } = useWishlist();

  const shown = React.useMemo(() => {
    let list = query.trim() ? searchProducts(query) : products;
    if (cat !== "all") list = list.filter((p) => p.category === cat);
    if (onlySaved) list = list.filter((p) => savedIds.includes(p.id));
    return list;
  }, [query, cat, onlySaved, savedIds]);

  const openProduct = React.useCallback((id: string) => {
    setQuery("");
    setCat("all");
    setOnlySaved(false);
    requestAnimationFrame(() => {
      document.getElementById(`course-${id}`)?.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  }, []);

  return (
    <section id="courses" className="relative scroll-mt-24 py-24 sm:py-28">
      <div className="container-tight">
        <SectionHeading
          eyebrow="The Library"
          title={<>Learn the skills that <span className="text-gradient-gold">actually pay.</span></>}
          description="Premium, practical courses in programming, AI, web, design and productivity — each trilingual (English · العربية · Türkçe), delivered instantly."
        />

        {/* search */}
        <div className="mx-auto mt-10 max-w-xl">
          <label htmlFor="course-search" className="sr-only">Search courses</label>
          <div className="relative">
            <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-soft/40" />
            <input
              id="course-search"
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search courses — python, ai, design, sql…"
              className="h-12 w-full rounded-full border border-white/12 bg-white/[0.05] pl-11 pr-11 text-sm text-soft placeholder:text-soft/35 outline-none transition-colors focus:border-gold/50 focus:ring-2 focus:ring-gold/25"
            />
            {query && (
              <button
                onClick={() => setQuery("")}
                aria-label="Clear search"
                className="absolute right-4 top-1/2 -translate-y-1/2 text-soft/40 hover:text-soft"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>

        {/* category filter + wishlist toggle */}
        <div className="mt-6 flex flex-wrap justify-center gap-2">
          <FilterChip active={cat === "all" && !onlySaved} onClick={() => { setCat("all"); setOnlySaved(false); }} label="All" icon={Star} />
          {categories.map((c) => (
            <FilterChip
              key={c.id}
              active={cat === c.id && !onlySaved}
              onClick={() => { setCat(c.id); setOnlySaved(false); }}
              label={c.label}
              icon={CAT_ICON[c.icon] || Code}
            />
          ))}
          <FilterChip
            active={onlySaved}
            onClick={() => setOnlySaved((v) => !v)}
            label={count ? `Saved (${count})` : "Saved"}
            icon={Heart}
          />
        </div>

        <p aria-live="polite" className="mt-5 text-center text-xs text-soft/45">
          {shown.length} {shown.length === 1 ? "course" : "courses"}
          {query ? ` matching “${query}”` : ""}
        </p>

        {shown.length === 0 ? (
          <div className="mt-8 rounded-2xl border border-white/10 bg-white/[0.03] p-10 text-center">
            <p className="text-soft/70">No courses match that search.</p>
            <Button variant="glass" size="sm" className="mt-4" onClick={() => { setQuery(""); setCat("all"); setOnlySaved(false); }}>
              Clear filters
            </Button>
          </div>
        ) : (
          <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {shown.map((p) => <ProductCard key={p.id} p={p} onOpen={openProduct} />)}
          </div>
        )}
      </div>
    </section>
  );
}

function FilterChip({ active, onClick, label, icon: Icon }: { active: boolean; onClick: () => void; label: string; icon: LucideIcon }) {
  return (
    <button
      onClick={onClick}
      aria-pressed={active}
      className={cn(
        "flex items-center gap-1.5 rounded-full border px-4 py-2 text-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gold/60",
        active ? "border-gold/40 bg-gold/10 text-gold-light" : "border-white/10 bg-white/[0.03] text-soft/60 hover:text-soft"
      )}
    >
      <Icon className="h-3.5 w-3.5" /> {label}
    </button>
  );
}
