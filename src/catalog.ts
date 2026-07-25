/**
 * ============================================================
 *  E-TQAN — EDUCATIONAL MARKETPLACE CATALOG
 * ============================================================
 *  Courses & bundles (trilingual EN/AR/TR product PDFs).
 *  Edit prices / products here only. Delivery, payments and the
 *  storefront grid are all driven by this file.
 * ============================================================
 */

export type Locale = "en" | "ar" | "tr";
export type Accent = "gold" | "emerald" | "royal" | "violet" | "cyan";

export interface Category {
  id: string;
  label: string;
  icon: string;
}

export interface Product {
  id: string;
  category: string;
  type: "course" | "bundle";
  title: string;
  subtitle: string;
  description: string;
  level: "Beginner" | "Intermediate" | "Advanced" | "All levels";
  accent: Accent;
  badge?: string;
  featured?: boolean;
  originalPrice: number;
  offerPrice: number;
  highlights: string[];
  /** Search keywords. */
  tags?: string[];
  /** Recommended companion product ids. */
  related?: string[];
  /** Bundle only: product ids it contains. */
  includes?: string[];
  /** Trilingual source files, relative to the private courses dir. */
  files: Partial<Record<Locale, string>>;
}

export const categories: Category[] = [
  { id: "programming", label: "Programming", icon: "code" },
  { id: "ai", label: "AI & Automation", icon: "sparkles" },
  { id: "web", label: "Web & Apps", icon: "layout" },
  { id: "productivity", label: "Productivity", icon: "table" },
  { id: "design", label: "Design", icon: "palette" },
  { id: "bundles", label: "Bundles", icon: "layers" },
];

const F = (folder: string, base: string): Partial<Record<Locale, string>> => ({
  en: `${folder}/${base} - English.pdf`,
  ar: `${folder}/${base} - Arabic.pdf`,
  tr: `${folder}/${base} - Turkish.pdf`,
});

export const products: Product[] = [
  // ── Programming ──
  {
    id: "python", category: "programming", type: "course", accent: "emerald",
    title: "Python", subtitle: "From Zero to Confident Coder", level: "Beginner",
    description: "The clearest path into programming. Learn Python by building — variables, logic, functions, data structures and your first real projects.",
    originalPrice: 15, offerPrice: 10, badge: "Most popular",
    highlights: ["Beginner-friendly, hands-on", "Real mini-projects", "Trilingual: EN · AR · TR"],
    tags: ["python", "programming", "beginner", "data", "automation", "scripting", "pandas"],
    related: ["sql", "ai-app-building", "excel-ai"],
    files: F("01_python", "Python"),
  },
  {
    id: "javascript", category: "programming", type: "course", accent: "gold",
    title: "JavaScript", subtitle: "The Language of the Web", level: "Beginner",
    description: "Make websites come alive. Master modern JavaScript — the DOM, events, async, and the fundamentals every web developer needs.",
    originalPrice: 15, offerPrice: 10,
    highlights: ["Modern ES2026 syntax", "Interactive web projects", "Trilingual: EN · AR · TR"],
    tags: ["javascript", "js", "web", "frontend", "dom", "async", "react", "node"],
    related: ["html", "css", "building-websites"],
    files: F("02_javascript", "JavaScript"),
  },
  {
    id: "java", category: "programming", type: "course", accent: "royal",
    title: "Java", subtitle: "Build Robust, Real Software", level: "Intermediate",
    description: "The backbone of enterprise apps. Learn object-oriented programming, collections and clean architecture with Java.",
    originalPrice: 15, offerPrice: 10,
    highlights: ["OOP done right", "Enterprise-grade patterns", "Trilingual: EN · AR · TR"],
    tags: ["java", "oop", "backend", "android", "enterprise", "spring"],
    related: ["sql", "python"],
    files: F("03_java", "Java"),
  },
  {
    id: "html", category: "programming", type: "course", accent: "cyan",
    title: "HTML", subtitle: "The Skeleton of Every Website", level: "Beginner",
    description: "Where every web developer starts. Structure pages the right way — semantic, accessible, SEO-ready HTML.",
    originalPrice: 7, offerPrice: 5,
    highlights: ["Semantic & accessible", "SEO foundations", "Trilingual: EN · AR · TR"],
    tags: ["html", "web", "markup", "semantic", "seo", "accessibility"],
    related: ["css", "javascript", "building-websites"],
    files: F("04_html", "HTML"),
  },
  {
    id: "css", category: "programming", type: "course", accent: "violet",
    title: "CSS", subtitle: "Design Beautiful Interfaces", level: "Beginner",
    description: "Turn plain pages into stunning designs. Flexbox, grid, animations and responsive layouts that look premium on any screen.",
    originalPrice: 7, offerPrice: 5,
    highlights: ["Flexbox & Grid mastery", "Responsive & animated", "Trilingual: EN · AR · TR"],
    tags: ["css", "design", "styling", "flexbox", "grid", "responsive"],
    related: ["html", "javascript", "design-graphics"],
    files: F("05_css", "CSS"),
  },
  {
    id: "sql", category: "programming", type: "course", accent: "emerald",
    title: "SQL", subtitle: "Talk to Data Like a Pro", level: "Beginner",
    description: "Data runs the world. Query, filter, join and analyze databases with confidence — the skill behind every data job.",
    originalPrice: 10, offerPrice: 7,
    highlights: ["Queries to joins", "Real datasets", "EN · AR · TR"],
    tags: ["sql", "database", "data", "queries", "joins", "mysql", "postgres"],
    related: ["python", "excel-ai"],
    files: { en: "06_sql/SQL - English.pdf", ar: "06_sql/SQL - Arabic.pdf" },
  },

  // ── AI & Automation ──
  {
    id: "ai-arsenal", category: "ai", type: "course", accent: "gold",
    title: "AI Arsenal 2026", subtitle: "Every AI Tool + 200 Project Ideas", level: "All levels",
    description: "Your complete AI advantage. A curated arsenal of the best AI tools plus 200 ready-to-build project ideas to turn skills into income.",
    originalPrice: 20, offerPrice: 15, badge: "Flagship", featured: true,
    highlights: ["The best AI tools, organized", "200 project ideas included", "Trilingual: EN · AR · TR"],
    tags: ["ai", "tools", "prompts", "business", "ideas", "blueprint", "income"],
    related: ["ai-app-building", "design-graphics", "excel-ai"],
    files: {
      en: "11_ai_arsenal_2026/AI Arsenal 2026 - English (Tools Guide).pdf",
      ar: "11_ai_arsenal_2026/AI Arsenal 2026 - Arabic (Tools Guide).pdf",
      tr: "11_ai_arsenal_2026/AI Arsenal 2026 - Turkish (Tools Guide).pdf",
    },
  },
  {
    id: "ai-app-building", category: "ai", type: "course", accent: "royal",
    title: "AI App Building", subtitle: "Ship Apps with AI — Fast", level: "Intermediate",
    description: "Build real applications powered by AI, even without a heavy coding background. From idea to working app using modern AI tools.",
    originalPrice: 20, offerPrice: 15,
    highlights: ["Idea → working app", "AI-first workflow", "Trilingual: EN · AR · TR"],
    tags: ["ai", "apps", "nocode", "build", "ship", "product"],
    related: ["ai-arsenal", "building-websites", "javascript"],
    files: F("07_ai_app_building", "AI App Building"),
  },

  // ── Web & Apps ──
  {
    id: "building-websites", category: "web", type: "course", accent: "cyan",
    title: "Building Any Website", subtitle: "From Blank Page to Live Site", level: "Beginner",
    description: "Launch professional websites for yourself or clients. Plan, design, build and deploy — the complete modern workflow.",
    originalPrice: 15, offerPrice: 10,
    highlights: ["Plan → design → deploy", "Client-ready results", "Trilingual: EN · AR · TR"],
    tags: ["website", "web", "fullstack", "deploy", "frontend", "backend"],
    related: ["html", "css", "javascript"],
    files: F("08_building_any_website", "Building Any Website"),
  },

  // ── Productivity ──
  {
    id: "excel-ai", category: "productivity", type: "course", accent: "emerald",
    title: "Excel + AI", subtitle: "10x Your Spreadsheet Power", level: "All levels",
    description: "Do in minutes what used to take hours. Master Excel and supercharge it with AI for analysis, automation and reporting.",
    originalPrice: 10, offerPrice: 7,
    highlights: ["Formulas to automation", "AI-powered analysis", "Trilingual: EN · AR · TR"],
    tags: ["excel", "spreadsheet", "data", "ai", "analysis", "reporting", "pivot"],
    related: ["sql", "ai-arsenal"],
    files: F("09_excel_ai", "Excel and AI"),
  },

  // ── Design ──
  {
    id: "design-graphics", category: "design", type: "course", accent: "violet",
    title: "Design & Graphics", subtitle: "Create Like a Pro Designer", level: "Beginner",
    description: "Design stunning visuals for brands and social media. Principles, tools and AI shortcuts to produce professional graphics fast.",
    originalPrice: 10, offerPrice: 7,
    highlights: ["Design principles", "Tools + AI shortcuts", "Trilingual: EN · AR · TR"],
    tags: ["design", "graphics", "branding", "color", "typography", "canva", "figma"],
    related: ["css", "ai-arsenal"],
    files: F("10_design_graphics", "Design and Graphics"),
  },

  // ── Bundles ──
  {
    id: "bundle-languages", category: "bundles", type: "bundle", accent: "royal",
    title: "Programming Languages Bundle", subtitle: "6 Courses · One Path", level: "Beginner",
    description: "Everything to become a developer: HTML, CSS, JavaScript, Python, Java and SQL — one clear learning path, one discounted price.",
    originalPrice: 54, offerPrice: 29, badge: "Save 40%",
    includes: ["html", "css", "javascript", "python", "java", "sql"],
    highlights: ["6 full courses", "Beginner → job-ready", "Trilingual: EN · AR · TR"],
    tags: ["bundle", "programming", "languages", "path", "value"],
    related: ["bundle-gold"],
    files: {},
  },
  {
    id: "bundle-future-skills", category: "bundles", type: "bundle", accent: "emerald",
    title: "Future Skills Bundle", subtitle: "AI · Web · Design · Data", level: "All levels",
    description: "The skills that pay in 2026: AI App Building, Building Any Website, Design & Graphics, and Excel + AI — bundled and discounted.",
    originalPrice: 65, offerPrice: 39, badge: "Save 36%",
    includes: ["ai-app-building", "building-websites", "design-graphics", "excel-ai"],
    highlights: ["4 future-proof skills", "Skills → income", "Trilingual: EN · AR · TR"],
    tags: ["bundle", "ai", "web", "design", "future", "value"],
    related: ["bundle-gold"],
    files: {},
  },
  {
    id: "bundle-gold", category: "bundles", type: "bundle", accent: "gold",
    title: "Gold Master Library", subtitle: "Every Course. One Price.", level: "All levels",
    description: "The complete E-tqan library — every current course and bundle, plus AI Arsenal 2026 and 200 project ideas. The best value we offer.",
    originalPrice: 144, offerPrice: 79, badge: "Best value", featured: true,
    includes: [
      "python", "javascript", "java", "html", "css", "sql",
      "ai-arsenal", "ai-app-building", "building-websites", "excel-ai", "design-graphics",
    ],
    highlights: ["The entire library", "Lifetime updates", "Trilingual: EN · AR · TR"],
    tags: ["bundle", "everything", "library", "best value", "complete"],
    related: ["bundle-languages", "bundle-future-skills"],
    files: {},
  },
];

export function getProduct(id: string): Product | undefined {
  return products.find((p) => p.id === id);
}

export function productsByCategory(catId: string): Product[] {
  return products.filter((p) => p.category === catId);
}

/** Free-text search across title, subtitle, description and tags. */
export function searchProducts(query: string): Product[] {
  const q = query.trim().toLowerCase();
  if (!q) return products;
  const terms = q.split(/\s+/).filter(Boolean);
  return products.filter((p) => {
    const haystack = [
      p.title, p.subtitle, p.description, p.level, p.category,
      ...(p.tags ?? []), ...p.highlights,
    ].join(" ").toLowerCase();
    return terms.every((t) => haystack.includes(t));
  });
}

/** Recommended companions for a product (explicit `related`, then same-category). */
export function recommendationsFor(id: string, limit = 3): Product[] {
  const p = getProduct(id);
  if (!p) return [];
  const out: Product[] = [];
  for (const rid of p.related ?? []) {
    const r = getProduct(rid);
    if (r && r.id !== id) out.push(r);
  }
  for (const c of products) {
    if (out.length >= limit) break;
    if (c.id !== id && c.category === p.category && !out.some((o) => o.id === c.id)) out.push(c);
  }
  return out.slice(0, limit);
}

/** Featured products for merchandising rows. */
export function featuredProducts(): Product[] {
  return products.filter((p) => p.featured);
}
