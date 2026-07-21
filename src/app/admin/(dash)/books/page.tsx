import { isDbConfigured } from "@/lib/db";
import { books } from "@/config";
import { getEffectiveConfig } from "@/lib/site-settings";
import { DbNotice } from "@/components/admin/ui";
import { BookAdmin } from "@/components/admin/BookAdmin";

export const dynamic = "force-dynamic";

export default async function BooksPage() {
  if (!isDbConfigured()) return <DbNotice />;
  const cfg = await getEffectiveConfig();

  return (
    <div>
      <h1 className="font-display text-2xl font-semibold text-soft">
        Books &amp; Pricing
      </h1>
      <p className="mt-1 text-sm text-soft/50">
        Edit prices, discounts and product files. Prices apply to the live store.
      </p>

      <div className="mt-6 space-y-5">
        {books.map((b) => {
          const eff = cfg.books[b.id];
          return (
            <BookAdmin
              key={b.id}
              bookId={b.id}
              title={b.title}
              originalPrice={eff.originalPrice}
              offerPrice={eff.offerPrice}
              active={eff.active}
            />
          );
        })}
      </div>
    </div>
  );
}
