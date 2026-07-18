#!/usr/bin/env python3
"""Generates every original figure used in The Triple Analysis.
All price data is synthetic (random-walk generated) purely to illustrate
concepts -- none of it is copied from any reference chart or image.
"""
import numpy as np
import matplotlib.pyplot as plt
from figlib import (
    NAVY, NAVY_DEEP, GOLD, GOLD_LIGHT, CREAM, GREEN, RED, GREY, GRID,
    new_ax, save, synth_walk, to_ohlc, plot_candles, box, hline, arrow,
    marker_point, set_ylim_pad, rolling_mean,
)
from matplotlib.patches import Rectangle, FancyArrowPatch, Polygon
from matplotlib.lines import Line2D

# ============================================================ 1.1 legend
def fig_01_01():
    fig, ax = plt.subplots(figsize=(8.6, 5.4), dpi=150)
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
    fig.patch.set_facecolor("white")

    items = [
        ("box", GOLD_LIGHT, GOLD, "كتلة طلب صعودية (Order Block)"),
        ("box", "#F4A6A6", RED, "كتلة طلب هبوطية (Order Block)"),
        ("box", "#F2D98A", "#B7791F", "فجوة القيمة العادلة (FVG)"),
        ("hline", GREY, None, "مستوى السيولة"),
        ("arrow_solid", NAVY, None, "كسر الهيكل (BOS)"),
        ("arrow_dashed", RED, None, "تغيّر الطابع (CHOCH)"),
        ("tri_down", NAVY, None, "قمة تأرجحية (Swing High)"),
        ("tri_up", NAVY, None, "قاع تأرجحي (Swing Low)"),
    ]
    y = 9.0
    for kind, c1, c2, label in items:
        x0, x1 = 0.4, 1.6
        if kind == "box":
            ax.add_patch(Rectangle((x0, y - 0.35), x1 - x0, 0.7, facecolor=c1, edgecolor=c2, alpha=0.5, linewidth=1.6))
        elif kind == "hline":
            ax.plot([x0, x1], [y, y], color=c1, linestyle="--", linewidth=1.6)
        elif kind == "arrow_solid":
            ax.add_patch(FancyArrowPatch((x0, y - 0.3), (x1, y + 0.3), arrowstyle="-|>", color=c1, linewidth=2.2, mutation_scale=16))
        elif kind == "arrow_dashed":
            ax.add_patch(FancyArrowPatch((x0, y - 0.3), (x1, y + 0.3), arrowstyle="-|>", color=c1, linewidth=2.2, linestyle="dashed", mutation_scale=16))
        elif kind == "tri_down":
            ax.plot([1.0], [y], marker="v", color=c1, markersize=10)
        elif kind == "tri_up":
            ax.plot([1.0], [y], marker="^", color=c1, markersize=10)
        ax.text(2.0, y, label, fontsize=12, va="center", ha="left", color=NAVY)
        y -= 1.15
    save(fig, "fig-01-01")

# ============================================================ 2.1 Asian sweep -> London open
def fig_02_01():
    fig, ax = new_ax()
    asian = synth_walk(18, drift=0.0, vol=0.35, start=100, seed=11)
    london = synth_walk(22, drift=0.55, vol=0.9, start=asian[-1], seed=12)
    closes = np.concatenate([asian, london])
    o, h, l, c = to_ohlc(closes, seed=11)
    plot_candles(ax, o, h, l, c)
    hline(ax, h[:18].max(), 0, 17, color=GREY, label="أعلى نطاق الجلسة الآسيوية")
    hline(ax, l[:18].min(), 0, 17, color=GREY, label="أدنى نطاق الجلسة الآسيوية")
    arrow(ax, (17, h[:18].max()), (20, h[:18].max() + 1.6), color=RED, label="اكتساح سيولة")
    arrow(ax, (20, l[19]), (39, c[-1]), color=NAVY, label="توسّع جلسة لندن")
    ax.axvline(18, color=GOLD, linestyle=":", linewidth=1.4)
    ax.text(9, ax.get_ylim()[1], "الجلسة الآسيوية", color=GOLD, fontsize=9, ha="center", va="bottom", fontweight="bold")
    ax.text(29, ax.get_ylim()[1], "جلسة لندن", color=GOLD, fontsize=9, ha="center", va="bottom", fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h) + [h[:18].max() + 2.2])
    save(fig, "fig-02-01")

# ============================================================ 3.1 HH-HL then CHOCH
def fig_03_01():
    fig, ax = new_ax()
    up = synth_walk(26, drift=0.5, vol=0.7, start=100, seed=21)
    down = synth_walk(18, drift=-0.75, vol=0.8, start=up[-1], seed=22)
    closes = np.concatenate([up, down])
    o, h, l, c = to_ohlc(closes, seed=21)
    plot_candles(ax, o, h, l, c)
    for x in [4, 12, 20]:
        marker_point(ax, x, l[x] - 0.2, color=NAVY, label="HL", va="top", dy=0.9)
    for x in [8, 16]:
        marker_point(ax, x, h[x] + 0.2, color=NAVY, label="HH", va="bottom", dy=0.9)
    marker_point(ax, 26, h[26] + 0.2, color=RED, label="LH", va="bottom", dy=0.9)
    marker_point(ax, 34, l[34] - 0.2, color=RED, label="LL", va="top", dy=0.9)
    arrow(ax, (20, l[20] - 1), (25, h[25] + 1.4), color=NAVY, label="BOS")
    arrow(ax, (25, h[25] + 1.4), (30, l[30] - 1.6), color=RED, ls="dashed", label="CHOCH")
    set_ylim_pad(ax, list(l) + list(h))
    save(fig, "fig-03-01")

# ============================================================ 4.1 Equal lows sweep + CHOCH
def fig_04_01():
    fig, ax = new_ax()
    d1 = synth_walk(14, drift=-0.5, vol=0.6, start=108, seed=31)
    base = d1[-1]
    d2 = synth_walk(10, drift=0.1, vol=0.5, start=base + 1.2, seed=32)
    d3 = synth_walk(8, drift=-0.5, vol=0.5, start=d2[-1], seed=33)
    sweep = synth_walk(4, drift=-1.2, vol=0.4, start=d3[-1], seed=34)
    rev = synth_walk(16, drift=0.9, vol=0.7, start=sweep[-1], seed=35)
    closes = np.concatenate([d1, d2, d3, sweep, rev])
    o, h, l, c = to_ohlc(closes, seed=31)
    plot_candles(ax, o, h, l, c)
    eq_level = min(l[13], l[13 + 10 + 8 - 1])
    hline(ax, eq_level, 0, 36, color=GREY, label="قيعان متساوية (سيولة)")
    arrow(ax, (36, l[36] - 0.6), (40, l[36] - 2.2), color=RED, label="اكتساح")
    arrow(ax, (36, l[36] - 2.0), (51, c[-1]), color=NAVY, label="CHOCH ثم انعكاس")
    set_ylim_pad(ax, list(l) + list(h) + [eq_level - 2.5])
    save(fig, "fig-04-01")

# ============================================================ 5.1 Order block formation + retest
def fig_05_01():
    fig, ax = new_ax()
    pre = synth_walk(12, drift=-0.1, vol=0.4, start=100, seed=41)
    impulse = synth_walk(10, drift=1.1, vol=0.5, start=pre[-1], seed=42)
    pull = synth_walk(8, drift=-0.5, vol=0.5, start=impulse[-1], seed=43)
    cont = synth_walk(12, drift=0.9, vol=0.6, start=pull[-1], seed=44)
    closes = np.concatenate([pre, impulse, pull, cont])
    o, h, l, c = to_ohlc(closes, seed=41)
    plot_candles(ax, o, h, l, c)
    ob_x = 11
    box(ax, ob_x - 0.5, ob_x + 0.5, min(o[ob_x], c[ob_x]) - 0.15, max(o[ob_x], c[ob_x]) + 0.15,
        color=GOLD_LIGHT, edge=GOLD, label="كتلة طلب صعودية (Order Block)")
    arrow(ax, (12, c[12]), (21, c[21] + 1.2), color=NAVY, label="BOS")
    arrow(ax, (29, l[29] + 0.3), (30, o[ob_x]), color=GOLD, ls="dashed", label="إعادة اختبار")
    set_ylim_pad(ax, list(l) + list(h))
    save(fig, "fig-05-01")

# ============================================================ 5.2 Breaker block
def fig_05_02():
    fig, ax = new_ax()
    up = synth_walk(14, drift=0.6, vol=0.6, start=100, seed=51)
    ob_seg = synth_walk(6, drift=-0.2, vol=0.35, start=up[-1], seed=52)
    down = synth_walk(14, drift=-0.9, vol=0.7, start=ob_seg[-1], seed=53)
    retest = synth_walk(10, drift=-0.7, vol=0.5, start=down[-1], seed=54)
    closes = np.concatenate([up, ob_seg, down, retest])
    o, h, l, c = to_ohlc(closes, seed=51)
    plot_candles(ax, o, h, l, c)
    ob_x = 16
    y0, y1 = min(o[ob_x], c[ob_x]) - 0.15, max(o[ob_x], c[ob_x]) + 0.15
    box(ax, ob_x - 0.6, ob_x + 0.6, y0, y1, color=GOLD_LIGHT, edge=GOLD, label="كتلة طلب صعودية مكسورة (OB)")
    arrow(ax, (18, c[18]), (30, l[30] - 1.4), color=RED, label="كسر")
    arrow(ax, (38, h[38] + 0.3), (41, y0), color=RED, ls="dashed", label="إعادة اختبار كمقاومة")
    ax.text(ob_x, y0 - 1.0, "كتلة الكاسر (Breaker Block)", color=RED, fontsize=9.5, ha="center", fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h))
    save(fig, "fig-05-02")

# ============================================================ 6.1 FVG + OB confluence
def fig_06_01():
    fig, ax = new_ax()
    pre = synth_walk(10, drift=0.1, vol=0.4, start=100, seed=61)
    imp = synth_walk(3, drift=2.2, vol=0.3, start=pre[-1], seed=62)
    hold = synth_walk(14, drift=0.15, vol=0.5, start=imp[-1], seed=63)
    pull = synth_walk(10, drift=-0.55, vol=0.5, start=hold[-1], seed=64)
    closes = np.concatenate([pre, imp, hold, pull])
    o, h, l, c = to_ohlc(closes, seed=61)
    plot_candles(ax, o, h, l, c)
    x1, x2, x3 = 10, 11, 12
    fvg_low = h[x1]
    fvg_high = l[x3]
    if fvg_high < fvg_low:
        fvg_low, fvg_high = fvg_high, fvg_low
    box(ax, x1 + 0.3, x3 - 0.3, fvg_low, fvg_high, color="#F2D98A", edge="#B7791F", label="FVG")
    box(ax, 9.5, 10.5, min(o[9], c[9]) - 0.1, max(o[9], c[9]) + 0.1, color=GOLD_LIGHT, edge=GOLD)
    ax.text(10, min(o[9], c[9]) - 1.0, "Order Block", color=GOLD, fontsize=9, ha="center", fontweight="bold")
    arrow(ax, (33, l[33] + 0.4), (37, fvg_high), color=NAVY, ls="dashed", label="العودة إلى FVG / OB")
    set_ylim_pad(ax, list(l) + list(h))
    save(fig, "fig-06-01")

# ============================================================ 7.1 Inducement then continuation
def fig_07_01():
    fig, ax = new_ax()
    up1 = synth_walk(14, drift=0.55, vol=0.55, start=100, seed=71)
    dip = synth_walk(6, drift=-0.6, vol=0.35, start=up1[-1], seed=72)
    up2 = synth_walk(16, drift=0.7, vol=0.6, start=dip[-1], seed=73)
    closes = np.concatenate([up1, dip, up2])
    o, h, l, c = to_ohlc(closes, seed=71)
    plot_candles(ax, o, h, l, c)
    dip_x = 17
    marker_point(ax, dip_x, l[dip_x] - 0.15, color=RED, label="استدراج (اكتساح صغير)", va="top", dy=0.9)
    arrow(ax, (dip_x, l[dip_x]), (dip_x + 3, l[dip_x] + 1.5), color=RED, ls="dashed")
    arrow(ax, (dip_x + 3, l[dip_x] + 1.5), (35, c[-1]), color=NAVY, label="استمرار نحو الهدف / OB الرئيسية")
    set_ylim_pad(ax, list(l) + list(h))
    save(fig, "fig-07-01")

# ============================================================ 8.1 Discount zone + OB confluence
def fig_08_01():
    fig, ax = new_ax()
    up = synth_walk(28, drift=0.6, vol=0.7, start=100, seed=81)
    pull = synth_walk(14, drift=-0.55, vol=0.55, start=up[-1], seed=82)
    closes = np.concatenate([up, pull])
    o, h, l, c = to_ohlc(closes, seed=81)
    plot_candles(ax, o, h, l, c)
    swing_low = l[:28].min()
    swing_high = h[:28].max()
    rng = swing_high - swing_low
    disc_top = swing_low + rng * 0.30
    disc_bot = swing_low + rng * 0.15
    box(ax, 0, 42, disc_bot, disc_top, color="#DDEBDD", edge=GREEN, alpha=0.35, label="منطقة الخصم (ارتداد 70-85%)")
    hline(ax, swing_high, 0, 42, color=GREY, ls=":", label="قمة تأرجحية (Swing High)")
    hline(ax, swing_low, 0, 42, color=GREY, ls=":", label="قاع تأرجحي (Swing Low)")
    box(ax, 38, 40, disc_bot - 0.2, disc_top + 0.2, color=GOLD_LIGHT, edge=GOLD, label="OB")
    set_ylim_pad(ax, list(l) + list(h))
    save(fig, "fig-08-01")

# ============================================================ 9.1 IFC news candle
def fig_09_01():
    fig, ax = new_ax()
    pre = synth_walk(16, drift=0.05, vol=0.3, start=100, seed=91)
    news = synth_walk(2, drift=3.2, vol=0.3, start=pre[-1], seed=92)
    post = synth_walk(20, drift=0.5, vol=0.6, start=news[-1], seed=93)
    closes = np.concatenate([pre, news, post])
    o, h, l, c = to_ohlc(closes, seed=91)
    plot_candles(ax, o, h, l, c, width=0.7)
    news_x = 16
    ax.annotate("شمعة تمويل مؤسسي / خبر (IFC)", xy=(news_x, c[news_x]), xytext=(news_x + 3, c[news_x] + 3.5),
                fontsize=9.5, color=RED, fontweight="bold",
                arrowprops=dict(arrowstyle="-|>", color=RED, linewidth=1.8))
    fvg_lo, fvg_hi = h[15], l[17]
    if fvg_hi < fvg_lo:
        fvg_lo, fvg_hi = fvg_hi, fvg_lo
    box(ax, 15.6, 17.4, fvg_lo, fvg_hi, color="#F2D98A", edge="#B7791F", label="FVG متروكة خلفها")
    set_ylim_pad(ax, list(l) + list(h) + [c[news_x] + 4.5])
    save(fig, "fig-09-01")

# ============================================================ 10.1 Multi-timeframe triptych
def fig_10_01():
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 4.2), dpi=150)
    titles = ["يومي — الانحياز", "ساعة — منطقة الاهتمام", "5 دقائق — توقيت الدخول"]
    seeds = [101, 102, 103]
    drifts = [0.5, 0.15, 0.05]
    for ax, title, sd, dr in zip(axes, titles, seeds, drifts):
        closes = synth_walk(24, drift=dr, vol=0.6, start=100, seed=sd)
        o, h, l, c = to_ohlc(closes, seed=sd)
        plot_candles(ax, o, h, l, c, width=0.6)
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(title, fontsize=10, color=NAVY, fontweight="bold")
        set_ylim_pad(ax, list(l) + list(h))
    fig.tight_layout(pad=0.6)
    save(fig, "fig-10-01")

# ============================================================ 11.1 Confluence entry composite
def fig_11_01():
    fig, ax = new_ax()
    up = synth_walk(26, drift=0.55, vol=0.6, start=100, seed=111)
    pull = synth_walk(14, drift=-0.5, vol=0.5, start=up[-1], seed=112)
    cont = synth_walk(10, drift=0.8, vol=0.5, start=pull[-1], seed=113)
    closes = np.concatenate([up, pull, cont])
    o, h, l, c = to_ohlc(closes, seed=111)
    plot_candles(ax, o, h, l, c)
    swing_low, swing_high = l[:26].min(), h[:26].max()
    rng = swing_high - swing_low
    box(ax, 24, 40, swing_low + rng * 0.15, swing_low + rng * 0.30, color="#DDEBDD", edge=GREEN, alpha=0.3, label="منطقة الخصم")
    box(ax, 35, 37, min(o[36], c[36]) - 0.2, max(o[36], c[36]) + 0.2, color=GOLD_LIGHT, edge=GOLD, label="Order Block")
    fvg_lo, fvg_hi = h[37], l[39]
    if fvg_hi < fvg_lo: fvg_lo, fvg_hi = fvg_hi, fvg_lo
    box(ax, 37.6, 39.4, fvg_lo, fvg_hi, color="#F2D98A", edge="#B7791F", label="FVG")
    hline(ax, l[26:40].min(), 24, 40, color=GREY, label="سيولة مكتسحة")
    ax.text(20, ax.get_ylim()[1], "5 عوامل تقارب ← دخول عالي الاحتمالية", color=NAVY, fontsize=9.5,
            ha="center", va="bottom", fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h))
    save(fig, "fig-11-01")

# ============================================================ 12.1 Weekly systems
def fig_12_01():
    fig, ax = new_ax()
    seg1 = synth_walk(10, drift=0.5, vol=0.5, start=100, seed=121)
    seg2 = synth_walk(10, drift=-0.1, vol=0.5, start=seg1[-1], seed=122)
    seg3 = synth_walk(10, drift=0.7, vol=0.6, start=seg2[-1], seed=123)
    seg4 = synth_walk(10, drift=0.2, vol=0.4, start=seg3[-1], seed=124)
    closes = np.concatenate([seg1, seg2, seg3, seg4])
    o, h, l, c = to_ohlc(closes, seed=121)
    plot_candles(ax, o, h, l, c)
    marker_point(ax, 5, l[5] - 0.2, color=NAVY, label="الإثنين: النظام 1 (OB)", va="top", dy=0.9)
    marker_point(ax, 23, l[23] - 0.2, color=GOLD, label="الأربعاء: النظام 2 (اكتساح+FVG)", va="top", dy=0.9)
    for day_x, day in zip([0, 10, 20, 30], ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس"]):
        ax.axvline(day_x, color=GRID, linewidth=1)
        ax.text(day_x + 4, ax.get_ylim()[1] if False else h.max() + 1.2, day, fontsize=8.5, color=GREY, ha="center")
    set_ylim_pad(ax, list(l) + list(h) + [h.max() + 1.6])
    save(fig, "fig-12-01")

# ============================================================ 13.1 Actual vs forecast reaction
def fig_13_01():
    fig, ax = plt.subplots(figsize=(8.6, 4.4), dpi=150)
    fig.patch.set_facecolor("white")
    cats = ["التوقع", "الفعلي"]
    vals = [3.1, 3.4]
    colors = [GREY, GOLD]
    bars = ax.bar(cats, vals, color=colors, width=0.5, zorder=3)
    ax.set_ylabel("التضخم السنوي CPI (%)")
    ax.grid(axis="y", color=GRID, zorder=0)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.05, f"{v}%", ha="center", fontsize=10, fontweight="bold", color=NAVY)
    ax2 = ax.inset_axes([1.15, 0.15, 0.7, 0.7])
    closes = synth_walk(20, drift=0.0, vol=0.15, start=100, seed=131)
    closes[8:] += 1.4
    ax2.plot(closes, color=NAVY, linewidth=2)
    ax2.axvline(8, color=RED, linestyle="--", linewidth=1.2)
    ax2.text(8.3, closes.max(), "صدور البيانات", color=RED, fontsize=8)
    ax2.set_title("ردة فعل السعر", fontsize=9, color=NAVY)
    ax2.set_xticks([]); ax2.set_yticks([])
    for s in ax2.spines.values(): s.set_visible(False)
    save(fig, "fig-13-01")

# ============================================================ 14.1 Rate decision vs presser
def fig_14_01():
    fig, ax = new_ax(price_axis=True)
    closes = synth_walk(40, drift=0.02, vol=0.25, start=100, seed=141)
    decision_x, presser_x = 15, 22
    closes[decision_x:presser_x] += 0.1
    closes[presser_x:] += np.linspace(0, 3.0, 40 - presser_x)
    ax.plot(closes, color=NAVY, linewidth=1.8)
    ax.axvline(decision_x, color=GREY, linestyle=":", linewidth=1.4)
    ax.axvline(presser_x, color=GOLD, linestyle="--", linewidth=1.6)
    ax.text(decision_x, closes.max() + 0.3, "قرار الفائدة\n(كما هو متوقع)", fontsize=8.5, color=GREY, ha="center")
    ax.text(presser_x, closes.max() + 1.6, "المؤتمر الصحفي\n(نبرة متشددة)", fontsize=8.5, color=GOLD, ha="center", fontweight="bold")
    arrow(ax, (presser_x, closes[presser_x]), (39, closes[-1]), color=GOLD, label="ارتفاع العملة")
    ax.set_ylabel("مؤشر العملة")
    save(fig, "fig-14-01")

# ============================================================ 15.1 Rate differential vs FX
def fig_15_01():
    fig, ax1 = plt.subplots(figsize=(8.6, 4.6), dpi=150)
    fig.patch.set_facecolor("white")
    n = 30
    diff = np.linspace(0.5, 2.8, n) + np.random.default_rng(151).normal(0, 0.05, n)
    fx = 1.10 + np.cumsum(np.random.default_rng(152).normal(0.004, 0.006, n))
    ax1.plot(diff, color=GOLD, linewidth=2.2, label="فارق الفائدة (نقطة مئوية)")
    ax1.set_ylabel("فارق الفائدة (نقطة مئوية)", color=GOLD)
    ax1.tick_params(axis="y", labelcolor=GOLD)
    for s in ["top"]: ax1.spines[s].set_visible(False)
    ax2 = ax1.twinx()
    ax2.plot(fx, color=NAVY, linewidth=2.2, label="زوج العملات")
    ax2.set_ylabel("زوج العملات", color=NAVY)
    ax2.tick_params(axis="y", labelcolor=NAVY)
    for s in ["top"]: ax2.spines[s].set_visible(False)
    ax1.set_xticks([]); ax1.grid(axis="y", color=GRID)
    ax1.set_xlabel("الزمن")
    save(fig, "fig-15-01")

# ============================================================ 16.1 Headline vs core CPI
def fig_16_01():
    fig, ax = plt.subplots(figsize=(8.6, 4.4), dpi=150)
    fig.patch.set_facecolor("white")
    months = np.arange(12)
    headline = 6.5 - months * 0.25 + np.random.default_rng(161).normal(0, 0.1, 12)
    core = 5.8 - months * 0.12 + np.random.default_rng(162).normal(0, 0.08, 12)
    ax.plot(months, headline, color=NAVY, linewidth=2.2, marker="o", markersize=4, label="التضخم العام (CPI)")
    ax.plot(months, core, color=GOLD, linewidth=2.2, marker="o", markersize=4, label="التضخم الأساسي (Core CPI)")
    ax.set_ylabel("التغير السنوي (%)")
    ax.set_xlabel("الشهر")
    ax.grid(axis="y", color=GRID)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    ax.legend(frameon=False, fontsize=9.5)
    save(fig, "fig-16-01")

# ============================================================ 17.1 NFP reaction
def fig_17_01():
    fig, ax = new_ax()
    pre = synth_walk(10, drift=0.0, vol=0.12, start=100, seed=171)
    spike = synth_walk(3, drift=1.6, vol=0.2, start=pre[-1], seed=172)
    fade = synth_walk(15, drift=-0.2, vol=0.25, start=spike[-1], seed=173)
    closes = np.concatenate([pre, spike, fade])
    ax.plot(closes, color=NAVY, linewidth=1.9)
    ax.axvline(10, color=RED, linestyle="--", linewidth=1.4)
    ax.text(10.2, closes.max(), "صدور بيانات التوظيف (NFP)", color=RED, fontsize=9, fontweight="bold")
    arrow(ax, (13, spike[-1]), (16, fade[2]), color=GOLD, ls="dashed", label="تراجع جزئي\n(ضعف الأجور)")
    ax.set_ylabel("مؤشر الدولار")
    save(fig, "fig-17-01")

# ============================================================ 18.1 GDP components pie
def fig_18_01():
    fig, ax = plt.subplots(figsize=(6.4, 6.4), dpi=150)
    fig.patch.set_facecolor("white")
    labels = ["الاستهلاك", "الاستثمار", "الإنفاق\nالحكومي", "صافي الصادرات"]
    sizes = [58, 20, 17, 5]
    colors = [NAVY, GOLD, GOLD_LIGHT, GREY]
    ax.pie(sizes, labels=labels, colors=colors, autopct="%1.0f%%", startangle=90,
           textprops={"fontsize": 10, "color": "white", "fontweight": "bold"},
           wedgeprops={"edgecolor": "white", "linewidth": 1.5})
    for t in ax.texts:
        if "%" not in t.get_text():
            t.set_color(NAVY)
            t.set_fontweight("bold")
    ax.set_aspect("equal")
    save(fig, "fig-18-01")

# ============================================================ 19.1 PMI leading GDP
def fig_19_01():
    fig, ax1 = plt.subplots(figsize=(8.6, 4.6), dpi=150)
    fig.patch.set_facecolor("white")
    months = np.arange(12)
    pmi = 56 - months * 1.1 + np.random.default_rng(191).normal(0, 0.4, 12)
    gdp = 2.8 - np.maximum(0, months - 5) * 0.35 + np.random.default_rng(192).normal(0, 0.05, 12)
    ax1.plot(months, pmi, color=GOLD, linewidth=2.2, marker="o", markersize=4)
    ax1.axhline(50, color=GREY, linestyle=":", linewidth=1.2)
    ax1.set_ylabel("PMI", color=GOLD)
    ax1.tick_params(axis="y", labelcolor=GOLD)
    for s in ["top"]: ax1.spines[s].set_visible(False)
    ax2 = ax1.twinx()
    ax2.plot(months, gdp, color=NAVY, linewidth=2.2, linestyle="--", marker="s", markersize=4)
    ax2.set_ylabel("نمو الناتج المحلي الإجمالي (%)", color=NAVY)
    ax2.tick_params(axis="y", labelcolor=NAVY)
    for s in ["top"]: ax2.spines[s].set_visible(False)
    ax1.set_xlabel("الشهر")
    ax1.grid(axis="y", color=GRID)
    save(fig, "fig-19-01")

# ============================================================ 20.1 Trade balance vs currency
def fig_20_01():
    fig, ax1 = plt.subplots(figsize=(8.6, 4.6), dpi=150)
    fig.patch.set_facecolor("white")
    months = np.arange(12)
    surplus = 2 + months * 0.6 + np.random.default_rng(201).normal(0, 0.3, 12)
    curr = 100 + np.cumsum(np.random.default_rng(202).normal(0.5, 0.4, 12))
    ax1.bar(months, surplus, color=GOLD_LIGHT, width=0.5, zorder=3, label="الفائض التجاري")
    ax1.set_ylabel("الفائض التجاري (مليار دولار)", color=GOLD)
    ax1.tick_params(axis="y", labelcolor=GOLD)
    ax1.grid(axis="y", color=GRID, zorder=0)
    for s in ["top"]: ax1.spines[s].set_visible(False)
    ax2 = ax1.twinx()
    ax2.plot(months, curr, color=NAVY, linewidth=2.4)
    ax2.set_ylabel("قيمة العملة", color=NAVY)
    ax2.tick_params(axis="y", labelcolor=NAVY)
    for s in ["top"]: ax2.spines[s].set_visible(False)
    ax1.set_xlabel("الشهر")
    save(fig, "fig-20-01")

# ============================================================ 21.1 Earnings beat, weak guidance
def fig_21_01():
    fig, ax = new_ax()
    pre = synth_walk(10, drift=0.05, vol=0.3, start=100, seed=211)
    pop = synth_walk(2, drift=1.5, vol=0.2, start=pre[-1], seed=212)
    fade = synth_walk(16, drift=-0.6, vol=0.4, start=pop[-1], seed=213)
    closes = np.concatenate([pre, pop, fade])
    o, h, l, c = to_ohlc(closes, seed=211)
    plot_candles(ax, o, h, l, c)
    ax.axvline(10, color=GREY, linestyle=":", linewidth=1.2)
    ax.text(10.2, h.max(), "الأرباح: تفوق التوقعات", fontsize=8.5, color=GREEN, fontweight="bold")
    arrow(ax, (12, c[12]), (26, c[-1]), color=RED, label="توجيهات ضعيفة ← بيع مكثف")
    set_ylim_pad(ax, list(l) + list(h))
    save(fig, "fig-21-01")

# ============================================================ 22.1 Weekly calendar impact
def fig_22_01():
    fig, ax = plt.subplots(figsize=(8.6, 4.2), dpi=150)
    fig.patch.set_facecolor("white")
    days = ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة"]
    impact = [1, 2, 3, 2, 1]
    colors = [GOLD_LIGHT if v < 3 else RED for v in impact]
    ax.barh(days, impact, color=colors, zorder=3)
    ax.set_xlabel("الأثر المتوقع (1=منخفض، 3=مرتفع)")
    ax.set_xlim(0, 3.5)
    ax.invert_yaxis()
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    ax.grid(axis="x", color=GRID, zorder=0)
    labels = ["مبيعات التجزئة", "PMI", "قرار الفائدة", "طلبات إعانة البطالة", "ثقة المستهلك"]
    for i, (d, lab) in enumerate(zip(days, labels)):
        ax.text(impact[i] + 0.1, i, lab, va="center", fontsize=9, color=NAVY)
    save(fig, "fig-22-01")

# ============================================================ 23.1 Dow theory primary/secondary
def fig_23_01():
    fig, ax = new_ax()
    seg = []
    starts = [100]
    drifts = [0.55, -0.35, 0.6, -0.3, 0.65]
    lens = [10, 6, 10, 6, 10]
    seeds = range(231, 236)
    cur = 100
    all_closes = []
    for dr, ln, sd in zip(drifts, lens, seeds):
        c_ = synth_walk(ln, drift=dr, vol=0.5, start=cur, seed=sd)
        all_closes.append(c_)
        cur = c_[-1]
    closes = np.concatenate(all_closes)
    o, h, l, c = to_ohlc(closes, seed=231)
    plot_candles(ax, o, h, l, c)
    # primary trendline through major swing lows
    ax.plot([0, 41], [l[0] + 0.5, l[26] + 3], color=NAVY, linewidth=2, linestyle="-")
    ax.text(41.5, l[26] + 3, "الاتجاه الرئيسي", color=NAVY, fontsize=9, fontweight="bold", va="center")
    ax.axvspan(10, 16, color=RED, alpha=0.08)
    ax.text(13, h.max() + 0.5, "تصحيح\nثانوي", color=RED, fontsize=8.5, ha="center", fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h) + [h.max() + 1.5])
    save(fig, "fig-23-01")

# ============================================================ 24.1 Candlestick vs Heikin Ashi
def fig_24_01():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.3), dpi=150)
    closes = synth_walk(24, drift=0.3, vol=0.7, start=100, seed=241)
    o, h, l, c = to_ohlc(closes, seed=241)
    plot_candles(axes[0], o, h, l, c)
    axes[0].set_title("الشموع اليابانية", fontsize=10.5, color=NAVY, fontweight="bold")
    # Heikin Ashi transform
    ha_c = (o + h + l + c) / 4
    ha_o = np.zeros_like(o)
    ha_o[0] = (o[0] + c[0]) / 2
    for i in range(1, len(o)):
        ha_o[i] = (ha_o[i - 1] + ha_c[i - 1]) / 2
    ha_h = np.maximum.reduce([h, ha_o, ha_c])
    ha_l = np.minimum.reduce([l, ha_o, ha_c])
    plot_candles(axes[1], ha_o, ha_h, ha_l, ha_c)
    axes[1].set_title("هايكن آشي (ممهدة)", fontsize=10.5, color=NAVY, fontweight="bold")
    for ax in axes:
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        ax.set_xticks([]); ax.set_yticks([])
    fig.tight_layout(pad=0.6)
    save(fig, "fig-24-01")

# ============================================================ 25.1 Candlestick pattern reference sheet
def _draw_candle_shape(ax, cx, o, h, l, c, w=0.5):
    color = GREEN if c >= o else RED
    ax.plot([cx, cx], [l, h], color=color, linewidth=2, solid_capstyle="round")
    b0, b1 = min(o, c), max(o, c)
    if b1 - b0 < 0.05:
        b1 = b0 + 0.05
    ax.add_patch(Rectangle((cx - w / 2, b0), w, b1 - b0, facecolor=color, edgecolor=color))

def fig_25_01():
    fig, axes = plt.subplots(2, 3, figsize=(10, 6.4), dpi=150)
    specs = [
        ("المطرقة (Hammer)", [(0, 1, 0, 4, 1)]),
        ("الشهاب (Shooting Star)", [(0, 4, 5, 1, 0)]),
        ("الابتلاع الصعودي (Bullish Engulfing)", [(0, 3, 0.3, 3.3, 1), (1, 1, -0.2, 3.5, 3.3)]),
        ("الابتلاع الهبوطي (Bearish Engulfing)", [(0, 1, 3, 3.5, 3.3), (1, 3.3, 0.3, 3.6, 1)]),
        ("الدوجي (Doji)", [(0, 2, 0, 5, 2.08)]),
        ("نجمة الصباح (Morning Star)", [(0, 4, 4.3, 0.8, 1), (1, 1.15, 1.35, 0.75, 0.95), (2, 1.2, 4.3, 1.0, 4)]),
    ]
    for ax, (title, candles) in zip(axes.flat, specs):
        for cx, o, h, l, c in candles:
            _draw_candle_shape(ax, cx, o, h, l, c)
        ax.set_xlim(-1, 3)
        ax.set_ylim(-0.5, 6)
        ax.set_title(title, fontsize=10.5, color=NAVY, fontweight="bold")
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values(): s.set_visible(False)
    fig.tight_layout(pad=1.0)
    save(fig, "fig-25-01")

# ============================================================ 25.2 Hammer context dependent
def fig_25_02():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.3), dpi=150)
    # panel A: hammer mid-range, fails
    a = axes[0]
    closes = synth_walk(20, drift=-0.05, vol=0.5, start=100, seed=252)
    o, h, l, c = to_ohlc(closes, seed=252)
    o[10], h[10], l[10], c[10] = 98.5, 98.7, 96.5, 98.6
    plot_candles(a, o, h, l, c)
    a.text(10, l[10] - 1.2, "مطرقة\n(بدون سياق)", ha="center", color=RED, fontsize=9, fontweight="bold")
    arrow(a, (10, c[10]), (19, l[19] - 1), color=RED, label="تفشل")
    a.set_title("بدون سياق دعم/OB", fontsize=10, color=NAVY)
    # panel B: hammer at OB, succeeds
    b = axes[1]
    closes2 = synth_walk(20, drift=-0.4, vol=0.5, start=105, seed=253)
    o2, h2, l2, c2 = to_ohlc(closes2, seed=253)
    o2[15], h2[15], l2[15], c2[15] = 96.5, 96.7, 94.3, 96.6
    plot_candles(b, o2, h2, l2, c2)
    box(b, 14.4, 15.6, l2[15] - 0.3, o2[15] + 0.5, color=GOLD_LIGHT, edge=GOLD, label="Order Block")
    arrow(b, (15, c2[15]), (19, c2[15] + 2.5), color=GREEN, label="تنجح")
    b.set_title("عند كتلة طلب (Order Block)", fontsize=10, color=NAVY)
    for ax in axes:
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        ax.set_xticks([])
    fig.tight_layout(pad=0.8)
    save(fig, "fig-25-02")

# ============================================================ 26.1 Role reversal
def fig_26_01():
    fig, ax = new_ax()
    approach = synth_walk(14, drift=0.15, vol=0.4, start=100, seed=261)
    level = approach.max() + 0.5
    breakout = synth_walk(3, drift=1.2, vol=0.3, start=approach[-1], seed=262)
    cont = synth_walk(6, drift=0.5, vol=0.4, start=breakout[-1], seed=263)
    retest = synth_walk(5, drift=-0.3, vol=0.3, start=cont[-1], seed=264)
    bounce = synth_walk(10, drift=0.6, vol=0.5, start=retest[-1], seed=265)
    closes = np.concatenate([approach, breakout, cont, retest, bounce])
    o, h, l, c = to_ohlc(closes, seed=261)
    plot_candles(ax, o, h, l, c)
    hline(ax, level, 0, len(closes) - 1, color=GOLD, label="مقاومة سابقة ← دعم جديد")
    arrow(ax, (14, c[14]), (17, c[17] + 1.5), color=GREEN, label="اختراق")
    arrow(ax, (23, l[23] + 0.2), (28, l[28] + 0.2), color=GOLD, ls="dashed", label="إعادة اختبار ناجحة")
    set_ylim_pad(ax, list(l) + list(h))
    save(fig, "fig-26-01")

# ============================================================ 26.2 Trendline & channel
def fig_26_02():
    fig, ax = new_ax()
    n = 30
    x = np.arange(n)
    base = 100 + x * 0.4
    noise = np.random.default_rng(266).normal(0, 0.9, n)
    closes = base + noise
    o, h, l, c = to_ohlc(closes, seed=266)
    plot_candles(ax, o, h, l, c)
    lower = base - 2.2
    upper = base + 2.2
    ax.plot(x, lower, color=NAVY, linewidth=2)
    ax.plot(x, upper, color=NAVY, linewidth=2, linestyle="--")
    ax.text(n - 1.5, lower[-1] - 0.5, "خط الاتجاه (دعم)", color=NAVY, fontsize=9, ha="right", fontweight="bold")
    ax.text(n - 1.5, upper[-1] + 0.8, "القناة (مقاومة)", color=NAVY, fontsize=9, ha="right", fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h) + [lower.min() - 1, upper.max() + 1])
    save(fig, "fig-26-02")

# ============================================================ 27.1 RSI divergence
def rsi(closes, period=14):
    deltas = np.diff(closes)
    seed = deltas[:period]
    up = seed[seed > 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi_arr = np.zeros_like(closes)
    rsi_arr[:period] = 100. - 100. / (1. + rs)
    for i in range(period, len(closes)):
        delta = deltas[i - 1]
        upval = max(delta, 0)
        downval = -min(delta, 0)
        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period
        rs = up / down if down != 0 else 0
        rsi_arr[i] = 100. - 100. / (1. + rs)
    return rsi_arr

def fig_27_01():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.6, 6), dpi=150, gridspec_kw={"height_ratios": [2.2, 1]})
    n = 40
    closes = 100 + np.linspace(0, 8, n) + np.random.default_rng(271).normal(0, 0.5, n)
    closes[-6:] += np.linspace(0.5, 2.2, 6)  # new high
    o, h, l, c = to_ohlc(closes, seed=271)
    plot_candles(ax1, o, h, l, c)
    for s in ["top", "right"]: ax1.spines[s].set_visible(False)
    ax1.set_xticks([]); ax1.set_ylabel("السعر")
    ax1.grid(axis="y", color=GRID)
    r = rsi(closes)
    r[20:26] -= np.linspace(0, 6, 6)
    r[-6:] -= np.linspace(4, 10, 6)
    ax2.plot(r, color=GOLD, linewidth=2)
    ax2.axhline(70, color=GREY, linestyle=":", linewidth=1)
    ax2.axhline(30, color=GREY, linestyle=":", linewidth=1)
    ax2.set_ylabel("RSI")
    ax2.set_xlabel("الزمن")
    for s in ["top", "right"]: ax2.spines[s].set_visible(False)
    ax1.plot([22, n - 3], [h[22] + 0.3, h[n - 3] + 0.3], color=RED, linewidth=1.6, linestyle="--")
    ax2.plot([22, n - 3], [r[22] + 1, r[n - 3] + 1], color=RED, linewidth=1.6, linestyle="--")
    ax1.text((22 + n - 3) / 2, h.max() + 1, "تباعد هبوطي", color=RED, fontsize=9.5, ha="center", fontweight="bold")
    fig.tight_layout(pad=0.6)
    save(fig, "fig-27-01")

# ============================================================ 28.1 Chart pattern reference sheet
def fig_28_01():
    fig, axes = plt.subplots(2, 3, figsize=(10.5, 6.6), dpi=150)

    def hs(ax):
        x = np.linspace(0, 10, 100)
        y = np.zeros_like(x)
        y += 1.2 * np.exp(-((x - 2) ** 2) / 0.3)
        y += 2.2 * np.exp(-((x - 5) ** 2) / 0.4)
        y += 1.2 * np.exp(-((x - 8) ** 2) / 0.3)
        y += np.linspace(0, -0.3, 100)
        ax.plot(x, y, color=NAVY, linewidth=2)
        ax.axhline(0.15, color=GOLD, linestyle="--", linewidth=1.4)
        ax.set_title("الرأس والكتفين (Head & Shoulders)", fontsize=10, fontweight="bold", color=NAVY)

    def dt(ax):
        x = np.linspace(0, 10, 100)
        y = 1.8 * np.exp(-((x - 2.5) ** 2) / 0.5) + 1.8 * np.exp(-((x - 7) ** 2) / 0.5) + 0.2
        ax.plot(x, y, color=NAVY, linewidth=2)
        ax.axhline(0.5, color=GOLD, linestyle="--", linewidth=1.4)
        ax.set_title("القمة المزدوجة (Double Top)", fontsize=10, fontweight="bold", color=NAVY)

    def tri(ax):
        x_apex = (2 - 0.3) / (0.12 + 0.08)
        x = np.linspace(0, x_apex * 0.94, 100)
        upper = 2 - x * 0.12
        lower = 0.3 + x * 0.08
        ax.plot(x, upper, color=NAVY, linewidth=2)
        ax.plot(x, lower, color=NAVY, linewidth=2)
        zig_x = np.array([0.5, 1.8, 2.6, 3.9, 4.7, 5.9])
        zig_y = np.array([1.55, 0.85, 1.35, 1.0, 1.2, 1.05])
        ax.plot(zig_x, zig_y, color=GOLD, linewidth=1.6)
        ax.set_title("المثلث المتماثل (Symmetrical Triangle)", fontsize=10, fontweight="bold", color=NAVY)

    def wedge(ax):
        x = np.linspace(0, 10, 100)
        upper = 0.8 + x * 0.18
        lower = 0.2 + x * 0.22
        ax.plot(x, upper, color=NAVY, linewidth=2)
        ax.plot(x, lower, color=NAVY, linewidth=2)
        ax.set_title("الوتد الصاعد (Rising Wedge)", fontsize=10, fontweight="bold", color=NAVY)

    def flag(ax):
        x1 = np.linspace(0, 4, 40)
        y1 = x1 * 0.9
        x2 = np.linspace(4, 7, 30)
        y2 = y1[-1] - (x2 - 4) * 0.15 + 0.1 * np.sin((x2 - 4) * 6)
        x3 = np.linspace(7, 10, 30)
        y3 = y2[-1] + (x3 - 7) * 0.85
        ax.plot(x1, y1, color=NAVY, linewidth=2)
        ax.plot(x2, y2, color=GOLD, linewidth=2)
        ax.plot(x3, y3, color=NAVY, linewidth=2)
        ax.set_title("العلم الصعودي (Bull Flag)", fontsize=10, fontweight="bold", color=NAVY)

    def rect(ax):
        x = np.linspace(0, 10, 100)
        y = 1 + 0.4 * np.sin(x * 2.2)
        ax.plot(x, y, color=NAVY, linewidth=2)
        ax.axhline(1.35, color=GOLD, linestyle="--", linewidth=1.2)
        ax.axhline(0.65, color=GOLD, linestyle="--", linewidth=1.2)
        ax.set_title("المستطيل (Rectangle)", fontsize=10, fontweight="bold", color=NAVY)

    for ax, fn in zip(axes.flat, [hs, dt, tri, wedge, flag, rect]):
        fn(ax)
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values(): s.set_visible(False)
    fig.tight_layout(pad=1.0)
    save(fig, "fig-28-01")

# ============================================================ 28.2 Head & shoulders measured move
def fig_28_02():
    fig, ax = new_ax()
    x = np.arange(46)
    base = 100 + np.concatenate([
        np.linspace(0, 4, 10),
        np.linspace(4, 1, 6),
        np.linspace(1, 7, 8),
        np.linspace(7, 1.5, 8),
        np.linspace(1.5, 4.2, 6),
        np.linspace(4.2, -3, 8),
    ])
    noise = np.random.default_rng(282).normal(0, 0.2, len(base))
    closes = base + noise
    o, h, l, c = to_ohlc(closes, seed=282)
    plot_candles(ax, o, h, l, c)
    neckline = 101.3
    hline(ax, neckline, 0, 45, color=GOLD, label="خط العنق (Neckline)")
    head_top = max(h[16:24])
    arrow(ax, (20, head_top), (20, neckline), color=NAVY, style="<->", label="ارتفاع الرأس")
    target = neckline - (head_top - neckline)
    hline(ax, target, 38, 45, color=RED, label="الهدف المُقاس")
    set_ylim_pad(ax, list(l) + list(h) + [target - 1])
    save(fig, "fig-28-02")

# ============================================================ 29.1 Price + RSI/MACD panel
def fig_29_01():
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8.6, 7.6), dpi=150,
                                          gridspec_kw={"height_ratios": [2, 1, 1]})
    n = 40
    closes = 100 + np.linspace(0, 6, n) + np.random.default_rng(291).normal(0, 0.4, n)
    closes[-6:] += np.linspace(0.3, 1.6, 6)
    o, h, l, c = to_ohlc(closes, seed=291)
    plot_candles(ax1, o, h, l, c)
    ax1.set_xticks([]); ax1.grid(axis="y", color=GRID)
    for s in ["top", "right"]: ax1.spines[s].set_visible(False)
    ax1.set_ylabel("السعر")

    r = rsi(closes)
    r[-6:] -= np.linspace(3, 9, 6)
    ax2.plot(r, color=GOLD, linewidth=1.8)
    ax2.axhline(70, color=GREY, linestyle=":", linewidth=1)
    ax2.axhline(30, color=GREY, linestyle=":", linewidth=1)
    ax2.set_ylabel("RSI")
    ax2.set_xticks([])
    for s in ["top", "right"]: ax2.spines[s].set_visible(False)

    ema12 = rolling_mean(closes, 3)
    ema26 = rolling_mean(closes, 8)
    macd = ema12 - ema26
    signal = rolling_mean(macd, 4)
    ax3.bar(np.arange(n), macd - signal, color=[GREEN if v >= 0 else RED for v in macd - signal], width=0.7)
    ax3.plot(macd, color=NAVY, linewidth=1.5)
    ax3.plot(signal, color=RED, linewidth=1.3, linestyle="--")
    ax3.set_ylabel("MACD")
    ax3.set_xlabel("الزمن")
    for s in ["top", "right"]: ax3.spines[s].set_visible(False)
    fig.tight_layout(pad=0.6)
    save(fig, "fig-29-01")

# ============================================================ 29.2 MA crossover
def fig_29_02():
    fig, ax = new_ax()
    n = 50
    closes = 100 + np.cumsum(np.random.default_rng(292).normal(0.12, 0.6, n))
    o, h, l, c = to_ohlc(closes, seed=292)
    plot_candles(ax, o, h, l, c, width=0.55)
    ma_fast = rolling_mean(closes, 5)
    ma_slow = rolling_mean(closes, 15)
    ax.plot(ma_fast, color=GOLD, linewidth=2, label="MA 5")
    ax.plot(ma_slow, color=NAVY, linewidth=2, label="MA 20")
    cross_x = 18
    marker_point(ax, cross_x, ma_fast[cross_x], color=GREEN, label="التقاطع الذهبي (Golden Cross)", va="top", dy=1.2)
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    set_ylim_pad(ax, list(l) + list(h))
    save(fig, "fig-29-02")

# ============================================================ 29.3 Bollinger squeeze
def fig_29_03():
    fig, ax = new_ax()
    n = 45
    vol = np.concatenate([np.full(20, 0.25), np.linspace(0.25, 1.4, 10), np.full(15, 1.3)])
    closes = 100 + np.cumsum(np.random.default_rng(293).normal(0, vol))
    o, h, l, c = to_ohlc(closes, seed=293)
    plot_candles(ax, o, h, l, c, width=0.55)
    ma = rolling_mean(closes, 10)
    rolling_std = np.array([closes[max(0, i - 10):i + 1].std() for i in range(n)])
    upper = ma + 2 * rolling_std
    lower = ma - 2 * rolling_std
    ax.plot(ma, color=NAVY, linewidth=1.6)
    ax.plot(upper, color=GOLD, linewidth=1.6, linestyle="--")
    ax.plot(lower, color=GOLD, linewidth=1.6, linestyle="--")
    ax.fill_between(np.arange(n), lower, upper, color=GOLD_LIGHT, alpha=0.15)
    ax.axvspan(10, 20, color=GREY, alpha=0.12)
    ax.text(15, ax.get_ylim()[1] if False else h.max(), "انضغاط (Squeeze)", color=GREY, fontsize=9, ha="center", fontweight="bold")
    ax.text(35, h.max(), "توسّع (Expansion)", color=GOLD, fontsize=9, ha="center", fontweight="bold")
    set_ylim_pad(ax, list(lower) + list(upper))
    save(fig, "fig-29-03")

# ============================================================ 30.1 Volume failure
def fig_30_01():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.6, 6), dpi=150, gridspec_kw={"height_ratios": [2.2, 1]})
    pre = synth_walk(14, drift=0.0, vol=0.18, start=100, seed=301)
    level = pre.max() + 0.4
    brk = synth_walk(3, drift=1.1, vol=0.25, start=pre[-1], seed=302)
    fail = synth_walk(12, drift=-0.6, vol=0.35, start=brk[-1], seed=303)
    closes = np.concatenate([pre, brk, fail])
    o, h, l, c = to_ohlc(closes, seed=301)
    plot_candles(ax1, o, h, l, c)
    hline(ax1, level, 0, len(closes) - 1, color=GOLD, label="مقاومة")
    for s in ["top", "right"]: ax1.spines[s].set_visible(False)
    ax1.set_xticks([]); ax1.grid(axis="y", color=GRID)
    vols = np.random.default_rng(304).uniform(0.5, 1.0, len(closes))
    vols[14:17] = np.random.default_rng(305).uniform(0.25, 0.4, 3)
    ax2.bar(np.arange(len(closes)), vols, color=[RED if i in (14, 15, 16) else NAVY for i in range(len(closes))], width=0.6)
    ax2.set_ylabel("الحجم")
    ax2.set_xlabel("الزمن")
    ax2.text(15, vols.max(), "Weak volume\non breakout", color=RED, fontsize=8.5, ha="center", fontweight="bold")
    for s in ["top", "right"]: ax2.spines[s].set_visible(False)
    fig.tight_layout(pad=0.6)
    save(fig, "fig-30-01")

# ============================================================ 31.1 Wyckoff accumulation
def fig_31_01():
    fig, ax = new_ax()
    accum = synth_walk(24, drift=0.0, vol=0.45, start=100, seed=311)
    markup = synth_walk(14, drift=0.9, vol=0.6, start=accum[-1], seed=312)
    closes = np.concatenate([accum, markup])
    o, h, l, c = to_ohlc(closes, seed=311)
    plot_candles(ax, o, h, l, c)
    box(ax, 0, 23, l[:24].min() - 0.2, h[:24].max() + 0.2, color="#DDE7EE", edge=NAVY, alpha=0.3, label="التجميع (Wyckoff)")
    arrow(ax, (23, c[23]), (37, c[-1]), color=GREEN, label="مرحلة الصعود (Markup)")
    set_ylim_pad(ax, list(l) + list(h))
    save(fig, "fig-31-01")

# ============================================================ 32.1 Triple analysis composite
def fig_32_01():
    fig, ax = new_ax()
    up = synth_walk(26, drift=0.55, vol=0.6, start=100, seed=321)
    pull = synth_walk(14, drift=-0.5, vol=0.5, start=up[-1], seed=322)
    cont = synth_walk(10, drift=0.8, vol=0.5, start=pull[-1], seed=323)
    closes = np.concatenate([up, pull, cont])
    o, h, l, c = to_ohlc(closes, seed=321)
    plot_candles(ax, o, h, l, c)
    swing_low, swing_high = l[:26].min(), h[:26].max()
    rng = swing_high - swing_low
    box(ax, 24, 40, swing_low + rng * 0.15, swing_low + rng * 0.30, color="#DDEBDD", edge=GREEN, alpha=0.3, label="SMC: خصم + OB")
    box(ax, 35, 37, min(o[36], c[36]) - 0.2, max(o[36], c[36]) + 0.2, color=GOLD_LIGHT, edge=GOLD)
    ax.text(4, h.max() + 2.0, "1: الانحياز الأساسي = صعودي", color=NAVY, fontsize=9, fontweight="bold")
    ax.text(4, h.max() + 1.2, "2: منطقة SMC = خصم + OB", color=GREEN, fontsize=9, fontweight="bold")
    ax.text(4, h.max() + 0.4, "3: المحفز الفني = ابتلاع صعودي", color=GOLD, fontsize=9, fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h) + [h.max() + 2.6])
    save(fig, "fig-32-01")

# ============================================================ 33.1 Equity curve drawdown/recovery
def fig_33_01():
    fig, ax = plt.subplots(figsize=(8.6, 4.6), dpi=150)
    fig.patch.set_facecolor("white")
    trades = np.arange(12)
    pnl = np.array([-1, -1, -1, -1, -1, 3, 0.5, -1, 0.4, -1, -1, 6]) * 1.0
    equity = 100 + np.cumsum(pnl)
    ax.plot(trades, equity, color=NAVY, linewidth=2.2, marker="o", markersize=5)
    peak = np.maximum.accumulate(equity)
    ax.fill_between(trades, equity, peak, color=RED, alpha=0.15)
    ax.set_xlabel("رقم الصفقة")
    ax.set_ylabel("رأس المال (Equity)")
    ax.grid(axis="y", color=GRID)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    ax.annotate("5 صفقات خاسرة\n(مخاطرة 1% لكل صفقة)", xy=(4, equity[4]), xytext=(1, equity[4] - 4),
                fontsize=9, color=RED, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=RED))
    ax.annotate("صفقة رابحة بعائد مخاطرة مرتفع\nتعوّض التراجع", xy=(11, equity[11]), xytext=(7.5, equity[11] + 1.5),
                fontsize=9, color=GREEN, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=GREEN))
    save(fig, "fig-33-01")


# ============================================================ 2.2 ICT / SMC relationship map
def fig_02_02():
    fig, ax = plt.subplots(figsize=(8.6, 4.6), dpi=150)
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")
    fig.patch.set_facecolor("white")
    box_ict = Rectangle((3.3, 4.3), 3.4, 1.1, facecolor=NAVY, edgecolor=NAVY)
    ax.add_patch(box_ict)
    ax.text(5, 4.85, "ICT (Inner Circle Trader)", color="white", ha="center", va="center", fontsize=11, fontweight="bold")
    ax.text(5, 3.85, "المصدر الأصلي للمصطلحات والمفاهيم", color=GREY, ha="center", fontsize=9)
    box_smc = Rectangle((3.3, 2.5), 3.4, 1.1, facecolor=GOLD, edgecolor=GOLD)
    ax.add_patch(box_smc)
    ax.text(5, 3.05, "Smart Money Concepts (SMC)", color="white", ha="center", va="center", fontsize=11, fontweight="bold")
    arrow(ax, (5, 4.3), (5, 3.6), color=NAVY)
    ax.text(5, 2.05, "تنظيم تعليمي وتبسيط لمفاهيم ICT", color=GREY, ha="center", fontsize=9)
    labels = ["BOS / CHOCH", "Order Blocks", "FVG", "السيولة", "علاوة/خصم"]
    xs = np.linspace(1.0, 9.0, len(labels))
    for x, lab in zip(xs, labels):
        ax.add_patch(Rectangle((x - 0.75, 0.3), 1.5, 0.8, facecolor="#F7F4EE", edgecolor=GOLD, linewidth=1.2))
        ax.text(x, 0.7, lab, ha="center", va="center", fontsize=8, color=NAVY, fontweight="bold")
        arrow(ax, (x, 1.1), (5, 2.5), color=GOLD_LIGHT, lw=1.2, style="-")
    save(fig, "fig-02-02")

# ============================================================ 3.2 HH/HL/LH/LL clean definitions
def fig_03_02():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.4), dpi=150)
    up = np.array([100, 102, 101.3, 104, 103.2, 106, 105.3, 108])
    o, h, l, c = to_ohlc(up, seed=302)
    plot_candles(axes[0], o, h, l, c, width=0.5)
    marker_point(axes[0], 1, h[1] + 0.2, color=NAVY, label="HH", va="bottom", dy=0.5)
    marker_point(axes[0], 2, l[2] - 0.2, color=NAVY, label="HL", va="top", dy=0.5)
    marker_point(axes[0], 3, h[3] + 0.2, color=NAVY, label="HH", va="bottom", dy=0.5)
    marker_point(axes[0], 4, l[4] - 0.2, color=NAVY, label="HL", va="top", dy=0.5)
    marker_point(axes[0], 5, h[5] + 0.2, color=NAVY, label="HH", va="bottom", dy=0.5)
    marker_point(axes[0], 6, l[6] - 0.2, color=NAVY, label="HL", va="top", dy=0.5)
    axes[0].set_title("الاتجاه الصاعد: قمم أعلى / قيعان أعلى (HH/HL)", fontsize=10, color=NAVY, fontweight="bold")

    down = np.array([108, 106, 106.8, 104, 104.7, 102, 102.6, 100])
    o2, h2, l2, c2 = to_ohlc(down, seed=303)
    plot_candles(axes[1], o2, h2, l2, c2, width=0.5)
    marker_point(axes[1], 1, l2[1] - 0.2, color=RED, label="LL", va="top", dy=0.5)
    marker_point(axes[1], 2, h2[2] + 0.2, color=RED, label="LH", va="bottom", dy=0.5)
    marker_point(axes[1], 3, l2[3] - 0.2, color=RED, label="LL", va="top", dy=0.5)
    marker_point(axes[1], 4, h2[4] + 0.2, color=RED, label="LH", va="bottom", dy=0.5)
    marker_point(axes[1], 5, l2[5] - 0.2, color=RED, label="LL", va="top", dy=0.5)
    marker_point(axes[1], 6, h2[6] + 0.2, color=RED, label="LH", va="bottom", dy=0.5)
    axes[1].set_title("الاتجاه الهابط: قمم أدنى / قيعان أدنى (LH/LL)", fontsize=10, color=NAVY, fontweight="bold")
    for ax in axes:
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        ax.set_xticks([])
    fig.tight_layout(pad=0.8)
    save(fig, "fig-03-02")

# ============================================================ 5.3 Classic supply & demand zones
def fig_05_03():
    fig, ax = new_ax()
    seg1 = synth_walk(10, drift=-0.1, vol=0.4, start=105, seed=531)
    seg2 = synth_walk(8, drift=0.9, vol=0.5, start=seg1[-1], seed=532)
    seg3 = synth_walk(10, drift=-0.5, vol=0.5, start=seg2[-1], seed=533)
    seg4 = synth_walk(8, drift=0.85, vol=0.5, start=seg3[-1], seed=534)
    closes = np.concatenate([seg1, seg2, seg3, seg4])
    o, h, l, c = to_ohlc(closes, seed=531)
    plot_candles(ax, o, h, l, c)
    box(ax, -0.5, 9.5, min(o[:10].min(), c[:10].min()) - 0.2, max(o[:10].max(), c[:10].max()) + 0.2,
        color="#DDEBDD", edge=GREEN, alpha=0.35, label="منطقة الطلب (Demand Zone)")
    box(ax, 17.5, 25.5, min(o[18:26].min(), c[18:26].min()) - 0.2, max(o[18:26].max(), c[18:26].max()) + 0.2,
        color="#F4D9D9", edge=RED, alpha=0.35, label="منطقة العرض (Supply Zone)")
    set_ylim_pad(ax, list(l) + list(h))
    save(fig, "fig-05-03")

# ============================================================ 24.2 Bar chart sample
def fig_24_02():
    fig, ax = new_ax()
    closes = synth_walk(20, drift=0.3, vol=0.6, start=100, seed=242)
    o, h, l, c = to_ohlc(closes, seed=242)
    for x, (oo, hh, ll, cc) in enumerate(zip(o, h, l, c)):
        color = GREEN if cc >= oo else RED
        ax.plot([x, x], [ll, hh], color=color, linewidth=1.6)
        ax.plot([x - 0.18, x], [oo, oo], color=color, linewidth=1.6)
        ax.plot([x, x + 0.18], [cc, cc], color=color, linewidth=1.6)
    ax.set_title("المخطط الشريطي (OHLC)", fontsize=11, color=NAVY, fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h))
    save(fig, "fig-24-02")

# ============================================================ 24.3 Line chart sample
def fig_24_03():
    fig, ax = new_ax()
    closes = synth_walk(30, drift=0.25, vol=0.6, start=100, seed=243)
    ax.plot(closes, color=NAVY, linewidth=2)
    ax.fill_between(np.arange(30), closes, closes.min() - 1, color=GOLD_LIGHT, alpha=0.15)
    ax.set_title("المخطط الخطي (أسعار الإغلاق فقط)", fontsize=11, color=NAVY, fontweight="bold")
    save(fig, "fig-24-03")

# ============================================================ 24.4 Arithmetic vs logarithmic scale
def fig_24_04():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.4), dpi=150)
    n = 40
    closes = 10 * np.exp(np.linspace(0, 2.3, n)) + np.random.default_rng(244).normal(0, 3, n)
    closes = np.clip(closes, 8, None)
    axes[0].plot(closes, color=NAVY, linewidth=2)
    axes[0].set_yscale("linear")
    axes[0].set_title("المقياس الحسابي", fontsize=10.5, color=NAVY, fontweight="bold")
    axes[0].set_ylabel("السعر")
    axes[1].plot(closes, color=GOLD, linewidth=2)
    axes[1].set_yscale("log")
    axes[1].set_title("المقياس اللوغاريتمي", fontsize=10.5, color=NAVY, fontweight="bold")
    axes[1].set_ylabel("السعر (لوغاريتمي)")
    for ax in axes:
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        ax.set_xticks([])
        ax.grid(axis="y", color=GRID)
    fig.tight_layout(pad=0.8)
    save(fig, "fig-24-04")

# ============================================================ 26.3 How to draw a trendline (steps)
def fig_26_03():
    fig, axes = plt.subplots(1, 3, figsize=(11, 4), dpi=150)
    closes = synth_walk(24, drift=0.35, vol=0.6, start=100, seed=263)
    o, h, l, c = to_ohlc(closes, seed=263)
    swing_xs = [2, 9, 16]

    for i, ax in enumerate(axes):
        plot_candles(ax, o, h, l, c, width=0.5)
        for sx in swing_xs:
            ax.plot([sx], [l[sx] - 0.3], marker="^", color=GOLD, markersize=8, zorder=6)
        if i >= 1:
            ax.plot([swing_xs[0], swing_xs[1]], [l[swing_xs[0]] - 0.3, l[swing_xs[1]] - 0.3],
                     color=NAVY, linewidth=2)
        if i == 2:
            ax.plot([swing_xs[1], 23], [l[swing_xs[1]] - 0.3, l[swing_xs[1]] - 0.3 + (23 - swing_xs[1]) *
                     ((l[swing_xs[1]] - 0.3 - (l[swing_xs[0]] - 0.3)) / (swing_xs[1] - swing_xs[0]))],
                     color=NAVY, linewidth=2, linestyle="--")
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        ax.set_xticks([])
    axes[0].set_title("1. تحديد قاعين تأرجحيين", fontsize=9.5, color=NAVY, fontweight="bold")
    axes[1].set_title("2. وصلهما بخط", fontsize=9.5, color=NAVY, fontweight="bold")
    axes[2].set_title("3. تمديده للأمام", fontsize=9.5, color=NAVY, fontweight="bold")
    fig.tight_layout(pad=0.8)
    save(fig, "fig-26-03")

# ============================================================ 26.4 Support & resistance basic definition
def fig_26_04():
    fig, ax = new_ax()
    n = 30
    x = np.arange(n)
    closes = 100 + 3 * np.sin(x / 3.2) + np.random.default_rng(264).normal(0, 0.25, n)
    o, h, l, c = to_ohlc(closes, seed=264)
    plot_candles(ax, o, h, l, c, width=0.55)
    hline(ax, closes.max() - 0.3, 0, n - 1, color=RED, label="مقاومة")
    hline(ax, closes.min() + 0.3, 0, n - 1, color=GREEN, label="دعم")
    set_ylim_pad(ax, list(l) + list(h))
    save(fig, "fig-26-04")

# ============================================================ 26.5 Retest concept
def fig_26_05():
    fig, ax = new_ax()
    pre = synth_walk(12, drift=0.1, vol=0.4, start=100, seed=265)
    level = pre.max() + 0.4
    brk = synth_walk(4, drift=0.9, vol=0.3, start=pre[-1], seed=266)
    back = synth_walk(4, drift=-0.5, vol=0.25, start=brk[-1], seed=267)
    cont = synth_walk(10, drift=0.7, vol=0.5, start=back[-1], seed=268)
    closes = np.concatenate([pre, brk, back, cont])
    o, h, l, c = to_ohlc(closes, seed=265)
    plot_candles(ax, o, h, l, c)
    hline(ax, level, 0, len(closes) - 1, color=GOLD, label="مستوى مكسور")
    arrow(ax, (15, c[15]), (19, level + 0.1), color=NAVY, ls="dashed", label="إعادة اختبار")
    arrow(ax, (19, level), (29, c[-1]), color=GREEN, label="استمرار")
    set_ylim_pad(ax, list(l) + list(h))
    save(fig, "fig-26-05")

# ============================================================ 26.6 Breakout vs false breakout
def fig_26_06():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.3), dpi=150)
    pre = synth_walk(12, drift=0.05, vol=0.35, start=100, seed=269)
    level = pre.max() + 0.3

    real = synth_walk(10, drift=0.9, vol=0.4, start=pre[-1], seed=270)
    closes1 = np.concatenate([pre, real])
    o1, h1, l1, c1 = to_ohlc(closes1, seed=269)
    plot_candles(axes[0], o1, h1, l1, c1, width=0.55)
    axes[0].axhline(level, color=GOLD, linestyle="--", linewidth=1.4)
    axes[0].set_title("اختراق حقيقي", fontsize=10.5, color=GREEN, fontweight="bold")

    fake_up = synth_walk(3, drift=1.0, vol=0.3, start=pre[-1], seed=271)
    fake_down = synth_walk(9, drift=-0.6, vol=0.4, start=fake_up[-1], seed=272)
    closes2 = np.concatenate([pre, fake_up, fake_down])
    o2, h2, l2, c2 = to_ohlc(closes2, seed=269)
    plot_candles(axes[1], o2, h2, l2, c2, width=0.55)
    axes[1].axhline(level, color=GOLD, linestyle="--", linewidth=1.4)
    axes[1].set_title("اختراق كاذب", fontsize=10.5, color=RED, fontweight="bold")
    for ax in axes:
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        ax.set_xticks([])
    fig.tight_layout(pad=0.8)
    save(fig, "fig-26-06")

# ============================================================ 28.3 Cup and Handle
def fig_28_03():
    fig, ax = plt.subplots(figsize=(8.6, 4.4), dpi=150)
    fig.patch.set_facecolor("white")
    x1 = np.linspace(0, 6, 60)
    cup = 3 - 2.6 * np.exp(-((x1 - 3) ** 2) / 4)
    x2 = np.linspace(6, 7.5, 15)
    handle = cup[-1] - 0.5 * np.sin((x2 - 6) * 2.2) - (x2 - 6) * 0.15
    x3 = np.linspace(7.5, 9, 15)
    breakout = handle[-1] + (x3 - 7.5) * 1.1
    ax.plot(x1, cup, color=NAVY, linewidth=2.2)
    ax.plot(x2, handle, color=GOLD, linewidth=2.2)
    ax.plot(x3, breakout, color=GREEN, linewidth=2.2)
    ax.axhline(3.0, color=GREY, linestyle=":", linewidth=1.2)
    ax.text(3, 3.15, "الحافة (مقاومة)", color=GREY, fontsize=9, ha="center")
    ax.text(3, 0.2, "الكوب (Cup)", color=NAVY, fontsize=10, ha="center", fontweight="bold")
    ax.text(6.7, cup[-1] - 0.9, "المقبض (Handle)", color=GOLD, fontsize=10, ha="center", fontweight="bold")
    ax.set_title("الكوب والمقبض (Cup and Handle)", fontsize=11, color=NAVY, fontweight="bold")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
    save(fig, "fig-28-03")

# ============================================================ 28.4 Double Bottom
def fig_28_04():
    fig, ax = plt.subplots(figsize=(8.6, 4.4), dpi=150)
    fig.patch.set_facecolor("white")
    x = np.linspace(0, 10, 100)
    y = 2.2 - 1.8 * np.exp(-((x - 2.5) ** 2) / 0.5) - 1.8 * np.exp(-((x - 7) ** 2) / 0.5)
    ax.plot(x, y, color=NAVY, linewidth=2.2)
    ax.axhline(1.9, color=GOLD, linestyle="--", linewidth=1.4)
    ax.text(4.75, 2.0, "خط العنق (مقاومة)", color=GOLD, fontsize=9, ha="center")
    ax.text(2.5, 0.15, "القاع 1", color=RED, fontsize=9.5, ha="center", fontweight="bold")
    ax.text(7, 0.15, "القاع 2", color=RED, fontsize=9.5, ha="center", fontweight="bold")
    ax.set_title("القاع المزدوج (Double Bottom)", fontsize=11, color=NAVY, fontweight="bold")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
    save(fig, "fig-28-04")

# ============================================================ 29.4 Fibonacci retracement (generic)
def fig_29_04():
    fig, ax = new_ax()
    up = synth_walk(20, drift=0.7, vol=0.5, start=100, seed=294)
    pull = synth_walk(16, drift=-0.35, vol=0.4, start=up[-1], seed=295)
    closes = np.concatenate([up, pull])
    o, h, l, c = to_ohlc(closes, seed=294)
    plot_candles(ax, o, h, l, c)
    swing_low, swing_high = l[:20].min(), h[:20].max()
    rng = swing_high - swing_low
    levels = {"0%": 1.0, "23.6%": 0.764, "38.2%": 0.618, "50%": 0.5, "61.8%": 0.382, "78.6%": 0.214, "100%": 0.0}
    for label, frac in levels.items():
        y = swing_low + rng * frac
        hline(ax, y, 0, 35, color=GREY, ls=":", lw=1.0, label=label, label_side="right")
    set_ylim_pad(ax, list(l) + list(h))
    save(fig, "fig-29-04")

# ============================================================ 29.5 Elliott Wave (5-3)
def fig_29_05():
    fig, ax = plt.subplots(figsize=(8.6, 4.6), dpi=150)
    fig.patch.set_facecolor("white")
    pts_x = [0, 1, 1.6, 2.6, 3.2, 4.4, 5, 6.2, 6.8, 8]
    pts_y = [0, 2.2, 1.4, 3.6, 2.6, 5.0, 3.8, 4.6, 3.0, 1.6]
    ax.plot(pts_x, pts_y, color=NAVY, linewidth=2.2, marker="o", markersize=4)
    wave_labels = ["1", "2", "3", "4", "5", "A", "B", "C"]
    for i, lab in enumerate(wave_labels):
        ax.text(pts_x[i + 1], pts_y[i + 1] + 0.25, lab, fontsize=10, color=GOLD, fontweight="bold", ha="center")
    ax.axvspan(0, 5, color=GREEN, alpha=0.05)
    ax.axvspan(5, 8, color=RED, alpha=0.05)
    ax.text(2.5, -0.6, "الموجات الدافعة (1-5)", color=GREEN, fontsize=9.5, ha="center", fontweight="bold")
    ax.text(6.5, -0.6, "الموجات التصحيحية (A-B-C)", color=RED, fontsize=9.5, ha="center", fontweight="bold")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
    save(fig, "fig-29-05")

# ============================================================ 30.2 Open Interest
def fig_30_02():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.6, 5.6), dpi=150, gridspec_kw={"height_ratios": [1.6, 1]})
    n = 30
    closes = synth_walk(n, drift=0.4, vol=0.5, start=100, seed=302)
    o, h, l, c = to_ohlc(closes, seed=302)
    plot_candles(ax1, o, h, l, c, width=0.55)
    for s in ["top", "right"]: ax1.spines[s].set_visible(False)
    ax1.set_xticks([]); ax1.grid(axis="y", color=GRID)
    oi = 1000 + np.cumsum(np.random.default_rng(303).normal(35, 15, n))
    ax2.plot(oi, color=GOLD, linewidth=2)
    ax2.fill_between(np.arange(n), oi.min() - 50, oi, color=GOLD_LIGHT, alpha=0.2)
    ax2.set_ylabel("الفائدة المفتوحة (Open Interest)")
    ax2.set_xlabel("الزمن")
    for s in ["top", "right"]: ax2.spines[s].set_visible(False)
    fig.tight_layout(pad=0.6)
    save(fig, "fig-30-02")


# ============================================================ 3.3 Swing High (dedicated single concept)
def fig_03_03():
    fig, ax = new_ax(w=7.2, h=4.0)
    closes = np.array([100, 101.2, 102.6, 104.3, 103.0, 101.5, 100.4])
    o, h, l, c = to_ohlc(closes, seed=333, wick=0.5)
    plot_candles(ax, o, h, l, c, width=0.5)
    marker_point(ax, 3, h[3] + 0.15, color=NAVY, label="قمة تأرجحية (Swing High)", va="bottom", dy=0.6)
    set_ylim_pad(ax, list(l) + list(h), pad_frac=0.3)
    save(fig, "fig-03-03")

# ============================================================ 3.4 Swing Low (dedicated single concept)
def fig_03_04():
    fig, ax = new_ax(w=7.2, h=4.0)
    closes = np.array([104, 102.8, 101.4, 99.7, 101.0, 102.5, 103.6])
    o, h, l, c = to_ohlc(closes, seed=334, wick=0.5)
    plot_candles(ax, o, h, l, c, width=0.5)
    marker_point(ax, 3, l[3] - 0.15, color=NAVY, label="قاع تأرجحي (Swing Low)", va="top", dy=0.6)
    set_ylim_pad(ax, list(l) + list(h), pad_frac=0.3)
    save(fig, "fig-03-04")

# ============================================================ 3.5 HH (dedicated single concept)
def fig_03_05():
    fig, ax = new_ax(w=7.2, h=4.0)
    closes = np.array([100, 102.6, 101.4, 105.2])
    o, h, l, c = to_ohlc(closes, seed=335, wick=0.5)
    plot_candles(ax, o, h, l, c, width=0.5)
    ax.plot([1, 3], [h[1], h[3]], color=GREY, linestyle=":", linewidth=1.3)
    marker_point(ax, 1, h[1] + 0.15, color=GREY, label=None, va="bottom", dy=0.6)
    marker_point(ax, 3, h[3] + 0.15, color=NAVY, label="قمة أعلى (HH)", va="bottom", dy=0.6)
    set_ylim_pad(ax, list(l) + list(h), pad_frac=0.3)
    save(fig, "fig-03-05")

# ============================================================ 3.6 HL (dedicated single concept)
def fig_03_06():
    fig, ax = new_ax(w=7.2, h=4.0)
    closes = np.array([104, 100.8, 103.2, 102.0, 105.5])
    o, h, l, c = to_ohlc(closes, seed=336, wick=0.5)
    plot_candles(ax, o, h, l, c, width=0.5)
    ax.plot([1, 3], [l[1], l[3]], color=GREY, linestyle=":", linewidth=1.3)
    marker_point(ax, 1, l[1] - 0.15, color=GREY, label=None, va="top", dy=0.6)
    marker_point(ax, 3, l[3] - 0.15, color=NAVY, label="قاع أعلى (HL)", va="top", dy=0.6)
    set_ylim_pad(ax, list(l) + list(h), pad_frac=0.3)
    save(fig, "fig-03-06")

# ============================================================ 3.7 LH (dedicated single concept)
def fig_03_07():
    fig, ax = new_ax(w=7.2, h=4.0)
    closes = np.array([100, 105.2, 101.4, 102.6])
    o, h, l, c = to_ohlc(closes, seed=337, wick=0.5)
    plot_candles(ax, o, h, l, c, width=0.5)
    ax.plot([1, 3], [h[1], h[3]], color=GREY, linestyle=":", linewidth=1.3)
    marker_point(ax, 1, h[1] + 0.15, color=GREY, label=None, va="bottom", dy=0.6)
    marker_point(ax, 3, h[3] + 0.15, color=RED, label="قمة أدنى (LH)", va="bottom", dy=0.6)
    set_ylim_pad(ax, list(l) + list(h), pad_frac=0.3)
    save(fig, "fig-03-07")

# ============================================================ 3.8 LL (dedicated single concept)
def fig_03_08():
    fig, ax = new_ax(w=7.2, h=4.0)
    closes = np.array([105.5, 102.0, 103.2, 100.8, 104])
    o, h, l, c = to_ohlc(closes, seed=338, wick=0.5)
    plot_candles(ax, o, h, l, c, width=0.5)
    ax.plot([1, 3], [l[1], l[3]], color=GREY, linestyle=":", linewidth=1.3)
    marker_point(ax, 1, l[1] - 0.15, color=GREY, label=None, va="top", dy=0.6)
    marker_point(ax, 3, l[3] - 0.15, color=RED, label="قاع أدنى (LL)", va="top", dy=0.6)
    set_ylim_pad(ax, list(l) + list(h), pad_frac=0.3)
    save(fig, "fig-03-08")

# ============================================================ 27.2a Uptrend (dedicated single concept)
def fig_27_02():
    fig, ax = new_ax(w=7.4, h=4.0)
    closes = synth_walk(24, drift=0.55, vol=0.5, start=100, seed=2702)
    o, h, l, c = to_ohlc(closes, seed=2702)
    plot_candles(ax, o, h, l, c, width=0.55)
    lo_xs = [2, 10, 18]
    ax.plot(lo_xs, [l[x] - 0.2 for x in lo_xs], color=GREEN, linewidth=2)
    ax.text(12, ax.get_ylim()[0], "اتجاه صاعد (Uptrend)", color=GREEN, fontsize=10.5,
            ha="center", va="bottom", fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h))
    save(fig, "fig-27-02")

# ============================================================ 27.2b Downtrend (dedicated single concept)
def fig_27_03():
    fig, ax = new_ax(w=7.4, h=4.0)
    closes = synth_walk(24, drift=-0.55, vol=0.5, start=100, seed=2703)
    o, h, l, c = to_ohlc(closes, seed=2703)
    plot_candles(ax, o, h, l, c, width=0.55)
    hi_xs = [2, 10, 18]
    ax.plot(hi_xs, [h[x] + 0.2 for x in hi_xs], color=RED, linewidth=2)
    ax.text(12, ax.get_ylim()[1], "اتجاه هابط (Downtrend)", color=RED, fontsize=10.5,
            ha="center", va="top", fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h))
    save(fig, "fig-27-03")

# ============================================================ 27.2c Sideways trend (dedicated single concept)
def fig_27_04():
    fig, ax = new_ax(w=7.4, h=4.0)
    n = 24
    closes = 100 + 1.6 * np.sin(np.arange(n) / 2.6) + np.random.default_rng(2704).normal(0, 0.25, n)
    o, h, l, c = to_ohlc(closes, seed=2704)
    plot_candles(ax, o, h, l, c, width=0.55)
    hline(ax, closes.max() + 0.2, 0, n - 1, color=GOLD, ls="--")
    hline(ax, closes.min() - 0.2, 0, n - 1, color=GOLD, ls="--")
    ax.text(n / 2, closes.max() + 1.1, "اتجاه عرضي (Sideways / Range)", color=GOLD, fontsize=10.5,
            ha="center", va="bottom", fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h) + [closes.max() + 1.4])
    save(fig, "fig-27-04")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("fig_")]
    for fn in fns:
        fn()
        print("generated", fn.__name__)
    print(f"\nTotal figures: {len(fns)}")
