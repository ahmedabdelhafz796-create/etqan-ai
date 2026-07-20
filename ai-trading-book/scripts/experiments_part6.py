# -*- coding: utf-8 -*-
"""Part 6 experiments (ch16-18): reinforcement learning.
A tabular Q-learning agent is ACTUALLY trained on real GOOG data."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle
from figlib import NAVY, GOLD, GREEN, RED, GREY, GRID, save, new_ax, arrow
from backtesting.test import GOOG
from experiments_part3 import make_features

R = {}
COST = 0.0005          # تكلفة تغيير المركز 0.05%


# ---------- real environment from real GOOG data ----------
def _env():
    F = make_features(GOOG)
    rets = F["next_ret"].values          # عائد اليوم التالي (القرار اليوم، الجني غدًا)
    # حالة مُجزأة: (اتجاه الأمس 3) × (نظام تقلب 2) × (موقع من MA20 3) = 18 حالة
    s_ret = np.digitize(F["ret_lag1"].values, [-0.005, 0.005])
    s_vol = (F["vol20"].values > np.nanmedian(F["vol20"].values)).astype(int)
    s_ma = np.digitize(F["dist_ma20"].values, [-0.02, 0.02])
    states = s_ret * 6 + s_vol * 3 + s_ma
    n = len(states)
    i1, i2 = int(n * .7), int(n * .85)
    return states, rets, i1, i2


def _train_q(states, rets, i1, penalty=0.0, episodes=60, seed=0):
    """Tabular Q-learning, actions: 0=خارج السوق, 1=داخل السوق.
    hist = return of the GREEDY policy on the train slice after each episode."""
    g = np.random.default_rng(seed)
    Q = np.zeros((18, 2))
    alpha, gamma = 0.1, 0.9
    hist, eps_hist = [], []
    for ep in range(episodes):
        eps = max(0.02, 0.5 * (0.93 ** ep))
        pos = 0
        for t in range(i1 - 1):
            s = states[t]
            a = g.integers(2) if g.random() < eps else int(np.argmax(Q[s]))
            r = a * rets[t] - COST * abs(a - pos) - penalty * a * abs(rets[t])
            s2 = states[t + 1]
            Q[s, a] += alpha * (r + gamma * Q[s2].max() - Q[s, a])
            pos = a
        hist.append((_equity(Q, states, rets, 0, i1 - 1)[-1] - 1) * 100)
        eps_hist.append(eps)
    return Q, hist, eps_hist


def _equity(Q, states, rets, lo, hi):
    pos, eq = 0, [1.0]
    for t in range(lo, hi):
        a = int(np.argmax(Q[states[t]]))
        eq.append(eq[-1] * (1 + a * rets[t] - COST * abs(a - pos)))
        pos = a
    return np.array(eq)


# ==================== CH16 ====================
def fig_16_01():
    """Agent-environment loop diagram."""
    fig, ax = plt.subplots(figsize=(8.8, 4.6), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 12); ax.set_ylim(0, 5.6); ax.axis("off")
    ax.add_patch(mpatches.FancyBboxPatch((1.0, 3.6), 3.6, 1.3,
                 boxstyle="round,pad=0.08", facecolor=NAVY, edgecolor="none"))
    ax.text(2.8, 4.25, "الوكيل (Agent)\nسياسة القرار", fontsize=10, color="white",
            ha="center", va="center", fontweight="bold")
    ax.add_patch(mpatches.FancyBboxPatch((7.4, 3.6), 3.6, 1.3,
                 boxstyle="round,pad=0.08", facecolor=GOLD, edgecolor="none"))
    ax.text(9.2, 4.25, "البيئة (Environment)\nالسوق الحقيقي", fontsize=10, color="white",
            ha="center", va="center", fontweight="bold")
    arrow(ax, (4.7, 4.5), (7.3, 4.5), color=GREEN, lw=2.2)
    ax.text(6, 4.75, "الفعل: شراء / خروج", fontsize=9.5, color=GREEN,
            ha="center", fontweight="bold")
    arrow(ax, (7.3, 3.8), (4.7, 3.8), color=RED, lw=2.2)
    ax.text(6, 3.3, "المكافأة: الربح/الخسارة بعد التكاليف", fontsize=9.5, color=RED,
            ha="center", fontweight="bold")
    arrow(ax, (7.3, 3.55), (4.7, 2.6), color=GREY, lw=1.8)
    ax.text(6, 2.35, "الحالة الجديدة: (اتجاه الأمس، نظام التقلب، الموقع من MA20)",
            fontsize=9.5, color=GREY, ha="center", fontweight="bold")
    ax.text(6, 1.0, "لا «إجابات صحيحة» هنا كما في التعلم الخاضع — فقط أفعال ومكافآت:\nالوكيل يكتشف بنفسه أي سلوك يعظّم المكافأة التراكمية",
            fontsize=9.5, color=NAVY, ha="center", fontweight="bold")
    save(fig, "fig-16-01")


def fig_16_02():
    """REAL Q-learning training curve on real GOOG train slice."""
    states, rets, i1, i2 = _env()
    Q, hist, eps_hist = _train_q(states, rets, i1)
    np.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "q_table.npy"), Q)
    R["ch16"] = {"final_greedy_train": float(hist[-1]),
                 "std_first20": float(np.std(hist[:20])),
                 "std_last20": float(np.std(hist[-20:])),
                 "episodes": len(hist)}
    fig, ax = new_ax(price_axis=False, w=9.2, h=4.2)
    ax.plot(hist, color=NAVY, lw=1.6, label="عائد السياسة الجشعة على التدريب بعد كل حلقة %")
    k = 7
    smooth = np.convolve(hist, np.ones(k) / k, mode="valid")
    ax.plot(np.arange(k - 1, len(hist)), smooth, color=GOLD, lw=2.4,
            label="متوسط متحرك (7 حلقات)")
    ax.set_xlabel("حلقات التدريب (Episodes) — تدريب فعلي على 1500 يوم GOOG")
    ax.set_ylabel("عائد السياسة المتعلمة %")
    ax.legend(frameon=False, fontsize=9)
    save(fig, "fig-16-02")


# ==================== CH17 ====================
def fig_17_01():
    """DQN architecture diagram."""
    fig, ax = plt.subplots(figsize=(9.2, 4.8), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 12); ax.set_ylim(0, 5.6); ax.axis("off")

    def box(x, y, w, h, lab, c, fs=9):
        ax.add_patch(mpatches.FancyBboxPatch((x, y), w, h,
                     boxstyle="round,pad=0.07,rounding_size=0.12",
                     facecolor=c, edgecolor="none", zorder=3))
        ax.text(x + w / 2, y + h / 2, lab, fontsize=fs, color="white",
                ha="center", va="center", fontweight="bold", zorder=4)

    box(0.4, 3.8, 3.0, 1.2, "حالة السوق\n(مميزات متصلة)", GREY)
    box(4.3, 3.8, 3.2, 1.2, "شبكة عصبية\nQ(s, a; θ)", NAVY)
    box(8.4, 3.8, 3.2, 1.2, "قيمة Q لكل فعل\nخروج / شراء", GREEN)
    arrow(ax, (3.45, 4.4), (4.25, 4.4), color=GREY, lw=1.8)
    arrow(ax, (7.55, 4.4), (8.35, 4.4), color=GREY, lw=1.8)
    box(1.2, 1.6, 4.4, 1.1, "ذاكرة إعادة التشغيل\n(Replay Buffer)", GOLD)
    box(6.6, 1.6, 4.4, 1.1, "شبكة هدف مجمدة\n(Target Network)", RED)
    ax.text(6, 0.55, "الترقية عن الجدول: تعميم عبر حالات لم تُرَ + استقرار التدريب بالذاكرة والشبكة المجمدة",
            fontsize=9.5, color=NAVY, ha="center", fontweight="bold")
    save(fig, "fig-17-01")


def fig_17_02():
    """REAL exploration schedule + its effect (from the actual training run)."""
    states, rets, i1, i2 = _env()
    _, hist, eps_hist = _train_q(states, rets, i1)
    fig, ax = new_ax(price_axis=False, w=9.2, h=4.2)
    ax.plot(np.array(eps_hist) * 100, color=RED, lw=2.2, label="نسبة الاستكشاف ε %")
    ax.set_ylabel("نسبة القرارات العشوائية %")
    ax.set_xlabel("حلقات التدريب — جدول التخميد الفعلي المستخدم في تجربتنا")
    ax2 = ax.twinx()
    k = 7
    smooth = np.convolve(hist, np.ones(k) / k, mode="valid")
    ax2.plot(np.arange(k - 1, len(hist)), smooth, color=NAVY, lw=2.0,
             label="أداء السياسة المتعلمة الممهد %")
    ax2.set_ylabel("عائد السياسة الممهد %")
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, frameon=False, fontsize=9, loc="center right")
    save(fig, "fig-17-02")


# ==================== CH18 ====================
def fig_18_01():
    """REAL test equity: greedy Q-agent vs buy&hold on unseen GOOG test."""
    states, rets, i1, i2 = _env()
    Q, _, _ = _train_q(states, rets, i1)
    n = len(states)
    eq_agent = _equity(Q, states, rets, i2, n - 1)
    eq_bh = np.cumprod(1 + rets[i2:n - 1]); eq_bh = np.insert(eq_bh, 0, 1.0)
    R["ch18"] = {"agent_final": float(eq_agent[-1]), "bh_final": float(eq_bh[-1]),
                 "agent_dd": float((1 - eq_agent / np.maximum.accumulate(eq_agent)).max()),
                 "bh_dd": float((1 - eq_bh / np.maximum.accumulate(eq_bh)).max()),
                 "time_in_market": float(np.mean([int(np.argmax(Q[s])) for s in states[i2:n - 1]]))}
    fig, ax = new_ax(price_axis=False, w=9.4, h=4.4)
    ax.plot((eq_bh - 1) * 100, color=GREY, lw=1.8, label="شراء واحتفاظ")
    ax.plot((eq_agent - 1) * 100, color=NAVY, lw=2.0, label="وكيل Q-Learning (بعد التكاليف)")
    ax.axhline(0, color=GRID, lw=1)
    ax.set_xlabel("أيام الاختبار غير المرئية (GOOG) — تقييم فعلي للوكيل المدرَّب")
    ax.set_ylabel("العائد التراكمي %")
    ax.legend(frameon=False, fontsize=9)
    save(fig, "fig-18-01")


def fig_18_02():
    """REAL reward-shaping comparison: plain PnL vs volatility-penalized reward."""
    states, rets, i1, i2 = _env()
    n = len(states)
    Q1, _, _ = _train_q(states, rets, i1, penalty=0.0)
    Q2, _, _ = _train_q(states, rets, i1, penalty=0.7)
    eq1 = _equity(Q1, states, rets, i2, n - 1)
    eq2 = _equity(Q2, states, rets, i2, n - 1)
    dd = lambda e: (1 - e / np.maximum.accumulate(e)).max() * 100
    R["ch18_shaping"] = {"plain_final": float(eq1[-1]), "penal_final": float(eq2[-1]),
                         "plain_dd": float(dd(eq1)), "penal_dd": float(dd(eq2))}
    fig, ax = new_ax(price_axis=False, w=9.4, h=4.4)
    ax.plot((eq1 - 1) * 100, color=NAVY, lw=2.0,
            label=f"مكافأة الربح الخام (تراجع أقصى {dd(eq1):.1f}%)")
    ax.plot((eq2 - 1) * 100, color=GREEN, lw=2.0,
            label=f"مكافأة معاقبة للتقلب (تراجع أقصى {dd(eq2):.1f}%)")
    ax.axhline(0, color=GRID, lw=1)
    ax.set_xlabel("أيام الاختبار (GOOG) — نفس الوكيل بدالتي مكافأة مختلفتين")
    ax.set_ylabel("العائد التراكمي %")
    ax.legend(frameon=False, fontsize=9)
    save(fig, "fig-18-02")


FIGS = [fig_16_01, fig_16_02, fig_17_01, fig_17_02, fig_18_01, fig_18_02]
if __name__ == "__main__":
    names = sys.argv[1:]
    for f in FIGS:
        if names and f.__name__ not in names:
            continue
        f()
        print(f.__name__, "done")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "metrics_part6.json"), "w") as fh:
        json.dump(R, fh, indent=1, ensure_ascii=False)
    print(json.dumps(R, indent=1, ensure_ascii=False))
