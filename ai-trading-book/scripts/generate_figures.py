# -*- coding: utf-8 -*-
"""Figure generator for 'AI in Trading'. Every model-result figure is produced
by actually running the analysis on REAL historical market data (Yahoo Finance
OHLCV bundled with backtesting.py: GOOG daily 2004-2013, EURUSD hourly)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, FancyArrowPatch
from figlib import (NAVY, NAVY_DEEP, GOLD, GOLD_LIGHT, CREAM, GREEN, RED, GREY,
                    GRID, save, new_ax, arrow, set_ylim_pad)

BLUE = "#2563EB"

from backtesting.test import GOOG, EURUSD  # real Yahoo Finance OHLCV


def _box(ax, x, y, w, h, label, color, tcolor="white", fs=10):
    ax.add_patch(mpatches.FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                 boxstyle="round,pad=0.06,rounding_size=0.12",
                 facecolor=color, edgecolor="none", zorder=3))
    ax.text(x, y, label, fontsize=fs, color=tcolor, fontweight="bold",
            ha="center", va="center", zorder=4)


# ============================================================ 1.1 AI fields map
def fig_01_01():
    fig, ax = plt.subplots(figsize=(9.4, 5.2), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")
    _box(ax, 5, 5.3, 4.2, 0.95, "الذكاء الاصطناعي (AI)", NAVY_DEEP, fs=12)
    fields = [(1.7, "التعلم الآلي\nMachine Learning", NAVY, "تصنيف · انحدار · تجميع\n(الأجزاء 3)"),
              (4.0, "التعلم العميق\nDeep Learning", GOLD, "شبكات عصبية · LSTM\nTransformers (الجزء 4)"),
              (6.3, "معالجة اللغة\nNLP", GREEN, "تحليل مشاعر · LLMs\n(الجزء 5)"),
              (8.6, "التعلم المعزز\nRL", RED, "وكلاء تداول\n(الجزء 6)")]
    for x, title, color, sub in fields:
        arrow(ax, (5, 4.8), (x, 3.75), color=GREY, lw=1.6)
        _box(ax, x, 3.2, 2.1, 1.0, title, color, fs=9.5)
        ax.text(x, 2.2, sub, fontsize=8.5, color="#4B5563", ha="center", va="top")
    ax.text(5, 0.7, "كل مجال يخدم مرحلة مختلفة من نظام التداول الذكي — وستتعلمها كلها بالترتيب في هذا الكتاب",
            fontsize=9.5, color=NAVY, ha="center", fontweight="bold")
    save(fig, "fig-01-01")


# ============================================================ 1.2 REAL overfitting demo on GOOG
def fig_01_02():
    """Fit deg-1 and deg-12 polynomials on 60 real GOOG closes, then show how
    each extrapolates over the NEXT 20 real days. Actually computed."""
    closes = GOOG.Close.values
    n_fit, n_test = 60, 20
    seg = closes[700:700 + n_fit + n_test]
    x_fit = np.arange(n_fit); y_fit = seg[:n_fit]
    x_all = np.arange(n_fit + n_test)

    p1 = np.polyfit(x_fit, y_fit, 1)
    p12 = np.polyfit(x_fit, y_fit, 12)

    fig, ax = new_ax(price_axis=False, w=9.2, h=4.8)
    ax.plot(x_all, seg, "o", ms=3, color=GREY, label="سعر GOOG الحقيقي (يومي)")
    ax.plot(x_all, np.polyval(p1, x_all), color=GREEN, lw=2.2, label="نموذج بسيط (درجة 1)")
    ax.plot(x_all, np.polyval(p12, x_all), color=RED, lw=2.2, label="نموذج مفرط التعقيد (درجة 12)")
    ax.axvline(n_fit, color=NAVY, ls="--", lw=1.4)
    ax.text(n_fit - 2, ax.get_ylim()[1], "بيانات التدريب", fontsize=9, color=NAVY, ha="right", va="top", fontweight="bold")
    ax.text(n_fit + 2, ax.get_ylim()[1], "المستقبل غير المرئي", fontsize=9, color=RED, ha="left", va="top", fontweight="bold")
    # clamp crazy extrapolation for display
    lo, hi = seg.min() - 40, seg.max() + 40
    ax.set_ylim(lo, hi)
    ax.set_ylabel("سعر الإغلاق (دولار)")
    ax.set_xlabel("أيام التداول (بيانات حقيقية 2007)")
    ax.legend(frameon=False, fontsize=9, loc="lower left")
    save(fig, "fig-01-02")


# ============================================================ 1.3 Train/Val/Test on real GOOG timeline
def fig_01_03():
    closes = GOOG.Close.values
    idx = GOOG.index
    n = len(closes)
    i1, i2 = int(n * 0.7), int(n * 0.85)
    fig, ax = new_ax(price_axis=False, w=9.2, h=4.4)
    ax.plot(closes, color=NAVY, lw=1.4)
    ax.axvspan(0, i1, color=GREEN, alpha=0.10)
    ax.axvspan(i1, i2, color=GOLD, alpha=0.14)
    ax.axvspan(i2, n, color=RED, alpha=0.10)
    for x0, x1, lab, c in [(0, i1, "تدريب 70%", GREEN), (i1, i2, "تحقق 15%", GOLD), (i2, n, "اختبار 15%", RED)]:
        ax.text((x0 + x1) / 2, closes.max() * 0.98, lab, fontsize=10.5, color=c,
                ha="center", fontweight="bold")
    ax.set_ylabel("سعر GOOG (دولار)")
    ax.set_xlabel(f"{idx[0].year} — {idx[-1].year}: التقسيم الزمني يحترم ترتيب الأحداث (لا خلط عشوائي)")
    save(fig, "fig-01-03")


# ============================================================ 2.1 Python stack layers
def fig_02_01():
    fig, ax = plt.subplots(figsize=(8.8, 5.2), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.2); ax.axis("off")
    layers = [
        ("مصادر البيانات: yfinance · Alpha Vantage · Binance API", "#6B7280", 5.5),
        ("المعالجة: Pandas · NumPy", NAVY, 4.4),
        ("التعلم الآلي: Scikit-learn · XGBoost · LightGBM", GOLD, 3.3),
        ("التعلم العميق واللغة: TensorFlow · PyTorch · Transformers", GREEN, 2.2),
        ("العرض والتقارير: Matplotlib · Seaborn", RED, 1.1),
    ]
    for label, color, y in layers:
        _box(ax, 5, y, 8.6, 0.85, label, color, fs=10.5)
        if y > 1.2:
            arrow(ax, (5, y - 0.48), (5, y - 0.62), color=GREY, lw=1.4)
    save(fig, "fig-02-01")


# ============================================================ 2.2 REAL first analysis: GOOG close + MA20 + volume
def fig_02_02():
    df = GOOG
    close = df.Close.values
    vol = df.Volume.values
    ma20 = np.convolve(close, np.ones(20) / 20, mode="valid")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9.2, 5.6), dpi=150,
                                     gridspec_kw={"height_ratios": [2.4, 1]}, sharex=True)
    fig.patch.set_facecolor("white")
    ax1.plot(close, color=NAVY, lw=1.3, label="إغلاق GOOG")
    ax1.plot(np.arange(19, len(close)), ma20, color=GOLD, lw=1.8, label="متوسط 20 يومًا")
    ax1.legend(frameon=False, fontsize=9, loc="upper left")
    ax1.set_ylabel("السعر (دولار)")
    ax1.grid(axis="y", color=GRID)
    for s in ["top", "right"]: ax1.spines[s].set_visible(False)
    ax2.bar(np.arange(len(vol)), vol / 1e6, color="#9CB4CE", width=1.0)
    ax2.set_ylabel("الحجم (مليون)")
    ax2.set_xlabel("أيام التداول 2004-2013 (بيانات ياهو فاينانس الحقيقية)")
    ax2.grid(axis="y", color=GRID)
    for s in ["top", "right"]: ax2.spines[s].set_visible(False)
    fig.tight_layout(pad=0.8)
    save(fig, "fig-02-02")


# ============================================================ 2.3 REAL returns distribution
def fig_02_03():
    close = GOOG.Close.values
    rets = np.diff(close) / close[:-1] * 100
    fig, ax = new_ax(price_axis=False, w=8.8, h=4.4)
    ax.hist(rets, bins=80, color=NAVY, alpha=0.85, edgecolor="white", linewidth=0.3)
    ax.axvline(rets.mean(), color=GOLD, lw=2, label=f"المتوسط {rets.mean():.3f}%")
    ax.axvline(rets.mean() + 2 * rets.std(), color=RED, ls="--", lw=1.6, label="±2 انحراف معياري")
    ax.axvline(rets.mean() - 2 * rets.std(), color=RED, ls="--", lw=1.6)
    ax.set_xlabel("العائد اليومي % (GOOG 2004-2013 — بيانات حقيقية)")
    ax.set_ylabel("عدد الأيام")
    ax.set_xlim(-12, 12)
    ax.legend(frameon=False, fontsize=9)
    ax.text(11.5, ax.get_ylim()[1] * 0.55,
            "لاحظ الذيول الطويلة:\nأيام تتجاوز ±2σ أكثر\nمما يفترضه التوزيع الطبيعي\n— هذه طبيعة الأسواق",
            fontsize=8.5, color=RED, ha="right", fontweight="bold")
    save(fig, "fig-02-03")




# ============================================================ 3.1 REAL OHLCV candles (EURUSD hourly)
def fig_03_01():
    from figlib import plot_candles
    df = EURUSD.iloc[200:240]
    fig, ax = new_ax(w=9.2, h=4.6)
    plot_candles(ax, df.Open.values, df.High.values, df.Low.values, df.Close.values, width=0.6)
    ax.set_ylabel("EUR/USD")
    ax.set_xlabel("40 شمعة ساعة حقيقية من بيانات EURUSD")
    i = 25
    ax.annotate("Open / High / Low / Close\nخمس قيم لكل فترة (+الحجم) هي الوقود الخام لكل نموذج",
                xy=(i, df.High.values[i]), xytext=(8, df.High.values.max()),
                fontsize=8.5, color=NAVY, fontweight="bold",
                arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.4))
    save(fig, "fig-03-01")


# ============================================================ 3.4 REAL outlier days in GOOG (2008 crash visible)
def fig_03_02():
    close = GOOG.Close.values
    rets = np.diff(close) / close[:-1] * 100
    mu, sd = rets.mean(), rets.std()
    out_idx = np.where(np.abs(rets - mu) > 4 * sd)[0]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9.2, 5.6), dpi=150, sharex=True,
                                     gridspec_kw={"height_ratios": [1.6, 1]})
    fig.patch.set_facecolor("white")
    ax1.plot(close, color=NAVY, lw=1.2)
    ax1.set_ylabel("سعر GOOG")
    ax1.grid(axis="y", color=GRID)
    for s in ["top", "right"]: ax1.spines[s].set_visible(False)
    ax2.plot(rets, color=GREY, lw=0.7)
    ax2.plot(out_idx, rets[out_idx], "o", color=RED, ms=5,
             label=f"أيام شاذة فعلية (> 4σ): {len(out_idx)} يومًا")
    ax2.axhline(mu + 4 * sd, color=RED, ls="--", lw=1)
    ax2.axhline(mu - 4 * sd, color=RED, ls="--", lw=1)
    ax2.set_ylabel("العائد اليومي %")
    ax2.set_xlabel("أيام التداول 2004-2013 — لاحظ عنقود أزمة 2008 الحقيقي")
    ax2.legend(frameon=False, fontsize=9)
    ax2.grid(axis="y", color=GRID)
    for s in ["top", "right"]: ax2.spines[s].set_visible(False)
    fig.tight_layout(pad=0.8)
    save(fig, "fig-03-02")


# ============================================================ 3.2 Data pipeline diagram
def fig_03_03():
    fig, ax = plt.subplots(figsize=(9.4, 4.6), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.4); ax.axis("off")
    srcs = [(1.8, 4.4, "تاريخية\nOHLCV", NAVY), (5.0, 4.4, "بديلة\nأخبار · تواصل", GOLD),
            (8.2, 4.4, "لحظية\nWebSocket", RED)]
    for x, y, lab, c in srcs:
        _box(ax, x, y, 2.3, 1.0, lab, c, fs=9.5)
        arrow(ax, (x, y - 0.55), (5.0, 3.05), color=GREY, lw=1.5)
    _box(ax, 5.0, 2.6, 3.6, 0.85, "تنظيف وتوحيد (Pandas)", GREEN, fs=10)
    arrow(ax, (5.0, 2.15), (5.0, 1.75), color=GREY, lw=1.5)
    _box(ax, 5.0, 1.3, 4.6, 0.85, "مخزن مميزات جاهز للنماذج", NAVY_DEEP, fs=10)
    save(fig, "fig-03-03")


# ============================================================ 4.2 REAL normalization comparison
def fig_04_01():
    close = GOOG.Close.values[:500]
    mm = (close - close.min()) / (close.max() - close.min())
    z = (close - close.mean()) / close.std()
    fig, axes = plt.subplots(1, 3, figsize=(11.2, 3.6), dpi=150)
    fig.patch.set_facecolor("white")
    for ax, (data, title, c) in zip(axes, [
            (close, "الخام: 100-350 دولار", NAVY),
            (mm, "Min-Max: 0 إلى 1", GOLD),
            (z, "Z-Score: متوسط 0، انحراف 1", GREEN)]):
        ax.plot(data, color=c, lw=1.3)
        ax.set_title(title, fontsize=9.5, color=c, fontweight="bold")
        ax.grid(axis="y", color=GRID)
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        ax.set_xticks([])
    fig.suptitle("نفس بيانات GOOG الحقيقية بثلاثة مقاييس — الشكل واحد والمدى مختلف", fontsize=10,
                 color=NAVY, fontweight="bold", y=0.02)
    fig.tight_layout(pad=1.0, rect=[0, 0.06, 1, 1])
    save(fig, "fig-04-01")


# ============================================================ 4.3 REAL engineered features panel
def fig_04_02():
    close = GOOG.Close.values
    n = 400
    seg = close[300:300 + n]
    ma20 = np.convolve(seg, np.ones(20) / 20, mode="same")
    # RSI-14 computed for real
    delta = np.diff(seg, prepend=seg[0])
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)
    ag = np.convolve(gain, np.ones(14) / 14, mode="same")
    al = np.convolve(loss, np.ones(14) / 14, mode="same") + 1e-9
    rsi = 100 - 100 / (1 + ag / al)
    vol20 = np.array([seg[max(0, i - 20):i + 1].std() for i in range(n)])
    fig, axes = plt.subplots(3, 1, figsize=(9.2, 6.4), dpi=150, sharex=True,
                              gridspec_kw={"height_ratios": [2, 1, 1]})
    fig.patch.set_facecolor("white")
    axes[0].plot(seg, color=NAVY, lw=1.3, label="السعر (خام)")
    axes[0].plot(ma20, color=GOLD, lw=1.6, label="ميزة 1: MA20")
    axes[0].legend(frameon=False, fontsize=8.5)
    axes[1].plot(rsi, color=GREEN, lw=1.3)
    axes[1].axhline(70, color=GRID); axes[1].axhline(30, color=GRID)
    axes[1].set_ylabel("ميزة 2: RSI14")
    axes[2].plot(vol20, color=RED, lw=1.3)
    axes[2].set_ylabel("ميزة 3: تقلب 20ي")
    axes[2].set_xlabel("هندسة المميزات: من عمود سعر واحد إلى ثلاث إشارات مختلفة (بيانات GOOG حقيقية)")
    for ax in axes:
        ax.grid(axis="y", color=GRID)
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
    fig.tight_layout(pad=0.7)
    save(fig, "fig-04-02")


# ============================================================ 4.5 Look-ahead bias diagram
def fig_04_03():
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 3.8), dpi=150)
    fig.patch.set_facecolor("white")
    for ax, (title, ok) in zip(axes, [("خطأ: خلط عشوائي يسرّب المستقبل", False),
                                        ("صحيح: قطع زمني صارم", True)]):
        ax.set_xlim(0, 10); ax.set_ylim(0, 3); ax.axis("off")
        rng = np.random.default_rng(42)
        for i in range(20):
            x = 0.5 + i * 0.475
            if ok:
                c = GREEN if i < 14 else RED
            else:
                c = GREEN if rng.random() < 0.7 else RED
            ax.add_patch(Rectangle((x, 1.2), 0.4, 0.8, facecolor=c, edgecolor="white"))
        if ok:
            ax.axvline(0.5 + 14 * 0.475 - 0.03, color=NAVY, lw=2, ls="--")
            ax.text(0.5 + 14 * 0.475, 2.45, "نقطة القطع", fontsize=8.5, color=NAVY, ha="center", fontweight="bold")
        ax.set_title(title, fontsize=10, color=(GREEN if ok else RED), fontweight="bold")
        ax.text(5, 0.55, "أخضر = تدريب   أحمر = اختبار", fontsize=8.5, color=GREY, ha="center")
    fig.tight_layout(pad=1.0)
    save(fig, "fig-04-03")


if __name__ == "__main__":
    only = sys.argv[1:] or None
    fns = [(k, v) for k, v in sorted(globals().items()) if k.startswith("fig_")]
    for name, fn in fns:
        if only and name not in only:
            continue
        fn()
        print("generated", name)
