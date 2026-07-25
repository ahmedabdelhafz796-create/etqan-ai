/* ============================================================
   E-TQAN — BOOK APPENDIX BUILDER
   ============================================================
   Produces the closing reference chapter every premium E-tqan
   title ends with: summary, cheat sheet, glossary, learning
   roadmap and references — fully localized (EN / AR / TR).

   Content is per-course and authored here so all 32 book
   editions share one maintained source of reference material.
   ============================================================ */

import { chapter, p, lead, summary, cheatSheet, glossary, references, roadmap } from "./dsl.mjs";

const L = {
  en: {
    eyebrow: "Appendix · Reference",
    title: "Reference, Cheat Sheets & Roadmap",
    intro:
      "Everything you need after the chapters: the key takeaways, a printable cheat sheet, a glossary of every term used, a staged learning roadmap, and where to go deeper.",
    goals: ["Review the essentials at a glance", "Keep a cheat sheet beside you while you build", "Look up any term quickly", "Follow a realistic study plan"],
    lead: "Bookmark this chapter. It is designed to be the page you return to long after the first read — a working reference rather than a recap.",
    sSummary: "Key Takeaways",
    sCheat: "Cheat Sheet",
    sGloss: "Glossary",
    sRoad: "Learning Roadmap",
    sRefs: "References & Further Reading",
  },
  ar: {
    eyebrow: "الملحق · مرجع",
    title: "المرجع وأوراق الغشّ وخارطة الطريق",
    intro:
      "كل ما تحتاجه بعد الفصول: أهمّ الخلاصات، وورقة غشّ قابلة للطباعة، ومسرد لكل مصطلح استُخدم، وخارطة تعلُّم مرحلية، وأين تتعمّق أكثر.",
    goals: ["مراجعة الأساسيات بلمحة", "إبقاء ورقة الغشّ بجانبك أثناء البناء", "البحث عن أي مصطلح سريعًا", "اتّباع خطة دراسة واقعية"],
    lead: "ضع علامة على هذا الفصل. صُمِّم ليكون الصفحة التي تعود إليها بعد القراءة الأولى بزمن طويل — مرجعًا عمليًا لا مجرّد تلخيص.",
    sSummary: "أهمّ الخلاصات",
    sCheat: "ورقة الغشّ",
    sGloss: "المسرد",
    sRoad: "خارطة التعلُّم",
    sRefs: "المراجع وقراءات إضافية",
  },
  tr: {
    eyebrow: "Ek · Referans",
    title: "Referans, Kopya Kâğıdı ve Yol Haritası",
    intro:
      "Bölümlerden sonra ihtiyacın olan her şey: temel çıkarımlar, yazdırılabilir bir kopya kâğıdı, kullanılan her terimin sözlüğü, aşamalı bir öğrenme yol haritası ve daha derine inebileceğin kaynaklar.",
    goals: ["Temelleri bir bakışta gözden geçir", "Kurarken kopya kâğıdını yanında tut", "Herhangi bir terimi hızlıca ara", "Gerçekçi bir çalışma planı izle"],
    lead: "Bu bölümü işaretle. İlk okumadan çok sonra da geri döneceğin sayfa olarak tasarlandı — bir özet değil, çalışan bir referans.",
    sSummary: "Temel Çıkarımlar",
    sCheat: "Kopya Kâğıdı",
    sGloss: "Sözlük",
    sRoad: "Öğrenme Yol Haritası",
    sRefs: "Kaynaklar ve İleri Okuma",
  },
};

/** Shared, language-neutral reference links (names/URLs stay in English). */
const COMMON_REFS = {
  python: [
    { name: "Official Python Documentation", url: "https://docs.python.org/3/", note: "the definitive reference" },
    { name: "PEP 8 — Style Guide for Python Code", url: "https://peps.python.org/pep-0008/" },
    { name: "pandas User Guide", url: "https://pandas.pydata.org/docs/user_guide/" },
    { name: "Real Python", url: "https://realpython.com", note: "practical tutorials" },
  ],
  javascript: [
    { name: "MDN Web Docs — JavaScript", url: "https://developer.mozilla.org/en-US/docs/Web/JavaScript", note: "the reference every professional uses" },
    { name: "javascript.info", url: "https://javascript.info", note: "modern, thorough tutorial" },
    { name: "Node.js Documentation", url: "https://nodejs.org/docs/latest/api/" },
    { name: "Can I Use", url: "https://caniuse.com", note: "browser support tables" },
  ],
  java: [
    { name: "Oracle Java Documentation", url: "https://docs.oracle.com/en/java/" },
    { name: "OpenJDK", url: "https://openjdk.org" },
    { name: "Spring Framework Guides", url: "https://spring.io/guides", note: "for backend work" },
    { name: "Baeldung", url: "https://www.baeldung.com", note: "practical Java articles" },
  ],
  html: [
    { name: "MDN Web Docs — HTML", url: "https://developer.mozilla.org/en-US/docs/Web/HTML" },
    { name: "W3C Markup Validator", url: "https://validator.w3.org", note: "validate every page" },
    { name: "WAI-ARIA Authoring Practices", url: "https://www.w3.org/WAI/ARIA/apg/", note: "accessibility patterns" },
    { name: "HTML Living Standard", url: "https://html.spec.whatwg.org" },
  ],
  css: [
    { name: "MDN Web Docs — CSS", url: "https://developer.mozilla.org/en-US/docs/Web/CSS" },
    { name: "A Complete Guide to Flexbox", url: "https://css-tricks.com/snippets/css/a-guide-to-flexbox/" },
    { name: "A Complete Guide to Grid", url: "https://css-tricks.com/snippets/css/complete-guide-grid/" },
    { name: "Coolors", url: "https://coolors.co", note: "palette generator" },
  ],
  sql: [
    { name: "PostgreSQL Documentation", url: "https://www.postgresql.org/docs/" },
    { name: "MySQL Reference Manual", url: "https://dev.mysql.com/doc/" },
    { name: "SQLite Documentation", url: "https://sqlite.org/docs.html" },
    { name: "Use The Index, Luke", url: "https://use-the-index-luke.com", note: "indexing & performance" },
  ],
  "ai-app-building": [
    { name: "OpenAI Platform Docs", url: "https://platform.openai.com/docs" },
    { name: "Anthropic Claude Docs", url: "https://docs.claude.com" },
    { name: "Vercel Documentation", url: "https://vercel.com/docs", note: "deployment" },
    { name: "React Documentation", url: "https://react.dev" },
  ],
  "building-websites": [
    { name: "MDN Web Docs", url: "https://developer.mozilla.org", note: "the web platform reference" },
    { name: "Next.js Documentation", url: "https://nextjs.org/docs" },
    { name: "web.dev", url: "https://web.dev", note: "performance & best practices" },
    { name: "OWASP Top Ten", url: "https://owasp.org/www-project-top-ten/", note: "web security basics" },
  ],
  "excel-ai": [
    { name: "Microsoft Excel Functions (A–Z)", url: "https://support.microsoft.com/en-us/office/excel-functions-alphabetical-b3944572-255d-4efb-bb96-c6d90033e188" },
    { name: "Microsoft Copilot in Excel", url: "https://support.microsoft.com/copilot-excel" },
    { name: "Power Query Documentation", url: "https://learn.microsoft.com/power-query/" },
    { name: "ExcelJet", url: "https://exceljet.net", note: "formula recipes" },
  ],
  "design-graphics": [
    { name: "Google Fonts", url: "https://fonts.google.com" },
    { name: "Adobe Color", url: "https://color.adobe.com" },
    { name: "Refactoring UI", note: "practical visual design principles" },
    { name: "Figma Learn", url: "https://help.figma.com" },
  ],
  "ai-arsenal": [
    { name: "Anthropic Claude Docs", url: "https://docs.claude.com" },
    { name: "OpenAI Platform Docs", url: "https://platform.openai.com/docs" },
    { name: "Hugging Face", url: "https://huggingface.co", note: "open models & datasets" },
    { name: "Y Combinator Library", url: "https://www.ycombinator.com/library", note: "startup fundamentals" },
  ],
};

/* Per-course, per-language appendix content. */
const DATA = {
  python: {
    en: {
      takeaways: [
        "A program transforms input into output — you design the logic in the middle.",
        "Python is high-level, interpreted and dynamically typed; that is why it feels effortless.",
        "Indentation *is* the syntax: four spaces define every block.",
        "Choose the right data structure (list, dict, tuple, set) and clean code follows.",
        "Functions with clear names, type hints and docstrings are the mark of a professional.",
        "Classes model things that have both data and behavior — reach for them when that fits.",
        "Handle specific exceptions and always open files with `with`.",
        "`pandas` turns raw files into decisions; `groupby` answers most business questions.",
        "Skill comes from reps: build small projects relentlessly.",
      ],
      cheats: [
        { t: "Core syntax", rows: [["name = value", "assign a variable"], ["f\"{x}\"", "f-string interpolation"], ["if / elif / else", "branch"], ["for x in seq:", "iterate values"], ["while cond:", "loop until false"], ["def f(a, b=1):", "function with default"]] },
        { t: "Data structures", rows: [["[1,2,3]", "list — ordered, mutable"], ["(1,2)", "tuple — immutable"], ["{\"k\": v}", "dict — key → value"], ["{1,2,3}", "set — unique"], ["lst[1:3]", "slice (stop exclusive)"], ["lst[::-1]", "reversed copy"]] },
        { t: "Useful built-ins", rows: [["len(x)", "size"], ["range(n)", "0…n-1"], ["enumerate(x)", "index + value"], ["zip(a, b)", "pair up"], ["sorted(x)", "sorted copy"], ["sum/min/max", "aggregate"]] },
        { t: "Files & errors", rows: [["with open(p, encoding=\"utf-8\")", "safe file access"], ["try / except E", "catch a specific error"], ["finally", "always runs"], ["json.loads / dumps", "JSON ↔ dict"], ["pathlib.Path", "modern file paths"], ["python -m venv .venv", "virtual environment"]] },
      ],
      terms: [
        { term: "Variable", def: "A name that points to a value." },
        { term: "Dynamic typing", def: "Python infers a value's type at runtime; you never declare it." },
        { term: "Interpreter", def: "The program that runs your Python line by line, with no separate compile step." },
        { term: "f-string", def: "A string prefixed with `f` where `{expressions}` are evaluated inline." },
        { term: "List comprehension", def: "A one-line expression that builds a list, e.g. `[x*2 for x in xs]`." },
        { term: "Immutable", def: "A value that cannot be changed after creation (tuples, strings)." },
        { term: "Docstring", def: "The triple-quoted description directly under a `def` or `class`." },
        { term: "Type hint", def: "An annotation such as `price: float` that documents intent without enforcing it at runtime." },
        { term: "Exception", def: "An error object raised at runtime that you can catch with `try/except`." },
        { term: "Virtual environment", def: "An isolated per-project package directory created with `python -m venv`." },
        { term: "Module", def: "A `.py` file whose names you can `import` elsewhere." },
        { term: "OOP", def: "Object-oriented programming — modelling data plus behavior as classes and objects." },
        { term: "DataFrame", def: "The pandas table structure: labelled rows and columns." },
        { term: "groupby", def: "A pandas/SQL operation that splits data into groups, aggregates each, and combines results." },
      ],
      stages: [
        { when: "Week 1–2", focus: "Chapters 1–4: mindset, setup, variables & types, control flow. Type every example." },
        { when: "Week 3", focus: "Chapter 5: lists, dicts, tuples, sets and comprehensions." },
        { when: "Week 4", focus: "Chapters 6–7: clean functions, then object-oriented design." },
        { when: "Week 5", focus: "Chapter 8: exceptions, files, modules and pip." },
        { when: "Week 6–8", focus: "Chapters 9–10: pandas analysis, then build and extend the capstone." },
      ],
    },
    ar: {
      takeaways: [
        "البرنامج يحوّل مُدخلًا إلى مُخرَج — وأنت تصمّم المنطق في الوسط.",
        "بايثون عالية المستوى ومُفسَّرة وديناميكية الأنواع؛ لذلك تبدو سلسة.",
        "المسافة البادئة *هي* الصياغة: أربع مسافات تُعرّف كل كتلة.",
        "اختر هيكل البيانات الصحيح (قائمة، قاموس، صف، مجموعة) فيتبعه كود نظيف.",
        "الدوال بأسماء واضحة وتلميحات أنواع وسلاسل توثيق علامة المحترف.",
        "الأصناف تُنمذِج ما له بيانات وسلوك معًا — استخدمها حين يناسب ذلك.",
        "التقط الاستثناءات المحدّدة، وافتح الملفات دائمًا بـ `with`.",
        "‏`pandas` يحوّل الملفات الخام إلى قرارات؛ و`groupby` يجيب معظم أسئلة العمل.",
        "المهارة من التكرار: ابنِ مشاريع صغيرة بلا توقّف.",
      ],
      cheats: [
        { t: "الصياغة الأساسية", rows: [["name = value", "إسناد متغيّر"], ["f\"{x}\"", "دمج داخل f-string"], ["if / elif / else", "تفريع"], ["for x in seq:", "المرور على القيم"], ["while cond:", "تكرار حتى الخطأ"], ["def f(a, b=1):", "دالة بقيمة افتراضية"]] },
        { t: "هياكل البيانات", rows: [["[1,2,3]", "قائمة — مرتّبة وقابلة للتغيير"], ["(1,2)", "صف — غير قابل للتغيير"], ["{\"k\": v}", "قاموس — مفتاح ← قيمة"], ["{1,2,3}", "مجموعة — فريدة"], ["lst[1:3]", "تقطيع (النهاية غير شاملة)"], ["lst[::-1]", "نسخة معكوسة"]] },
        { t: "دوال مضمّنة مفيدة", rows: [["len(x)", "الحجم"], ["range(n)", "من 0 إلى n-1"], ["enumerate(x)", "فهرس + قيمة"], ["zip(a, b)", "ازدواج"], ["sorted(x)", "نسخة مرتّبة"], ["sum/min/max", "تجميع"]] },
        { t: "الملفات والأخطاء", rows: [["with open(p, encoding=\"utf-8\")", "وصول آمن للملف"], ["try / except E", "التقاط خطأ محدّد"], ["finally", "تعمل دائمًا"], ["json.loads / dumps", "JSON ↔ قاموس"], ["pathlib.Path", "مسارات حديثة"], ["python -m venv .venv", "بيئة افتراضية"]] },
      ],
      terms: [
        { term: "المتغيّر", def: "اسم يشير إلى قيمة." },
        { term: "ديناميكية الأنواع", def: "تستنتج بايثون نوع القيمة وقت التشغيل؛ ولا تصرّح به أبدًا." },
        { term: "المُفسِّر", def: "البرنامج الذي يشغّل كودك سطرًا بسطر بلا خطوة ترجمة منفصلة." },
        { term: "f-string", def: "نص يبدأ بـ `f` وتُقيَّم فيه `{التعبيرات}` مباشرةً." },
        { term: "استيعاب القوائم", def: "تعبير من سطر واحد يبني قائمة، مثل `[x*2 for x in xs]`." },
        { term: "غير قابل للتغيير", def: "قيمة لا يمكن تعديلها بعد إنشائها (الصفوف، النصوص)." },
        { term: "سلسلة التوثيق", def: "الوصف بين ثلاث علامات اقتباس أسفل `def` أو `class` مباشرةً." },
        { term: "تلميح النوع", def: "تعليق مثل `price: float` يوثّق النيّة دون فرضها وقت التشغيل." },
        { term: "الاستثناء", def: "كائن خطأ يُرمى وقت التشغيل وتستطيع التقاطه بـ `try/except`." },
        { term: "البيئة الافتراضية", def: "مجلد حزم معزول لكل مشروع يُنشأ بـ `python -m venv`." },
        { term: "الوحدة", def: "ملف `.py` تستطيع استيراد أسمائه في مكان آخر." },
        { term: "البرمجة الكائنية", def: "نمذجة البيانات مع السلوك كأصناف وكائنات." },
        { term: "DataFrame", def: "هيكل الجدول في pandas: صفوف وأعمدة موسومة." },
        { term: "groupby", def: "عملية تقسّم البيانات إلى مجموعات وتجمّع كلًّا ثم تدمج النتائج." },
      ],
      stages: [
        { when: "الأسبوع 1–2", focus: "الفصول 1–4: العقلية والإعداد والمتغيّرات والتحكّم. اكتب كل مثال." },
        { when: "الأسبوع 3", focus: "الفصل 5: القوائم والقواميس والصفوف والمجموعات والاستيعابات." },
        { when: "الأسبوع 4", focus: "الفصلان 6–7: الدوال النظيفة ثم التصميم الكائني." },
        { when: "الأسبوع 5", focus: "الفصل 8: الاستثناءات والملفات والوحدات وpip." },
        { when: "الأسبوع 6–8", focus: "الفصلان 9–10: تحليل pandas ثم بناء المشروع الختامي وتوسيعه." },
      ],
    },
    tr: {
      takeaways: [
        "Bir program girdiyi çıktıya dönüştürür — ortadaki mantığı sen tasarlarsın.",
        "Python yüksek seviyeli, yorumlanan ve dinamik tiplidir; bu yüzden zahmetsiz hissettirir.",
        "Girinti söz dizimin *kendisidir*: dört boşluk her bloğu tanımlar.",
        "Doğru veri yapısını seç (liste, sözlük, demet, küme); temiz kod ardından gelir.",
        "Net isimli, tip ipuçlu ve belge dizili fonksiyonlar profesyonelin işaretidir.",
        "Sınıflar, verisi ve davranışı olan şeyleri modeller — uyduğunda onlara yönel.",
        "Belirli istisnaları yakala ve dosyaları her zaman `with` ile aç.",
        "`pandas` ham dosyaları karara çevirir; `groupby` çoğu iş sorusunu yanıtlar.",
        "Beceri tekrardan gelir: durmadan küçük projeler kur.",
      ],
      cheats: [
        { t: "Çekirdek söz dizimi", rows: [["name = value", "değişken ata"], ["f\"{x}\"", "f-string araya ekleme"], ["if / elif / else", "dallanma"], ["for x in seq:", "değerleri gez"], ["while cond:", "yanlış olana kadar döngü"], ["def f(a, b=1):", "varsayılanlı fonksiyon"]] },
        { t: "Veri yapıları", rows: [["[1,2,3]", "liste — sıralı, değiştirilebilir"], ["(1,2)", "demet — değiştirilemez"], ["{\"k\": v}", "sözlük — anahtar → değer"], ["{1,2,3}", "küme — benzersiz"], ["lst[1:3]", "dilim (son hariç)"], ["lst[::-1]", "ters kopya"]] },
        { t: "Yararlı yerleşikler", rows: [["len(x)", "boyut"], ["range(n)", "0…n-1"], ["enumerate(x)", "indeks + değer"], ["zip(a, b)", "eşleştir"], ["sorted(x)", "sıralı kopya"], ["sum/min/max", "topla"]] },
        { t: "Dosya & hata", rows: [["with open(p, encoding=\"utf-8\")", "güvenli dosya erişimi"], ["try / except E", "belirli hatayı yakala"], ["finally", "her zaman çalışır"], ["json.loads / dumps", "JSON ↔ sözlük"], ["pathlib.Path", "modern dosya yolları"], ["python -m venv .venv", "sanal ortam"]] },
      ],
      terms: [
        { term: "Değişken", def: "Bir değere işaret eden ad." },
        { term: "Dinamik tipleme", def: "Python bir değerin tipini çalışma anında bulur; sen bildirmezsin." },
        { term: "Yorumlayıcı", def: "Kodunu ayrı bir derleme adımı olmadan satır satır çalıştıran program." },
        { term: "f-string", def: "`f` ile başlayan ve `{ifadelerin}` yerinde değerlendirildiği metin." },
        { term: "Liste kavrayışı", def: "Liste kuran tek satırlık ifade, örn. `[x*2 for x in xs]`." },
        { term: "Değiştirilemez", def: "Oluşturulduktan sonra değiştirilemeyen değer (demet, metin)." },
        { term: "Belge dizisi", def: "Bir `def` ya da `class` altındaki üç tırnaklı açıklama." },
        { term: "Tip ipucu", def: "`price: float` gibi, çalışma anında zorlamadan niyeti belgeleyen not." },
        { term: "İstisna", def: "Çalışma anında fırlatılan ve `try/except` ile yakalanabilen hata nesnesi." },
        { term: "Sanal ortam", def: "`python -m venv` ile oluşturulan, projeye özel izole paket dizini." },
        { term: "Modül", def: "Adlarını başka yerde `import` edebileceğin bir `.py` dosyası." },
        { term: "NYP", def: "Nesne yönelimli programlama — veri ve davranışı sınıf ve nesne olarak modelleme." },
        { term: "DataFrame", def: "pandas tablo yapısı: etiketli satır ve sütunlar." },
        { term: "groupby", def: "Veriyi gruplara bölen, her birini toplayan ve sonuçları birleştiren işlem." },
      ],
      stages: [
        { when: "Hafta 1–2", focus: "Bölüm 1–4: zihniyet, kurulum, değişkenler ve akış. Her örneği yaz." },
        { when: "Hafta 3", focus: "Bölüm 5: listeler, sözlükler, demetler, kümeler ve kavrayışlar." },
        { when: "Hafta 4", focus: "Bölüm 6–7: temiz fonksiyonlar, sonra nesne yönelimli tasarım." },
        { when: "Hafta 5", focus: "Bölüm 8: istisnalar, dosyalar, modüller ve pip." },
        { when: "Hafta 6–8", focus: "Bölüm 9–10: pandas analizi, sonra bitirme projesini kur ve genişlet." },
      ],
    },
  },
};

/* ── Generic fallbacks so every course gets a complete appendix ── */

const GENERIC = {
  en: {
    takeaways: [
      "Fundamentals outlast tools — learn the concepts, not just today's syntax.",
      "Type or build every example yourself; reading alone does not create skill.",
      "Do the exercises and the project — they are where understanding becomes ability.",
      "Prefer clarity over cleverness in everything you produce.",
      "Review this appendix regularly; spaced repetition is what makes knowledge stick.",
    ],
    stages: [
      { when: "Week 1", focus: "Read the first half, typing every example as you go." },
      { when: "Week 2", focus: "Finish the chapters and complete all exercises." },
      { when: "Week 3", focus: "Build the book's project end to end, without shortcuts." },
      { when: "Week 4", focus: "Extend the project with your own ideas, then review this appendix." },
    ],
  },
  ar: {
    takeaways: [
      "الأساسيات تبقى أطول من الأدوات — تعلّم المفاهيم لا صياغة اليوم فقط.",
      "اكتب أو ابنِ كل مثال بنفسك؛ القراءة وحدها لا تصنع مهارة.",
      "أنجِز التمارين والمشروع — فيهما تتحوّل المعرفة إلى قدرة.",
      "فضّل الوضوح على الذكاء في كل ما تنتجه.",
      "راجِع هذا الملحق دوريًا؛ التكرار المتباعد هو ما يثبّت المعرفة.",
    ],
    stages: [
      { when: "الأسبوع 1", focus: "اقرأ النصف الأول، مع كتابة كل مثال أثناء تقدّمك." },
      { when: "الأسبوع 2", focus: "أكمِل الفصول وأنجِز جميع التمارين." },
      { when: "الأسبوع 3", focus: "ابنِ مشروع الكتاب من البداية للنهاية بلا اختصارات." },
      { when: "الأسبوع 4", focus: "وسّع المشروع بأفكارك ثم راجِع هذا الملحق." },
    ],
  },
  tr: {
    takeaways: [
      "Temeller araçlardan uzun ömürlüdür — bugünün söz dizimini değil, kavramları öğren.",
      "Her örneği kendin yaz ya da kur; yalnızca okumak beceri yaratmaz.",
      "Alıştırmaları ve projeyi yap — anlayışın yeteneğe dönüştüğü yer orası.",
      "Ürettiğin her şeyde zekâ gösterisinden çok netliği yeğle.",
      "Bu eki düzenli gözden geçir; aralıklı tekrar bilgiyi kalıcı kılar.",
    ],
    stages: [
      { when: "Hafta 1", focus: "İlk yarıyı oku, ilerledikçe her örneği yaz." },
      { when: "Hafta 2", focus: "Bölümleri bitir ve tüm alıştırmaları tamamla." },
      { when: "Hafta 3", focus: "Kitabın projesini kısayol kullanmadan baştan sona kur." },
      { when: "Hafta 4", focus: "Projeyi kendi fikirlerinle genişlet, sonra bu eki gözden geçir." },
    ],
  },
};

/** Per-course generic cheat sheet + glossary seeds (kept concise, per language). */
const SEEDS = {
  en: {
    cheats: (name) => [
      { t: `${name} — where to start`, rows: [["Chapter 1", "orientation & why it matters"], ["Chapter 2", "core mechanics"], ["Mid-book", "applied techniques"], ["Final chapter", "the project"]] },
      { t: "Working habits", rows: [["Type it", "never copy-paste blindly"], ["Break it", "test edge cases on purpose"], ["Name it well", "clarity beats brevity"], ["Ship small", "finish something every week"]] },
    ],
    terms: [
      { term: "Best practice", def: "A convention the professional community has converged on because it prevents common failures." },
      { term: "Edge case", def: "An unusual input or state that breaks naive implementations — empty, huge, or malformed." },
      { term: "Iteration", def: "Improving work in small, repeated cycles instead of one perfect attempt." },
      { term: "Workflow", def: "The repeatable sequence of steps you follow to produce a result reliably." },
      { term: "Portfolio", def: "A collection of finished work that demonstrates ability better than any certificate." },
    ],
  },
  ar: {
    cheats: (name) => [
      { t: `${name} — من أين تبدأ`, rows: [["الفصل 1", "التوجيه وأهمّية الموضوع"], ["الفصل 2", "الآليات الأساسية"], ["منتصف الكتاب", "تقنيات تطبيقية"], ["الفصل الأخير", "المشروع"]] },
      { t: "عادات العمل", rows: [["اكتبه", "لا تنسخ وتلصق بعمى"], ["اكسره", "اختبر الحالات الحدّية عمدًا"], ["سمِّه جيّدًا", "الوضوح يتفوّق على الإيجاز"], ["أطلِق صغيرًا", "أنهِ شيئًا كل أسبوع"]] },
    ],
    terms: [
      { term: "أفضل ممارسة", def: "عُرف اتّفق عليه المحترفون لأنه يمنع الأخطاء الشائعة." },
      { term: "حالة حدّية", def: "مُدخل أو حالة غير معتادة تكسر التنفيذ الساذج — فارغ أو ضخم أو مشوّه." },
      { term: "التكرار التحسيني", def: "تحسين العمل بدورات صغيرة متتابعة بدل محاولة واحدة كاملة." },
      { term: "سير العمل", def: "التسلسل المتكرّر من الخطوات الذي تتبعه لإنتاج نتيجة موثوقة." },
      { term: "معرض الأعمال", def: "مجموعة أعمال منجزة تُثبت القدرة أفضل من أي شهادة." },
    ],
  },
  tr: {
    cheats: (name) => [
      { t: `${name} — nereden başlamalı`, rows: [["Bölüm 1", "yönlendirme ve neden önemli"], ["Bölüm 2", "çekirdek mekanikler"], ["Kitabın ortası", "uygulamalı teknikler"], ["Son bölüm", "proje"]] },
      { t: "Çalışma alışkanlıkları", rows: [["Yaz", "asla körü körüne kopyalama"], ["Kır", "uç durumları bilerek test et"], ["İyi adlandır", "netlik kısalığı yener"], ["Küçük yayınla", "her hafta bir şey bitir"]] },
    ],
    terms: [
      { term: "En iyi uygulama", def: "Yaygın hataları önlediği için profesyonel topluluğun üzerinde uzlaştığı kural." },
      { term: "Uç durum", def: "Naif uygulamaları bozan olağandışı girdi ya da durum — boş, çok büyük veya bozuk." },
      { term: "Yineleme", def: "İşi tek mükemmel denemeyle değil, küçük ve tekrarlı döngülerle iyileştirmek." },
      { term: "İş akışı", def: "Bir sonucu güvenilir biçimde üretmek için izlediğin tekrarlanabilir adımlar." },
      { term: "Portföy", def: "Yeteneği herhangi bir sertifikadan iyi gösteren bitmiş işler koleksiyonu." },
    ],
  },
};

/**
 * Build the appendix chapter for a course.
 * @param {string} courseId  catalog id (e.g. "python")
 * @param {"en"|"ar"|"tr"} lang
 * @param {number} no        chapter number
 * @param {string} title     course display title (for generic seeds)
 */
export function appendixChapter(courseId, lang, no, title) {
  const t = L[lang] || L.en;
  const g = GENERIC[lang] || GENERIC.en;
  const seed = SEEDS[lang] || SEEDS.en;
  const specific = (DATA[courseId] && DATA[courseId][lang]) || null;

  const takeaways = specific?.takeaways ?? g.takeaways;
  const cheats = specific?.cheats ?? seed.cheats(title);
  const terms = [...(specific?.terms ?? []), ...seed.terms];
  const stages = specific?.stages ?? g.stages;
  const refs = COMMON_REFS[courseId] ?? [];

  return chapter(no, t.title,
    { eyebrow: t.eyebrow, intro: t.intro, goals: t.goals },
    lead(t.lead),
    summary(takeaways, t.sSummary),
    cheatSheet(cheats, t.sCheat),
    glossary(terms, t.sGloss),
    roadmap(stages, t.sRoad),
    refs.length ? references(refs, t.sRefs) : p(""),
  );
}
