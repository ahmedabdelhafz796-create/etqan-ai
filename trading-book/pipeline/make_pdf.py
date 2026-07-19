"""Assemble the 300 plates into a single navigable book PDF.

Cover -> provenance -> chapter TOC -> clickable image index -> 300 plates,
with nested PDF bookmarks (chapter > plate) and internal links throughout.
Pages are 1280x720 pt (16:9); plates are embedded at full 2560x1440 px,
i.e. 2 px per point (≈144 ppi on screen, 300+ DPI when printed at ~8.5in wide).

Run from trading-book/:  python3 -m pipeline.make_pdf
"""

from __future__ import annotations

import csv
import os

from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "Trading Book Images")
COMPACT = bool(os.environ.get("COMPACT"))
OUT = os.path.join(ROOT, "Trading_Book_300_Charts_screen.pdf" if COMPACT else "Trading_Book_300_Charts.pdf")


def plate_source(path):
    """Full-res PNG for print edition; 1680px JPEG for the screen edition."""
    if not COMPACT:
        return path
    import hashlib
    from PIL import Image

    cache = os.path.join(ROOT, ".jpg_cache")
    os.makedirs(cache, exist_ok=True)
    out = os.path.join(cache, hashlib.md5(path.encode()).hexdigest() + ".jpg")
    if not os.path.exists(out):
        im = Image.open(path).convert("RGB")
        im = im.resize((1400, int(1400 * im.height / im.width)), Image.LANCZOS)
        im.save(out, "JPEG", quality=72, optimize=True)
    return out

PW, PH = 1280, 720
NAVY = HexColor("#1F2937")
GOLD = HexColor("#B7791F")
INK2 = HexColor("#475569")
MUTED = HexColor("#94A3B8")
CREAM = HexColor("#FCFCFA")

CHAPTERS = ["SMC", "ICT", "Price Action", "Technical Analysis", "Indicators",
            "Wyckoff", "Elliott", "Fibonacci", "Fundamental Analysis"]
CHAPTER_TITLES = {
    "SMC": "Smart Money Concepts", "ICT": "ICT Concepts", "Price Action": "Price Action",
    "Technical Analysis": "Classical Technical Analysis", "Indicators": "Indicators",
    "Wyckoff": "The Wyckoff Method", "Elliott": "Elliott Wave", "Fibonacci": "Fibonacci",
    "Fundamental Analysis": "Fundamental Analysis",
}


def load_index():
    rows = []
    with open(os.path.join(IMG, "index.csv")) as f:
        for r in csv.DictReader(f):
            rows.append(r)
    rows.sort(key=lambda r: int(r["Image Name"][:3]))
    return rows


def main():
    rows = load_index()
    per_page = 72
    n_index_pages = (len(rows) + per_page - 1) // per_page
    front = 3 + n_index_pages  # cover, provenance, chapter TOC, index pages
    page_of = {int(r["Image Name"][:3]): front + k + 1 for k, r in enumerate(rows)}
    first_of_chapter = {}
    for r in rows:
        first_of_chapter.setdefault(r["Topic"], int(r["Image Name"][:3]))

    c = canvas.Canvas(OUT, pagesize=(PW, PH), pageCompression=1)
    c.setTitle("The Trading Book — 300 Real-Data Chart Studies" + (" (screen edition)" if COMPACT else ""))
    c.setAuthor("etqan-ai trading-book pipeline")
    c.setSubject("300 annotated trading case studies rendered from real historical market data")

    # ---------------------------------------------------------------- cover
    c.setFillColor(NAVY)
    c.rect(0, 0, PW, PH, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(0, 118, PW, 3, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 54)
    c.setFillColor(HexColor("#FFFFFF"))
    c.drawCentredString(PW / 2, 470, "THE TRADING BOOK")
    c.setFont("Helvetica", 26)
    c.setFillColor(HexColor("#E0A94A"))
    c.drawCentredString(PW / 2, 420, "300 Real-Data Chart Studies")
    c.setFont("Helvetica", 15)
    c.setFillColor(HexColor("#CBD3DD"))
    c.drawCentredString(PW / 2, 350, "Smart Money Concepts  ·  ICT  ·  Price Action  ·  Classical Patterns  ·  Indicators")
    c.drawCentredString(PW / 2, 326, "Wyckoff  ·  Elliott Wave  ·  Fibonacci  ·  Fundamental Analysis")
    c.setFont("Helvetica", 12.5)
    c.setFillColor(MUTED)
    c.drawCentredString(PW / 2, 180, "Every chart rendered from genuine historical OHLCV data — every setup algorithmically")
    c.drawCentredString(PW / 2, 162, "detected in the data, verified against the documented market record. No simulated prices.")
    c.bookmarkPage("cover")
    c.addOutlineEntry("Cover", "cover", 0)
    c.showPage()

    # ---------------------------------------------------------------- provenance
    c.setFillColor(CREAM)
    c.rect(0, 0, PW, PH, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 30)
    c.drawString(80, PH - 90, "Data Provenance & Method")
    c.setFillColor(INK2)
    y = PH - 140
    for line in [
        "Every plate in this book is rendered from real historical market data:",
        "",
        "   •  GOOG (Alphabet, NASDAQ) — daily OHLCV, 2004-2013, plus weekly/monthly aggregations.",
        "      Verified: reproduces the +19.1% earnings gap (2008-04-18), the -10.1% miss (2006-02-01),",
        "      and the 2012-10-18 early-release intraday selloff, exactly as documented.",
        "   •  EURUSD (FX spot) — 1-hour OHLCV, Apr 2017 - Feb 2018, plus 4-hour aggregation.",
        "      Verified: hourly volume peaks precisely at the London (07:00 UTC) and New York",
        "      (12:30-15:00 UTC) opens; FOMC, ECB and NFP reactions land on their documented dates.",
        "   •  ASML.AS (Euronext Amsterdam) daily 2010-2013 and 002032.SZ (Shenzhen) daily 2004-2015.",
        "   •  U.S. quarterly macro series (GDP, CPI, rates, unemployment) 1959-2009 — Federal Reserve",
        "      (FRED) compilation, with NBER-dated recessions.",
        "",
        "Every annotation marks an event detected algorithmically in the data itself — gaps, sweeps,",
        "structure breaks, pattern geometry, indicator crosses. Entry / stop / target levels and the",
        "risk-reward boxes are computed from each setup's real dimensions. Nothing is drawn that",
        "did not happen in the historical record; a provenance line appears on every plate.",
        "",
        "Charts were produced with an open, reproducible pipeline (mplfinance rendering, 2560 x 1440",
        "lossless PNG); the source code ships alongside this book in the same repository.",
    ]:
        c.setFont("Helvetica", 14)
        c.drawString(80, y, line)
        y -= 21.5
    c.bookmarkPage("provenance")
    c.addOutlineEntry("Data Provenance & Method", "provenance", 0)
    c.showPage()

    # ---------------------------------------------------------------- chapter TOC
    c.setFillColor(CREAM)
    c.rect(0, 0, PW, PH, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 30)
    c.drawString(80, PH - 90, "Contents")
    y = PH - 150
    counts = {}
    for r in rows:
        counts[r["Topic"]] = counts.get(r["Topic"], 0) + 1
    for ch in CHAPTERS:
        if ch not in first_of_chapter:
            continue
        num = first_of_chapter[ch]
        pg = page_of[num]
        c.setFont("Helvetica-Bold", 17)
        c.setFillColor(NAVY)
        c.drawString(110, y, CHAPTER_TITLES[ch])
        c.setFont("Helvetica", 14)
        c.setFillColor(INK2)
        c.drawString(560, y, f"{counts[ch]} plates")
        c.drawRightString(PW - 110, y, f"page {pg}")
        c.setStrokeColor(HexColor("#E4E4DC"))
        c.line(110, y - 8, PW - 110, y - 8)
        c.linkAbsolute("", f"p{num:03d}", (100, y - 10, PW - 100, y + 16))
        y -= 44
    c.setFont("Helvetica", 12)
    c.setFillColor(MUTED)
    c.drawString(110, y - 10, "All entries are clickable — chapter titles here, and every row of the image index that follows.")
    c.bookmarkPage("toc")
    c.addOutlineEntry("Contents", "toc", 0)
    c.showPage()

    # ---------------------------------------------------------------- image index
    for pg_i in range(n_index_pages):
        c.setFillColor(CREAM)
        c.rect(0, 0, PW, PH, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 24)
        c.drawString(80, PH - 70, f"Image Index  ({pg_i + 1}/{n_index_pages})")
        chunk = rows[pg_i * per_page : (pg_i + 1) * per_page]
        half = (len(chunk) + 1) // 2
        for col, sub in enumerate([chunk[:half], chunk[half:]]):
            x0 = 80 + col * 590
            y = PH - 110
            for r in sub:
                num = int(r["Image Name"][:3])
                c.setFont("Helvetica-Bold", 9.5)
                c.setFillColor(GOLD)
                c.drawString(x0, y, f"{num:03d}")
                c.setFont("Helvetica", 9.5)
                c.setFillColor(INK2)
                concept = r["Concept"][:44]
                c.drawString(x0 + 30, y, f"{concept}  ·  {r['Ticker']}  {r['Timeframe']}")
                c.setFillColor(MUTED)
                c.drawRightString(x0 + 545, y, str(page_of[num]))
                c.linkAbsolute("", f"p{num:03d}", (x0 - 4, y - 3, x0 + 550, y + 9))
                y -= 15.8
        c.bookmarkPage(f"idx{pg_i}")
        if pg_i == 0:
            c.addOutlineEntry("Image Index", "idx0", 0)
        c.showPage()

    # ---------------------------------------------------------------- plates
    chapter_seen = set()
    for r in rows:
        num = int(r["Image Name"][:3])
        ch = r["Topic"]
        path = os.path.join(IMG, ch, r["Image Name"])
        c.setFillColor(CREAM)
        c.rect(0, 0, PW, PH, fill=1, stroke=0)
        c.drawImage(plate_source(path), 0, 0, width=PW, height=PH)
        c.setFont("Helvetica", 9)
        c.setFillColor(MUTED)
        c.drawRightString(PW - 14, 8, f"{page_of[num]}")
        c.bookmarkPage(f"p{num:03d}")
        if ch not in chapter_seen:
            chapter_seen.add(ch)
            c.addOutlineEntry(CHAPTER_TITLES[ch], f"p{num:03d}", 0)
        c.addOutlineEntry(f"{num:03d} — {r['Concept']} ({r['Ticker']} {r['Timeframe']})", f"p{num:03d}", 1)
        c.showPage()

    c.save()
    print("PDF written:", OUT, f"{os.path.getsize(OUT)/1e6:.1f} MB, {front + len(rows)} pages")


if __name__ == "__main__":
    main()
