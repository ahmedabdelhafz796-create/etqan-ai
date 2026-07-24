import { getBook } from "@/config";
import { getProduct } from "@/catalog";

/**
 * A single lookup that resolves any purchasable id — whether it's a legacy
 * trading book or a catalog course/bundle — to the fields the payment,
 * webhook, thank-you and download flows all need. `ext` is the file
 * extension of the decrypted asset on the CDN (books ship as a single PDF,
 * courses/bundles as a ZIP of their trilingual PDFs).
 */
export interface Purchasable {
  id: string;
  title: string;
  ext: "pdf" | "zip";
}

export function getPurchasable(id: string): Purchasable | undefined {
  const book = getBook(id);
  if (book) return { id: book.id, title: book.title, ext: "pdf" };
  const product = getProduct(id);
  if (product) return { id: product.id, title: product.title, ext: "zip" };
  return undefined;
}
