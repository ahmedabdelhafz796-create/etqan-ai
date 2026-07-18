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
    "22-economic-calendar-news.md",
    "23-intro-technical.md",
    "24-chart-types.md",
    "25-candlestick-patterns.md",
    "26-support-resistance.md",
    "27-trend-analysis.md",
    "28-chart-patterns.md",
    "29-technical-indicators.md",
    "30-volume-analysis.md",
    "31-advanced-technical.md",
    "32-triple-analysis-framework.md",
    "33-psychology-risk.md",
    "34-appendices.md",
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

# Insert page-break-before on h1/h2 tags (skip the very first tag in the doc)
def add_page_breaks(html):
    parts = re.split(r'(<h[12] id="[^"]+">)', html)
    out = []
    first_heading_seen = False
    for chunk in parts:
        m = re.match(r'<h([12]) id="([^"]+)">', chunk)
        if m:
            if first_heading_seen:
                cls = "part-break" if m.group(1) == "1" else "chapter-break"
                chunk = f'<div class="{cls}"></div>' + chunk
            first_heading_seen = True
        out.append(chunk)
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
    @bottom-center {{ content: none; }}
  }}
  @page toc {{
    margin: 2.4cm 2cm;
    @top-center {{ content: none; }}
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
  h2 {{
    font-size: 16.5pt;
    color: #1F2937;
    margin-top: 0.3em;
    margin-bottom: 0.6em;
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

<div class="toc-page">
  <h1>المحتويات</h1>
  <ul>
    {toc_html}
  </ul>
</div>

{body_html}

</body>
</html>
"""

with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write(html_doc)

print("HTML written:", OUT_HTML)

from weasyprint import HTML
HTML(OUT_HTML).write_pdf(OUT_PDF)
print("PDF written:", OUT_PDF)
