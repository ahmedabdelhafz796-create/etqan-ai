"""Publication-quality chart rendering & annotation.

Renders the real OHLCV windows with mplfinance and draws the professional
annotation layer: zones, structure, arrows, entry/SL/TP with risk-reward
shading, fib grids, session shading, volume profile, lesson box, and a
provenance footer on every image.

Design language (consistent across all 300 plates):
  candles   up #0F766E (teal) / down #C2410C (vermilion) - CVD-safe pair;
            direction is also encoded by fill so color is never the only cue
  zones     demand #0F766E @12%, supply #C2410C @12%, neutral #64748B @12%
  accents   entry #1D4ED8, stop #B91C1C, target #047857, liquidity #7C3AED
  grid/axes recessive gray on an off-white surface
"""

from __future__ import annotations

import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplfinance as mpf
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, Rectangle

from . import data_sources as ds

# ---------------------------------------------------------------- palette

INK = "#1E293B"
INK2 = "#475569"
MUTED = "#64748B"
SURFACE = "#FCFCFA"
PANEL = "#F6F6F2"
GRID = "#E4E4DC"
UP = "#0F766E"
DOWN = "#C2410C"
ENTRY = "#1D4ED8"
STOP = "#B91C1C"
TARGET = "#047857"
LIQ = "#7C3AED"
NEUT = "#64748B"
GOLD = "#B7791F"

MC = mpf.make_marketcolors(
    up=UP, down=DOWN, edge={"up": UP, "down": DOWN},
    wick={"up": UP, "down": DOWN}, volume={"up": "#8FBFB9", "down": "#E0A88E"},
)
STYLE = mpf.make_mpf_style(
    marketcolors=MC, facecolor=SURFACE, figcolor=SURFACE, edgecolor=GRID,
    gridcolor=GRID, gridstyle="-", y_on_right=True,
    rc={
        "font.size": 15, "axes.labelcolor": INK2, "xtick.color": INK2,
        "ytick.color": INK2, "axes.edgecolor": GRID, "axes.linewidth": 1.2,
        "font.family": "DejaVu Sans",
    },
)

W_PX, H_PX, DPI = 2560, 1440, 100


def fmt_price(v, dataset):
    return f"{v:,.4f}" if dataset.startswith("EURUSD") else f"{v:,.2f}"


class Plate:
    """One rendered chart plate with an annotation toolkit."""

    def __init__(self, case, df_full: pd.DataFrame, w0: int, w1: int,
                 overlays=None, panels=None):
        self.case = case
        self.dataset = case["dataset"]
        self.name = self.dataset.rsplit("_", 1)[0]
        self.tf = self.dataset.rsplit("_", 1)[1]
        self.df_full = df_full
        self.w0, self.w1 = w0, w1
        self.df = df_full.iloc[w0:w1]
        self.addplots = []
        self.panel_kinds = panels or []
        self._build_overlays(overlays or [])

    # x coordinate of a global integer index inside the window
    def x(self, i) -> float:
        return float(i - self.w0)

    def _build_overlays(self, overlays):
        from . import indicators as ind

        self.extra_panels = 0
        df, sl = self.df_full, slice(self.w0, self.w1)
        self.overlay_legend = []
        for ov in overlays:
            if ov.startswith("ema") or ov.startswith("sma"):
                n = int(ov[3:])
                fn = ind.ema if ov.startswith("ema") else ind.sma
                col = {20: "#B7791F", 50: "#1D4ED8", 100: "#7C3AED", 200: "#0F172A", 9: "#B7791F", 21: "#1D4ED8"}.get(n, MUTED)
                self.addplots.append(mpf.make_addplot(fn(df.Close, n).iloc[sl], color=col, width=2.2, panel=0))
                self.overlay_legend.append((f"{ov.upper()[:3]} {n}", col))
            elif ov == "bb":
                mid, up, lo = ind.bollinger(df.Close)
                for s, c, w in [(mid, GOLD, 1.8), (up, MUTED, 1.6), (lo, MUTED, 1.6)]:
                    self.addplots.append(mpf.make_addplot(s.iloc[sl], color=c, width=w, panel=0))
                self.overlay_legend += [("BB(20,2)", MUTED)]
            elif ov == "vwap":
                self.addplots.append(mpf.make_addplot(ind.vwap_session(df).iloc[sl], color=LIQ, width=2.4, panel=0))
                self.overlay_legend.append(("Session VWAP", LIQ))
            elif ov == "psar":
                self.addplots.append(mpf.make_addplot(ind.psar(df).iloc[sl], type="scatter", markersize=14, marker=".", color=LIQ, panel=0))
                self.overlay_legend.append(("Parabolic SAR", LIQ))
            elif ov == "supertrend":
                st, _ = ind.supertrend(df)
                self.addplots.append(mpf.make_addplot(st.iloc[sl], color=LIQ, width=2.2, panel=0))
                self.overlay_legend.append(("Supertrend(10,3)", LIQ))
            elif ov == "ichimoku":
                conv, base, sa, sb, lag = ind.ichimoku(df)
                for s, c in [(conv, "#1D4ED8"), (base, "#B7791F"), (sa, "#0F766E"), (sb, "#C2410C")]:
                    self.addplots.append(mpf.make_addplot(s.iloc[sl], color=c, width=1.8, panel=0))
                self.overlay_legend += [("Tenkan", "#1D4ED8"), ("Kijun", "#B7791F"), ("Span A/B", "#0F766E")]

        panel_id = 2
        self.panel_map = {}
        for pk in self.panel_kinds:
            if pk == "rsi":
                r = ind.rsi(df.Close).iloc[sl]
                self.addplots.append(mpf.make_addplot(r, color="#1D4ED8", width=2.0, panel=panel_id, ylabel="RSI(14)"))
            elif pk == "macd":
                line, sig, hist = ind.macd(df.Close)
                self.addplots += [
                    mpf.make_addplot(line.iloc[sl], color="#1D4ED8", width=2.0, panel=panel_id, ylabel="MACD"),
                    mpf.make_addplot(sig.iloc[sl], color="#B7791F", width=2.0, panel=panel_id),
                    mpf.make_addplot(hist.iloc[sl], type="bar", color="#94A3B8", panel=panel_id),
                ]
            elif pk == "stoch":
                k, d = ind.stochastic(df)
                self.addplots += [
                    mpf.make_addplot(k.iloc[sl], color="#1D4ED8", width=2.0, panel=panel_id, ylabel="Stoch(14,3)"),
                    mpf.make_addplot(d.iloc[sl], color="#B7791F", width=2.0, panel=panel_id),
                ]
            elif pk == "adx":
                a, pdi, mdi = ind.adx(df)
                self.addplots += [
                    mpf.make_addplot(a.iloc[sl], color=INK, width=2.2, panel=panel_id, ylabel="ADX/DI"),
                    mpf.make_addplot(pdi.iloc[sl], color=UP, width=1.8, panel=panel_id),
                    mpf.make_addplot(mdi.iloc[sl], color=DOWN, width=1.8, panel=panel_id),
                ]
            elif pk == "atr":
                self.addplots.append(mpf.make_addplot(ind.atr(df).iloc[sl], color="#7C3AED", width=2.0, panel=panel_id, ylabel="ATR(14)"))
            elif pk == "obv":
                self.addplots.append(mpf.make_addplot(ind.obv(df).iloc[sl], color="#1D4ED8", width=2.0, panel=panel_id, ylabel="OBV"))
            elif pk == "cci":
                self.addplots.append(mpf.make_addplot(ind.cci(df).iloc[sl], color="#1D4ED8", width=2.0, panel=panel_id, ylabel="CCI(20)"))
            elif pk == "cmf":
                self.addplots.append(mpf.make_addplot(ind.cmf(df).iloc[sl], color="#1D4ED8", width=2.0, panel=panel_id, ylabel="CMF(20)"))
            self.panel_map[pk] = panel_id
            panel_id += 1
        self.extra_panels = panel_id - 2

    # ------------------------------------------------------------ figure

    def open(self):
        n_extra = self.extra_panels
        ratios = [7, 1.6] + [2.2] * n_extra
        kw = dict(addplot=self.addplots) if self.addplots else {}
        self.fig, axes = mpf.plot(
            self.df, type="candle", style=STYLE, volume=True,
            returnfig=True, **kw,
            figsize=(W_PX / DPI, H_PX / DPI), panel_ratios=tuple(ratios),
            datetime_format="%Y-%m-%d %H:%M" if self.tf in ("1H", "4H") else "%Y-%m-%d",
            xrotation=0, scale_padding=dict(left=0.4, top=1.3, bottom=0.8, right=1.2),
            tight_layout=False, warn_too_much_data=10000,
            update_width_config=dict(candle_width=0.72, candle_linewidth=1.5, volume_width=0.6),
        )
        self.ax = axes[0]
        self.ax_vol = axes[2]
        self.panel_axes = {pk: axes[2 * pid] for pk, pid in self.panel_map.items()}
        self.ax.set_facecolor(SURFACE)
        for a in self.fig.axes:
            a.tick_params(labelsize=14)
            a.grid(True, color=GRID, linewidth=0.9, alpha=0.85)
        self.fig.subplots_adjust(left=0.035, right=0.945, top=0.865, bottom=0.055, hspace=0.10)
        if self.overlay_legend:
            handles = [plt.Line2D([], [], color=c, lw=3) for _, c in self.overlay_legend]
            self.ax.legend(handles, [n for n, _ in self.overlay_legend], loc="upper left",
                           fontsize=13, frameon=True, facecolor="white", edgecolor=GRID, framealpha=0.9)
        return self

    # ------------------------------------------------------------ chrome

    def chrome(self):
        c = self.case
        meta = ds.META[self.name]
        focal = c["focal_ts"]
        fdate = focal.strftime("%Y-%m-%d %H:%M UTC") if self.tf in ("1H", "4H") else focal.strftime("%Y-%m-%d")
        fig = self.fig
        fig.text(0.035, 0.975, f"{meta['ticker']}", fontsize=30, fontweight="bold", color=INK, va="top")
        fig.text(0.035, 0.938, meta["market"], fontsize=15, color=INK2, va="top")
        fig.text(0.035, 0.912, f"Timeframe: {ds.TF_LABEL[self.tf]}   |   Focal bar: {fdate}   |   Times: {meta['tz']}",
                 fontsize=14, color=MUTED, va="top")
        # concept badge, right side
        fig.text(0.945, 0.968, c["concept"], fontsize=23, fontweight="bold", color="white",
                 ha="right", va="top",
                 bbox=dict(boxstyle="round,pad=0.45", facecolor=c.get("badge", "#1F2937"), edgecolor="none"))
        fig.text(0.945, 0.915, f"Case {c['num']:03d}  ·  {c['category']}", fontsize=14,
                 color=INK2, ha="right", va="top")
        # provenance footer
        fig.text(0.5, 0.008,
                 f"REAL HISTORICAL DATA — {meta['market']} · {meta['source']} · rendered with mplfinance; "
                 "every candle is the published historical OHLCV record, no simulated prices",
                 fontsize=11.5, color=MUTED, ha="center", va="bottom", style="italic")

    def lesson(self, lines, loc="lower left"):
        txt = "\n".join("•  " + "\n   ".join(textwrap.wrap(l, 58)) for l in lines)
        x, ha = (0.012, "left") if "left" in loc else (0.988, "right")
        y, va = (0.02, "bottom") if "lower" in loc else (0.97, "top")
        self.ax.text(x, y, txt, transform=self.ax.transAxes, fontsize=13.6, color=INK,
                     ha=ha, va=va, linespacing=1.55, zorder=20,
                     bbox=dict(boxstyle="round,pad=0.6", facecolor="#FFFFFF",
                               edgecolor="#CBD5E1", alpha=0.93))

    # ------------------------------------------------------------ primitives

    def zone(self, x0, x1, y0, y1, color=NEUT, label=None, alpha=0.13, label_loc="left", lw=1.6):
        x0, x1 = self.x(x0), self.x(x1)
        self.ax.add_patch(Rectangle((x0, min(y0, y1)), x1 - x0, abs(y1 - y0),
                                    facecolor=color, edgecolor=color, alpha=alpha, lw=0, zorder=3))
        self.ax.add_patch(Rectangle((x0, min(y0, y1)), x1 - x0, abs(y1 - y0),
                                    facecolor="none", edgecolor=color, lw=lw, zorder=4))
        if label:
            lx = x0 if label_loc == "left" else x1
            ha = "right" if label_loc == "left" else "left"
            self.ax.text(lx - 0.4 if label_loc == "left" else lx + 0.4, (y0 + y1) / 2, label,
                         fontsize=14, fontweight="bold", color=color, ha=ha, va="center", zorder=15,
                         bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=color, alpha=0.9))

    def ray(self, x0, y, color=NEUT, label=None, x1=None, ls="--", lw=2.0, label_side="right"):
        x0 = self.x(x0)
        x1 = self.x(x1) if x1 is not None else len(self.df) - 0.2
        self.ax.plot([x0, x1], [y, y], color=color, ls=ls, lw=lw, zorder=6)
        if label:
            if label_side == "right":
                self.ax.text(x1 - 0.5, y, label, fontsize=13.5, fontweight="bold", color=color,
                             ha="right", va="center", zorder=15,
                             bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor=color, alpha=0.9))
            else:
                self.ax.text(x0 - 0.3, y, label, fontsize=13.5, fontweight="bold", color=color,
                             ha="right", va="center", zorder=15,
                             bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="none", alpha=0.85))

    def seg(self, i1, p1, i2, p2, color=INK, lw=2.4, ls="-"):
        self.ax.plot([self.x(i1), self.x(i2)], [p1, p2], color=color, lw=lw, ls=ls, zorder=7)

    def arrow(self, i_from, p_from, i_to, p_to, color=INK, lw=2.6, style="-|>", mut=26):
        a = FancyArrowPatch((self.x(i_from), p_from), (self.x(i_to), p_to),
                            arrowstyle=style, mutation_scale=mut, color=color, lw=lw, zorder=12,
                            shrinkA=2, shrinkB=2)
        self.ax.add_patch(a)

    def mark(self, i, p, color=GOLD, r=420, marker="o"):
        self.ax.scatter([self.x(i)], [p], s=r, facecolors="none", edgecolors=color,
                        linewidths=3.0, marker=marker, zorder=12)

    def callout(self, i, p, text, dx=6, dy_frac=0.06, color=INK, fontsize=14.5):
        ylo, yhi = self.ax.get_ylim()
        dy = (yhi - ylo) * dy_frac
        self.ax.annotate(text, xy=(self.x(i), p), xytext=(self.x(i) + dx, p + dy),
                         fontsize=fontsize, fontweight="bold", color=color, zorder=15,
                         ha="left" if dx >= 0 else "right",
                         arrowprops=dict(arrowstyle="-|>", color=color, lw=2.2,
                                         shrinkA=0, shrinkB=4),
                         bbox=dict(boxstyle="round,pad=0.35", facecolor="white",
                                   edgecolor=color, alpha=0.92))

    def label(self, i, p, text, color=INK, fontsize=14.5, va="bottom", ha="center", boxed=True):
        kw = dict(fontsize=fontsize, fontweight="bold", color=color, ha=ha, va=va, zorder=15)
        if boxed:
            kw["bbox"] = dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=color, alpha=0.9)
        self.ax.text(self.x(i), p, text, **kw)

    # ------------------------------------------------------------ composites

    def trade(self, entry_i, entry, sl, tps, side, extend=None):
        """Entry/SL/TP block with shaded risk & reward and R:R math."""
        x0 = self.x(entry_i)
        x1 = self.x(extend) if extend is not None else len(self.df) - 0.2
        risk = abs(entry - sl)
        self.ax.add_patch(Rectangle((x0, min(entry, sl)), x1 - x0, abs(entry - sl),
                                    facecolor=STOP, alpha=0.10, lw=0, zorder=2))
        best_tp = tps[-1]
        self.ax.add_patch(Rectangle((x0, min(entry, best_tp)), x1 - x0, abs(best_tp - entry),
                                    facecolor=TARGET, alpha=0.10, lw=0, zorder=2))
        self.ax.plot([x0, x1], [entry, entry], color=ENTRY, lw=2.6, zorder=8)
        self.ax.plot([x0, x1], [sl, sl], color=STOP, lw=2.6, zorder=8)
        f = lambda v: fmt_price(v, self.dataset)
        box = lambda c: dict(boxstyle="round,pad=0.28", facecolor="white", edgecolor=c, alpha=0.92)
        self.ax.text(x1 - 0.5, entry, f"ENTRY {f(entry)}", fontsize=13.5, fontweight="bold",
                     color=ENTRY, va="center", ha="right", zorder=15, bbox=box(ENTRY))
        self.ax.text(x1 - 0.5, sl, f"SL {f(sl)}", fontsize=13.5, fontweight="bold",
                     color=STOP, va="center", ha="right", zorder=15, bbox=box(STOP))
        for k, tp in enumerate(tps, 1):
            rr = abs(tp - entry) / risk if risk else 0
            self.ax.plot([x0, x1], [tp, tp], color=TARGET, lw=2.2, ls="--", zorder=8)
            self.ax.text(x1 - 0.5, tp, f"TP{k} {f(tp)}  ({rr:.1f}R)", fontsize=13.5,
                         fontweight="bold", color=TARGET, va="center", ha="right", zorder=15, bbox=box(TARGET))

    def premium_discount(self, i_lo, p_lo, i_hi, p_hi, x_end=None):
        """Premium/discount halves of a real dealing range + equilibrium."""
        x0 = self.x(min(i_lo, i_hi))
        x1 = self.x(x_end) if x_end is not None else len(self.df) - 0.2
        eq = (p_lo + p_hi) / 2
        self.ax.add_patch(Rectangle((x0, eq), x1 - x0, p_hi - eq, facecolor=DOWN, alpha=0.07, lw=0, zorder=2))
        self.ax.add_patch(Rectangle((x0, p_lo), x1 - x0, eq - p_lo, facecolor=UP, alpha=0.07, lw=0, zorder=2))
        self.ax.plot([x0, x1], [eq, eq], color=MUTED, lw=2.0, ls=(0, (6, 3)), zorder=6)
        bx = lambda c: dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor=c, alpha=0.9)
        self.ax.text(x1 - 0.5, p_hi, "PREMIUM", fontsize=13, fontweight="bold", color=DOWN, va="center", ha="right", bbox=bx(DOWN), zorder=15)
        self.ax.text(x1 - 0.5, eq, f"EQ 50%  {fmt_price(eq, self.dataset)}", fontsize=12.5, fontweight="bold", color=MUTED, va="center", ha="right", bbox=bx(MUTED), zorder=15)
        self.ax.text(x1 - 0.5, p_lo, "DISCOUNT", fontsize=13, fontweight="bold", color=UP, va="center", ha="right", bbox=bx(UP), zorder=15)

    def fib(self, i_lo, p_lo, i_hi, p_hi, levels=(0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0),
            ext=(), color=GOLD):
        lo_first = i_lo < i_hi
        x0 = self.x(min(i_lo, i_hi))
        x1 = len(self.df) - 0.2
        d = p_hi - p_lo
        for lv in levels:
            p = p_hi - lv * d if lo_first else p_lo + lv * d
            self.ax.plot([x0, x1], [p, p], color=color, lw=1.6, ls="-", alpha=0.75, zorder=5)
            self.ax.text(x1 - 0.4, p, f"{lv:.3f}  {fmt_price(p, self.dataset)}", fontsize=12,
                         color=color, va="center", ha="right", fontweight="bold",
                         bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=0.75), zorder=14)
        for lv in ext:
            p = p_lo + lv * d if lo_first else p_hi - lv * d
            self.ax.plot([x0, x1], [p, p], color=LIQ, lw=1.6, ls=(0, (4, 3)), alpha=0.8, zorder=5)
            self.ax.text(x1 - 0.4, p, f"{lv:.3f} ext  {fmt_price(p, self.dataset)}", fontsize=12,
                         color=LIQ, va="center", ha="right", fontweight="bold",
                         bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=0.75), zorder=14)

    def session(self, hours, label, color=GOLD, alpha=0.10):
        """Shade all bars whose UTC hour is in `hours` (intraday only)."""
        hrs = self.df.index.hour
        in_s = np.isin(hrs, hours)
        start = None
        for k in range(len(self.df) + 1):
            on = k < len(self.df) and in_s[k]
            if on and start is None:
                start = k
            elif not on and start is not None:
                self.ax.axvspan(start - 0.5, k - 0.5, facecolor=color, alpha=alpha, zorder=1)
                start = None
        ylo, yhi = self.ax.get_ylim()
        first = np.argmax(in_s) if in_s.any() else 0
        self.ax.text(first, yhi - (yhi - ylo) * 0.015, label, fontsize=13, fontweight="bold",
                     color=color, ha="left", va="top", zorder=15,
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=color, alpha=0.85))

    def volume_profile(self, prof, width_frac=0.16):
        """Horizontal volume-at-price histogram on the right of the price panel."""
        v = prof["volume"] / prof["volume"].max()
        n = len(self.df)
        x_base = n - 0.5
        for c, vv in zip(prof["centers"], v):
            self.ax.barh(c, -vv * n * width_frac, left=x_base, height=(prof["centers"][1] - prof["centers"][0]) * 0.85,
                         color="#94A3B8", alpha=0.45, zorder=2)
        for key, col, lab in [("poc", GOLD, "POC"), ("vah", DOWN, "VAH"), ("val", UP, "VAL")]:
            self.ray(self.w0, prof[key], color=col, label=f"{lab}  {fmt_price(prof[key], self.dataset)}", lw=2.2)

    # ------------------------------------------------------------ save

    def save(self, path):
        self.chrome()
        self.fig.savefig(path, dpi=DPI, facecolor=SURFACE)
        plt.close(self.fig)
