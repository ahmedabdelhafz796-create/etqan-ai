import { SectionHeading } from "@/components/ui/section-heading";
import { BookCard } from "@/components/sections/BookCard";
import { books } from "@/config";

export function BookStore() {
  return (
    <section id="store" className="relative scroll-mt-24 py-24 sm:py-28">
      <div className="container-tight">
        <SectionHeading
          eyebrow="The Library"
          title={
            <>
              Two books. One institutional{" "}
              <span className="text-gradient-gold">edge.</span>
            </>
          }
          description="Each title is a complete, self-contained education — designed to take you from reading price like a professional to building your own trading systems."
        />

        <div className="mt-14 space-y-10">
          {books.map((book, i) => (
            <BookCard key={book.id} book={book} index={i} />
          ))}
        </div>
      </div>
    </section>
  );
}
