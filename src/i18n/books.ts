import { books as baseBooks, type Book } from "@/config";
import type { Locale } from "@/i18n/config";

/**
 * Localized book text overlays. Structural fields (id, prices, icons, accents,
 * stat values) stay in `config.ts`; only human text is overlaid here, aligned
 * by index. The merge is defensive: any missing string falls back to English,
 * so a partial translation can never break the page.
 */

interface ChapterOverlay {
  title: string;
  lessons: string[];
}
interface ModuleOverlay {
  title: string;
  chapters: ChapterOverlay[];
}
interface BookOverlay {
  title: string;
  subtitle: string;
  badge: string;
  tagline: string;
  description: string;
  highlights: string[];
  statsLabels: string[];
  includes: string[];
  curriculum: ModuleOverlay[];
}

type LocaleOverlays = Record<string, BookOverlay>;

const AR: LocaleOverlays = {
  "triple-analysis": {
    title: "التحليل الثلاثي",
    subtitle: "الإطار المؤسسي لقراءة أي سوق",
    badge: "الإصدار الأول الأكثر مبيعًا",
    tagline: "الهيكل · السيولة · تدفق الأوامر — موحّدة في نموذج واحد قابل للتكرار.",
    description:
      "تعليم تداول متكامل من الأساس، مبني على المنطق نفسه الذي تستخدمه المؤسسات لتحريك السعر. يدمج «التحليل الثلاثي» هيكل السوق والسيولة وتدفق الأوامر في إطار قرار واحد — ثم يمنحك القوائم والنماذج ودراسات الحالة لتتداوله بثقة.",
    highlights: [
      "اقرأ هيكل السوق كمتداول مكتب",
      "ارسم خريطة السيولة قبل تحرك السعر",
      "مفاهيم SMC وICT مشروحة خطوة بخطوة",
      "نماذج دخول وخروج مؤسسية",
    ],
    statsLabels: ["وحدات", "فصول", "أمثلة رسوم"],
    includes: [
      "تحديثات مدى الحياة للإصدار الأول",
      "قوائم تحقّق احترافية قابلة للطباعة",
      "أكثر من 220 مثالًا مشروحًا على الرسوم",
      "تمارين تطبيقية مع حلول",
    ],
    curriculum: [
      {
        title: "الأسس وهيكل السوق",
        chapters: [
          { title: "كيف تتحرك الأسواق حقًا", lessons: ["نموذج القوى الثلاث: الهيكل، السيولة، تدفق الأوامر", "لماذا تفشل أنماط التجزئة — وما الذي يحلّ محلها", "قراءة سياق الأطر الزمنية الأعلى أولًا"] },
          { title: "إتقان هيكل السوق", lessons: ["كسر الهيكل (BOS) مقابل تغيّر الطابع (CHoCH)", "الهيكل الداخلي مقابل الخارجي", "رسم الاتجاهات عبر الأطر الزمنية المتداخلة"] },
        ],
      },
      {
        title: "هندسة السيولة",
        chapters: [
          { title: "تشريح السيولة", lessons: ["برك سيولة الشراء والبيع", "القمم والقيعان المتساوية وفراغات السيولة", "اصطياد الوقف والكنس والعكس"] },
          { title: "رسم خريطة السيولة عمليًا", lessons: ["تحديد أهداف الجذب نحو السيولة", "مصفوفات العلاوة والخصم", "توقيت الدخول حول اقتناص السيولة"] },
        ],
      },
      {
        title: "تدفق الأوامر والمال الذكي",
        chapters: [
          { title: "أسس تدفق الأوامر", lessons: ["كتل الأوامر والتخفيف وكتل الكسر", "فجوات القيمة العادلة وعدم التوازن", "الإزاحة كإشارة للنيّة"] },
          { title: "مفاهيم المال الذكي (SMC)", lessons: ["دليل SMC مختصرًا", "بصمات تدفق الأوامر المؤسسية", "دمج SMC مع الهيكل والسيولة"] },
          { title: "مفاهيم ICT مشروحة", lessons: ["مناطق القتل ونقطة الدخول المثلى (OTE)", "الرصاصة الفضية وتأرجح جوداس", "قوة الثلاثة: تجميع، تلاعب، توزيع"] },
        ],
      },
      {
        title: "الحافة الكلاسيكية: وايكوف والعرض/الطلب",
        chapters: [
          { title: "منهج وايكوف", lessons: ["مخططات التجميع والتوزيع", "الينابيع والدفعات العلوية والاختبارات", "عقلية المشغّل المركّب"] },
          { title: "العرض والطلب", lessons: ["رسم مناطق تصمد فعلًا", "المناطق الطازجة مقابل المختبَرة", "التقاء مع السيولة وكتل الأوامر"] },
        ],
      },
      {
        title: "التنفيذ ونماذج الدخول",
        chapters: [
          { title: "نماذج دخول متقدمة", lessons: ["قائمة تحقّق الإعداد الممتاز A+", "دخول مصقول: من تحيّز الإطار الأعلى إلى مُحفّز الأدنى", "التدرّج في الدخول مع التأكيد"] },
          { title: "استراتيجيات الخروج", lessons: ["الخروج الجزئي والصفقات المستمرة", "وقف متحرك قائم على الهيكل", "تثبيت الربح عند أهداف السيولة"] },
        ],
      },
      {
        title: "المخاطر وعلم النفس والتطبيق",
        chapters: [
          { title: "نظام إدارة المخاطر", lessons: ["تحديد الحجم وإعادة صياغة قاعدة 1%", "مضاعفات R والتوقع", "التحكم في التراجع وحساب التعافي"] },
          { title: "علم نفس التداول", lessons: ["إتقان الخوف والطمع ونفاد الصبر", "بناء العملية فوق النتيجة", "الروتين اليومي للمحترف"] },
          { title: "دراسات حالة وتمارين", lessons: ["تحليلات صفقات كاملة من الدخول للخروج", "أمثلة سوق حقيقية مشروحة", "تمارين تطبيقية وقوائم تحقّق احترافية"] },
        ],
      },
    ],
  },
  "ai-trading": {
    title: "التداول المتقدم بالذكاء الاصطناعي",
    subtitle: "التحليل المؤسسي والأتمتة وأنظمة التداول الاحترافية",
    badge: "متقدم · مستوى الممارس",
    tagline: "حيث يلتقي المنطق المؤسسي بالذكاء الاصطناعي التطبيقي.",
    description:
      "الرفيق المتقدم للمتداولين المستعدين لتصنيع حافتهم. يتعمق «التداول المتقدم بالذكاء الاصطناعي» في التحليل المؤسسي وخطوط بيانات السوق وهندسة التنفيذ ودمج الذكاء الاصطناعي — محوّلًا المهارة التقديرية إلى أنظمة وسير عمل تداول احترافية قابلة للتكرار.",
    highlights: [
      "صمّم أنظمة تداول مؤسسية متكاملة",
      "ادمج الذكاء الاصطناعي في التحليل والتنفيذ — بمسؤولية",
      "اهندس خطوط بيانات السوق والأتمتة",
      "ابنِ سير عمل احترافيًا قابلًا للتوسّع",
    ],
    statsLabels: ["وحدات", "فصول", "مخططات أنظمة"],
    includes: [
      "18 مخطط نظام احترافي",
      "مكتبة أوامر وسير عمل الذكاء الاصطناعي",
      "قوالب اختبار وتقييم",
      "تحديثات مدى الحياة للإصدار الأول",
    ],
    curriculum: [
      {
        title: "نظام التشغيل المؤسسي",
        chapters: [
          { title: "التفكير كمؤسسة", lessons: ["سير عمل المكتب: بحث ← فرضية ← تنفيذ ← مراجعة", "التفويض وميزانية المخاطر وتآكل الحافة", "لماذا تتفوق العملية على التنبؤ"] },
          { title: "تحليل مؤسسي متقدم", lessons: ["التحيّز المؤسسي متعدد الأطر", "تحليل الأسواق المتبادلة والارتباط", "أنظمة التقلب والتموضع"] },
        ],
      },
      {
        title: "هندسة بيانات السوق",
        chapters: [
          { title: "مصادر بيانات السوق وتنظيفها", lessons: ["بيانات التيك ودفتر الأوامر وOHLCV", "نظافة البيانات وتحيّز البقاء والنظر المستقبلي", "بناء خط بيانات موثوق"] },
          { title: "هندسة الميزات للمتداولين", lessons: ["تحويل الهيكل والسيولة إلى ميزات", "إشارات التقلب والزخم والبنية الدقيقة", "تصنيف الصفقات للتقييم"] },
        ],
      },
      {
        title: "دمج الذكاء الاصطناعي في التداول",
        chapters: [
          { title: "الذكاء الاصطناعي كمحلّل مساعد", lessons: ["استخدام النماذج اللغوية لتسريع البحث والتدوين", "أطر الأوامر لتحليل السوق", "الحواجز: أين يساعد الذكاء الاصطناعي وأين يفشل"] },
          { title: "اتخاذ قرار مدعوم بالنماذج", lessons: ["توليد الإشارة مقابل تأكيدها", "المجموعات: دمج القواعد مع النماذج", "تجنّب فرط الملاءمة والتنقيب عن البيانات"] },
        ],
      },
      {
        title: "التنفيذ والأتمتة",
        chapters: [
          { title: "نماذج التنفيذ", lessons: ["أنواع الأوامر والانزلاق والتأثير", "التنفيذ الذكي والتعبئة الجزئية", "نمذجة الكمون والفارق والتكلفة"] },
          { title: "الأتمتة الاحترافية", lessons: ["من قائمة التحقّق إلى قواعد مقنّنة", "بناء حلقة تداول شبه مؤتمتة", "أنظمة الأمان ومفاتيح الإيقاف والمراقبة"] },
        ],
      },
      {
        title: "أنظمة التداول والاختبار الخلفي",
        chapters: [
          { title: "تصميم النظام", lessons: ["تشريح نظام تداول متين", "الدخول والخروج والحجم ومرشحات النظام", "دمج الحافة التقديرية والمنهجية"] },
          { title: "التحقق والاختبار الخلفي", lessons: ["التحليل الأمامي والاختبار خارج العيّنة", "المقاييس المهمة: شارب، التوقع، التراجع", "اختبار الضغط لتغيّر النظام"] },
        ],
      },
      {
        title: "المخاطر وسير العمل والإتقان",
        chapters: [
          { title: "المخاطر على مستوى المحفظة", lessons: ["الارتباط والتعرّض والحرارة", "تحديد الحجم الديناميكي", "الحفاظ على رأس المال كحافة"] },
          { title: "سير العمل الاحترافي", lessons: ["الإيقاع التشغيلي اليومي/الأسبوعي", "مراجعة الصفقات وتحليل الأداء", "التوسّع من متداول فرد إلى نظام"] },
          { title: "مفاهيم متقدمة ودراسات حالة", lessons: ["بناء أنظمة كاملة مُفكّكة", "دراسات حالة بأسلوب مؤسسي حقيقي", "تمارين متقدمة وقوائم تحقّق احترافية"] },
        ],
      },
    ],
  },
};

const TR: LocaleOverlays = {
  "triple-analysis": {
    title: "Triple Analysis",
    subtitle: "Herhangi Bir Piyasayı Okumak İçin Kurumsal Çerçeve",
    badge: "Çok Satan İlk Baskı",
    tagline: "Yapı · Likidite · Emir Akışı — tek, tekrarlanabilir bir modelde birleşti.",
    description:
      "Kurumların fiyatı hareket ettirmek için kullandığı mantık üzerine sıfırdan kurulmuş, eksiksiz bir işlem eğitimi. Triple Analysis; piyasa yapısını, likiditeyi ve emir akışını tek bir karar çerçevesinde birleştirir — sonra bunu güvenle işlemen için kontrol listeleri, modeller ve vaka çalışmaları verir.",
    highlights: [
      "Piyasa yapısını bir masa yatırımcısı gibi oku",
      "Fiyat hareket etmeden likiditeyi haritala",
      "SMC ve ICT kavramları adım adım açıklandı",
      "Kurumsal giriş ve çıkış modelleri",
    ],
    statsLabels: ["Modül", "Bölüm", "Grafik Örneği"],
    includes: [
      "İlk Baskı'ya ömür boyu güncelleme",
      "Yazdırılabilir profesyonel kontrol listeleri",
      "220+ açıklamalı grafik örneği",
      "Çözümlü alıştırmalar",
    ],
    curriculum: [
      {
        title: "Temeller ve Piyasa Yapısı",
        chapters: [
          { title: "Piyasalar Gerçekte Nasıl Hareket Eder", lessons: ["Üç kuvvet modeli: yapı, likidite, emir akışı", "Perakende kalıpları neden başarısız olur — yerine ne gelir", "Önce üst zaman dilimi bağlamını okumak"] },
          { title: "Piyasa Yapısı Ustalığı", lessons: ["Yapı kırılımı (BOS) vs karakter değişimi (CHoCH)", "İç yapı vs dış yapı", "İç içe zaman dilimlerinde trendleri haritalamak"] },
        ],
      },
      {
        title: "Likidite Mühendisliği",
        chapters: [
          { title: "Likiditenin Anatomisi", lessons: ["Alış ve satış tarafı likidite havuzları", "Eşit tepe/dipler ve likidite boşlukları", "Zarar avları, süpürmeler ve baskın-dönüş"] },
          { title: "Uygulamada Likidite Haritalama", lessons: ["Likiditeye çekiliş hedeflerini işaretlemek", "Prim ve iskonto dizileri", "Likidite kapmaları çevresinde giriş zamanlaması"] },
        ],
      },
      {
        title: "Emir Akışı ve Akıllı Para",
        chapters: [
          { title: "Emir Akışı Temelleri", lessons: ["Emir blokları, hafifletme ve kırıcı bloklar", "Adil değer boşlukları ve dengesizlik", "Niyet sinyali olarak yer değiştirme"] },
          { title: "Akıllı Para Kavramları (SMC)", lessons: ["SMC oyun kitabı özetlendi", "Kurumsal emir akışı izleri", "SMC'yi yapı ve likidite ile birleştirmek"] },
          { title: "ICT Kavramları, Çözümlendi", lessons: ["Öldürme bölgeleri ve optimal giriş (OTE)", "Gümüş kurşun ve judas salınımı", "Üçün gücü: birikim, manipülasyon, dağıtım"] },
        ],
      },
      {
        title: "Klasik Avantaj: Wyckoff ve A/T",
        chapters: [
          { title: "Wyckoff Yöntemi", lessons: ["Birikim ve dağıtım şemaları", "Yaylar, yukarı itişler ve testler", "Bileşik operatör zihniyeti"] },
          { title: "Arz ve Talep", lessons: ["Gerçekten tutan bölgeler çizmek", "Taze vs test edilmiş bölgeler", "Likidite ve emir bloklarıyla birleşim"] },
        ],
      },
      {
        title: "Uygulama ve Giriş Modelleri",
        chapters: [
          { title: "Gelişmiş Giriş Modelleri", lessons: ["A+ kurulum kontrol listesi", "Rafine girişler: üst zaman diliminden alt tetikleyiciye", "Onayla kademeli giriş"] },
          { title: "Çıkış Stratejileri", lessons: ["Kısmi çıkışlar ve koşucular", "Yapı temelli takip eden stoplar", "Likidite hedeflerinde kârı kilitlemek"] },
        ],
      },
      {
        title: "Risk, Psikoloji ve Uygulama",
        chapters: [
          { title: "Risk Yönetim Sistemi", lessons: ["Pozisyon boyutu ve %1 kuralının yeniden çerçevelenmesi", "R-katları ve beklenti", "Düşüş kontrolü ve toparlanma matematiği"] },
          { title: "İşlem Psikolojisi", lessons: ["Korku, açgözlülük ve sabırsızlığa hâkim olmak", "Sonuç yerine süreç inşa etmek", "Profesyonelin günlük rutini"] },
          { title: "Vaka Çalışmaları ve Alıştırmalar", lessons: ["Girişten çıkışa tam işlem çözümlemeleri", "Açıklamalı gerçek piyasa örnekleri", "Alıştırmalar ve profesyonel kontrol listeleri"] },
        ],
      },
    ],
  },
  "ai-trading": {
    title: "Advanced AI Trading",
    subtitle: "Kurumsal Analiz, Otomasyon ve Profesyonel İşlem Sistemleri",
    badge: "İleri · Uygulayıcı Seviyesi",
    tagline: "Kurumsal mantığın uygulamalı yapay zekâ ile buluştuğu yer.",
    description:
      "Avantajını sanayileştirmeye hazır yatırımcılar için ileri seviye tamamlayıcı. Advanced AI Trading; kurumsal analiz, piyasa verisi hatları, uygulama mühendisliği ve yapay zekâ entegrasyonuna derinlemesine iner — takdire dayalı beceriyi tekrarlanabilir, profesyonel işlem sistemlerine dönüştürür.",
    highlights: [
      "Uçtan uca kurumsal işlem sistemleri tasarla",
      "Yapay zekâyı analiz ve uygulamaya entegre et — sorumlu şekilde",
      "Piyasa verisi ve otomasyon hatları kur",
      "Ölçeklenen profesyonel iş akışları inşa et",
    ],
    statsLabels: ["Modül", "Bölüm", "Sistem Şablonu"],
    includes: [
      "18 profesyonel sistem şablonu",
      "Yapay zekâ komut ve iş akışı kütüphanesi",
      "Backtest ve değerlendirme şablonları",
      "İlk Baskı'ya ömür boyu güncelleme",
    ],
    curriculum: [
      {
        title: "Kurumsal İşletim Sistemi",
        chapters: [
          { title: "Bir Kurum Gibi Düşünmek", lessons: ["Masa iş akışı: araştırma → tez → uygulama → inceleme", "Yetki, risk bütçesi ve avantaj erimesi", "Süreç neden tahmini yener"] },
          { title: "Gelişmiş Kurumsal Analiz", lessons: ["Çoklu zaman dilimi kurumsal ön yargı", "Piyasalar arası ve korelasyon analizi", "Oynaklık rejimleri ve konumlanma"] },
        ],
      },
      {
        title: "Piyasa Verisi Mühendisliği",
        chapters: [
          { title: "Piyasa Verisini Toplama ve Temizleme", lessons: ["Tick, emir defteri ve OHLCV verisi", "Veri hijyeni, hayatta kalma ve ileriye bakış yanlılığı", "Güvenilir bir veri hattı kurmak"] },
          { title: "Yatırımcılar İçin Özellik Mühendisliği", lessons: ["Yapı ve likiditeyi özelliklere dönüştürmek", "Oynaklık, momentum ve mikroyapı sinyalleri", "İşlemleri değerlendirme için etiketlemek"] },
        ],
      },
      {
        title: "İşlem İçin Yapay Zekâ Entegrasyonu",
        chapters: [
          { title: "Yardımcı Analist Olarak Yapay Zekâ", lessons: ["Araştırma ve günlük için LLM kullanmak", "Piyasa analizi için komut çerçeveleri", "Sınırlar: yapay zekâ nerede yardım eder, nerede etmez"] },
          { title: "Model Destekli Karar Verme", lessons: ["Sinyal üretimi vs onayı", "Topluluklar: kuralları modellerle birleştirmek", "Aşırı uyum ve veri gözetlemesinden kaçınmak"] },
        ],
      },
      {
        title: "Uygulama ve Otomasyon",
        chapters: [
          { title: "Uygulama Modelleri", lessons: ["Emir türleri, kayma ve etki", "Akıllı uygulama ve kısmi dolumlar", "Gecikme, spread ve maliyet modellemesi"] },
          { title: "Profesyonel Otomasyon", lessons: ["Kontrol listesinden kodlanmış kurallara", "Yarı otomatik işlem döngüsü kurmak", "Güvenlik önlemleri, durdurma anahtarları ve izleme"] },
        ],
      },
      {
        title: "İşlem Sistemleri ve Backtesting",
        chapters: [
          { title: "Sistem Tasarımı", lessons: ["Sağlam bir işlem sisteminin anatomisi", "Giriş, çıkış, boyut ve rejim filtreleri", "Takdire dayalı ve sistematik avantajları birleştirmek"] },
          { title: "Doğrulama ve Backtesting", lessons: ["İleriye dönük analiz ve örneklem dışı test", "Önemli metrikler: Sharpe, beklenti, düşüş", "Rejim değişimi için stres testi"] },
        ],
      },
      {
        title: "Risk, İş Akışı ve Ustalık",
        chapters: [
          { title: "Portföy Düzeyinde Risk", lessons: ["Korelasyon, maruziyet ve ısı", "Dinamik pozisyon boyutlandırma", "Avantaj olarak sermaye koruması"] },
          { title: "Profesyonel İş Akışları", lessons: ["Günlük/haftalık işletim ritmi", "İşlem incelemesi ve performans analitiği", "Tek yatırımcıdan sisteme ölçeklenmek"] },
          { title: "Gelişmiş Kavramlar ve Vaka Çalışmaları", lessons: ["Tam sistem kurulumları çözümlendi", "Gerçek kurumsal tarz vaka çalışmaları", "Gelişmiş alıştırmalar ve profesyonel kontrol listeleri"] },
        ],
      },
    ],
  },
};

const OVERLAYS: Partial<Record<Locale, LocaleOverlays>> = { ar: AR, tr: TR };

function localize(book: Book, ov: BookOverlay | undefined): Book {
  if (!ov) return book;
  return {
    ...book,
    title: ov.title ?? book.title,
    subtitle: ov.subtitle ?? book.subtitle,
    badge: ov.badge ?? book.badge,
    tagline: ov.tagline ?? book.tagline,
    description: ov.description ?? book.description,
    highlights: book.highlights.map((h, i) => ov.highlights?.[i] ?? h),
    stats: book.stats.map((s, i) => ({ ...s, label: ov.statsLabels?.[i] ?? s.label })),
    includes: book.includes.map((h, i) => ov.includes?.[i] ?? h),
    curriculum: book.curriculum.map((m, mi) => ({
      icon: m.icon,
      title: ov.curriculum?.[mi]?.title ?? m.title,
      chapters: m.chapters.map((c, ci) => ({
        title: ov.curriculum?.[mi]?.chapters?.[ci]?.title ?? c.title,
        lessons: c.lessons.map(
          (l, li) => ov.curriculum?.[mi]?.chapters?.[ci]?.lessons?.[li] ?? l
        ),
      })),
    })),
  };
}

/** Return the book catalog with text localized for the given locale. */
export function getLocalizedBooks(locale: Locale): Book[] {
  const overlays = OVERLAYS[locale];
  return baseBooks.map((b) => localize(b, overlays?.[b.id]));
}
