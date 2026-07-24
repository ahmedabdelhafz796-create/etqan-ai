"""Wyckoff, Elliott Wave and Fibonacci case builders (~40 plates)."""

from __future__ import annotations

import numpy as np

from . import annotate as an
from . import data_sources as ds
from . import detectors as det
from .cases_util import plan, take, trade_from

WY = "Wyckoff"
EW = "Elliott Wave"
FIB = "Fibonacci"

L = {
    "SPRING": ["The composite operator shook the range's lows — a Spring: a false break that finds no supply.",
               "The immediate reclaim and rally reveal absorption: the sell-stops were bought, not sold.",
               "Springs are the lowest-risk longs in accumulation: risk the Spring low, target the range top and beyond."],
    "UT": ["An Upthrust pushed above the range and failed — the mirror of the Spring: demand tested and found absent.",
           "The rejection back inside traps breakout buyers and marks distribution's hand.",
           "Shorts risk the Upthrust high; the range bottom is the first objective."],
    "ACC": ["A Wyckoff accumulation: selling climax, automatic rally, secondary tests, a Spring, then Sign of Strength.",
            "The range is a campaign — the operator buys from panicked sellers over weeks, not in one bar.",
            "The markup only leaves once the float has changed hands; the labeled phases show the sequence."],
    "DIST": ["A Wyckoff distribution: buying climax, automatic reaction, upthrusts, then Sign of Weakness.",
             "Strength is sold to latecomers inside the range before the markdown.",
             "LPSY rallies — weaker each time — are the exits and the short entries."],
    "SOS": ["A Sign of Strength: a wide-range advance out of the range on expanding volume, then a Last Point of Support.",
            "The LPS pullback — shallow, quiet — is the professional's entry, not the SOS bar itself.",
            "Risk under the LPS; the cause built in the range projects the effect above it."],
    "SOW": ["A Sign of Weakness: a break that gives ground on expanded volume, then a weak rally (LPSY).",
            "The inability to reclaim the range floor confirms supply has control.",
            "Shorts on the LPSY with risk above it, riding the markdown."],
    "IMP": ["A five-wave impulse: motive waves 1-3-5 in the trend, corrective 2 and 4 against it.",
            "The rules hold here: wave 2 keeps above the origin, wave 3 is not the shortest, wave 4 stays out of wave 1's territory.",
            "Impulse identification is about position: after 5, expect the largest correction of the sequence."],
    "ABC": ["A three-wave A-B-C correction against the prior trend.",
            "C commonly relates to A by equality or 1.618 — the measured relationship is drawn.",
            "Corrections are counter-trend: the trade is positioning for the *next* motive wave at C's completion."],
    "EXT": ["An extended third wave: the impulse's engine, typically reaching 1.618 of wave 1 or beyond.",
            "Extensions explain why 'overbought' fails as a short signal mid-trend.",
            "The fib extension grid drawn from waves 1-2 projected the terminus in advance."],
    "DIAG": ["A diagonal: overlapping, wedge-shaped waves at the end of a larger move.",
             "Terminal diagonals warn of exhaustion — expect a sharp reversal once the boundary breaks.",
             "The whole diagonal's origin is the reversal's minimum objective."],
    "RETR": ["The pullback found support precisely in the fib retracement cluster of the prior leg.",
             "Fibs work as consensus focal points: enough participants act there to make them self-fulfilling.",
             "Confluence (fib + structure + prior zone) beats any single level."],
    "EXT2": ["Fib extensions of the prior leg projected the target grid; price delivered into 1.272/1.618.",
             "Extensions provide objective take-profit placement when there is no structure to the left.",
             "Scaling out across the grid converts a good entry into a managed campaign."],
    "CLUS": ["Two independent fib measurements from different legs land at almost the same price — a cluster.",
             "Overlapping projections concentrate orders and sharpen the level's gravity.",
             "The reaction at the cluster is drawn from the real data — no curve fitting after the fact."],
    "TZ": ["Fibonacci time zones: vertical intervals at 1, 2, 3, 5, 8, 13, 21 bars from the pivot.",
           "Time symmetry complements price symmetry — turns cluster near the later zones.",
           "Use time zones as *alert* windows, never as standalone triggers."],
}


def build_wyckoff():
    plans = []
    for dsn, n in [("GOOG_D", 2), ("EURUSD_1H", 1), ("SUPOR_D", 1)]:
        df = ds.load(dsn)
        for ev in take(det.spring_upthrust(df, kind="spring"), dsn, n, min_gap=30):
            def draw(p, ev=ev, dfx=df):
                p.zone(ev["start"], ev["i"] - 1, ev["bot"], ev["top"], color=an.NEUT, alpha=0.08, label="trading range")
                p.ray(ev["start"], ev["bot"], color=an.INK, x1=min(ev["i"] + 10, p.w1 - 1), ls="-")
                p.mark(ev["i"], dfx.Low.iloc[ev["i"]], color=an.UP, r=700)
                p.callout(ev["i"], dfx.Low.iloc[ev["i"]], "SPRING: false break of the range low,\nimmediate reclaim", dx=4, dy_frac=-0.1, color=an.UP)
                entry = ev["bot"] * 1.002
                e, s, tps = trade_from(entry, dfx.Low.iloc[ev["i"]] * 0.997, "bull", rs=(1, 2, 3))
                p.trade(min(ev["i"] + 2, p.w1 - 2), e, s, tps, "bull")
            plans.append(plan(dsn, ev["i"], "Wyckoff Spring", WY, draw, L["SPRING"],
                              before=(ev["i"] - ev["start"]) + 12, after=30, score=ev["score"]))
    for dsn, n in [("GOOG_D", 2), ("EURUSD_4H", 1), ("ASML_D", 1)]:
        df = ds.load(dsn)
        for ev in take(det.spring_upthrust(df, kind="upthrust"), dsn, n, min_gap=30):
            def draw(p, ev=ev, dfx=df):
                p.zone(ev["start"], ev["i"] - 1, ev["bot"], ev["top"], color=an.NEUT, alpha=0.08, label="trading range")
                p.ray(ev["start"], ev["top"], color=an.INK, x1=min(ev["i"] + 10, p.w1 - 1), ls="-")
                p.mark(ev["i"], dfx.High.iloc[ev["i"]], color=an.DOWN, r=700)
                p.callout(ev["i"], dfx.High.iloc[ev["i"]], "UPTHRUST: break above fails,\nclose back inside", dx=4, dy_frac=0.1, color=an.DOWN)
                entry = ev["top"] * 0.998
                e, s, tps = trade_from(entry, dfx.High.iloc[ev["i"]] * 1.003, "bear", rs=(1, 2, 3))
                p.trade(min(ev["i"] + 2, p.w1 - 2), e, s, tps, "bear")
            plans.append(plan(dsn, ev["i"], "Wyckoff Upthrust (UTAD)", WY, draw, L["UT"],
                              before=(ev["i"] - ev["start"]) + 12, after=30, score=ev["score"]))

    # full accumulation / distribution schematics on the best spring/upthrust contexts
    for dsn, kind, n in [("GOOG_D", "spring", 1), ("EURUSD_4H", "spring", 1),
                         ("GOOG_D", "upthrust", 1), ("SUPOR_D", "upthrust", 1)]:
        df = ds.load(dsn)
        for ev in take(det.spring_upthrust(df, kind=kind), dsn, n, min_gap=50):
            acc = kind == "spring"
            def draw(p, ev=ev, dfx=df, acc=acc):
                s0 = ev["start"]
                p.zone(s0, ev["i"] - 1, ev["bot"], ev["top"], color=an.NEUT, alpha=0.07,
                       label="ACCUMULATION" if acc else "DISTRIBUTION")
                seg = dfx.iloc[max(0, s0 - 8) : s0 + 6]
                if acc:
                    sc_i = int(dfx.index.get_loc(seg.Low.idxmin()))
                    p.label(sc_i, dfx.Low.iloc[sc_i], "SC", color=an.DOWN, va="top")
                    ar = dfx.iloc[sc_i : sc_i + 8]
                    ar_i = int(dfx.index.get_loc(ar.High.idxmax()))
                    p.label(ar_i, dfx.High.iloc[ar_i], "AR", color=an.UP)
                    p.label(ev["i"], dfx.Low.iloc[ev["i"]], "SPRING", color=an.UP, va="top")
                    after = dfx.iloc[ev["i"] : min(ev["i"] + 12, len(dfx))]
                    sos_i = int(dfx.index.get_loc(after.Close.idxmax()))
                    p.label(sos_i, dfx.High.iloc[sos_i], "SOS", color=an.UP)
                else:
                    bc_i = int(dfx.index.get_loc(seg.High.idxmax()))
                    p.label(bc_i, dfx.High.iloc[bc_i], "BC", color=an.UP)
                    ar = dfx.iloc[bc_i : bc_i + 8]
                    ar_i = int(dfx.index.get_loc(ar.Low.idxmin()))
                    p.label(ar_i, dfx.Low.iloc[ar_i], "AR", color=an.DOWN, va="top")
                    p.label(ev["i"], dfx.High.iloc[ev["i"]], "UT", color=an.DOWN)
                    after = dfx.iloc[ev["i"] : min(ev["i"] + 12, len(dfx))]
                    sow_i = int(dfx.index.get_loc(after.Close.idxmin()))
                    p.label(sow_i, dfx.Low.iloc[sow_i], "SOW", color=an.DOWN, va="top")
            nm = "Wyckoff Accumulation Schematic" if acc else "Wyckoff Distribution Schematic"
            plans.append(plan(dsn, ev["i"], nm, WY, draw, L["ACC" if acc else "DIST"],
                              before=(ev["i"] - ev["start"]) + 20, after=32, score=ev["score"]))

    # SOS/LPS and SOW/LPSY (2)
    for dsn, kind in [("GOOG_D", "spring"), ("EURUSD_1H", "upthrust")]:
        df = ds.load(dsn)
        evs = det.spring_upthrust(df, kind=kind)
        for ev in take(evs, dsn, 1, min_gap=45):
            bull = kind == "spring"
            def draw(p, ev=ev, dfx=df, bull=bull):
                lvl = ev["top"] if bull else ev["bot"]
                p.ray(ev["start"], lvl, color=an.INK, x1=min(ev["i"] + 14, p.w1 - 1), label="range boundary")
                after = dfx.iloc[ev["i"] : min(ev["i"] + 14, len(dfx))]
                if bull:
                    sos_i = int(dfx.index.get_loc(after.Close.idxmax()))
                    p.label(sos_i, dfx.High.iloc[sos_i], "SOS", color=an.UP)
                    back = dfx.iloc[sos_i : min(sos_i + 12, len(dfx))]
                    lps_i = int(dfx.index.get_loc(back.Low.idxmin()))
                    p.mark(lps_i, dfx.Low.iloc[lps_i], color=an.UP)
                    p.callout(lps_i, dfx.Low.iloc[lps_i], "LPS: quiet pullback holds\nabove the old range", dx=4, dy_frac=-0.09, color=an.UP)
                else:
                    sow_i = int(dfx.index.get_loc(after.Close.idxmin()))
                    p.label(sow_i, dfx.Low.iloc[sow_i], "SOW", color=an.DOWN, va="top")
                    back = dfx.iloc[sow_i : min(sow_i + 12, len(dfx))]
                    lpsy_i = int(dfx.index.get_loc(back.High.idxmax()))
                    p.mark(lpsy_i, dfx.High.iloc[lpsy_i], color=an.DOWN)
                    p.callout(lpsy_i, dfx.High.iloc[lpsy_i], "LPSY: weak rally fails under\nthe broken floor", dx=4, dy_frac=0.09, color=an.DOWN)
            nm = "SOS → LPS (markup begins)" if bull else "SOW → LPSY (markdown begins)"
            plans.append(plan(dsn, ev["i"], nm, WY, draw, L["SOS" if bull else "SOW"],
                              before=(ev["i"] - ev["start"]) + 12, after=36, score=ev["score"]))
    return plans


# ---------------------------------------------------------------- Elliott

def _impulse_candidates(df, order=7):
    zz = det.zigzag(df, order)
    out = []
    for k in range(5, len(zz)):
        s = zz[k - 5 : k + 1]
        types = [p[2] for p in s]
        if types[0] == "L" and types == ["L", "H", "L", "H", "L", "H"]:
            p0, p1, p2, p3, p4, p5 = [p[1] for p in s]
            i5 = s[5][0]
            w1, w3, w5 = p1 - p0, p3 - p2, p5 - p4
            if w1 <= 0 or w3 <= 0 or w5 <= 0:
                continue
            if p2 < p0 or p4 < p1:  # wave2 below origin / wave4 overlaps wave1
                continue
            if w3 < w1 and w3 < w5:  # wave 3 shortest
                continue
            score = (p5 - p0) / (df.High.iloc[i5] + 1e-9) * 100 + (2 if w3 > 1.5 * w1 else 0)
            out.append(dict(i=i5, score=float(score), pts=s, up=True))
    return out


def build_elliott():
    plans = []
    for dsn, n in [("GOOG_D", 2), ("EURUSD_4H", 1), ("SUPOR_D", 1)]:
        df = ds.load(dsn)
        for ev in take(_impulse_candidates(df), dsn, n, min_gap=40):
            def draw(p, ev=ev, dfx=df):
                s = ev["pts"]
                labels = ["0", "1", "2", "3", "4", "5"]
                for (i, px, t), lab in zip(s, labels):
                    p.label(i, px, lab, color=an.INK, va="bottom" if t == "H" else "top")
                for (i1, p1, _), (i2, p2, _) in zip(s[:-1], s[1:]):
                    p.seg(i1, p1, i2, p2, color=an.ENTRY, lw=2.6)
            plans.append(plan(dsn, ev["i"], "Elliott 5-Wave Impulse", EW, draw, L["IMP"],
                              before=(ev["i"] - ev["pts"][0][0]) + 15, after=28, score=ev["score"]))

    # ABC corrections: 3-swing counter-trend after an impulse
    for dsn, n in [("GOOG_D", 2), ("EURUSD_1H", 1), ("ASML_D", 1)]:
        df = ds.load(dsn)
        zz = det.zigzag(df, 6)
        cands = []
        for k in range(3, len(zz)):
            s = zz[k - 3 : k + 1]
            if [p[2] for p in s] == ["H", "L", "H", "L"]:
                pH, pA, pB, pC = [p[1] for p in s]
                a_len = pH - pA
                c_len = pB - pC
                if a_len <= 0 or c_len <= 0:
                    continue
                ratio = c_len / a_len
                if 0.7 <= ratio <= 1.9:
                    cands.append(dict(i=s[3][0], score=float(2 - abs(1 - ratio)), pts=s, ratio=ratio))
        for ev in take(cands, dsn, n, min_gap=30):
            def draw(p, ev=ev, dfx=df):
                s = ev["pts"]
                for (i, px, t), lab in zip(s, ["", "A", "B", "C"]):
                    if lab:
                        p.label(i, px, lab, color=an.DOWN, va="bottom" if t == "H" else "top")
                for (i1, p1, _), (i2, p2, _) in zip(s[:-1], s[1:]):
                    p.seg(i1, p1, i2, p2, color=an.DOWN, lw=2.4, ls="--")
                p.callout(s[3][0], s[3][1], f"C = {ev['ratio']:.2f} × A", dx=4, dy_frac=-0.08, color=an.DOWN)
            plans.append(plan(dsn, ev["i"], "A-B-C Correction", EW, draw, L["ABC"],
                              before=(ev["i"] - ev["pts"][0][0]) + 20, after=25, score=ev["score"]))

    # extended wave 3 (2): impulses where w3 > 1.618 w1
    for dsn in ["GOOG_D", "SUPOR_D"]:
        df = ds.load(dsn)
        cands = [e for e in _impulse_candidates(df)
                 if (e["pts"][3][1] - e["pts"][2][1]) > 1.6 * (e["pts"][1][1] - e["pts"][0][1])]
        for ev in take(cands, dsn, 1, min_gap=40):
            def draw(p, ev=ev, dfx=df):
                s = ev["pts"]
                for (i, px, t), lab in zip(s, ["0", "1", "2", "3 (ext)", "4", "5"]):
                    p.label(i, px, lab, color=an.INK, va="bottom" if t == "H" else "top")
                for (i1, p1, _), (i2, p2, _) in zip(s[:-1], s[1:]):
                    p.seg(i1, p1, i2, p2, color=an.ENTRY, lw=2.6)
                w1 = s[1][1] - s[0][1]
                p.fib(s[2][0], s[2][1], s[2][0] + 1, s[2][1] + w1, levels=(), ext=(1.618, 2.618))
            plans.append(plan(dsn, ev["i"], "Extended Wave 3", EW, draw, L["EXT"],
                              before=(ev["i"] - ev["pts"][0][0]) + 15, after=28, score=ev["score"]))

    # diagonal (2): wedge at end of larger trend
    for dsn in ["GOOG_D", "EURUSD_4H"]:
        df = ds.load(dsn)
        for ev in take(det.wedge(df), dsn, 1, min_gap=40):
            def draw(p, ev=ev, dfx=df):
                for pts, col in [(ev["h_pts"], an.DOWN), (ev["l_pts"], an.UP)]:
                    (x1, y1), (x2, y2) = pts[0], pts[-1]
                    m = (y2 - y1) / (x2 - x1) if x2 != x1 else 0
                    p.seg(x1, y1, min(ev["i"] + 5, p.w1 - 1), y1 + m * (ev["i"] + 5 - x1), color=col, lw=2.4)
                p.callout(ev["i"], dfx.Close.iloc[ev["i"]], "Overlapping waves in a\nterminal wedge = diagonal", dx=-14, color=an.LIQ)
            plans.append(plan(dsn, ev["i"], "Ending Diagonal", EW, draw, L["DIAG"],
                              before=(ev["i"] - ev["start"]) + 12, after=25, score=ev["score"]))
    return plans


# ---------------------------------------------------------------- Fibonacci

def build_fib():
    plans = []
    # retracement holds (5): pullback into 0.382-0.618 then resumes
    for dsn, n in [("GOOG_D", 2), ("EURUSD_1H", 1), ("EURUSD_4H", 1), ("SUPOR_D", 1)]:
        df = ds.load(dsn)
        zz = det.zigzag(df, 6)
        cands = []
        for k in range(2, len(zz)):
            a, b = zz[k - 2], zz[k - 1]
            if a[2] == "L" and b[2] == "H":
                lo_i, lo_p, hi_i, hi_p = a[0], a[1], b[0], b[1]
                rng = hi_p - lo_p
                if rng <= 0:
                    continue
                seg = df.iloc[hi_i : min(hi_i + 30, len(df))]
                if not len(seg):
                    continue
                pull = (hi_p - seg.Low.min()) / rng
                j = int(df.index.get_loc(seg.Low.idxmin()))
                after = df.iloc[j : min(j + 12, len(df))]
                resumed = after.Close.max() > hi_p - 0.15 * rng
                if 0.35 <= pull <= 0.66 and resumed:
                    lvl = min((0.382, 0.5, 0.618), key=lambda l: abs(l - pull))
                    cands.append(dict(i=j, score=float(1 - abs(lvl - pull) * 5 + rng / lo_p),
                                      leg=(lo_i, lo_p, hi_i, hi_p), lvl=lvl, pull=pull))
        for ev in take(cands, dsn, n, min_gap=25):
            def draw(p, ev=ev, dfx=df):
                lo_i, lo_p, hi_i, hi_p = ev["leg"]
                p.fib(lo_i, lo_p, hi_i, hi_p)
                p.mark(ev["i"], dfx.Low.iloc[ev["i"]], color=an.GOLD, r=600)
                p.callout(ev["i"], dfx.Low.iloc[ev["i"]],
                          f"Pullback holds the {ev['lvl']:.3f}\nretracement ({ev['pull']*100:.0f}% actual)",
                          dx=4, dy_frac=-0.09, color=an.GOLD)
                rng = hi_p - lo_p
                entry = dfx.Low.iloc[ev["i"]] + rng * 0.03
                e, s, tps = trade_from(entry, lo_p + rng * 0.15, "bull", rs=(1, 2))
                p.trade(min(ev["i"] + 2, p.w1 - 2), e, s, tps, "bull")
            plans.append(plan(dsn, ev["i"], f"Fib Retracement {ev['lvl']:.3f} Hold", FIB, draw, L["RETR"],
                              before=70, after=35, score=ev["score"]))

    # extensions reached (3)
    for dsn, n in [("GOOG_D", 1), ("EURUSD_4H", 1), ("ASML_D", 1)]:
        df = ds.load(dsn)
        zz = det.zigzag(df, 6)
        cands = []
        for k in range(3, len(zz)):
            a, b, c = zz[k - 3], zz[k - 2], zz[k - 1]
            if a[2] == "L" and b[2] == "H" and c[2] == "L":
                rng = b[1] - a[1]
                if rng <= 0 or c[1] < a[1]:
                    continue
                t1272 = c[1] + 1.272 * rng
                t1618 = c[1] + 1.618 * rng
                seg = df.iloc[c[0] : min(c[0] + 60, len(df))]
                hit = seg[seg.High >= t1272]
                if len(hit):
                    j = int(df.index.get_loc(hit.index[0]))
                    deep = seg.High.max() >= t1618
                    cands.append(dict(i=j, score=float(rng / a[1] * 100 + (2 if deep else 0)),
                                      abc=(a, b, c), t1272=t1272, t1618=t1618))
        for ev in take(cands, dsn, n, min_gap=35):
            def draw(p, ev=ev, dfx=df):
                a, b, c = ev["abc"]
                p.seg(a[0], a[1], b[0], b[1], color=an.MUTED, lw=2.0)
                p.seg(b[0], b[1], c[0], c[1], color=an.MUTED, lw=2.0, ls="--")
                for lvl, price in [(1.272, ev["t1272"]), (1.618, ev["t1618"])]:
                    p.ray(c[0], price, color=an.LIQ, label=f"{lvl} extension", ls=(0, (4, 3)))
                p.mark(ev["i"], dfx.High.iloc[ev["i"]], color=an.LIQ)
            plans.append(plan(dsn, ev["i"], "Fib Extension Targets", FIB, draw, L["EXT2"],
                              before=70, after=30, score=ev["score"]))

    # clusters (2): two legs projecting to the same zone
    for dsn in ["GOOG_D", "EURUSD_4H"]:
        df = ds.load(dsn)
        zz = det.zigzag(df, 6)
        cands = []
        for k in range(4, len(zz)):
            s = zz[k - 4 : k + 1]
            if [x[2] for x in s[:4]] == ["L", "H", "L", "H"]:
                l1, h1, l2, h2 = s[0], s[1], s[2], s[3]
                r1 = (h1[1] - l1[1]) * 0.618 + l2[1]
                r2 = (h2[1] - l2[1]) * 0.382 + l2[1]
                if abs(r1 - r2) < 0.015 * r1:
                    seg = df.iloc[h2[0] : min(h2[0] + 25, len(df))]
                    t = seg[seg.Low <= max(r1, r2)]
                    if len(t):
                        j = int(df.index.get_loc(t.index[0]))
                        cands.append(dict(i=j, score=float(1 - abs(r1 - r2) / (0.015 * r1)),
                                          z=(min(r1, r2), max(r1, r2)), legs=(l1, h1, l2, h2)))
        for ev in take(cands, dsn, 1, min_gap=35):
            def draw(p, ev=ev, dfx=df):
                l1, h1, l2, h2 = ev["legs"]
                p.seg(l1[0], l1[1], h1[0], h1[1], color=an.MUTED, lw=1.8)
                p.seg(l2[0], l2[1], h2[0], h2[1], color=an.MUTED, lw=1.8)
                p.zone(l2[0], p.w1 - 1, ev["z"][0], ev["z"][1], color=an.GOLD, label="FIB CLUSTER")
                p.mark(ev["i"], dfx.Low.iloc[ev["i"]], color=an.GOLD)
            plans.append(plan(dsn, ev["i"], "Fibonacci Confluence Cluster", FIB, draw, L["CLUS"],
                              before=60, after=30, score=ev["score"]))

    # time zones (2)
    for dsn in ["GOOG_D", "EURUSD_4H"]:
        df = ds.load(dsn)
        zz = det.zigzag(df, 8)
        lows = [p for p in zz if p[2] == "L"]
        cands = [dict(i=p[0] + 21, score=abs(p[1]) and 1.0, pivot=p) for p in lows if p[0] + 24 < len(df)]
        for ev in take(cands, dsn, 1, min_gap=50):
            def draw(p, ev=ev, dfx=df):
                piv = ev["pivot"]
                p.mark(piv[0], piv[1], color=an.GOLD, r=600)
                for fibn in (1, 2, 3, 5, 8, 13, 21):
                    x = piv[0] + fibn
                    if p.w0 < x < p.w1:
                        p.ax.axvline(p.x(x), color=an.GOLD, lw=1.4, ls=(0, (3, 3)), alpha=0.8)
                        ylo, yhi = p.ax.get_ylim()
                        p.ax.text(p.x(x), yhi - (yhi - ylo) * 0.02, str(fibn), fontsize=12,
                                  color=an.GOLD, ha="center", va="top", fontweight="bold")
            plans.append(plan(dsn, ev["i"], "Fibonacci Time Zones", FIB, draw, L["TZ"],
                              before=30, after=25, score=ev["score"]))
    return plans
