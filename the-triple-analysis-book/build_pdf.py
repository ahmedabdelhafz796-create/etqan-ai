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

# Mark figure-caption paragraphs (a standalone bold "الشكل X.Y — ..." line)
# so they can be styled distinctly from regular bold text.
body_html = re.sub(
    r'<p><strong>(الشكل [^<]+)</strong></p>',
    r'<p class="fig-caption"><strong>\1</strong></p>',
    body_html,
)

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

COPYRIGHT_HTML = """
<div class="en-page">
  <h1>Copyright</h1>
  <p><strong>THE TRIPLE ANALYSIS</strong><br>
  A Complete Guide to Smart Money Concepts, Fundamental Analysis, and Technical Analysis</p>
  <p>First Edition &mdash; 2026</p>
  <p>Copyright &copy; 2026 by Ahmed Abdelhafez and Ahmed Abu Omran. All rights reserved.</p>
  <p>No part of this publication may be reproduced, distributed, or transmitted in any form or by any
  means &mdash; including photocopying, recording, or other electronic or mechanical methods, or by any
  information storage and retrieval system &mdash; without the prior written permission of the authors,
  except in the case of brief quotations embodied in critical reviews and certain other noncommercial
  uses permitted by copyright law.</p>
  <p>The Triple Analysis, and all associated diagrams, figures, charts, and illustrations contained
  within this book, are original works created by the authors and are protected under applicable
  intellectual property and copyright laws. Unauthorized reproduction or distribution of this work, or
  any portion of it, may result in civil and criminal penalties, and will be prosecuted to the maximum
  extent possible under the law.</p>
  <h2>Disclaimer</h2>
  <p>This book is intended for educational and informational purposes only. Trading and investing in
  financial markets involve substantial risk of loss and are not suitable for every individual. Nothing
  contained in this book should be construed as financial, investment, legal, or tax advice, nor as a
  recommendation or solicitation to buy or sell any financial instrument.</p>
  <p>All charts, figures, and price examples presented throughout this book are illustrative and based
  on synthetic or simulated data created solely to demonstrate the concepts discussed; they do not
  represent the performance of any real financial instrument, strategy, product, or account, whether
  past or future.</p>
  <p>The authors and publisher make no representations or warranties with respect to the accuracy or
  completeness of the contents of this book and specifically disclaim any implied warranties. Trading
  decisions are the sole responsibility of the reader. The authors and publisher shall not be held liable
  for any loss or damage, financial or otherwise, arising directly or indirectly from the use or
  application of any information contained in this book.</p>
  <p>Readers should conduct their own due diligence and consult a licensed financial professional before
  making any investment or trading decision.</p>
  <h2>Publication Information</h2>
  <p>Title: The Triple Analysis<br>
  Authors: Ahmed Abdelhafez, Ahmed Abu Omran<br>
  Edition: First Edition, 2026<br>
  Language: Arabic (with English terminology)</p>
</div>
"""

AUTHORS_HTML = """
<div class="en-page authors-page">
  <h1>Authors</h1>
  <div class="author-name">Ahmed Abdelhafez</div>
  <div class="author-role">Co-Author</div>
  <div class="author-name" style="margin-top:52px;">Ahmed Abu Omran</div>
  <div class="author-role">Co-Author</div>
</div>
"""

MESSAGE_HTML = """
<div class="en-page">
  <h1>A Message from the Authors</h1>
  <p>This book is the product of a long road &mdash; years spent inside the charts, inside our own
  losing trades as much as our winning ones, and inside the slow, often humbling process of turning
  scattered experience into something that could actually be taught.</p>
  <p>We did not set out to write a book of shortcuts. What follows is closer to a working record: the
  frameworks we kept coming back to, the mistakes that cost us before they taught us anything, and the
  slow refinement of a process that finally held together under real market conditions. If you study it
  seriously and apply it with patience, it will give you a genuine foundation &mdash; one built for the
  long run, not for the next trade.</p>
  <p>But we want to be honest with you about something before you turn the next page: none of this
  &mdash; not the market structure, not the smart money concepts, not the indicators &mdash; is the real
  lesson. The real lesson is quieter than that. It is composure. It is discipline. It is the ability to
  sit with a losing trade without letting it dictate your next decision.</p>
  <p>You will go through stretches where your strategy feels unstoppable, where every setup seems to
  work and every instinct seems right. Do not mistake that for mastery. Without risk management and
  psychological discipline behind it, no edge survives contact with enough trades. We have watched it
  happen to others, and early in our own journeys, we watched it happen to us.</p>
  <p>So take the frameworks in this book seriously &mdash; they work, and we built them to last. But
  take the discipline more seriously still. Real professionalism in this business does not begin with
  controlling the market. It begins with controlling yourself.</p>
  <p class="message-signoff">&mdash; Ahmed Abdelhafez &amp; Ahmed Abu Omran</p>
</div>
"""

LEGAL_HTML = """
<div class="en-page legal-page">
  <div class="part-break"></div>
  <h1>Legal Notice</h1>
  <p>This book, <strong>The Triple Analysis</strong>, including its text, structure, and all original
  diagrams, figures, and illustrations, is the intellectual property of its authors, Ahmed Abdelhafez
  and Ahmed Abu Omran, and is protected under national and international copyright law.</p>
  <p>The following actions are strictly prohibited without prior written consent from the authors:</p>
  <ul>
    <li>Reselling this book, in whole or in part, in any format.</li>
    <li>Republishing this book, or any portion of it, under any name.</li>
    <li>Copying, duplicating, or uploading this book to any website, file-sharing service, forum, or
    social media platform.</li>
    <li>Using any text, diagram, figure, or illustration from this book for commercial purposes.</li>
    <li>Translating, adapting, or creating derivative works based on this book without authorization.</li>
  </ul>
  <p>All rights not expressly granted herein are reserved by the authors. Any violation of these terms
  may expose the responsible party to civil and criminal liability under applicable copyright laws, and
  the authors reserve the right to pursue all available legal remedies against any individual or entity
  found to be in breach of this notice.</p>
  <p>For permissions, licensing inquiries, or authorized use of any material from this book, please
  contact the authors directly.</p>
  <p style="margin-top:2em;">&copy; 2026 Ahmed Abdelhafez &amp; Ahmed Abu Omran. All Rights Reserved.</p>
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
      content: "\\00a9 2026 Ahmed Abdelhafez & Ahmed Abu Omran. All Rights Reserved.";
      font-family: "Noto Sans Arabic", sans-serif;
      font-size: 6.7pt;
      color: #aaaaaa;
      direction: ltr;
      unicode-bidi: bidi-override;
      text-align: left;
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
      content: "\\00a9 2026 Ahmed Abdelhafez & Ahmed Abu Omran. All Rights Reserved.";
      font-family: "Noto Sans Arabic", sans-serif;
      font-size: 6.7pt;
      color: #aaaaaa;
      direction: ltr;
      unicode-bidi: bidi-override;
      text-align: left;
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

  /* ---------- ENGLISH FRONT/BACK MATTER ---------- */
  .en-page {{
    page: toc;
    page-break-after: always;
    direction: ltr;
    text-align: left;
    font-family: Georgia, "Times New Roman", serif;
    padding-top: 1.5cm;
  }}
  .en-page.legal-page {{
    page: auto;
  }}
  .en-page h1 {{
    font-family: Georgia, "Times New Roman", serif;
    font-size: 20pt;
    color: #1F2937;
    text-align: left;
    border-bottom: 3px solid #B7791F;
    padding-bottom: 12px;
    margin: 0 0 22px;
  }}
  .en-page h2 {{
    font-family: Georgia, "Times New Roman", serif;
    font-size: 14pt;
    color: #B7791F;
    margin: 1.6em 0 0.5em;
  }}
  .en-page p {{
    font-size: 10.5pt;
    line-height: 1.75;
    color: #2A2420;
    margin: 0 0 0.9em;
  }}
  .en-page ul {{
    padding-left: 1.4em;
    font-size: 10.5pt;
    line-height: 1.75;
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
    font-size: 13pt;
    letter-spacing: 3px;
    color: #B7791F;
    text-transform: uppercase;
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
