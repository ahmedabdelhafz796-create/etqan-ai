"""Smart Money Concepts + ICT case builders (90 plates)."""

from __future__ import annotations

import numpy as np

from . import annotate as an
from . import data_sources as ds
from . import detectors as det
from .cases_util import plan, take, trade_from, swing_leg

SMC = "Smart Money Concepts"
ICT = "ICT"


# ------------------------------------------------------------------ draws

def _zone_trade(name, extra_note=None):
    def draw(p, ev, df):
        i = ev["i"]
        side = ev["side"]
        col = an.UP if side == "bull" else an.DOWN
        p.zone(i - 1 if name == "FVG" else i, p.w1 - 1, ev["bot"], ev["top"],
               color=col, label=f"{side.upper()} {name}")
        entry = (ev["top"] + ev["bot"]) / 2
        pad = (ev["top"] - ev["bot"]) * 0.6 + 0.0015 * entry
        sl = ev["bot"] - pad if side == "bull" else ev["top"] + pad
        e, s, tps = trade_from(entry, sl, side)
        p.trade(min(i + 6, p.w1 - 2), e, s, tps, side)
        note = extra_note or ("Aggressive displacement away from the zone signals institutional interest"
                              if side == "bull" else "Strong rejection marks supply left behind by sellers")
        p.callout(i, ev["top"] if side == "bull" else ev["bot"], note, dx=-10 if i - p.w0 > (p.w1 - p.w0) * 0.6 else 8)
    return draw


def _fvg_events(dataset, side=None, n=3, min_score=0.9):
    df = ds.load(dataset)
    evs = [e for e in det.fvg(df) if e["score"] >= min_score and (side is None or e["side"] == side)]
    return take(evs, dataset, n)


def _ob_events(dataset, side=None, n=3):
    df = ds.load(dataset)
    evs = [e for e in det.order_block(df) if side is None or e["side"] == side]
    return take(evs, dataset, n)


def _draw_structure(kind):
    def draw(p, ev, df):
        col = an.UP if ev["side"] == "bull" else an.DOWN
        i = ev["i"]
        # broken level ray + zigzag path
        p.ray(ev["level_i"], ev["level"], color=col, x1=min(i + 6, p.w1 - 1),
              label=f"{'swing high' if ev['side']=='bull' else 'swing low'} broken", ls="-")
        zz = det.zigzag(df.iloc[p.w0:p.w1], 6)
        pts = [(p.w0 + a, b) for a, b, _ in zz]
        for (i1, p1), (i2, p2) in zip(pts[:-1], pts[1:]):
            p.seg(i1, p1, i2, p2, color="#94A3B8", lw=2.0, ls="-")
        p.callout(i, df.Close.iloc[i],
                  f"{kind}: close beyond the prior swing —\n"
                  + ("trend continuation confirmed" if kind == "BOS" else "first sign the trend is turning"),
                  dx=-12 if i - p.w0 > (p.w1 - p.w0) * 0.55 else 6, color=col)
        p.mark(i, df.Close.iloc[i], color=col)
    return draw


def _draw_sweep(label):
    def draw(p, ev, df):
        i = ev["i"]
        side = ev["side"]  # bull = swept lows then up
        col = an.LIQ
        p.ray(ev["level_i"], ev["level"], color=col, x1=min(i + 4, p.w1 - 1),
              label="resting liquidity", ls="--")
        wick = df.Low.iloc[i] if side == "bull" else df.High.iloc[i]
        p.mark(i, wick, color=col)
        p.callout(i, wick, f"{label}:\nwick runs the stops, close returns inside",
                  dx=-12 if i - p.w0 > (p.w1 - p.w0) * 0.55 else 6, dy_frac=-0.09 if side == "bull" else 0.09, color=col)
        entry = df.Close.iloc[i]
        sl = wick - abs(entry - wick) * 0.35 if side == "bull" else wick + abs(wick - entry) * 0.35
        e, s, tps = trade_from(entry, sl, side, rs=(1, 2, 3))
        p.trade(min(i + 3, p.w1 - 2), e, s, tps, side)
    return draw


def _draw_eq(kind_label):
    def draw(p, ev, df):
        col = an.LIQ
        i1, i2, lvl = ev["i1"], ev["i2"], ev["level"]
        p.ray(i1, lvl, color=col, x1=min(ev["i"] + 10, p.w1 - 1), label=kind_label, ls="--")
        px = df.High if ev["kind"] == "H" else df.Low
        for j in (i1, i2):
            p.mark(j, px.iloc[j], color=col)
        p.callout(i2, px.iloc[i2],
                  "Equal extremes = engineered liquidity pool;\nstops cluster just beyond this line",
                  dx=6, dy_frac=0.10 if ev["kind"] == "H" else -0.10, color=col)
    return draw


# ------------------------------------------------------------------ lessons

L = {
    "FVG": ["A displacement candle left a three-candle imbalance (Fair Value Gap) — one side of the auction was skipped.",
            "Algorithms frequently rebalance these inefficiencies before continuing, so the gap acts as a magnet and entry zone.",
            "Plan: limit order at the 50% of the gap (consequent encroachment), stop beyond the far edge, scale out at 1R/2R/3R."],
    "IFVG": ["This Fair Value Gap failed to hold — price closed straight through it, inverting its role (IFVG).",
             "What was support becomes resistance (and vice versa): the failed rebalance traps the traders who faded it.",
             "Entry on the retest of the inverted gap; stop beyond the opposite edge; targets into the next liquidity pool."],
    "OB": ["The last opposite-direction candle before the impulsive leg is the Order Block — the footprint of institutional accumulation.",
           "Retail sees a reversal candle; smart money sees where positions were built before the markup.",
           "Entry on the return to the block, stop beyond its far side; the risk box and reward boxes show the asymmetry."],
    "BB_BLOCK": ["An order block that failed and was traded through becomes a Breaker: its polarity flips.",
                 "Trapped positions from the failed zone provide the fuel when price returns to it.",
                 "Entry on the breaker retest with structure confirmation; invalidation beyond the original block."],
    "MIT": ["Price returned to the origin of the impulse and mitigated the imbalance left there before continuing.",
            "Institutions reduce inventory risk by re-delivering into their own footprint — the mitigation is the second chance entry.",
            "Confirmation is the reaction at the zone; stop below the mitigation low."],
    "BOS": ["A close beyond the prior swing extreme is a Break of Structure — the trend's order flow is intact.",
            "Each BOS re-authorizes trading with the trend; pullbacks into imbalance after a BOS are continuation entries.",
            "Countertrend traders fading the move supply the liquidity that drives it."],
    "CHOCH": ["The first close beyond the *opposite* swing is a Change of Character — the earliest structural warning of reversal.",
              "A CHoCH alone is not an entry: it defines the new dealing range to trade from.",
              "Wait for the retracement into premium/discount of the new range before committing risk."],
    "SWEEP": ["Stops resting beyond an obvious level were run in a single wick — then price closed back inside the range.",
              "Retail breakout traders entered exactly where institutions wanted counterparties; their stops financed the reversal.",
              "The sweep + reclaim is the confirmation; entries live on the reclaim close, not the break."],
    "EQH": ["Two highs at (almost) the same price look like a 'double top' to retail — to smart money they are a shelf of buy-stops.",
            "Price is drawn toward equal extremes because that is where resting orders guarantee fills for size.",
            "Expect the level to be swept before any genuine reversal; never sell blindly in front of it."],
    "EQL": ["Equal lows advertise a pool of sell-stops beneath support.",
            "The 'support holds' narrative recruits longs whose stops become the target.",
            "Trade the sweep-and-reclaim, or the continuation after the pool is consumed."],
    "PD": ["The dealing range is measured from the swing low to the swing high; 50% is equilibrium.",
           "Institutions buy in discount (below EQ) and sell in premium (above EQ) — retail chases in the wrong half.",
           "Only long setups taken in discount and shorts in premium carry positive expectancy in this framework."],
    "DISP": ["A single candle covering multiples of the average range is displacement — urgency from participants who move size.",
             "Displacement validates the zones it leaves behind (order block, FVG) and sets the directional bias.",
             "Chasing the displacement candle itself is the retail mistake; the entry is the retracement it later grants."],
    "IND": ["Before running the real pool, price manufactured a smaller, nearer pool — inducement — to bait early entries.",
            "Their stops became the liquidity that powered the move into the true point of interest.",
            "Mark the obvious minor level; assume it exists to be consumed, not respected."],
    "OTE": ["After the structural break, the retracement entered the 62%-79% pocket — ICT's Optimal Trade Entry.",
            "The OTE aligns fib depth with the premium/discount logic of the new range.",
            "Stop hides beyond the swing; first target the range midpoint, then the origin of the break."],
}


# ------------------------------------------------------------------ builders

def build_smc():
    plans = []

    # --- FVG (7)
    for dsn, side, n in [("GOOG_D", "bull", 2), ("GOOG_D", "bear", 1), ("EURUSD_1H", "bull", 2),
                         ("EURUSD_4H", "bear", 1), ("SUPOR_D", "bull", 1)]:
        for ev in _fvg_events(dsn, side, n):
            plans.append(plan(dsn, ev["i"], f"Fair Value Gap ({side})", SMC,
                              lambda p, e=ev, d=ds.load(dsn): _zone_trade("FVG")(p, e, d),
                              L["FVG"], overlays=["ema20"], panels=[], score=ev["score"]))

    # --- IFVG (3): FVG later closed through, then retested
    for dsn, n in [("GOOG_D", 2), ("EURUSD_1H", 1)]:
        df = ds.load(dsn)
        cands = []
        for e in det.fvg(df):
            i = e["i"]
            seg = df.iloc[i + 2 : i + 40]
            through = seg[seg.Close < e["bot"]] if e["side"] == "bull" else seg[seg.Close > e["top"]]
            if len(through):
                j = df.index.get_loc(through.index[0])
                cands.append(dict(e, i=j, score=e["score"], fvg_i=i))
        for ev in take(cands, dsn, n):
            def draw(p, e=None, d=None, ev=ev, dfx=df):
                i0, i = ev["fvg_i"], ev["i"]
                inv_side = "bear" if ev["side"] == "bull" else "bull"
                col = an.DOWN if inv_side == "bear" else an.UP
                p.zone(i0 - 1, p.w1 - 1, ev["bot"], ev["top"], color=col,
                       label=f"IFVG (was {ev['side']} FVG)")
                p.callout(i, dfx.Close.iloc[i], "Close through the gap\ninverts its role", dx=6, color=col)
                entry = (ev["top"] + ev["bot"]) / 2
                pad = (ev["top"] - ev["bot"]) * 0.8
                sl = ev["top"] + pad if inv_side == "bear" else ev["bot"] - pad
                e2, s2, tps = trade_from(entry, sl, inv_side)
                p.trade(min(i + 4, p.w1 - 2), e2, s2, tps, inv_side)
            plans.append(plan(dsn, ev["i"], "Inversion FVG (IFVG)", SMC, draw, L["IFVG"],
                              overlays=["ema20"], score=ev["score"]))

    # --- Order / Breaker / Mitigation blocks (10)
    for dsn, side, n in [("GOOG_D", "bull", 2), ("GOOG_D", "bear", 1),
                         ("EURUSD_1H", "bull", 2), ("EURUSD_4H", "bear", 1), ("ASML_D", "bull", 1)]:
        for ev in _ob_events(dsn, side, n):
            plans.append(plan(dsn, ev["i"], f"Order Block ({side})", SMC,
                              lambda p, e=ev, d=ds.load(dsn): _zone_trade("ORDER BLOCK")(p, e, d),
                              L["OB"], overlays=[], score=ev["score"]))
    # breaker: OB later closed through then retested
    for dsn, n in [("GOOG_D", 2), ("EURUSD_1H", 1)]:
        df = ds.load(dsn)
        cands = []
        for e in det.order_block(df):
            i = e["i"]
            seg = df.iloc[i + 3 : i + 45]
            through = seg[seg.Close < e["bot"]] if e["side"] == "bull" else seg[seg.Close > e["top"]]
            if len(through):
                j = df.index.get_loc(through.index[0])
                cands.append(dict(e, i=j, ob_i=i))
        for ev in take(cands, dsn, n):
            def draw(p, ev=ev, dfx=df):
                new_side = "bear" if ev["side"] == "bull" else "bull"
                col = an.DOWN if new_side == "bear" else an.UP
                p.zone(ev["ob_i"], p.w1 - 1, ev["bot"], ev["top"], color=col, label="BREAKER")
                p.callout(ev["i"], dfx.Close.iloc[ev["i"]],
                          "Block violated — polarity flips\n(trapped positions fuel the retest)", dx=6, color=col)
                entry = ev["top"] if new_side == "bear" else ev["bot"]
                pad = (ev["top"] - ev["bot"]) * 1.1
                sl = entry + pad if new_side == "bear" else entry - pad
                e2, s2, tps = trade_from(entry, sl, new_side)
                p.trade(min(ev["i"] + 4, p.w1 - 2), e2, s2, tps, new_side)
            plans.append(plan(dsn, ev["i"], "Breaker Block", SMC, draw, L["BB_BLOCK"], score=ev["score"]))
    # mitigation: OB retested (touch, no close-through) then continuation
    for dsn, n in [("GOOG_D", 1), ("EURUSD_4H", 1)]:
        df = ds.load(dsn)
        cands = []
        for e in det.order_block(df):
            i = e["i"]
            seg = df.iloc[i + 4 : i + 40]
            if e["side"] == "bull":
                touch = seg[(seg.Low <= e["top"]) & (seg.Close >= e["bot"])]
            else:
                touch = seg[(seg.High >= e["bot"]) & (seg.Close <= e["top"])]
            if len(touch):
                j = df.index.get_loc(touch.index[0])
                after = df.iloc[j : j + 8]
                ok = after.Close.iloc[-1] > e["top"] if e["side"] == "bull" else after.Close.iloc[-1] < e["bot"]
                if ok:
                    cands.append(dict(e, i=j, ob_i=i))
        for ev in take(cands, dsn, n):
            def draw(p, ev=ev, dfx=df):
                col = an.UP if ev["side"] == "bull" else an.DOWN
                p.zone(ev["ob_i"], p.w1 - 1, ev["bot"], ev["top"], color=col, label="MITIGATION BLOCK")
                p.arrow(ev["ob_i"] + 1, (ev["top"] + ev["bot"]) / 2, ev["i"],
                        dfx.Low.iloc[ev["i"]] if ev["side"] == "bull" else dfx.High.iloc[ev["i"]],
                        color=an.MUTED, lw=2.0, style="->")
                p.callout(ev["i"], dfx.Low.iloc[ev["i"]] if ev["side"] == "bull" else dfx.High.iloc[ev["i"]],
                          "Return to origin mitigates the\nimbalance before continuation", dx=5, color=col)
                entry = ev["top"] if ev["side"] == "bull" else ev["bot"]
                pad = (ev["top"] - ev["bot"]) * 1.2
                sl = ev["bot"] - pad * 0.4 if ev["side"] == "bull" else ev["top"] + pad * 0.4
                e2, s2, tps = trade_from(entry, sl, ev["side"])
                p.trade(min(ev["i"] + 3, p.w1 - 2), e2, s2, tps, ev["side"])
            plans.append(plan(dsn, ev["i"], "Mitigation Block", SMC, draw, L["MIT"], score=ev["score"]))

    # --- structure: BOS / CHoCH (12)
    for dsn, kind, side, n in [("GOOG_D", "BOS", "bull", 2), ("GOOG_D", "BOS", "bear", 1),
                               ("EURUSD_1H", "BOS", "bull", 1), ("EURUSD_4H", "BOS", "bear", 1),
                               ("SUPOR_D", "BOS", "bull", 1),
                               ("GOOG_D", "CHOCH", "bear", 2), ("GOOG_D", "CHOCH", "bull", 1),
                               ("EURUSD_1H", "CHOCH", "bull", 1), ("EURUSD_4H", "CHOCH", "bear", 1),
                               ("ASML_D", "CHOCH", "bull", 1)]:
        df = ds.load(dsn)
        evs = [e for e in det.structure_events(df) if e["kind"] == kind and e["side"] == side]
        for ev in take(evs, dsn, n):
            nm = "Break of Structure (BOS)" if kind == "BOS" else "Change of Character (CHoCH)"
            plans.append(plan(dsn, ev["i"], f"{nm} — {side}", SMC, _draw_structure(kind),
                              L[kind], score=ev["score"], ev=ev))

    # --- liquidity sweeps & grabs (8)
    for dsn, side, n, label, concept in [
        ("GOOG_D", "bull", 2, "Liquidity sweep of the lows", "Liquidity Sweep (sell-side)"),
        ("GOOG_D", "bear", 1, "Liquidity sweep of the highs", "Liquidity Sweep (buy-side)"),
        ("EURUSD_1H", "bull", 2, "Liquidity sweep of the lows", "Liquidity Sweep (sell-side)"),
        ("EURUSD_4H", "bear", 1, "Liquidity sweep of the highs", "Liquidity Sweep (buy-side)"),
        ("EURUSD_1H", "bear", 1, "Stop hunt above the highs", "Liquidity Grab / Stop Hunt"),
        ("SUPOR_D", "bull", 1, "Stop hunt below support", "Liquidity Grab / Stop Hunt"),
    ]:
        df = ds.load(dsn)
        evs = [e for e in det.sweep(df) if e["side"] == side]
        for ev in take(evs, dsn, n):
            plans.append(plan(dsn, ev["i"], concept, SMC, _draw_sweep(label), L["SWEEP"], score=ev["score"], ev=ev))

    # --- equal highs / lows (6)
    for dsn, kind, n in [("GOOG_D", "H", 1), ("EURUSD_1H", "H", 1), ("EURUSD_4H", "H", 1),
                         ("GOOG_D", "L", 1), ("EURUSD_1H", "L", 1), ("ASML_D", "L", 1)]:
        df = ds.load(dsn)
        tol = 0.004 if dsn.startswith("EURUSD") else 0.008
        evs = det.equal_levels(df, tol_frac=tol, kind=kind)
        for ev in take(evs, dsn, n, min_gap=25):
            nm = "Equal Highs (buy-side liquidity)" if kind == "H" else "Equal Lows (sell-side liquidity)"
            plans.append(plan(dsn, ev["i"], nm, SMC, _draw_eq("EQH  $$$" if kind == "H" else "EQL  $$$"),
                              L["EQH" if kind == "H" else "EQL"], before=55, after=40, score=ev["score"], ev=ev))

    # --- premium / discount (3)
    for dsn, n in [("GOOG_D", 1), ("EURUSD_4H", 1), ("SUPOR_D", 1)]:
        df = ds.load(dsn)
        evs = [e for e in det.structure_events(df) if e["kind"] == "BOS"]
        for ev in take(evs, dsn, n, min_gap=40):
            def draw(p, ev=ev, dfx=df):
                leg = swing_leg(dfx, min(ev["i"] + 10, len(dfx) - 1))
                if leg:
                    lo_i, lo_p, hi_i, hi_p = leg
                    p.premium_discount(lo_i, lo_p, hi_i, hi_p)
                    p.callout(ev["i"], dfx.Close.iloc[ev["i"]],
                              "Dealing range defined —\nbuy discount, sell premium", dx=-14, color=an.INK)
            plans.append(plan(dsn, ev["i"], "Premium & Discount", SMC, draw, L["PD"],
                              before=60, after=55, score=ev["score"]))

    # --- displacement (2)
    for dsn, n in [("GOOG_D", 1), ("EURUSD_1H", 1)]:
        df = ds.load(dsn)
        for ev in take(det.displacement(df), dsn, n):
            def draw(p, ev=ev, dfx=df):
                col = an.UP if ev["side"] == "bull" else an.DOWN
                i = ev["i"]
                p.mark(i, dfx.Close.iloc[i], color=col, r=700)
                p.callout(i, dfx.Close.iloc[i],
                          "Displacement: candle range is a\nmultiple of ATR — urgency of size", dx=-13, color=col)
                fv = [e for e in det.fvg(dfx) if abs(e["i"] - i) <= 2]
                if fv:
                    e0 = fv[0]
                    p.zone(e0["i"] - 1, min(i + 20, p.w1 - 1), e0["bot"], e0["top"], color=col, label="FVG left behind")
            plans.append(plan(dsn, ev["i"], "Displacement", SMC, draw, L["DISP"], score=ev["score"]))

    # --- inducement (2): sweep of a minor level right before a larger reversal
    for dsn, n in [("EURUSD_1H", 1), ("GOOG_D", 1)]:
        df = ds.load(dsn)
        evs = det.sweep(df, order=3, lookback=15)
        for ev in take(evs, dsn, n):
            def draw(p, ev=ev, dfx=df):
                col = an.LIQ
                p.ray(ev["level_i"], ev["level"], color=col, x1=min(ev["i"] + 3, p.w1 - 1),
                      label="inducement level", ls=":")
                p.mark(ev["i"], dfx.Low.iloc[ev["i"]] if ev["side"] == "bull" else dfx.High.iloc[ev["i"]], color=col)
                p.callout(ev["i"], dfx.Low.iloc[ev["i"]] if ev["side"] == "bull" else dfx.High.iloc[ev["i"]],
                          "Minor pool consumed first (inducement)\nbefore the real move", dx=5,
                          dy_frac=-0.1 if ev["side"] == "bull" else 0.1, color=col)
            plans.append(plan(dsn, ev["i"], "Inducement", SMC, draw, L["IND"], score=ev["score"]))

    # --- OTE (3): BOS then 62-79% retracement
    for dsn, n in [("GOOG_D", 1), ("EURUSD_1H", 1), ("EURUSD_4H", 1)]:
        df = ds.load(dsn)
        cands = []
        for ev in det.structure_events(df):
            leg = swing_leg(df, ev["i"])
            if not leg:
                continue
            lo_i, lo_p, hi_i, hi_p = leg
            rng = hi_p - lo_p
            if rng <= 0:
                continue
            seg = df.iloc[ev["i"] : ev["i"] + 25]
            if ev["side"] == "bull":
                depth = (hi_p - seg.Low.min()) / rng if len(seg) else 0
                hit = 0.60 <= depth <= 0.82
            else:
                depth = (seg.High.max() - lo_p) / rng if len(seg) else 0
                hit = 0.60 <= depth <= 0.82
            if hit:
                j = seg.Low.idxmin() if ev["side"] == "bull" else seg.High.idxmax()
                cands.append(dict(ev, i=int(df.index.get_loc(j)), leg=leg))
        for ev in take(cands, dsn, n):
            def draw(p, ev=ev, dfx=df):
                lo_i, lo_p, hi_i, hi_p = ev["leg"]
                if ev["side"] == "bull":
                    p.fib(lo_i, lo_p, hi_i, hi_p, levels=(0, 0.5, 0.62, 0.705, 0.79, 1.0))
                else:
                    p.fib(hi_i, hi_p, lo_i, lo_p, levels=(0, 0.5, 0.62, 0.705, 0.79, 1.0))
                rng = hi_p - lo_p
                if ev["side"] == "bull":
                    z0, z1 = hi_p - 0.79 * rng, hi_p - 0.62 * rng
                else:
                    z0, z1 = lo_p + 0.62 * rng, lo_p + 0.79 * rng
                col = an.UP if ev["side"] == "bull" else an.DOWN
                p.zone(min(lo_i, hi_i), p.w1 - 1, z0, z1, color=col, alpha=0.10, label="OTE 62-79%")
                entry = (z0 + z1) / 2
                sl = lo_p - rng * 0.06 if ev["side"] == "bull" else hi_p + rng * 0.06
                e2, s2, tps = trade_from(entry, sl, ev["side"], rs=(1, 2, 3))
                p.trade(min(ev["i"] + 3, p.w1 - 2), e2, s2, tps, ev["side"])
            plans.append(plan(dsn, ev["i"], "Optimal Trade Entry (OTE)", SMC, draw, L["OTE"],
                              before=75, after=45, score=ev["score"]))

    return plans


# ------------------------------------------------------------------ ICT

KZ = dict(asia=(list(range(0, 5)), "ASIA SESSION", an.NEUT),
          london=(list(range(7, 11)), "LONDON KILL ZONE 07-10 UTC", an.GOLD),
          ny=(list(range(12, 16)), "NEW YORK KILL ZONE 12-15 UTC", an.ENTRY),
          sb=([15], "SILVER BULLET WINDOW 15-16 UTC", an.LIQ))

L_ICT = {
    "KZ": ["Kill zones are the windows when London / New York institutional flow is active — realized volume in this feed peaks exactly there.",
           "Setups formed inside the kill zone carry follow-through; the same pattern in dead hours usually fails.",
           "Time first, then price: the zone qualifies the trade before the chart does."],
    "ASIA": ["The Asia session usually builds a tight accumulation range whose extremes become the day's first liquidity pools.",
             "London's opening move frequently runs one side of the Asia range before the true direction emerges.",
             "Mark the range at 05:00 UTC and trade the London reaction to it, not the range itself."],
    "JUDAS": ["The first London push swept the overnight extreme, then reversed — a Judas swing designed to recruit breakout traders on the wrong side.",
              "The false move creates both the liquidity and the premium entry for the real daily direction.",
              "Rule: London's first hour break of the Asia range is suspect until the reclaim proves otherwise."],
    "PO3": ["One session, three acts: accumulation in a narrow opening range, a manipulation leg that runs stops beyond it, then distribution in the true direction.",
            "The daily candle's wick is the manipulation; its body is the distribution — Power of Three explains the anatomy.",
            "Position during accumulation or on the manipulation extreme, never chasing the distribution leg."],
    "BIAS": ["Yesterday's high and low are the reference liquidity for today's delivery (daily bias).",
             "A run on the previous day's extreme that fails to accept beyond it typically rotates to the opposite extreme.",
             "Bias answers *which pool gets taken first* — entries still come from intraday structure."],
    "DOL": ["Price does not move randomly — it is drawn from one liquidity pool to the next (Draw on Liquidity).",
            "Equal highs ahead acted as the magnet; once consumed, the draw flipped to the opposite side.",
            "Trade toward the nearest untapped pool, not away from it."],
    "MMXM": ["The Market Maker model: an original consolidation, an engineered sell-off into the discount array, then a re-accumulation that mirrors the way down.",
             "The low of the curve forms where the last sellers are filled against institutional buying.",
             "Longs are only valid on the buy-side of the curve — after the smart-money reversal confirms."],
    "SB": ["The Silver Bullet is a one-hour algorithmic delivery window (15:00-16:00 UTC / 10-11am New York).",
           "Inside it, the playbook is one precise draw: take the FVG that forms and target the nearest pool.",
           "Small window, small target, high frequency — a time-based edge, not a price pattern."],
}


def build_ict():
    plans = []
    dsn = "EURUSD_1H"
    df = ds.load(dsn)

    def kz_draw(keys, focus=None):
        def draw(p, ev=None, dfx=None):
            for k in keys:
                hrs, lab, col = KZ[k]
                p.session(hrs, lab, color=col)
            if focus:
                focus(p, ev, dfx)
        return draw

    # pick days with strong killzone moves: use daily range on real data
    daily = df.resample("1D").agg(ds.OHLC_AGG).dropna()
    daily["rng"] = (daily.High - daily.Low) / daily.Low

    def day_events(k=30):
        evs = []
        for ts, r in daily.nlargest(k, "rng").iterrows():
            locs = df.index.normalize() == ts.normalize()
            if locs.sum() >= 20:
                i = int(np.where(locs)[0][12])  # NY-open bar of that day
                evs.append(dict(i=i, score=float(r["rng"])))
        return evs

    evs = take(day_events(), dsn, 6, min_gap=30)
    for ev, (concept, keys) in zip(evs, [
        ("London Kill Zone", ["asia", "london"]),
        ("New York Kill Zone", ["london", "ny"]),
        ("London Kill Zone — continuation", ["asia", "london"]),
        ("New York Kill Zone — reversal", ["ny"]),
        ("Asia Range → London expansion", ["asia", "london"]),
        ("Session Liquidity map", ["asia", "london", "ny"]),
    ]):
        lesson = L_ICT["ASIA"] if "Asia" in concept else L_ICT["KZ"]
        plans.append(plan(dsn, ev["i"], concept, ICT, kz_draw(keys), lesson,
                          before=30, after=26, score=ev["score"]))

    # Judas swing: London (07-08) breaks Asia range then closes back through it
    cands = []
    for ts in daily.index:
        day_mask = df.index.normalize() == ts.normalize()
        idx = np.where(day_mask)[0]
        if len(idx) < 20:
            continue
        day = df.iloc[idx]
        asia = day[day.index.hour < 5]
        if len(asia) < 3:
            continue
        a_hi, a_lo = asia.High.max(), asia.Low.min()
        lon = day[(day.index.hour >= 7) & (day.index.hour <= 9)]
        if not len(lon):
            continue
        rest = day[day.index.hour >= 10]
        if not len(rest):
            continue
        if lon.High.max() > a_hi and rest.Close.iloc[-1] < a_lo:
            j = int(df.index.get_loc(lon.High.idxmax()))
            cands.append(dict(i=j, score=(lon.High.max() - a_hi) + (a_lo - rest.Close.iloc[-1]),
                              a_hi=a_hi, a_lo=a_lo, side="bear"))
        if lon.Low.min() < a_lo and rest.Close.iloc[-1] > a_hi:
            j = int(df.index.get_loc(lon.Low.idxmin()))
            cands.append(dict(i=j, score=(a_lo - lon.Low.min()) + (rest.Close.iloc[-1] - a_hi),
                              a_hi=a_hi, a_lo=a_lo, side="bull"))
    for ev in take(cands, dsn, 4, min_gap=24):
        def draw(p, ev=ev, dfx=df):
            p.session(KZ["asia"][0], "ASIA RANGE", color=an.NEUT)
            p.session(KZ["london"][0], "LONDON OPEN", color=an.GOLD)
            p.ray(max(p.w0, ev["i"] - 12), ev["a_hi"], color=an.LIQ, label="Asia high", ls="--")
            p.ray(max(p.w0, ev["i"] - 12), ev["a_lo"], color=an.LIQ, label="Asia low", ls="--")
            px = dfx.High.iloc[ev["i"]] if ev["side"] == "bear" else dfx.Low.iloc[ev["i"]]
            p.mark(ev["i"], px, color=an.DOWN if ev["side"] == "bear" else an.UP)
            p.callout(ev["i"], px, "Judas swing: false London break,\nreal move goes the other way",
                      dx=4, dy_frac=0.09 if ev["side"] == "bear" else -0.09,
                      color=an.DOWN if ev["side"] == "bear" else an.UP)
        plans.append(plan(dsn, ev["i"], "Judas Swing", ICT, draw, L_ICT["JUDAS"],
                          before=18, after=22, score=ev["score"]))

    # Power of Three: big-range trending days
    po3 = take(day_events(60), dsn, 3, min_gap=40)
    for ev in po3:
        def draw(p, ev=ev, dfx=df):
            day0 = dfx.index[ev["i"]].normalize()
            idx = np.where(dfx.index.normalize() == day0)[0]
            d0, d1 = idx[0], idx[-1]
            day = dfx.iloc[d0 : d1 + 1]
            acc = day.iloc[:6]
            p.zone(d0, d0 + 5, acc.Low.min(), acc.High.max(), color=an.NEUT, label="ACCUMULATION")
            bull = day.Close.iloc[-1] > day.Open.iloc[0]
            man_p = day.Low.min() if bull else day.High.max()
            man_i = d0 + int(np.argmin(day.Low.values) if bull else np.argmax(day.High.values))
            p.mark(man_i, man_p, color=an.LIQ)
            p.callout(man_i, man_p, "MANIPULATION\n(stop run beyond the range)", dx=3,
                      dy_frac=-0.1 if bull else 0.1, color=an.LIQ)
            p.arrow(man_i, man_p, d1, day.Close.iloc[-1], color=an.UP if bull else an.DOWN, lw=3.0)
            p.label(d1 - 3, day.Close.iloc[-1], "DISTRIBUTION", color=an.UP if bull else an.DOWN)
        plans.append(plan(dsn, ev["i"], "Power of Three (AMD)", ICT, draw, L_ICT["PO3"],
                          before=14, after=16, score=ev["score"]))

    # Daily bias: previous day H/L runs
    cands = []
    for k in range(1, len(daily) - 1):
        pd_hi, pd_lo = daily.High.iloc[k - 1], daily.Low.iloc[k - 1]
        ts = daily.index[k]
        idx = np.where(df.index.normalize() == ts.normalize())[0]
        if len(idx) < 20:
            continue
        day = df.iloc[idx]
        if day.High.max() > pd_hi and day.Close.iloc[-1] < daily.Open.iloc[k]:
            j = int(df.index.get_loc(day.High.idxmax()))
            cands.append(dict(i=j, score=(day.High.max() - pd_hi) * 1e4, pd_hi=pd_hi, pd_lo=pd_lo, side="bear"))
        if day.Low.min() < pd_lo and day.Close.iloc[-1] > daily.Open.iloc[k]:
            j = int(df.index.get_loc(day.Low.idxmin()))
            cands.append(dict(i=j, score=(pd_lo - day.Low.min()) * 1e4, pd_hi=pd_hi, pd_lo=pd_lo, side="bull"))
    for ev in take(cands, dsn, 4, min_gap=30):
        def draw(p, ev=ev, dfx=df):
            p.ray(p.w0 + 1, ev["pd_hi"], color=an.DOWN, label="Prev. day HIGH (buy stops)", ls="--")
            p.ray(p.w0 + 1, ev["pd_lo"], color=an.UP, label="Prev. day LOW (sell stops)", ls="--")
            px = dfx.High.iloc[ev["i"]] if ev["side"] == "bear" else dfx.Low.iloc[ev["i"]]
            p.mark(ev["i"], px, color=an.LIQ)
            p.callout(ev["i"], px, "Previous-day extreme purged,\nno acceptance → rotation", dx=4,
                      dy_frac=0.09 if ev["side"] == "bear" else -0.09, color=an.LIQ)
        concept = "Daily Bias — previous day " + ("high run" if ev["side"] == "bear" else "low run")
        plans.append(plan(dsn, ev["i"], concept, ICT, draw, L_ICT["BIAS"],
                          before=30, after=20, score=ev["score"]))

    # Draw on liquidity: EQH consumed
    eq = det.equal_levels(df, tol_frac=0.0006, kind="H")
    cands = []
    for e in eq:
        seg = df.iloc[e["i2"] + 1 : e["i2"] + 30]
        hit = seg[seg.High > e["level"]]
        if len(hit):
            j = int(df.index.get_loc(hit.index[0]))
            cands.append(dict(e, i=j))
    for ev in take(cands, dsn, 3, min_gap=30):
        def draw(p, ev=ev, dfx=df):
            p.ray(ev["i1"], ev["level"], color=an.LIQ, x1=ev["i"], label="draw on liquidity", ls="--")
            for j in (ev["i1"], ev["i2"]):
                p.mark(j, dfx.High.iloc[j], color=an.LIQ)
            p.arrow(ev["i2"], dfx.Low.iloc[ev["i2"]], ev["i"], ev["level"], color=an.UP, lw=2.6)
            p.callout(ev["i"], dfx.High.iloc[ev["i"]], "Pool consumed —\ndraw satisfied", dx=3, color=an.LIQ)
        plans.append(plan(dsn, ev["i"], "Draw on Liquidity (DOL)", ICT, draw, L_ICT["DOL"],
                          before=45, after=25, score=ev["score"]))

    # Market maker buy model: decline into re-accumulation and mirror rally
    sm = [e for e in det.sweep(df) if e["side"] == "bull"]
    for ev in take(sm, dsn, 2, min_gap=60):
        def draw(p, ev=ev, dfx=df):
            i = ev["i"]
            p.mark(i, dfx.Low.iloc[i], color=an.LIQ, r=650)
            p.label(i, dfx.Low.iloc[i] * 0.9985, "SMART MONEY REVERSAL", color=an.UP, va="top")
            p.callout(max(p.w0 + 6, i - 22), dfx.High.iloc[max(p.w0 + 6, i - 22)],
                      "Sell-side of the curve:\nengineered decline", dx=2, color=an.DOWN)
            p.callout(min(p.w1 - 4, i + 14), dfx.High.iloc[min(p.w1 - 4, i + 14)],
                      "Buy-side of the curve:\nre-accumulation mirrors the drop", dx=-16, color=an.UP)
        plans.append(plan(dsn, ev["i"], "Market Maker Buy Model", ICT, draw, L_ICT["MMXM"],
                          before=55, after=40, score=ev["score"]))

    # Silver bullet: FVG formed 15-16 UTC
    sb_cands = [e for e in det.fvg(df, min_frac=0.3) if df.index[e["i"]].hour == 15]
    for ev in take(sb_cands, dsn, 2, min_gap=30):
        def draw(p, ev=ev, dfx=df):
            p.session([15], "SILVER BULLET 15-16 UTC", color=an.LIQ, alpha=0.16)
            col = an.UP if ev["side"] == "bull" else an.DOWN
            p.zone(ev["i"] - 1, min(ev["i"] + 8, p.w1 - 1), ev["bot"], ev["top"], color=col, label="SB FVG")
            entry = (ev["top"] + ev["bot"]) / 2
            sl = ev["bot"] - (ev["top"] - ev["bot"]) if ev["side"] == "bull" else ev["top"] + (ev["top"] - ev["bot"])
            e2, s2, tps = trade_from(entry, sl, ev["side"], rs=(1, 2))
            p.trade(min(ev["i"] + 2, p.w1 - 2), e2, s2, tps, ev["side"])
        plans.append(plan(dsn, ev["i"], "Silver Bullet (NY AM)", ICT, draw, L_ICT["SB"],
                          before=20, after=16, score=ev["score"]))

    return plans
