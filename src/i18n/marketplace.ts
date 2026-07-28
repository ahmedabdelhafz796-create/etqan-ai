import type { Locale } from "@/i18n/config";

/**
 * Copy for the AI automation marketplace — the site's primary product line.
 *
 * Kept out of `dictionaries.ts` on purpose. That file is the trading
 * library's storefront copy and is already long; this is a different
 * product with a different vocabulary (workflows, nodes, triggers,
 * credentials) and its own three-locale surface. Splitting them means a
 * change to one product's wording can never silently disturb the other,
 * and the three languages of *this* product sit next to each other where
 * drift between them is visible.
 *
 * Every number quoted here is measured from the shipped artefacts in
 * `suite/dist` — node counts, workflow counts, test counts. Nothing is
 * rounded up for marketing.
 */

const en = {
  hero: {
    badge: "23 production workflows · 151 behavioural tests passing",
    headline1: "Automation that survives",
    headlineAccent: "real traffic",
    headline2: "— not just the demo.",
    headlinePlain:
      "Automation that survives real traffic — not just the demo.",
    subtitle:
      "n8n systems, AI agents and workflow templates for people who actually ship. Most templates work once, in a clean run, on the author's machine. These are tested against replay attacks, network failures, malformed payloads and silent errors — and the test results ship with them.",
    ctaPrimary: "Browse the systems",
    ctaSecondary: "Start with the free tool",
    trust: [
      "Import as JSON — runs on n8n Cloud or self-hosted",
      "Zero embedded credentials",
      "Lifetime updates included",
    ],
    stats: [
      { value: "23", label: "Workflows shipped" },
      { value: "285", label: "Nodes engineered" },
      { value: "151", label: "Behavioural tests" },
      { value: "0", label: "Known defects" },
    ],
  },

  integrations: {
    title: "Built on tools you already run",
    note: "Every workflow imports as plain n8n JSON. No proprietary runtime, no lock-in, no account with us required.",
    items: [
      "n8n",
      "OpenAI",
      "Stripe",
      "Lemon Squeezy",
      "Paddle",
      "Gumroad",
      "PayPal",
      "Slack",
      "SMTP / Gmail",
      "Airtable",
      "Google Sheets",
      "Webhooks",
    ],
  },

  how: {
    eyebrow: "How it works",
    title1: "Running in",
    titleAccent: "under an hour",
    description:
      "No framework to learn and no code to write. Three steps, and the third one is the system checking itself.",
    steps: [
      {
        n: "01",
        title: "Import the JSON",
        body: "Every workflow is a standard n8n export. Open n8n, paste the file, and the full canvas appears — nodes, connections, sticky notes explaining each decision.",
      },
      {
        n: "02",
        title: "Fill in one Config node",
        body: "Each workflow starts with a single Config node holding every value you need to change. Credentials stay in n8n's credential store — nothing is ever written into the workflow file.",
      },
      {
        n: "03",
        title: "Run the Setup Checker",
        body: "A shipped workflow that inspects your install for the mistakes that cause silent failure — placeholder values, mismatched signing secrets, missing error workflow — and tells you the fix for each.",
      },
    ],
  },

  catalog: {
    eyebrow: "The catalogue",
    title1: "AI systems, tools and",
    titleAccent: "templates",
    description:
      "Five bundles, built from 23 production workflows. Buy the one that matches the problem you have today; every bundle includes the Setup Checker and the Central Error Hub.",
    kinds: { tool: "Free tool", system: "System", suite: "Full suite" },
    bestValue: "Best value",
    free: "Free",
    getFree: "Download free",
    getBundle: "Get this bundle",
    seeInside: "What's inside",
    workflowsLabel: "workflows",
    nodesLabel: "nodes",
    payNote:
      "Checkout and delivery for every bundle is handled by Lemon Squeezy. The trading library below is a separate product line with its own checkout.",
    outcomesLabel: "What it does for you",
    useCasesLabel: "Bought for",
    includesLabel: "Workflows included",
  },

  bundles: {
    "free-secure-downloads": {
      tagline: "See the standard before you spend anything",
      summary:
        "A single endpoint that verifies a signed download link, enforces expiry and a download cap, and returns a specific reason for every refusal instead of a bare 403. It is the smallest complete example of how everything else here is built.",
      outcomes: [
        "Links that expire and cap downloads, so a shared URL stops working",
        "Refusals that explain themselves — expired, cap reached, bad signature",
        "Flags links used from many IP addresses, so leaks surface early",
        "No database required — state lives in n8n's own static store",
      ],
      useCases: [
        "You sell a PDF or a ZIP and email a raw file link today",
        "You want to see the code quality before buying a bundle",
        "You need download protection without standing up a backend",
      ],
    },
    "delivery-essentials": {
      tagline: "For when customers aren't getting their files",
      summary:
        "The complete path from a confirmed payment to a file in the buyer's inbox, across six payment gateways — plus the two workflows that handle it when something goes wrong: automatic re-issue when a buyer can't download, and update broadcasts to past buyers with fresh links.",
      outcomes: [
        "One endpoint accepts Stripe, Paddle, Lemon Squeezy, Gumroad, PayPal and NOWPayments",
        "Replay protection, so a webhook delivered twice never sends the file twice",
        "'I can't download my file' answered automatically, with rate limits and human escalation",
        "Ship an update and every past buyer gets a fresh signed link, batched to protect your sending reputation",
      ],
      useCases: [
        "You sell digital products and refund people who never got them",
        "Download support tickets are eating your day",
        "You publish updates and re-emailing every buyer by hand is impossible",
      ],
    },
    "revenue-protection": {
      tagline: "For when you're losing money you already earned",
      summary:
        "Five workflows aimed at the revenue that leaks after the sale: fraud scored before delivery, chargebacks caught while they are still alerts, leaked files traced back to the buyer who leaked them, and both kinds of failed payment recovered on a timed sequence.",
      outcomes: [
        "Fraud scoring before delivery using local signals only — no paid API, no data leaving your instance",
        "Chargeback alerts triaged with a refund-or-fight recommendation and the evidence pack assembled",
        "Per-buyer watermarking that traces a leaked file to the account that leaked it, with the takedown notice drafted",
        "Abandoned carts and failed subscription payments recovered without discounting by default",
      ],
      useCases: [
        "Your chargeback ratio is climbing toward the level that closes payment accounts",
        "Your product is being shared and you cannot prove by whom",
        "Failed renewals quietly churn customers you already won",
      ],
    },
    "ai-agents": {
      tagline: "For when you're drowning in manual work",
      summary:
        "Five AI agents built to refuse rather than invent. Each one states its confidence, hands off to a human when it is unsure, and never takes an irreversible action on its own — support answers, lead qualification, translation, sales copy and CV screening.",
      outcomes: [
        "A support agent that answers from your knowledge base, scores its own confidence, and escalates with a draft already written",
        "A lead qualifier that routes serious buyers to a human immediately instead of behind four tyre-kickers",
        "Translation that protects prices, brand names and formatting — and emits text direction so RTL renders correctly",
        "CV screening that ranks with stated reasoning and never auto-rejects anyone",
      ],
      useCases: [
        "The same five support questions arrive every day",
        "You sell in several languages and updating copy takes a week",
        "Hiring: too many applications, no time to read them fairly",
      ],
    },
    "complete-suite": {
      tagline: "The whole operating system for a digital business",
      summary:
        "All 23 workflows — delivery, revenue protection, AI agents — plus the four that only make sense once everything else is running: sequential VAT invoicing, affiliate commission payouts, sales anomaly detection, and a daily pulse that reads what every other workflow already wrote.",
      outcomes: [
        "Everything in the three systems above, priced below their sum",
        "Correctly numbered sequential invoices with the tax evidence authorities ask for",
        "Affiliate commissions tracked, reversed on refund, and deduplicated into one payout instruction",
        "One daily message covering what needs action, what was recovered, and what ran",
      ],
      useCases: [
        "You are building the business, not patching one leak",
        "You want the invoicing, analytics and payout side handled too",
        "You would rather install once than assemble bundles over six months",
      ],
    },
  },

  categories: {
    delivery: "Delivery",
    protection: "Protection",
    agent: "AI agent",
    growth: "Revenue",
    finance: "Finance",
    ops: "Operations",
  },
  triggers: {
    webhook: "Webhook",
    schedule: "Scheduled",
    manual: "Manual",
    error: "On error",
  },

  workflows: {
    "instant-digital-delivery":
      "One endpoint that turns a confirmed payment from any major gateway into a signed, expiring download link in the buyer's inbox.",
    "secure-download-endpoint":
      "Verifies a signed download link, enforces expiry and a download cap, and returns a specific reason for every refusal instead of a bare 403.",
    "product-update-broadcast":
      "Notifies past buyers of an update with a freshly signed link — filtered to actual buyers, deduplicated per version, batched to protect sending reputation.",
    "download-problem-self-service":
      "Handles the message that dominates a digital seller's inbox — 'I can't get my file' — by verifying entitlement and reissuing a fresh link automatically.",
    "delivery-test-runner":
      "Fires three scenarios at your live delivery endpoint and reports whether delivery, replay protection and payment gating all behave correctly.",
    "setup-checker":
      "Inspects an installation for the mistakes that cause silent failure — placeholders, mismatched secrets, missing error workflow — with the fix for each.",
    "central-error-hub":
      "Receives failures from every workflow in the suite, ranks them by business impact, suppresses repeat storms, and explains each in language you can act on.",
    "pre-payment-fraud-scoring":
      "Scores every order for fraud before delivery using local signals only — disposable domains, velocity, geo mismatch, amount anomalies.",
    "chargeback-early-warning":
      "Catches fraud alerts before they become formal disputes, recommends refund-or-fight with reasoning, and assembles the evidence pack automatically.",
    "leak-detection-watermarking":
      "Stamps every copy with a buyer-specific marker, detects sharing from download behaviour, traces a leak back to its account, and drafts the takedown.",
    "cart-abandonment-recovery":
      "Recovers interrupted checkouts with a timed two-message sequence that stops the moment the buyer purchases — discounting off by default.",
    "failed-payment-recovery":
      "Catches failed subscription payments as they happen and runs an escalating recovery sequence until the card is updated or the sequence ends.",
    "post-purchase-sequence":
      "Helps first and asks second — checks privately whether the buyer is happy before requesting a public review, and only mentions an upsell after the refund window closes.",
    "ai-customer-support-agent":
      "Answers from a knowledge base you control, scores its own confidence, and hands anything uncertain to a human with a draft already written.",
    "ai-lead-qualifier":
      "Reads every inbound enquiry, scores intent and fit, and routes hot leads to a human immediately while everything else goes to nurture.",
    "ai-product-translation":
      "Translates product copy into every language you sell in, protects prices and brand names, skips unchanged text, and emits text direction for RTL.",
    "ai-sales-page-writer":
      "Turns a product's facts into a structured sales page — problem, proof, what you get, honest limits — then scans it for unsupported claims.",
    "cv-screening-triage":
      "Reads every application against the requirements you wrote and ranks candidates with stated reasoning — without ever auto-rejecting anyone.",
    "automatic-invoice-vat":
      "Issues a correctly numbered sequential invoice for every paid order, applies your tax rates, and captures the evidence tax authorities ask for.",
    "commission-affiliate-payouts":
      "Tracks what each affiliate has earned, reverses commission on refunds, preserves the rate at time of sale, and produces one deduplicated payout instruction.",
    "sales-anomaly-detection":
      "Watches order volume against the same weekday in recent weeks and tells you whether demand fell or your pipeline broke — which need opposite responses.",
    "sales-pipeline-followup":
      "Tracks open deals, measures how long each has been silent, and sends one daily digest of who needs chasing — prioritised by value, with a draft for each.",
    "daily-business-pulse":
      "Reads the data every other workflow already writes and sends one daily message: what needs action, what was recovered, and what ran.",
  },

  standards: {
    eyebrow: "The standard",
    title1: "Six rules every workflow",
    titleAccent: "has to pass",
    description:
      "Not a promise — a build gate. The factory that generates these workflows refuses to write a file that fails any of them, and 151 behavioural tests run the real code to prove it.",
    items: [
      {
        title: "No embedded credentials",
        body: "Not one API key, token or password appears in any workflow file. Credentials live in n8n's credential store, referenced by name.",
      },
      {
        title: "Retry on every network call",
        body: "Every node that touches the network retries with backoff. The rule is default-deny: a new node type is treated as remote until proven local.",
      },
      {
        title: "Every node has an error path",
        body: "Checked per node, not per file. A workflow with one handled failure and five unhandled ones does not build.",
      },
      {
        title: "Replay protection",
        body: "Webhooks get delivered twice. Every entry point is idempotent, so the second delivery is recognised and dropped instead of charging or emailing twice.",
      },
      {
        title: "Nothing fails silently",
        body: "Every failure reaches the Central Error Hub, ranked by business impact, with repeat storms suppressed so one outage doesn't send 400 alerts.",
      },
      {
        title: "Runs self-hosted, not just on Cloud",
        body: "No `require()` of Node built-ins inside Code nodes — the classic trap that works for the author on n8n Cloud and throws for the buyer on a default self-hosted install.",
      },
    ],
  },

  proof: {
    eyebrow: "Proof, not adjectives",
    title1: "The tests ship",
    titleAccent: "with the files",
    description:
      "Every bundle contains the test report for the workflows inside it. You can read what was tested and what the assertion was before you trust any of it in front of a paying customer.",
    metrics: [
      { value: "151", label: "Behavioural tests", note: "Real code executed, not linted" },
      { value: "14", label: "Gate integrity probes", note: "Tests that the build gate itself works" },
      { value: "23", label: "Workflows", note: "Every one imported into live n8n" },
      { value: "285", label: "Nodes", note: "Counted, excluding sticky notes" },
    ],
    footnote:
      "The gate probes exist because a build gate that passes everything is worse than no gate. Each probe deliberately breaks a rule and fails the build if the gate lets it through.",
  },

  books: {
    eyebrow: "Also from Etqan",
    title1: "The trading",
    titleAccent: "library",
    description:
      "A separate, secondary product line: two institutional trading books, sold through their own crypto checkout. Nothing to do with the automation systems above.",
    cta: "Browse the trading books",
  },

  faq: {
    eyebrow: "FAQ",
    title: "Answers, before you ask.",
    description:
      "What you get, how it installs, and what happens when something breaks.",
    items: [
      {
        q: "What exactly do I receive after paying?",
        a: "A ZIP containing one folder per workflow. Each folder has the n8n workflow JSON, a README explaining every decision, and the test report for that workflow. The bundle also includes an INSTALL guide written in the order you should actually install things, and a licence file.",
      },
      {
        q: "Do I need to know how to code?",
        a: "No. You import a JSON file into n8n and fill in one Config node per workflow. The Code nodes are already written and tested. If you can copy an API key from Stripe into a form, you can install these.",
      },
      {
        q: "Does this work on self-hosted n8n or only n8n Cloud?",
        a: "Both, deliberately. A common failure in published templates is a Code node calling require('crypto') — that works on n8n Cloud but throws on a default self-hosted install unless the operator sets NODE_FUNCTION_ALLOW_BUILTIN. These use n8n's built-in Crypto node instead, so the same file runs in both places.",
      },
      {
        q: "What does '151 behavioural tests' actually mean?",
        a: "A minimal n8n executor runs the real workflows: the actual Code node JavaScript, real HMAC signatures, real branch conditions. The tests assert on what the workflow does — that a replayed webhook is dropped, that a failed email routes to the error hub, that an expired link returns the expiry reason. It is not a linter or a schema check.",
      },
      {
        q: "Which payment gateways are supported?",
        a: "Stripe, Paddle, Lemon Squeezy, Gumroad, PayPal and NOWPayments arrive at one delivery endpoint, each with its own signature verification. Adding a seventh means one branch in one node.",
      },
      {
        q: "Do the AI agents need an OpenAI key?",
        a: "The five agent workflows do. The fraud scoring workflow deliberately does not — it uses local signals only, so no order data leaves your instance and there is no per-order API cost.",
      },
      {
        q: "What if a workflow breaks after an n8n update?",
        a: "Updates are included for the lifetime of the product. When n8n ships a breaking node change, the affected workflows are rebuilt, re-tested against the same 151 assertions, and you get the new files.",
      },
      {
        q: "Can I use these in client work?",
        a: "Yes. You can install and modify them for your own business and for clients you build for. You cannot resell or republish the workflow files themselves as a template product. The licence file in every bundle states this in full.",
      },
      {
        q: "How is this different from the free templates on n8n.io?",
        a: "Mostly in what happens on the bad day. A free template shows the happy path and usually has no retry, no replay protection and no error path — which is fine for a demo and expensive in production. The difference here is not cleverness, it is the six rules above, enforced by a build gate rather than by intention.",
      },
    ],
  },

  newsletter: {
    title: "New workflows, in your inbox",
    description:
      "A short note when a new system ships, when an existing one is rebuilt for an n8n breaking change, and when something in the build standard changes. Nothing else.",
    placeholder: "you@email.com",
    subscribe: "Subscribe",
    joining: "Joining…",
    success: "You're on the list.",
    agree: "By subscribing you agree to receive occasional emails. Unsubscribe anytime.",
    emailLabel: "Email address",
  },

  footer: {
    tagline:
      "Production-hardened n8n systems, AI agents and workflow templates — built to a published standard and shipped with the tests that prove it.",
    groups: {
      products: "Products",
      resources: "Resources",
    },
    links: {
      catalog: "All bundles",
      free: "Free tool",
      how: "How it works",
      standard: "The standard",
      proof: "Test results",
      faq: "FAQ",
      books: "Trading books",
    },
    disclaimerLabel: "Trading books disclaimer:",
  },

  finalCta: {
    title1: "Start with the free tool.",
    titleAccent: "Buy nothing until it convinces you.",
    body: "The Secure Download Endpoint is the same build standard as everything else here — same gate, same tests, same documentation. Install it, read the code, then decide.",
    primary: "Download the free tool",
    secondary: "See all bundles",
  },
} as const;

/* ── Arabic ───────────────────────────────────────────────────────────── */

const ar = {
  hero: {
    badge: "٢٣ سير عمل جاهز للإنتاج، و١٥١ اختبار سلوكي ناجح",
    headline1: "أتمتة تصمد أمام",
    headlineAccent: "التشغيل الحقيقي",
    headline2: "— لا مجرد عرض تجريبي.",
    headlinePlain: "أتمتة تصمد أمام التشغيل الحقيقي — لا مجرد عرض تجريبي.",
    subtitle:
      "أنظمة n8n ووكلاء ذكاء اصطناعي وقوالب سير عمل لمن ينفّذ فعلاً. معظم القوالب تعمل مرة واحدة، في تشغيل نظيف، على جهاز صاحبها. هذه مختبَرة ضد إعادة الإرسال وأعطال الشبكة والبيانات المشوّهة والأخطاء الصامتة — ونتائج الاختبارات تُسلَّم معها.",
    ctaPrimary: "تصفّح الأنظمة",
    ctaSecondary: "ابدأ بالأداة المجانية",
    trust: [
      "استيراد كملف JSON — يعمل على n8n السحابي أو المستضاف ذاتياً",
      "صفر بيانات اعتماد مضمّنة",
      "تحديثات مدى الحياة",
    ],
    stats: [
      { value: "23", label: "سير عمل مُسلَّم" },
      { value: "285", label: "عقدة مهندَسة" },
      { value: "151", label: "اختبار سلوكي" },
      { value: "0", label: "أخطاء معروفة" },
    ],
  },

  integrations: {
    title: "مبني على أدوات تستخدمها بالفعل",
    note: "كل سير عمل يُستورد كملف n8n JSON عادي. لا بيئة تشغيل خاصة، ولا احتكار، ولا حاجة لحساب عندنا.",
    items: [
      "n8n",
      "OpenAI",
      "Stripe",
      "Lemon Squeezy",
      "Paddle",
      "Gumroad",
      "PayPal",
      "Slack",
      "SMTP / Gmail",
      "Airtable",
      "Google Sheets",
      "Webhooks",
    ],
  },

  how: {
    eyebrow: "كيف يعمل",
    title1: "يعمل خلال",
    titleAccent: "أقل من ساعة",
    description:
      "لا إطار عمل تتعلّمه ولا كود تكتبه. ثلاث خطوات، والثالثة هي النظام وهو يفحص نفسه.",
    steps: [
      {
        n: "٠١",
        title: "استورد ملف JSON",
        body: "كل سير عمل هو تصدير n8n قياسي. افتح n8n، الصق الملف، فتظهر اللوحة كاملة — العقد والوصلات وملاحظات تشرح كل قرار.",
      },
      {
        n: "٠٢",
        title: "املأ عقدة Config واحدة",
        body: "كل سير عمل يبدأ بعقدة Config واحدة تحتوي كل قيمة تحتاج تغييرها. بيانات الاعتماد تبقى في مخزن n8n — ولا تُكتب أبداً داخل الملف.",
      },
      {
        n: "٠٣",
        title: "شغّل فاحص الإعداد",
        body: "سير عمل مرفق يفحص تركيبك بحثاً عن الأخطاء التي تسبب فشلاً صامتاً — قيم افتراضية متروكة، مفاتيح توقيع غير متطابقة، سير خطأ مفقود — ويعطيك الحل لكل واحدة.",
      },
    ],
  },

  catalog: {
    eyebrow: "الكتالوج",
    title1: "أنظمة وأدوات وقوالب",
    titleAccent: "ذكاء اصطناعي",
    description:
      "خمس حزم مبنية من ٢٣ سير عمل إنتاجي. اشترِ ما يطابق مشكلتك اليوم؛ وكل حزمة تتضمن فاحص الإعداد ومركز الأخطاء.",
    kinds: { tool: "أداة مجانية", system: "نظام", suite: "الحزمة الكاملة" },
    bestValue: "الأفضل قيمة",
    free: "مجاناً",
    getFree: "حمّل مجاناً",
    getBundle: "احصل على الحزمة",
    seeInside: "ما بالداخل",
    workflowsLabel: "سير عمل",
    nodesLabel: "عقدة",
    payNote:
      "الدفع والتسليم لكل الحزم عبر Lemon Squeezy. مكتبة التداول بالأسفل خط منتجات منفصل له بوابة دفع خاصة به.",
    outcomesLabel: "ماذا يفعل لك",
    useCasesLabel: "يُشترى من أجل",
    includesLabel: "سير العمل المضمّن",
  },

  bundles: {
    "free-secure-downloads": {
      tagline: "شاهد المستوى قبل أن تدفع شيئاً",
      summary:
        "نقطة نهاية واحدة تتحقق من رابط تحميل موقّع، تفرض انتهاء الصلاحية وحداً أقصى للتحميلات، وتعيد سبباً محدداً لكل رفض بدل 403 فارغ. وهي أصغر مثال كامل على طريقة بناء كل ما هنا.",
      outcomes: [
        "روابط تنتهي صلاحيتها وتحدّ التحميلات، فالرابط المُشارَك يتوقف",
        "رفض يشرح نفسه — منتهٍ، تجاوز الحد، توقيع خاطئ",
        "يرصد الروابط المستخدمة من عناوين IP كثيرة، فيظهر التسريب مبكراً",
        "لا حاجة لقاعدة بيانات — الحالة في مخزن n8n نفسه",
      ],
      useCases: [
        "تبيع PDF أو ZIP وترسل رابط ملف مباشر اليوم",
        "تريد رؤية جودة الكود قبل شراء حزمة",
        "تحتاج حماية التحميل دون بناء خادم خلفي",
      ],
    },
    "delivery-essentials": {
      tagline: "حين لا يصل العملاء إلى ملفاتهم",
      summary:
        "المسار الكامل من دفعة مؤكدة إلى ملف في بريد المشتري، عبر ست بوابات دفع — إضافة إلى سيري العمل اللذين يتوليان الخطأ: إعادة إصدار تلقائية حين يعجز المشتري عن التحميل، وبث التحديثات للمشترين السابقين بروابط جديدة.",
      outcomes: [
        "نقطة واحدة تستقبل Stripe وPaddle وLemon Squeezy وGumroad وPayPal وNOWPayments",
        "حماية من إعادة الإرسال، فالويب هوك المكرر لا يرسل الملف مرتين",
        "«لا أستطيع تحميل ملفي» تُجاب تلقائياً، مع حدود معدل وتصعيد بشري",
        "تنشر تحديثاً فيصل كل مشترٍ سابق برابط موقّع جديد، على دفعات تحمي سمعة الإرسال",
      ],
      useCases: [
        "تبيع منتجات رقمية وتعيد المال لمن لم يستلمها",
        "تذاكر دعم التحميل تلتهم يومك",
        "تنشر تحديثات وإعادة المراسلة يدوياً مستحيلة",
      ],
    },
    "revenue-protection": {
      tagline: "حين تخسر مالاً كسبته بالفعل",
      summary:
        "خمسة سير عمل موجّهة للإيراد الذي يتسرب بعد البيع: احتيال يُقيَّم قبل التسليم، ونزاعات تُلتقط وهي ما زالت تنبيهات، وملفات مسرّبة تُتتبَّع إلى من سرّبها، ونوعا الدفع الفاشل يُستردّان بتسلسل زمني.",
      outcomes: [
        "تقييم احتيال قبل التسليم بإشارات محلية فقط — بلا API مدفوع ودون خروج بيانات",
        "تنبيهات النزاع تُفرز بتوصية «ردّ أم نازع» مع تجميع ملف الأدلة",
        "علامة مائية لكل مشترٍ تتتبع الملف المسرّب إلى حسابه، مع صياغة إشعار الإزالة",
        "سلات متروكة ودفعات اشتراك فاشلة تُستردّ دون خصم افتراضي",
      ],
      useCases: [
        "نسبة النزاعات لديك تقترب من الحد الذي يغلق حسابات الدفع",
        "منتجك يُشارَك ولا تستطيع إثبات من فعلها",
        "تجديدات فاشلة تُسرّب عملاء ربحتهم بالفعل",
      ],
    },
    "ai-agents": {
      tagline: "حين تغرق في العمل اليدوي",
      summary:
        "خمسة وكلاء ذكاء اصطناعي بُنيت لترفض بدل أن تخترع. كل وكيل يعلن ثقته، ويسلّم لإنسان عند الشك، ولا يتخذ إجراءً لا رجعة فيه وحده — دعم، تأهيل عملاء، ترجمة، صفحات بيع، وفرز سير ذاتية.",
      outcomes: [
        "وكيل دعم يجيب من قاعدة معرفتك، يقيس ثقته، ويصعّد ومعه مسودة جاهزة",
        "مؤهِّل عملاء يوجّه المشتري الجاد إلى إنسان فوراً لا خلف أربعة متفرجين",
        "ترجمة تحمي الأسعار وأسماء العلامات والتنسيق — وتحدد اتجاه النص ليعرض RTL صحيحاً",
        "فرز سير ذاتية يرتّب بأسباب معلنة ولا يرفض أحداً تلقائياً",
      ],
      useCases: [
        "نفس الأسئلة الخمسة تصل كل يوم",
        "تبيع بعدة لغات وتحديث النصوص يستغرق أسبوعاً",
        "توظيف: طلبات كثيرة ولا وقت لقراءتها بإنصاف",
      ],
    },
    "complete-suite": {
      tagline: "نظام تشغيل كامل لأعمال رقمية",
      summary:
        "كل الـ٢٣ سير عمل — تسليم وحماية إيراد ووكلاء — إضافة إلى الأربعة التي لا معنى لها إلا بعد تشغيل الباقي: فوترة ضريبية متسلسلة، ومدفوعات عمولات المسوّقين، وكشف شذوذ المبيعات، ونبض يومي يقرأ ما كتبته بقية الأنظمة.",
      outcomes: [
        "كل ما في الأنظمة الثلاثة أعلاه، بسعر أقل من مجموعها",
        "فواتير متسلسلة مرقّمة صحيحاً مع الأدلة التي تطلبها الجهات الضريبية",
        "عمولات تُتتبَّع وتُعكس عند الاسترداد وتُجمَّع في أمر دفع واحد بلا تكرار",
        "رسالة يومية واحدة: ما يحتاج تدخلاً، وما استُرد، وما عمل",
      ],
      useCases: [
        "تبني الأعمال لا ترقّع تسريباً واحداً",
        "تريد الفوترة والتحليلات والعمولات مغطاة أيضاً",
        "تفضّل تركيباً واحداً على تجميع حزم عبر ستة أشهر",
      ],
    },
  },

  categories: {
    delivery: "التسليم",
    protection: "الحماية",
    agent: "وكيل ذكي",
    growth: "الإيراد",
    finance: "المالية",
    ops: "التشغيل",
  },
  triggers: {
    webhook: "ويب هوك",
    schedule: "مجدول",
    manual: "يدوي",
    error: "عند الخطأ",
  },

  workflows: {
    "instant-digital-delivery":
      "نقطة واحدة تحوّل دفعة مؤكدة من أي بوابة كبرى إلى رابط تحميل موقّع ومحدود المدة في بريد المشتري.",
    "secure-download-endpoint":
      "يتحقق من رابط تحميل موقّع، ويفرض الصلاحية وحد التحميلات، ويعيد سبباً محدداً لكل رفض بدل 403 فارغ.",
    "product-update-broadcast":
      "يبلّغ المشترين السابقين بالتحديث برابط موقّع جديد — مقتصراً على المشترين الفعليين، بلا تكرار، وعلى دفعات تحمي سمعة الإرسال.",
    "download-problem-self-service":
      "يعالج الرسالة التي تسيطر على بريد البائع — «لا أستطيع الحصول على ملفي» — بالتحقق من الاستحقاق وإعادة إصدار رابط جديد تلقائياً.",
    "delivery-test-runner":
      "يطلق ثلاثة سيناريوهات على نقطة التسليم الحية ويبلّغ إن كان التسليم وحماية الإعادة وبوابة الدفع تعمل كما يجب.",
    "setup-checker":
      "يفحص التركيب بحثاً عن الأخطاء التي تسبب فشلاً صامتاً — قيم افتراضية، مفاتيح غير متطابقة، سير خطأ مفقود — مع حل كل واحدة.",
    "central-error-hub":
      "يستقبل الأعطال من كل سير عمل، يرتّبها بأثرها على العمل، يكبح العواصف المتكررة، ويشرح كل عطل بلغة قابلة للتنفيذ.",
    "pre-payment-fraud-scoring":
      "يقيّم كل طلب للاحتيال قبل التسليم بإشارات محلية فقط — نطاقات مؤقتة، سرعة الطلبات، تعارض جغرافي، مبالغ شاذة.",
    "chargeback-early-warning":
      "يلتقط تنبيهات الاحتيال قبل أن تصبح نزاعات رسمية، ويوصي بالرد أو المنازعة مع التعليل، ويجمّع ملف الأدلة تلقائياً.",
    "leak-detection-watermarking":
      "يبصم كل نسخة بعلامة خاصة بالمشتري، ويكشف المشاركة من سلوك التحميل، ويتتبع التسريب إلى حسابه، ويصيغ إشعار الإزالة.",
    "cart-abandonment-recovery":
      "يسترد السلات المتوقفة برسالتين موقوتتين تتوقفان لحظة الشراء — والخصم مُعطَّل افتراضياً.",
    "failed-payment-recovery":
      "يلتقط دفعات الاشتراك الفاشلة فور حدوثها ويشغّل تسلسل استرداد متصاعداً حتى تُحدَّث البطاقة أو ينتهي التسلسل.",
    "post-purchase-sequence":
      "يساعد أولاً ويطلب ثانياً — يسأل المشتري بخصوصية إن كان راضياً قبل طلب تقييم علني، ولا يذكر عرضاً إضافياً إلا بعد انتهاء مهلة الاسترداد.",
    "ai-customer-support-agent":
      "يجيب من قاعدة معرفة تتحكم بها، يقيس ثقته بنفسه، ويسلّم كل ما هو غير مؤكد لإنسان ومعه مسودة جاهزة.",
    "ai-lead-qualifier":
      "يقرأ كل استفسار وارد، يقيس النية والملاءمة، ويوجّه العملاء الجادين لإنسان فوراً بينما يذهب الباقي للرعاية.",
    "ai-product-translation":
      "يترجم نصوص المنتج لكل لغة تبيع بها، يحمي الأسعار وأسماء العلامات، يتجاهل النص غير المتغير، ويحدد اتجاه النص لـRTL.",
    "ai-sales-page-writer":
      "يحوّل حقائق المنتج إلى صفحة بيع منظمة — المشكلة، الدليل، ما تحصل عليه، الحدود الصادقة — ثم يفحصها من الادعاءات غير المدعومة.",
    "cv-screening-triage":
      "يقرأ كل طلب مقابل المتطلبات التي كتبتها ويرتّب المرشحين بأسباب معلنة — دون رفض أحد تلقائياً أبداً.",
    "automatic-invoice-vat":
      "يصدر فاتورة متسلسلة مرقّمة صحيحاً لكل طلب مدفوع، يطبّق نسب الضريبة، ويحفظ الأدلة التي تطلبها الجهات الضريبية.",
    "commission-affiliate-payouts":
      "يتتبع ما كسبه كل مسوّق، يعكس العمولة عند الاسترداد، يحفظ النسبة وقت البيع، وينتج أمر دفع واحداً بلا تكرار.",
    "sales-anomaly-detection":
      "يراقب حجم الطلبات مقابل نفس اليوم من الأسابيع الماضية ويخبرك إن كان الطلب انخفض أم أن مسارك تعطّل — ولكلٍ رد مختلف.",
    "sales-pipeline-followup":
      "يتتبع الصفقات المفتوحة، يقيس صمت كل منها، ويرسل ملخصاً يومياً بمن يحتاج متابعة — مرتّباً بالقيمة ومع مسودة لكل واحد.",
    "daily-business-pulse":
      "يقرأ ما كتبته بقية الأنظمة ويرسل رسالة يومية واحدة: ما يحتاج تدخلاً، وما استُرد، وما عمل.",
  },

  standards: {
    eyebrow: "المعيار",
    title1: "ست قواعد يجب أن يجتازها",
    titleAccent: "كل سير عمل",
    description:
      "ليست وعداً — بل بوابة بناء. المصنع الذي يولّد هذه الأنظمة يرفض كتابة ملف يخالف أياً منها، و١٥١ اختباراً سلوكياً تشغّل الكود الحقيقي لإثبات ذلك.",
    items: [
      {
        title: "صفر بيانات اعتماد مضمّنة",
        body: "لا مفتاح API ولا رمز ولا كلمة مرور داخل أي ملف. بيانات الاعتماد في مخزن n8n، يُشار إليها بالاسم.",
      },
      {
        title: "إعادة محاولة لكل نداء شبكة",
        body: "كل عقدة تلمس الشبكة تعيد المحاولة بتباعد متزايد. القاعدة رفض افتراضي: أي نوع عقدة جديد يُعامَل كبعيد حتى يثبت العكس.",
      },
      {
        title: "لكل عقدة مسار خطأ",
        body: "يُفحص لكل عقدة لا لكل ملف. سير عمل فيه عطل واحد معالج وخمسة غير معالجة لا يُبنى.",
      },
      {
        title: "حماية من إعادة الإرسال",
        body: "الويب هوك يصل مرتين. كل مدخل غير متكرر الأثر، فالوصول الثاني يُكتشف ويُهمَل بدل تحصيل أو إرسال مزدوج.",
      },
      {
        title: "لا شيء يفشل بصمت",
        body: "كل عطل يصل مركز الأخطاء مرتَّباً بأثره على العمل، مع كبح العواصف حتى لا يرسل انقطاع واحد ٤٠٠ تنبيه.",
      },
      {
        title: "يعمل مستضافاً ذاتياً لا سحابياً فقط",
        body: "لا استدعاء require لوحدات Node داخل عقد الكود — الفخ الكلاسيكي الذي يعمل عند الكاتب على السحابة ويفشل عند المشتري على تركيب ذاتي.",
      },
    ],
  },

  proof: {
    eyebrow: "دليل لا صفات",
    title1: "الاختبارات تُسلَّم",
    titleAccent: "مع الملفات",
    description:
      "كل حزمة تحتوي تقرير اختبار سير العمل الذي بداخلها. تقرأ ما اختُبر وما كان الادعاء قبل أن تثق بأي منها أمام عميل يدفع.",
    metrics: [
      { value: "151", label: "اختبار سلوكي", note: "كود حقيقي يُنفَّذ لا يُفحص نصياً" },
      { value: "14", label: "فحص سلامة البوابة", note: "اختبارات تتأكد أن البوابة نفسها تعمل" },
      { value: "23", label: "سير عمل", note: "كل واحد استُورد في n8n حي" },
      { value: "285", label: "عقدة", note: "معدودة، دون الملاحظات" },
    ],
    footnote:
      "فحوص سلامة البوابة موجودة لأن بوابة تمرر كل شيء أسوأ من غياب بوابة. كل فحص يكسر قاعدة عمداً ويُفشل البناء إن سمحت البوابة بمروره.",
  },

  books: {
    eyebrow: "أيضاً من إتقان",
    title1: "مكتبة",
    titleAccent: "التداول",
    description:
      "خط منتجات ثانوي منفصل: كتابان مؤسسيان في التداول، يُباعان عبر بوابة كريبتو خاصة بهما. لا علاقة لهما بأنظمة الأتمتة أعلاه.",
    cta: "تصفّح كتب التداول",
  },

  faq: {
    eyebrow: "الأسئلة الشائعة",
    title: "إجابات قبل أن تسأل.",
    description: "ماذا تحصل عليه، وكيف يُركَّب، وماذا يحدث حين يتعطل شيء.",
    items: [
      {
        q: "ماذا أستلم بالضبط بعد الدفع؟",
        a: "ملف ZIP فيه مجلد لكل سير عمل. كل مجلد يحوي ملف n8n JSON، وملف README يشرح كل قرار، وتقرير الاختبار لذلك السير. والحزمة تتضمن دليل تركيب مكتوباً بالترتيب الذي يجب أن تركّب به فعلاً، وملف ترخيص.",
      },
      {
        q: "هل أحتاج معرفة برمجية؟",
        a: "لا. تستورد ملف JSON في n8n وتملأ عقدة Config واحدة لكل سير عمل. عقد الكود مكتوبة ومختبَرة مسبقاً. إن كنت تستطيع نسخ مفتاح API من Stripe إلى حقل، تستطيع تركيب هذه.",
      },
      {
        q: "هل تعمل على n8n المستضاف ذاتياً أم السحابي فقط؟",
        a: "الاثنان، عمداً. من أشيع أعطال القوالب المنشورة عقدة كود تستدعي require('crypto') — تعمل على n8n السحابي وتفشل على تركيب ذاتي افتراضي ما لم يفعّل المشغّل NODE_FUNCTION_ALLOW_BUILTIN. هذه تستخدم عقدة Crypto المدمجة، فيعمل الملف نفسه في الحالتين.",
      },
      {
        q: "ما معنى «١٥١ اختباراً سلوكياً» فعلياً؟",
        a: "منفّذ n8n مصغّر يشغّل سير العمل الحقيقي: جافاسكربت عقد الكود الفعلية، وتوقيعات HMAC حقيقية، وشروط تفرّع حقيقية. الاختبارات تتحقق مما يفعله سير العمل — أن الويب هوك المكرر يُهمَل، وأن بريداً فاشلاً يذهب لمركز الأخطاء، وأن رابطاً منتهياً يعيد سبب الانتهاء. ليس فحصاً نصياً ولا فحص مخطط.",
      },
      {
        q: "ما بوابات الدفع المدعومة؟",
        a: "Stripe وPaddle وLemon Squeezy وGumroad وPayPal وNOWPayments تصل جميعها إلى نقطة تسليم واحدة، لكل منها تحقق توقيع خاص. إضافة سابعة تعني فرعاً واحداً في عقدة واحدة.",
      },
      {
        q: "هل يحتاج وكلاء الذكاء مفتاح OpenAI؟",
        a: "الخمسة وكلاء نعم. أما تقييم الاحتيال فلا، عمداً — يستخدم إشارات محلية فقط، فلا تخرج بيانات الطلبات من نظامك ولا تكلفة API لكل طلب.",
      },
      {
        q: "ماذا لو تعطل سير عمل بعد تحديث n8n؟",
        a: "التحديثات مشمولة مدى حياة المنتج. حين يصدر n8n تغييراً كاسراً في عقدة، يُعاد بناء الأنظمة المتأثرة، وتُختبر مقابل نفس الـ١٥١ ادعاءً، وتصلك الملفات الجديدة.",
      },
      {
        q: "هل أستخدمها في أعمال العملاء؟",
        a: "نعم. تستطيع تركيبها وتعديلها لعملك ولعملاء تبني لهم. لا تستطيع إعادة بيع ملفات سير العمل نفسها أو نشرها كمنتج قوالب. ملف الترخيص في كل حزمة يوضح ذلك كاملاً.",
      },
      {
        q: "بم تختلف عن القوالب المجانية على n8n.io؟",
        a: "غالباً فيما يحدث في اليوم السيئ. القالب المجاني يعرض المسار السعيد وعادةً بلا إعادة محاولة ولا حماية إعادة إرسال ولا مسار خطأ — وهذا مقبول في عرض تجريبي ومكلف في الإنتاج. الفرق هنا ليس ذكاءً بل القواعد الست أعلاه، مفروضة ببوابة بناء لا بالنيّة.",
      },
    ],
  },

  newsletter: {
    title: "أنظمة جديدة إلى بريدك",
    description:
      "رسالة قصيرة عند إصدار نظام جديد، وعند إعادة بناء نظام قائم بسبب تغيير كاسر في n8n، وعند تغيّر شيء في معيار البناء. لا شيء غير ذلك.",
    placeholder: "you@email.com",
    subscribe: "اشترك",
    joining: "جارٍ الاشتراك…",
    success: "تم تسجيلك في القائمة.",
    agree: "بالاشتراك توافق على استلام رسائل من حين لآخر. يمكنك إلغاء الاشتراك في أي وقت.",
    emailLabel: "البريد الإلكتروني",
  },

  footer: {
    tagline:
      "أنظمة n8n مُحصّنة للإنتاج، ووكلاء ذكاء اصطناعي، وقوالب سير عمل — مبنية على معيار منشور وتُسلَّم مع الاختبارات التي تثبته.",
    groups: {
      products: "المنتجات",
      resources: "الموارد",
    },
    links: {
      catalog: "كل الحزم",
      free: "الأداة المجانية",
      how: "كيف يعمل",
      standard: "المعيار",
      proof: "نتائج الاختبار",
      faq: "الأسئلة الشائعة",
      books: "كتب التداول",
    },
    disclaimerLabel: "إخلاء مسؤولية كتب التداول:",
  },

  finalCta: {
    title1: "ابدأ بالأداة المجانية.",
    titleAccent: "لا تشترِ شيئاً حتى تقتنع.",
    body: "نقطة التحميل الآمن مبنية بنفس معيار كل ما هنا — نفس البوابة، نفس الاختبارات، نفس التوثيق. ركّبها، اقرأ الكود، ثم قرّر.",
    primary: "حمّل الأداة المجانية",
    secondary: "شاهد كل الحزم",
  },
} as const;

/* ── Turkish ──────────────────────────────────────────────────────────── */

const tr = {
  hero: {
    badge: "23 üretime hazır iş akışı · 151 davranışsal test geçiyor",
    headline1: "Gerçek trafikte ayakta kalan",
    headlineAccent: "otomasyon",
    headline2: "— sadece demoda değil.",
    headlinePlain: "Gerçek trafikte ayakta kalan otomasyon — sadece demoda değil.",
    subtitle:
      "Gerçekten yayına alan insanlar için n8n sistemleri, yapay zeka ajanları ve iş akışı şablonları. Çoğu şablon bir kez, temiz bir çalıştırmada, yazarın makinesinde çalışır. Bunlar tekrar saldırılarına, ağ hatalarına, bozuk yüklere ve sessiz hatalara karşı test edildi — ve test sonuçları dosyalarla birlikte geliyor.",
    ctaPrimary: "Sistemlere göz at",
    ctaSecondary: "Ücretsiz araçla başla",
    trust: [
      "JSON olarak içe aktar — n8n Cloud'da veya kendi sunucunda çalışır",
      "Gömülü kimlik bilgisi yok",
      "Ömür boyu güncelleme dahil",
    ],
    stats: [
      { value: "23", label: "Teslim edilen iş akışı" },
      { value: "285", label: "Mühendislik yapılmış düğüm" },
      { value: "151", label: "Davranışsal test" },
      { value: "0", label: "Bilinen hata" },
    ],
  },

  integrations: {
    title: "Zaten kullandığın araçlar üzerine kurulu",
    note: "Her iş akışı düz n8n JSON olarak içe aktarılır. Özel çalışma zamanı yok, kilitlenme yok, bizde hesap açman gerekmiyor.",
    items: [
      "n8n",
      "OpenAI",
      "Stripe",
      "Lemon Squeezy",
      "Paddle",
      "Gumroad",
      "PayPal",
      "Slack",
      "SMTP / Gmail",
      "Airtable",
      "Google Sheets",
      "Webhooks",
    ],
  },

  how: {
    eyebrow: "Nasıl çalışır",
    title1: "Bir saatten",
    titleAccent: "kısa sürede çalışır",
    description:
      "Öğrenilecek bir çatı ya da yazılacak kod yok. Üç adım — ve üçüncüsü sistemin kendini denetlemesi.",
    steps: [
      {
        n: "01",
        title: "JSON'u içe aktar",
        body: "Her iş akışı standart bir n8n dışa aktarımıdır. n8n'i aç, dosyayı yapıştır, tuval eksiksiz görünsün — düğümler, bağlantılar ve her kararı açıklayan notlar.",
      },
      {
        n: "02",
        title: "Tek bir Config düğümü doldur",
        body: "Her iş akışı, değiştirmen gereken tüm değerleri tutan tek bir Config düğümüyle başlar. Kimlik bilgileri n8n'in kasasında kalır — dosyaya asla yazılmaz.",
      },
      {
        n: "03",
        title: "Setup Checker'ı çalıştır",
        body: "Kurulumunu sessiz hatalara yol açan yanlışlara karşı denetleyen bir iş akışı — bırakılmış varsayılan değerler, uyuşmayan imza anahtarları, eksik hata akışı — ve her biri için çözümü söyler.",
      },
    ],
  },

  catalog: {
    eyebrow: "Katalog",
    title1: "Yapay zeka sistemleri, araçları ve",
    titleAccent: "şablonları",
    description:
      "23 üretim iş akışından oluşan beş paket. Bugünkü sorununa uyanı al; her paket Setup Checker ve Central Error Hub içerir.",
    kinds: { tool: "Ücretsiz araç", system: "Sistem", suite: "Tam paket" },
    bestValue: "En iyi değer",
    free: "Ücretsiz",
    getFree: "Ücretsiz indir",
    getBundle: "Bu paketi al",
    seeInside: "İçinde ne var",
    workflowsLabel: "iş akışı",
    nodesLabel: "düğüm",
    payNote:
      "Tüm paketlerin ödemesi ve teslimatı Lemon Squeezy üzerinden yapılır. Aşağıdaki trading kütüphanesi kendi ödeme akışına sahip ayrı bir ürün hattıdır.",
    outcomesLabel: "Senin için ne yapar",
    useCasesLabel: "Ne için alınır",
    includesLabel: "Dahil iş akışları",
  },

  bundles: {
    "free-secure-downloads": {
      tagline: "Para harcamadan önce standardı gör",
      summary:
        "İmzalı bir indirme bağlantısını doğrulayan, süre ve indirme sınırını uygulayan ve her reddi boş bir 403 yerine somut bir gerekçeyle döndüren tek bir uç nokta. Buradaki her şeyin nasıl kurulduğunun en küçük eksiksiz örneği.",
      outcomes: [
        "Süresi dolan ve indirmeyi sınırlayan bağlantılar — paylaşılan URL çalışmayı bırakır",
        "Kendini açıklayan retler — süresi doldu, sınıra ulaşıldı, imza hatalı",
        "Çok sayıda IP'den kullanılan bağlantıları işaretler, sızıntı erken görünür",
        "Veritabanı gerekmez — durum n8n'in kendi deposunda tutulur",
      ],
      useCases: [
        "PDF veya ZIP satıyorsun ve bugün çıplak bir dosya bağlantısı yolluyorsun",
        "Paket almadan önce kod kalitesini görmek istiyorsun",
        "Arka uç kurmadan indirme koruması gerekiyor",
      ],
    },
    "delivery-essentials": {
      tagline: "Müşteriler dosyalarını alamadığında",
      summary:
        "Onaylanmış ödemeden alıcının gelen kutusundaki dosyaya kadar tüm yol, altı ödeme sağlayıcısı üzerinden — artı işler ters gittiğinde devreye giren iki iş akışı: alıcı indiremediğinde otomatik yeniden düzenleme ve geçmiş alıcılara taze bağlantılı güncelleme yayını.",
      outcomes: [
        "Tek uç nokta Stripe, Paddle, Lemon Squeezy, Gumroad, PayPal ve NOWPayments'i kabul eder",
        "Tekrar koruması — iki kez gelen webhook dosyayı iki kez göndermez",
        "'Dosyamı indiremiyorum' otomatik yanıtlanır, hız sınırı ve insana yükseltme ile",
        "Güncelleme yayınla, her eski alıcı taze imzalı bağlantı alsın — gönderim itibarını koruyan gruplarla",
      ],
      useCases: [
        "Dijital ürün satıyorsun ve hiç almayanlara iade yapıyorsun",
        "İndirme destek talepleri gününü yiyor",
        "Güncelleme yayınlıyorsun ve herkese elle e-posta atmak imkânsız",
      ],
    },
    "revenue-protection": {
      tagline: "Zaten kazandığın parayı kaybederken",
      summary:
        "Satıştan sonra sızan gelire yönelik beş iş akışı: teslimattan önce puanlanan dolandırıcılık, henüz uyarıyken yakalanan ters ibrazlar, sızdıran hesaba kadar izlenen dosyalar ve zamanlanmış bir diziyle kurtarılan iki tür başarısız ödeme.",
      outcomes: [
        "Teslimattan önce yalnızca yerel sinyallerle dolandırıcılık puanlaması — ücretli API yok, veri dışarı çıkmaz",
        "Ters ibraz uyarıları iade-mi-itiraz-mı önerisiyle ayrıştırılır, kanıt paketi hazırlanır",
        "Alıcıya özel filigran sızan dosyayı sızdıran hesaba kadar izler, kaldırma bildirimi taslak halinde",
        "Terk edilmiş sepetler ve başarısız abonelik ödemeleri varsayılan olarak indirim yapmadan kurtarılır",
      ],
      useCases: [
        "Ters ibraz oranın ödeme hesaplarını kapattıran seviyeye tırmanıyor",
        "Ürünün paylaşılıyor ve kimin yaptığını kanıtlayamıyorsun",
        "Başarısız yenilemeler kazandığın müşterileri sessizce kaybettiriyor",
      ],
    },
    "ai-agents": {
      tagline: "Elle yapılan işte boğulduğunda",
      summary:
        "Uydurmak yerine reddetmek üzere kurulmuş beş yapay zeka ajanı. Her biri güvenini bildirir, emin olmadığında insana devreder ve tek başına geri alınamaz bir işlem yapmaz — destek, müşteri niteleme, çeviri, satış metni ve CV eleme.",
      outcomes: [
        "Kendi bilgi tabanından yanıtlayan, güvenini puanlayan ve taslağı hazır şekilde devreden bir destek ajanı",
        "Ciddi alıcıyı dört meraklının arkasında bekletmeden doğrudan insana yönlendiren bir niteleyici",
        "Fiyatları, marka adlarını ve biçimlendirmeyi koruyan çeviri — RTL'in doğru görünmesi için metin yönü ile",
        "Gerekçesini bildirerek sıralayan ve kimseyi otomatik elemeyen CV taraması",
      ],
      useCases: [
        "Aynı beş destek sorusu her gün geliyor",
        "Birkaç dilde satıyorsun ve metni güncellemek bir hafta sürüyor",
        "İşe alım: çok başvuru var, adil okumaya vakit yok",
      ],
    },
    "complete-suite": {
      tagline: "Dijital bir iş için eksiksiz işletim sistemi",
      summary:
        "23 iş akışının tamamı — teslimat, gelir koruma, yapay zeka ajanları — artı ancak diğer her şey çalışırken anlam kazanan dördü: sıralı KDV faturalandırma, ortaklık komisyon ödemeleri, satış anomali tespiti ve diğer iş akışlarının yazdığını okuyan günlük nabız.",
      outcomes: [
        "Yukarıdaki üç sistemin tamamı, toplamlarının altında bir fiyatla",
        "Vergi otoritelerinin istediği kanıtlarla doğru numaralandırılmış sıralı faturalar",
        "İzlenen, iadede geri alınan ve tek bir ödeme talimatında tekilleştirilen komisyonlar",
        "Günde tek mesaj: müdahale gerekenler, kurtarılanlar ve çalışanlar",
      ],
      useCases: [
        "Tek bir sızıntıyı yamamak yerine işi kuruyorsun",
        "Faturalandırma, analitik ve ödeme tarafının da çözülmesini istiyorsun",
        "Altı ayda paket toplamaktansa bir kez kurmayı tercih ediyorsun",
      ],
    },
  },

  categories: {
    delivery: "Teslimat",
    protection: "Koruma",
    agent: "Yapay zeka ajanı",
    growth: "Gelir",
    finance: "Finans",
    ops: "Operasyon",
  },
  triggers: {
    webhook: "Webhook",
    schedule: "Zamanlanmış",
    manual: "Manuel",
    error: "Hata anında",
  },

  workflows: {
    "instant-digital-delivery":
      "Herhangi bir büyük sağlayıcıdan gelen onaylı ödemeyi, alıcının gelen kutusunda imzalı ve süreli bir indirme bağlantısına çeviren tek uç nokta.",
    "secure-download-endpoint":
      "İmzalı indirme bağlantısını doğrular, süreyi ve indirme sınırını uygular, her reddi boş 403 yerine somut gerekçeyle döndürür.",
    "product-update-broadcast":
      "Eski alıcılara taze imzalı bağlantıyla güncelleme bildirir — yalnızca gerçek alıcılara, sürüm başına tekilleştirilmiş, itibarı koruyan gruplarla.",
    "download-problem-self-service":
      "Satıcının gelen kutusuna hâkim olan mesajı — 'dosyamı alamıyorum' — hak sahipliğini doğrulayıp otomatik yeni bağlantı üreterek çözer.",
    "delivery-test-runner":
      "Canlı teslimat uç noktana üç senaryo gönderir ve teslimatın, tekrar korumasının ve ödeme kontrolünün doğru davrandığını raporlar.",
    "setup-checker":
      "Kurulumu sessiz hataya yol açan yanlışlara karşı denetler — bırakılmış varsayılanlar, uyuşmayan anahtarlar, eksik hata akışı — her biri için çözümüyle.",
    "central-error-hub":
      "Tüm iş akışlarından hataları toplar, iş etkisine göre sıralar, tekrar fırtınalarını bastırır ve her birini harekete geçirilebilir dille açıklar.",
    "pre-payment-fraud-scoring":
      "Her siparişi teslimattan önce yalnızca yerel sinyallerle puanlar — geçici alan adları, hız, coğrafi uyumsuzluk, tutar anomalileri.",
    "chargeback-early-warning":
      "Dolandırıcılık uyarılarını resmî itiraza dönüşmeden yakalar, gerekçesiyle iade-mi-itiraz-mı önerir ve kanıt paketini otomatik hazırlar.",
    "leak-detection-watermarking":
      "Her kopyayı alıcıya özel işaretler, indirme davranışından paylaşımı tespit eder, sızıntıyı hesabına kadar izler ve kaldırma bildirimini taslaklar.",
    "cart-abandonment-recovery":
      "Yarım kalan ödemeleri, alıcı satın aldığı anda duran zamanlanmış iki mesajlık diziyle kurtarır — indirim varsayılan olarak kapalı.",
    "failed-payment-recovery":
      "Başarısız abonelik ödemelerini anında yakalar ve kart güncellenene ya da dizi bitene kadar kademeli bir kurtarma dizisi çalıştırır.",
    "post-purchase-sequence":
      "Önce yardım eder, sonra ister — herkese açık yorum istemeden önce alıcının memnun olup olmadığını özel olarak sorar ve ek satışı ancak iade süresi kapandıktan sonra anar.",
    "ai-customer-support-agent":
      "Senin kontrolündeki bilgi tabanından yanıtlar, kendi güvenini puanlar ve emin olmadığı her şeyi taslağı hazır şekilde bir insana devreder.",
    "ai-lead-qualifier":
      "Her gelen talebi okur, niyet ve uygunluğu puanlar, sıcak müşterileri doğrudan insana yönlendirir, gerisini besleme akışına alır.",
    "ai-product-translation":
      "Ürün metnini sattığın her dile çevirir, fiyatları ve marka adlarını korur, değişmeyen metni atlar ve RTL için metin yönü üretir.",
    "ai-sales-page-writer":
      "Ürün gerçeklerini yapılandırılmış bir satış sayfasına çevirir — sorun, kanıt, ne alıyorsun, dürüst sınırlar — sonra desteksiz iddialara karşı tarar.",
    "cv-screening-triage":
      "Her başvuruyu yazdığın gereksinimlere göre okur ve adayları gerekçesini bildirerek sıralar — kimseyi otomatik elemeden.",
    "automatic-invoice-vat":
      "Her ödenmiş sipariş için doğru numaralı sıralı fatura keser, vergi oranlarını uygular ve otoritelerin istediği kanıtları kaydeder.",
    "commission-affiliate-payouts":
      "Her ortağın kazancını izler, iadede komisyonu geri alır, satış anındaki oranı korur ve tekilleştirilmiş tek bir ödeme talimatı üretir.",
    "sales-anomaly-detection":
      "Sipariş hacmini son haftaların aynı gününe karşı izler ve talebin mi düştüğünü yoksa hattının mı bozulduğunu söyler — ikisi zıt tepki ister.",
    "sales-pipeline-followup":
      "Açık fırsatları izler, her birinin ne kadardır sessiz olduğunu ölçer ve kimin aranması gerektiğine dair günlük tek özet gönderir — değere göre sıralı, her biri için taslakla.",
    "daily-business-pulse":
      "Diğer iş akışlarının zaten yazdığı veriyi okur ve günde tek mesaj gönderir: müdahale gerekenler, kurtarılanlar ve çalışanlar.",
  },

  standards: {
    eyebrow: "Standart",
    title1: "Her iş akışının geçmesi gereken",
    titleAccent: "altı kural",
    description:
      "Bir vaat değil — bir yapı kapısı. Bu iş akışlarını üreten fabrika, bunlardan herhangi birini ihlal eden bir dosyayı yazmayı reddeder ve 151 davranışsal test bunu kanıtlamak için gerçek kodu çalıştırır.",
    items: [
      {
        title: "Gömülü kimlik bilgisi yok",
        body: "Hiçbir dosyada tek bir API anahtarı, token veya parola yok. Kimlik bilgileri n8n'in kasasında durur, adıyla çağrılır.",
      },
      {
        title: "Her ağ çağrısında yeniden deneme",
        body: "Ağa dokunan her düğüm artan beklemeyle yeniden dener. Kural varsayılan-ret: yeni bir düğüm tipi, aksi kanıtlanana dek uzak sayılır.",
      },
      {
        title: "Her düğümün bir hata yolu var",
        body: "Dosya başına değil düğüm başına denetlenir. Bir hatası ele alınmış, beşi alınmamış bir iş akışı derlenmez.",
      },
      {
        title: "Tekrar koruması",
        body: "Webhook'lar iki kez gelir. Her giriş noktası idempotenttir; ikinci teslimat tanınır ve düşürülür, iki kez tahsilat ya da e-posta olmaz.",
      },
      {
        title: "Hiçbir şey sessizce başarısız olmaz",
        body: "Her hata iş etkisine göre sıralanmış olarak Central Error Hub'a ulaşır; tekrar fırtınaları bastırılır, tek kesinti 400 uyarı göndermez.",
      },
      {
        title: "Yalnızca Cloud'da değil, kendi sunucunda da çalışır",
        body: "Kod düğümlerinde Node yerleşiklerini require etmek yok — yazarı için n8n Cloud'da çalışıp alıcısı için varsayılan kendi kurulumunda patlayan klasik tuzak.",
      },
    ],
  },

  proof: {
    eyebrow: "Sıfat değil kanıt",
    title1: "Testler dosyalarla",
    titleAccent: "birlikte geliyor",
    description:
      "Her paket, içindeki iş akışlarının test raporunu içerir. Ödeme yapan bir müşterinin önünde herhangi birine güvenmeden önce neyin test edildiğini ve iddianın ne olduğunu okuyabilirsin.",
    metrics: [
      { value: "151", label: "Davranışsal test", note: "Gerçek kod çalıştırıldı, lint değil" },
      { value: "14", label: "Kapı bütünlüğü sondası", note: "Kapının kendisinin çalıştığını sınayan testler" },
      { value: "23", label: "İş akışı", note: "Her biri canlı n8n'e aktarıldı" },
      { value: "285", label: "Düğüm", note: "Sayıldı, yapışkan notlar hariç" },
    ],
    footnote:
      "Kapı sondaları var çünkü her şeyi geçiren bir yapı kapısı, kapı olmamasından kötüdür. Her sonda bir kuralı bilerek çiğner ve kapı geçirirse yapıyı başarısız kılar.",
  },

  books: {
    eyebrow: "Ayrıca Etqan'dan",
    title1: "Trading",
    titleAccent: "kütüphanesi",
    description:
      "Ayrı, ikincil bir ürün hattı: kendi kripto ödeme akışıyla satılan iki kurumsal trading kitabı. Yukarıdaki otomasyon sistemleriyle ilgisi yok.",
    cta: "Trading kitaplarına göz at",
  },

  faq: {
    eyebrow: "SSS",
    title: "Sormadan önce cevaplar.",
    description: "Ne alıyorsun, nasıl kuruluyor ve bir şey bozulduğunda ne oluyor.",
    items: [
      {
        q: "Ödemeden sonra tam olarak ne alıyorum?",
        a: "Her iş akışı için bir klasör içeren bir ZIP. Her klasörde n8n iş akışı JSON'u, her kararı açıklayan bir README ve o iş akışının test raporu var. Paket ayrıca gerçekten kurman gereken sırayla yazılmış bir KURULUM rehberi ve bir lisans dosyası içerir.",
      },
      {
        q: "Kod bilmem gerekiyor mu?",
        a: "Hayır. n8n'e bir JSON dosyası aktarıyor ve iş akışı başına tek bir Config düğümü dolduruyorsun. Kod düğümleri yazılmış ve test edilmiş durumda. Stripe'tan bir API anahtarını kopyalayıp bir forma yapıştırabiliyorsan bunları kurabilirsin.",
      },
      {
        q: "Kendi sunucumdaki n8n'de mi yoksa sadece n8n Cloud'da mı çalışıyor?",
        a: "Bilerek ikisinde de. Yayınlanmış şablonlarda sık görülen bir hata, require('crypto') çağıran bir Kod düğümüdür — bu n8n Cloud'da çalışır ama operatör NODE_FUNCTION_ALLOW_BUILTIN ayarlamadıkça varsayılan kendi kurulumunda patlar. Bunlar n8n'in yerleşik Crypto düğümünü kullanır, böylece aynı dosya iki yerde de çalışır.",
      },
      {
        q: "'151 davranışsal test' aslında ne demek?",
        a: "Minimal bir n8n yürütücüsü gerçek iş akışlarını çalıştırır: gerçek Kod düğümü JavaScript'i, gerçek HMAC imzaları, gerçek dallanma koşulları. Testler iş akışının ne yaptığını doğrular — tekrarlanan bir webhook'un düşürüldüğünü, başarısız bir e-postanın hata merkezine gittiğini, süresi dolmuş bir bağlantının süre gerekçesini döndürdüğünü. Bu bir lint ya da şema kontrolü değil.",
      },
      {
        q: "Hangi ödeme sağlayıcıları destekleniyor?",
        a: "Stripe, Paddle, Lemon Squeezy, Gumroad, PayPal ve NOWPayments her biri kendi imza doğrulamasıyla tek bir teslimat uç noktasına gelir. Yedincisini eklemek tek düğümde tek dal demektir.",
      },
      {
        q: "Yapay zeka ajanları OpenAI anahtarı istiyor mu?",
        a: "Beş ajan iş akışı istiyor. Dolandırıcılık puanlama iş akışı bilerek istemiyor — yalnızca yerel sinyaller kullanır, sipariş verisi sisteminden çıkmaz ve sipariş başına API maliyeti olmaz.",
      },
      {
        q: "Bir n8n güncellemesinden sonra bir iş akışı bozulursa?",
        a: "Güncellemeler ürünün ömrü boyunca dahildir. n8n bozucu bir düğüm değişikliği yayınladığında etkilenen iş akışları yeniden derlenir, aynı 151 iddiaya karşı yeniden test edilir ve yeni dosyalar sana gelir.",
      },
      {
        q: "Bunları müşteri işlerinde kullanabilir miyim?",
        a: "Evet. Kendi işin ve iş yaptığın müşteriler için kurabilir ve değiştirebilirsin. İş akışı dosyalarının kendisini şablon ürünü olarak yeniden satamaz veya yayınlayamazsın. Her paketteki lisans dosyası bunu tam olarak yazar.",
      },
      {
        q: "Bu n8n.io'daki ücretsiz şablonlardan nasıl farklı?",
        a: "Çoğunlukla kötü günde olanlarla. Ücretsiz bir şablon mutlu yolu gösterir ve genelde yeniden deneme, tekrar koruması ve hata yolu içermez — demo için sorun değil, üretimde pahalı. Buradaki fark zekâ değil, niyetle değil bir yapı kapısıyla dayatılan yukarıdaki altı kural.",
      },
    ],
  },

  newsletter: {
    title: "Yeni iş akışları, gelen kutunda",
    description:
      "Yeni bir sistem yayınlandığında, mevcut bir sistem n8n'in bozucu değişikliği için yeniden derlendiğinde ve yapı standardında bir şey değiştiğinde kısa bir not. Başka hiçbir şey.",
    placeholder: "you@email.com",
    subscribe: "Abone ol",
    joining: "Kaydediliyor…",
    success: "Listeye eklendin.",
    agree: "Abone olarak ara sıra e-posta almayı kabul edersin. İstediğin zaman çıkabilirsin.",
    emailLabel: "E-posta adresi",
  },

  footer: {
    tagline:
      "Üretime dayanıklı n8n sistemleri, yapay zeka ajanları ve iş akışı şablonları — yayınlanmış bir standarda göre kurulur ve bunu kanıtlayan testlerle birlikte gelir.",
    groups: {
      products: "Ürünler",
      resources: "Kaynaklar",
    },
    links: {
      catalog: "Tüm paketler",
      free: "Ücretsiz araç",
      how: "Nasıl çalışır",
      standard: "Standart",
      proof: "Test sonuçları",
      faq: "SSS",
      books: "Trading kitapları",
    },
    disclaimerLabel: "Trading kitapları sorumluluk reddi:",
  },

  finalCta: {
    title1: "Ücretsiz araçla başla.",
    titleAccent: "Seni ikna edene kadar hiçbir şey satın alma.",
    body: "Secure Download Endpoint, buradaki her şeyle aynı yapı standardında — aynı kapı, aynı testler, aynı belgeler. Kur, kodu oku, sonra karar ver.",
    primary: "Ücretsiz aracı indir",
    secondary: "Tüm paketleri gör",
  },
} as const;

export type MarketplaceCopy = typeof en;

const copy: Record<Locale, MarketplaceCopy> = {
  en,
  // The three locales are structurally identical by construction; the casts
  // keep the readonly literal types from fighting each other while still
  // failing the build if a key goes missing.
  ar: ar as unknown as MarketplaceCopy,
  tr: tr as unknown as MarketplaceCopy,
};

export function getMarketplaceCopy(locale: Locale): MarketplaceCopy {
  return copy[locale] ?? en;
}
