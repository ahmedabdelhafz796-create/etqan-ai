"""Shared helpers for generating professional, original vector figures
for The Triple Analysis. All chart data below is synthetic (randomly
generated to look like realistic market behaviour) — nothing is traced,
copied, or extracted from any reference image.
"""
import re
import numpy as np
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import matplotlib.text
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Rectangle
import arabic_reshaper
from bidi.algorithm import get_display
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
    "font.family": ["Noto Naskh Arabic", "DejaVu Sans"],
    "font.sans-serif": ["Noto Naskh Arabic", "DejaVu Sans"],
    "font.size": 10.5,
    "axes.edgecolor": NAVY,
    "axes.labelcolor": NAVY,
    "text.color": NAVY,
    "xtick.color": "#555555",
    "ytick.color": "#555555",
    "svg.fonttype": "path",
    "axes.unicode_minus": False,
})


# ---- Arabic text shaping/bidi so labels typed in the book's language
# render correctly inside matplotlib figures (which does no shaping or
# bidi reordering on its own). Standard trading abbreviations (BOS, RSI,
# FVG...) are typically embedded inside Arabic strings and are handled
# correctly by the bidi algorithm automatically -- no special-casing needed.
_ARABIC_RE = re.compile(r'[؀-ۿ]')

# matplotlib (esp. Legend) sometimes calls Text.set_text(...) more than once
# on the same artist -- reshaping+bidi-reordering an already-processed string
# corrupts it (arabic_reshaper expects unshaped input). A leading zero-width
# space marks text this function has already produced, so a second call is a
# no-op instead of re-mangling it.
_PROCESSED_MARK = "​"


def ar(text):
    text = str(text)
    if text.startswith(_PROCESSED_MARK):
        return text
    if not _ARABIC_RE.search(text):
        return text
    return _PROCESSED_MARK + get_display(arabic_reshaper.reshape(text))


_orig_set_text = matplotlib.text.Text.set_text


def _patched_set_text(self, s):
    return _orig_set_text(self, ar(s) if s else s)


matplotlib.text.Text.set_text = _patched_set_text

FIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
os.makedirs(FIG_DIR, exist_ok=True)


def new_ax(w=8.6, h=4.6, price_axis=True):
    """price_axis=True mimics the real trading-platform convention (TradingView /
    MetaTrader): the price scale sits on the RIGHT edge of the chart, not the left."""
    fig, ax = plt.subplots(figsize=(w, h), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    if price_axis:
        for spine in ["top", "left"]:
            ax.spines[spine].set_visible(False)
        ax.spines["right"].set_color(NAVY)
        ax.spines["bottom"].set_color(NAVY)
        ax.yaxis.tick_right()
        ax.yaxis.set_label_position("right")
        ax.set_ylabel("السعر", fontsize=10, labelpad=10, rotation=270, va="bottom")
    else:
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        ax.spines["left"].set_color(NAVY)
        ax.spines["bottom"].set_color(NAVY)
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.set_xlabel("الزمن", fontsize=10, labelpad=8)
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


def regime_walk(segments, start=100.0, seed=0):
    """Concatenate several (n, drift, vol) regimes into one longer, more
    organic multi-swing series -- reads like a real multi-month chart instead
    of a short single-drift snippet (matches the density of real technical
    analysis textbook charts, which span many swings rather than one move)."""
    closes = []
    cur = start
    for i, (n, drift, vol) in enumerate(segments):
        seg = synth_walk(n, drift, vol, start=cur, seed=seed + i * 17)
        closes.append(seg)
        cur = seg[-1]
    return np.concatenate(closes)


# ---------------- classic-textbook annotation primitives ----------------

def letter_point(ax, x, y, letter, color=NAVY, dy=0.5, va="bottom", fontsize=11.5,
                  circle=True, r=None):
    """Marks a swing point with a small circle + bold letter (A, B, C, D...),
    the lettered swing-point convention used throughout classic technical
    analysis texts (Dow Theory, Murrey Math, Edwards & Magee)."""
    if circle:
        ax.add_patch(mpatches.Circle((x, y), r or 0.35, facecolor="none",
                                      edgecolor=color, linewidth=1.6, zorder=6))
    ty = y + dy if va == "bottom" else y - dy
    ax.text(x, ty, letter, fontsize=fontsize, color=color, fontweight="bold",
            ha="center", va=va, zorder=7)


def zigzag(ax, points, color=NAVY, lw=2.2, ls="-", letters=None, letter_color=None,
           dy=0.6, fontsize=11.5):
    """Draws a connecting zig-zag line through a list of (x, y) swing points,
    optionally labelling each point with a letter -- the schematic style used
    to illustrate Dow Theory / Elliott Wave swing sequences."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    ax.plot(xs, ys, color=color, linewidth=lw, linestyle=ls, marker="o", markersize=5.5, zorder=5)
    if letters:
        lc = letter_color or color
        for (x, y), letter in zip(points, letters):
            ax.text(x, y + dy, letter, fontsize=fontsize, color=lc, fontweight="bold",
                    ha="center", va="bottom", zorder=7)


def channel(ax, x0, x1, y0, slope, width, color=NAVY, lw=2.0, ls="-"):
    """Draws a price channel: two parallel lines of a given slope spanning
    [x0, x1], `width` apart (lower line's value at x0 is y0)."""
    xs = np.array([x0, x1], dtype=float)
    lower = y0 + slope * (xs - x0)
    upper = lower + width
    ax.plot(xs, lower, color=color, linewidth=lw, linestyle=ls, zorder=4)
    ax.plot(xs, upper, color=color, linewidth=lw, linestyle=ls, zorder=4)
    return lower, upper


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


def hline(ax, y, x0, x1, color=GREY, ls="--", lw=1.4, label=None, label_side="left"):
    """Default label_side is 'left' -- the price scale now lives on the right edge
    of the chart (TradingView/MetaTrader convention), so annotation labels default
    to the opposite side to avoid colliding with the price axis."""
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
