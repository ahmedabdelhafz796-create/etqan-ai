"""Price Action + classical Technical Analysis case builders (~86 plates)."""

from __future__ import annotations

import numpy as np

from . import annotate as an
from . import data_sources as ds
from . import detectors as det
from .cases_util import plan, take, trade_from

PA = "Price Action"
TA = "Technical Analysis"

L = {
    "PIN": ["A long rejection wick with a tiny body: one side attacked, was absorbed, and paid for it into the close.",
            "The wick shows *where* the market refused to trade — that extreme becomes the stop's natural home.",
            "Entry on the break of the pin's body-side high/low; risk the far end of the wick."],
    "ENG": ["This candle's body completely engulfed the previous one — control changed hands within a single bar.",
            "Strength matters: the engulfing body exceeds the average true range, so it reflects real order flow, not drift.",
            "Trade in the engulfing direction; invalidate beyond the pattern's extreme."],
    "INSIDE": ["An inside bar is compression: the market agreed on value for a bar, coiling within the mother bar's range.",
               "The mother bar's extremes are the breakout triggers — and the fade levels for false breaks.",
               "Trade the break of the mother bar with stop at its midpoint or opposite extreme."],
    "OUTSIDE": ["An outside bar swallowed the entire prior range — volatility expansion and a two-sided fight resolved by the close.",
                "The close's position inside the bar tells you who won.",
                "Continuation entries follow the close direction; the opposite extreme is the invalidation."],
    "TREND": ["A regression channel with high R² — this market trended cleanly, and every touch of the channel edges was tradeable.",
              "Trend trading is buying the lower rail in an up channel, never selling it because it 'looks high'.",
              "The break of the channel — with momentum — is the first exit signal for trend positions."],
    "BRK": ["A multi-touch level finally broke with an expansion candle and above-average volume.",
            "Breakouts fail when they happen quietly; this one had range and participation.",
            "Entry on the close beyond the level or on the retest; stop back inside the range."],
    "RETEST": ["After the breakout, price returned to the broken level and held — old resistance acting as new support.",
               "The retest is the highest-probability entry of the breakout sequence: risk is smallest and the trap is visible.",
               "Stop below the retest low; targets project the height of the broken range."],
    "SR": ["This level was defended repeatedly — each touch is marked. Support/resistance is memory of unfinished business.",
           "The more touches, the more stops accumulate behind the level — strength and fragility grow together.",
           "Trade reactions at the level with tight invalidation, or trade its clean break; never mid-range."],
    "FAKE": ["Price broke the obvious level, found no follow-through, and snapped back — a textbook fakeout.",
             "Breakout traders' stops fueled the reversal: the failure is more tradeable than the break.",
             "Entry on re-entry into the range; stop beyond the false-break extreme."],
    "COMP": ["Contraction precedes expansion: ranges tightened bar after bar before the release.",
             "Volatility is cyclical — the squeeze tells you *when* a move is due, structure tells you *which way*.",
             "Position before the release with the compression extreme as risk, or join the expansion candle."],
    "HS": ["Head & Shoulders: the failure of the third push (the right shoulder cannot reach the head) exposes trend exhaustion.",
           "The neckline break confirms; its measured objective projects the head-to-neckline height.",
           "Volume typically fades across the pattern and returns on the break — exactly what happened here."],
    "DT": ["The second test of the extreme failed at (nearly) the same price — a double top/bottom with a clear neckline.",
           "The pattern completes only on the neckline break; early entries are guesses.",
           "Measured move: pattern height projected from the neckline; stop above/below the second extreme."],
    "FLAG": ["A violent pole then a tight counter-drift: the flag is the market catching its breath, not changing its mind.",
             "Shallow, low-volume pullbacks after impulsive moves resolve in the pole's direction far more often than not.",
             "Entry on the flag break; target projects the full pole height from the breakout."],
    "TRI": ["Converging swing highs and lows — the triangle compresses until one side runs out of orders.",
            "Ascending/descending variants tip their hand: the flat side is the accumulating side.",
            "Trade the break with the measured height as target; the apex area itself is chop, avoid it."],
    "WEDGE": ["Both boundaries slope the same way but converge — momentum shrinking with every push: a terminal wedge.",
              "Rising wedges resolve down and falling wedges up far more often, because each push attracts weaker follow-through.",
              "Entry on the boundary break; stop beyond the last extreme inside the wedge."],
    "CUP": ["A rounded base (the cup) then a brief shallow handle: sellers exhausted gradually, then briefly shaken out.",
            "The handle's job is to clear late stops beneath the rim before the markup.",
            "Buy the rim breakout; the cup depth projects the target."],
    "RECT": ["A horizontal battle: matched highs and lows defining a rectangle of balanced auction.",
             "Range extremes are for fading only while acceptance holds; the eventual break carries the range height.",
             "Both playbooks are shown: rotation trades inside, then the measured breakout."],
    "GAPS": ["An opening gap that never filled during the session — initiative behavior by one side at the open.",
             "Breakaway gaps start moves, measuring gaps mark midpoints, exhaustion gaps end them; context decides.",
             "Gap-and-go trades follow the gap's direction while it holds; a full fill negates the signal."],
}


def build_pa():
    plans = []

    # pins (5)
    for dsn, n in [("GOOG_D", 2), ("EURUSD_1H", 1), ("EURUSD_4H", 1), ("SUPOR_D", 1)]:
        df = ds.load(dsn)
        for ev in take(det.pin_bar(df), dsn, n):
            def draw(p, ev=ev, dfx=df):
                i, side = ev["i"], ev["side"]
                col = an.UP if side == "bull" else an.DOWN
                wick = dfx.Low.iloc[i] if side == "bull" else dfx.High.iloc[i]
                p.mark(i, wick, color=col, r=650)
                p.callout(i, wick, "Pin bar: long rejection wick,\nbody at the opposite end", dx=5,
                          dy_frac=-0.1 if side == "bull" else 0.1, color=col)
                entry = dfx.High.iloc[i] if side == "bull" else dfx.Low.iloc[i]
                e, s, tps = trade_from(entry, wick, side, rs=(1, 2))
                p.trade(min(i + 2, p.w1 - 2), e, s, tps, side)
            plans.append(plan(dsn, ev["i"], f"Pin Bar ({ev['side']})", PA, draw, L["PIN"], score=ev["score"]))

    # engulfing (6)
    for dsn, side, n in [("GOOG_D", "bull", 2), ("GOOG_D", "bear", 1), ("EURUSD_1H", "bull", 1),
                         ("EURUSD_4H", "bear", 1), ("ASML_D", "bull", 1)]:
        df = ds.load(dsn)
        evs = [e for e in det.engulfing(df) if e["side"] == side]
        for ev in take(evs, dsn, n):
            def draw(p, ev=ev, dfx=df):
                i, side = ev["i"], ev["side"]
                col = an.UP if side == "bull" else an.DOWN
                lo = min(dfx.Low.iloc[i - 1], dfx.Low.iloc[i])
                hi = max(dfx.High.iloc[i - 1], dfx.High.iloc[i])
                p.zone(i - 1, i, lo, hi, color=col, alpha=0.10, label=None)
                p.callout(i, dfx.Close.iloc[i], f"{side} engulfing:\nbody swallows prior bar", dx=5, color=col)
                entry = dfx.Close.iloc[i]
                sl = lo if side == "bull" else hi
                e, s, tps = trade_from(entry, sl, side, rs=(1, 2))
                p.trade(min(i + 2, p.w1 - 2), e, s, tps, side)
            plans.append(plan(dsn, ev["i"], f"Engulfing ({ev['side']})", PA, draw, L["ENG"], score=ev["score"]))

    # inside / outside (5)
    for dsn, n in [("GOOG_D", 2), ("EURUSD_4H", 1)]:
        df = ds.load(dsn)
        for ev in take(det.inside_bar(df), dsn, n):
            def draw(p, ev=ev, dfx=df):
                i = ev["i"]
                p.zone(i - 1, i, ev["mother_lo"], ev["mother_hi"], color=an.NEUT, label="mother bar")
                p.callout(i, dfx.Close.iloc[i], "Inside bar coils\nwithin prior range", dx=5)
                side = "bull" if ev["brk"] >= 0 else "bear"
                entry = ev["mother_hi"] if side == "bull" else ev["mother_lo"]
                sl = ev["mother_lo"] if side == "bull" else ev["mother_hi"]
                e, s, tps = trade_from(entry, sl, side, rs=(1, 2))
                p.trade(min(i + 1, p.w1 - 2), e, s, tps, side)
            plans.append(plan(dsn, ev["i"], "Inside Bar", PA, draw, L["INSIDE"], score=ev["score"]))
    for dsn, n in [("GOOG_D", 1), ("EURUSD_1H", 1)]:
        df = ds.load(dsn)
        for ev in take(det.outside_bar(df), dsn, n):
            def draw(p, ev=ev, dfx=df):
                i = ev["i"]
                col = an.UP if ev["side"] == "bull" else an.DOWN
                p.mark(i, dfx.Close.iloc[i], color=col, r=600)
                p.callout(i, dfx.High.iloc[i], "Outside bar engulfs the prior\nrange — expansion bar", dx=4, color=col)
            plans.append(plan(dsn, ev["i"], "Outside Bar", PA, draw, L["OUTSIDE"], score=ev["score"]))

    # trend / channels (8)
    for dsn, side, n, concept in [("GOOG_D", "bull", 2, "Uptrend Channel"), ("GOOG_W", "bull", 1, "Weekly Trend"),
                                  ("EURUSD_4H", "bull", 1, "Uptrend Channel"), ("GOOG_D", "bear", 1, "Downtrend Channel"),
                                  ("SUPOR_D", "bull", 1, "Uptrend Channel"), ("EURUSD_1H", "bear", 1, "Downtrend Channel"),
                                  ("ASML_D", "bull", 1, "Trendline Respect")]:
        df = ds.load(dsn)
        evs = [e for e in det.trend_channel(df) if e["side"] == side]
        for ev in take(evs, dsn, n, min_gap=30):
            def draw(p, ev=ev, dfx=df):
                s0, i1 = ev["start"], ev["i"]
                xs = np.array([s0, i1])
                mid = ev["m"] * (xs - s0) + ev["b"]
                p.seg(s0, mid[0] + ev["up"], i1, mid[1] + ev["up"], color=an.INK, lw=2.4)
                p.seg(s0, mid[0] + ev["dn"], i1, mid[1] + ev["dn"], color=an.INK, lw=2.4)
                p.seg(s0, mid[0], i1, mid[1], color=an.MUTED, lw=1.6, ls="--")
                p.label((s0 + i1) // 2, mid[1] + ev["up"], f"R² = {ev['score']:.2f}", color=an.INK)
            plans.append(plan(dsn, ev["i"], concept, PA, draw, L["TREND"],
                              before=(ev["i"] - ev["start"]) + 12, after=25, score=ev["score"]))

    # breakout + retest + S/R + fakeout (13)
    for dsn, n_b, n_r, n_s, n_f in [("GOOG_D", 2, 1, 2, 1), ("EURUSD_1H", 1, 1, 1, 1), ("SUPOR_D", 1, 1, 1, 1)]:
        df = ds.load(dsn)
        rects = det.rectangle_range(df)
        # breakout events: range then close beyond
        b_c, r_c, f_c = [], [], []
        for r in rects:
            seg = df.iloc[r["i"] : min(r["i"] + 30, len(df))]
            up = seg[seg.Close > r["top"] * 1.002]
            dn = seg[seg.Close < r["bot"] * 0.998]
            first_up = df.index.get_loc(up.index[0]) if len(up) else None
            first_dn = df.index.get_loc(dn.index[0]) if len(dn) else None
            j = None
            if first_up is not None and (first_dn is None or first_up < first_dn):
                j, side, lvl = first_up, "bull", r["top"]
            elif first_dn is not None:
                j, side, lvl = first_dn, "bear", r["bot"]
            if j is None:
                continue
            after = df.iloc[j : j + 12]
            good = after.Close.iloc[-1] > lvl if side == "bull" else after.Close.iloc[-1] < lvl
            e = dict(i=int(j), score=r["score"] * (2 if good else 1), side=side, lvl=lvl, r=r)
            (b_c if good else f_c).append(e)
            if good:
                # retest: price returns to lvl after break
                back = df.iloc[j + 2 : j + 25]
                t = back[back.Low <= lvl] if side == "bull" else back[back.High >= lvl]
                if len(t):
                    r_c.append(dict(e, i=int(df.index.get_loc(t.index[0]))))
        def mk_draw(kind):
            def draw(p, ev, dfx):
                r = ev["r"]
                p.zone(r["start"], min(ev["i"], r["i"]), r["bot"], r["top"], color=an.NEUT, alpha=0.08, label="range")
                p.ray(r["start"], ev["lvl"], color=an.INK, x1=min(ev["i"] + 8, p.w1 - 1),
                      label="breakout level", ls="-")
                col = an.UP if ev["side"] == "bull" else an.DOWN
                if kind == "brk":
                    p.callout(ev["i"], dfx.Close.iloc[ev["i"]], "Expansion close beyond the range", dx=4, color=col)
                elif kind == "retest":
                    p.mark(ev["i"], ev["lvl"], color=col)
                    p.callout(ev["i"], ev["lvl"], "Retest holds:\nold resistance = new support" if ev["side"] == "bull"
                              else "Retest holds:\nold support = new resistance", dx=4, color=col)
                    height = r["top"] - r["bot"]
                    entry = ev["lvl"]
                    sl = entry - height * 0.35 if ev["side"] == "bull" else entry + height * 0.35
                    tp = entry + height if ev["side"] == "bull" else entry - height
                    p.trade(min(ev["i"] + 2, p.w1 - 2), entry, sl, [tp], ev["side"])
                else:
                    p.callout(ev["i"], dfx.Close.iloc[ev["i"]], "No follow-through —\nfakeout & snap-back", dx=4, color=an.LIQ)
            return draw
        for ev in take(b_c, dsn, n_b, min_gap=25):
            plans.append(plan(dsn, ev["i"], f"Breakout ({ev['side']})", PA, mk_draw("brk"), L["BRK"],
                              before=55, after=30, score=ev["score"], ev=ev))
        for ev in take(r_c, dsn, n_r, min_gap=25):
            plans.append(plan(dsn, ev["i"], "Break & Retest", PA, mk_draw("retest"), L["RETEST"],
                              before=55, after=30, score=ev["score"], ev=ev))
        for ev in take(f_c, dsn, n_f, min_gap=25):
            plans.append(plan(dsn, ev["i"], "Fakeout (failed break)", PA, mk_draw("fake"), L["FAKE"],
                              before=55, after=30, score=ev["score"], ev=ev))
        # S/R multi-touch levels
        sr_c = []
        for kind in ("H", "L"):
            for e in det.equal_levels(df, tol_frac=0.006 if not dsn.startswith("EURUSD") else 0.003, kind=kind):
                sr_c.append(dict(e, score=e["score"]))
        for ev in take(sr_c, dsn, n_s, min_gap=30):
            def draw(p, ev=ev, dfx=df):
                col = an.DOWN if ev["kind"] == "H" else an.UP
                nm = "RESISTANCE" if ev["kind"] == "H" else "SUPPORT"
                p.ray(max(p.w0 + 1, ev["i1"] - 4), ev["level"], color=col, label=nm, ls="-")
                px = dfx.High if ev["kind"] == "H" else dfx.Low
                for j in (ev["i1"], ev["i2"]):
                    p.mark(j, px.iloc[j], color=col)
            nm = "Resistance Level" if ev["kind"] == "H" else "Support Level"
            plans.append(plan(dsn, ev["i"], nm, PA, draw, L["SR"], before=55, after=35, score=ev["score"]))

    # compression → expansion (2)
    for dsn, n in [("GOOG_D", 1), ("EURUSD_4H", 1)]:
        df = ds.load(dsn)
        for ev in take(det.bb_squeeze(df), dsn, n):
            def draw(p, ev=ev, dfx=df):
                i = ev["i"]
                seg = dfx.iloc[max(p.w0, i - 12) : i + 1]
                p.zone(max(p.w0, i - 12), i, seg.Low.min(), seg.High.max(), color=an.NEUT, label="compression")
                col = an.UP if ev["side"] == "bull" else an.DOWN
                p.arrow(i, dfx.Close.iloc[i], min(i + 8, p.w1 - 2), dfx.Close.iloc[min(i + 8, len(dfx) - 1)],
                        color=col, lw=3.0)
                p.label(min(i + 8, p.w1 - 2), dfx.Close.iloc[min(i + 8, len(dfx) - 1)], "expansion", color=col)
            plans.append(plan(dsn, ev["i"], "Compression → Expansion", PA, draw, L["COMP"], score=ev["score"]))

    return plans


def build_ta():
    plans = []

    # H&S + inverse (6)
    for dsn, inv, n in [("GOOG_D", False, 2), ("SUPOR_D", False, 1), ("GOOG_D", True, 2), ("EURUSD_4H", True, 1)]:
        df = ds.load(dsn)
        evs = [e for e in det.head_shoulders(df) if e["inv"] == inv]
        for ev in take(evs, dsn, n, min_gap=30):
            def draw(p, ev=ev, dfx=df):
                pts = ev["pts"]
                names = ["LS", "", "HEAD", "", "RS"]
                for (i, px, _), nm in zip(pts, names):
                    if nm:
                        p.label(i, px, nm, color=an.INK, va="bottom" if not ev["inv"] else "top")
                for (i1, p1, _), (i2, p2, _) in zip(pts[:-1], pts[1:]):
                    p.seg(i1, p1, i2, p2, color="#94A3B8", lw=2.0)
                p.ray(pts[1][0], ev["neck"], color=an.GOLD, x1=min(ev["i"] + 8, p.w1 - 1), label="neckline")
                col = an.DOWN if not ev["inv"] else an.UP
                p.callout(ev["i"], dfx.Close.iloc[ev["i"]], "Neckline break confirms", dx=4, color=col)
                height = abs(ev["pts"][2][1] - ev["neck"])
                side = "bear" if not ev["inv"] else "bull"
                entry = ev["neck"]
                sl = ev["pts"][4][1]
                tp = entry - height if side == "bear" else entry + height
                p.trade(min(ev["i"] + 2, p.w1 - 2), entry, sl, [tp], side)
            nm = "Inverse Head & Shoulders" if ev["inv"] else "Head & Shoulders"
            plans.append(plan(dsn, ev["i"], nm, TA, draw, L["HS"],
                              before=max(40, ev["i"] - ev["pts"][0][0] + 15), after=30, score=ev["score"]))

    # double tops/bottoms (8) + triple (2)
    def dbl_draw(kind):
        def draw(p, ev, dfx):
            a, c = ev["p1"], ev["p2"]
            col = an.DOWN if kind == "top" else an.UP
            for i, px, _ in (a, c):
                p.mark(i, px, color=col)
            p.seg(a[0], a[1], c[0], c[1], color=col, lw=1.8, ls=":")
            p.ray(ev["neck_i"], ev["neck"], color=an.GOLD, x1=min(ev["i"] + 8, p.w1 - 1), label="neckline")
            p.callout(ev["i"], dfx.Close.iloc[ev["i"]], "Neckline break =\npattern completion", dx=4, color=col)
            height = abs(a[1] - ev["neck"])
            side = "bear" if kind == "top" else "bull"
            tp = ev["neck"] - height if side == "bear" else ev["neck"] + height
            p.trade(min(ev["i"] + 2, p.w1 - 2), ev["neck"], c[1], [tp], side)
        return draw

    for dsn, kind, n in [("GOOG_D", "top", 2), ("EURUSD_4H", "top", 1), ("ASML_D", "top", 1),
                         ("GOOG_D", "bottom", 2), ("EURUSD_1H", "bottom", 1), ("SUPOR_D", "bottom", 1)]:
        df = ds.load(dsn)
        evs = det.double_extreme(df, kind=kind)
        for ev in take(evs, dsn, n, min_gap=30):
            nm = "Double Top" if kind == "top" else "Double Bottom"
            plans.append(plan(dsn, ev["i"], nm, TA, dbl_draw(kind), L["DT"], before=60, after=30, score=ev["score"], ev=ev))
    # triple =三 touches: reuse equal_levels with 3 hits
    for dsn, kind in [("GOOG_D", "H"), ("EURUSD_4H", "L")]:
        df = ds.load(dsn)
        evs = det.equal_levels(df, tol_frac=0.01 if not dsn.startswith("EURUSD") else 0.004, kind=kind)
        # cluster: need a third touch near same level
        cands = []
        for e in evs:
            seg = df.iloc[e["i2"] + 3 : e["i2"] + 45]
            px = seg.High if kind == "H" else seg.Low
            near = seg[(px - e["level"]).abs() <= 0.012 * e["level"]]
            if len(near):
                j = int(df.index.get_loc(near.index[0]))
                cands.append(dict(e, i=j, i3=j))
        for ev in take(cands, dsn, 1, min_gap=40):
            def draw(p, ev=ev, dfx=df):
                col = an.DOWN if ev["kind"] == "H" else an.UP
                p.ray(ev["i1"], ev["level"], color=col, x1=min(ev["i3"] + 6, p.w1 - 1),
                      label="triple " + ("top" if ev["kind"] == "H" else "bottom"))
                px = dfx.High if ev["kind"] == "H" else dfx.Low
                for j in (ev["i1"], ev["i2"], ev["i3"]):
                    p.mark(j, px.iloc[j], color=col)
            nm = "Triple Top" if kind == "H" else "Triple Bottom"
            plans.append(plan(dsn, ev["i"], nm, TA, draw, L["DT"], before=60, after=30, score=ev["score"]))

    # flags & pennants (5)
    for dsn, side, n in [("GOOG_D", "bull", 2), ("EURUSD_1H", "bull", 1), ("GOOG_D", "bear", 1), ("SUPOR_D", "bull", 1)]:
        df = ds.load(dsn)
        evs = [e for e in det.flag(df) if e["side"] == side]
        for ev in take(evs, dsn, n):
            def draw(p, ev=ev, dfx=df):
                col = an.UP if ev["side"] == "bull" else an.DOWN
                p.arrow(ev["pole_start"], dfx.Close.iloc[ev["pole_start"]], ev["pole_end"],
                        dfx.Close.iloc[ev["pole_end"]], color=col, lw=3.4)
                p.label(ev["pole_start"], dfx.Close.iloc[ev["pole_start"]], "pole", color=col)
                cons = dfx.iloc[ev["pole_end"] + 1 : ev["cons_end"] + 1]
                p.zone(ev["pole_end"] + 1, ev["cons_end"], cons.Low.min(), cons.High.max(),
                       color=an.NEUT, label="flag")
                pole_h = abs(dfx.Close.iloc[ev["pole_end"]] - dfx.Close.iloc[ev["pole_start"]])
                side_ = ev["side"]
                entry = cons.High.max() if side_ == "bull" else cons.Low.min()
                sl = cons.Low.min() if side_ == "bull" else cons.High.max()
                tp = entry + pole_h if side_ == "bull" else entry - pole_h
                p.trade(min(ev["cons_end"] + 1, p.w1 - 2), entry, sl, [tp], side_)
            nm = f"{'Bull' if ev['side']=='bull' else 'Bear'} Flag"
            plans.append(plan(dsn, ev["i"], nm, TA, draw, L["FLAG"], before=45, after=30, score=ev["score"]))

    # triangles (4) & wedges (3)
    def tri_draw(ev, dfx):
        def draw(p, ev=ev, dfx=dfx):
            for pts, col in [(ev["h_pts"], an.DOWN), (ev["l_pts"], an.UP)]:
                (x1, y1), (x2, y2) = pts[0], pts[-1]
                # extend line to focal bar
                m = (y2 - y1) / (x2 - x1) if x2 != x1 else 0
                y_end = y1 + m * (ev["i"] + 6 - x1)
                p.seg(x1, y1, min(ev["i"] + 6, p.w1 - 1), y_end, color=col, lw=2.4)
                for x, y in pts:
                    p.mark(x, y, color=col, r=260)
        return draw

    for dsn, n in [("GOOG_D", 2), ("EURUSD_4H", 1), ("EURUSD_1H", 1)]:
        df = ds.load(dsn)
        for ev in take(det.triangle(df), dsn, n, min_gap=35):
            nm = ev["kind"].capitalize() + " Triangle"
            plans.append(plan(dsn, ev["i"], nm, TA, tri_draw(ev, df), L["TRI"],
                              before=(ev["i"] - ev["start"]) + 10, after=28, score=ev["score"]))
    for dsn, n in [("GOOG_D", 2), ("SUPOR_D", 1)]:
        df = ds.load(dsn)
        for ev in take(det.wedge(df), dsn, n, min_gap=35):
            nm = ev["kind"].capitalize() + " Wedge"
            plans.append(plan(dsn, ev["i"], nm, TA, tri_draw(ev, df), L["WEDGE"],
                              before=(ev["i"] - ev["start"]) + 10, after=28, score=ev["score"]))

    # cup & handle (2)
    for dsn, n in [("GOOG_D", 1), ("SUPOR_D", 1)]:
        df = ds.load(dsn)
        for ev in take(det.cup_handle(df), dsn, n, min_gap=60):
            def draw(p, ev=ev, dfx=df):
                xs = np.arange(ev["start"], ev["cup_end"])
                seg = dfx.Close.iloc[ev["start"] : ev["cup_end"]].values
                coef = np.polyfit(xs, seg, 2)
                fit = np.polyval(coef, xs)
                for k in range(0, len(xs) - 4, 4):
                    p.seg(xs[k], fit[k], xs[k + 4], fit[k + 4], color=an.GOLD, lw=2.2)
                p.ray(ev["start"], ev["rim"], color=an.INK, x1=min(ev["i"] + 8, p.w1 - 1), label="rim")
                p.zone(ev["cup_end"], ev["i"], dfx.Low.iloc[ev["cup_end"] : ev["i"] + 1].min(),
                       dfx.High.iloc[ev["cup_end"] : ev["i"] + 1].max(), color=an.NEUT, label="handle")
            plans.append(plan(dsn, ev["i"], "Cup & Handle", TA, draw, L["CUP"],
                              before=(ev["i"] - ev["start"]) + 10, after=30, score=ev["score"]))

    # rectangles (3)
    for dsn, n in [("GOOG_D", 1), ("EURUSD_4H", 1), ("ASML_D", 1)]:
        df = ds.load(dsn)
        for ev in take(det.rectangle_range(df), dsn, n, min_gap=40):
            def draw(p, ev=ev, dfx=df):
                p.zone(ev["start"], ev["i"], ev["bot"], ev["top"], color=an.NEUT, label="RECTANGLE")
                p.ray(ev["start"], ev["top"], color=an.DOWN, x1=min(ev["i"] + 10, p.w1 - 1), ls="-")
                p.ray(ev["start"], ev["bot"], color=an.UP, x1=min(ev["i"] + 10, p.w1 - 1), ls="-")
            plans.append(plan(dsn, ev["i"], "Rectangle Range", TA, draw, L["RECT"],
                              before=(ev["i"] - ev["start"]) + 10, after=30, score=ev["score"]))

    # gaps (3): breakaway / runaway / exhaustion by context
    df = ds.load("GOOG_D")
    gev = take(det.gaps(df, min_pct=4.0), "GOOG_D", 3, min_gap=20)
    kinds = ["Breakaway Gap", "Runaway (Measuring) Gap", "Exhaustion Gap"]
    for ev, nm in zip(gev, kinds):
        def draw(p, ev=ev, dfx=df, nm=nm):
            i = ev["i"]
            lo = min(dfx.Close.iloc[i - 1], dfx.Open.iloc[i])
            hi = max(dfx.Close.iloc[i - 1], dfx.Open.iloc[i])
            p.zone(i - 1, i, lo, hi, color=an.LIQ, alpha=0.20, label=f"gap {ev['pct']:+.1f}%")
            p.callout(i, dfx.Open.iloc[i], nm, dx=5, color=an.LIQ)
        plans.append(plan("GOOG_D", ev["i"], nm, TA, draw, L["GAPS"], score=ev["score"]))

    return plans
