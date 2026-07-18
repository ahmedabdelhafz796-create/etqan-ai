"""Shared helpers for generating professional, original vector figures
for The Triple Analysis. All chart data below is synthetic (randomly
generated to look like realistic market behaviour) — nothing is traced,
copied, or extracted from any reference image.
"""
import numpy as np
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Rectangle
import os

# ---- Brand palette (consistent with the book / etqan-ai brand) ----
NAVY = "#1F2937"
NAVY_DEEP = "#141b26"
GOLD = "#B7791F"
GOLD_LIGHT = "#E0A94A"
CREAM = "#F7F4EE"
GREEN = "#1F8A56"
RED = "#B91C1C"
GREY = "#8a8f98"
GRID = "#E6E1D6"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10.5,
    "axes.edgecolor": NAVY,
    "axes.labelcolor": NAVY,
    "text.color": NAVY,
    "xtick.color": "#555555",
    "ytick.color": "#555555",
    "svg.fonttype": "path",
})

FIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
os.makedirs(FIG_DIR, exist_ok=True)


def new_ax(w=8.6, h=4.6, price_axis=True):
    fig, ax = plt.subplots(figsize=(w, h), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(NAVY)
    ax.spines["bottom"].set_color(NAVY)
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    if price_axis:
        ax.set_ylabel("Price", fontsize=10, labelpad=8)
    ax.set_xlabel("Time →", fontsize=10, labelpad=8)
    ax.set_xticks([])
    return fig, ax


def save(fig, name, pad=0.25):
    path = os.path.join(FIG_DIR, f"{name}.svg")
    fig.tight_layout(pad=pad)
    fig.savefig(path, format="svg", facecolor="white", bbox_inches="tight")
    plt.close(fig)
    return path


# ---------------- synthetic price generation ----------------

def synth_walk(n, drift, vol, start=100.0, seed=0):
    rng = np.random.default_rng(seed)
    steps = rng.normal(drift, vol, n)
    closes = start + np.cumsum(steps)
    return closes


def to_ohlc(closes, wick=0.6, seed=0):
    rng = np.random.default_rng(seed + 999)
    n = len(closes)
    opens = np.empty(n)
    opens[0] = closes[0] - rng.normal(0, 0.3)
    opens[1:] = closes[:-1] + rng.normal(0, 0.15, n - 1)
    highs = np.maximum(opens, closes) + np.abs(rng.normal(0.15, 0.15, n)) * wick
    lows = np.minimum(opens, closes) - np.abs(rng.normal(0.15, 0.15, n)) * wick
    return opens, highs, lows, closes


def plot_candles(ax, opens, highs, lows, closes, width=0.6, start_x=0):
    n = len(closes)
    xs = np.arange(start_x, start_x + n)
    for x, o, h, l, c in zip(xs, opens, highs, lows, closes):
        color = GREEN if c >= o else RED
        ax.plot([x, x], [l, h], color=color, linewidth=1.1, zorder=3, solid_capstyle="round")
        body_bottom = min(o, c)
        body_h = max(abs(c - o), 0.03 * (max(highs) - min(lows) + 1e-6))
        ax.add_patch(Rectangle((x - width / 2, body_bottom), width, body_h,
                                facecolor=color, edgecolor=color, zorder=4))
    ax.set_xlim(start_x - 1, start_x + n)
    return xs


def box(ax, x0, x1, y0, y1, color=GOLD, alpha=0.22, edge=None, lw=1.4, label=None,
        label_pos="top", fontsize=9, z=2):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor=color, alpha=alpha,
                            edgecolor=edge or color, linewidth=lw, zorder=z))
    if label:
        ly = y1 + (y1 - y0) * 0.12 if label_pos == "top" else y0 - (y1 - y0) * 0.25
        ax.text((x0 + x1) / 2, ly, label, ha="center", va="bottom" if label_pos == "top" else "top",
                 fontsize=fontsize, color=edge or NAVY, fontweight="bold")


def hline(ax, y, x0, x1, color=GREY, ls="--", lw=1.4, label=None, label_side="right"):
    ax.plot([x0, x1], [y, y], color=color, linestyle=ls, linewidth=lw, zorder=2)
    if label:
        xt = x1 + 0.3 if label_side == "right" else x0 - 0.3
        ha = "left" if label_side == "right" else "right"
        ax.text(xt, y, label, fontsize=9, color=color, va="center", ha=ha, fontweight="bold")


def arrow(ax, xy0, xy1, color=NAVY, lw=2.2, style="-|>", ls="solid", label=None, fontsize=9.5, label_offset=(0, 0.4)):
    a = FancyArrowPatch(xy0, xy1, arrowstyle=style, color=color, linewidth=lw,
                         linestyle=ls, mutation_scale=16, zorder=5)
    ax.add_patch(a)
    if label:
        mx, my = (xy0[0] + xy1[0]) / 2 + label_offset[0], (xy0[1] + xy1[1]) / 2 + label_offset[1]
        ax.text(mx, my, label, fontsize=fontsize, color=color, fontweight="bold", ha="center")


def marker_point(ax, x, y, color=NAVY, label=None, va="bottom", dy=0.5, fontsize=9):
    ax.plot([x], [y], marker="v" if va == "bottom" else "^", color=color, markersize=7, zorder=6)
    if label:
        ax.text(x, y + (dy if va == "bottom" else -dy), label, fontsize=fontsize, color=color,
                ha="center", va="bottom" if va == "bottom" else "top", fontweight="bold")


def rolling_mean(x, window):
    """Edge-aware rolling mean (expanding window at the start) -- avoids the
    zero-padding artifacts that np.convolve(mode='same') introduces at the
    edges of the series."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    out = np.empty(n)
    for i in range(n):
        lo = max(0, i - window + 1)
        out[i] = x[lo:i + 1].mean()
    return out


def set_ylim_pad(ax, values, pad_frac=0.18):
    lo, hi = min(values), max(values)
    pad = (hi - lo) * pad_frac
    ax.set_ylim(lo - pad, hi + pad)
