import type { Locale } from "@/i18n/config";

/**
 * UI string dictionaries for the storefront (EN / AR / TR).
 * Book content is localized separately in `books.ts`.
 */

const en = {
  nav: {
    links: {
      library: "Library",
      curriculum: "Curriculum",
      signals: "Signals",
      why: "Why Us",
      faq: "FAQ",
    },
    cta: "Get the Books",
    menu: "Toggle menu",
    language: "Language",
  },
  hero: {
    badgeUntil: "until",
    headline1: "Trade the way",
    headlineGold: "institutions",
    headline2: "actually do.",
    headlinePlain: "Trade the way institutions actually do.",
    subtitle:
      "A premium library of professional trading books — market structure, liquidity, order flow, SMC, ICT, Wyckoff and AI-driven institutional analysis. No hype. No indicators. Just the real logic that moves price.",
    ctaPrimary: "Explore the Library",
    ctaSecondary: "See the Signals",
    trust1: "Lifetime access & updates",
    trust2: "Institutional-grade curriculum",
    trust3: "Secure crypto checkout",
    from: "From",
    stats: {
      modules: "Core Modules",
      chapters: "Chapters",
      examples: "Chart Examples",
      books: "Flagship Books",
    },
  },
  ticker: { live: "Live Markets" },
  celebration: {
    title: "🎉 First Edition Celebration",
    subtitle: "Founding-price offer — locked until July 30",
    ends: "ends",
    endsIn: "Offer ends in",
    endedNotice:
      "The First Edition Celebration has ended — thank you to our founding readers. Books are now at their standard prices.",
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
  why: {
    eyebrow: "Why these books",
    title1: "Everything a serious trader needs —",
    titleGold: "nothing they don't.",
    description:
      "No signals-only shortcuts, no recycled indicator hype. Just a complete, professional education engineered to compound over a lifetime.",
    perks: [
      { title: "Institutional Concepts", desc: "Learn the framework desks and funds trade — structure, liquidity, order flow." },
      { title: "Professional Charts", desc: "Hundreds of clean, annotated charts that show, not just tell." },
      { title: "Case Studies", desc: "Full trade breakdowns from bias to entry to exit." },
      { title: "Exercises", desc: "Practice sets with worked solutions to build real skill." },
      { title: "Real Examples", desc: "Live-market examples across FX, crypto, indices and metals." },
      { title: "Risk Management", desc: "A complete system for sizing, R-multiples and drawdown control." },
      { title: "Psychology", desc: "Master fear, greed and impatience — the real edge." },
      { title: "AI Integration", desc: "Use AI as a co-analyst — the right way, at the right time." },
      { title: "Lifetime Knowledge", desc: "Timeless principles plus lifetime updates to every edition." },
    ],
  },
  telegram: {
    goingLive: "Going live",
    title1: "Exclusive",
    titleGold: "Telegram Signals",
    body: "Beginning {date}, we publish professional trading signals and trade ideas built on the exact framework taught in the books — full transparency, real risk management, zero noise.",
    cta: "Join Telegram",
    note: "Free preview channel now · VIP room opens {date}.",
    features: [
      { title: "Daily Analysis", desc: "Structured market breakdowns before every session." },
      { title: "Entry Levels", desc: "Precise, pre-planned entries with clear invalidation." },
      { title: "Stop Loss (SL)", desc: "Defined risk on every idea — no exceptions." },
      { title: "Take Profit (TP)", desc: "Layered targets mapped to real liquidity." },
      { title: "Market Reviews", desc: "End-of-day recaps and what to watch next." },
      { title: "VIP Community", desc: "A focused room of serious, like-minded traders." },
    ],
  },
  warning: {
    title: "Important Warning for Beginners",
    body1:
      "The AI Version of the books should never be your first learning source. Automation and AI amplify whatever skill you already have — including the gaps. Every beginner must first genuinely understand the fundamentals:",
    fundamentals: [
      "Technical Analysis",
      "Market Structure",
      "Price Action",
      "Risk Management",
      "Trading Psychology",
      "Institutional Concepts",
    ],
    body2:
      "Only after mastering these foundations should the AI Version be used — as a force multiplier, not a shortcut. Respect the order, and the tools will serve you. Skip it, and they will cost you.",
  },
  quote: {
    lead: "The greatest strategy in trading is",
    leadGold: "not an indicator.",
    leadTail: "It is mastering yourself.",
    body: "If you cannot control your emotions — your fear, greed and impatience — no strategy in the world will save you. Self-control is the greatest edge a trader can ever build.",
    attribution: "A veteran institutional trader",
  },
  testimonials: {
    eyebrow: "Trusted by traders",
    title1: "Results people can",
    titleGold: "feel.",
    description:
      "A snapshot of what serious traders say after putting the framework to work.",
    items: [
      { role: "Swing Trader · 3 yrs", quote: "Triple Analysis finally connected the dots for me. I stopped chasing indicators and started reading liquidity. My win-rate didn't just improve — my whole mindset did." },
      { role: "Prop Firm Funded", quote: "The risk management chapter alone paid for the book ten times over. This is the first material that reads like it was written by someone who actually trades size." },
      { role: "Quant-curious Trader", quote: "Advanced AI Trading is in a different league. The system blueprints and the AI workflow library changed how I research markets entirely. Worth every dollar." },
      { role: "Full-time FX", quote: "I've bought a lot of courses. Most are noise. This is the first library that respects your intelligence and your time. Clean, deep, and genuinely institutional." },
      { role: "Crypto & Indices", quote: "The case studies are gold. Watching a full trade broken down from HTF bias to the exact exit taught me more than a year of YouTube ever did." },
      { role: "Part-time, Growing", quote: "What sold me was the honesty — the warning about AI, the psychology focus. It's clear these authors care about you actually making it." },
    ],
  },
  faq: {
    eyebrow: "FAQ",
    title: "Answers, before you ask.",
    description:
      "Everything you need to know about the books, delivery, pricing and the signals.",
    items: [
      { q: "Are these books for beginners or advanced traders?", a: "Triple Analysis is built to take a motivated beginner to a professional level, step by step. Advanced AI Trading is for traders who already understand the fundamentals and want to industrialize their edge with systems and AI. Read the warning section — order matters." },
      { q: "What format are the books delivered in?", a: "High-resolution digital PDFs, optimized for both desktop and tablet. You get instant access after checkout, plus every future update to your edition at no extra cost." },
      { q: "How do I pay?", a: "Checkout is handled securely through crypto payments. Prices are shown in USD and converted at checkout. The moment payment confirms, your download is delivered — no waiting, no middlemen." },
      { q: "Is the First Edition price really going away?", a: "Yes. The founding-price offer is locked until July 30, 2026 at 23:59. When the countdown hits zero, discounts are removed automatically and the books return to their standard prices." },
      { q: "Do I need indicators or paid software to apply this?", a: "No. Everything is taught using pure price action and market structure on any standard charting platform." },
      { q: "When do the Telegram signals start?", a: "Professional signals and trade ideas begin publishing August 1st, 2026 — built on the exact framework taught in the books, with full entries, stop loss, take profit and risk notes." },
      { q: "Is this financial advice?", a: "No. These are educational materials. Trading involves substantial risk, and nothing here is a guarantee of profit. You are always responsible for your own decisions and risk." },
    ],
  },
  newsletter: {
    title: "Get the trader's edge in your inbox",
    description:
      "Occasional deep-dives on market structure, liquidity and psychology — plus early access to new editions and the signals launch. No spam, ever.",
    placeholder: "you@email.com",
    subscribe: "Subscribe",
    joining: "Joining…",
    success: "You're on the list. Welcome aboard.",
    agree: "By subscribing you agree to receive occasional emails. Unsubscribe anytime.",
    emailLabel: "Email address",
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
      library: "المكتبة",
      curriculum: "المنهج",
      signals: "التوصيات",
      why: "لماذا نحن",
      faq: "الأسئلة الشائعة",
    },
    cta: "احصل على الكتب",
    menu: "فتح القائمة",
    language: "اللغة",
  },
  hero: {
    badgeUntil: "حتى",
    headline1: "تداول بطريقة",
    headlineGold: "المؤسسات",
    headline2: "الحقيقية.",
    headlinePlain: "تداول بطريقة المؤسسات الحقيقية.",
    subtitle:
      "مكتبة فاخرة من كتب التداول الاحترافية — هيكل السوق، السيولة، تدفق الأوامر، مفاهيم SMC وICT ووايكوف، والتحليل المؤسسي المدعوم بالذكاء الاصطناعي. بلا مبالغة، بلا مؤشرات. فقط المنطق الحقيقي الذي يحرّك السعر.",
    ctaPrimary: "استكشف المكتبة",
    ctaSecondary: "شاهد التوصيات",
    trust1: "وصول وتحديثات مدى الحياة",
    trust2: "منهج بمستوى مؤسسي",
    trust3: "دفع آمن بالعملات الرقمية",
    from: "يبدأ من",
    stats: {
      modules: "وحدات أساسية",
      chapters: "فصول",
      examples: "أمثلة على الرسوم",
      books: "كتب رئيسية",
    },
  },
  ticker: { live: "أسواق مباشرة" },
  celebration: {
    title: "🎉 احتفال الإصدار الأول",
    subtitle: "عرض سعر التأسيس — ثابت حتى 30 يوليو",
    ends: "ينتهي",
    endsIn: "ينتهي العرض خلال",
    endedNotice:
      "انتهى احتفال الإصدار الأول — شكرًا لقرائنا المؤسسين. عادت الكتب الآن إلى أسعارها الأساسية.",
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
  why: {
    eyebrow: "لماذا هذه الكتب",
    title1: "كل ما يحتاجه المتداول الجاد —",
    titleGold: "ولا شيء زائد.",
    description:
      "لا اختصارات قائمة على التوصيات فقط، ولا ضجيج مؤشرات مكرّر. فقط تعليم احترافي كامل مصمم ليتراكم أثره مدى الحياة.",
    perks: [
      { title: "مفاهيم مؤسسية", desc: "تعلّم الإطار الذي تتداول به المكاتب والصناديق — الهيكل، السيولة، تدفق الأوامر." },
      { title: "رسوم احترافية", desc: "مئات الرسوم الواضحة والمشروحة التي تُري ولا تكتفي بالإخبار." },
      { title: "دراسات حالة", desc: "تحليلات كاملة لصفقات من التحيّز إلى الدخول إلى الخروج." },
      { title: "تمارين", desc: "مجموعات تدريبية مع حلول مشروحة لبناء مهارة حقيقية." },
      { title: "أمثلة واقعية", desc: "أمثلة من السوق الحي عبر الفوركس والعملات والمؤشرات والمعادن." },
      { title: "إدارة المخاطر", desc: "نظام كامل لتحديد الحجم ومضاعفات المخاطرة والتحكم في التراجع." },
      { title: "علم النفس", desc: "أتقِن الخوف والطمع ونفاد الصبر — الحافة الحقيقية." },
      { title: "دمج الذكاء الاصطناعي", desc: "استخدم الذكاء الاصطناعي كمحلّل مساعد — بالطريقة والوقت الصحيحين." },
      { title: "معرفة مدى الحياة", desc: "مبادئ خالدة مع تحديثات مدى الحياة لكل إصدار." },
    ],
  },
  telegram: {
    goingLive: "الإطلاق",
    title1: "حصري",
    titleGold: "توصيات تيليجرام",
    body: "ابتداءً من {date}، ننشر توصيات تداول احترافية وأفكار صفقات مبنية على الإطار نفسه الذي تعلّمه الكتب — شفافية كاملة، إدارة مخاطر حقيقية، بلا ضجيج.",
    cta: "انضم إلى تيليجرام",
    note: "قناة معاينة مجانية الآن · تُفتح غرفة VIP في {date}.",
    features: [
      { title: "تحليل يومي", desc: "تحليلات منظّمة للسوق قبل كل جلسة." },
      { title: "مستويات الدخول", desc: "دخول دقيق ومخطّط مسبقًا مع إبطال واضح." },
      { title: "وقف الخسارة (SL)", desc: "مخاطرة محددة في كل فكرة — بلا استثناء." },
      { title: "جني الأرباح (TP)", desc: "أهداف متدرجة مرتبطة بسيولة حقيقية." },
      { title: "مراجعات السوق", desc: "ملخّصات نهاية اليوم وما يجب مراقبته لاحقًا." },
      { title: "مجتمع VIP", desc: "غرفة مركّزة من المتداولين الجادين المتشابهين." },
    ],
  },
  warning: {
    title: "تحذير مهم للمبتدئين",
    body1:
      "لا ينبغي أبدًا أن تكون نسخة الذكاء الاصطناعي من الكتب مصدر تعلّمك الأول. الأتمتة والذكاء الاصطناعي يضخّمان مهارتك الحالية — بما في ذلك الثغرات. على كل مبتدئ أن يفهم الأساسيات فهمًا حقيقيًا أولًا:",
    fundamentals: [
      "التحليل الفني",
      "هيكل السوق",
      "حركة السعر",
      "إدارة المخاطر",
      "علم نفس التداول",
      "المفاهيم المؤسسية",
    ],
    body2:
      "فقط بعد إتقان هذه الأسس ينبغي استخدام نسخة الذكاء الاصطناعي — كمضاعِف للقوة، لا كاختصار. احترم الترتيب فتخدمك الأدوات، وتجاوزه فتكلّفك.",
  },
  quote: {
    lead: "أعظم استراتيجية في التداول",
    leadGold: "ليست مؤشرًا.",
    leadTail: "بل هي إتقان نفسك.",
    body: "إن لم تستطع التحكم في مشاعرك — خوفك وطمعك ونفاد صبرك — فلن تنقذك أي استراتيجية في العالم. ضبط النفس هو أعظم حافة يمكن للمتداول بناؤها.",
    attribution: "متداول مؤسسي مخضرم",
  },
  testimonials: {
    eyebrow: "موثوق من المتداولين",
    title1: "نتائج",
    titleGold: "يشعر بها الناس.",
    description: "لمحة عمّا يقوله المتداولون الجادون بعد تطبيق الإطار.",
    items: [
      { role: "متداول تأرجحي · 3 سنوات", quote: "ربط لي «التحليل الثلاثي» كل النقاط أخيرًا. توقفت عن مطاردة المؤشرات وبدأت أقرأ السيولة. لم يتحسّن معدل نجاحي فقط — بل عقليتي كلها." },
      { role: "ممول من شركة تمويل", quote: "فصل إدارة المخاطر وحده سدّد ثمن الكتاب عشر مرات. هذه أول مادة تُقرأ وكأن من كتبها يتداول بأحجام حقيقية." },
      { role: "متداول مهتم بالكمّي", quote: "«التداول المتقدم بالذكاء الاصطناعي» في مستوى مختلف. مخططات الأنظمة ومكتبة سير عمل الذكاء الاصطناعي غيّرت طريقة بحثي في الأسواق تمامًا." },
      { role: "فوركس بدوام كامل", quote: "اشتريت كثيرًا من الدورات، معظمها ضجيج. هذه أول مكتبة تحترم ذكاءك ووقتك. واضحة وعميقة ومؤسسية بحق." },
      { role: "عملات ومؤشرات", quote: "دراسات الحالة كنز. مشاهدة صفقة كاملة مُحلّلة من التحيّز إلى الخروج علّمتني أكثر من عام كامل من يوتيوب." },
      { role: "بدوام جزئي، في تطوّر", quote: "ما أقنعني هو الصدق — التحذير من الذكاء الاصطناعي والتركيز على علم النفس. واضح أن المؤلفين يهتمون بنجاحك فعلًا." },
    ],
  },
  faq: {
    eyebrow: "الأسئلة الشائعة",
    title: "إجابات، قبل أن تسأل.",
    description: "كل ما تحتاج معرفته عن الكتب والتسليم والأسعار والتوصيات.",
    items: [
      { q: "هل هذه الكتب للمبتدئين أم للمتقدمين؟", a: "«التحليل الثلاثي» مصمم لينقل المبتدئ المتحمّس إلى المستوى الاحترافي خطوة بخطوة. و«التداول المتقدم بالذكاء الاصطناعي» للمتداولين الذين أتقنوا الأساسيات ويريدون تصنيع حافتهم بالأنظمة والذكاء الاصطناعي. اقرأ قسم التحذير — الترتيب مهم." },
      { q: "بأي صيغة تُسلّم الكتب؟", a: "ملفات PDF رقمية عالية الدقة، محسّنة للحاسوب واللوحي. تحصل على وصول فوري بعد الدفع، إضافة إلى كل تحديث مستقبلي لإصدارك دون تكلفة إضافية." },
      { q: "كيف أدفع؟", a: "تتم عملية الدفع بأمان عبر العملات الرقمية. تُعرض الأسعار بالدولار وتُحوّل عند الدفع. لحظة تأكيد الدفع يصلك التنزيل — بلا انتظار ولا وسطاء." },
      { q: "هل سعر الإصدار الأول سيختفي فعلًا؟", a: "نعم. عرض سعر التأسيس ثابت حتى 30 يوليو 2026 الساعة 23:59. عند وصول العدّاد إلى الصفر تُزال الخصومات تلقائيًا وتعود الكتب إلى أسعارها الأساسية." },
      { q: "هل أحتاج مؤشرات أو برامج مدفوعة لتطبيق هذا؟", a: "لا. كل شيء يُدرّس باستخدام حركة السعر وهيكل السوق الصرف على أي منصة رسوم قياسية." },
      { q: "متى تبدأ توصيات تيليجرام؟", a: "تبدأ التوصيات الاحترافية وأفكار الصفقات بالنشر في 1 أغسطس 2026 — مبنية على الإطار نفسه الذي تعلّمه الكتب، مع دخول كامل ووقف خسارة وجني أرباح وملاحظات مخاطرة." },
      { q: "هل هذه نصيحة مالية؟", a: "لا. هذه مواد تعليمية. ينطوي التداول على مخاطر كبيرة، ولا شيء هنا ضمان للربح. أنت دائمًا مسؤول عن قراراتك ومخاطرك." },
    ],
  },
  newsletter: {
    title: "احصل على حافة المتداول في بريدك",
    description:
      "تحليلات معمّقة من حين لآخر حول هيكل السوق والسيولة وعلم النفس — إضافة إلى وصول مبكر للإصدارات الجديدة وإطلاق التوصيات. بلا رسائل مزعجة أبدًا.",
    placeholder: "you@email.com",
    subscribe: "اشترك",
    joining: "جارٍ الاشتراك…",
    success: "أنت الآن في القائمة. أهلًا بك.",
    agree: "بالاشتراك فإنك توافق على تلقّي رسائل من حين لآخر. يمكنك إلغاء الاشتراك في أي وقت.",
    emailLabel: "البريد الإلكتروني",
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
      library: "Kütüphane",
      curriculum: "Müfredat",
      signals: "Sinyaller",
      why: "Neden Biz",
      faq: "SSS",
    },
    cta: "Kitapları Al",
    menu: "Menüyü aç",
    language: "Dil",
  },
  hero: {
    badgeUntil: "bitiş",
    headline1: "Kurumların",
    headlineGold: "gerçekte",
    headline2: "işlem yaptığı gibi işlem yap.",
    headlinePlain: "Kurumların gerçekte işlem yaptığı gibi işlem yap.",
    subtitle:
      "Profesyonel işlem kitaplarından oluşan seçkin bir kütüphane — piyasa yapısı, likidite, emir akışı, SMC, ICT, Wyckoff ve yapay zekâ destekli kurumsal analiz. Abartı yok. Gösterge yok. Sadece fiyatı hareket ettiren gerçek mantık.",
    ctaPrimary: "Kütüphaneyi Keşfet",
    ctaSecondary: "Sinyalleri Gör",
    trust1: "Ömür boyu erişim ve güncelleme",
    trust2: "Kurumsal düzeyde müfredat",
    trust3: "Güvenli kripto ödeme",
    from: "Başlangıç",
    stats: {
      modules: "Temel Modül",
      chapters: "Bölüm",
      examples: "Grafik Örneği",
      books: "Amiral Kitap",
    },
  },
  ticker: { live: "Canlı Piyasalar" },
  celebration: {
    title: "🎉 İlk Baskı Kutlaması",
    subtitle: "Kuruluş fiyatı teklifi — 30 Temmuz'a kadar sabit",
    ends: "bitiş",
    endsIn: "Teklifin bitişine",
    endedNotice:
      "İlk Baskı Kutlaması sona erdi — kurucu okurlarımıza teşekkürler. Kitaplar artık standart fiyatlarında.",
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
  why: {
    eyebrow: "Neden bu kitaplar",
    title1: "Ciddi bir yatırımcının ihtiyacı olan her şey —",
    titleGold: "gereksiz hiçbir şey yok.",
    description:
      "Yalnızca sinyale dayalı kısayollar yok, tekrar edilen gösterge gürültüsü yok. Sadece bir ömür boyu katlanarak büyüyecek eksiksiz, profesyonel bir eğitim.",
    perks: [
      { title: "Kurumsal Kavramlar", desc: "Masaların ve fonların işlem yaptığı çerçeveyi öğren — yapı, likidite, emir akışı." },
      { title: "Profesyonel Grafikler", desc: "Sadece anlatmayan, gösteren yüzlerce temiz, açıklamalı grafik." },
      { title: "Vaka Çalışmaları", desc: "Ön yargıdan girişe ve çıkışa tam işlem çözümlemeleri." },
      { title: "Alıştırmalar", desc: "Gerçek beceri kazandıran çözümlü alıştırma setleri." },
      { title: "Gerçek Örnekler", desc: "Forex, kripto, endeksler ve metallerde canlı piyasa örnekleri." },
      { title: "Risk Yönetimi", desc: "Pozisyon boyutu, R-katları ve düşüş kontrolü için eksiksiz bir sistem." },
      { title: "Psikoloji", desc: "Korku, açgözlülük ve sabırsızlığı yönet — gerçek avantaj." },
      { title: "Yapay Zekâ Entegrasyonu", desc: "Yapay zekâyı yardımcı analist olarak kullan — doğru şekilde, doğru zamanda." },
      { title: "Ömür Boyu Bilgi", desc: "Zamansız ilkeler ve her baskı için ömür boyu güncelleme." },
    ],
  },
  telegram: {
    goingLive: "Yayında",
    title1: "Özel",
    titleGold: "Telegram Sinyalleri",
    body: "{date} tarihinden itibaren, kitaplarda öğretilen çerçeveye dayalı profesyonel işlem sinyalleri ve işlem fikirleri yayınlıyoruz — tam şeffaflık, gerçek risk yönetimi, sıfır gürültü.",
    cta: "Telegram'a Katıl",
    note: "Şimdi ücretsiz önizleme kanalı · VIP oda {date} tarihinde açılıyor.",
    features: [
      { title: "Günlük Analiz", desc: "Her seanstan önce yapılandırılmış piyasa çözümlemeleri." },
      { title: "Giriş Seviyeleri", desc: "Net geçersizlik ile önceden planlanmış kesin girişler." },
      { title: "Zarar Durdur (SL)", desc: "Her fikirde tanımlı risk — istisnasız." },
      { title: "Kâr Al (TP)", desc: "Gerçek likiditeye bağlanmış kademeli hedefler." },
      { title: "Piyasa İncelemeleri", desc: "Gün sonu özetleri ve sırada izlenecekler." },
      { title: "VIP Topluluk", desc: "Ciddi ve benzer düşünen yatırımcılardan oluşan odaklı bir oda." },
    ],
  },
  warning: {
    title: "Yeni Başlayanlar İçin Önemli Uyarı",
    body1:
      "Kitapların Yapay Zekâ Sürümü asla ilk öğrenme kaynağın olmamalı. Otomasyon ve yapay zekâ, mevcut becerini — boşluklar dâhil — büyütür. Her yeni başlayan önce temelleri gerçekten anlamalı:",
    fundamentals: [
      "Teknik Analiz",
      "Piyasa Yapısı",
      "Fiyat Hareketi",
      "Risk Yönetimi",
      "İşlem Psikolojisi",
      "Kurumsal Kavramlar",
    ],
    body2:
      "Bu temelleri ustalıkla öğrendikten sonra ancak Yapay Zekâ Sürümü kullanılmalı — kısayol olarak değil, güç çarpanı olarak. Sıraya saygı gösterirsen araçlar sana hizmet eder; atlarsan sana pahalıya mal olur.",
  },
  quote: {
    lead: "İşlemdeki en büyük strateji",
    leadGold: "bir gösterge değildir.",
    leadTail: "Kendine hâkim olmaktır.",
    body: "Duygularını — korkunu, açgözlülüğünü ve sabırsızlığını — kontrol edemiyorsan, dünyadaki hiçbir strateji seni kurtaramaz. Öz denetim, bir yatırımcının inşa edebileceği en büyük avantajdır.",
    attribution: "Kıdemli bir kurumsal yatırımcı",
  },
  testimonials: {
    eyebrow: "Yatırımcıların güvendiği",
    title1: "İnsanların",
    titleGold: "hissedebildiği sonuçlar.",
    description:
      "Çerçeveyi uygulamaya koyduktan sonra ciddi yatırımcıların söylediklerinden bir kesit.",
    items: [
      { role: "Swing Yatırımcı · 3 yıl", quote: "Triple Analysis nihayet noktaları birleştirdi. Gösterge kovalamayı bırakıp likidite okumaya başladım. Sadece kazanma oranım değil — tüm zihniyetim değişti." },
      { role: "Prop Firma Fonlu", quote: "Tek başına risk yönetimi bölümü kitabın parasını on kat çıkardı. Bu, gerçekten büyük hacimle işlem yapan biri tarafından yazıldığı okunan ilk materyal." },
      { role: "Kantitatif Meraklısı", quote: "Advanced AI Trading bambaşka bir seviyede. Sistem şablonları ve yapay zekâ iş akışı kütüphanesi piyasaları araştırma şeklimi tamamen değiştirdi." },
      { role: "Tam Zamanlı Forex", quote: "Çok kurs aldım, çoğu gürültü. Bu, zekâna ve zamanına saygı duyan ilk kütüphane. Temiz, derin ve gerçekten kurumsal." },
      { role: "Kripto ve Endeksler", quote: "Vaka çalışmaları altın değerinde. Tam bir işlemin baştan sona çözümlenmesini izlemek bana bir yıllık YouTube'dan fazlasını öğretti." },
      { role: "Yarı Zamanlı, Gelişen", quote: "Beni ikna eden dürüstlüktü — yapay zekâ uyarısı, psikoloji vurgusu. Yazarların gerçekten başarmanı önemsediği belli." },
    ],
  },
  faq: {
    eyebrow: "SSS",
    title: "Sormadan önce, cevaplar.",
    description:
      "Kitaplar, teslimat, fiyatlandırma ve sinyaller hakkında bilmen gereken her şey.",
    items: [
      { q: "Bu kitaplar yeni başlayanlar için mi yoksa ileri seviye için mi?", a: "Triple Analysis, istekli bir başlangıç seviyesindekini adım adım profesyonel seviyeye taşımak için tasarlandı. Advanced AI Trading ise temelleri anlayan ve avantajını sistemler ve yapay zekâ ile sanayileştirmek isteyen yatırımcılar içindir. Uyarı bölümünü oku — sıra önemlidir." },
      { q: "Kitaplar hangi formatta teslim edilir?", a: "Masaüstü ve tablet için optimize edilmiş yüksek çözünürlüklü dijital PDF'ler. Ödemeden sonra anında erişim ve baskının gelecekteki tüm güncellemelerini ek ücret olmadan alırsın." },
      { q: "Nasıl ödeme yaparım?", a: "Ödeme kripto ile güvenli şekilde yapılır. Fiyatlar USD gösterilir ve ödemede dönüştürülür. Ödeme onaylandığı an indirmen teslim edilir — bekleme yok, aracı yok." },
      { q: "İlk Baskı fiyatı gerçekten kalkacak mı?", a: "Evet. Kuruluş fiyatı teklifi 30 Temmuz 2026 saat 23:59'a kadar sabittir. Geri sayım sıfıra ulaştığında indirimler otomatik kaldırılır ve kitaplar standart fiyatlarına döner." },
      { q: "Bunu uygulamak için gösterge veya ücretli yazılım gerekli mi?", a: "Hayır. Her şey, herhangi bir standart grafik platformunda saf fiyat hareketi ve piyasa yapısı kullanılarak öğretilir." },
      { q: "Telegram sinyalleri ne zaman başlıyor?", a: "Profesyonel sinyaller ve işlem fikirleri 1 Ağustos 2026'da yayınlanmaya başlar — kitaplarda öğretilen çerçeveye dayalı, tam giriş, zarar durdur, kâr al ve risk notlarıyla." },
      { q: "Bu finansal tavsiye mi?", a: "Hayır. Bunlar eğitim materyalleridir. İşlem yapmak önemli risk taşır ve buradaki hiçbir şey kâr garantisi değildir. Kararlarından ve riskinden her zaman sen sorumlusun." },
    ],
  },
  newsletter: {
    title: "Yatırımcı avantajını gelen kutuna al",
    description:
      "Piyasa yapısı, likidite ve psikoloji üzerine ara sıra derinlemesine yazılar — ayrıca yeni baskılara ve sinyal lansmanına erken erişim. Asla spam yok.",
    placeholder: "sen@email.com",
    subscribe: "Abone Ol",
    joining: "Katılıyor…",
    success: "Listedesin. Aramıza hoş geldin.",
    agree: "Abone olarak ara sıra e-posta almayı kabul edersin. İstediğin zaman çıkabilirsin.",
    emailLabel: "E-posta adresi",
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
