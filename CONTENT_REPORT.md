# Content Report — E-tqan Library

Every source file provided was **transformed into an original, premium
educational book** — not repackaged. Author names and publisher branding from
the sources were removed; content was rewritten, expanded and modernized to
2026 standards, then professionally typeset with the E-tqan identity.

## The book engine

Books are produced by a purpose-built pipeline in `bookgen/`:

- **Design system** (`engine/theme.css`) — dramatic dark cover, ivory body,
  per-book accent, clickable ToC, running footers, PDF bookmarks.
- **Authoring DSL** (`engine/dsl.mjs`) — chapters, callouts (tip/warn/note/key/
  pitfall), syntax-highlighted code cards, tables, quizzes, exercises, projects,
  case studies, SVG flow diagrams, pull quotes.
- **Renderer** (`engine/render.mjs`) — assembles cover + colophon + clickable
  ToC + chapters, highlights code (highlight.js), and prints to PDF via headless
  Chromium with real bookmarks and page numbers.
- **Fonts** — self-hosted Sora, Source Serif 4, Inter, JetBrains Mono (Latin +
  latin-ext) and Cairo/Amiri (Arabic), with correct unicode-ranges for EN/TR/AR.

Book **sources are the paid product**, so they are stored **encrypted**
(`bookgen/books.vault.enc`); plaintext content is never committed to this public
repo. Rendered PDFs are packed into encrypted delivery blobs
(`assets/courses/*.enc`) and only decrypted to the CDN at build time.

Each book includes: a premium cover, colophon, **clickable table of contents /
PDF bookmarks**, chapter openers with learning goals, rich body with diagrams,
comparison tables, callouts, highlighted code, **exercises, quizzes (with answer
keys), projects and real-world case studies**, and a capstone.

## The library (11 courses + 3 bundles, trilingual)

| Course | Chapters | Languages | Delivery |
|--------|:--------:|-----------|----------|
| Python | 10 | EN · AR · TR | `python.enc` |
| JavaScript | 7 | EN · AR · TR | `javascript.enc` |
| Java | 6 | EN · AR · TR | `java.enc` |
| HTML | 5 | EN · AR · TR | `html.enc` |
| CSS | 5 | EN · AR · TR | `css.enc` |
| SQL | 5 | EN · AR | `sql.enc` |
| AI App Building | 6 | EN · AR · TR | `ai-app-building.enc` |
| Building Any Website | 5 | EN · AR · TR | `building-websites.enc` |
| Excel + AI | 5 | EN · AR · TR | `excel-ai.enc` |
| Design & Graphics | 5 | EN · AR · TR | `design-graphics.enc` |
| **AI Arsenal 2026** | 7 | EN · AR · TR | `ai-arsenal.enc` |
| Bundle — Programming Languages | — | trilingual | `bundle-languages.enc` |
| Bundle — Future Skills | — | trilingual | `bundle-future-skills.enc` |
| Bundle — Gold Master Library | — | trilingual | `bundle-gold.enc` |

> SQL ships EN·AR because the provided source had no Turkish edition; all other
> courses are fully trilingual. Bundles package the premium editions of their
> member courses.

## The "200 Project Ideas" → business blueprints

The AI Arsenal source's "project ideas" were transformed, per the master prompt,
into an actionable framework rather than a list:

- A **nine-part business-blueprint framework** (problem, solution, market, stack,
  monetization, costs, revenue, risks, scaling + AI leverage).
- Fully **worked blueprints** (niche newsletter, productized AI agency,
  micro-SaaS) with realistic numbers, risks and monetization.
- A **categorized 200-idea bank** across ten categories to run through the
  framework, plus a launch-and-scale playbook.

## Modernization & de-branding

- Updated to current tools/practices (e.g. Python 3.12, ES2020+, `const`/`let`,
  Flexbox/Grid, mobile-first, XLOOKUP, modern AI tools).
- Original author names and publisher branding from the source PDFs were
  removed; all content is presented under the E-tqan identity as original
  educational material.

## Verifying content integrity

`npm test` (`tests/catalog.test.mjs`) asserts every catalog product has a
committed, non-empty encrypted delivery blob, so the store can never list a
course it cannot deliver.
