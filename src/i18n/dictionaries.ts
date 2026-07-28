import type { Locale } from "@/i18n/config";

/**
 * UI strings for the trading library and shared site chrome (EN / AR / TR).
 * Book content is localized separately in `books.ts`.
 *
 * This file used to carry the whole homepage. When the site became an AI
 * automation marketplace, the sections it served — the hero, the ticker,
 * the celebration banner, the Telegram signals block, the risk warning,
 * the trading quote and the testimonials wall — were removed, and their
 * copy went with them. What remains is the book storefront (`store`,
 * `buy`, `countdown`), the nav labels and the footer.
 *
 * The marketplace's own copy lives in `marketplace.ts`.
 */

const en = {
  nav: {
    links: {
      library: "Trading Books",
      automation: "AI Systems",
      how: "How it works",
      standard: "The standard",
      faq: "FAQ",
    },
    cta: "Browse AI Systems",
    menu: "Toggle menu",
    language: "Language",
  },
  countdown: {
    days: "Days",
    hours: "Hours",
    minutes: "Minutes",
    seconds: "Seconds",
    ended: "Offer has ended.",
    endedRestored: "Original prices have been restored.",
  },
  store: {
    eyebrow: "The Library",
    title1: "Two books. One institutional",
    titleGold: "edge.",
    description:
      "Each title is a complete, self-contained education — designed to take you from reading price like a professional to building your own trading systems.",
    book: "Book",
    save: "Save",
    inside: "Inside the Book",
    insideMeta: "modules · {chapters} chapters · full curriculum",
    includes: "Every copy includes",
  },
  buy: {
    now: "Buy Now",
    loading: "Opening secure checkout…",
    secure: "Secure crypto checkout · instant delivery",
    unavailable: "Checkout opens soon — payment link is being finalized.",
  },
  footer: {
    tagline:
      "Institutional-grade trading books and signals for traders who are serious about mastering the markets — and themselves.",
    groups: {
      library: "Library",
      community: "Community",
    },
    links: {
      whyBuy: "Why Buy",
      faq: "FAQ",
      telegramSignals: "Telegram Signals",
      newsletter: "Newsletter",
      testimonials: "Testimonials",
    },
    disclaimerLabel: "Risk disclaimer:",
    disclaimer:
      "Trading financial markets carries substantial risk and is not suitable for every investor. The content sold and published by {name} is educational in nature and does not constitute financial, investment or trading advice. Past performance and examples are not indicative of future results. You are solely responsible for your own trading decisions and any resulting profit or loss. Never risk capital you cannot afford to lose.",
    rights: "All rights reserved.",
    terms: "Terms",
    privacy: "Privacy",
    refund: "Refund Policy",
  },
};

export type Dictionary = typeof en;

const ar: Dictionary = {
  nav: {
    links: {
      library: "كتب التداول",
      automation: "أنظمة الذكاء",
      how: "كيف يعمل",
      standard: "المعيار",
      faq: "الأسئلة الشائعة",
    },
    cta: "تصفّح الأنظمة",
    menu: "فتح القائمة",
    language: "اللغة",
  },
  countdown: {
    days: "أيام",
    hours: "ساعات",
    minutes: "دقائق",
    seconds: "ثوانٍ",
    ended: "انتهى العرض.",
    endedRestored: "تمت استعادة الأسعار الأصلية.",
  },
  store: {
    eyebrow: "المكتبة",
    title1: "كتابان. حافة",
    titleGold: "مؤسسية واحدة.",
    description:
      "كل كتاب هو تعليم كامل ومتكامل — مصمم لينقلك من قراءة السعر باحترافية إلى بناء أنظمة التداول الخاصة بك.",
    book: "الكتاب",
    save: "وفّر",
    inside: "داخل الكتاب",
    insideMeta: "وحدات · {chapters} فصلًا · منهج كامل",
    includes: "كل نسخة تتضمن",
  },
  buy: {
    now: "اشترِ الآن",
    loading: "جارٍ فتح الدفع الآمن…",
    secure: "دفع آمن بالعملات الرقمية · تسليم فوري",
    unavailable: "الدفع يُفتح قريبًا — يجري تجهيز رابط الدفع.",
  },
  footer: {
    tagline:
      "كتب وتوصيات تداول بمستوى مؤسسي للمتداولين الجادين في إتقان الأسواق — وأنفسهم.",
    groups: { library: "المكتبة", community: "المجتمع" },
    links: {
      whyBuy: "لماذا تشتري",
      faq: "الأسئلة الشائعة",
      telegramSignals: "توصيات تيليجرام",
      newsletter: "النشرة البريدية",
      testimonials: "آراء العملاء",
    },
    disclaimerLabel: "إخلاء مسؤولية المخاطر:",
    disclaimer:
      "ينطوي تداول الأسواق المالية على مخاطر كبيرة وقد لا يناسب كل مستثمر. المحتوى الذي تبيعه وتنشره {name} تعليمي بطبيعته ولا يشكّل نصيحة مالية أو استثمارية أو تداولية. الأداء والأمثلة السابقة ليست مؤشرًا على نتائج مستقبلية. أنت وحدك المسؤول عن قرارات تداولك وأي ربح أو خسارة تنتج عنها. لا تخاطر أبدًا برأس مال لا يمكنك تحمّل خسارته.",
    rights: "جميع الحقوق محفوظة.",
    terms: "الشروط",
    privacy: "الخصوصية",
    refund: "سياسة الاسترداد",
  },
};

const tr: Dictionary = {
  nav: {
    links: {
      library: "Trading Kitapları",
      automation: "AI Sistemleri",
      how: "Nasıl çalışır",
      standard: "Standart",
      faq: "SSS",
    },
    cta: "AI Sistemlerine Göz At",
    menu: "Menüyü aç",
    language: "Dil",
  },
  countdown: {
    days: "Gün",
    hours: "Saat",
    minutes: "Dakika",
    seconds: "Saniye",
    ended: "Teklif sona erdi.",
    endedRestored: "Orijinal fiyatlar geri yüklendi.",
  },
  store: {
    eyebrow: "Kütüphane",
    title1: "İki kitap. Tek kurumsal",
    titleGold: "avantaj.",
    description:
      "Her kitap eksiksiz, kendi içinde bütün bir eğitimdir — fiyatı bir profesyonel gibi okumaktan kendi işlem sistemlerini kurmaya kadar götürür.",
    book: "Kitap",
    save: "Kazan",
    inside: "Kitabın İçinde",
    insideMeta: "modül · {chapters} bölüm · tam müfredat",
    includes: "Her kopya şunları içerir",
  },
  buy: {
    now: "Şimdi Al",
    loading: "Güvenli ödeme açılıyor…",
    secure: "Güvenli kripto ödeme · anında teslim",
    unavailable: "Ödeme yakında açılıyor — ödeme bağlantısı hazırlanıyor.",
  },
  footer: {
    tagline:
      "Piyasalara — ve kendilerine — hâkim olma konusunda ciddi olan yatırımcılar için kurumsal düzeyde işlem kitapları ve sinyalleri.",
    groups: { library: "Kütüphane", community: "Topluluk" },
    links: {
      whyBuy: "Neden Al",
      faq: "SSS",
      telegramSignals: "Telegram Sinyalleri",
      newsletter: "Bülten",
      testimonials: "Yorumlar",
    },
    disclaimerLabel: "Risk uyarısı:",
    disclaimer:
      "Finansal piyasalarda işlem yapmak önemli risk taşır ve her yatırımcı için uygun değildir. {name} tarafından satılan ve yayınlanan içerik doğası gereği eğitseldir ve finansal, yatırım veya işlem tavsiyesi oluşturmaz. Geçmiş performans ve örnekler gelecekteki sonuçların göstergesi değildir. İşlem kararlarından ve bunlardan doğan kâr veya zarardan yalnızca sen sorumlusun. Asla kaybetmeyi göze alamayacağın sermayeyle risk alma.",
    rights: "Tüm hakları saklıdır.",
    terms: "Şartlar",
    privacy: "Gizlilik",
    refund: "İade Politikası",
  },
};

const dictionaries: Record<Locale, Dictionary> = { en, ar, tr };

export function getDictionary(locale: Locale): Dictionary {
  return dictionaries[locale] ?? en;
}
