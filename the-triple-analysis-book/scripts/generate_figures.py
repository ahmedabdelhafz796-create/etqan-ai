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
    marker_point, set_ylim_pad, rolling_mean, regime_walk, letter_point,
    zigzag, channel,
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

# ============================================================ 4.3a Buy-side liquidity (dedicated)
def fig_04_02():
    fig, ax = new_ax(w=8.6, h=4.6)
    closes = regime_walk([(14, 0.5, 0.4), (4, 0.05, 0.15), (12, -0.6, 0.5)], start=100, seed=402)
    o, h, l, c = to_ohlc(closes, seed=402)
    plot_candles(ax, o, h, l, c, width=0.55)
    level = h[12:18].max() + 0.1
    hline(ax, level, 0, len(closes) - 1, color=RED, lw=2.0)
    box(ax, 0, len(closes) - 1, level, level + 1.3, color="#F4A6A6", alpha=0.3, edge=None)
    ax.text(len(closes) / 2, level + 0.65, "سيولة شراء (Buy-side Liquidity): أوامر وقف بيع + شراء معلّقة",
            color=RED, fontsize=9.5, ha="center", va="center", fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h) + [level + 1.6], pad_frac=0.12)
    save(fig, "fig-04-02")

# ============================================================ 4.3b Sell-side liquidity (dedicated)
def fig_04_03():
    fig, ax = new_ax(w=8.6, h=4.6)
    closes = regime_walk([(14, -0.5, 0.4), (4, -0.05, 0.15), (12, 0.6, 0.5)], start=100, seed=403)
    o, h, l, c = to_ohlc(closes, seed=403)
    plot_candles(ax, o, h, l, c, width=0.55)
    level = l[12:18].min() - 0.1
    hline(ax, level, 0, len(closes) - 1, color=GREEN, lw=2.0)
    box(ax, 0, len(closes) - 1, level - 1.3, level, color="#DDEBDD", alpha=0.4, edge=None)
    ax.text(len(closes) / 2, level - 0.65, "سيولة بيع (Sell-side Liquidity): أوامر وقف شراء + بيع معلّقة",
            color=GREEN, fontsize=9.5, ha="center", va="center", fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h) + [level - 1.6], pad_frac=0.12)
    save(fig, "fig-04-03")

# ============================================================ 4.6-4.8 Trend liquidity (dedicated)
def fig_04_04():
    fig, ax = new_ax(w=8.6, h=4.6)
    closes = regime_walk([(8, 0.55, 0.35), (3, -0.15, 0.2), (8, 0.5, 0.35), (3, -0.15, 0.2),
                           (8, 0.5, 0.35), (3, -0.15, 0.2), (8, 0.55, 0.35)], start=100, seed=404)
    o, h, l, c = to_ohlc(closes, seed=404)
    plot_candles(ax, o, h, l, c, width=0.55)
    for x in [10, 21, 32]:
        marker_point(ax, x, l[x] - 0.15, color=GOLD, label="سيولة اتجاه", va="top", dy=0.6, fontsize=8.5)
    ax.text(len(closes) / 2, h.max() + 0.6, "سيولة الاتجاه: تتجمع تدريجيًا عند كل تصحيح بسيط", color=GOLD,
            fontsize=9.5, ha="center", fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h) + [h.max() + 1.0], pad_frac=0.12)
    save(fig, "fig-04-04")

# ============================================================ 4.4-4.5 Equal highs/lows liquidity (dedicated)
def fig_04_05():
    fig, ax = new_ax(w=8.6, h=4.6)
    closes = regime_walk([(10, 0.1, 0.3), (6, 0.5, 0.3), (10, -0.15, 0.3), (6, 0.5, 0.3),
                           (10, -0.15, 0.25)], start=100, seed=405)
    o, h, l, c = to_ohlc(closes, seed=405)
    plot_candles(ax, o, h, l, c, width=0.55)
    level = max(h[9], h[25]) + 0.1
    hline(ax, level, 0, len(closes) - 1, color=GOLD, lw=2.0, label="قمم متساوية (Equal Highs)")
    letter_point(ax, 9, h[9] + 0.3, "A", color=NAVY, va="bottom", dy=0.3, fontsize=10.5)
    letter_point(ax, 25, h[25] + 0.3, "B", color=NAVY, va="bottom", dy=0.3, fontsize=10.5)
    ax.text(len(closes) / 2, l.min() - 0.2, "بركة سيولة كثيفة عند كل تكرار للمستوى نفسه تقريبًا",
            color=GOLD, fontsize=9, ha="center", fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h) + [level + 1.0, l.min() - 0.9], pad_frac=0.08)
    save(fig, "fig-04-05")

# ============================================================ 4.9 Geometric liquidity (dedicated)
def fig_04_06():
    n = 40
    def shape(i):
        return 3.2 * np.exp(-((i - 12) ** 2) / 20) + 3.3 * np.exp(-((i - 28) ** 2) / 20)
    fig, ax, o, h, l, c = _pattern_candles(shape, n=n, seed=406, base=100, figsize=(8.6, 4.6))
    level = max(h[12], h[28]) + 0.1
    hline(ax, level, 0, n - 1, color=RED, lw=2.0, label="قمة مزدوجة ظاهريًا")
    box(ax, 8, 32, level, level + 0.9, color="#F4A6A6", alpha=0.3, edge=None)
    ax.text(n / 2, level + 0.45, "تُقرأ أولًا كمصيدة سيولة قبل قراءتها كنموذج انعكاس تقليدي",
            color=RED, fontsize=9, ha="center", fontweight="bold")
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])
    set_ylim_pad(ax, list(l) + list(h) + [level + 1.2], pad_frac=0.1)
    ax.set_title("السيولة الهندسية (Geometric Liquidity)", fontsize=11, color=NAVY, fontweight="bold")
    save(fig, "fig-04-06")

# ============================================================ 4.10 Liquidity sweep definition (dedicated)
def fig_04_07():
    fig, ax = new_ax(w=8.6, h=4.6)
    pre = synth_walk(16, drift=0.05, vol=0.3, start=100, seed=4071)
    level = pre.max() + 0.3
    sweep = synth_walk(2, drift=1.4, vol=0.2, start=pre[-1], seed=4072)
    rev = synth_walk(16, drift=-0.7, vol=0.5, start=sweep[-1], seed=4073)
    closes = np.concatenate([pre, sweep, rev])
    o, h, l, c = to_ohlc(closes, seed=4071, wick=0.9)
    plot_candles(ax, o, h, l, c, width=0.55)
    hline(ax, level, 0, len(closes) - 1, color=GREY, lw=1.8, ls=":")
    arrow(ax, (17, h[17]), (17, level + 1.4), color=RED, label="فتيل يخترق المستوى")
    arrow(ax, (18, h[18] + 0.2), (30, c[-1]), color=NAVY, ls="dashed", label="ارتداد سريع معاكس")
    ax.set_title("سحب السيولة (Liquidity Sweep)", fontsize=11, color=NAVY, fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h) + [level + 1.8])
    save(fig, "fig-04-07")

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

# ============================================================ 5.6 Mitigation block (dedicated)
def fig_05_04():
    fig, ax = new_ax(w=8.6, h=4.6)
    up = synth_walk(12, drift=0.6, vol=0.5, start=100, seed=5041)
    ob_seg = synth_walk(4, drift=-0.15, vol=0.3, start=up[-1], seed=5042)
    cont = synth_walk(10, drift=0.7, vol=0.5, start=ob_seg[-1], seed=5043)
    pull = synth_walk(8, drift=-0.4, vol=0.4, start=cont[-1], seed=5044)
    resume = synth_walk(10, drift=0.75, vol=0.5, start=pull[-1], seed=5045)
    closes = np.concatenate([up, ob_seg, cont, pull, resume])
    o, h, l, c = to_ohlc(closes, seed=5041)
    plot_candles(ax, o, h, l, c, width=0.55)
    ob_x = 13
    y0, y1 = min(o[ob_x], c[ob_x]) - 0.15, max(o[ob_x], c[ob_x]) + 0.15
    box(ax, ob_x - 0.6, ob_x + 0.6, y0, y1, color=GOLD_LIGHT, edge=GOLD)
    arrow(ax, (27, c[27]), (33, (y0 + y1) / 2), color=NAVY, ls="dashed", label="عودة لتخفيف أوامر سابقة")
    arrow(ax, (33, (y0 + y1) / 2), (44, c[-1]), color=GREEN, label="استئناف نفس الاتجاه")
    ax.text(ob_x, y1 + 0.8, "بلوك التخفيف (Mitigation Block)", color=GOLD, fontsize=9.5, ha="center", fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h) + [y1 + 1.2])
    save(fig, "fig-05-04")

# ============================================================ 5.7 Rejection block (dedicated)
def fig_05_05():
    fig, ax = new_ax(w=8.6, h=4.6)
    pre = synth_walk(14, drift=0.1, vol=0.3, start=100, seed=505)
    o, h, l, c = to_ohlc(pre, seed=505, wick=0.4)
    level = h[6:10].max() + 0.2
    for x in [6, 8, 10]:
        h[x] = level - np.random.default_rng(505 + x).uniform(0, 0.05)
    plot_candles(ax, o, h, l, c, width=0.55)
    hline(ax, level, 0, len(pre) - 1, color=RED, lw=2.0)
    for x in [6, 8, 10]:
        letter_point(ax, x, h[x] + 0.15, "رفض", color=RED, va="bottom", dy=0.4, circle=False, fontsize=8)
    ax.text(len(pre) / 2, level + 1.0, "بلوك الرفض: فتائل متكررة تدافع عن نفس المستوى", color=RED, fontsize=9.5,
            ha="center", fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h) + [level + 1.4])
    save(fig, "fig-05-05")

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

# ============================================================ 6.2a Bullish FVG 3-candle definition (dedicated)
def fig_06_02():
    fig, ax = new_ax(w=7.4, h=4.2)
    closes = np.array([100, 100.4, 103.8, 104.6])
    o, h, l, c = to_ohlc(closes, seed=602, wick=0.35)
    plot_candles(ax, o, h, l, c, width=0.5)
    box(ax, 0.55, 1.45, h[0], l[2], color="#F2D98A", edge="#B7791F")
    ax.text(1, (h[0] + l[2]) / 2, "FVG", color="#B7791F", fontsize=9.5, ha="center", va="center", fontweight="bold")
    for x, lab in zip([0, 1, 2], ["الشمعة 1", "الشمعة 2", "الشمعة 3"]):
        ax.text(x, l[x] - 0.35, lab, color=NAVY, fontsize=9, ha="center", fontweight="bold")
    ax.text(1, h.max() + 0.4, "لا تداخل بين قمة (1) وقاع (3)", color="#B7791F", fontsize=8.5, ha="center", fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h), pad_frac=0.3)
    ax.set_title("تعريف FVG صاعدة عبر ثلاث شموع متتالية", fontsize=10.5, color=NAVY, fontweight="bold")
    save(fig, "fig-06-02")

# ============================================================ 6.2b Bearish FVG 3-candle definition (dedicated)
def fig_06_03():
    fig, ax = new_ax(w=7.4, h=4.2)
    closes = np.array([105, 104.6, 101.2, 100.4])
    o, h, l, c = to_ohlc(closes, seed=603, wick=0.35)
    plot_candles(ax, o, h, l, c, width=0.5)
    box(ax, 0.55, 1.45, l[0], h[2], color="#F4A6A6", edge=RED)
    ax.text(1, (l[0] + h[2]) / 2, "FVG", color=RED, fontsize=9.5, ha="center", va="center", fontweight="bold")
    for x, lab in zip([0, 1, 2], ["الشمعة 1", "الشمعة 2", "الشمعة 3"]):
        ax.text(x, h[x] + 0.35, lab, color=NAVY, fontsize=9, ha="center", fontweight="bold")
    ax.text(1, l.min() - 0.4, "لا تداخل بين قاع (1) وقمة (3)", color=RED, fontsize=8.5, ha="center", fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h), pad_frac=0.3)
    ax.set_title("تعريف FVG هبوطية عبر ثلاث شموع متتالية", fontsize=10.5, color=NAVY, fontweight="bold")
    save(fig, "fig-06-03")

# ============================================================ 6.3 Compound imbalance (dedicated)
def fig_06_04():
    fig, ax = new_ax(w=8.6, h=4.6)
    pre = synth_walk(10, drift=0.1, vol=0.3, start=100, seed=6041)
    imp = synth_walk(7, drift=1.9, vol=0.25, start=pre[-1], seed=6042)
    post = synth_walk(10, drift=0.3, vol=0.5, start=imp[-1], seed=6043)
    closes = np.concatenate([pre, imp, post])
    o, h, l, c = to_ohlc(closes, seed=6041, wick=0.35)
    plot_candles(ax, o, h, l, c, width=0.55)
    for k in range(3):
        x1, x3 = 10 + k * 2, 12 + k * 2
        lo, hi = h[x1], l[x3]
        if hi < lo: lo, hi = hi, lo
        box(ax, x1 + 0.3, x3 - 0.3, lo, hi, color="#F2D98A", edge="#B7791F")
    ax.text(13, h.max() + 0.5, "اختلال مركّب: عدة فجوات متتالية تُعامل ككتلة اهتمام واحدة", color="#B7791F",
            fontsize=9, ha="center", fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h) + [h.max() + 0.9])
    save(fig, "fig-06-04")

# ============================================================ 6.5 Partial fill of FVG (dedicated)
def fig_06_05():
    fig, ax = new_ax(w=8.6, h=4.6)
    pre = synth_walk(10, drift=0.1, vol=0.3, start=100, seed=6051)
    imp = synth_walk(3, drift=2.0, vol=0.25, start=pre[-1], seed=6052)
    hold = synth_walk(12, drift=0.2, vol=0.4, start=imp[-1], seed=6053)
    fill = synth_walk(6, drift=-0.5, vol=0.3, start=hold[-1], seed=6054)
    cont = synth_walk(10, drift=0.7, vol=0.5, start=fill[-1], seed=6055)
    closes = np.concatenate([pre, imp, hold, fill, cont])
    o, h, l, c = to_ohlc(closes, seed=6051, wick=0.4)
    plot_candles(ax, o, h, l, c, width=0.55)
    x1, x3 = 10, 12
    lo, hi = h[x1], l[x3]
    if hi < lo: lo, hi = hi, lo
    box(ax, x1 + 0.3, x3 - 0.3, lo, hi, color="#F2D98A", edge="#B7791F", label="FVG")
    mid = (lo + hi) / 2
    hline(ax, mid, x3, 41, color=GREY, ls=":", lw=1.2)
    arrow(ax, (26, hold[-1]), (31, mid), color=NAVY, ls="dashed", label="ملء جزئي فقط (لمس الحافة القريبة)")
    set_ylim_pad(ax, list(l) + list(h))
    save(fig, "fig-06-05")

# ============================================================ 6.6-6.7 FVG entry steps (dedicated)
def fig_06_06():
    fig, axes = plt.subplots(1, 4, figsize=(12, 3.6), dpi=150)
    titles = ["1. تحديد الانحياز العام", "2. تحديد FVG حديثة", "3. انتظار لمس الحافة", "4. دخول + وقف خلف الحافة البعيدة"]
    for i, (ax, title) in enumerate(zip(axes, titles)):
        closes = synth_walk(16, drift=0.5, vol=0.4, start=100, seed=606 + i)
        o, h, l, c = to_ohlc(closes, seed=606 + i, wick=0.4)
        plot_candles(ax, o, h, l, c, width=0.5)
        if i >= 1:
            box(ax, 7.3, 8.7, h[7], l[9] if l[9] > h[7] else h[7] + 0.6, color="#F2D98A", edge="#B7791F")
        if i == 3:
            ax.axhline(h[7] - 0.3, color=RED, linestyle=":", linewidth=1.3)
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(title, fontsize=9, color=NAVY, fontweight="bold")
    fig.tight_layout(pad=0.8)
    save(fig, "fig-06-06")

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

# ============================================================ 7.2 Valid inducement sequence (dedicated)
def fig_07_02():
    fig, ax = new_ax(w=8.6, h=4.6)
    pre = synth_walk(10, drift=-0.5, vol=0.4, start=108, seed=702)
    ob_seg = synth_walk(4, drift=-0.1, vol=0.25, start=pre[-1], seed=7021)
    ind_up = synth_walk(6, drift=0.5, vol=0.3, start=ob_seg[-1], seed=7022)
    sweep = synth_walk(3, drift=-0.7, vol=0.25, start=ind_up[-1], seed=7023)
    cont = synth_walk(14, drift=0.8, vol=0.5, start=sweep[-1], seed=7024)
    closes = np.concatenate([pre, ob_seg, ind_up, sweep, cont])
    o, h, l, c = to_ohlc(closes, seed=702, wick=0.4)
    plot_candles(ax, o, h, l, c, width=0.55)
    ob_x = 12
    box(ax, ob_x - 1, ob_x + 1, min(o[ob_x], c[ob_x]) - 0.15, max(o[ob_x], c[ob_x]) + 0.15,
        color=GOLD_LIGHT, edge=GOLD, label="1: كتلة طلب (فريم أكبر)")
    ind_x = 19
    letter_point(ax, ind_x, h[ind_x] + 0.2, "2: حافز", color=RED, va="bottom", dy=0.6, circle=False, fontsize=9)
    arrow(ax, (ind_x, l[22] - 0.2), (ind_x + 2, l[22] - 1.0), color=RED, ls="dashed", label="3: سحب سيولة الحافز")
    arrow(ax, (ind_x + 2, l[22] - 0.8), (36, c[-1]), color=NAVY, label="4: استكمال نحو كتلة الطلب")
    set_ylim_pad(ax, list(l) + list(h) + [l[22] - 1.6])
    ax.set_title("تسلسل الحافز الصالح: كتلة طلب ← حافز ← سحب سيولة ← استكمال", fontsize=10.5, color=NAVY, fontweight="bold")
    save(fig, "fig-07-02")

# ============================================================ 7.3 Internal trap (dedicated, two-panel)
def fig_07_03():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.4), dpi=150)
    htf_closes = regime_walk([(14, 0.6, 0.4), (10, -0.15, 0.3), (14, 0.7, 0.45)], start=100, seed=703)
    o1, h1, l1, c1 = to_ohlc(htf_closes, seed=703, wick=0.4)
    plot_candles(axes[0], o1, h1, l1, c1, width=0.55)
    box(axes[0], 13, 24, l1[14:24].min() - 0.2, h1[14:24].max() + 0.2, color="#DDE7EE", edge=NAVY, alpha=0.3)
    axes[0].set_title("الإطار الأعلى: نطاق تصحيحي عام", fontsize=10, color=NAVY, fontweight="bold")

    ltf = synth_walk(30, drift=-0.05, vol=0.35, start=100, seed=7031)
    trap_x = 18
    ltf[trap_x:trap_x + 3] -= 1.2
    o2, h2, l2, c2 = to_ohlc(ltf, seed=7031, wick=0.4)
    plot_candles(axes[1], o2, h2, l2, c2, width=0.55)
    marker_point(axes[1], trap_x + 1, l2[trap_x + 1] - 0.15, color=RED, label="فخ داخلي", va="top", dy=0.6, fontsize=9)
    axes[1].set_title("الإطار الأصغر: الفخ الداخلي يظهر هنا فقط", fontsize=10, color=NAVY, fontweight="bold")
    for ax in axes:
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        ax.set_xticks([])
    fig.tight_layout(pad=0.8)
    save(fig, "fig-07-03")

# ============================================================ 7.6 Avoiding traps: naive vs contextual entry (dedicated)
def fig_07_04():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.4), dpi=150)
    pre = synth_walk(14, drift=-0.5, vol=0.4, start=108, seed=704)
    dip = synth_walk(4, drift=-0.6, vol=0.3, start=pre[-1], seed=7041)
    rev = synth_walk(14, drift=0.75, vol=0.5, start=dip[-1], seed=7042)
    closes = np.concatenate([pre, dip, rev])
    o, h, l, c = to_ohlc(closes, seed=704, wick=0.4)

    plot_candles(axes[0], o, h, l, c, width=0.55)
    marker_point(axes[0], 15, h[15] + 0.2, color=RED, label="بيع فوري عند الكسر", va="bottom", dy=0.6, fontsize=8.5)
    arrow(axes[0], (16, c[16]), (26, c[26] + 1.5), color=RED, ls="dashed", label="خسارة")
    axes[0].set_title("الدخول الساذج: بيع عند أول كسر صغير", fontsize=10, color=RED, fontweight="bold")

    plot_candles(axes[1], o, h, l, c, width=0.55)
    marker_point(axes[1], 17, l[17] - 0.2, color=GREEN, label="شراء بعد فهم السياق", va="top", dy=0.6, fontsize=8.5)
    arrow(axes[1], (18, c[18]), (31, c[-1]), color=GREEN, label="ربح")
    axes[1].set_title("الدخول الواعي بالسياق: انتظار التأكيد", fontsize=10, color=GREEN, fontweight="bold")
    for ax in axes:
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        ax.set_xticks([])
    fig.tight_layout(pad=0.8)
    save(fig, "fig-07-04")

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

# ============================================================ 8.1 Discount vs Premium halves (dedicated)
def fig_08_02():
    fig, ax = new_ax(w=8.6, h=4.6)
    closes = regime_walk([(16, 0.6, 0.5), (14, -0.5, 0.45)], start=100, seed=802)
    o, h, l, c = to_ohlc(closes, seed=802)
    plot_candles(ax, o, h, l, c, width=0.55)
    swing_low, swing_high = l.min(), h.max()
    mid = (swing_low + swing_high) / 2
    box(ax, 0, len(closes) - 1, swing_low, mid, color="#DDEBDD", edge=GREEN, alpha=0.3)
    box(ax, 0, len(closes) - 1, mid, swing_high, color="#F4A6A6", alpha=0.25, edge=RED)
    ax.text(len(closes) / 2, (swing_low + mid) / 2, "منطقة الخصم (Discount) — تُفضَّل للشراء", color=GREEN,
            fontsize=9.5, ha="center", va="center", fontweight="bold")
    ax.text(len(closes) / 2, (mid + swing_high) / 2, "منطقة العلاوة (Premium) — تُفضَّل للبيع", color=RED,
            fontsize=9.5, ha="center", va="center", fontweight="bold")
    hline(ax, mid, 0, len(closes) - 1, color=NAVY, ls="--", lw=1.6, label="50%")
    set_ylim_pad(ax, list(l) + list(h), pad_frac=0.15)
    save(fig, "fig-08-02")

# ============================================================ 8.2 Fibonacci levels in SMC (dedicated)
def fig_08_03():
    fig, ax = new_ax(w=8.6, h=4.6)
    closes = regime_walk([(16, 0.6, 0.5), (14, -0.5, 0.45)], start=100, seed=803)
    o, h, l, c = to_ohlc(closes, seed=803)
    plot_candles(ax, o, h, l, c, width=0.55)
    swing_low, swing_high = l.min(), h.max()
    rng = swing_high - swing_low
    levels = {"0%": 1.0, "50%": 0.5, "61.8%": 0.382, "70.5%": 0.295, "100%": 0.0}
    for label, frac in levels.items():
        y = swing_low + rng * frac
        hline(ax, y, 0, len(closes) - 1, color=GREY, ls=":", lw=1.1, label=label, label_side="right")
    disc_top = swing_low + rng * 0.295
    box(ax, 0, len(closes) - 1, swing_low, disc_top, color="#DDEBDD", edge=GREEN, alpha=0.3)
    ax.text(len(closes) / 2, (swing_low + disc_top) / 2, "الخصم العميق (61.8%–70.5%)", color=GREEN,
            fontsize=9, ha="center", va="center", fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h), pad_frac=0.15)
    save(fig, "fig-08-03")

# ============================================================ 8.3 Rule 70-80-85 zoom (dedicated)
def fig_08_04():
    fig, ax = new_ax(w=8.6, h=4.6)
    closes = regime_walk([(16, 0.6, 0.5), (16, -0.5, 0.45)], start=100, seed=804)
    o, h, l, c = to_ohlc(closes, seed=804)
    plot_candles(ax, o, h, l, c, width=0.55)
    swing_low, swing_high = l[:16].min(), h[:16].max()
    rng = swing_high - swing_low
    zone_top = swing_low + rng * 0.30
    zone_bot = swing_low + rng * 0.15
    box(ax, 0, len(closes) - 1, zone_bot, zone_top, color="#DDEBDD", edge=GREEN, alpha=0.4, label="ارتداد 70%–85%")
    box(ax, 0, len(closes) - 1, zone_top, zone_top + (rng * 0.2), color="#F4A6A6", alpha=0.2, edge=None)
    ax.text(len(closes) / 2, zone_top + rng * 0.1, "لا تشترِ هنا (ارتداد ضحل فقط 20%-30%)", color=RED,
            fontsize=8.5, ha="center", fontweight="bold")
    ax.text(len(closes) / 2, (zone_bot + zone_top) / 2, "منطقة الدخول المفضلة (70%-85%)", color=GREEN,
            fontsize=9, ha="center", va="center", fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h) + [zone_top + rng * 0.3], pad_frac=0.08)
    ax.set_title("قاعدة 70-80-85: انتظار الخصم العميق قبل الشراء", fontsize=10.5, color=NAVY, fontweight="bold")
    save(fig, "fig-08-04")

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

# ============================================================ 9.3 Bank/news candle BCD (dedicated)
def fig_09_02():
    fig, ax = new_ax(w=8.6, h=4.6)
    pre = synth_walk(18, drift=0.02, vol=0.15, start=100, seed=902)
    news = synth_walk(1, drift=4.2, vol=0.15, start=pre[-1], seed=9021)
    post = synth_walk(18, drift=0.6, vol=0.6, start=news[-1], seed=9022)
    closes = np.concatenate([pre, news, post])
    o, h, l, c = to_ohlc(closes, seed=902)
    plot_candles(ax, o, h, l, c, width=0.6)
    news_x = 18
    ax.axvline(news_x, color=GREY, linestyle=":", linewidth=1.3)
    ax.annotate("شمعة أخبار (BCD): توقيت حدث عالي التأثير", xy=(news_x, c[news_x]), xytext=(news_x - 8, c[news_x] + 3.5),
                fontsize=9.5, color=RED, fontweight="bold",
                arrowprops=dict(arrowstyle="-|>", color=RED, linewidth=1.8))
    ax.text(news_x + 10, c[-1] + 0.5, "يحدد اتجاه الأيام التالية", color=NAVY, fontsize=9, ha="center", fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h) + [c[news_x] + 4.5])
    save(fig, "fig-09-02")

# ============================================================ 9.4 Flip zone (dedicated)
def fig_09_03():
    fig, ax = new_ax(w=8.6, h=4.6)
    approach = synth_walk(16, drift=0.15, vol=0.4, start=100, seed=903)
    level = approach.max() + 0.4
    ifc = synth_walk(2, drift=1.6, vol=0.2, start=approach[-1], seed=9031)
    cont = synth_walk(8, drift=0.5, vol=0.4, start=ifc[-1], seed=9032)
    retest = synth_walk(6, drift=-0.35, vol=0.3, start=cont[-1], seed=9033)
    bounce = synth_walk(12, drift=0.6, vol=0.5, start=retest[-1], seed=9034)
    closes = np.concatenate([approach, ifc, cont, retest, bounce])
    o, h, l, c = to_ohlc(closes, seed=903)
    plot_candles(ax, o, h, l, c, width=0.55)
    hline(ax, level, 0, len(closes) - 1, color=GOLD, lw=2.0, label="منطقة الفليب (Flip Zone)")
    box(ax, 16, 18, min(o[17], c[17]) - 0.15, max(o[17], c[17]) + 0.15, color=GOLD_LIGHT, edge=GOLD)
    ax.text(17, max(o[17], c[17]) + 1.0, "شمعة تدفق أوامر (IFC)", color=GOLD, fontsize=8.5, ha="center", fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h) + [max(o[17], c[17]) + 1.4])
    save(fig, "fig-09-03")

# ============================================================ 9.5a Accumulation -> Expansion (dedicated)
def fig_09_04():
    fig, ax = new_ax(w=8.6, h=4.6)
    accum = synth_walk(20, drift=0.0, vol=0.35, start=100, seed=904)
    expand = synth_walk(16, drift=0.9, vol=0.6, start=accum[-1], seed=9041)
    closes = np.concatenate([accum, expand])
    o, h, l, c = to_ohlc(closes, seed=904)
    plot_candles(ax, o, h, l, c, width=0.55)
    box(ax, 0, 19, l[:20].min() - 0.15, h[:20].max() + 0.15, color="#DDE7EE", edge=NAVY, alpha=0.3, label="تراكم (Accumulation)")
    arrow(ax, (20, c[20]), (35, c[-1]), color=GREEN, label="اندفاع (Expansion)")
    set_ylim_pad(ax, list(l) + list(h))
    save(fig, "fig-09-04")

# ============================================================ 9.5b Expansion -> Re-balance (dedicated)
def fig_09_05():
    fig, ax = new_ax(w=8.6, h=4.6)
    expand = synth_walk(12, drift=1.0, vol=0.5, start=100, seed=905)
    rebalance = synth_walk(14, drift=-0.35, vol=0.35, start=expand[-1], seed=9051)
    cont = synth_walk(10, drift=0.7, vol=0.5, start=rebalance[-1], seed=9052)
    closes = np.concatenate([expand, rebalance, cont])
    o, h, l, c = to_ohlc(closes, seed=905)
    plot_candles(ax, o, h, l, c, width=0.55)
    x1, x3 = 10, 12
    fvg_lo, fvg_hi = h[x1], l[x3]
    if fvg_hi < fvg_lo: fvg_lo, fvg_hi = fvg_hi, fvg_lo
    box(ax, x1 + 0.3, x3 - 0.3, fvg_lo, fvg_hi, color="#F2D98A", edge="#B7791F", label="FVG")
    arrow(ax, (12, c[12]), (25, fvg_hi), color=NAVY, ls="dashed", label="إعادة توازن نحو الاختلال")
    set_ylim_pad(ax, list(l) + list(h))
    save(fig, "fig-09-05")

# ============================================================ 9.5c Distribution (dedicated)
def fig_09_06():
    fig, ax = new_ax(w=8.6, h=4.6)
    up = synth_walk(18, drift=0.6, vol=0.5, start=100, seed=906)
    dist = synth_walk(16, drift=0.0, vol=0.4, start=up[-1], seed=9061)
    down = synth_walk(14, drift=-0.8, vol=0.55, start=dist[-1], seed=9062)
    closes = np.concatenate([up, dist, down])
    o, h, l, c = to_ohlc(closes, seed=906)
    plot_candles(ax, o, h, l, c, width=0.55)
    box(ax, 18, 33, l[18:34].min() - 0.15, h[18:34].max() + 0.15, color="#F4A6A6", edge=RED, alpha=0.3, label="توزيع (Distribution)")
    arrow(ax, (34, c[34]), (47, c[-1]), color=RED, label="انعكاس هبوطي")
    set_ylim_pad(ax, list(l) + list(h))
    save(fig, "fig-09-06")

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

# ============================================================ 10.5 HTF/LTF conflict resolution (dedicated)
def fig_10_02():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.4), dpi=150)
    htf = regime_walk([(20, 0.6, 0.45), (8, -0.2, 0.3), (14, 0.6, 0.45)], start=100, seed=1002)
    o1, h1, l1, c1 = to_ohlc(htf, seed=1002, wick=0.4)
    plot_candles(axes[0], o1, h1, l1, c1, width=0.55)
    axes[0].text(len(htf) / 2, h1.max() + 0.5, "انحياز صاعد واضح على الفريم الأعلى", color=GREEN, fontsize=9,
                 ha="center", fontweight="bold")
    axes[0].set_title("الإطار الأعلى (HTF): الحكم الفصل", fontsize=10, color=NAVY, fontweight="bold")

    ltf = synth_walk(30, drift=-0.15, vol=0.4, start=100, seed=1003)
    o2, h2, l2, c2 = to_ohlc(ltf, seed=1003, wick=0.4)
    plot_candles(axes[1], o2, h2, l2, c2, width=0.55)
    axes[1].text(15, h2.max() + 0.4, "تصحيح هابط بسيط فقط — ليس انعكاسًا", color=RED, fontsize=9,
                 ha="center", fontweight="bold")
    axes[1].set_title("الإطار الأصغر (LTF): تصحيح مؤقت", fontsize=10, color=NAVY, fontweight="bold")
    for ax in axes:
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        ax.set_xticks([])
    fig.tight_layout(pad=0.8)
    save(fig, "fig-10-02")

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

# ============================================================ 12.1 System 1: Daily bias + OB entry (dedicated)
def fig_12_02():
    fig, ax = new_ax(w=8.6, h=4.6)
    up = synth_walk(14, drift=0.6, vol=0.5, start=100, seed=1202)
    ob_seg = synth_walk(4, drift=-0.15, vol=0.3, start=up[-1], seed=12021)
    bos = synth_walk(8, drift=0.8, vol=0.5, start=ob_seg[-1], seed=12022)
    retest = synth_walk(8, drift=-0.5, vol=0.4, start=bos[-1], seed=12023)
    cont = synth_walk(10, drift=0.7, vol=0.5, start=retest[-1], seed=12024)
    closes = np.concatenate([up, ob_seg, bos, retest, cont])
    o, h, l, c = to_ohlc(closes, seed=1202)
    plot_candles(ax, o, h, l, c, width=0.55)
    ob_x = 15
    box(ax, ob_x - 0.6, ob_x + 0.6, min(o[ob_x], c[ob_x]) - 0.15, max(o[ob_x], c[ob_x]) + 0.15, color=GOLD_LIGHT, edge=GOLD)
    ax.text(2, h.max() + 0.8, "1: انحياز يومي صاعد", color=NAVY, fontsize=9, fontweight="bold")
    ax.text(2, h.max() + 0.1, "2: كتلة طلب 4 ساعات", color=GOLD, fontsize=9, fontweight="bold")
    arrow(ax, (32, l[32]), (38, l[32] + 0.2), color=GREEN, label="3: دخول عند الرفض")
    set_ylim_pad(ax, list(l) + list(h) + [h.max() + 1.4])
    ax.set_title("النظام 1: الانحياز اليومي + الدخول من كتلة طلب", fontsize=10.5, color=NAVY, fontweight="bold")
    save(fig, "fig-12-02")

# ============================================================ 12.2 System 2: Liquidity sweep + FVG entry (dedicated)
def fig_12_03():
    fig, ax = new_ax(w=8.6, h=4.6)
    pre = synth_walk(14, drift=-0.1, vol=0.3, start=100, seed=1203)
    sweep = synth_walk(3, drift=-0.9, vol=0.25, start=pre[-1], seed=12031)
    imp = synth_walk(3, drift=1.6, vol=0.3, start=sweep[-1], seed=12032)
    cont = synth_walk(14, drift=0.6, vol=0.5, start=imp[-1], seed=12033)
    closes = np.concatenate([pre, sweep, imp, cont])
    o, h, l, c = to_ohlc(closes, seed=1203)
    plot_candles(ax, o, h, l, c, width=0.55)
    level = l[:14].min() + 0.05
    hline(ax, level, 0, len(closes) - 1, color=GREY, lw=1.6, label="1: سيولة (قيعان متساوية)")
    arrow(ax, (16, l[16]), (18, l[16] - 1.0), color=RED, ls="dashed", label="2: سحب سيولة")
    x1, x3 = 17, 19
    fvg_lo, fvg_hi = h[x1], l[x3]
    if fvg_hi < fvg_lo: fvg_lo, fvg_hi = fvg_hi, fvg_lo
    box(ax, x1 + 0.3, x3 - 0.3, fvg_lo, fvg_hi, color="#F2D98A", edge="#B7791F", label="3: FVG")
    set_ylim_pad(ax, list(l) + list(h) + [l[16] - 1.4])
    ax.set_title("النظام 2: سحب السيولة + الدخول من FVG", fontsize=10.5, color=NAVY, fontweight="bold")
    save(fig, "fig-12-03")

# ============================================================ 12.3 System 3: CHOCH + flip zone entry (dedicated)
def fig_12_04():
    fig, ax = new_ax(w=8.6, h=4.6)
    down = synth_walk(14, drift=-0.55, vol=0.5, start=108, seed=1204)
    choch = synth_walk(4, drift=0.9, vol=0.4, start=down[-1], seed=12041)
    cont = synth_walk(10, drift=0.5, vol=0.5, start=choch[-1], seed=12042)
    retest = synth_walk(6, drift=-0.35, vol=0.3, start=cont[-1], seed=12043)
    bounce = synth_walk(10, drift=0.7, vol=0.5, start=retest[-1], seed=12044)
    closes = np.concatenate([down, choch, cont, retest, bounce])
    o, h, l, c = to_ohlc(closes, seed=1204)
    plot_candles(ax, o, h, l, c, width=0.55)
    arrow(ax, (13, l[13]), (17, h[17] + 0.5), color=NAVY, label="1: CHOCH")
    flip = h[14:18].max() + 0.1
    hline(ax, flip, 18, len(closes) - 1, color=GOLD, lw=2.0, label="2: منطقة فليب")
    marker_point(ax, 30, flip + 0.1, color=GREEN, label="3: إعادة اختبار ناجحة", va="bottom", dy=0.6, fontsize=8.5)
    set_ylim_pad(ax, list(l) + list(h) + [h[14:18].max() + 1.2])
    ax.set_title("النظام 3: CHOCH + الدخول من منطقة الفليب", fontsize=10.5, color=NAVY, fontweight="bold")
    save(fig, "fig-12-04")

# ============================================================ 12.4 System 4: Multi-timeframe alignment (dedicated)
def fig_12_05():
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 4.2), dpi=150)
    titles = ["يومي: انحياز صاعد", "4 ساعات: منطقة اهتمام", "15 دقيقة: دخول دقيق"]
    seeds = [1205, 1206, 1207]
    drifts = [0.5, 0.15, 0.05]
    for ax, title, sd, dr in zip(axes, titles, seeds, drifts):
        closes = synth_walk(24, drift=dr, vol=0.6, start=100, seed=sd)
        o, h, l, c = to_ohlc(closes, seed=sd)
        plot_candles(ax, o, h, l, c, width=0.6)
        for spine in ["top", "right"]: ax.spines[spine].set_visible(False)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(title, fontsize=10, color=GREEN, fontweight="bold")
        set_ylim_pad(ax, list(l) + list(h))
    fig.suptitle("النظام 4: دخول فقط عند توافق الفريمات الثلاثة على نفس الاتجاه", fontsize=10.5, color=NAVY, fontweight="bold")
    fig.tight_layout(pad=0.8, rect=[0, 0, 1, 0.92])
    save(fig, "fig-12-05")

# ============================================================ 12.5 System 5: Discount/Premium + inducement (dedicated)
def fig_12_06():
    fig, ax = new_ax(w=8.6, h=4.6)
    up = synth_walk(20, drift=0.6, vol=0.5, start=100, seed=1208)
    pull = synth_walk(10, drift=-0.4, vol=0.4, start=up[-1], seed=12081)
    ind = synth_walk(4, drift=-0.3, vol=0.2, start=pull[-1], seed=12082)
    sweep = synth_walk(2, drift=-0.6, vol=0.2, start=ind[-1], seed=12083)
    cont = synth_walk(12, drift=0.75, vol=0.5, start=sweep[-1], seed=12084)
    closes = np.concatenate([up, pull, ind, sweep, cont])
    o, h, l, c = to_ohlc(closes, seed=1208)
    plot_candles(ax, o, h, l, c, width=0.55)
    swing_low, swing_high = l[:20].min(), h[:20].max()
    rng = swing_high - swing_low
    disc_top = swing_low + rng * 0.30
    box(ax, 0, len(closes) - 1, swing_low, disc_top, color="#DDEBDD", edge=GREEN, alpha=0.3, label="1: منطقة خصم عميقة")
    letter_point(ax, 32, l[32] - 0.2, "2: حافز", color=RED, va="top", dy=0.5, circle=False, fontsize=9)
    arrow(ax, (34, l[34]), (44, c[-1]), color=GREEN, label="3: دخول بعد السحب")
    set_ylim_pad(ax, list(l) + list(h))
    ax.set_title("النظام 5: الخصم/العلاوة + الحافز", fontsize=10.5, color=NAVY, fontweight="bold")
    save(fig, "fig-12-06")

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

# ============================================================ 13.3 Three-layer framework flow (dedicated)
def fig_13_02():
    fig, ax = plt.subplots(figsize=(8.6, 3.8), dpi=150)
    ax.set_xlim(0, 10); ax.set_ylim(0, 4); ax.axis("off")
    fig.patch.set_facecolor("white")
    boxes = [
        (0.5, "التحليل الأساسي", "تحديد الانحياز الكلي", NAVY),
        (3.8, "مفاهيم SMC", "تحديد منطقة الاهتمام", GOLD),
        (7.1, "التحليل الفني", "توقيت الدخول الدقيق", GREEN),
    ]
    for x, title, sub, color in boxes:
        ax.add_patch(Rectangle((x, 1.3), 2.4, 1.4, facecolor=color, alpha=0.15, edgecolor=color, linewidth=1.8))
        ax.text(x + 1.2, 2.25, title, ha="center", va="center", fontsize=10.5, color=color, fontweight="bold")
        ax.text(x + 1.2, 1.65, sub, ha="center", va="center", fontsize=8.5, color=NAVY)
    for x0 in [0.5, 3.8]:
        ax.add_patch(FancyArrowPatch((x0 + 2.4, 2.0), (x0 + 3.3, 2.0), arrowstyle="-|>", color=GREY,
                                      linewidth=2, mutation_scale=16))
    save(fig, "fig-13-02")

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

# ============================================================ 14.5 QE vs QT (dedicated)
def fig_14_02():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), dpi=150)
    n = 24
    qe_balance = 100 + np.cumsum(np.random.default_rng(1402).uniform(1.5, 3.5, n))
    qe_curr = 100 - np.cumsum(np.random.default_rng(1403).uniform(0.2, 0.8, n))
    axes[0].plot(qe_balance, color=NAVY, linewidth=2.2, label="ميزانية البنك المركزي")
    axes[0].plot(qe_curr, color=RED, linewidth=2.2, linestyle="--", label="قيمة العملة")
    axes[0].set_title("التيسير الكمي (QE)", fontsize=10.5, color=NAVY, fontweight="bold")

    qt_balance = 130 - np.cumsum(np.random.default_rng(1404).uniform(1.5, 3.5, n))
    qt_curr = 96 + np.cumsum(np.random.default_rng(1405).uniform(0.2, 0.8, n))
    axes[1].plot(qt_balance, color=NAVY, linewidth=2.2, label="ميزانية البنك المركزي")
    axes[1].plot(qt_curr, color=GREEN, linewidth=2.2, linestyle="--", label="قيمة العملة")
    axes[1].set_title("التشديد الكمي (QT)", fontsize=10.5, color=NAVY, fontweight="bold")

    for ax in axes:
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        ax.set_xticks([]); ax.set_yticks([])
        ax.legend(frameon=False, fontsize=8.5, loc="center left")
    fig.tight_layout(pad=0.8)
    save(fig, "fig-14-02")

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

# ============================================================ 15.6 Yield curve: normal vs inverted (dedicated)
def fig_15_02():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), dpi=150)
    maturities = ["1ش", "3ش", "1س", "2س", "5س", "10س", "30س"]
    normal = [1.0, 1.3, 1.8, 2.3, 2.8, 3.2, 3.6]
    axes[0].plot(range(len(maturities)), normal, color=GREEN, linewidth=2.4, marker="o", markersize=5)
    axes[0].set_xticks(range(len(maturities))); axes[0].set_xticklabels(maturities, fontsize=8.5)
    axes[0].set_title("منحنى طبيعي: نمو اقتصادي متوقع", fontsize=10, color=GREEN, fontweight="bold")

    inverted = [3.6, 3.5, 3.3, 3.0, 2.6, 2.2, 2.0]
    axes[1].plot(range(len(maturities)), inverted, color=RED, linewidth=2.4, marker="o", markersize=5)
    axes[1].set_xticks(range(len(maturities))); axes[1].set_xticklabels(maturities, fontsize=8.5)
    axes[1].set_title("منحنى معكوس: إشارة تحذيرية من ركود", fontsize=10, color=RED, fontweight="bold")

    for ax in axes:
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        ax.set_ylabel("العائد (%)")
        ax.grid(axis="y", color=GRID)
    fig.tight_layout(pad=0.8)
    save(fig, "fig-15-02")

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

# ============================================================ 16.8 Inflation vs Disinflation vs Deflation (dedicated)
def fig_16_02():
    fig, ax = plt.subplots(figsize=(8.6, 4.4), dpi=150)
    fig.patch.set_facecolor("white")
    months = np.arange(12)
    inflation = 2.0 + months * 0.15
    disinflation = 6.0 - months * 0.3
    deflation = 1.0 - months * 0.2
    ax.plot(months, inflation, color=RED, linewidth=2.2, label="تضخم متسارع")
    ax.plot(months, disinflation, color=GOLD, linewidth=2.2, label="تباطؤ تضخم (Disinflation)")
    ax.plot(months, deflation, color=NAVY, linewidth=2.2, label="انكماش (Deflation)")
    ax.axhline(0, color=GREY, linestyle=":", linewidth=1.2)
    ax.set_ylabel("التغير السنوي في الأسعار (%)")
    ax.set_xlabel("الشهر")
    ax.grid(axis="y", color=GRID)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    ax.legend(frameon=False, fontsize=9)
    save(fig, "fig-16-02")

# ============================================================ 16.5 PPI as a leading indicator of CPI (dedicated)
def fig_16_03():
    fig, ax1 = plt.subplots(figsize=(8.6, 4.6), dpi=150)
    fig.patch.set_facecolor("white")
    months = np.arange(14)
    ppi = 3.0 + 2.5 * np.sin((months - 2) / 3.5) + np.random.default_rng(1603).normal(0, 0.08, 14)
    cpi = 3.0 + 2.5 * np.sin((months - 5) / 3.5) + np.random.default_rng(1604).normal(0, 0.08, 14)
    ax1.plot(months, ppi, color=GOLD, linewidth=2.2, marker="o", markersize=4, label="مؤشر أسعار المنتجين (PPI)")
    ax1.plot(months, cpi, color=NAVY, linewidth=2.2, marker="s", markersize=4, label="مؤشر أسعار المستهلك (CPI)")
    ax1.annotate("", xy=(5, cpi[5]), xytext=(2, ppi[2]),
                 arrowprops=dict(arrowstyle="-|>", color=RED, linewidth=1.6, linestyle="--"))
    ax1.text(3.5, (ppi[2] + cpi[5]) / 2 + 0.5, "PPI يتقدّم بنحو 3 أشهر", color=RED, fontsize=9, ha="center", fontweight="bold")
    ax1.set_ylabel("التغير السنوي (%)")
    ax1.set_xlabel("الشهر")
    ax1.grid(axis="y", color=GRID)
    for s in ["top", "right"]: ax1.spines[s].set_visible(False)
    ax1.legend(frameon=False, fontsize=9)
    save(fig, "fig-16-03")

# ============================================================ 16.7 Inflation targeting reaction (dedicated)
def fig_16_04():
    fig, ax = new_ax(price_axis=False, w=8.6, h=4.6)
    n = 30
    rate = np.concatenate([np.full(12, 2.0), np.linspace(2.0, 4.5, 10), np.full(8, 4.5)])
    cpi_target = np.full(n, 2.0)
    cpi_actual = np.concatenate([np.linspace(2.0, 5.5, 14), np.linspace(5.5, 3.0, 16)])
    ax.plot(cpi_actual, color=RED, linewidth=2.2, label="التضخم الفعلي (CPI)")
    ax.plot(cpi_target, color=GREY, linestyle=":", linewidth=1.6, label="هدف التضخم (2%)")
    ax.plot(rate, color=NAVY, linewidth=2.2, linestyle="--", label="سعر الفائدة")
    ax.axvspan(12, 22, color=GOLD, alpha=0.08)
    ax.text(17, 6.0, "رفع الفائدة تدريجيًا لإعادة التضخم للهدف", color=GOLD, fontsize=9, ha="center", fontweight="bold")
    ax.set_ylabel("%")
    ax.legend(frameon=False, fontsize=9)
    save(fig, "fig-16-04")

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

# ============================================================ 17.5 Participation rate vs unemployment (dedicated)
def fig_17_02():
    fig, ax1 = plt.subplots(figsize=(8.6, 4.4), dpi=150)
    fig.patch.set_facecolor("white")
    months = np.arange(12)
    unemployment = 5.5 - months * 0.15 + np.random.default_rng(1702).normal(0, 0.05, 12)
    participation = 63.0 - months * 0.12 + np.random.default_rng(1703).normal(0, 0.04, 12)
    ax1.plot(months, unemployment, color=RED, linewidth=2.2, marker="o", markersize=4, label="معدل البطالة")
    ax1.set_ylabel("معدل البطالة (%)", color=RED)
    ax1.tick_params(axis="y", labelcolor=RED)
    for s in ["top"]: ax1.spines[s].set_visible(False)
    ax2 = ax1.twinx()
    ax2.plot(months, participation, color=NAVY, linewidth=2.2, linestyle="--", marker="s", markersize=4, label="معدل المشاركة")
    ax2.set_ylabel("معدل المشاركة (%)", color=NAVY)
    ax2.tick_params(axis="y", labelcolor=NAVY)
    for s in ["top"]: ax2.spines[s].set_visible(False)
    ax1.set_xlabel("الشهر")
    ax1.grid(axis="y", color=GRID)
    ax1.text(6, unemployment.max() + 0.3, "انخفاض البطالة مع تراجع المشاركة معًا:\nانسحاب من سوق العمل، لا تحسّن حقيقي بالضرورة",
              color=NAVY, fontsize=8.5, ha="center", fontweight="bold")
    save(fig, "fig-17-02")

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

# ============================================================ 18.4 Technical recession (dedicated)
def fig_18_02():
    fig, ax = plt.subplots(figsize=(8.6, 4.2), dpi=150)
    fig.patch.set_facecolor("white")
    quarters = ["ر1", "ر2", "ر3", "ر4", "ر5", "ر6"]
    growth = [1.8, 0.9, -0.4, -0.6, 0.3, 1.1]
    colors = [RED if v < 0 else GREEN for v in growth]
    bars = ax.bar(quarters, growth, color=colors, width=0.55, zorder=3)
    ax.axhline(0, color=NAVY, linewidth=1.2)
    ax.axvspan(1.5, 3.5, color=RED, alpha=0.08)
    ax.text(2.5, 1.6, "ركود فني (ربعان سلبيان متتاليان)", color=RED, fontsize=9.5, ha="center", fontweight="bold")
    for b, v in zip(bars, growth):
        ax.text(b.get_x() + b.get_width() / 2, v + (0.1 if v >= 0 else -0.2), f"{v}%", ha="center",
                fontsize=9, fontweight="bold", color=NAVY)
    ax.set_ylabel("نمو الناتج المحلي (ربع سنوي %)")
    ax.grid(axis="y", color=GRID, zorder=0)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    save(fig, "fig-18-02")

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

# ============================================================ 20.3 Current account deficit financed by capital inflows (dedicated)
def fig_20_02():
    fig, ax = plt.subplots(figsize=(8.6, 4.2), dpi=150)
    fig.patch.set_facecolor("white")
    cats = ["عجز الحساب الجاري", "فائض حساب رأس المال"]
    vals = [-4.2, 4.2]
    colors = [RED, GREEN]
    bars = ax.bar(cats, vals, color=colors, width=0.45, zorder=3)
    ax.axhline(0, color=NAVY, linewidth=1.3)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + (0.2 if v >= 0 else -0.3), f"{v:+.1f} مليار", ha="center",
                fontsize=9.5, fontweight="bold", color=NAVY)
    ax.text(0.5, 3.0, "يجب تمويل العجز بتدفقات استثمارية داخلة مساوية تقريبًا", color=NAVY, fontsize=9,
            ha="center", fontweight="bold")
    ax.set_ylabel("مليار دولار")
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    ax.set_xticks([]); ax.set_xticklabels([])
    ax.legend(bars, cats, frameon=False, fontsize=9, loc="lower center")
    save(fig, "fig-20-02")

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

# ============================================================ 21.6 P/E comparable valuation (dedicated)
def fig_21_02():
    fig, ax = plt.subplots(figsize=(8.6, 4.2), dpi=150)
    fig.patch.set_facecolor("white")
    cats = ["الشركة A", "الشركة B", "الشركة C", "متوسط القطاع"]
    vals = [28, 15, 34, 22]
    colors = [RED if v > 22 else GREEN for v in vals[:3]] + [GREY]
    bars = ax.bar(cats, vals, color=colors, width=0.5, zorder=3)
    ax.axhline(22, color=NAVY, linestyle="--", linewidth=1.4)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.6, f"{v}x", ha="center", fontsize=9.5, fontweight="bold", color=NAVY)
    ax.text(1.5, 37, "مضاعف الربحية (P/E) مقارنة بمتوسط القطاع", color=NAVY, fontsize=9.5, ha="center", fontweight="bold")
    ax.set_ylabel("مضاعف P/E")
    ax.grid(axis="y", color=GRID, zorder=0)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    save(fig, "fig-21-02")

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

# ============================================================ 22.3 Three news-trading strategies (dedicated)
def fig_22_02():
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 4.0), dpi=150)
    pre = synth_walk(10, drift=0.0, vol=0.15, start=100, seed=2202)
    spike = synth_walk(4, drift=1.6, vol=0.6, start=pre[-1], seed=22021)
    settle = synth_walk(10, drift=0.4, vol=0.3, start=spike[-1], seed=22022)
    closes = np.concatenate([pre, spike, settle])
    o, h, l, c = to_ohlc(closes, seed=2202, wick=0.6)

    titles = ["التداول اللحظي عند الصدور", "انتظار الاستقرار", "التموضع المسبق"]
    colors = [RED, GOLD, GREEN]
    for ax, title, color in zip(axes, titles, colors):
        plot_candles(ax, o, h, l, c, width=0.55)
        ax.axvline(10, color=GREY, linestyle=":", linewidth=1.2)
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(title, fontsize=9.5, color=color, fontweight="bold")
    marker_point(axes[0], 11, h[11] + 0.2, color=RED, label="دخول خطر", va="bottom", dy=0.5, fontsize=8)
    marker_point(axes[1], 16, l[16] - 0.2, color=GOLD, label="دخول بعد استقرار", va="top", dy=0.5, fontsize=8)
    marker_point(axes[2], 3, l[3] - 0.2, color=GREEN, label="تموضع مسبق", va="top", dy=0.5, fontsize=8)
    fig.tight_layout(pad=0.8)
    save(fig, "fig-22-02")

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

def _candle_pattern_fig(name, title, candles, xlim=(-1, None), ylim=(0, 5)):
    n = max(cx for cx, *_ in candles) + 1
    x1 = xlim[1] if xlim[1] is not None else n
    fig, ax = plt.subplots(figsize=(8.0, 2.7), dpi=150)
    fig.patch.set_facecolor("white")
    for cx, o, h, l, c in candles:
        _draw_candle_shape(ax, cx, o, h, l, c, w=0.55)
    ax.set_xlim(xlim[0], x1)
    ax.set_ylim(*ylim)
    ax.set_title(title, fontsize=11, color=NAVY, fontweight="bold")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
    save(fig, name)

# ============================================================ 25.2 dedicated single-candle patterns
def fig_25_03():
    _candle_pattern_fig("fig-25-03", "المطرقة (Hammer) — انعكاس صعودي محتمل", [(0, 2.7, 3.1, 1.0, 3.0)])

def fig_25_04():
    _candle_pattern_fig("fig-25-04", "الرجل المشنوق (Hanging Man) — انعكاس هبوطي محتمل", [(0, 3.0, 3.1, 1.0, 2.7)])

def fig_25_05():
    _candle_pattern_fig("fig-25-05", "النجمة الساقطة (Shooting Star) — انعكاس هبوطي محتمل", [(0, 2.3, 4.5, 2.2, 2.6)])

def fig_25_06():
    _candle_pattern_fig("fig-25-06", "المغزل (Spinning Top) — تردد وتوازن", [(0, 2.4, 4.0, 1.0, 2.7)])

def fig_25_07():
    _candle_pattern_fig("fig-25-07", "الدوجي (Doji) — تردد شديد", [(0, 2.5, 4.0, 1.0, 2.55)])

def fig_25_08():
    _candle_pattern_fig("fig-25-08", "ماروبوزو (Marubozu) — سيطرة كاملة لطرف واحد", [(0, 1.0, 4.0, 1.0, 4.0)])

# ============================================================ 25.3 dedicated two-candle patterns
def fig_25_09():
    _candle_pattern_fig("fig-25-09", "السحابة الداكنة (Dark Cloud Cover) — انعكاس هبوطي",
                        [(0, 1.5, 3.6, 1.4, 3.5), (1, 3.8, 3.9, 2.0, 2.3)], xlim=(-1, 2))

def fig_25_10():
    _candle_pattern_fig("fig-25-10", "خط الاختراق (Piercing Line) — انعكاس صعودي",
                        [(0, 3.5, 3.6, 1.4, 1.5), (1, 1.2, 3.2, 1.1, 2.8)], xlim=(-1, 2))

# ============================================================ 25.4 dedicated three-candle patterns
def fig_25_11():
    _candle_pattern_fig("fig-25-11", "نجمة المساء (Evening Star) — انعكاس هبوطي",
                        [(0, 1.0, 4.3, 0.8, 4.0), (1, 4.05, 4.4, 3.85, 4.15), (2, 3.9, 4.1, 0.8, 1.1)],
                        xlim=(-1, 3))

def fig_25_12():
    _candle_pattern_fig("fig-25-12", "ثلاثة جنود بيض (Three White Soldiers) — استمرار صعودي قوي",
                        [(0, 1.0, 2.1, 0.9, 2.0), (1, 1.6, 2.9, 1.5, 2.8), (2, 2.3, 3.7, 2.2, 3.6)],
                        xlim=(-1, 3))

def fig_25_13():
    _candle_pattern_fig("fig-25-13", "ثلاثة غربان سود (Three Black Crows) — استمرار هبوطي قوي",
                        [(0, 3.6, 3.7, 2.5, 2.6), (1, 3.0, 3.1, 1.7, 1.8), (2, 2.2, 2.3, 0.9, 1.0)],
                        xlim=(-1, 3), ylim=(0, 4.2))

# ============================================================ 25.5 dedicated continuation patterns
def fig_25_14():
    _candle_pattern_fig("fig-25-14", "الثلاث طرق الصاعدة (Rising Three Methods) — استمرار صعودي",
                        [(0, 1.0, 4.0, 0.9, 3.9), (1, 3.6, 3.7, 3.0, 3.1), (2, 3.2, 3.3, 2.6, 2.7),
                         (3, 2.8, 2.9, 2.3, 2.4), (4, 2.5, 5.0, 2.4, 4.8)], xlim=(-1, 5))

def fig_25_15():
    _candle_pattern_fig("fig-25-15", "الثلاث طرق الهابطة (Falling Three Methods) — استمرار هبوطي",
                        [(0, 4.0, 4.1, 1.0, 1.1), (1, 1.4, 2.0, 1.3, 1.9), (2, 1.8, 2.4, 1.7, 2.3),
                         (3, 2.2, 2.7, 2.1, 2.6), (4, 2.5, 2.6, 0.0, 0.2)], xlim=(-1, 5))

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

# ============================================================ 31.1 Harmonic pattern XABCD (dedicated)
def fig_31_02():
    fig, ax = plt.subplots(figsize=(8.0, 5.0), dpi=150)
    fig.patch.set_facecolor("white")
    pts = {"X": (0, 1.0), "A": (1.5, 4.5), "B": (2.6, 2.4), "C": (3.8, 3.8), "D": (5.0, 0.6)}
    xs = [p[0] for p in pts.values()]
    ys = [p[1] for p in pts.values()]
    ax.plot(xs, ys, color=NAVY, linewidth=2.2, marker="o", markersize=6)
    for name, (x, y) in pts.items():
        ax.text(x, y + 0.25, name, fontsize=12, color=GOLD, fontweight="bold", ha="center")
    ax.text(0.75, 3.0, "XA", color=GREY, fontsize=8.5, ha="center")
    ax.text(2.05, 3.7, "AB (61.8% XA)", color=GREY, fontsize=8.5, ha="center")
    ax.text(3.2, 2.9, "BC", color=GREY, fontsize=8.5, ha="center")
    ax.text(4.4, 2.4, "CD", color=GREY, fontsize=8.5, ha="center")
    ax.text(2.5, -0.4, "منطقة D: عكس محتمل عند تطابق نسب فيبوناتشي الدقيقة", color=NAVY, fontsize=9,
            ha="center", fontweight="bold")
    ax.set_xlim(-0.5, 5.5); ax.set_ylim(-0.8, 5.2)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
    ax.set_title("النمط التوافقي (Harmonic Pattern) — تسلسل X-A-B-C-D", fontsize=11, color=NAVY, fontweight="bold")
    save(fig, "fig-31-02")

# ============================================================ 31.2 Gann angles (dedicated)
def fig_31_03():
    fig, ax = new_ax(w=8.6, h=4.8)
    closes = synth_walk(40, drift=0.4, vol=0.5, start=100, seed=3103)
    o, h, l, c = to_ohlc(closes, seed=3103)
    plot_candles(ax, o, h, l, c, width=0.5)
    x0, y0 = 0, l.min()
    for slope, label, color in [(0.5, "1x2", GREY), (1.0, "1x1 (زاوية جان الأساسية)", GOLD), (2.0, "2x1", RED)]:
        xs = np.array([x0, 39])
        ax.plot(xs, y0 + slope * (xs - x0), color=color, linewidth=1.8, linestyle="--")
        ax.text(39.3, y0 + slope * 39, label, color=color, fontsize=8.5, va="center")
    set_ylim_pad(ax, list(l) + list(h) + [y0 + 2.0 * 39], pad_frac=0.05)
    ax.set_title("زوايا جان (Gann Angles): علاقة هندسية بين السعر والزمن", fontsize=10.5, color=NAVY, fontweight="bold")
    save(fig, "fig-31-03")

# ============================================================ 31.4 Market Profile / Value Area (dedicated)
def fig_31_04():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.4, 4.8), dpi=150, gridspec_kw={"width_ratios": [2.6, 1]})
    n = 40
    closes = 100 + 3 * np.sin(np.arange(n) / 5) + np.random.default_rng(3104).normal(0, 0.3, n)
    o, h, l, c = to_ohlc(closes, seed=3104)
    plot_candles(ax1, o, h, l, c, width=0.55)
    for s in ["top", "right"]: ax1.spines[s].set_visible(False)
    ax1.set_xticks([])
    price_bins = np.linspace(l.min(), h.max(), 20)
    counts = np.exp(-((price_bins - np.median(closes)) ** 2) / 1.2) * 40 + np.random.default_rng(3105).uniform(0, 3, 20)
    ax2.barh(price_bins, counts, height=(price_bins[1] - price_bins[0]) * 0.9, color=GOLD_LIGHT, edgecolor=GOLD)
    va_lo, va_hi = np.percentile(price_bins, 30), np.percentile(price_bins, 70)
    ax2.axhspan(va_lo, va_hi, color=GREEN, alpha=0.12)
    ax2.text(counts.max() * 0.5, (va_lo + va_hi) / 2, "منطقة القيمة\n(Value Area)", color=GREEN, fontsize=8.5,
              ha="center", va="center", fontweight="bold")
    ax2.set_ylim(ax1.get_ylim())
    ax2.set_xlabel("حجم عند كل مستوى")
    for s in ["top", "right"]: ax2.spines[s].set_visible(False)
    ax2.set_yticks([])
    fig.suptitle("بروفايل السوق (Market Profile): توزيع الحجم عبر المستويات السعرية", fontsize=10.5, color=NAVY, fontweight="bold")
    fig.tight_layout(pad=0.8, rect=[0, 0, 1, 0.93])
    save(fig, "fig-31-04")

# ============================================================ 31.6 Pivot points (dedicated)
def fig_31_05():
    fig, ax = new_ax(w=8.6, h=4.8)
    closes = synth_walk(30, drift=0.1, vol=0.5, start=100, seed=3106)
    o, h, l, c = to_ohlc(closes, seed=3106)
    plot_candles(ax, o, h, l, c, width=0.55)
    pp = (h.max() + l.min() + c[-1]) / 3
    rng = h.max() - l.min()
    levels = {"R2": pp + rng, "R1": pp + rng * 0.5, "PP": pp, "S1": pp - rng * 0.5, "S2": pp - rng}
    colors_map = {"R2": RED, "R1": RED, "PP": NAVY, "S1": GREEN, "S2": GREEN}
    for label, y in levels.items():
        hline(ax, y, 0, len(closes) - 1, color=colors_map[label], ls="--", lw=1.4, label=label, label_side="right")
    set_ylim_pad(ax, list(l) + list(h) + [levels["R2"] + 1, levels["S2"] - 1])
    ax.set_title("نقاط البيفوت (Pivot Points): PP وR1/R2 وS1/S2", fontsize=10.5, color=NAVY, fontweight="bold")
    save(fig, "fig-31-05")

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

# ============================================================ 33.2 Fear vs Greed behavior (dedicated)
def fig_33_02():
    fig, ax = new_ax(w=8.6, h=4.8)
    closes = regime_walk([(10, 0.5, 0.4), (8, -0.4, 0.4), (14, 0.65, 0.5)], start=100, seed=3302)
    o, h, l, c = to_ohlc(closes, seed=3302)
    plot_candles(ax, o, h, l, c, width=0.55)
    marker_point(ax, 9, h[9] + 0.2, color=RED, label="خروج مبكر بدافع الخوف", va="bottom", dy=0.6, fontsize=8.5)
    marker_point(ax, 25, l[25] - 0.2, color=GOLD, label="بقاء في الاتجاه أملًا بمزيد من الربح (طمع)", va="top", dy=0.6, fontsize=8.5)
    arrow(ax, (9, c[9]), (17, l[17]), color=RED, ls="dashed")
    ax.text(len(closes) / 2, h.max() + 1.0, "الخوف والطمع يشوّهان التنفيذ حتى مع تحليل صحيح", color=NAVY,
            fontsize=9.5, ha="center", fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h) + [h.max() + 1.4])
    save(fig, "fig-33-02")

# ============================================================ 33.6 Position sizing formula (dedicated)
def fig_33_03():
    fig, ax = plt.subplots(figsize=(8.6, 4.0), dpi=150)
    ax.set_xlim(0, 10); ax.set_ylim(0, 4); ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.text(5, 3.3, "حجم المركز = (رأس المال × نسبة المخاطرة) ÷ (مسافة الوقف × قيمة النقطة)", fontsize=12,
            color=NAVY, ha="center", fontweight="bold")
    boxes = [(0.6, "رأس المال\n10,000$", NAVY), (3.0, "نسبة المخاطرة\n1%", GOLD),
             (5.4, "مسافة الوقف\n50 نقطة", RED), (7.8, "حجم المركز\n2 لوت", GREEN)]
    for x, label, color in boxes:
        ax.add_patch(Rectangle((x, 1.0), 1.8, 1.3, facecolor=color, alpha=0.15, edgecolor=color, linewidth=1.8))
        ax.text(x + 0.9, 1.65, label, ha="center", va="center", fontsize=9.5, color=color, fontweight="bold")
    for x0 in [0.6, 3.0, 5.4]:
        ax.add_patch(FancyArrowPatch((x0 + 1.8, 1.65), (x0 + 2.4, 1.65), arrowstyle="-|>", color=GREY,
                                      linewidth=2, mutation_scale=14))
    save(fig, "fig-33-03")

# ============================================================ 33.9 RRR vs breakeven win rate (dedicated)
def fig_33_04():
    fig, ax = plt.subplots(figsize=(8.6, 4.4), dpi=150)
    fig.patch.set_facecolor("white")
    win_rates = np.array([70, 50, 40, 30])
    rrr = np.array([0.5, 1.0, 1.5, 2.5])
    bars = ax.bar([f"{w}%" for w in win_rates], rrr, color=GOLD_LIGHT, edgecolor=GOLD, width=0.5, zorder=3)
    for b, v in zip(bars, rrr):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.05, f"1:{v}", ha="center", fontsize=9.5, fontweight="bold", color=NAVY)
    ax.set_xlabel("نسبة النجاح")
    ax.set_ylabel("الحد الأدنى لـ RRR للتعادل تقريبًا")
    ax.grid(axis="y", color=GRID, zorder=0)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    save(fig, "fig-33-04")


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

# ============================================================ 24.3 Candlestick anatomy (dedicated)
def fig_24_05():
    fig, ax = plt.subplots(figsize=(6.4, 5.2), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 4); ax.set_ylim(0, 10); ax.axis("off")
    ax.plot([2, 2], [1.2, 2.6], color=GREEN, linewidth=2)
    ax.add_patch(Rectangle((1.6, 2.6), 0.8, 4.2, facecolor=GREEN, edgecolor=GREEN))
    ax.plot([2, 2], [6.8, 8.4], color=GREEN, linewidth=2)
    ax.annotate("الفتيل العلوي (أعلى سعر)", xy=(2, 8.0), xytext=(3.1, 9.2), fontsize=9.5, color=NAVY,
                ha="left", arrowprops=dict(arrowstyle="-|>", color=NAVY, linewidth=1.4))
    ax.annotate("جسم الشمعة (بين الافتتاح والإغلاق)", xy=(2.4, 4.7), xytext=(3.1, 5.6), fontsize=9.5, color=NAVY,
                ha="left", arrowprops=dict(arrowstyle="-|>", color=NAVY, linewidth=1.4))
    ax.annotate("الفتيل السفلي (أدنى سعر)", xy=(2, 1.8), xytext=(3.1, 1.0), fontsize=9.5, color=NAVY,
                ha="left", arrowprops=dict(arrowstyle="-|>", color=NAVY, linewidth=1.4))
    ax.text(2, 6.8, "إغلاق", color="white", fontsize=8.5, ha="center", va="bottom", fontweight="bold")
    ax.text(2, 2.6, "افتتاح", color="white", fontsize=8.5, ha="center", va="top", fontweight="bold")
    ax.set_title("تشريح شمعة صاعدة (Bullish Candle)", fontsize=11, color=NAVY, fontweight="bold")
    save(fig, "fig-24-05")

# ============================================================ 24.5-24.7 Renko, Kagi, Point & Figure (reference sheet)
def fig_24_06():
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.8), dpi=150)

    def renko(ax):
        rng = np.random.default_rng(2406)
        y = 0
        ys = [0]
        for i in range(10):
            step = rng.choice([-1, 1]) * 0.5
            color = GREEN if step > 0 else RED
            ax.add_patch(Rectangle((i, min(y, y + step)), 0.9, abs(step), facecolor=color, edgecolor=color))
            y += step
            ys.append(y)
        ax.set_xlim(-0.5, 10.5)
        ax.set_ylim(min(ys) - 0.5, max(ys) + 0.5)
        ax.set_title("رينكو (Renko)", fontsize=10, color=NAVY, fontweight="bold")

    def kagi(ax):
        pts_x = [0, 1, 1, 2, 2, 3, 3, 4]
        pts_y = [0, 0, 1.4, 1.4, 0.6, 0.6, 2.0, 2.0]
        ax.plot(pts_x, pts_y, color=NAVY, linewidth=2.4)
        ax.set_xlim(-0.5, 4.5)
        ax.set_ylim(-0.5, 2.5)
        ax.set_title("كاغي (Kagi)", fontsize=10, color=NAVY, fontweight="bold")

    def pnf(ax):
        rng = np.random.default_rng(2407)
        col_x = 0
        y = 0
        ys = [0]
        for i in range(6):
            up = rng.random() > 0.4
            marker = "x" if up else "o"
            color = GREEN if up else RED
            n = rng.integers(2, 5)
            for j in range(n):
                y += 1 if up else -1
                ax.text(col_x, y, marker, color=color, ha="center", va="center", fontsize=11, fontweight="bold")
                ys.append(y)
            col_x += 1
        ax.set_xlim(-1, 6)
        ax.set_ylim(min(ys) - 1, max(ys) + 1)
        ax.set_title("النقاط والأشكال (P&F)", fontsize=10, color=NAVY, fontweight="bold")

    for ax, fn in zip(axes, [renko, kagi, pnf]):
        fn(ax)
        for s in ax.spines.values(): s.set_visible(False)
        ax.set_xticks([]); ax.set_yticks([])
    fig.tight_layout(pad=1.0)
    save(fig, "fig-24-06")

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
# ============================================================ 26.1a Support (dedicated single concept)
def fig_26_07():
    fig, ax = new_ax(w=8.6, h=4.6)
    closes = regime_walk([
        (10, -0.55, 0.4), (2, 0.1, 0.2), (10, 0.6, 0.45),
        (10, -0.5, 0.4), (2, 0.1, 0.2), (12, 0.55, 0.5),
        (10, -0.45, 0.4), (2, 0.1, 0.2), (10, 0.6, 0.45),
    ], start=108, seed=2607)
    o, h, l, c = to_ohlc(closes, seed=2607)
    plot_candles(ax, o, h, l, c, width=0.55)
    level = min(l[9], l[9 + 2 + 10 + 10 + 2 - 1], l[-13]) + 0.15
    hline(ax, level, 0, len(closes) - 1, color=GREEN, lw=2.2, label="مستوى الدعم")
    for x, letter in zip([9, 33, 56], ["A", "B", "C"]):
        letter_point(ax, x, l[x] - 0.25, letter, color=GREEN, va="top", dy=0.9)
    ax.text(len(closes) / 2, ax.get_ylim()[0], "الدعم: مستوى يميل الطلب عنده لتجاوز العرض فيوقف الهبوط",
            color=GREEN, fontsize=9.5, ha="center", va="bottom", fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h), pad_frac=0.22)
    save(fig, "fig-26-07")

# ============================================================ 26.1b Resistance (dedicated single concept)
def fig_26_08():
    fig, ax = new_ax(w=8.6, h=4.6)
    closes = regime_walk([
        (10, 0.55, 0.4), (2, -0.1, 0.2), (10, -0.6, 0.45),
        (10, 0.5, 0.4), (2, -0.1, 0.2), (12, -0.55, 0.5),
        (10, 0.45, 0.4), (2, -0.1, 0.2), (10, -0.6, 0.45),
    ], start=92, seed=2608)
    o, h, l, c = to_ohlc(closes, seed=2608)
    plot_candles(ax, o, h, l, c, width=0.55)
    level = max(h[9], h[9 + 2 + 10 + 10 + 2 - 1], h[-13]) - 0.15
    hline(ax, level, 0, len(closes) - 1, color=RED, lw=2.2, label="مستوى المقاومة")
    for x, letter in zip([9, 33, 56], ["A", "B", "C"]):
        letter_point(ax, x, h[x] + 0.25, letter, color=RED, va="bottom", dy=0.9)
    ax.text(len(closes) / 2, ax.get_ylim()[1], "المقاومة: مستوى يميل العرض عنده لتجاوز الطلب فيوقف الصعود",
            color=RED, fontsize=9.5, ha="center", va="top", fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h), pad_frac=0.22)
    save(fig, "fig-26-08")

# ============================================================ 26.2 Four ways to identify S/R (reference sheet)
def fig_26_09():
    fig, axes = plt.subplots(2, 2, figsize=(10.5, 7), dpi=150)

    def swings(ax):
        closes = regime_walk([(10, 0.5, 0.4), (10, -0.5, 0.4), (10, 0.5, 0.4)], start=100, seed=2691)
        o, h, l, c = to_ohlc(closes, seed=2691)
        plot_candles(ax, o, h, l, c, width=0.5)
        hline(ax, h[9], 0, 29, color=RED, lw=1.6)
        hline(ax, l[19], 0, 29, color=GREEN, lw=1.6)
        ax.set_title("١. القمم والقيعان التاريخية", fontsize=10, color=NAVY, fontweight="bold")

    def ma(ax):
        closes = synth_walk(34, drift=0.3, vol=0.6, start=100, seed=2692)
        o, h, l, c = to_ohlc(closes, seed=2692)
        plot_candles(ax, o, h, l, c, width=0.5)
        ax.plot(rolling_mean(closes, 12), color=GOLD, linewidth=2.2)
        ax.set_title("٢. المتوسطات المتحركة", fontsize=10, color=NAVY, fontweight="bold")

    def tl(ax):
        closes = regime_walk([(16, 0.55, 0.35), (16, 0.35, 0.55)], start=100, seed=2693)
        o, h, l, c = to_ohlc(closes, seed=2693)
        plot_candles(ax, o, h, l, c, width=0.5)
        channel(ax, 0, 31, l[0] - 0.3, 0.42, 0)
        ax.set_title("٣. خطوط الاتجاه", fontsize=10, color=NAVY, fontweight="bold")

    def round_num(ax):
        closes = 100 + np.cumsum(np.random.default_rng(2694).normal(0, 0.35, 32))
        o, h, l, c = to_ohlc(closes, seed=2694)
        plot_candles(ax, o, h, l, c, width=0.5)
        hline(ax, 100, 0, 31, color=GOLD, lw=2.0)
        ax.set_title("٤. المستويات النفسية المستديرة", fontsize=10, color=NAVY, fontweight="bold")

    for ax, fn in zip(axes.flat, [swings, ma, tl, round_num]):
        fn(ax)
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        ax.set_xticks([])
    fig.tight_layout(pad=1.0)
    save(fig, "fig-26-09")

# ============================================================ 26.3 Round psychological numbers (dedicated)
def fig_26_10():
    fig, ax = new_ax(w=8.6, h=4.6)
    closes = regime_walk([
        (12, 0.1, 0.25), (3, 0.35, 0.15), (10, -0.3, 0.35),
        (3, 0.35, 0.15), (12, -0.1, 0.25),
    ], start=1.1955, seed=2610)
    closes = 1.19 + (closes - closes.min()) * 0.006
    o, h, l, c = to_ohlc(closes, seed=2610, wick=0.4)
    plot_candles(ax, o, h, l, c, width=0.55)
    hline(ax, 1.2000, 0, len(closes) - 1, color=GOLD, lw=2.2, label="1.2000 (رقم مستدير)")
    ax.set_ylabel("EUR/USD")
    ax.text(len(closes) / 2, ax.get_ylim()[1], "الأرقام المستديرة تجذب أوامر معلقة كثيفة → سيولة مكثفة",
            color=GOLD, fontsize=9.5, ha="center", va="top", fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h), pad_frac=0.25)
    save(fig, "fig-26-10")

# ============================================================ 26.5a Bounce strategy (dedicated)
def fig_26_11():
    fig, ax = new_ax(w=8.6, h=4.6)
    closes = regime_walk([(14, -0.5, 0.4), (3, 0.1, 0.2), (14, 0.65, 0.5)], start=108, seed=2611)
    o, h, l, c = to_ohlc(closes, seed=2611)
    plot_candles(ax, o, h, l, c, width=0.55)
    level = l[14:17].min() + 0.1
    hline(ax, level, 0, len(closes) - 1, color=GREEN, lw=2.0, label="دعم")
    marker_point(ax, 16, level - 0.2, color=NAVY, label="دخول شراء (ارتداد)", va="top", dy=0.9)
    arrow(ax, (17, c[17]), (30, c[30]), color=GREEN, label="هدف")
    ax.axhline(level - 1.0, color=RED, linestyle=":", linewidth=1.3)
    ax.text(2, level - 1.0, "وقف خسارة", color=RED, fontsize=8.5, va="top")
    set_ylim_pad(ax, list(l) + list(h) + [level - 1.4])
    save(fig, "fig-26-11")

# ============================================================ 26.5b Breakout strategy (dedicated)
def fig_26_12():
    fig, ax = new_ax(w=8.6, h=4.6)
    closes = regime_walk([(16, 0.05, 0.3), (4, 0.9, 0.35), (12, 0.6, 0.5)], start=100, seed=2612)
    o, h, l, c = to_ohlc(closes, seed=2612)
    plot_candles(ax, o, h, l, c, width=0.55)
    level = h[:16].max() + 0.1
    hline(ax, level, 0, len(closes) - 1, color=GOLD, lw=2.0, label="مقاومة")
    marker_point(ax, 17, h[17] + 0.2, color=NAVY, label="دخول شراء (اختراق)", va="bottom", dy=0.9)
    arrow(ax, (18, c[18]), (31, c[-1]), color=GREEN, label="هدف")
    ax.text(4, level + 1.6, "إغلاق واضح خارج المستوى + زخم", color=GOLD, fontsize=8.5, ha="left", fontweight="bold")
    set_ylim_pad(ax, list(l) + list(h) + [level + 2.0])
    save(fig, "fig-26-12")

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
    n1, n2, n3 = 34, 9, 9
    n = n1 + n2 + n3
    i1 = np.arange(n1)
    cup = -5.2 * np.exp(-((i1 - 17) ** 2) / 90)
    i2 = np.arange(n2)
    handle = cup[-1] - 1.0 * np.sin(i2 * 0.7) * np.linspace(1, 0.3, n2) - i2 * 0.1
    i3 = np.arange(n3)
    breakout = handle[-1] + i3 * 0.45
    closes = 105 + np.concatenate([cup, handle, breakout])
    o, h, l, c = to_ohlc(closes, seed=2803, wick=0.4)
    fig, ax = plt.subplots(figsize=(8.6, 4.6), dpi=150)
    fig.patch.set_facecolor("white")
    plot_candles(ax, o, h, l, c, width=0.55)
    rim = max(h[0], h[n1 - 1]) + 0.1
    hline(ax, rim, 0, n - 1, color=GREY, ls=":", lw=1.6, label="الحافة (مقاومة)")
    ax.text(n1 / 2, l[:n1].min() - 0.5, "الكوب (Cup)", color=NAVY, fontsize=10, ha="center", fontweight="bold")
    ax.text(n1 + n2 / 2, l[n1:n1 + n2].min() - 0.5, "المقبض (Handle)", color=GOLD, fontsize=10, ha="center", fontweight="bold")
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])
    set_ylim_pad(ax, list(l) + list(h) + [l[:n1].min() - 0.8], pad_frac=0.15)
    ax.set_title("الكوب والمقبض (Cup and Handle)", fontsize=11, color=NAVY, fontweight="bold")
    save(fig, "fig-28-03")

# ============================================================ 28.4 Double Bottom
def fig_28_04():
    n = 46
    def shape(i):
        return -3.3 * np.exp(-((i - 13) ** 2) / 22) - 3.3 * np.exp(-((i - 33) ** 2) / 22)
    fig, ax, o, h, l, c = _pattern_candles(shape, n=n, seed=2804, base=105)
    neck = max(h[18], h[28]) + 0.1
    hline(ax, neck, 0, n - 1, color=GOLD, lw=2.0, label="خط العنق (مقاومة)")
    letter_point(ax, 13, l[13] - 0.3, "القاع 1", color=RED, va="top", dy=0.4, fontsize=10.5)
    letter_point(ax, 33, l[33] - 0.3, "القاع 2", color=RED, va="top", dy=0.4, fontsize=10.5)
    ax.set_title("القاع المزدوج (Double Bottom)", fontsize=11, color=NAVY, fontweight="bold")
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

# ============================================================ 29.10 RSI overbought/oversold (dedicated)
def fig_29_06():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.6, 5.4), dpi=150, gridspec_kw={"height_ratios": [2, 1]})
    n = 40
    closes = 100 + np.cumsum(np.random.default_rng(2906).normal(0.15, 0.5, n))
    o, h, l, c = to_ohlc(closes, seed=2906)
    plot_candles(ax1, o, h, l, c, width=0.55)
    ax1.set_xticks([]); ax1.grid(axis="y", color=GRID)
    for s in ["top", "right"]: ax1.spines[s].set_visible(False)
    ax1.set_ylabel("السعر")
    r = rsi(closes)
    ax2.plot(r, color=GOLD, linewidth=2)
    ax2.axhline(70, color=RED, linestyle="--", linewidth=1.3)
    ax2.axhline(30, color=GREEN, linestyle="--", linewidth=1.3)
    ax2.fill_between(np.arange(n), 70, 100, color=RED, alpha=0.08)
    ax2.fill_between(np.arange(n), 0, 30, color=GREEN, alpha=0.08)
    ax2.text(n - 1, 72, "تشبع شرائي", color=RED, fontsize=8.5, ha="right", fontweight="bold")
    ax2.text(n - 1, 24, "تشبع بيعي", color=GREEN, fontsize=8.5, ha="right", fontweight="bold")
    ax2.set_ylabel("RSI")
    ax2.set_ylim(0, 100)
    ax2.set_xticks([])
    for s in ["top", "right"]: ax2.spines[s].set_visible(False)
    fig.tight_layout(pad=0.6)
    save(fig, "fig-29-06")

# ============================================================ 29.11 Stochastic (dedicated)
def fig_29_07():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.6, 5.4), dpi=150, gridspec_kw={"height_ratios": [2, 1]})
    n = 40
    closes = 100 + 3 * np.sin(np.arange(n) / 4) + np.random.default_rng(2907).normal(0, 0.3, n)
    o, h, l, c = to_ohlc(closes, seed=2907)
    plot_candles(ax1, o, h, l, c, width=0.55)
    ax1.set_xticks([]); ax1.grid(axis="y", color=GRID)
    for s in ["top", "right"]: ax1.spines[s].set_visible(False)
    ax1.set_ylabel("السعر")
    k = 50 + 45 * np.sin(np.arange(n) / 3.2)
    dline = rolling_mean(k, 3)
    ax2.plot(k, color=NAVY, linewidth=1.8, label="%K")
    ax2.plot(dline, color=GOLD, linewidth=1.6, linestyle="--", label="%D")
    ax2.axhline(80, color=RED, linestyle=":", linewidth=1.2)
    ax2.axhline(20, color=GREEN, linestyle=":", linewidth=1.2)
    ax2.set_ylabel("ستوكاستيك")
    ax2.set_ylim(0, 100)
    ax2.set_xticks([])
    ax2.legend(frameon=False, fontsize=8.5, loc="upper right")
    for s in ["top", "right"]: ax2.spines[s].set_visible(False)
    fig.tight_layout(pad=0.6)
    save(fig, "fig-29-07")

# ============================================================ 29.13 Ichimoku Cloud (dedicated, simplified)
def fig_29_08():
    fig, ax = new_ax(w=8.6, h=4.8)
    n = 50
    closes = synth_walk(n, drift=0.35, vol=0.5, start=100, seed=2908)
    o, h, l, c = to_ohlc(closes, seed=2908)
    plot_candles(ax, o, h, l, c, width=0.5)
    tenkan = rolling_mean(closes, 5)
    kijun = rolling_mean(closes, 12)
    span_a = (tenkan + kijun) / 2 + 2.5
    span_b = rolling_mean(closes, 20) + 2.5
    ax.plot(tenkan, color=RED, linewidth=1.4, label="خط التحويل (Tenkan)")
    ax.plot(kijun, color=NAVY, linewidth=1.6, label="خط الأساس (Kijun)")
    ax.fill_between(np.arange(n), span_a, span_b, color=GOLD_LIGHT, alpha=0.3,
                     where=(span_a >= span_b), interpolate=True)
    ax.fill_between(np.arange(n), span_a, span_b, color="#B0C4DE", alpha=0.3,
                     where=(span_a < span_b), interpolate=True)
    ax.text(n / 2, max(span_a.max(), span_b.max()) + 1.5, "السحابة المستقبلية (Kumo)", color=GOLD,
            fontsize=9, ha="center", fontweight="bold")
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    set_ylim_pad(ax, list(l) + list(h) + list(span_a) + list(span_b) + [max(span_a.max(), span_b.max()) + 2])
    save(fig, "fig-29-08")

# ============================================================ 29.15 Fibonacci extension (dedicated)
def fig_29_09():
    fig, ax = new_ax(w=8.6, h=4.6)
    up1 = synth_walk(16, drift=0.65, vol=0.5, start=100, seed=2909)
    pull = synth_walk(10, drift=-0.35, vol=0.4, start=up1[-1], seed=29091)
    ext = synth_walk(14, drift=0.7, vol=0.5, start=pull[-1], seed=29092)
    closes = np.concatenate([up1, pull, ext])
    o, h, l, c = to_ohlc(closes, seed=2909)
    plot_candles(ax, o, h, l, c, width=0.5)
    swing_low, swing_high = l[:16].min(), h[:16].max()
    rng = swing_high - swing_low
    levels = {"100%": swing_high, "127%": swing_low + rng * 1.27, "161.8%": swing_low + rng * 1.618}
    for label, y in levels.items():
        hline(ax, y, 16, len(closes) - 1, color=GOLD, ls=":", lw=1.2, label=label, label_side="right")
    set_ylim_pad(ax, list(l) + list(h) + [levels["161.8%"] + 1.0])
    ax.set_title("امتداد فيبوناتشي: أهداف محتملة بعد تجاوز نقطة سابقة", fontsize=10.5, color=NAVY, fontweight="bold")
    save(fig, "fig-29-09")

# ============================================================ 29.17 ATR-based stop distance (dedicated)
def fig_29_10():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.6, 5.4), dpi=150, gridspec_kw={"height_ratios": [2, 1]})
    n = 40
    vol = np.concatenate([np.full(20, 0.3), np.linspace(0.3, 1.2, 10), np.full(10, 1.1)])
    closes = 100 + np.cumsum(np.random.default_rng(2910).normal(0.1, vol))
    o, h, l, c = to_ohlc(closes, seed=2910)
    plot_candles(ax1, o, h, l, c, width=0.55)
    atr_est = np.array([np.mean(h[max(0, i - 14):i + 1] - l[max(0, i - 14):i + 1]) for i in range(n)])
    entry_x = 30
    stop_narrow = c[entry_x] - atr_est[10] * 1.5
    stop_wide = c[entry_x] - atr_est[entry_x] * 1.5
    ax1.axhline(stop_narrow, color=RED, linestyle=":", linewidth=1.3)
    ax1.axhline(stop_wide, color=GREEN, linestyle="--", linewidth=1.6)
    ax1.text(n - 1, stop_narrow, "وقف ثابت (ضيق جدًا هنا)", color=RED, fontsize=8, ha="right", va="bottom")
    ax1.text(n - 1, stop_wide, "وقف مبني على ATR الحالي", color=GREEN, fontsize=8, ha="right", va="top")
    ax1.set_xticks([]); ax1.grid(axis="y", color=GRID)
    for s in ["top", "right"]: ax1.spines[s].set_visible(False)
    ax1.set_ylabel("السعر")
    ax2.plot(atr_est, color=NAVY, linewidth=2)
    ax2.set_ylabel("ATR")
    ax2.set_xticks([])
    for s in ["top", "right"]: ax2.spines[s].set_visible(False)
    fig.tight_layout(pad=0.6)
    save(fig, "fig-29-10")

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

# ============================================================ 30.2 Price-volume scenarios (dedicated)
def fig_30_03():
    fig = plt.figure(figsize=(9.4, 6.2), dpi=150)
    fig.patch.set_facecolor("white")

    def panel(ax_pair, drift, vol_pattern, title, color):
        ax1, ax2 = ax_pair
        n = 20
        closes = 100 + np.cumsum(np.full(n, drift))
        o, h, l, c = to_ohlc(closes, seed=abs(hash(title)) % 1000, wick=0.3)
        plot_candles(ax1, o, h, l, c, width=0.55)
        ax1.set_xticks([]); ax1.set_yticks([])
        for s in ax1.spines.values(): s.set_visible(False)
        ax1.set_title(title, fontsize=9, color=color, fontweight="bold")
        vols = vol_pattern(n)
        ax2.bar(np.arange(n), vols, color=color, width=0.7)
        ax2.set_xticks([]); ax2.set_yticks([])
        for s in ax2.spines.values(): s.set_visible(False)

    gs = fig.add_gridspec(4, 2, height_ratios=[1.4, 0.6, 1.4, 0.6], hspace=0.15, wspace=0.2)
    specs = [
        (0.5, lambda n: np.linspace(1, 3, n), "سعر صاعد + حجم صاعد: اتجاه قوي وموثوق", GREEN),
        (0.5, lambda n: np.linspace(3, 1, n), "سعر صاعد + حجم هابط: اتجاه ضعيف", GOLD),
        (-0.5, lambda n: np.linspace(1, 3, n), "سعر هابط + حجم صاعد: اتجاه هابط قوي", RED),
        (-0.5, lambda n: np.linspace(3, 1, n), "سعر هابط + حجم هابط: اتجاه هابط ضعيف", GOLD),
    ]
    for i, (drift, vol_pattern, title, color) in enumerate(specs):
        row, col = divmod(i, 2)
        ax1 = fig.add_subplot(gs[row * 2, col])
        ax2 = fig.add_subplot(gs[row * 2 + 1, col])
        panel((ax1, ax2), drift, vol_pattern, title, color)
    save(fig, "fig-30-03")

# ============================================================ 30.3a OBV (dedicated)
def fig_30_04():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.6, 5.4), dpi=150, gridspec_kw={"height_ratios": [1.6, 1]})
    n = 34
    closes = 100 + 0.3 * np.arange(n) + np.random.default_rng(3004).normal(0, 0.6, n)
    o, h, l, c = to_ohlc(closes, seed=3004)
    plot_candles(ax1, o, h, l, c, width=0.55)
    ax1.set_xticks([]); ax1.grid(axis="y", color=GRID)
    for s in ["top", "right"]: ax1.spines[s].set_visible(False)
    ax1.set_ylabel("السعر")
    vols = np.random.default_rng(3005).uniform(5, 15, n)
    vols[20:] += np.linspace(0, 8, n - 20)
    directions = np.sign(np.diff(closes, prepend=closes[0]))
    obv = np.cumsum(directions * vols)
    ax2.plot(obv, color=GOLD, linewidth=2.2)
    ax2.set_ylabel("OBV")
    ax2.set_xticks([])
    for s in ["top", "right"]: ax2.spines[s].set_visible(False)
    fig.tight_layout(pad=0.6)
    save(fig, "fig-30-04")

# ============================================================ 30.3b VWAP (dedicated)
def fig_30_05():
    fig, ax = new_ax(w=8.6, h=4.6)
    n = 40
    closes = 100 + np.cumsum(np.random.default_rng(3006).normal(0.05, 0.4, n))
    o, h, l, c = to_ohlc(closes, seed=3006)
    plot_candles(ax, o, h, l, c, width=0.55)
    vols = np.random.default_rng(3007).uniform(5, 20, n)
    vwap = np.cumsum(closes * vols) / np.cumsum(vols)
    ax.plot(vwap, color=GOLD, linewidth=2.2, label="VWAP")
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    set_ylim_pad(ax, list(l) + list(h))
    save(fig, "fig-30-05")

# ============================================================ 30.4 Climax volume vs dry-up (dedicated)
def fig_30_06():
    fig = plt.figure(figsize=(10, 5.2), dpi=150)
    fig.patch.set_facecolor("white")
    gs = fig.add_gridspec(2, 2, height_ratios=[1.6, 1], hspace=0.15, wspace=0.25)

    up = synth_walk(20, drift=0.5, vol=0.4, start=100, seed=3008)
    climax = synth_walk(4, drift=1.3, vol=0.3, start=up[-1], seed=30081)
    closes1 = np.concatenate([up, climax])
    o1, h1, l1, c1 = to_ohlc(closes1, seed=3008, wick=0.7)
    vols1 = np.concatenate([np.random.default_rng(3009).uniform(4, 8, 20), [18, 22, 20, 15]])

    pull = synth_walk(20, drift=-0.05, vol=0.3, start=100, seed=3010)
    o2, h2, l2, c2 = to_ohlc(pull, seed=3010, wick=0.4)
    vols2 = np.random.default_rng(3011).uniform(5, 10, 20) - np.linspace(0, 6, 20)
    vols2 = np.clip(vols2, 1, None)

    specs = [(o1, h1, l1, c1, vols1, "قمة حجم عند انعكاس (Climax Volume)", RED),
             (o2, h2, l2, c2, vols2, "جفاف الحجم أثناء تصحيح (Volume Dry-up)", GOLD)]
    for col, (o, h, l, c, vols, title, color) in enumerate(specs):
        ax1 = fig.add_subplot(gs[0, col])
        ax2 = fig.add_subplot(gs[1, col])
        plot_candles(ax1, o, h, l, c, width=0.55)
        ax1.set_xticks([]); ax1.set_yticks([])
        for s in ax1.spines.values(): s.set_visible(False)
        ax1.set_title(title, fontsize=9.5, color=color, fontweight="bold")
        ax2.bar(np.arange(len(vols)), vols, color=color, width=0.7)
        ax2.set_xticks([]); ax2.set_yticks([])
        for s in ax2.spines.values(): s.set_visible(False)
    save(fig, "fig-30-06")


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


def _trendline_through(ax, p1, p2, x0, x1, color=NAVY, lw=2.0, ls="-"):
    """Draws a straight line through two real chart points (p1, p2) and
    extends it across [x0, x1] -- this is how trendlines/wedge & triangle
    boundaries are actually drawn in technical analysis: anchored on two real
    swing points, not an abstract formula."""
    (xa, ya), (xb, yb) = p1, p2
    slope = (yb - ya) / (xb - xa)
    y0 = ya + slope * (x0 - xa)
    y1 = ya + slope * (x1 - xa)
    ax.plot([x0, x1], [y0, y1], color=color, linewidth=lw, linestyle=ls, zorder=4)

def _pattern_candles(shape, n=60, seed=0, base=100.0, width=0.6, wick=0.55, figsize=(8.6, 4.6)):
    """Renders a chart pattern as an actual realistic candlestick chart: the
    pattern's shape is sampled at n integer bars, then passed through the
    same synthetic-OHLC machinery used everywhere else in the book, so every
    pattern figure is a real-looking price chart (not an idealized smooth
    curve) -- matching the reference textbook pages (Murrey Math / Dow
    Theory) the annotations are modeled on."""
    fig, ax = plt.subplots(figsize=figsize, dpi=150)
    fig.patch.set_facecolor("white")
    i = np.arange(n)
    closes = base + shape(i)
    o, h, l, c = to_ohlc(closes, seed=seed, wick=wick)
    plot_candles(ax, o, h, l, c, width=width)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])
    set_ylim_pad(ax, list(l) + list(h), pad_frac=0.3)
    return fig, ax, o, h, l, c

# ============================================================ 28.5 Head & Shoulders (dedicated definition)
def fig_28_05():
    n = 60
    def shape(i):
        return (2.2 * np.exp(-((i - 12) ** 2) / 22) + 4.2 * np.exp(-((i - 30) ** 2) / 30)
                + 2.2 * np.exp(-((i - 48) ** 2) / 22) - np.linspace(0, 1.2, n))
    fig, ax, o, h, l, c = _pattern_candles(shape, n=n, seed=2805, base=100)
    neck = min(l[6], l[54]) - 0.1
    hline(ax, neck, 0, n - 1, color=GOLD, lw=2.0, label="خط الرقبة (Neckline)")
    letter_point(ax, 12, h[12] + 0.3, "الكتف الأيسر", color=NAVY, va="bottom", dy=0.5, circle=False, fontsize=9.5)
    letter_point(ax, 30, h[30] + 0.3, "الرأس", color=RED, va="bottom", dy=0.5, circle=False, fontsize=10.5)
    letter_point(ax, 48, h[48] + 0.3, "الكتف الأيمن", color=NAVY, va="bottom", dy=0.5, circle=False, fontsize=9.5)
    ax.set_title("الرأس والكتفين (Head & Shoulders) — نمط انعكاسي هابط", fontsize=11, color=NAVY, fontweight="bold")
    save(fig, "fig-28-05")

# ============================================================ 28.6 Inverse Head & Shoulders (dedicated)
def fig_28_06():
    n = 60
    def shape(i):
        return -(2.2 * np.exp(-((i - 12) ** 2) / 22) + 4.2 * np.exp(-((i - 30) ** 2) / 30)
                  + 2.2 * np.exp(-((i - 48) ** 2) / 22)) + np.linspace(0, 1.2, n)
    fig, ax, o, h, l, c = _pattern_candles(shape, n=n, seed=2806, base=105)
    neck = max(h[6], h[54]) + 0.1
    hline(ax, neck, 0, n - 1, color=GOLD, lw=2.0, label="خط الرقبة (Neckline)")
    letter_point(ax, 12, l[12] - 0.3, "الكتف الأيسر", color=NAVY, va="top", dy=0.5, circle=False, fontsize=9.5)
    letter_point(ax, 30, l[30] - 0.3, "الرأس", color=GREEN, va="top", dy=0.5, circle=False, fontsize=10.5)
    letter_point(ax, 48, l[48] - 0.3, "الكتف الأيمن", color=NAVY, va="top", dy=0.5, circle=False, fontsize=9.5)
    ax.set_title("الرأس والكتفين المقلوب (Inverse H&S) — نمط انعكاسي صاعد", fontsize=11, color=NAVY, fontweight="bold")
    save(fig, "fig-28-06")

# ============================================================ 28.7 Triple Top (dedicated)
def fig_28_07():
    n = 56
    def shape(i):
        return (3.4 * np.exp(-((i - 9) ** 2) / 20) + 3.6 * np.exp(-((i - 27) ** 2) / 20)
                + 3.3 * np.exp(-((i - 45) ** 2) / 20))
    fig, ax, o, h, l, c = _pattern_candles(shape, n=n, seed=2807, base=100)
    support = min(l[17], l[35]) - 0.1
    hline(ax, support, 0, n - 1, color=GOLD, lw=2.0, label="الدعم")
    for xt, lab in zip([9, 27, 45], ["1", "2", "3"]):
        letter_point(ax, xt, h[xt] + 0.3, lab, color=RED, va="bottom", dy=0.4, fontsize=11)
    ax.set_title("القمة الثلاثية (Triple Top) — نمط انعكاسي هابط", fontsize=11, color=NAVY, fontweight="bold")
    save(fig, "fig-28-07")

# ============================================================ 28.8 Triple Bottom (dedicated)
def fig_28_08():
    n = 56
    def shape(i):
        return -(3.4 * np.exp(-((i - 9) ** 2) / 20) + 3.6 * np.exp(-((i - 27) ** 2) / 20)
                  + 3.3 * np.exp(-((i - 45) ** 2) / 20))
    fig, ax, o, h, l, c = _pattern_candles(shape, n=n, seed=2808, base=106)
    resist = max(h[17], h[35]) + 0.1
    hline(ax, resist, 0, n - 1, color=GOLD, lw=2.0, label="المقاومة")
    for xt, lab in zip([9, 27, 45], ["1", "2", "3"]):
        letter_point(ax, xt, l[xt] - 0.3, lab, color=GREEN, va="top", dy=0.4, fontsize=11)
    ax.set_title("القاع الثلاثي (Triple Bottom) — نمط انعكاسي صاعد", fontsize=11, color=NAVY, fontweight="bold")
    save(fig, "fig-28-08")

# ============================================================ 28.9 Rising Wedge (dedicated)
def fig_28_09():
    n = 46
    closes = regime_walk([(6, 0.5, 0.3), (6, -0.35, 0.25), (6, 0.4, 0.25), (6, -0.3, 0.2),
                           (6, 0.35, 0.2), (6, -0.25, 0.18), (6, 0.3, 0.18), (4, -0.2, 0.15)],
                          start=100, seed=2809)
    o, h, l, c = to_ohlc(closes, seed=2809, wick=0.4)
    fig, ax = plt.subplots(figsize=(8.6, 4.6), dpi=150)
    fig.patch.set_facecolor("white")
    plot_candles(ax, o, h, l, c, width=0.55)
    _trendline_through(ax, (5, h[5]), (41, h[41]), 2, 44, color=NAVY, lw=2.0)
    _trendline_through(ax, (11, l[11]), (45, l[45]), 2, 44, color=NAVY, lw=2.0)
    for x, letter in zip([5, 17, 29, 41], ["A", "B", "C", "D"]):
        letter_point(ax, x, h[x] + 0.25, letter, color=NAVY, va="bottom", dy=0.35, fontsize=9.5)
    ax.text(n / 2, h.max() + 1.0, "احتمال انعكاس هبوطي رغم ميل النمط للأعلى", color=RED, fontsize=9.5,
            ha="center", fontweight="bold")
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])
    set_ylim_pad(ax, list(l) + list(h) + [h.max() + 1.3], pad_frac=0.1)
    ax.set_title("الوتد الصاعد (Rising Wedge) — نمط انعكاسي هابط", fontsize=11, color=NAVY, fontweight="bold")
    save(fig, "fig-28-09")

# ============================================================ 28.10 Falling Wedge (dedicated)
def fig_28_10():
    n = 46
    closes = regime_walk([(6, -0.5, 0.3), (6, 0.35, 0.25), (6, -0.4, 0.25), (6, 0.3, 0.2),
                           (6, -0.35, 0.2), (6, 0.25, 0.18), (6, -0.3, 0.18), (4, 0.2, 0.15)],
                          start=106, seed=2810)
    o, h, l, c = to_ohlc(closes, seed=2810, wick=0.4)
    fig, ax = plt.subplots(figsize=(8.6, 4.6), dpi=150)
    fig.patch.set_facecolor("white")
    plot_candles(ax, o, h, l, c, width=0.55)
    _trendline_through(ax, (5, l[5]), (41, l[41]), 2, 44, color=NAVY, lw=2.0)
    _trendline_through(ax, (11, h[11]), (45, h[45]), 2, 44, color=NAVY, lw=2.0)
    for x, letter in zip([5, 17, 29, 41], ["A", "B", "C", "D"]):
        letter_point(ax, x, l[x] - 0.25, letter, color=NAVY, va="top", dy=0.35, fontsize=9.5)
    ax.text(n / 2, l.min() - 1.0, "احتمال انعكاس صعودي رغم ميل النمط للأسفل", color=GREEN, fontsize=9.5,
            ha="center", fontweight="bold")
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])
    set_ylim_pad(ax, list(l) + list(h) + [l.min() - 1.3], pad_frac=0.1)
    ax.set_title("الوتد الهابط (Falling Wedge) — نمط انعكاسي صاعد", fontsize=11, color=NAVY, fontweight="bold")
    save(fig, "fig-28-10")

# ============================================================ 28.11 Symmetrical Triangle (dedicated)
def fig_28_11():
    n = 42
    closes = regime_walk([(5, 0.55, 0.3), (5, -0.6, 0.3), (5, 0.45, 0.28), (5, -0.5, 0.28),
                           (5, 0.35, 0.22), (5, -0.4, 0.22), (5, 0.25, 0.18), (7, -0.05, 0.15)],
                          start=100, seed=2811)
    o, h, l, c = to_ohlc(closes, seed=2811, wick=0.4)
    fig, ax = plt.subplots(figsize=(8.6, 4.6), dpi=150)
    fig.patch.set_facecolor("white")
    plot_candles(ax, o, h, l, c, width=0.55)
    _trendline_through(ax, (4, h[4]), (34, h[34]), 1, 40, color=RED, lw=2.0)
    _trendline_through(ax, (9, l[9]), (29, l[29]), 1, 40, color=GREEN, lw=2.0)
    ax.text(n / 2, h.max() + 1.1, "تضيّق تدريجي: قمم أدنى فأدنى وقيعان أعلى فأعلى", color=NAVY, fontsize=9.5,
            ha="center", fontweight="bold")
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])
    set_ylim_pad(ax, list(l) + list(h) + [h.max() + 1.4], pad_frac=0.1)
    ax.set_title("المثلث المتماثل (Symmetrical Triangle) — استمراري أو انعكاسي حسب الاختراق", fontsize=10.5, color=NAVY, fontweight="bold")
    save(fig, "fig-28-11")

# ============================================================ 28.12 Ascending Triangle (dedicated)
def fig_28_12():
    n = 40
    top = 106.0
    closes = np.array([top - 5 + (i % 8) * 0.6 + i * 0.05 for i in range(n)]) + \
        np.random.default_rng(2812).normal(0, 0.15, n)
    closes = np.minimum(closes, top - 0.05 * (n - np.arange(n)))
    o, h, l, c = to_ohlc(closes, seed=2812, wick=0.35)
    fig, ax = plt.subplots(figsize=(8.6, 4.6), dpi=150)
    fig.patch.set_facecolor("white")
    plot_candles(ax, o, h, l, c, width=0.55)
    hline(ax, top, 0, n - 1, color=RED, lw=2.0, label="مقاومة أفقية ثابتة")
    ax.plot([0, n - 1], [l.min(), h[-1] - 0.3], color=GREEN, linewidth=2.0)
    ax.text(2, l.min() + 0.3, "دعم صاعد تدريجيًا", color=GREEN, fontsize=9, ha="left", fontweight="bold")
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])
    set_ylim_pad(ax, list(l) + list(h) + [top + 0.6], pad_frac=0.12)
    ax.set_title("المثلث الصاعد (Ascending Triangle) — يميل للاختراق صعودًا", fontsize=11, color=NAVY, fontweight="bold")
    save(fig, "fig-28-12")

# ============================================================ 28.13 Descending Triangle (dedicated)
def fig_28_13():
    n = 40
    bot = 96.0
    closes = np.array([bot + 5 - (i % 8) * 0.6 - i * 0.05 for i in range(n)]) + \
        np.random.default_rng(2813).normal(0, 0.15, n)
    closes = np.maximum(closes, bot + 0.05 * (n - np.arange(n)))
    o, h, l, c = to_ohlc(closes, seed=2813, wick=0.35)
    fig, ax = plt.subplots(figsize=(8.6, 4.6), dpi=150)
    fig.patch.set_facecolor("white")
    plot_candles(ax, o, h, l, c, width=0.55)
    hline(ax, bot, 0, n - 1, color=GREEN, lw=2.0, label="دعم أفقي ثابت")
    ax.plot([0, n - 1], [h.max(), l[-1] + 0.3], color=RED, linewidth=2.0)
    ax.text(2, h.max() - 0.3, "مقاومة هابطة تدريجيًا", color=RED, fontsize=9, ha="left", fontweight="bold")
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])
    set_ylim_pad(ax, list(l) + list(h) + [bot - 0.6], pad_frac=0.12)
    ax.set_title("المثلث الهابط (Descending Triangle) — يميل للاختراق هبوطًا", fontsize=11, color=NAVY, fontweight="bold")
    save(fig, "fig-28-13")

# ============================================================ 28.14 Flag (dedicated)
def fig_28_14():
    pole = synth_walk(16, drift=0.75, vol=0.35, start=100, seed=28141)
    flag = synth_walk(14, drift=-0.18, vol=0.35, start=pole[-1], seed=28142)
    cont = synth_walk(16, drift=0.7, vol=0.4, start=flag[-1], seed=28143)
    closes = np.concatenate([pole, flag, cont])
    n = len(closes)
    o, h, l, c = to_ohlc(closes, seed=2814, wick=0.4)
    fig, ax = plt.subplots(figsize=(8.6, 4.6), dpi=150)
    fig.patch.set_facecolor("white")
    plot_candles(ax, o, h, l, c, width=0.55)
    channel(ax, 16, 30, h[16:30].max() + 0.1, -0.11, -(h[16:30].max() - l[16:30].min() + 0.3), color=GOLD, lw=2.0)
    ax.text(8, l[:16].min() - 0.6, "العمود (Pole)", color=GREEN, fontsize=9.5, ha="center", fontweight="bold")
    ax.text(23, h[16:30].max() + 1.0, "العلم (Flag)", color=GOLD, fontsize=9.5, ha="center", fontweight="bold")
    ax.text(39, c[-1], "استمرار الاتجاه", color=GREEN, fontsize=9.5, ha="center", fontweight="bold")
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])
    set_ylim_pad(ax, list(l) + list(h) + [h[16:30].max() + 1.3, l[:16].min() - 0.9], pad_frac=0.08)
    ax.set_title("العلم (Flag) — نمط استمراري", fontsize=11, color=NAVY, fontweight="bold")
    save(fig, "fig-28-14")

# ============================================================ 28.15 Pennant (dedicated)
def fig_28_15():
    pole = synth_walk(16, drift=0.75, vol=0.35, start=100, seed=28151)
    n2 = 14
    mid = (pole[-1] + pole[-1] - 1.6) / 2
    upper = pole[-1] - np.arange(n2) * 0.06
    lower = pole[-1] - 1.6 + np.arange(n2) * 0.09
    pennant = (upper + lower) / 2 + np.random.default_rng(28152).normal(0, 0.12, n2)
    cont = synth_walk(16, drift=0.7, vol=0.4, start=pennant[-1], seed=28153)
    closes = np.concatenate([pole, pennant, cont])
    o, h, l, c = to_ohlc(closes, seed=2815, wick=0.4)
    fig, ax = plt.subplots(figsize=(8.6, 4.6), dpi=150)
    fig.patch.set_facecolor("white")
    plot_candles(ax, o, h, l, c, width=0.55)
    ax.plot([16, 16 + n2 - 1], [upper[0] + 0.2, upper[-1] + 0.2], color=GOLD, linewidth=2.0)
    ax.plot([16, 16 + n2 - 1], [lower[0] - 0.2, lower[-1] - 0.2], color=GOLD, linewidth=2.0)
    ax.text(8, pole.min() - 0.6, "العمود (Pole)", color=GREEN, fontsize=9.5, ha="center", fontweight="bold")
    ax.text(23, upper[0] + 0.9, "الراية (Pennant)", color=GOLD, fontsize=9.5, ha="center", fontweight="bold")
    ax.text(39, c[-1], "استمرار الاتجاه", color=GREEN, fontsize=9.5, ha="center", fontweight="bold")
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])
    set_ylim_pad(ax, list(l) + list(h) + [upper[0] + 1.2, pole.min() - 0.9], pad_frac=0.08)
    ax.set_title("الراية (Pennant) — نمط استمراري", fontsize=11, color=NAVY, fontweight="bold")
    save(fig, "fig-28-15")

# ============================================================ 28.16 Rectangle (dedicated)
def fig_28_16():
    n = 40
    top, bot = 103.4, 100.6
    i = np.arange(n)
    closes = (top + bot) / 2 + (top - bot) / 2 * 0.85 * np.sin(i * 0.85) + \
        np.random.default_rng(2816).normal(0, 0.12, n)
    o, h, l, c = to_ohlc(closes, seed=2816, wick=0.35)
    fig, ax = plt.subplots(figsize=(8.6, 4.6), dpi=150)
    fig.patch.set_facecolor("white")
    plot_candles(ax, o, h, l, c, width=0.55)
    hline(ax, top, 0, n - 1, color=RED, lw=2.0, label="مقاومة")
    hline(ax, bot, 0, n - 1, color=GREEN, lw=2.0, label="دعم")
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])
    set_ylim_pad(ax, [bot - 0.6] + [top + 0.6] + list(l) + list(h), pad_frac=0.08)
    ax.set_title("المستطيل (Rectangle) — تذبذب أفقي بين دعم ومقاومة متوازيين", fontsize=11, color=NAVY, fontweight="bold")
    save(fig, "fig-28-16")

# ============================================================ 28.17 Double Top (dedicated)
def fig_28_17():
    n = 46
    def shape(i):
        return 3.3 * np.exp(-((i - 13) ** 2) / 22) + 3.3 * np.exp(-((i - 33) ** 2) / 22)
    fig, ax, o, h, l, c = _pattern_candles(shape, n=n, seed=2817, base=100)
    neck = min(l[18], l[28]) - 0.1
    hline(ax, neck, 0, n - 1, color=GOLD, lw=2.0, label="خط العنق (Neckline)")
    letter_point(ax, 13, h[13] + 0.3, "القمة 1", color=RED, va="bottom", dy=0.4, fontsize=10.5)
    letter_point(ax, 33, h[33] + 0.3, "القمة 2", color=RED, va="bottom", dy=0.4, fontsize=10.5)
    ax.set_title("القمة المزدوجة (Double Top) — نمط انعكاسي هابط", fontsize=11, color=NAVY, fontweight="bold")
    save(fig, "fig-28-17")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("fig_")]
    for fn in fns:
        fn()
        print("generated", fn.__name__)
    print(f"\nTotal figures: {len(fns)}")
