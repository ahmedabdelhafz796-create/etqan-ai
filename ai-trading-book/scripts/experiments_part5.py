# -*- coding: utf-8 -*-
"""Part 5 experiments (ch13-15): NLP & news. Market-data figures are REAL
computations on GOOG; headline examples are clearly labeled as illustrative."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from figlib import NAVY, GOLD, GREEN, RED, GREY, GRID, save, new_ax, arrow
from backtesting.test import GOOG

R = {}


# ==================== CH13 ====================
def fig_13_01():
    """NLP sentiment pipeline diagram."""
    fig, ax = plt.subplots(figsize=(9.6, 3.6), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 12); ax.set_ylim(0, 3.6); ax.axis("off")
    steps = [("نص خام\n(عنوان خبر)", GREY), ("تنظيف\nوتقطيع", NAVY),
             ("تمثيل رقمي\n(Embedding)", GOLD), ("نموذج\nتصنيف", NAVY),
             ("درجة مشاعر\n−1 … +1", GREEN)]
    for i, (lab, c) in enumerate(steps):
        x = 1.2 + i * 2.4
        ax.add_patch(mpatches.FancyBboxPatch((x - 0.95, 1.35), 1.9, 1.15,
                     boxstyle="round,pad=0.06,rounding_size=0.12",
                     facecolor=c, edgecolor="none", zorder=3))
        ax.text(x, 1.92, lab, fontsize=9, color="white", ha="center", va="center",
                fontweight="bold", zorder=4)
        if i < len(steps) - 1:
            arrow(ax, (x + 1.0, 1.92), (x + 1.42, 1.92), color=GREY, lw=1.8)
    ax.text(6, 0.55, "الهدف: تحويل تدفق الأخبار النصي إلى ميزة رقمية قابلة للدخول في نماذج الأجزاء السابقة",
            fontsize=9.5, color=NAVY, ha="center", fontweight="bold")
    save(fig, "fig-13-01")


def fig_13_02():
    """Lexicon sentiment actually computed by the chapter's code on
    example headlines (labeled as illustrative examples)."""
    POS = {"نمو", "قياسي", "أرباح", "يتجاوز", "ترقية", "قوي", "توسع"}
    NEG = {"خسائر", "تحقيق", "تراجع", "استقالة", "دعوى", "ضعيف", "خفض"}

    def score(text):
        words = text.replace("،", " ").split()
        s = sum(w in POS for w in words) - sum(w in NEG for w in words)
        return s / max(len(words), 1) * 10

    headlines = [
        "الشركة تعلن أرباح قياسية وخطة توسع جديدة",
        "نمو المبيعات يتجاوز التوقعات مع ترقية التصنيف",
        "تقرير محايد عن نتائج الربع الثالث",
        "تراجع الإيرادات مع خسائر تشغيلية ملحوظة",
        "استقالة المدير المالي وفتح تحقيق تنظيمي",
    ]
    scores = [score(h) for h in headlines]
    R["ch13_scores"] = [round(s, 2) for s in scores]
    fig, ax = new_ax(price_axis=False, w=9.4, h=4.0)
    colors = [GREEN if s > 0.5 else RED if s < -0.5 else GREY for s in scores]
    ypos = np.arange(len(headlines))[::-1]
    ax.barh(ypos, scores, color=colors, height=0.55, zorder=3)
    for y, s, h in zip(ypos, scores, headlines):
        ax.text(0.08 if s < 0 else -0.08, y, h, fontsize=8.6, color=NAVY,
                ha="left" if s < 0 else "right", va="center")
        ax.text(s + (0.09 if s >= 0 else -0.09), y, f"{s:+.1f}",
                fontsize=8.6, color=colors[ypos.tolist().index(y)],
                ha="left" if s >= 0 else "right", va="center", fontweight="bold")
    ax.axvline(0, color=NAVY, lw=1.2)
    ax.set_yticks([])
    ax.set_xlim(-3.4, 3.4)
    ax.set_xlabel("درجة المشاعر بالمعجم (عناوين توضيحية — حسبها كود الفصل حرفيًا)")
    save(fig, "fig-13-02")


def fig_13_03():
    """REAL: news-day proxy — |return| on top-decile volume days vs rest (GOOG)."""
    v = GOOG.Volume.values[1:]
    r = np.abs(np.diff(GOOG.Close.values) / GOOG.Close.values[:-1]) * 100
    thr = np.quantile(v, 0.9)
    hi, lo = r[v >= thr], r[v < thr]
    R["ch13_vol"] = {"high_vol_days_mean_absret": float(hi.mean()),
                     "normal_days_mean_absret": float(lo.mean()),
                     "n_high": int(len(hi))}
    fig, ax = new_ax(price_axis=False, w=8.6, h=4.0)
    bars = ax.bar(["أيام التداول العادية", "أيام أعلى 10% حجم تداول\n(وكيل أيام الأخبار)"],
                  [lo.mean(), hi.mean()], color=[GREY, GOLD], width=0.45, zorder=3)
    for b, val in zip(bars, [lo.mean(), hi.mean()]):
        ax.text(b.get_x() + b.get_width() / 2, val + 0.04, f"{val:.2f}%",
                ha="center", fontsize=11, fontweight="bold", color=NAVY)
    ax.set_ylabel("متوسط الحركة اليومية المطلقة")
    ax.set_xlabel(f"قياس فعلي على {len(r)} يوم GOOG — الخبر يحرّك السوق قبل أن يقرأه أحد بالكامل")
    save(fig, "fig-13-03")


# ==================== CH14 ====================
def fig_14_01():
    """LLM structured extraction diagram."""
    fig, ax = plt.subplots(figsize=(9.6, 4.6), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 12); ax.set_ylim(0, 5.4); ax.axis("off")
    ax.add_patch(mpatches.FancyBboxPatch((0.4, 3.1), 4.6, 1.9,
                 boxstyle="round,pad=0.08", facecolor="#F7F4EE", edgecolor=NAVY, lw=1.4))
    ax.text(2.7, 4.6, "المدخل: خبر + تعليمات", fontsize=9.5, color=NAVY,
            ha="center", fontweight="bold")
    ax.text(2.7, 3.85, '"صنّف أثر الخبر التالي على السهم\nوأعد JSON فقط: {sentiment, confidence}"',
            fontsize=8.4, color=GREY, ha="center", va="center")
    ax.add_patch(mpatches.FancyBboxPatch((5.6, 3.35), 2.2, 1.4,
                 boxstyle="round,pad=0.08", facecolor=NAVY, edgecolor="none"))
    ax.text(6.7, 4.05, "نموذج لغوي\nكبير (LLM)", fontsize=9.5, color="white",
            ha="center", va="center", fontweight="bold")
    ax.add_patch(mpatches.FancyBboxPatch((8.6, 3.1), 3.0, 1.9,
                 boxstyle="round,pad=0.08", facecolor="#F7F4EE", edgecolor=GREEN, lw=1.4))
    ax.text(10.1, 4.6, "المخرج المنضبط", fontsize=9.5, color=GREEN,
            ha="center", fontweight="bold")
    ax.text(10.1, 3.8, '{"sentiment": -0.7,\n "confidence": 0.85}',
            fontsize=8.6, color=NAVY, ha="center", va="center", family="monospace")
    arrow(ax, (5.05, 4.05), (5.55, 4.05), color=GREY, lw=1.8)
    arrow(ax, (7.85, 4.05), (8.55, 4.05), color=GREY, lw=1.8)
    for i, (t, c) in enumerate([("مخرج رقمي منضبط لا إنشاء حر — شرط الدمج في نظام آلي", GREEN),
                                ("درجة الثقة تسمح بتجاهل الحالات الغامضة (عتبة القسم 5.5)", GOLD),
                                ("التحقق من صحة JSON قبل الاستخدام إلزامي — النموذج قد يخطئ الصيغة", RED)]):
        ax.text(6, 2.15 - i * 0.62, "• " + t, fontsize=9, color=c, ha="center", fontweight="bold")
    save(fig, "fig-14-01")


# ==================== CH15 ====================
def fig_15_01():
    """Integrated news+price system architecture."""
    fig, ax = plt.subplots(figsize=(9.4, 5.4), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 12); ax.set_ylim(0, 6.4); ax.axis("off")

    def box(x, y, w, h, lab, c, fs=9):
        ax.add_patch(mpatches.FancyBboxPatch((x, y), w, h,
                     boxstyle="round,pad=0.07,rounding_size=0.12",
                     facecolor=c, edgecolor="none", zorder=3))
        ax.text(x + w / 2, y + h / 2, lab, fontsize=fs, color="white",
                ha="center", va="center", fontweight="bold", zorder=4)

    box(0.5, 4.8, 3.2, 1.0, "تدفق الأخبار (API)", GREY)
    box(0.5, 3.4, 3.2, 1.0, "بيانات الأسعار", GREY)
    box(4.6, 4.8, 3.0, 1.0, "درجة مشاعر\n(LLM/معجم)", NAVY)
    box(4.6, 3.4, 3.0, 1.0, "مميزات سعرية\n(الفصل 4)", NAVY)
    box(8.6, 4.1, 3.0, 1.0, "دمج المميزات", GOLD)
    box(8.6, 2.6, 3.0, 1.0, "نموذج القرار\n(الجزء 3/4)", NAVY)
    box(8.6, 1.1, 3.0, 1.0, "إدارة المخاطر\nوالتنفيذ", GREEN)
    arrow(ax, (3.75, 5.3), (4.55, 5.3), color=GREY, lw=1.6)
    arrow(ax, (3.75, 3.9), (4.55, 3.9), color=GREY, lw=1.6)
    arrow(ax, (7.65, 5.3), (8.55, 4.8), color=GREY, lw=1.6)
    arrow(ax, (7.65, 3.9), (8.55, 4.35), color=GREY, lw=1.6)
    arrow(ax, (10.1, 4.05), (10.1, 3.65), color=GREY, lw=1.6)
    arrow(ax, (10.1, 2.55), (10.1, 2.15), color=GREY, lw=1.6)
    ax.text(6, 0.35, "القاعدة الذهبية: المشاعر ميزة إضافية تدخل نفس الانضباط المنهجي — لا نظام موازٍ بلا اختبار",
            fontsize=9.5, color=NAVY, ha="center", fontweight="bold")
    save(fig, "fig-15-01")


def fig_15_02():
    """REAL event study: big overnight gaps in GOOG (news-driven events) and
    the average path AFTER them."""
    o, c = GOOG.Open.values, GOOG.Close.values
    gap = (o[1:] - c[:-1]) / c[:-1]          # فجوة الافتتاح = أثر خبر بين الجلستين
    rets = np.diff(c) / c[:-1]
    H = 10
    up_idx = np.where(gap > 0.03)[0]
    dn_idx = np.where(gap < -0.03)[0]

    def avg_path(idxs):
        paths = []
        for i in idxs:
            if i + H < len(rets):
                paths.append(np.cumsum(rets[i + 1:i + 1 + H]) * 100)
        return np.mean(paths, axis=0), len(paths)

    up_path, n_up = avg_path(up_idx)
    dn_path, n_dn = avg_path(dn_idx)
    R["ch15"] = {"n_up_gaps": n_up, "n_dn_gaps": n_dn,
                 "up_path_d10": float(up_path[-1]), "dn_path_d10": float(dn_path[-1])}
    fig, ax = new_ax(price_axis=False, w=9.2, h=4.4)
    x = np.arange(1, H + 1)
    ax.plot(x, up_path, "-o", ms=4, color=GREEN, lw=2,
            label=f"بعد فجوة صعود >3% ({n_up} حدثًا)")
    ax.plot(x, dn_path, "-o", ms=4, color=RED, lw=2,
            label=f"بعد فجوة هبوط >3% ({n_dn} حدثًا)")
    ax.axhline(0, color=NAVY, lw=1.1)
    ax.set_xlabel("أيام التداول بعد يوم الفجوة (GOOG — دراسة حدث فعلية)")
    ax.set_ylabel("متوسط العائد التراكمي %")
    ax.legend(frameon=False, fontsize=9)
    save(fig, "fig-15-02")


FIGS = [fig_13_01, fig_13_02, fig_13_03, fig_14_01, fig_15_01, fig_15_02]
if __name__ == "__main__":
    names = sys.argv[1:]
    for f in FIGS:
        if names and f.__name__ not in names:
            continue
        f()
        print(f.__name__, "done")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "metrics_part5.json"), "w") as fh:
        json.dump(R, fh, indent=1, ensure_ascii=False)
    print(json.dumps(R, indent=1, ensure_ascii=False))
