#!/usr/bin/env python3
import os
import re
import markdown
from markdown.extensions.toc import TocExtension

BASE = os.path.dirname(os.path.abspath(__file__))
CHAPTERS_DIR = os.path.join(BASE, "chapters")
OUT_HTML = os.path.join(BASE, "book.html")
OUT_PDF = os.path.join(BASE, "The-Triple-Analysis.pdf")

FILES = [
    "00-front-matter.md",
    "01-glossary.md",
    "02-intro-smc.md",
    "03-market-structure.md",
    "04-liquidity.md",
    "05-order-blocks.md",
    "06-fvg-imbalance.md",
    "07-inducement-traps.md",
    "08-discount-premium.md",
    "09-institutional-order-flow.md",
    "10-multi-timeframe.md",
    "11-entry-methods.md",
    "12-complete-smc-systems.md",
    "13-intro-fundamental.md",
    "14-central-banks.md",
    "15-interest-rates.md",
    "16-inflation.md",
    "17-employment-data.md",
    "18-gdp-growth.md",
    "19-consumer-business-confidence.md",
    "20-trade-balance.md",
    "21-company-financials.md",
    "22-sector-analysis.md",
    "23-intermarket-analysis.md",
    "24-economic-calendar-news.md",
    "25-intro-technical.md",
    "26-chart-types.md",
    "27-candlestick-patterns.md",
    "28-support-resistance.md",
    "29-trend-analysis.md",
    "30-chart-patterns.md",
    "31-technical-indicators.md",
    "32-volume-analysis.md",
    "33-advanced-technical.md",
    "34-triple-analysis-framework.md",
    "35-psychology-risk.md",
    "36-appendices.md",
]

# Chapters that should start a fresh page (h1 = Part title, h2 = Chapter title)
# We'll insert page-break markers before every h1 and h2 except the very first heading.

combined_md = []
for fname in FILES:
    path = os.path.join(CHAPTERS_DIR, fname)
    with open(path, encoding="utf-8") as f:
        combined_md.append(f.read().strip())

full_md = "\n\n".join(combined_md)

md = markdown.Markdown(extensions=[TocExtension(toc_depth="1-2"), "tables"])
body_html = md.convert(full_md)
toc_tokens = md.toc_tokens  # list of {level, id, name, children}

# Mark figure-caption paragraphs (a standalone bold "الشكل X.Y — ..." line)
# so they can be styled distinctly from regular bold text.
body_html = re.sub(
    r'<p><strong>(الشكل [^<]+)</strong></p>',
    r'<p class="fig-caption"><strong>\1</strong></p>',
    body_html,
)

# Force a fresh page only before a new Part/Chapter title (h1), and only when
# real body content separates it from whatever came before (so a Part title
# immediately followed by its Chapter title stacks on one page instead of
# each claiming an almost-empty page). Subsections (h2) never force a page
# break -- they flow continuously within the chapter like a normal book, so
# a short section doesn't leave the rest of the page empty.
def add_page_breaks(html):
    heading_re = re.compile(r'<h([12]) id="[^"]+">.*?</h\1>', re.DOTALL)
    # A chapter that ends with a lone figure (very common: "case study" sections
    # close with "the figure illustrates this example" + image) often has that
    # figure overflow onto a fresh page by itself, since nothing else fits
    # after the preceding dense text. Forcing the next chapter onto yet another
    # new page in that situation leaves the figure's page mostly blank -- so we
    # skip the forced break here and let the next chapter flow right after the
    # figure, filling the remaining space on that page instead.
    trailing_figure_re = re.compile(r'(<img[^>]*>\s*</p>|fig-caption[^>]*>.*?</p>)\s*$', re.DOTALL)
    matches = list(heading_re.finditer(html))
    out = []
    last_end = 0
    first = True
    for m in matches:
        gap = html[last_end:m.start()]
        gap_text = re.sub(r'<[^>]+>', '', gap).strip()
        ends_with_figure = bool(trailing_figure_re.search(gap.rstrip()))
        out.append(gap)
        if not first and gap_text and m.group(1) == "1" and not ends_with_figure:
            out.append('<div class="chapter-break"></div>')
        out.append(m.group(0))
        last_end = m.end()
        first = False
    out.append(html[last_end:])
    return "".join(out)

body_html = add_page_breaks(body_html)

def render_toc(tokens, depth=0):
    items = []
    for tok in tokens:
        indent_class = "toc-part" if tok["level"] == 1 else "toc-chapter"
        items.append(
            f'<li class="{indent_class}">'
            f'<a href="#{tok["id"]}">'
            f'<span class="toc-title">{tok["name"]}</span>'
            f'<span class="toc-leader"></span>'
            f'<span class="toc-page"></span>'
            f'</a></li>'
        )
        if tok["children"]:
            items.append(f'<ul>{render_toc(tok["children"])}</ul>')
    return "\n".join(items)

toc_html = render_toc(toc_tokens)

COPYRIGHT_HTML = """
<div class="en-page">
  <h1>حقوق النشر</h1>
  <p><strong>التحليل الثلاثي (THE TRIPLE ANALYSIS)</strong><br>
  الدليل الشامل لمفاهيم الأموال الذكية، والتحليل الأساسي، والتحليل الفني</p>
  <p>الطبعة الأولى — 2026</p>
  <p>جميع الحقوق محفوظة © 2026 لـ Ahmed Abdelhafez وAhmed Abu Omran.</p>
  <p>لا يجوز إعادة إنتاج أي جزء من هذا الكتاب أو توزيعه أو نقله بأي شكل من الأشكال أو بأي وسيلة —
  سواء بالتصوير، أو التسجيل، أو أي وسيلة إلكترونية أو ميكانيكية أخرى، أو عبر أي نظام لتخزين المعلومات
  واسترجاعها — دون إذن كتابي مسبق من المؤلفَين، باستثناء الاقتباسات القصيرة المستخدمة في المراجعات
  النقدية وبعض الاستخدامات غير التجارية الأخرى التي يسمح بها قانون حقوق النشر.</p>
  <p>يُعد كتاب "التحليل الثلاثي"، وجميع ما يتضمنه من رسوم توضيحية وأشكال ومخططات، عملًا أصليًا أنتجه
  المؤلفان، ويخضع لحماية قوانين الملكية الفكرية وحقوق النشر المعمول بها. أي إعادة إنتاج أو توزيع غير
  مصرح به لهذا العمل، أو أي جزء منه، قد يُعرّض صاحبه لعقوبات مدنية وجنائية، وستُتخذ الإجراءات القانونية
  اللازمة إلى أقصى حد يسمح به القانون.</p>
  <h2>إخلاء المسؤولية</h2>
  <p>هذا الكتاب مُعَدّ لأغراض تعليمية وتثقيفية فقط. ينطوي التداول والاستثمار في الأسواق المالية على
  مخاطر جوهرية لخسارة رأس المال، وقد لا يكون مناسبًا لكل شخص. لا ينبغي اعتبار أي محتوى وارد في هذا
  الكتاب استشارة مالية أو استثمارية أو قانونية أو ضريبية، ولا توصية أو دعوة لشراء أو بيع أي أداة مالية.</p>
  <p>محتوى هذا الكتاب، وجميع الأطر والمفاهيم والقواعد الواردة فيه، مستمدّ من تجربة تداول حقيقية وشخصية
  خاضها المؤلفان على مدار سنوات، بما فيها من نجاحات وإخفاقات شكّلت فهمهما العملي للأسواق. أما المخططات
  والأشكال التوضيحية المرسومة داخل هذا الكتاب تحديدًا، فهي رسوم توضيحية أُعدّت خصيصًا لتجسيد وتبسيط تلك
  المفاهيم بأوضح صورة ممكنة للقارئ، وليست نسخة حرفية عن صفقة أو حساب أو أداة مالية بعينها؛ فأداء الأسواق
  الفعلي، ماضيًا أو مستقبلًا، لا يتكرر بالشكل نفسه ولا يمكن ضمانه.</p>
  <p>لا يقدّم المؤلفان أي إقرار أو ضمان بخصوص دقة أو اكتمال محتوى هذا الكتاب، ويُخليان مسؤوليتهما صراحةً
  عن أي ضمانات ضمنية. تقع مسؤولية أي قرار تداولي بالكامل على عاتق القارئ. لن يتحمّل المؤلفان أي مسؤولية
  عن أي خسارة أو ضرر، مالي أو غير مالي، ينشأ بشكل مباشر أو غير مباشر عن استخدام أو تطبيق أي معلومة
  واردة في هذا الكتاب.</p>
  <p>يُنصح القراء بإجراء أبحاثهم الخاصة واستشارة مختص مالي مرخّص قبل اتخاذ أي قرار استثماري أو تداولي.</p>
  <h2>معلومات الإصدار</h2>
  <p>عنوان الكتاب: التحليل الثلاثي<br>
  المؤلفان: Ahmed Abdelhafez، Ahmed Abu Omran<br>
  الطبعة: الأولى، 2026<br>
  اللغة: العربية (مع بعض المصطلحات الإنجليزية المتخصصة)</p>
</div>
"""

AUTHORS_HTML = """
<div class="en-page authors-page">
  <h1>المؤلفـان</h1>
  <div class="author-name">Ahmed Abdelhafez</div>
  <div class="author-role">مؤلف مشارك</div>
  <div class="author-name" style="margin-top:52px;">Ahmed Abu Omran</div>
  <div class="author-role">مؤلف مشارك</div>
</div>
"""

MESSAGE_HTML = """
<div class="en-page">
  <h1>رسالة من المؤلفَين</h1>
  <p>وُلد هذا الكتاب بعد رحلة طويلة — سنوات قضيناها بين المخططات، وبين صفقاتنا الخاسرة بقدر ما بين
  رابحاتها، وفي ذلك المسار البطيء، والمُحبِط أحيانًا، الذي حوّل خبرة متناثرة إلى شيء يمكن تعليمه فعلًا
  لغيرنا.</p>
  <p>لم نكتب هذا الكتاب بحثًا عن اختصارات سهلة. ما بين يديك أقرب إلى سجلٍّ عملي: الأطر التي عدنا إليها
  مرارًا، والأخطاء التي كلّفتنا قبل أن تُعلّمنا شيئًا، والتنقيح البطيء لمنهج استقرّ أخيرًا تحت ضغط ظروف
  السوق الحقيقية. إن درست هذا الكتاب بجدّية وطبّقته بصبر، فسيمنحك أساسًا حقيقيًا — أساسًا بُني ليدوم
  طويلًا، لا ليخدم صفقتك القادمة فقط.</p>
  <p>لكننا نريد أن نكون صادقَين معك قبل أن تقلب الصفحة التالية: لا شيء مما ستقرأه — لا هيكل السوق، ولا
  مفاهيم الأموال الذكية، ولا المؤشرات — هو الدرس الحقيقي. الدرس الحقيقي أهدأ من كل ذلك بكثير. إنه
  الهدوء. إنه الانضباط. إنه القدرة على الجلوس مع صفقة خاسرة دون أن تدعها تُملي عليك قرارك التالي.</p>
  <p>ستمر بفترات تشعر فيها أن استراتيجيتك لا تُقهر، حين يبدو كل إعداد صحيحًا وكل حدس مصيبًا. لا تخلط
  بين ذلك وبين الاحتراف الحقيقي. فبدون إدارة مخاطر وانضباط نفسي خلف أي ميزة تداولية، لن تصمد هذه الميزة
  أمام عدد كافٍ من الصفقات. رأينا ذلك يحدث لغيرنا، ورأيناه يحدث لنا في بدايات مشوارنا أيضًا.</p>
  <p>لذا خذ الأطر الواردة في هذا الكتاب على محمل الجد — فهي تعمل فعلًا، وقد بنيناها لتدوم. لكن خذ
  الانضباط على محمل جدٍّ أكبر. فالاحتراف الحقيقي في هذا المجال لا يبدأ بالسيطرة على السوق، بل يبدأ
  بالسيطرة على النفس.</p>
  <p class="message-signoff">— Ahmed Abdelhafez وAhmed Abu Omran</p>
</div>
"""

LEGAL_HTML = """
<div class="en-page legal-page">
  <div class="part-break"></div>
  <h1>تنبيه قانوني</h1>
  <p>يُعد هذا الكتاب، <strong>التحليل الثلاثي</strong>، بنصّه وهيكله وجميع ما يتضمنه من رسوم وأشكال
  توضيحية أصلية، ملكية فكرية لمؤلفَيه، Ahmed Abdelhafez وAhmed Abu Omran، ويخضع لحماية قوانين حقوق
  النشر المحلية والدولية.</p>
  <p>يُمنع منعًا باتًا القيام بأي من الإجراءات التالية دون إذن كتابي مسبق من المؤلفَين:</p>
  <ul>
    <li>إعادة بيع هذا الكتاب، كليًا أو جزئيًا، بأي صيغة.</li>
    <li>إعادة نشر هذا الكتاب، أو أي جزء منه، تحت أي اسم.</li>
    <li>نسخ هذا الكتاب أو تكراره أو رفعه على أي موقع إلكتروني، أو خدمة مشاركة ملفات، أو منتدى، أو
    منصة تواصل اجتماعي.</li>
    <li>استخدام أي نص أو رسم أو شكل توضيحي من هذا الكتاب لأغراض تجارية.</li>
    <li>ترجمة هذا الكتاب أو تعديله أو إنتاج أي عمل مشتق منه دون تصريح.</li>
  </ul>
  <p>تبقى جميع الحقوق غير الممنوحة صراحةً هنا محفوظة للمؤلفَين. أي انتهاك لهذه الشروط قد يُعرّض
  المخالف للمساءلة المدنية والجنائية وفق قوانين حقوق النشر المعمول بها، ويحتفظ المؤلفان بحقهما في
  اتخاذ كل الإجراءات القانونية المتاحة ضد أي فرد أو جهة يثبت انتهاكها لهذا التنبيه.</p>
  <p>للاستفسار عن التصاريح أو التراخيص أو الاستخدام المصرح به لأي مادة من هذا الكتاب، يُرجى التواصل
  مع المؤلفَين مباشرة.</p>
  <p style="margin-top:2em;">© 2026 Ahmed Abdelhafez وAhmed Abu Omran. جميع الحقوق محفوظة.</p>
</div>
"""

# target-counter needs the href value quoted as attr(href) works only same-origin;
# WeasyPrint supports target-counter(attr(href), page) directly.
html_doc = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<title>The Triple Analysis</title>
<style>
  @page {{
    size: A4;
    margin: 2.4cm 2cm 2.2cm 2cm;
    @top-center {{
      content: "The Triple Analysis \\2014 التحليل الثلاثي";
      font-family: "Noto Naskh Arabic";
      font-size: 8.5pt;
      color: #8a7a55;
    }}
    @bottom-left {{
      content: "\\00a9 2026 Ahmed Abdelhafez وAhmed Abu Omran - جميع الحقوق محفوظة";
      font-family: "Noto Naskh Arabic", "Noto Sans Arabic", sans-serif;
      font-size: 7pt;
      color: #aaaaaa;
    }}
    @bottom-center {{
      content: counter(page);
      font-family: "Noto Naskh Arabic";
      font-size: 9.5pt;
      color: #666;
    }}
  }}
  @page cover {{
    margin: 0;
    @top-center {{ content: none; }}
    @bottom-left {{ content: none; }}
    @bottom-center {{ content: none; }}
  }}
  @page toc {{
    margin: 2.4cm 2cm;
    @top-center {{ content: none; }}
    @bottom-left {{
      content: "\\00a9 2026 Ahmed Abdelhafez وAhmed Abu Omran - جميع الحقوق محفوظة";
      font-family: "Noto Naskh Arabic", "Noto Sans Arabic", sans-serif;
      font-size: 7pt;
      color: #aaaaaa;
    }}
    @bottom-center {{
      content: counter(page, lower-roman);
      font-family: "Noto Naskh Arabic";
      font-size: 9.5pt;
      color: #666;
    }}
  }}

  *, *::before, *::after {{
    box-sizing: border-box;
  }}

  html, body {{
    direction: rtl;
    font-family: "Noto Naskh Arabic", "Noto Sans Arabic", sans-serif;
    font-size: 12pt;
    line-height: 1.85;
    color: #1a1a1a;
    max-width: 100%;
    overflow-x: hidden;
  }}

  /* ---------- COVER ---------- */
  .cover {{
    page: cover;
    page-break-after: always;
    width: 21cm;
    height: 29.7cm;
    max-width: 100%;
    box-sizing: border-box;
    background: linear-gradient(160deg, #1F2937 0%, #141b26 55%, #0d1219 100%);
    color: #fff;
    text-align: center;
    padding: 5.2cm 1.8cm 0 1.8cm;
    overflow: hidden;
  }}
  .cover .kicker {{
    display: inline-block;
    font-size: 12pt;
    letter-spacing: 2px;
    color: #E0A94A;
    border: 1px solid rgba(224,169,74,0.5);
    border-radius: 999px;
    padding: 7px 22px;
    margin-bottom: 44px;
  }}
  .cover h1.title-en {{
    font-size: 34pt;
    font-weight: 900;
    letter-spacing: 1px;
    margin: 0 0 8px;
    font-family: "Noto Sans Arabic", sans-serif;
  }}
  .cover h1.title-ar {{
    font-size: 27pt;
    font-weight: 900;
    color: #E0A94A;
    margin: 0 0 36px;
  }}
  .cover .subtitle {{
    font-size: 13.5pt;
    color: #cbd3dd;
    max-width: 13cm;
    margin: 0 auto 50px;
    line-height: 1.7;
  }}
  .cover .pillars {{
    margin-bottom: 50px;
  }}
  .cover .pillar {{
    display: inline-block;
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 12px;
    padding: 12px 18px;
    font-size: 10.5pt;
    color: #fff;
    margin: 0 6px;
  }}
  .cover .edition {{
    display: block;
    margin-top: 2.2cm;
    font-size: 10pt;
    color: #8a93a1;
    letter-spacing: 1px;
  }}

  /* ---------- TOC ---------- */
  .toc-page {{
    page: toc;
    page-break-after: always;
  }}
  .toc-page h1 {{
    font-size: 22pt;
    text-align: center;
    color: #1F2937;
    margin-bottom: 30px;
  }}
  .toc-page ul {{
    list-style: none;
    padding-right: 0;
    margin: 0;
  }}
  .toc-page ul ul {{
    padding-right: 22px;
  }}
  .toc-page li {{
    margin: 0;
  }}
  .toc-page a {{
    display: flex;
    align-items: baseline;
    text-decoration: none;
    color: inherit;
    padding: 5px 0;
  }}
  .toc-part > a {{
    font-weight: 700;
    color: #B7791F;
    font-size: 12.5pt;
    margin-top: 10px;
  }}
  .toc-chapter > a {{
    font-size: 11pt;
    color: #2A2420;
  }}
  .toc-leader {{
    flex: 1;
    border-bottom: 1px dotted #999;
    margin: 0 8px;
    transform: translateY(-3px);
  }}
  .toc-page a::after {{
    content: target-counter(attr(href url), page);
    font-family: "Noto Naskh Arabic";
    font-size: 10pt;
    color: #555;
  }}

  /* ---------- CONTENT ---------- */
  .part-break {{ page-break-before: always; }}
  .chapter-break {{ page-break-before: always; }}

  h1 {{
    font-size: 20pt;
    color: #1F2937;
    text-align: center;
    border-bottom: 3px solid #B7791F;
    padding-bottom: 14px;
    margin: 0 0 26px;
  }}
  /* A Part title stacked directly above a Chapter title (no body text
     between them): shrink the Part title into a small kicker line instead
     of a second full-size heading, so the page doesn't look duplicated. */
  h1:has(+ h1) {{
    border-bottom: none;
    padding-bottom: 0;
    margin: 0 0 6px;
    font-size: 12pt;
    color: #B7791F;
    letter-spacing: 1px;
  }}
  h2 {{
    font-size: 16.5pt;
    color: #1F2937;
    margin-top: 0.3em;
    margin-bottom: 0.6em;
  }}
  /* A Chapter title stacked directly above its first subsection (no body
     text between them yet): tighten the gap. */
  h1 + h2 {{
    margin-top: 4px;
  }}
  h3 {{
    font-size: 13.5pt;
    color: #B7791F;
    margin-top: 1.3em;
  }}
  h4 {{
    font-size: 12pt;
    color: #1F2937;
    margin-top: 1em;
  }}
  hr {{
    border: none;
    border-top: 1px solid #ccc;
    margin: 1.4em 0;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
    font-size: 10.5pt;
  }}
  th, td {{
    border: 1px solid #ccc;
    padding: 7px 9px;
    text-align: right;
    vertical-align: top;
  }}
  th {{
    background: #1F2937;
    color: #fff;
  }}
  tr:nth-child(even) {{
    background: #F7F4EE;
  }}
  blockquote {{
    background: #FFF7E6;
    border-right: 4px solid #B7791F;
    margin: 1em 0;
    padding: 0.7em 1.1em;
    font-size: 10.5pt;
    color: #5b4a2a;
  }}
  strong {{ color: #1F2937; }}
  ul, ol {{ padding-right: 1.4em; }}
  li {{ margin: 0.25em 0; }}
  code {{
    font-family: monospace;
    background: #f0eee8;
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 10pt;
  }}
  p > img {{
    display: block;
    margin: 1.1em auto 0.4em;
    max-width: 94%;
    border: 1px solid #e3ded0;
    border-radius: 6px;
    padding: 8px;
    background: #ffffff;
    page-break-inside: avoid;
  }}
  p.fig-caption {{
    text-align: center;
    font-size: 9.5pt;
    color: #5b6472;
    margin: 0 0 1.6em;
    page-break-before: avoid;
  }}
  p.fig-caption strong {{
    color: #5b6472;
    font-weight: 700;
  }}

  /* ---------- FRONT/BACK MATTER (Copyright, Authors, Message, Legal) ---------- */
  .en-page {{
    page: toc;
    page-break-after: always;
    direction: rtl;
    text-align: right;
    font-family: "Noto Naskh Arabic", "Noto Sans Arabic", serif;
  }}
  .en-page.legal-page {{
    page: auto;
  }}
  .en-page h1 {{
    margin-top: 0.4cm;
    font-family: "Noto Naskh Arabic", "Noto Sans Arabic", serif;
    font-size: 20pt;
    color: #1F2937;
    text-align: right;
    border-bottom: 3px solid #B7791F;
    padding-bottom: 10px;
    margin: 0 0 16px;
  }}
  .en-page h2 {{
    font-family: "Noto Naskh Arabic", "Noto Sans Arabic", serif;
    font-size: 14pt;
    color: #B7791F;
    margin: 1em 0 0.4em;
    page-break-after: avoid;
  }}
  .en-page p {{
    font-size: 10.5pt;
    line-height: 1.55;
    color: #2A2420;
    margin: 0 0 0.55em;
    page-break-inside: avoid;
  }}
  .en-page ul {{
    padding-right: 1.4em;
    padding-left: 0;
    font-size: 10.5pt;
    line-height: 1.55;
    color: #2A2420;
  }}
  .en-page li {{
    margin: 0.35em 0;
  }}
  .authors-page {{
    text-align: center;
    padding-top: 4.5cm;
  }}
  .authors-page h1 {{
    text-align: center;
    border-bottom: none;
    font-size: 14pt;
    color: #B7791F;
    margin-bottom: 40px;
  }}
  .authors-page .author-name {{
    font-size: 20pt;
    font-weight: 700;
    color: #1F2937;
    margin: 26px 0 0;
  }}
  .authors-page .author-role {{
    font-size: 10.5pt;
    color: #8a7a55;
    letter-spacing: 1px;
    margin-top: 4px;
  }}
  .message-signoff {{
    margin-top: 2em;
    font-style: italic;
    color: #1F2937;
  }}
</style>
</head>
<body>

<div class="cover">
  <span class="kicker">الطبعة الأولى &mdash; 2026</span>
  <h1 class="title-en">THE TRIPLE ANALYSIS</h1>
  <h1 class="title-ar">التحليل الثلاثي</h1>
  <p class="subtitle">الدليل الشامل لمفاهيم الأموال الذكية (Smart Money Concepts)، والتحليل الأساسي (Fundamental Analysis)، والتحليل الفني (Technical Analysis) &mdash; من المبتدئ إلى المحترف</p>
  <div class="pillars">
    <div class="pillar">Smart&nbsp;Money<br>Concepts</div>
    <div class="pillar">Fundamental<br>Analysis</div>
    <div class="pillar">Technical<br>Analysis</div>
  </div>
  <span class="edition">33 فصلًا &middot; مسرد مصطلحات &middot; ملاحق مرجعية</span>
</div>

{COPYRIGHT_HTML}
{AUTHORS_HTML}
{MESSAGE_HTML}

<div class="toc-page">
  <h1>المحتويات</h1>
  <ul>
    {toc_html}
  </ul>
</div>

{body_html}

{LEGAL_HTML}

</body>
</html>
"""

with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write(html_doc)

print("HTML written:", OUT_HTML)

from weasyprint import HTML
HTML(OUT_HTML).write_pdf(OUT_PDF)
print("PDF written:", OUT_PDF)
