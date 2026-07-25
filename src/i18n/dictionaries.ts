import type { Locale } from "@/i18n/config";

/**
 * UI string dictionaries for the storefront (EN / AR / TR).
 * Book content is localized separately in `books.ts`.
 */

const en = {
  nav: {
    links: {
      library: "Courses",
      curriculum: "Categories",
      signals: "Support",
      why: "Why E-tqan",
      faq: "FAQ",
    },
    cta: "Browse Courses",
    menu: "Toggle menu",
    language: "Language",
  },
  hero: {
    badgeUntil: "until",
    headline1: "Learn the skills that",
    headlineGold: "actually",
    headline2: "pay.",
    headlinePlain: "Learn the skills that actually pay.",
    subtitle:
      "A premium digital library of practical, trilingual courses — programming, AI, web, design, productivity and trading. Beautifully written, delivered instantly in English, العربية and Türkçe.",
    ctaPrimary: "Explore Courses",
    ctaSecondary: "View Bundles",
    trust1: "Lifetime access & updates",
    trust2: "Trilingual · EN · AR · TR",
    trust3: "Secure crypto checkout",
    from: "From",
    stats: {
      modules: "Courses",
      chapters: "Categories",
      examples: "Languages",
      books: "Bundles",
    },
  },
  ticker: { live: "Trusted by learners worldwide" },
  celebration: {
    title: "🎉 Launch Celebration",
    subtitle: "Founding-price offer — locked until July 30",
    ends: "ends",
    endsIn: "Offer ends in",
    endedNotice:
      "The launch celebration has ended — thank you to our founding learners. Courses are now at their standard prices.",
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
    eyebrow: "Trading Track",
    title1: "Master the markets, the",
    titleGold: "institutional way.",
    description:
      "Our flagship trading library — a complete education in market structure, liquidity and order flow, plus AI-driven institutional analysis. One of many tracks in the E-tqan library.",
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
    eyebrow: "Why E-tqan",
    title1: "Real skills, taught properly —",
    titleGold: "nothing wasted.",
    description:
      "No fluff, no recycled tutorials. Every course is original, modern and built to be used — with projects, exercises and real-world examples that turn knowledge into ability.",
    perks: [
      { title: "Trilingual", desc: "Every course in English, العربية and Türkçe — learn in the language you think in." },
      { title: "Practical Projects", desc: "Build real things. Each course ends in a project you can show off." },
      { title: "Modern Content", desc: "Rewritten for 2026 — current tools, current best practices, no outdated advice." },
      { title: "Beautifully Designed", desc: "Premium, readable books with clean typography, diagrams and highlighted code." },
      { title: "Instant Delivery", desc: "Pay and download in seconds — no waiting, no accounts, no friction." },
      { title: "Beginner-Friendly", desc: "Clear explanations that assume nothing and build real understanding, step by step." },
      { title: "Exercises & Quizzes", desc: "Practice sets, checklists and quizzes so learning actually sticks." },
      { title: "Lifetime Updates", desc: "Buy once, keep every future update to your edition at no extra cost." },
      { title: "Secure Checkout", desc: "Private, encrypted delivery and secure crypto payments — your purchase is yours." },
    ],
  },
  telegram: {
    goingLive: "Support",
    title1: "Questions? We're",
    titleGold: "here to help",
    body: "Reach us any time on Telegram for help with your purchase, downloads, or choosing the right course. Real support from real people — no bots, no runaround.",
    cta: "Message us on Telegram",
    note: "Support handle: @Ahm_t_AHZ01 — we usually reply fast.",
    features: [
      { title: "Purchase Help", desc: "Trouble at checkout or with a download? We'll sort it out." },
      { title: "Course Guidance", desc: "Not sure where to start? We'll point you to the right track." },
      { title: "Fast Replies", desc: "A real person, usually within hours." },
      { title: "Bundle Advice", desc: "We'll help you pick the bundle that fits your goals and budget." },
      { title: "Feedback Welcome", desc: "Spotted something? Your feedback shapes the next edition." },
      { title: "Friendly & Direct", desc: "Clear answers, no scripts, no upsells." },
    ],
  },
  warning: {
    title: "How to Get the Most From These Courses",
    body1:
      "Skills compound. To get the most from the E-tqan library, learn in a sensible order and actually build as you go. A strong foundation makes everything after it easier:",
    fundamentals: [
      "Start with fundamentals",
      "Type the examples yourself",
      "Do the exercises",
      "Build the projects",
      "Review and repeat",
      "Then go advanced",
    ],
    body2:
      "Knowledge becomes skill only through practice. Read actively, build relentlessly, and revisit what you learn. Respect the order, and each course multiplies the value of the next.",
  },
  quote: {
    lead: "The best investment you can make is",
    leadGold: "in yourself.",
    leadTail: "Skills compound for life.",
    body: "Tools change, frameworks come and go, but the ability to learn and build never depreciates. Master the fundamentals, keep shipping, and your skills will pay you back for the rest of your life.",
    attribution: "The E-tqan philosophy",
  },
  testimonials: {
    eyebrow: "Loved by learners",
    title1: "Results people can",
    titleGold: "feel.",
    description:
      "A snapshot of what learners say after working through the E-tqan library.",
    items: [
      { role: "Self-taught Developer", quote: "The Python course finally made it click. Clear, modern, and every chapter ends with something to build. I went from copying tutorials to writing my own projects." },
      { role: "Career Switcher", quote: "Having every course in Arabic made all the difference — I could focus on learning instead of translating. The design and examples feel genuinely premium." },
      { role: "Student · CS", quote: "The exercises and quizzes are what set these apart. I actually remember what I learned because I practiced it. Worth far more than the price." },
      { role: "Freelancer", quote: "Bought the Future Skills bundle to level up my client work. The web and AI courses paid for themselves on my very next project." },
      { role: "Designer learning to code", quote: "Beginner-friendly without being dumbed down. The explanations assume nothing but still respect your intelligence. Exactly what I needed." },
      { role: "Lifelong Learner", quote: "Instant download, beautiful PDFs, real projects. This is how digital courses should be done. I've already bought three." },
    ],
  },
  faq: {
    eyebrow: "FAQ",
    title: "Answers, before you ask.",
    description:
      "Everything you need to know about the courses, delivery, languages and pricing.",
    items: [
      { q: "What do I actually get?", a: "Premium, professionally designed digital books (PDF) for each course — original content with diagrams, code, exercises, quizzes and projects. Each course is delivered in English, Arabic and Turkish, so you can learn in the language you prefer." },
      { q: "What format are the courses in, and what languages?", a: "High-resolution digital PDFs, optimized for desktop and tablet, with clickable bookmarks and highlighted code. Every course ships trilingual — English, العربية and Türkçe — in one download." },
      { q: "How do I pay and receive my course?", a: "Checkout is handled securely via crypto payments. Prices are in USD. The moment payment confirms, your private download is delivered automatically — no waiting, no accounts, no middlemen." },
      { q: "Are these for beginners?", a: "Most courses start from zero and build to a real, usable skill, with a project at the end. A few (like Advanced AI Trading) are for those who already know the basics. Each course clearly states its level." },
      { q: "What are bundles?", a: "Curated collections of courses at a big discount — like the Programming Languages bundle or the Gold Master Library with everything. If you plan to take several courses, a bundle is the best value." },
      { q: "Is the launch price really going away?", a: "Yes. The founding-price offer is locked until July 30, 2026 at 23:59. When the countdown hits zero, discounts are removed automatically and prices return to standard." },
      { q: "Can I get help if I need it?", a: "Absolutely. Reach us any time on Telegram at @Ahm_t_AHZ01 for help with your purchase, downloads, or choosing the right course." },
    ],
  },
  newsletter: {
    title: "New courses & offers in your inbox",
    description:
      "Occasional updates on new courses, bundles and learning tips — plus early access to launches and discounts. No spam, ever.",
    placeholder: "you@email.com",
    subscribe: "Subscribe",
    joining: "Joining…",
    success: "You're on the list. Welcome aboard.",
    agree: "By subscribing you agree to receive occasional emails. Unsubscribe anytime.",
    emailLabel: "Email address",
  },
  footer: {
    tagline:
      "A premium, trilingual digital library for people serious about learning real, practical skills — and putting them to work.",
    groups: {
      library: "Library",
      community: "Company",
    },
    links: {
      whyBuy: "Why E-tqan",
      faq: "FAQ",
      telegramSignals: "Support",
      newsletter: "Newsletter",
      testimonials: "Reviews",
    },
    disclaimerLabel: "Note:",
    disclaimer:
      "All content sold and published by {name} is original educational material for learning purposes. Course names and topics are provided for education only. By purchasing you agree that digital products are non-refundable once downloaded, except as required by law. Learn actively, build often, and enjoy.",
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
      library: "الدورات",
      curriculum: "التصنيفات",
      signals: "الدعم",
      why: "لماذا E-tqan",
      faq: "الأسئلة الشائعة",
    },
    cta: "تصفّح الدورات",
    menu: "فتح القائمة",
    language: "اللغة",
  },
  hero: {
    badgeUntil: "حتى",
    headline1: "تعلّم المهارات التي",
    headlineGold: "تُدِرّ",
    headline2: "دخلًا حقيقيًا.",
    headlinePlain: "تعلّم المهارات التي تُدِرّ دخلًا حقيقيًا.",
    subtitle:
      "مكتبة رقمية مميّزة من دورات عملية ثلاثية اللغة — برمجة، ذكاء اصطناعي، ويب، تصميم، إنتاجية وتداول. مكتوبة بإتقان، وتصلك فورًا بالإنجليزية والعربية والتركية.",
    ctaPrimary: "استكشف الدورات",
    ctaSecondary: "شاهد الباقات",
    trust1: "وصول وتحديثات مدى الحياة",
    trust2: "ثلاثية اللغة · EN · AR · TR",
    trust3: "دفع آمن بالعملات الرقمية",
    from: "يبدأ من",
    stats: {
      modules: "دورات",
      chapters: "تصنيفات",
      examples: "لغات",
      books: "باقات",
    },
  },
  ticker: { live: "موثوقة من المتعلّمين حول العالم" },
  celebration: {
    title: "🎉 احتفال الإطلاق",
    subtitle: "عرض سعر التأسيس — ثابت حتى 30 يوليو",
    ends: "ينتهي",
    endsIn: "ينتهي العرض خلال",
    endedNotice:
      "انتهى احتفال الإطلاق — شكرًا لمتعلّمينا المؤسسين. عادت الدورات الآن إلى أسعارها الأساسية.",
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
    eyebrow: "مسار التداول",
    title1: "أتقِن الأسواق بطريقة",
    titleGold: "المؤسسات.",
    description:
      "مكتبتنا الرئيسية للتداول — تعليم كامل في هيكل السوق والسيولة وتدفق الأوامر، مع التحليل المؤسسي المدعوم بالذكاء الاصطناعي. أحد مسارات عديدة في مكتبة E-tqan.",
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
    eyebrow: "لماذا E-tqan",
    title1: "مهارات حقيقية، تُعلَّم كما يجب —",
    titleGold: "بلا حشو.",
    description:
      "لا حشو ولا دروس مكرّرة. كل دورة أصلية وحديثة ومصمّمة لتُستخدَم — بمشاريع وتمارين وأمثلة واقعية تحوّل المعرفة إلى قدرة.",
    perks: [
      { title: "ثلاثية اللغة", desc: "كل دورة بالإنجليزية والعربية والتركية — تعلّم باللغة التي تفكّر بها." },
      { title: "مشاريع عملية", desc: "ابنِ أشياء حقيقية. كل دورة تنتهي بمشروع تفخر بعرضه." },
      { title: "محتوى حديث", desc: "أُعيدت كتابته لعام 2026 — أدوات وممارسات حالية، بلا نصائح قديمة." },
      { title: "تصميم أنيق", desc: "كتب مميّزة سهلة القراءة بخطوط نظيفة ورسوم وأكواد ملوّنة." },
      { title: "تسليم فوري", desc: "ادفع ونزّل خلال ثوانٍ — بلا انتظار ولا حسابات ولا تعقيد." },
      { title: "مناسبة للمبتدئين", desc: "شرح واضح لا يفترض معرفة سابقة ويبني فهمًا حقيقيًا خطوة بخطوة." },
      { title: "تمارين واختبارات", desc: "مجموعات تدريب وقوائم تحقّق واختبارات ليثبت التعلّم فعلًا." },
      { title: "تحديثات مدى الحياة", desc: "اشترِ مرة واحصل على كل تحديث مستقبلي لإصدارك دون تكلفة." },
      { title: "دفع آمن", desc: "تسليم خاص مشفّر ودفع آمن بالعملات الرقمية — مشتراك ملكك." },
    ],
  },
  telegram: {
    goingLive: "الدعم",
    title1: "لديك سؤال؟ نحن",
    titleGold: "هنا لمساعدتك",
    body: "تواصل معنا في أي وقت عبر تيليجرام للمساعدة في الشراء أو التنزيل أو اختيار الدورة المناسبة. دعم حقيقي من أشخاص حقيقيين — بلا روبوتات ولا لفّ ودوران.",
    cta: "راسِلنا على تيليجرام",
    note: "حساب الدعم: @Ahm_t_AHZ01 — نردّ عادةً بسرعة.",
    features: [
      { title: "مساعدة الشراء", desc: "مشكلة في الدفع أو التنزيل؟ سنحلّها لك." },
      { title: "إرشاد الدورات", desc: "لا تعرف من أين تبدأ؟ سنوجّهك للمسار الصحيح." },
      { title: "ردود سريعة", desc: "شخص حقيقي، عادةً خلال ساعات." },
      { title: "نصيحة الباقات", desc: "سنساعدك في اختيار الباقة التي تناسب أهدافك وميزانيتك." },
      { title: "ملاحظاتك مرحّب بها", desc: "لاحظت شيئًا؟ ملاحظاتك تصنع الإصدار التالي." },
      { title: "ودود ومباشر", desc: "إجابات واضحة، بلا نصوص جاهزة ولا بيع إضافي." },
    ],
  },
  warning: {
    title: "كيف تحقّق أقصى استفادة من هذه الدورات",
    body1:
      "المهارات تتراكم. لتحقيق أقصى استفادة من مكتبة E-tqan، تعلّم بترتيب منطقي وابنِ فعليًا وأنت تتقدّم. الأساس المتين يجعل كل ما بعده أسهل:",
    fundamentals: [
      "ابدأ بالأساسيات",
      "اكتب الأمثلة بنفسك",
      "أنجِز التمارين",
      "ابنِ المشاريع",
      "راجِع وكرّر",
      "ثم انتقل للمتقدّم",
    ],
    body2:
      "المعرفة تصبح مهارة بالممارسة فقط. اقرأ بفاعلية، وابنِ بلا توقّف، وعُد لما تعلّمته. احترم الترتيب، فتضاعف كل دورة قيمة التي تليها.",
  },
  quote: {
    lead: "أفضل استثمار يمكنك القيام به هو",
    leadGold: "في نفسك.",
    leadTail: "المهارات تتراكم مدى الحياة.",
    body: "الأدوات تتغيّر، والأطر تأتي وتذهب، لكن القدرة على التعلّم والبناء لا تفقد قيمتها أبدًا. أتقِن الأساسيات، وواصِل البناء، وستردّ لك مهاراتك الجميل بقية حياتك.",
    attribution: "فلسفة E-tqan",
  },
  testimonials: {
    eyebrow: "محبوبة من المتعلّمين",
    title1: "نتائج",
    titleGold: "يشعر بها الناس.",
    description: "لمحة عمّا يقوله المتعلّمون بعد إتمام دورات مكتبة E-tqan.",
    items: [
      { role: "مطوّر عصامي", quote: "دورة بايثون جعلت كل شيء يتّضح أخيرًا. واضحة وحديثة وكل فصل ينتهي بشيء تبنيه. انتقلت من نسخ الدروس إلى كتابة مشاريعي." },
      { role: "مغيّر مسار مهني", quote: "وجود كل دورة بالعربية أحدث فرقًا كبيرًا — ركّزت على التعلّم بدل الترجمة. التصميم والأمثلة تبدو مميّزة بحق." },
      { role: "طالب حاسوب", quote: "التمارين والاختبارات هي ما يميّزها. أتذكّر ما تعلّمته لأنني طبّقته. تستحق أضعاف سعرها." },
      { role: "مستقل", quote: "اشتريت باقة مهارات المستقبل لتطوير عملي مع العملاء. دورتا الويب والذكاء الاصطناعي سدّدتا ثمنهما في مشروعي التالي مباشرة." },
      { role: "مصمّم يتعلّم البرمجة", quote: "مناسبة للمبتدئين دون تبسيط مخلّ. الشرح لا يفترض معرفة لكنه يحترم ذكاءك. بالضبط ما احتجته." },
      { role: "متعلّم دائم", quote: "تنزيل فوري وملفات PDF جميلة ومشاريع حقيقية. هكذا يجب أن تكون الدورات الرقمية. اشتريت ثلاثًا بالفعل." },
    ],
  },
  faq: {
    eyebrow: "الأسئلة الشائعة",
    title: "إجابات، قبل أن تسأل.",
    description: "كل ما تحتاج معرفته عن الدورات والتسليم واللغات والأسعار.",
    items: [
      { q: "ماذا سأحصل عليه فعلًا؟", a: "كتب رقمية مميّزة ومصمّمة باحتراف (PDF) لكل دورة — محتوى أصلي برسوم وأكواد وتمارين واختبارات ومشاريع. تُسلَّم كل دورة بالإنجليزية والعربية والتركية لتتعلّم باللغة التي تفضّلها." },
      { q: "ما صيغة الدورات وما اللغات؟", a: "ملفات PDF عالية الدقة، محسّنة للحاسوب واللوحي، بفهارس قابلة للنقر وأكواد ملوّنة. كل دورة تُسلَّم ثلاثية اللغة — الإنجليزية والعربية والتركية — في تنزيل واحد." },
      { q: "كيف أدفع وأستلم دورتي؟", a: "يتم الدفع بأمان عبر العملات الرقمية بالدولار. لحظة تأكيد الدفع يصلك التنزيل الخاص تلقائيًا — بلا انتظار ولا حسابات ولا وسطاء." },
      { q: "هل هي للمبتدئين؟", a: "معظم الدورات تبدأ من الصفر وتصل إلى مهارة قابلة للاستخدام مع مشروع في النهاية. وبعضها (مثل التداول المتقدّم بالذكاء الاصطناعي) لمن يعرف الأساسيات. كل دورة تذكر مستواها بوضوح." },
      { q: "ما الباقات؟", a: "مجموعات منسّقة من الدورات بخصم كبير — مثل باقة لغات البرمجة أو مكتبة الذهب الشاملة. إن كنت تنوي أخذ عدة دورات، فالباقة أفضل قيمة." },
      { q: "هل سعر الإطلاق سيختفي فعلًا؟", a: "نعم. عرض سعر التأسيس ثابت حتى 30 يوليو 2026 الساعة 23:59. عند وصول العدّاد للصفر تُزال الخصومات تلقائيًا وتعود الأسعار للأساسية." },
      { q: "هل أحصل على مساعدة عند الحاجة؟", a: "بالتأكيد. تواصل معنا في أي وقت عبر تيليجرام @Ahm_t_AHZ01 للمساعدة في الشراء أو التنزيل أو اختيار الدورة المناسبة." },
    ],
  },
  newsletter: {
    title: "دورات وعروض جديدة في بريدك",
    description:
      "تحديثات من حين لآخر عن الدورات والباقات ونصائح التعلّم — مع وصول مبكر للإطلاقات والخصومات. بلا رسائل مزعجة أبدًا.",
    placeholder: "you@email.com",
    subscribe: "اشترك",
    joining: "جارٍ الاشتراك…",
    success: "أنت الآن في القائمة. أهلًا بك.",
    agree: "بالاشتراك فإنك توافق على تلقّي رسائل من حين لآخر. يمكنك إلغاء الاشتراك في أي وقت.",
    emailLabel: "البريد الإلكتروني",
  },
  footer: {
    tagline:
      "مكتبة رقمية مميّزة وثلاثية اللغة لمن يريد تعلّم مهارات حقيقية عملية — وتطبيقها.",
    groups: { library: "المكتبة", community: "الشركة" },
    links: {
      whyBuy: "لماذا E-tqan",
      faq: "الأسئلة الشائعة",
      telegramSignals: "الدعم",
      newsletter: "النشرة البريدية",
      testimonials: "الآراء",
    },
    disclaimerLabel: "ملاحظة:",
    disclaimer:
      "كل المحتوى الذي تبيعه وتنشره {name} مادة تعليمية أصلية لأغراض التعلّم. أسماء الدورات وموضوعاتها للتعليم فقط. بالشراء فإنك توافق على أن المنتجات الرقمية غير قابلة للاسترداد بعد تنزيلها، إلا بما يقتضيه القانون. تعلّم بفاعلية، وابنِ كثيرًا، واستمتع.",
    rights: "جميع الحقوق محفوظة.",
    terms: "الشروط",
    privacy: "الخصوصية",
    refund: "سياسة الاسترداد",
  },
};

const tr: Dictionary = {
  nav: {
    links: {
      library: "Kurslar",
      curriculum: "Kategoriler",
      signals: "Destek",
      why: "Neden E-tqan",
      faq: "SSS",
    },
    cta: "Kurslara Göz At",
    menu: "Menüyü aç",
    language: "Dil",
  },
  hero: {
    badgeUntil: "bitiş",
    headline1: "Gerçekten kazandıran",
    headlineGold: "becerileri",
    headline2: "öğren.",
    headlinePlain: "Gerçekten kazandıran becerileri öğren.",
    subtitle:
      "Pratik, üç dilli kurslardan oluşan seçkin bir dijital kütüphane — programlama, yapay zeka, web, tasarım, üretkenlik ve borsa. Özenle yazıldı; İngilizce, Arapça ve Türkçe olarak anında teslim.",
    ctaPrimary: "Kursları Keşfet",
    ctaSecondary: "Paketleri Gör",
    trust1: "Ömür boyu erişim ve güncelleme",
    trust2: "Üç dilli · EN · AR · TR",
    trust3: "Güvenli kripto ödeme",
    from: "Başlangıç",
    stats: {
      modules: "Kurs",
      chapters: "Kategori",
      examples: "Dil",
      books: "Paket",
    },
  },
  ticker: { live: "Dünya çapında öğrenenlerin güvendiği" },
  celebration: {
    title: "🎉 Lansman Kutlaması",
    subtitle: "Kuruluş fiyatı teklifi — 30 Temmuz'a kadar sabit",
    ends: "bitiş",
    endsIn: "Teklifin bitişine",
    endedNotice:
      "Lansman kutlaması sona erdi — kurucu öğrenenlerimize teşekkürler. Kurslar artık standart fiyatlarında.",
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
    eyebrow: "Borsa Yolu",
    title1: "Piyasalarda ustalaş,",
    titleGold: "kurumsal yolla.",
    description:
      "Amiral borsa kütüphanemiz — piyasa yapısı, likidite ve emir akışında eksiksiz bir eğitim, ayrıca yapay zeka destekli kurumsal analiz. E-tqan kütüphanesindeki birçok yoldan biri.",
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
    eyebrow: "Neden E-tqan",
    title1: "Gerçek beceriler, doğru öğretilir —",
    titleGold: "boşa hiçbir şey yok.",
    description:
      "Dolgu yok, tekrar edilen eğitimler yok. Her kurs özgün, moderndir ve kullanılmak için tasarlanmıştır — bilgiyi yeteneğe dönüştüren projeler, alıştırmalar ve gerçek örneklerle.",
    perks: [
      { title: "Üç Dilli", desc: "Her kurs İngilizce, Arapça ve Türkçe — düşündüğün dilde öğren." },
      { title: "Pratik Projeler", desc: "Gerçek şeyler kur. Her kurs gösterebileceğin bir projeyle biter." },
      { title: "Güncel İçerik", desc: "2026 için yeniden yazıldı — güncel araçlar, güncel en iyi uygulamalar." },
      { title: "Özenli Tasarım", desc: "Temiz tipografi, diyagramlar ve vurgulu kodla premium, okunası kitaplar." },
      { title: "Anında Teslim", desc: "Öde ve saniyeler içinde indir — bekleme yok, hesap yok, sürtünme yok." },
      { title: "Başlangıç Dostu", desc: "Hiçbir şey varsaymayan, adım adım gerçek anlayış kuran net açıklamalar." },
      { title: "Alıştırma & Testler", desc: "Öğrenme gerçekten kalıcı olsun diye alıştırmalar, kontrol listeleri ve testler." },
      { title: "Ömür Boyu Güncelleme", desc: "Bir kez al, baskının gelecekteki tüm güncellemelerini ücretsiz koru." },
      { title: "Güvenli Ödeme", desc: "Özel, şifreli teslim ve güvenli kripto ödeme — aldığın şey senindir." },
    ],
  },
  telegram: {
    goingLive: "Destek",
    title1: "Sorun mu var? Yardıma",
    titleGold: "hazırız",
    body: "Satın alma, indirme veya doğru kursu seçme konusunda yardım için istediğin zaman Telegram'dan bize ulaş. Gerçek insanlardan gerçek destek — bot yok, oyalama yok.",
    cta: "Telegram'dan yaz",
    note: "Destek hesabı: @Ahm_t_AHZ01 — genelde hızlı yanıtlarız.",
    features: [
      { title: "Satın Alma Yardımı", desc: "Ödeme ya da indirme sorunu mu? Biz hallederiz." },
      { title: "Kurs Rehberliği", desc: "Nereden başlayacağını bilmiyor musun? Doğru yolu gösteririz." },
      { title: "Hızlı Yanıt", desc: "Gerçek bir insan, genelde saatler içinde." },
      { title: "Paket Tavsiyesi", desc: "Hedeflerine ve bütçene uygun paketi seçmene yardım ederiz." },
      { title: "Geri Bildirim", desc: "Bir şey mi fark ettin? Geri bildirimin sonraki baskıyı şekillendirir." },
      { title: "Samimi & Net", desc: "Net yanıtlar, senaryo yok, ek satış yok." },
    ],
  },
  warning: {
    title: "Bu Kurslardan En İyi Şekilde Yararlanmak",
    body1:
      "Beceriler birikir. E-tqan kütüphanesinden en iyi şekilde yararlanmak için mantıklı bir sırayla öğren ve ilerledikçe gerçekten kur. Sağlam bir temel, sonraki her şeyi kolaylaştırır:",
    fundamentals: [
      "Temellerle başla",
      "Örnekleri kendin yaz",
      "Alıştırmaları yap",
      "Projeleri kur",
      "Gözden geçir ve tekrarla",
      "Sonra ileri seviyeye geç",
    ],
    body2:
      "Bilgi ancak pratikle beceriye dönüşür. Etkin oku, durmadan kur ve öğrendiğini tekrar ziyaret et. Sıraya saygı göster; her kurs bir sonrakinin değerini katlar.",
  },
  quote: {
    lead: "Yapabileceğin en iyi yatırım",
    leadGold: "kendinedir.",
    leadTail: "Beceriler ömür boyu birikir.",
    body: "Araçlar değişir, çerçeveler gelir geçer, ama öğrenme ve inşa etme yeteneği asla değer kaybetmez. Temellerde ustalaş, üretmeye devam et; becerilerin hayatın boyunca sana geri ödesin.",
    attribution: "E-tqan felsefesi",
  },
  testimonials: {
    eyebrow: "Öğrenenlerin sevdiği",
    title1: "İnsanların",
    titleGold: "hissedebildiği sonuçlar.",
    description:
      "E-tqan kütüphanesini bitirdikten sonra öğrenenlerin söylediklerinden bir kesit.",
    items: [
      { role: "Kendi Kendine Geliştirici", quote: "Python kursuyla her şey nihayet oturdu. Net, modern ve her bölüm kurulacak bir şeyle bitiyor. Eğitim kopyalamaktan kendi projelerimi yazmaya geçtim." },
      { role: "Kariyer Değiştiren", quote: "Her kursun Arapça olması çok şey değiştirdi — çeviri yerine öğrenmeye odaklandım. Tasarım ve örnekler gerçekten premium." },
      { role: "Öğrenci · Bilgisayar", quote: "Alıştırmalar ve testler bunları ayıran şey. Öğrendiğimi hatırlıyorum çünkü uyguladım. Fiyatının kat kat üstünde değer." },
      { role: "Serbest Çalışan", quote: "Müşteri işimi geliştirmek için Gelecek Becerileri paketini aldım. Web ve yapay zeka kursları bir sonraki projemde kendini amorti etti." },
      { role: "Kod öğrenen tasarımcı", quote: "Basitleştirmeden başlangıç dostu. Açıklamalar hiçbir şey varsaymıyor ama zekâna saygı duyuyor. Tam ihtiyacım olan şey." },
      { role: "Ömür Boyu Öğrenen", quote: "Anında indirme, güzel PDF'ler, gerçek projeler. Dijital kurslar böyle olmalı. Şimdiden üç tane aldım." },
    ],
  },
  faq: {
    eyebrow: "SSS",
    title: "Sormadan önce, cevaplar.",
    description:
      "Kurslar, teslimat, diller ve fiyatlandırma hakkında bilmen gereken her şey.",
    items: [
      { q: "Tam olarak ne alıyorum?", a: "Her kurs için premium, profesyonelce tasarlanmış dijital kitaplar (PDF) — diyagramlar, kod, alıştırmalar, testler ve projelerle özgün içerik. Her kurs İngilizce, Arapça ve Türkçe teslim edilir; tercih ettiğin dilde öğren." },
      { q: "Kurslar hangi formatta ve hangi dillerde?", a: "Masaüstü ve tablet için optimize, tıklanabilir yer imleri ve vurgulu kod içeren yüksek çözünürlüklü PDF'ler. Her kurs üç dilli — İngilizce, Arapça ve Türkçe — tek indirmede gelir." },
      { q: "Nasıl öderim ve kursumu nasıl alırım?", a: "Ödeme kripto ile güvenli şekilde, USD olarak yapılır. Ödeme onaylandığı an özel indirmen otomatik teslim edilir — bekleme yok, hesap yok, aracı yok." },
      { q: "Bunlar yeni başlayanlar için mi?", a: "Çoğu kurs sıfırdan başlar ve sonunda bir projeyle gerçek, kullanılabilir bir beceriye ulaşır. Birkaçı (Advanced AI Trading gibi) temelleri bilenler içindir. Her kurs seviyesini açıkça belirtir." },
      { q: "Paketler nedir?", a: "Büyük indirimle sunulan seçkin kurs koleksiyonları — Programlama Dilleri paketi ya da her şeyi içeren Gold Master Kütüphanesi gibi. Birkaç kurs alacaksan paket en iyi değerdir." },
      { q: "Lansman fiyatı gerçekten kalkacak mı?", a: "Evet. Kuruluş fiyatı teklifi 30 Temmuz 2026 saat 23:59'a kadar sabittir. Geri sayım sıfırlandığında indirimler otomatik kaldırılır ve fiyatlar standarda döner." },
      { q: "İhtiyaç halinde yardım alabilir miyim?", a: "Kesinlikle. Satın alma, indirme veya doğru kursu seçme konusunda yardım için istediğin zaman Telegram'dan @Ahm_t_AHZ01 adresine ulaş." },
    ],
  },
  newsletter: {
    title: "Yeni kurslar ve teklifler gelen kutunda",
    description:
      "Yeni kurslar, paketler ve öğrenme ipuçları üzerine ara sıra güncellemeler — ayrıca lansmanlara ve indirimlere erken erişim. Asla spam yok.",
    placeholder: "sen@email.com",
    subscribe: "Abone Ol",
    joining: "Katılıyor…",
    success: "Listedesin. Aramıza hoş geldin.",
    agree: "Abone olarak ara sıra e-posta almayı kabul edersin. İstediğin zaman çıkabilirsin.",
    emailLabel: "E-posta adresi",
  },
  footer: {
    tagline:
      "Gerçek, pratik beceriler öğrenmek — ve onları işe koşmak — konusunda ciddi olanlar için premium, üç dilli bir dijital kütüphane.",
    groups: { library: "Kütüphane", community: "Şirket" },
    links: {
      whyBuy: "Neden E-tqan",
      faq: "SSS",
      telegramSignals: "Destek",
      newsletter: "Bülten",
      testimonials: "Yorumlar",
    },
    disclaimerLabel: "Not:",
    disclaimer:
      "{name} tarafından satılan ve yayınlanan tüm içerik, öğrenme amaçlı özgün eğitim materyalidir. Kurs adları ve konuları yalnızca eğitim içindir. Satın alarak, dijital ürünlerin indirildikten sonra yasa gereği haller dışında iade edilemeyeceğini kabul edersin. Etkin öğren, sık kur ve keyfini çıkar.",
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
