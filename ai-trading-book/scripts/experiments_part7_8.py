# -*- coding: utf-8 -*-
"""Parts 7-8 experiments (ch19-22): trading bots, risk, ethics.
Backtests and drift/snooping measurements are REAL runs on real GOOG data."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from figlib import NAVY, GOLD, GREEN, RED, GREY, GRID, save, new_ax, arrow
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import GOOG, SMA
from experiments_part3 import make_features, FEATS
from sklearn.linear_model import LogisticRegression

R = {}


class SmaCross(Strategy):
    n1, n2 = 20, 60

    def init(self):
        self.ma1 = self.I(SMA, self.data.Close, self.n1)
        self.ma2 = self.I(SMA, self.data.Close, self.n2)

    def next(self):
        if crossover(self.ma1, self.ma2):
            self.buy()
        elif crossover(self.ma2, self.ma1):
            self.position.close()


# ==================== CH19 ====================
def fig_19_01():
    """Full bot architecture diagram."""
    fig, ax = plt.subplots(figsize=(9.6, 5.2), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 12); ax.set_ylim(0, 6.2); ax.axis("off")

    def box(x, y, w, h, lab, c, fs=9):
        ax.add_patch(mpatches.FancyBboxPatch((x, y), w, h,
                     boxstyle="round,pad=0.07,rounding_size=0.12",
                     facecolor=c, edgecolor="none", zorder=3))
        ax.text(x + w / 2, y + h / 2, lab, fontsize=fs, color="white",
                ha="center", va="center", fontweight="bold", zorder=4)

    chain = [(0.4, "تغذية البيانات\n(أسعار/أخبار)", GREY),
             (3.4, "محرك الإشارة\n(النموذج)", NAVY),
             (6.4, "إدارة المخاطر\n(حجم/حدود)", GOLD),
             (9.4, "التنفيذ\n(وسيط API)", GREEN)]
    for x, lab, c in chain:
        box(x, 4.0, 2.4, 1.3, lab, c)
    for x, _, _ in chain[:-1]:
        arrow(ax, (x + 2.45, 4.65), (x + 2.95, 4.65), color=GREY, lw=1.8)
    box(2.0, 1.8, 3.4, 1.1, "السجلات والمراقبة\n(Logging)", GREY)
    box(6.6, 1.8, 3.4, 1.1, "مفتاح الإيقاف\n(Kill Switch)", RED)
    for xx in (1.6, 4.6, 7.6, 10.6):
        ax.plot([xx, 3.7 if xx < 6 else 8.3], [3.95, 2.95], color=GRID, lw=1.0, ls=":")
    ax.text(6, 0.8, "كل مكوّن معزول وقابل للاختبار وحده — والمخاطر طبقة مستقلة لا يتجاوزها أي نموذج مهما بلغت «ثقته»",
            fontsize=9.5, color=NAVY, ha="center", fontweight="bold")
    save(fig, "fig-19-01")


def fig_19_02():
    """REAL backtest with backtesting.py on GOOG."""
    bt = Backtest(GOOG, SmaCross, cash=10000, commission=.001, finalize_trades=True)
    stats = bt.run()
    eq = stats._equity_curve.Equity / 10000
    bh = GOOG.Close / GOOG.Close.iloc[0]
    R["ch19"] = {"return_pct": float(stats["Return [%]"]),
                 "bh_return_pct": float(stats["Buy & Hold Return [%]"]),
                 "max_dd_pct": float(stats["Max. Drawdown [%]"]),
                 "n_trades": int(stats["# Trades"]),
                 "win_rate": float(stats["Win Rate [%]"]),
                 "sharpe": float(stats["Sharpe Ratio"])}
    fig, ax = new_ax(price_axis=True, w=9.4, h=4.4)
    ax.plot(bh.values * 100 - 100, color=GREY, lw=1.6, label="شراء واحتفاظ")
    ax.plot(np.asarray(eq.values, dtype=float) * 100 - 100, color=NAVY, lw=1.8,
            label=f"استراتيجية تقاطع المتوسطات 20/60 ({int(stats['# Trades'])} صفقة)")
    ax.axhline(0, color=GRID, lw=1)
    ax.set_xlabel("أيام GOOG 2004-2013 — اختبار خلفي فعلي بمكتبة backtesting.py بعمولة 0.1%")
    ax.set_ylabel("العائد التراكمي %")
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    save(fig, "fig-19-02")


# ==================== CH20 ====================
def fig_20_01():
    """Deployment infrastructure diagram."""
    fig, ax = plt.subplots(figsize=(9.4, 5.0), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 12); ax.set_ylim(0, 6.0); ax.axis("off")

    def box(x, y, w, h, lab, c, fs=8.8, tc="white"):
        ax.add_patch(mpatches.FancyBboxPatch((x, y), w, h,
                     boxstyle="round,pad=0.07,rounding_size=0.12",
                     facecolor=c, edgecolor="none", zorder=3))
        ax.text(x + w / 2, y + h / 2, lab, fontsize=fs, color=tc,
                ha="center", va="center", fontweight="bold", zorder=4)

    ax.add_patch(mpatches.FancyBboxPatch((0.5, 1.6), 7.2, 3.9,
                 boxstyle="round,pad=0.1", facecolor="#F7F4EE",
                 edgecolor=NAVY, lw=1.5, zorder=1))
    ax.text(4.1, 5.15, "خادم سحابي يعمل 24/7 (VPS)", fontsize=10, color=NAVY,
            ha="center", fontweight="bold")
    box(1.0, 3.6, 2.9, 1.0, "البوت داخل\nحاوية Docker", NAVY)
    box(4.4, 3.6, 2.9, 1.0, "قاعدة بيانات\n(صفقات وسجلات)", GREY)
    box(1.0, 2.0, 2.9, 1.0, "مراقبة وتنبيهات\n(هاتفك فورًا)", GOLD)
    box(4.4, 2.0, 2.9, 1.0, "مفاتيح API\nفي متغيرات البيئة", RED)
    box(8.6, 3.3, 3.0, 1.2, "الوسيط\n(أوامر حقيقية)", GREEN)
    box(8.6, 1.7, 3.0, 1.0, "بيئة تجريبية\nPaper Trading", GREY)
    arrow(ax, (7.35, 4.1), (8.55, 4.0), color=GREEN, lw=2.0)
    arrow(ax, (7.35, 3.75), (8.55, 2.35), color=GREY, lw=1.6)
    ax.text(6, 0.7, "القاعدة: أسابيع على الحساب التجريبي قبل أول دولار حقيقي — ولا مفاتيح API داخل الكود إطلاقًا",
            fontsize=9.5, color=RED, ha="center", fontweight="bold")
    save(fig, "fig-20-01")


def fig_20_02():
    """REAL cost sensitivity: same strategy, rising commission."""
    comms = [0.0, 0.0005, 0.001, 0.002, 0.005]
    rets = []
    for cm in comms:
        st = Backtest(GOOG, SmaCross, cash=10000, commission=cm,
                      finalize_trades=True).run()
        rets.append(float(st["Return [%]"]))
    R["ch20"] = {f"comm_{cm}": r for cm, r in zip(comms, rets)}
    fig, ax = new_ax(price_axis=False, w=9.0, h=4.2)
    labels = ["0%", "0.05%", "0.1%", "0.2%", "0.5%"]
    colors = [GREEN, GREEN, GOLD, GOLD, RED]
    bars = ax.bar(labels, rets, color=colors, width=0.5, zorder=3)
    for b, v in zip(bars, rets):
        ax.text(b.get_x() + b.get_width() / 2, v + 3, f"{v:.0f}%", ha="center",
                fontsize=10, fontweight="bold", color=NAVY)
    ax.set_xlabel("العمولة لكل صفقة — نفس الاستراتيجية، نفس البيانات (قياس فعلي)")
    ax.set_ylabel("العائد الكلي %")
    save(fig, "fig-20-02")


# ==================== CH21 ====================
def fig_21_01():
    """REAL model drift: logistic model trained on first 3 years of GOOG,
    rolling 126-day accuracy afterwards."""
    F = make_features(GOOG)
    X, y = F[FEATS].values, F.target.values
    n_train = 750  # ~3 سنوات
    mu, sd = X[:n_train].mean(0), X[:n_train].std(0) + 1e-9
    Xs = (X - mu) / sd
    m = LogisticRegression(max_iter=1000).fit(Xs[:n_train], y[:n_train])
    correct = (m.predict(Xs) == y).astype(float)
    w = 126
    roll = np.convolve(correct, np.ones(w) / w, mode="valid")
    xs = np.arange(len(roll)) + w // 2
    R["ch21"] = {"train_end": n_train,
                 "first_oos_window": float(roll[n_train]),
                 "min_oos_window": float(roll[n_train:].min()),
                 "mean_oos": float(correct[n_train:].mean())}
    fig, ax = new_ax(price_axis=False, w=9.4, h=4.4)
    ax.plot(xs, roll * 100, color=NAVY, lw=1.8)
    ax.axhline(50, color=RED, ls=":", lw=1.4)
    ax.axvline(n_train, color=GOLD, ls="--", lw=1.6)
    ax.text(n_train - 30, 57.5, "نهاية بيانات التدريب", fontsize=9, color=GOLD,
            ha="right", fontweight="bold")
    ax.text(len(correct) * 0.75, 50.6, "خط العشوائية 50%", fontsize=8.5, color=RED)
    ax.set_xlabel("أيام GOOG — نموذج دُرّب على أول 750 يومًا ثم تُرك دون إعادة تدريب")
    ax.set_ylabel("الدقة المتحركة (126 يومًا) %")
    save(fig, "fig-21-01")


def fig_21_02():
    """REAL data snooping: best of 60 SMA pairs in-sample vs its out-of-sample."""
    closes = GOOG.Close.values
    n = len(closes)
    half = n // 2
    rets = np.diff(closes) / closes[:-1]

    def strat_ret(n1, n2, lo, hi):
        ma1 = np.convolve(closes, np.ones(n1) / n1, mode="valid")
        ma2 = np.convolve(closes, np.ones(n2) / n2, mode="valid")
        off = n2 - n1
        sig = np.zeros(n)
        sig[n2 - 1:] = (ma1[off:] > ma2).astype(float)
        # صفقة اليوم بإشارة الأمس + تكلفة تغيير المركز
        r = sig[lo:hi - 1] * rets[lo:hi - 1] - 0.001 * np.abs(np.diff(sig[lo - 1:hi - 1]))
        return (np.cumprod(1 + r)[-1] - 1) * 100

    g = np.random.default_rng(4)
    pairs = set()
    while len(pairs) < 60:
        a = int(g.integers(5, 60)); b = int(g.integers(a + 10, 200))
        pairs.add((a, b))
    res = [(strat_ret(a, b, 250, half), strat_ret(a, b, half, n), a, b)
           for a, b in sorted(pairs)]
    res.sort(reverse=True)
    ins = [r[0] for r in res]
    best_in, best_out, ba, bb = res[0]
    med_out = float(np.median([r[1] for r in res]))
    R["ch21_snoop"] = {"best_pair": [ba, bb], "best_in": float(best_in),
                       "best_out": float(best_out), "median_out": med_out}
    fig, ax = new_ax(price_axis=False, w=9.2, h=4.4)
    ax.bar(np.arange(len(ins)), ins, color=GRID, width=0.8, zorder=2,
           label="عوائد 60 توليفة معايير داخل العينة")
    ax.bar([0], [best_in], color=GOLD, width=0.8, zorder=3,
           label=f"«الأفضل» داخل العينة: {best_in:.0f}%")
    ax.bar([1.8], [best_out], color=RED, width=0.8, zorder=3,
           label=f"نفس التوليفة خارج العينة: {best_out:.0f}%")
    ax.axhline(0, color=NAVY, lw=1.2)
    ax.set_xlabel("تجربة فعلية على GOOG: اختيار «أفضل» معايير من 60 توليفة ثم اختبارها على النصف الثاني")
    ax.set_ylabel("العائد الكلي %")
    ax.legend(frameon=False, fontsize=8.8)
    save(fig, "fig-21-02")


# ==================== CH22 ====================
def fig_22_01():
    """Responsible AI trading framework diagram."""
    fig, ax = plt.subplots(figsize=(9.0, 5.0), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 12); ax.set_ylim(0, 6.0); ax.axis("off")
    ax.add_patch(mpatches.FancyBboxPatch((3.7, 4.6), 4.6, 1.0,
                 boxstyle="round,pad=0.08", facecolor=NAVY, edgecolor="none"))
    ax.text(6, 5.1, "تداول مسؤول بالذكاء الاصطناعي", fontsize=11, color="white",
            ha="center", va="center", fontweight="bold")
    pillars = [("الشفافية\nافهم قرارات نموذجك\nولا تشغّل صندوقًا أسود", GOLD),
               ("الامتثال\nقوانين بلدك ووسيطك\nوقواعد السوق", GREY),
               ("حماية رأس المال\nحدود خسارة صارمة\nلا يتجاوزها كود", GREEN),
               ("النزاهة\nلا تلاعب بالسوق\nولا استغلال معلومات", RED)]
    for i, (lab, c) in enumerate(pillars):
        x = 0.6 + i * 2.85
        ax.add_patch(mpatches.FancyBboxPatch((x, 1.7), 2.5, 1.9,
                     boxstyle="round,pad=0.07,rounding_size=0.12",
                     facecolor=c, edgecolor="none", zorder=3))
        ax.text(x + 1.25, 2.65, lab, fontsize=8.6, color="white",
                ha="center", va="center", fontweight="bold", zorder=4)
        ax.plot([x + 1.25, 6], [3.65, 4.55], color=GRID, lw=1.2)
    ax.text(6, 0.75, "الأتمتة تضاعف السرعة — والمسؤولية: الخطأ الذي كان يكلفك صفقة صار يكلفك حسابًا",
            fontsize=9.5, color=NAVY, ha="center", fontweight="bold")
    save(fig, "fig-22-01")


FIGS = [fig_19_01, fig_19_02, fig_20_01, fig_20_02, fig_21_01, fig_21_02, fig_22_01]
if __name__ == "__main__":
    names = sys.argv[1:]
    for f in FIGS:
        if names and f.__name__ not in names:
            continue
        f()
        print(f.__name__, "done")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "metrics_part7_8.json"), "w") as fh:
        json.dump(R, fh, indent=1, ensure_ascii=False)
    print(json.dumps(R, indent=1, ensure_ascii=False))
