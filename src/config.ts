/**
 * ============================================================
 *  ETQAN AI — CENTRAL ADMIN CONFIGURATION
 * ============================================================
 *  Everything you'll ever need to edit lives in THIS file:
 *    • Book prices & discounts
 *    • Countdown / offer end date
 *    • Telegram link placeholder
 *    • Payment URL placeholder
 *    • Brand + social + SEO strings
 *
 *  Change a value here and it propagates across the entire site.
 * ============================================================
 */

export const siteConfig = {
  name: "ETQAN AI",
  brand: "Etqan • Trading Library",
  tagline: "Institutional-grade trading education, engineered for serious traders.",
  description:
    "A premium digital library of professional trading books — market structure, liquidity, order flow, SMC/ICT, Wyckoff and AI-driven institutional analysis. Learn the way funds actually trade.",
  url: process.env.NEXT_PUBLIC_SITE_URL || "https://etqan-ai.example.com",
  locale: "en_US",
  keywords: [
    "trading books",
    "smart money concepts",
    "ICT",
    "order flow",
    "market structure",
    "liquidity",
    "Wyckoff",
    "supply and demand",
    "AI trading",
    "institutional trading",
    "price action",
    "risk management",
  ],
  social: {
    telegram: process.env.NEXT_PUBLIC_TELEGRAM_URL || "TELEGRAM_URL_PLACEHOLDER",
    twitter: process.env.NEXT_PUBLIC_TWITTER_URL || "https://x.com/",
    youtube: process.env.NEXT_PUBLIC_YOUTUBE_URL || "https://youtube.com/",
    instagram: process.env.NEXT_PUBLIC_INSTAGRAM_URL || "https://instagram.com/",
    email: process.env.NEXT_PUBLIC_CONTACT_EMAIL || "support@etqan-ai.example.com",
  },
} as const;

/**
 * Analytics — inert until you provide an ID. The Analytics component only
 * injects a script when the matching value is set, so nothing loads (and no
 * cookies are set) while these are empty.
 */
export const analytics = {
  gaId: process.env.NEXT_PUBLIC_GA_ID || "", // e.g. G-XXXXXXXXXX
  plausibleDomain: process.env.NEXT_PUBLIC_PLAUSIBLE_DOMAIN || "", // e.g. etqan-ai.com
} as const;

/**
 * Optional direct-crypto wallet address (placeholder). NOWPayments manages
 * payout wallets in its dashboard, so this is only needed if you display a
 * manual wallet anywhere. Left empty by default.
 */
export const payment = {
  walletAddress: process.env.NEXT_PUBLIC_WALLET_ADDRESS || "", // WALLET_ADDRESS_PLACEHOLDER
} as const;

/**
 * Master placeholders. Replace ONE variable each and you're live.
 *   - PAYMENT_URL_PLACEHOLDER  → your NOWPayments / checkout link
 *   - TELEGRAM_URL_PLACEHOLDER → your Telegram invite link
 */
export const links = {
  paymentUrl: process.env.NEXT_PUBLIC_PAYMENT_URL || "PAYMENT_URL_PLACEHOLDER",
  telegramUrl: process.env.NEXT_PUBLIC_TELEGRAM_URL || "TELEGRAM_URL_PLACEHOLDER",
} as const;

/**
 * Offer / countdown configuration.
 * When `offerEndsAt` passes, discounts are hidden automatically and
 * original prices are restored across the whole site.
 */
export const offerConfig = {
  /** ISO string — First Edition Celebration deadline. */
  offerEndsAt: "2026-07-30T23:59:00",
  /** Human label used in banners. */
  offerDeadlineLabel: "July 30, 2026 · 23:59",
  celebrationTitle: "First Edition Celebration",
  celebrationSubtitle: "Founding-price offer — locked until July 30",
  /** Date the Telegram signals channel goes live. */
  telegramLaunchLabel: "August 1st, 2026",
} as const;

export type Currency = "USD";

export interface BookChapter {
  title: string;
  lessons: string[];
}

export interface BookModule {
  title: string;
  icon: string;
  chapters: BookChapter[];
}

export interface Book {
  id: string;
  order: number;
  title: string;
  subtitle: string;
  badge: string;
  tagline: string;
  description: string;
  cover: {
    label: string;
    edition: string;
    accent: "gold" | "emerald" | "royal";
  };
  currency: Currency;
  /** Full price shown once the offer ends. */
  originalPrice: number;
  /** Discounted price while the offer is live. */
  offerPrice: number;
  highlights: string[];
  stats: { label: string; value: string }[];
  /** Expandable "Inside the Book" curriculum. */
  curriculum: BookModule[];
  includes: string[];
}

/**
 * ============================================================
 *  BOOK CATALOG — edit prices / content here only.
 * ============================================================
 */
export const books: Book[] = [
  {
    id: "triple-analysis",
    order: 1,
    title: "Triple Analysis",
    subtitle: "The Institutional Framework for Reading Any Market",
    badge: "Bestselling First Edition",
    tagline: "Structure · Liquidity · Order Flow — unified into one repeatable model.",
    description:
      "A complete, ground-up trading education built on the exact logic institutions use to move price. Triple Analysis fuses market structure, liquidity engineering and order flow into a single decision framework — then hands you the checklists, entry models and case studies to trade it with confidence.",
    cover: { label: "Triple Analysis", edition: "First Edition", accent: "gold" },
    currency: "USD",
    originalPrice: 80,
    offerPrice: 65,
    highlights: [
      "Read market structure like a desk trader",
      "Map liquidity before price even moves",
      "SMC & ICT concepts, decoded step by step",
      "Institutional entry & exit execution models",
    ],
    stats: [
      { label: "Modules", value: "12" },
      { label: "Chapters", value: "48+" },
      { label: "Chart Examples", value: "220+" },
    ],
    curriculum: [
      {
        title: "Foundations & Market Structure",
        icon: "layout",
        chapters: [
          {
            title: "How Markets Really Move",
            lessons: [
              "The three-force model: structure, liquidity, order flow",
              "Why retail patterns fail — and what replaces them",
              "Reading higher-timeframe context first",
            ],
          },
          {
            title: "Market Structure Mastery",
            lessons: [
              "Break of structure (BOS) vs. change of character (CHoCH)",
              "Internal vs. external structure",
              "Mapping trends across nested timeframes",
            ],
          },
        ],
      },
      {
        title: "Liquidity Engineering",
        icon: "waves",
        chapters: [
          {
            title: "The Anatomy of Liquidity",
            lessons: [
              "Buy-side & sell-side liquidity pools",
              "Equal highs, equal lows and liquidity voids",
              "Stop hunts, sweeps and the raid-and-reverse",
            ],
          },
          {
            title: "Liquidity Mapping in Practice",
            lessons: [
              "Marking draw-on-liquidity targets",
              "Premium & discount arrays",
              "Timing entries around liquidity grabs",
            ],
          },
        ],
      },
      {
        title: "Order Flow & Smart Money",
        icon: "activity",
        chapters: [
          {
            title: "Order Flow Foundations",
            lessons: [
              "Order blocks, mitigation & breaker blocks",
              "Fair value gaps and imbalance",
              "Displacement as a signal of intent",
            ],
          },
          {
            title: "Smart Money Concepts (SMC)",
            lessons: [
              "The SMC playbook, distilled",
              "Institutional order flow footprints",
              "Combining SMC with structure & liquidity",
            ],
          },
          {
            title: "ICT Concepts, Decoded",
            lessons: [
              "Killzones and optimal trade entry (OTE)",
              "Silver bullet & judas swing setups",
              "Power of three: accumulation, manipulation, distribution",
            ],
          },
        ],
      },
      {
        title: "Classical Edge: Wyckoff & S/D",
        icon: "bar-chart-3",
        chapters: [
          {
            title: "Wyckoff Method",
            lessons: [
              "Accumulation & distribution schematics",
              "Springs, upthrusts and tests",
              "The composite operator mindset",
            ],
          },
          {
            title: "Supply & Demand",
            lessons: [
              "Drawing zones that actually hold",
              "Fresh vs. tested zones",
              "Confluence with liquidity & order blocks",
            ],
          },
        ],
      },
      {
        title: "Execution & Entry Models",
        icon: "crosshair",
        chapters: [
          {
            title: "Advanced Entry Models",
            lessons: [
              "The A+ setup checklist",
              "Refined entries: from HTF bias to LTF trigger",
              "Scaling in with confirmation",
            ],
          },
          {
            title: "Exit Strategies",
            lessons: [
              "Partial exits & runners",
              "Structure-based trailing stops",
              "Locking profit at liquidity targets",
            ],
          },
        ],
      },
      {
        title: "Risk, Psychology & Application",
        icon: "shield",
        chapters: [
          {
            title: "Risk Management System",
            lessons: [
              "Position sizing & the 1% rule reframed",
              "R-multiples and expectancy",
              "Drawdown control & recovery math",
            ],
          },
          {
            title: "Trading Psychology",
            lessons: [
              "Mastering fear, greed and impatience",
              "Building process over outcome",
              "The professional's daily routine",
            ],
          },
          {
            title: "Case Studies & Exercises",
            lessons: [
              "Full trade breakdowns, entry to exit",
              "Annotated real-market examples",
              "Practice exercises & professional checklists",
            ],
          },
        ],
      },
    ],
    includes: [
      "Lifetime updates to the First Edition",
      "Printable professional checklists",
      "220+ annotated chart examples",
      "Practice exercises with worked solutions",
    ],
  },
  {
    id: "ai-trading",
    order: 2,
    title: "Advanced AI Trading",
    subtitle: "Institutional Analysis, Automation & Professional Trading Systems",
    badge: "Advanced · Practitioner Level",
    tagline: "Where institutional logic meets applied artificial intelligence.",
    description:
      "The advanced companion for traders ready to industrialize their edge. Advanced AI Trading goes deep into institutional analysis, market-data pipelines, execution engineering and AI integration — turning discretionary skill into repeatable, professional-grade trading systems and workflows.",
    cover: { label: "Advanced AI Trading", edition: "First Edition", accent: "emerald" },
    currency: "USD",
    originalPrice: 120,
    offerPrice: 90,
    highlights: [
      "Design end-to-end institutional trading systems",
      "Integrate AI into analysis & execution — responsibly",
      "Engineer market-data & automation pipelines",
      "Build professional workflows that scale",
    ],
    stats: [
      { label: "Modules", value: "14" },
      { label: "Chapters", value: "60+" },
      { label: "System Blueprints", value: "18" },
    ],
    curriculum: [
      {
        title: "The Institutional Operating System",
        icon: "building-2",
        chapters: [
          {
            title: "Thinking Like an Institution",
            lessons: [
              "The desk workflow: research → thesis → execution → review",
              "Mandate, risk budget and edge decay",
              "Why process beats prediction",
            ],
          },
          {
            title: "Advanced Institutional Analysis",
            lessons: [
              "Multi-timeframe institutional bias",
              "Inter-market & correlation analysis",
              "Volatility regimes and positioning",
            ],
          },
        ],
      },
      {
        title: "Market Data Engineering",
        icon: "database",
        chapters: [
          {
            title: "Sourcing & Cleaning Market Data",
            lessons: [
              "Tick, order-book and OHLCV data explained",
              "Data hygiene, survivorship & look-ahead bias",
              "Building a reliable data pipeline",
            ],
          },
          {
            title: "Feature Engineering for Traders",
            lessons: [
              "Turning structure & liquidity into features",
              "Volatility, momentum and microstructure signals",
              "Labeling trades for evaluation",
            ],
          },
        ],
      },
      {
        title: "AI Integration for Trading",
        icon: "cpu",
        chapters: [
          {
            title: "AI as a Co-Analyst",
            lessons: [
              "Using LLMs to accelerate research & journaling",
              "Prompt frameworks for market analysis",
              "Guardrails: where AI helps and where it fails",
            ],
          },
          {
            title: "Model-Assisted Decision Making",
            lessons: [
              "Signal generation vs. signal confirmation",
              "Ensembles: combining rules with models",
              "Avoiding overfitting & data snooping",
            ],
          },
        ],
      },
      {
        title: "Execution & Automation",
        icon: "zap",
        chapters: [
          {
            title: "Execution Models",
            lessons: [
              "Order types, slippage and impact",
              "Smart execution & partial fills",
              "Latency, spread and cost modeling",
            ],
          },
          {
            title: "Professional Automation",
            lessons: [
              "From checklist to codified rules",
              "Building a semi-automated trading loop",
              "Fail-safes, kill-switches and monitoring",
            ],
          },
        ],
      },
      {
        title: "Trading Systems & Backtesting",
        icon: "line-chart",
        chapters: [
          {
            title: "System Design",
            lessons: [
              "Anatomy of a robust trading system",
              "Entry, exit, sizing and regime filters",
              "Combining discretionary & systematic edges",
            ],
          },
          {
            title: "Validation & Backtesting",
            lessons: [
              "Walk-forward analysis & out-of-sample testing",
              "Metrics that matter: Sharpe, expectancy, drawdown",
              "Stress-testing for regime change",
            ],
          },
        ],
      },
      {
        title: "Risk, Workflow & Mastery",
        icon: "shield-check",
        chapters: [
          {
            title: "Portfolio-Level Risk",
            lessons: [
              "Correlation, exposure and heat",
              "Dynamic position sizing",
              "Capital preservation as edge",
            ],
          },
          {
            title: "Professional Workflows",
            lessons: [
              "The daily / weekly operating rhythm",
              "Trade review & performance analytics",
              "Scaling from single trader to system",
            ],
          },
          {
            title: "Advanced Concepts & Case Studies",
            lessons: [
              "Full system builds, deconstructed",
              "Real institutional-style case studies",
              "Advanced exercises & professional checklists",
            ],
          },
        ],
      },
    ],
    includes: [
      "18 professional system blueprints",
      "AI prompt & workflow library",
      "Backtesting & evaluation templates",
      "Lifetime updates to the First Edition",
    ],
  },
];

export function getBook(id: string): Book | undefined {
  return books.find((b) => b.id === id);
}
