# E-tqan Book Engine

Turns authored content into **premium, print-ready PDF books** with the E-tqan
identity: dramatic cover, clickable bookmarks, syntax-highlighted code, diagrams,
tables, callouts, exercises, quizzes, case studies and projects.

This is the production toolchain behind the store's educational library. Source
files here are **authoring inputs** — the sold products are the encrypted ZIPs in
`assets/courses/` (see `scripts/prepare-downloads.mjs`).

## Layout

| Path | What |
|------|------|
| `engine/theme.css` | The premium book design system (light ivory body + dark cover, per-book accent) |
| `engine/dsl.mjs` | Authoring helpers (`chapter`, `code`, `table`, `quiz`, `exercise`, `flow`, …) |
| `engine/render.mjs` | Assembles cover + colophon + clickable ToC + chapters, highlights code, prints PDF via headless Chromium |
| `engine/fonts.css` + `fonts/` | Self-hosted premium fonts (Sora, Source Serif 4, Inter, JetBrains Mono, Cairo, Amiri) with correct unicode-ranges for EN/TR/AR |
| `build.mjs` | `node build.mjs <name>` renders `books/<name>.mjs` → `out/<name>.pdf` |
| `vault.mjs` | Packs/restores the private `books/` sources as an encrypted blob |
| `books.vault.enc` | **Encrypted** book sources (the paid content — never stored in plaintext here) |

`books/`, `out/` and `node_modules/` are gitignored.

## Setup (fresh container)

```bash
cd bookgen
npm install                       # playwright (library) + highlight.js
NOWPAYMENTS_IPN_SECRET=… node vault.mjs unpack   # restore books/ sources
```

Chromium is preinstalled; `render.mjs` points at it directly (no browser download).

## Author & render

```bash
node build.mjs python.en          # one book
node build.mjs all                # every book in books/
```

After editing content, re-seal the sources so they persist:

```bash
NOWPAYMENTS_IPN_SECRET=… node vault.mjs pack
```

## Publish to the store

Rendered PDFs are packed into the encrypted course ZIPs consumed by the app:

```bash
NOWPAYMENTS_IPN_SECRET=… EDU_DIR=… node ../scripts/pack-courses.mjs
```
