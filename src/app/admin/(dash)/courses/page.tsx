import fs from "fs";
import path from "path";
import { CheckCircle2, XCircle } from "lucide-react";
import { products, categories } from "@/catalog";
import { fmtMoney } from "@/components/admin/ui";

export const dynamic = "force-dynamic";

/**
 * Catalog overview — every course & bundle, its category, pricing, languages
 * and whether its encrypted delivery blob is present in the repo. Read-only:
 * the catalog is config-driven (src/catalog.ts) and delivery blobs are built
 * from the E-tqan book engine, so this page is the single source of truth for
 * "what's live and deliverable".
 */
export default function CoursesPage() {
  const coursesDir = path.join(process.cwd(), "assets", "courses");
  const catLabel = Object.fromEntries(categories.map((c) => [c.id, c.label]));

  const rows = products.map((p) => {
    const enc = path.join(coursesDir, `${p.id}.enc`);
    let ready = false;
    let sizeMb = 0;
    try {
      const st = fs.statSync(enc);
      ready = true;
      sizeMb = st.size / 1048576;
    } catch {
      ready = false;
    }
    const langs = p.type === "bundle" ? "EN · AR · TR" : Object.keys(p.files).map((l) => l.toUpperCase()).join(" · ") || "—";
    return { p, ready, sizeMb, langs };
  });

  const readyCount = rows.filter((r) => r.ready).length;

  return (
    <div>
      <h1 className="font-display text-2xl font-semibold text-soft">Courses &amp; Bundles</h1>
      <p className="mt-1 text-sm text-soft/50">
        The full catalog ({products.length} products, {readyCount} delivery-ready). Content is
        managed in <code className="text-gold-light">src/catalog.ts</code> and packed by the E-tqan book engine.
      </p>

      <div className="mt-6 glass overflow-x-auto rounded-2xl">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-white/10 text-xs uppercase text-soft/45">
            <tr>
              <th className="px-4 py-3">Product</th>
              <th className="px-4 py-3">Category</th>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3">Price</th>
              <th className="px-4 py-3">Languages</th>
              <th className="px-4 py-3">Delivery</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(({ p, ready, sizeMb, langs }) => (
              <tr key={p.id} className="border-b border-white/5">
                <td className="px-4 py-3">
                  <div className="font-medium text-soft">{p.title}</div>
                  <div className="text-xs text-soft/40">{p.id}</div>
                </td>
                <td className="px-4 py-3 text-soft/70">{catLabel[p.category] ?? p.category}</td>
                <td className="px-4 py-3 text-soft/60">{p.type}</td>
                <td className="px-4 py-3">
                  <span className="text-soft">{fmtMoney(p.offerPrice)}</span>{" "}
                  <span className="text-xs text-soft/40 line-through">{fmtMoney(p.originalPrice)}</span>
                </td>
                <td className="px-4 py-3 text-soft/60">{langs}</td>
                <td className="px-4 py-3">
                  {ready ? (
                    <span className="inline-flex items-center gap-1.5 text-emerald-light">
                      <CheckCircle2 className="h-4 w-4" /> {sizeMb.toFixed(1)}MB
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 text-soft/40">
                      <XCircle className="h-4 w-4" /> missing
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
