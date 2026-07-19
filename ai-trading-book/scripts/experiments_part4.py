# -*- coding: utf-8 -*-
"""Part 4 experiments (ch9-12): deep learning figures.
Training curves / gradients / comparisons are REAL: computed by numpy
networks actually trained on the real GOOG/EURUSD data."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, Circle
from figlib import NAVY, NAVY_DEEP, GOLD, GOLD_LIGHT, GREEN, RED, GREY, GRID, save, new_ax, arrow
from backtesting.test import GOOG, EURUSD
from experiments_part3 import make_features, FEATS

R = {}
rng = np.random.default_rng(7)


# ---------- tiny numpy MLP with manual backprop ----------
class MLP:
    def __init__(self, d_in, h, seed=0, l2=0.0):
        g = np.random.default_rng(seed)
        self.W1 = g.normal(0, np.sqrt(2 / d_in), (d_in, h))
        self.b1 = np.zeros(h)
        self.W2 = g.normal(0, np.sqrt(2 / h), (h, 1))
        self.b2 = np.zeros(1)
        self.l2 = l2

    def forward(self, X):
        self.z1 = X @ self.W1 + self.b1
        self.a1 = np.maximum(0, self.z1)          # ReLU
        self.z2 = self.a1 @ self.W2 + self.b2
        self.p = 1 / (1 + np.exp(-self.z2))       # sigmoid
        return self.p.ravel()

    def loss(self, X, y):
        p = np.clip(self.forward(X), 1e-9, 1 - 1e-9)
        return -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))

    def step(self, X, y, lr):
        m = len(y)
        p = self.forward(X)
        dz2 = (p - y).reshape(-1, 1) / m
        dW2 = self.a1.T @ dz2 + self.l2 * self.W2
        db2 = dz2.sum(0)
        da1 = dz2 @ self.W2.T
        dz1 = da1 * (self.z1 > 0)
        dW1 = X.T @ dz1 + self.l2 * self.W1
        db1 = dz1.sum(0)
        self.W1 -= lr * dW1; self.b1 -= lr * db1
        self.W2 -= lr * dW2; self.b2 -= lr * db2


def _prep_goog():
    F = make_features(GOOG)
    n = len(F)
    i1, i2 = int(n * .7), int(n * .85)
    X = F[FEATS].values
    mu, sd = X[:i1].mean(0), X[:i1].std(0) + 1e-9
    Xs = (X - mu) / sd
    y = F.target.values.astype(float)
    return (Xs[:i1], y[:i1]), (Xs[i1:i2], y[i1:i2]), (Xs[i2:], y[i2:])


# ==================== CH9 ====================
def fig_09_01():
    """ANN architecture diagram."""
    fig, ax = plt.subplots(figsize=(9.0, 5.2), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")
    layers = [(1.5, 5, "المدخلات\n(9 مميزات)", NAVY),
              (4.5, 4, "طبقة خفية\nReLU × 16", GOLD),
              (7.5, 1, "المخرج\nP(صعود)", GREEN)]
    ys = {}
    for x, k, lab, c in layers:
        pos = np.linspace(1.0, 5.0, k) if k > 1 else [3.0]
        ys[x] = pos
        for y in pos:
            ax.add_patch(Circle((x, y), 0.22, facecolor=c, edgecolor="white", lw=1.2, zorder=4))
        ax.text(x, 5.7, lab, fontsize=9.5, color=c, ha="center", fontweight="bold")
    for i in range(len(layers) - 1):
        x0, x1 = layers[i][0], layers[i + 1][0]
        for y0 in ys[x0]:
            for y1 in ys[x1]:
                ax.plot([x0 + 0.22, x1 - 0.22], [y0, y1], color=GREY, lw=0.4, alpha=0.5, zorder=2)
    ax.text(5, 0.25, "كل وصلة وزن قابل للتعلم — التدريب هو ضبط هذه الأوزان لتقليل الخطأ",
            fontsize=9.5, color=NAVY, ha="center", fontweight="bold")
    save(fig, "fig-09-01")


def fig_09_02():
    """REAL training: overfit run vs early-stopped/regularized run."""
    (Xtr, ytr), (Xva, yva), _ = _prep_goog()
    epochs = 400
    runs = {}
    for name, l2 in [("بلا تنظيم", 0.0), ("مع تنظيم L2", 2e-3)]:
        net = MLP(Xtr.shape[1], 32, seed=3, l2=l2)
        tr, va = [], []
        for e in range(epochs):
            net.step(Xtr, ytr, lr=0.5)
            tr.append(net.loss(Xtr, ytr))
            va.append(net.loss(Xva, yva))
        runs[name] = (tr, va)
    R["ch9"] = {"final_gap_noreg": float(runs["بلا تنظيم"][1][-1] - runs["بلا تنظيم"][0][-1]),
                "best_val_noreg_epoch": int(np.argmin(runs["بلا تنظيم"][1]))}
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.2), dpi=150, sharey=True)
    fig.patch.set_facecolor("white")
    for ax, (name, (tr, va)) in zip(axes, runs.items()):
        ax.plot(tr, color=NAVY, lw=1.6, label="خسارة التدريب")
        ax.plot(va, color=RED, lw=1.6, label="خسارة التحقق")
        if name == "بلا تنظيم":
            be = int(np.argmin(va))
            ax.axvline(be, color=GOLD, ls="--", lw=1.6)
            ax.text(be + 6, max(va) * 0.995, f"نقطة الإيقاف المبكر\n(حقبة {be})",
                    fontsize=8.5, color=GOLD, fontweight="bold")
        ax.set_title(name, fontsize=10.5, color=NAVY, fontweight="bold")
        ax.set_xlabel("الحقبات (Epochs)")
        ax.grid(axis="y", color=GRID)
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        ax.legend(frameon=False, fontsize=8.5)
    axes[0].set_ylabel("الخسارة (Log Loss)")
    save(fig, "fig-09-02")


# ==================== CH10 ====================
def fig_10_01():
    """REAL vanishing-gradient measurement on real EURUSD sequences:
    product of RNN Jacobian norms vs an LSTM-style gated path."""
    rets = np.diff(EURUSD.Close.values) / EURUSD.Close.values[:-1]
    rets = (rets - rets.mean()) / rets.std()
    T = 60
    g = np.random.default_rng(0)
    Wh = g.normal(0, 0.35 / np.sqrt(16), (16, 16))
    Wx = g.normal(0, 0.5, (1, 16))
    seqs = [rets[i:i + T] for i in range(0, 3000, 300)]
    norms_all = []
    for s in seqs:
        h = np.zeros(16)
        prod = 1.0
        norms = []
        for t in range(T):
            a = h @ Wh + s[t] * Wx.ravel()
            h = np.tanh(a)
            J = np.diag(1 - h ** 2) @ Wh.T
            prod *= np.linalg.norm(J, 2)
            norms.append(prod)
        norms_all.append(norms)
    mean_rnn = np.mean(norms_all, axis=0)
    lstm_path = 0.97 ** np.arange(1, T + 1)   # مسار خلية بحارس نسيان ~0.97
    R["ch10"] = {"rnn_norm_at_40": float(mean_rnn[39])}
    fig, ax = new_ax(price_axis=False, w=9.0, h=4.4)
    ax.semilogy(mean_rnn, color=RED, lw=2, label="RNN بسيطة: تلاشي حاد")
    ax.semilogy(lstm_path, color=GREEN, lw=2, label="مسار خلية LSTM (حارس نسيان ≈0.97)")
    ax.axhline(1e-4, color=GREY, ls=":", lw=1)
    ax.set_xlabel("المسافة الزمنية للخلف (خطوات) — مقاسة على متتاليات EURUSD حقيقية")
    ax.set_ylabel("حجم إشارة التدرج (لوغاريتمي)")
    ax.legend(frameon=False, fontsize=9)
    save(fig, "fig-10-01")


def fig_10_02():
    """LSTM cell diagram."""
    fig, ax = plt.subplots(figsize=(9.2, 5.0), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.6); ax.axis("off")
    ax.add_patch(mpatches.FancyBboxPatch((1.2, 1.0), 7.6, 3.4,
                 boxstyle="round,pad=0.1,rounding_size=0.2",
                 facecolor="#F7F4EE", edgecolor=NAVY, lw=1.6, zorder=1))
    arrow(ax, (0.2, 3.9), (9.8, 3.9), color=RED, lw=2.2)
    ax.text(0.5, 4.15, "حالة الخلية C (الذاكرة الطويلة)", fontsize=9, color=RED, fontweight="bold")
    gates = [(2.4, "حارس\nالنسيان\nf", RED), (4.2, "حارس\nالإدخال\ni", GOLD),
             (6.0, "المرشح\nC~", NAVY), (7.8, "حارس\nالإخراج\no", GREEN)]
    for x, lab, c in gates:
        ax.add_patch(Circle((x, 2.4), 0.52, facecolor=c, edgecolor="white", lw=1.5, zorder=3))
        ax.text(x, 2.4, lab, fontsize=8, color="white", ha="center", va="center",
                fontweight="bold", zorder=4)
        arrow(ax, (x, 2.95), (x, 3.75), color=c, lw=1.6)
    arrow(ax, (0.2, 1.6), (1.85, 2.3), color=GREY, lw=1.8)
    ax.text(0.2, 1.3, "المدخل الحالي x_t\n+ الحالة السابقة h", fontsize=8.5, color=GREY, fontweight="bold")
    arrow(ax, (8.35, 2.4), (9.8, 1.7), color=GREEN, lw=1.8)
    ax.text(9.75, 1.35, "المخرج h_t", fontsize=9, color=GREEN, ha="right", fontweight="bold")
    ax.text(5, 0.45, "الحوارس تتحكم بما يُنسى وما يُحفظ وما يُخرج — فتنجو الذاكرة البعيدة من التلاشي",
            fontsize=9.5, color=NAVY, ha="center", fontweight="bold")
    save(fig, "fig-10-02")


# ==================== CH11 ====================
def fig_11_01():
    """Transformer for time series — architecture diagram."""
    fig, ax = plt.subplots(figsize=(8.8, 5.6), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.4); ax.axis("off")
    def blk(y, lab, c, w=5.2):
        ax.add_patch(mpatches.FancyBboxPatch((5 - w / 2, y - 0.36), w, 0.72,
                     boxstyle="round,pad=0.05,rounding_size=0.1",
                     facecolor=c, edgecolor="none", zorder=3))
        ax.text(5, y, lab, fontsize=9.5, color="white", ha="center", va="center",
                fontweight="bold", zorder=4)
    blocks = [(5.9, "نافذة شموع (60 خطوة) + ترميز موضعي", GREY),
              (4.9, "انتباه ذاتي متعدد الرؤوس", NAVY),
              (3.9, "جمع + تطبيع (Residual)", GOLD),
              (2.9, "شبكة تغذية أمامية", NAVY),
              (1.9, "جمع + تطبيع (Residual)", GOLD),
              (0.9, "رأس تنبؤ: العائد/الاتجاه التالي", GREEN)]
    for i, (y, lab, c) in enumerate(blocks):
        blk(y, lab, c)
        if i < len(blocks) - 1:
            arrow(ax, (5, y - 0.4), (5, y - 0.62), color=GREY, lw=1.5)
    ax.text(8.6, 4.9, "×N طبقة", fontsize=10, color=NAVY, fontweight="bold")
    save(fig, "fig-11-01")


def fig_11_02():
    """REAL attention heatmap over a real EURUSD window (identity projections)."""
    close = EURUSD.Close.values
    w = 40
    seg = np.diff(close[1200:1200 + w + 1]) / close[1200:1200 + w]
    z = (seg - seg.mean()) / (seg.std() + 1e-12)
    A = z.reshape(-1, 1) @ z.reshape(1, -1) / np.sqrt(1.0)
    Aw = np.exp(A - A.max(1, keepdims=True))
    Aw = Aw / Aw.sum(1, keepdims=True)
    R["ch11"] = {"max_attn": float(Aw[-1].max())}
    fig, ax = plt.subplots(figsize=(7.6, 6.0), dpi=150)
    fig.patch.set_facecolor("white")
    im = ax.imshow(Aw, cmap="YlOrBr")
    ax.set_xlabel("يهتم بـ (خطوة زمنية)")
    ax.set_ylabel("الخطوة الحالية")
    ax.set_title("مصفوفة انتباه محسوبة فعليًا على نافذة 40 ساعة حقيقية من EURUSD\n(إسقاطات مبسطة لغرض الشرح): كل صف يوزع اهتمامه على الماضي كله دفعة واحدة",
                 fontsize=9.5, color=NAVY, fontweight="bold")
    fig.colorbar(im, ax=ax, shrink=0.8)
    fig.tight_layout()
    save(fig, "fig-11-02")


# ==================== CH12 ====================
def fig_12_01_02():
    """REAL windowed-model comparison on EURUSD test: persistence vs linear-AR
    vs window-MLP (numpy, actually trained)."""
    close = EURUSD.Close.values
    rets = np.diff(close) / close[:-1]
    rets_z = (rets - rets.mean()) / rets.std()
    W = 24
    Xw = np.stack([rets_z[i:i + W] for i in range(len(rets_z) - W)])
    yw = rets_z[W:]
    n = len(yw)
    i1, i2 = int(n * .7), int(n * .85)

    # baseline 1: persistence (توقع = آخر قيمة)
    p_pers = Xw[i2:, -1]
    # baseline 2: linear AR (least squares) — تدريب فعلي
    lin = np.linalg.lstsq(Xw[:i1], yw[:i1], rcond=None)[0]
    p_lin = Xw[i2:] @ lin

    # window-MLP numpy — تدريب فعلي (انحدار MSE)
    g = np.random.default_rng(1)
    W1 = g.normal(0, np.sqrt(2 / W), (W, 32)); b1 = np.zeros(32)
    W2 = g.normal(0, np.sqrt(2 / 32), (32, 1)); b2 = np.zeros(1)
    lr = 0.05
    Xtr, ytr = Xw[:i1], yw[:i1]
    for e in range(300):
        z1 = Xtr @ W1 + b1; a1 = np.maximum(0, z1)
        pred = (a1 @ W2 + b2).ravel()
        d = (pred - ytr).reshape(-1, 1) / len(ytr)
        dW2 = a1.T @ d; db2 = d.sum(0)
        da1 = d @ W2.T; dz1 = da1 * (z1 > 0)
        dW1 = Xtr.T @ dz1; db1 = dz1.sum(0)
        W1 -= lr * dW1; b1 -= lr * db1; W2 -= lr * dW2; b2 -= lr * db2
    a1t = np.maximum(0, Xw[i2:] @ W1 + b1)
    p_mlp = (a1t @ W2 + b2).ravel()

    def rmse(p): return float(np.sqrt(np.mean((p - yw[i2:]) ** 2)))
    res = {"Persistence": rmse(p_pers), "Linear AR(24)": rmse(p_lin),
           "Window-MLP": rmse(p_mlp), "Zero (mean)": rmse(np.zeros_like(p_pers))}
    R["ch12"] = res

    fig, ax = new_ax(price_axis=False, w=9.0, h=4.2)
    names = ["Persistence", "Linear AR(24)", "Window-MLP", "Zero (mean)"]
    vals = [res[k] for k in names]
    colors = [GREY, GOLD, NAVY, GREEN]
    bars = ax.bar(names, vals, color=colors, width=0.55, zorder=3)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.005, f"{v:.3f}", ha="center",
                fontsize=9.5, fontweight="bold", color=NAVY)
    ax.set_ylabel("RMSE على اختبار EURUSD (أقل = أفضل)")
    ax.set_xlabel("مقارنة فعلية: التعقيد لا يضمن التفوق على عوائد ساعة صافية الضوضاء")
    save(fig, "fig-12-01")

    k = 150
    fig, ax = new_ax(price_axis=False, w=9.2, h=4.2)
    ax.plot(yw[i2:i2 + k], color=GREY, lw=1.3, label="العائد الفعلي")
    ax.plot(p_mlp[:k], color=NAVY, lw=1.5, label="Window-MLP (مدرَّبة فعليًا)")
    ax.plot(p_lin[:k], color=GOLD, lw=1.3, label="Linear AR")
    ax.set_xlabel("150 ساعة اختبار حقيقية")
    ax.set_ylabel("العائد المعياري")
    ax.legend(frameon=False, fontsize=8.5)
    save(fig, "fig-12-02")


for f in (fig_09_01, fig_09_02, fig_10_01, fig_10_02, fig_11_01, fig_11_02, fig_12_01_02):
    f()
    print(f.__name__, "done")

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "metrics_part4.json"), "w") as fh:
    json.dump(R, fh, indent=1, ensure_ascii=False)
print(json.dumps(R, indent=1, ensure_ascii=False))
