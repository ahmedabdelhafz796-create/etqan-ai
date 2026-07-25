import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { renderBook } from "./engine/render.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dirname, "out");
fs.mkdirSync(OUT, { recursive: true });

const targets = process.argv.slice(2); // e.g. python.en  or  all
const booksDir = path.join(__dirname, "books");
let files = fs.readdirSync(booksDir).filter((f) => f.endsWith(".mjs"));
if (targets.length && targets[0] !== "all") {
  files = files.filter((f) => targets.some((t) => f === `${t}.mjs` || f.startsWith(`${t}.`) || f === t));
}

console.log(`[bookgen] rendering ${files.length} book(s)…`);
for (const f of files) {
  const mod = await import(path.join(booksDir, f));
  const book = mod.book || mod.default;
  const out = path.join(OUT, f.replace(/\.mjs$/, ".pdf"));
  await renderBook(book, out);
}
console.log("[bookgen] done.");
