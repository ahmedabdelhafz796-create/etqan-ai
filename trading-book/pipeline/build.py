"""Assemble the catalog, render all 300 plates, write index.csv and the ZIP.

Run from trading-book/:  python3 -m pipeline.build
"""

from __future__ import annotations

import csv
import os
import traceback
import zipfile

import matplotlib.pyplot as plt
import numpy as np

from . import annotate as an
from . import data_sources as ds
from . import detectors as det
from .cases_adv import build_elliott, build_fib, build_wyckoff
from .cases_fund import build_fund
from .cases_ind import build_ind
from .cases_pa_ta import build_pa, build_ta
from .cases_smc import build_ict, build_smc
from .cases_util import BADGE, CAT_ORDER, plan, reset_used, take

TARGET = 300
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "Trading Book Images")
FOLDER = {
    "Smart Money Concepts": "SMC", "ICT": "ICT", "Price Action": "Price Action",
    "Technical Analysis": "Technical Analysis", "Indicators": "Indicators",
    "Wyckoff": "Wyckoff", "Elliott Wave": "Elliott", "Fibonacci": "Fibonacci",
    "Fundamental Analysis": "Fundamental Analysis",
}


# ---------------------------------------------------------------- filler pool

FILL_SPECS = [
    # (category, concept template, dataset, detector, overlays, panels)
    ("Smart Money Concepts", "Fair Value Gap ({side})", None, "fvg", [], []),
    ("Smart Money Concepts", "{kind} — {side}", None, "structure", [], []),
    ("Smart Money Concepts", "Liquidity Sweep", None, "sweep", [], []),
    ("Smart Money Concepts", "Order Block ({side})", None, "ob", [], []),
    ("Price Action", "Engulfing ({side})", None, "engulf", [], []),
    ("Price Action", "Pin Bar ({side})", None, "pin", [], []),
    ("Indicators", "MACD {side} Cross", None, "macd", [], ["macd"]),
]
FILL_DATASETS = ["GOOG_W", "EURUSD_4H", "SUPOR_D", "GOOG_D", "EURUSD_1H", "ASML_D", "GOOG_M", "SUPOR_W"]


def _generic_draw(kind):
    from .cases_smc import _draw_structure, _draw_sweep, _zone_trade
    from .cases_util import trade_from

    if kind == "fvg":
        return lambda p, ev, dfx: _zone_trade("FVG")(p, ev, dfx)
    if kind == "ob":
        return lambda p, ev, dfx: _zone_trade("ORDER BLOCK")(p, ev, dfx)
    if kind == "sweep":
        return _draw_sweep("Liquidity sweep")
    if kind == "structure":
        def d(p, ev, dfx):
            _draw_structure(ev["kind"])(p, ev, dfx)
        return d
    if kind == "engulf":
        def d(p, ev, dfx):
            i, side = ev["i"], ev["side"]
            col = an.UP if side == "bull" else an.DOWN
            lo = min(dfx.Low.iloc[i - 1], dfx.Low.iloc[i])
            hi = max(dfx.High.iloc[i - 1], dfx.High.iloc[i])
            p.zone(i - 1, i, lo, hi, color=col, alpha=0.10)
            p.callout(i, dfx.Close.iloc[i], f"{side} engulfing", dx=5, color=col)
            e, s, tps = trade_from(dfx.Close.iloc[i], lo if side == "bull" else hi, side, rs=(1, 2))
            p.trade(min(i + 2, p.w1 - 2), e, s, tps, side)
        return d
    if kind == "pin":
        def d(p, ev, dfx):
            i, side = ev["i"], ev["side"]
            col = an.UP if side == "bull" else an.DOWN
            wick = dfx.Low.iloc[i] if side == "bull" else dfx.High.iloc[i]
            p.mark(i, wick, color=col, r=650)
            p.callout(i, wick, "Pin bar rejection", dx=5, dy_frac=-0.1 if side == "bull" else 0.1, color=col)
        return d
    if kind == "macd":
        def d(p, ev, dfx):
            col = an.UP if ev["side"] == "bull" else an.DOWN
            p.mark(ev["i"], dfx.Close.iloc[ev["i"]], color=col)
            ax = p.panel_axes.get("macd")
            if ax:
                ax.axvline(p.x(ev["i"]), color=col, lw=1.6, ls="--")
                ax.axhline(0, color=an.MUTED, lw=1.0)
        return d
    raise KeyError(kind)


FILL_LESSON = {
    "fvg": ["A real, detected three-candle imbalance on this timeframe - the auction skipped one side.",
            "Unfilled gaps act as magnets and re-entry zones for the algorithms that created them.",
            "Trade plan drawn from the gap's own geometry: 50% entry, stop past the far edge."],
    "ob": ["The last opposite candle before the detected displacement leg - an order block on this timeframe.",
           "The return to the block is the institutional re-entry; the far edge is the invalidation.",
           "The shaded risk/reward boxes are computed from the block's real dimensions."],
    "sweep": ["A detected run of a prior swing extreme that closed back inside - liquidity swept.",
              "Stops beyond the obvious level financed the reversal that followed.",
              "Entry on the reclaim; risk beyond the sweep's wick."],
    "structure": ["A detected close beyond the marked swing - the structural event annotated on the real sequence.",
                  "Structure, not indicators, defines trend state in this framework.",
                  "The gray zigzag traces the actual swing sequence from the data."],
    "engulf": ["A detected engulfing bar with above-average body on this timeframe.",
               "One bar, full control change: the prior bar's participants are all underwater.",
               "Invalidation is the pattern's extreme; targets in R multiples."],
    "pin": ["A detected rejection bar: dominant wick, minimal body.",
            "The wick maps where the market refused to trade.",
            "Stops belong beyond the wick; entries on the body-side break."],
    "macd": ["A detected MACD/signal cross on real data, marked in both panels.",
             "Crosses aligned with structure carry; counter-structure crosses chop.",
             "The zero line separates early-trend from late-trend crosses."],
}


def build_filler(needed_by_cat):
    out = []
    for cat, need in needed_by_cat.items():
        if need <= 0:
            continue
        for dsn in FILL_DATASETS:
            if need <= 0:
                break
            try:
                df = ds.load(dsn)
            except Exception:
                continue
            if len(df) < 120:
                continue
            for cat2, tmpl, _, kind, ov, pn in FILL_SPECS:
                if cat2 != cat or need <= 0:
                    continue
                if kind == "fvg":
                    evs = det.fvg(df)
                elif kind == "ob":
                    evs = det.order_block(df)
                elif kind == "sweep":
                    evs = det.sweep(df)
                elif kind == "structure":
                    evs = det.structure_events(df)
                elif kind == "engulf":
                    evs = det.engulfing(df)
                elif kind == "pin":
                    evs = det.pin_bar(df)
                elif kind == "macd":
                    evs = det.macd_cross(df)
                else:
                    continue
                for ev in take(evs, dsn, min(need, 3), min_gap=15):
                    concept = tmpl.format(**{k: ev.get(k, "") for k in ("side", "kind")}).strip(" —-")
                    out.append(plan(dsn, ev["i"], concept, cat, _generic_draw(kind),
                                    FILL_LESSON[kind], overlays=ov, panels=pn, score=ev.get("score", 0), ev=ev))
                    need -= 1
    return out


# ---------------------------------------------------------------- macro renderer

def render_macro(pl, num, path):
    s = pl["series"]
    fig, ax = plt.subplots(figsize=(an.W_PX / an.DPI, an.H_PX / an.DPI), dpi=an.DPI)
    fig.patch.set_facecolor(an.SURFACE)
    ax.set_facecolor(an.SURFACE)
    for a, b in pl["recessions"]:
        ax.axvspan(np.datetime64(a), np.datetime64(b), color="#94A3B8", alpha=0.22, zorder=1)
    ax.plot(s.index, s.values, color=an.ENTRY, lw=2.6, zorder=5)
    ax.axhline(0, color=an.MUTED, lw=1.2)
    ax.grid(True, color=an.GRID, lw=0.9, alpha=0.85)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(labelsize=15, colors=an.INK2)
    ax.set_ylabel(pl["unit"], fontsize=16, color=an.INK2)
    last = s.iloc[-1]
    ax.annotate(f"{last:.1f}{pl['unit']}", xy=(s.index[-1], last), xytext=(10, 0),
                textcoords="offset points", fontsize=15, fontweight="bold", color=an.ENTRY, va="center")
    hi_i = s.idxmax()
    ax.annotate(f"peak {s.max():.1f}{pl['unit']} ({hi_i.year})", xy=(hi_i, s.max()),
                xytext=(0, 18), textcoords="offset points", fontsize=14, fontweight="bold",
                color=an.INK, ha="center",
                arrowprops=dict(arrowstyle="-|>", color=an.INK, lw=2))
    fig.subplots_adjust(left=0.05, right=0.97, top=0.84, bottom=0.07)
    fig.text(0.05, 0.975, pl["concept"], fontsize=30, fontweight="bold", color=an.INK, va="top")
    fig.text(0.05, 0.935, pl["subtitle"], fontsize=15, color=an.INK2, va="top")
    fig.text(0.97, 0.968, "Macro", fontsize=23, fontweight="bold", color="white", ha="right", va="top",
             bbox=dict(boxstyle="round,pad=0.45", facecolor=pl["badge"], edgecolor="none"))
    fig.text(0.97, 0.915, f"Case {num:03d}  ·  {pl['category']}", fontsize=14, color=an.INK2,
             ha="right", va="top")
    import textwrap
    txt = "\n".join("•  " + "\n   ".join(textwrap.wrap(l, 66)) for l in pl["lesson"])
    ax.text(0.012, 0.03, txt, transform=ax.transAxes, fontsize=13.6, color=an.INK,
            va="bottom", linespacing=1.55,
            bbox=dict(boxstyle="round,pad=0.6", facecolor="white", edgecolor="#CBD5E1", alpha=0.93))
    fig.text(0.5, 0.008,
             "REAL HISTORICAL DATA — U.S. quarterly macro series, statsmodels `macrodata` (St. Louis Fed FRED compilation); "
             "shaded recessions per NBER dating — no simulated values",
             fontsize=11.5, color=an.MUTED, ha="center", va="bottom", style="italic")
    fig.savefig(path, dpi=an.DPI, facecolor=an.SURFACE)
    plt.close(fig)


# ---------------------------------------------------------------- main

def render_one(pl, num, path):
    if pl.get("kind") == "macro":
        render_macro(pl, num, path)
        return
    df = ds.load(pl["dataset"])
    case = dict(num=num, category=pl["category"], concept=pl["concept"],
                dataset=pl["dataset"], focal_ts=pl["focal_ts"], badge=pl["badge"])
    p = an.Plate(case, df, pl["w0"], pl["w1"], overlays=pl["overlays"], panels=pl["panels"]).open()
    if pl.get("ev") is not None:
        pl["draw"](p, pl["ev"], df)
    else:
        pl["draw"](p)
    p.lesson(pl["lesson"])
    p.save(path)


def main():
    reset_used()
    plans = []
    for fn in (build_fund, build_smc, build_ict, build_pa, build_ta, build_ind,
               build_wyckoff, build_elliott, build_fib):
        got = fn()
        print(f"{fn.__name__}: {len(got)}")
        plans.extend(got)

    by_cat = {c: [p for p in plans if p["category"] == c] for c in CAT_ORDER}
    total = sum(len(v) for v in by_cat.values())
    print("built:", total, {FOLDER[c]: len(v) for c, v in by_cat.items()})
    if total < TARGET:
        # top up SMC / PA / Indicators with real detected surplus events
        deficit = TARGET - total
        share = {"Smart Money Concepts": 0, "Price Action": 0, "Indicators": 0}
        keys = list(share)
        for k in range(deficit):
            share[keys[k % 3]] += 1
        extra = build_filler(share)
        for p in extra:
            by_cat[p["category"]].append(p)
        total = sum(len(v) for v in by_cat.values())
        print("after filler:", total)
    # trim overshoot (lowest score first within the largest categories)
    while total > TARGET:
        big = max(by_cat, key=lambda c: len(by_cat[c]))
        by_cat[big].sort(key=lambda p: -p.get("score", 0))
        by_cat[big].pop()
        total -= 1
    assert total == TARGET, total

    os.makedirs(OUT, exist_ok=True)
    rows = []
    num = 0
    failures = []
    for cat in CAT_ORDER:
        folder = os.path.join(OUT, FOLDER[cat])
        os.makedirs(folder, exist_ok=True)
        for pl in by_cat[cat]:
            num += 1
            fname = f"{num:03d}.png"
            path = os.path.join(folder, fname)
            try:
                render_one(pl, num, path)
            except Exception:
                plt.close("all")
                failures.append((num, pl["concept"], traceback.format_exc(limit=3)))
                # leave a hole; report at the end
                continue
            dsname = pl["dataset"].rsplit("_", 1)[0]
            meta = ds.META.get(dsname, {"ticker": "US-MACRO", "market": "U.S. macro (FRED)", "source": "statsmodels macrodata"})
            tf = pl["dataset"].rsplit("_", 1)[1] if pl.get("kind") != "macro" else "Quarterly"
            rows.append([fname, FOLDER[cat], meta["ticker"],
                         pl["focal_ts"].strftime("%Y-%m-%d %H:%M" if tf in ("1H", "4H") else "%Y-%m-%d"),
                         ds.TF_LABEL.get(tf, tf), pl["concept"], meta["market"], meta["source"]])
            if num % 25 == 0:
                print(f"rendered {num}/{TARGET}")

    with open(os.path.join(OUT, "index.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Image Name", "Topic", "Ticker", "Date", "Timeframe", "Concept", "Market", "Data Source"])
        w.writerows(rows)

    print(f"done: {len(rows)} rendered, {len(failures)} failures")
    for num_, c, tb in failures[:10]:
        print("FAIL", num_, c, tb.splitlines()[-1] if tb else "")

    if not failures:
        zpath = os.path.join(ROOT, "Trading_Book_300_Charts.zip")
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            for root, _, files in os.walk(OUT):
                for fn in sorted(files):
                    full = os.path.join(root, fn)
                    z.write(full, os.path.relpath(full, ROOT))
        print("zip written:", zpath, f"{os.path.getsize(zpath)/1e6:.1f} MB")


if __name__ == "__main__":
    main()
