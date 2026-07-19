"""Shared helpers for generating professional, original UI mockup figures
for the Digital Mastery book. All interfaces drawn here are recreated
generic mockups inspired by common software UI conventions -- not traced,
copied, or extracted from any real company's product.
"""
import re
import os
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, FancyArrowPatch
import arabic_reshaper
from bidi.algorithm import get_display

# ---- Brand palette (consistent with the book) ----
NAVY = "#1F2937"
NAVY_DEEP = "#141b26"
GOLD = "#B7791F"
GOLD_LIGHT = "#E0A94A"
CREAM = "#F7F4EE"
GREEN = "#1F8A56"
RED = "#B91C1C"
BLUE = "#2563EB"
GREY = "#8a8f98"
LIGHT_GREY = "#E5E7EB"
WHITE = "#FFFFFF"

plt.rcParams.update({
    "font.family": ["Noto Naskh Arabic", "DejaVu Sans"],
    "font.sans-serif": ["Noto Naskh Arabic", "DejaVu Sans"],
    "font.size": 10.5,
    "svg.fonttype": "none",  # real <text> elements so Arabic shaping renders correctly
    "axes.unicode_minus": False,
})

_ARABIC_RE = re.compile(r'[؀-ۿ]')
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


def save(fig, name, pad=0.15):
    path = os.path.join(FIG_DIR, f"{name}.svg")
    fig.savefig(path, format="svg", facecolor="white", bbox_inches="tight", pad_inches=pad)
    plt.close(fig)
    return path


def new_canvas(w=10, h=6.4):
    fig, ax = plt.subplots(figsize=(w, h), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    ax.set_aspect("equal")
    return fig, ax


def rounded_box(ax, x, y, w, h, color=WHITE, edge=LIGHT_GREY, lw=1.2, radius=0.12, zorder=2):
    box = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={radius}",
                          facecolor=color, edgecolor=edge, linewidth=lw, zorder=zorder)
    ax.add_patch(box)
    return box


def browser_window(ax, x, y, w, h, url="example.com", title_color=NAVY):
    """Draws a generic browser-window frame (chrome bar + URL field) with a
    content area below it, returning the (x, y, w, content_h) of the inner
    content area so callers can draw the page content inside it."""
    bar_h = 0.55
    rounded_box(ax, x, y, w, h, color=WHITE, edge="#D1D5DB", lw=1.4, radius=0.08, zorder=1)
    ax.add_patch(Rectangle((x, y + h - bar_h), w, bar_h, facecolor="#EEF0F3",
                            edgecolor="none", zorder=2))
    for i, c in enumerate([RED, "#E3A008", GREEN]):
        ax.add_patch(Circle((x + 0.28 + i * 0.26, y + h - bar_h / 2), 0.07, facecolor=c, zorder=3))
    rounded_box(ax, x + 1.15, y + h - bar_h + 0.12, w - 1.5, bar_h - 0.24,
                color=WHITE, edge="#D1D5DB", lw=1.0, radius=0.14, zorder=3)
    ax.text(x + 1.4, y + h - bar_h / 2, url, fontsize=9, color=GREY, va="center", ha="left", zorder=4)
    content_y = y
    content_h = h - bar_h
    ax.add_patch(Rectangle((x, content_y), w, content_h, facecolor=WHITE, edgecolor="none", zorder=1))
    return x, content_y, w, content_h


def phone_frame(ax, x, y, w, h):
    """Draws a generic smartphone outline; returns inner screen rect."""
    rounded_box(ax, x, y, w, h, color=NAVY_DEEP, edge=NAVY_DEEP, lw=0, radius=0.35, zorder=1)
    pad = w * 0.045
    screen_w = w - 2 * pad
    screen_h = h - 2 * pad
    ax.add_patch(Rectangle((x + pad, y + pad), screen_w, screen_h, facecolor=WHITE, zorder=2))
    notch_w = w * 0.3
    ax.add_patch(FancyBboxPatch((x + (w - notch_w) / 2, y + h - pad - 0.12), notch_w, 0.12,
                                 boxstyle="round,pad=0,rounding_size=0.06",
                                 facecolor=NAVY_DEEP, edgecolor="none", zorder=3))
    return x + pad, y + pad, screen_w, screen_h


def chat_bubble(ax, x, y, w, text, sender="bot", fontsize=9.5):
    """sender: 'bot' (left-aligned, grey) or 'user' (right-aligned, gold)."""
    color = GOLD_LIGHT if sender == "user" else "#EEF0F3"
    text_color = NAVY
    lines = text.split("\n")
    line_h = 0.32
    h = line_h * len(lines) + 0.24
    bx = x if sender == "bot" else x  # caller controls x per side
    rounded_box(ax, bx, y, w, h, color=color, edge="none", radius=0.12, zorder=3)
    for i, line in enumerate(lines):
        ax.text(bx + w / 2, y + h - 0.18 - i * line_h, line, fontsize=fontsize, color=text_color,
                 ha="center", va="top", zorder=4)
    return h


def button(ax, x, y, w, h, label, color=GOLD, text_color=WHITE, fontsize=10):
    rounded_box(ax, x, y, w, h, color=color, edge="none", radius=0.1, zorder=4)
    ax.text(x + w / 2, y + h / 2, label, fontsize=fontsize, color=text_color, fontweight="bold",
            ha="center", va="center", zorder=5)


def label_line(ax, x, y, w, height=0.22, color=LIGHT_GREY):
    ax.add_patch(Rectangle((x, y), w, height, facecolor=color, edgecolor="none", zorder=3))


def annotate_point(ax, x, y, text, tx, ty, color=RED, fontsize=9.5, ha="left"):
    ax.annotate("", xy=(x, y), xytext=(tx, ty),
                arrowprops=dict(arrowstyle="-|>", color=color, linewidth=1.6))
    ax.text(tx, ty, text, fontsize=fontsize, color=color, fontweight="bold", ha=ha, va="center")


def sidebar_item(ax, x, y, w, h, label, active=False):
    if active:
        ax.add_patch(Rectangle((x, y), w, h, facecolor="#2D3B4E", edgecolor="none", zorder=3))
    ax.text(x + w / 2, y + h / 2, label, fontsize=9.5,
            color=WHITE if active else "#9CA3AF", ha="center", va="center", zorder=4,
            fontweight="bold" if active else "normal")
