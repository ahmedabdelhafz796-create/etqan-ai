"use client";

import { SectionHeading } from "@/components/ui/section-heading";
import { BookCard } from "@/components/sections/BookCard";
import { useT } from "@/components/providers/I18nProvider";
import type { Book } from "@/config";

export function BookStore({
  books,
  activeIds,
}: {
  books: Book[];
  activeIds?: string[];
}) {
  const t = useT();
  const visible = activeIds
    ? books.filter((b) => activeIds.includes(b.id))
    : books;

  return (
    <section id="store" className="relative scroll-mt-24 py-24 sm:py-28">
      <div className="container-tight">
        <SectionHeading
          eyebrow={t.store.eyebrow}
          title={
            <>
              {t.store.title1}{" "}
              <span className="text-gradient-gold">{t.store.titleGold}</span>
            </>
          }
          description={t.store.description}
        />

        <div className="mt-14 space-y-10">
          {visible.map((book, i) => (
            <BookCard key={book.id} book={book} index={i} />
          ))}
        </div>
      </div>
    </section>
  );
}
