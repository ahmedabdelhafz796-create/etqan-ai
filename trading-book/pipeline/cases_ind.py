"""Indicator case builders (~60 plates)."""

from __future__ import annotations

import numpy as np

from . import annotate as an
from . import data_sources as ds
from . import detectors as det
from . import indicators as ind
from .cases_util import plan, take, trade_from

IND = "Indicators"

L = {
    "RSI_X": ["RSI stretched beyond the band while price pressed into a level — momentum exhaustion meeting structure.",
              "Overbought/oversold alone is not a signal in trends; it is one only at locations where the auction can turn.",
              "The reversion trade triggers when RSI re-crosses its band with a price confirmation candle."],
    "RSI_DIV": ["Price made a new extreme; RSI refused to confirm it — fewer participants powered the second push.",
                "Divergence is an early warning, not an entry: it needs a structural trigger (the marked swing break).",
                "Risk sits beyond the divergent extreme; the first target is the origin of the divergence."],
    "MACD": ["The MACD line crossed its signal while the histogram flipped — trend momentum changed gear.",
             "Crosses far from the zero line mean late entries; crosses near zero catch new trends early.",
             "Filter: only take crosses aligned with the higher-timeframe structure shown by the moving averages."],
    "GC": ["The 50-period average crossed the 200 (golden/death cross) — a regime label, not a timing tool.",
           "These crosses lag by design; their value is bias: which side's setups you are allowed to take.",
           "Combine with pullback entries — chasing the cross candle itself buys the worst price of the sequence."],
    "EMA_X": ["The fast EMA crossed the slow one after a clean pullback sequence.",
              "EMA crosses shine in trending conditions and chop you to death in ranges — the ADX panel arbitrates.",
              "Entries on the retest of the fast EMA post-cross keep risk tight."],
    "BB_SQ": ["Bollinger band width collapsed to a local minimum — the squeeze that precedes expansion.",
              "Direction comes from the break, not the squeeze; the bands only time the release.",
              "Trade the close outside the bands after the squeeze with the middle band as trailing reference."],
    "BB_RIDE": ["A strong trend 'walks the band': closes hugging the outer band signal strength, not overbought.",
                "Selling because price touched the upper band is the classic mean-reversion mistake in a trend.",
                "The exit cue is the first close back through the middle band, not the band touch."],
    "BB_REV": ["In a sideways auction, band extremes act as fade zones back toward the mean.",
               "This regime trade works only while the middle band is flat — the marked ADX confirms low trend energy.",
               "Stop beyond the band extreme; target the middle band or opposite band."],
    "VWAP": ["Session VWAP is the institution's benchmark: above it buyers are in control of the session's auction.",
             "The bounce/rejection at VWAP shows algorithmic execution defending average position price.",
             "Mean-reversion to VWAP and trend continuation from VWAP are both mapped here on real intraday data."],
    "ICHI": ["Ichimoku is a full system: Tenkan/Kijun momentum, cloud (Kumo) structure ahead, Chikou confirmation behind.",
             "The bullish sequence: price above cloud + TK cross + future cloud twist — all three visible here.",
             "The cloud's far edge is the system's natural invalidation."],
    "PSAR": ["Parabolic SAR flipped sides — the trailing-stop logic switched from one trend to the other.",
             "SAR's accelerating step means late-trend flips whipsaw; early-trend flips ride the whole move.",
             "Use the SAR dots as the trailing stop for the trade shown, not as the entry trigger by itself."],
    "STOCH": ["Stochastic %K crossed %D from an extreme — a momentum rotation inside the marked range context.",
              "In ranges, stochastic extremes at range edges are high-quality; mid-range crosses are noise.",
              "The trigger is the cross + the range edge holding, with a stop beyond the extreme."],
    "ADX": ["ADX rising through 25 with DI+ over DI- certifies a real trend in force.",
            "Every failed counter-trend fade during this stretch lost — trend filters exist to forbid those trades.",
            "Falling ADX below 20 hands the market back to range strategies."],
    "ATR": ["ATR expanded sharply — the volatility regime changed, and position sizing must change with it.",
            "Same setup, doubled ATR = half size for identical account risk: the math shown in the panel.",
            "Stops set in ATR multiples adapt automatically; fixed-point stops break when regimes shift."],
    "OBV": ["On-Balance Volume trended with price into the move — accumulation was confirmed by participation.",
            "When OBV leads price to new extremes, the crowd's volume is committed; when it lags, distrust the rally.",
            "The OBV trendline break marked here preceded the price break."],
    "CCI": ["CCI beyond ±100 flags a statistical stretch from the moving mean.",
            "The signal here is the re-entry from the extreme aligned with the larger structure.",
            "CCI extremes in trends mark continuation pullbacks, not reversals — direction filter first."],
    "CMF": ["Chaikin Money Flow stayed positive through the pullback — closes kept finishing high in their ranges on volume.",
            "CMF above zero during a correction = accumulation under cover of weakness.",
            "The long trigger is price resuming while CMF holds its zero line."],
    "ST": ["Supertrend flipped: the ATR-band trail switched sides and now defines the trade's risk line.",
           "Its virtue is discipline — one line, one rule, no discretion mid-trade.",
           "Re-entries occur on pullbacks to the line while it holds direction."],
    "VP": ["The volume profile shows where the auction actually did business: POC is fair price; VAH/VAL bound value.",
           "Moves from value edges back to POC are mean-reversion; acceptance outside value starts range extension.",
           "The marked reaction at the value-area boundary is the profile's core trade."],
    "VC": ["A volume climax: the highest participation of the window at the extreme of the move.",
           "Climactic volume at lows = capitulation transfer from weak to strong hands (and mirror-image at tops).",
           "The confirmation is the failure to make new extremes on the next bars — marked here."],
}


def build_ind():
    plans = []

    # RSI overbought/oversold at extremes (3)
    for dsn, n in [("GOOG_D", 1), ("EURUSD_4H", 1), ("SUPOR_D", 1)]:
        df = ds.load(dsn)
        r = ind.rsi(df.Close)
        cands = []
        for i in range(30, len(df) - 10):
            if r.iloc[i] > 74 or r.iloc[i] < 26:
                rev = abs(df.Close.iloc[min(i + 8, len(df) - 1)] - df.Close.iloc[i])
                cands.append(dict(i=i, score=float(abs(r.iloc[i] - 50) + rev / df.Close.iloc[i] * 100),
                                  side="bear" if r.iloc[i] > 70 else "bull", rsi=float(r.iloc[i])))
        for ev in take(cands, dsn, n, min_gap=25):
            def draw(p, ev=ev, dfx=df):
                col = an.UP if ev["side"] == "bull" else an.DOWN
                p.mark(ev["i"], dfx.Close.iloc[ev["i"]], color=col)
                p.callout(ev["i"], dfx.Close.iloc[ev["i"]],
                          f"RSI = {ev['rsi']:.0f} — {'oversold' if ev['side']=='bull' else 'overbought'}\nat a reaction point", dx=5, color=col)
                ax = p.panel_axes.get("rsi")
                if ax:
                    ax.axhline(70, color=an.DOWN, lw=1.2, ls="--")
                    ax.axhline(30, color=an.UP, lw=1.2, ls="--")
            plans.append(plan(dsn, ev["i"], "RSI Overbought/Oversold", IND, draw, L["RSI_X"],
                              panels=["rsi"], score=ev["score"]))

    # RSI divergence (5)
    for dsn, side, n in [("GOOG_D", "bull", 1), ("GOOG_D", "bear", 1), ("EURUSD_1H", "bull", 1),
                         ("EURUSD_4H", "bear", 1), ("ASML_D", "bull", 1)]:
        df = ds.load(dsn)
        evs = [e for e in det.rsi_divergence(df) if e["side"] == side]
        for ev in take(evs, dsn, n, min_gap=25):
            def draw(p, ev=ev, dfx=df):
                col = an.UP if ev["side"] == "bull" else an.DOWN
                p.seg(ev["i1"], ev["p1"], ev["i2"], ev["p2"], color=col, lw=2.6, ls="-")
                for j, px in [(ev["i1"], ev["p1"]), (ev["i2"], ev["p2"])]:
                    p.mark(j, px, color=col)
                ax = p.panel_axes.get("rsi")
                if ax:
                    ax.plot([p.x(ev["i1"]), p.x(ev["i2"])], [ev["r1"], ev["r2"]], color=col, lw=2.6)
                p.callout(ev["i2"], ev["p2"],
                          "Price new extreme, RSI higher low" if ev["side"] == "bull" else "Price new high, RSI lower high",
                          dx=4, dy_frac=-0.09 if ev["side"] == "bull" else 0.09, color=col)
            nm = f"RSI {'Bullish' if ev['side']=='bull' else 'Bearish'} Divergence"
            plans.append(plan(dsn, ev["i"], nm, IND, draw, L["RSI_DIV"], panels=["rsi"], score=ev["score"]))

    # MACD crosses (4)
    for dsn, side, n in [("GOOG_D", "bull", 1), ("GOOG_D", "bear", 1), ("EURUSD_4H", "bull", 1), ("SUPOR_D", "bear", 1)]:
        df = ds.load(dsn)
        evs = [e for e in det.macd_cross(df) if e["side"] == side]
        for ev in take(evs, dsn, n, min_gap=25):
            def draw(p, ev=ev, dfx=df):
                col = an.UP if ev["side"] == "bull" else an.DOWN
                p.mark(ev["i"], dfx.Close.iloc[ev["i"]], color=col)
                ax = p.panel_axes.get("macd")
                if ax:
                    ax.axvline(p.x(ev["i"]), color=col, lw=1.6, ls="--")
                    ax.axhline(0, color=an.MUTED, lw=1.0)
                p.callout(ev["i"], dfx.Close.iloc[ev["i"]], f"MACD {ev['side']} cross", dx=5, color=col)
            nm = f"MACD {'Bullish' if ev['side']=='bull' else 'Bearish'} Cross"
            plans.append(plan(dsn, ev["i"], nm, IND, draw, L["MACD"], panels=["macd"], score=ev["score"]))

    # Golden / death crosses (3)
    for dsn, side, n, nm in [("GOOG_D", "bull", 1, "Golden Cross (50/200)"), ("GOOG_D", "bear", 1, "Death Cross (50/200)"),
                             ("SUPOR_D", "bull", 1, "Golden Cross (50/200)")]:
        df = ds.load(dsn)
        evs = [e for e in det.ma_cross(df) if e["side"] == side]
        for ev in take(evs, dsn, n, min_gap=60):
            def draw(p, ev=ev, dfx=df, nm=nm):
                col = an.UP if ev["side"] == "bull" else an.DOWN
                f = ind.sma(dfx.Close, 50)
                p.mark(ev["i"], f.iloc[ev["i"]], color=col, r=700)
                p.callout(ev["i"], f.iloc[ev["i"]], nm, dx=5, color=col)
            plans.append(plan(dsn, ev["i"], nm, IND, draw, L["GC"], overlays=["sma50", "sma200"],
                              before=110, after=60, score=ev["score"]))

    # EMA 20/50 crosses (3)
    for dsn, side, n in [("GOOG_D", "bull", 1), ("EURUSD_4H", "bear", 1), ("EURUSD_1H", "bull", 1)]:
        df = ds.load(dsn)
        f, s = ind.ema(df.Close, 20), ind.ema(df.Close, 50)
        cands = []
        for i in range(55, len(df) - 10):
            prev, cur = f.iloc[i - 1] - s.iloc[i - 1], f.iloc[i] - s.iloc[i]
            if (prev < 0 < cur and side == "bull") or (prev > 0 > cur and side == "bear"):
                move = abs(df.Close.iloc[min(i + 10, len(df) - 1)] - df.Close.iloc[i]) / df.Close.iloc[i]
                cands.append(dict(i=i, score=float(move * 100), side=side))
        for ev in take(cands, dsn, n, min_gap=30):
            def draw(p, ev=ev, dfx=df):
                col = an.UP if ev["side"] == "bull" else an.DOWN
                p.mark(ev["i"], ind.ema(dfx.Close, 20).iloc[ev["i"]], color=col, r=650)
                p.callout(ev["i"], dfx.Close.iloc[ev["i"]], f"EMA20/50 {ev['side']} cross", dx=5, color=col)
            plans.append(plan(dsn, ev["i"], "EMA Crossover (20/50)", IND, draw, L["EMA_X"],
                              overlays=["ema20", "ema50"], score=ev["score"]))

    # Bollinger: squeeze (2), band ride (2), reversion (2)
    for dsn, n in [("GOOG_D", 1), ("EURUSD_1H", 1)]:
        df = ds.load(dsn)
        for ev in take(det.bb_squeeze(df), dsn, n, min_gap=30):
            def draw(p, ev=ev, dfx=df):
                col = an.UP if ev["side"] == "bull" else an.DOWN
                p.mark(ev["i"], dfx.Close.iloc[ev["i"]], color=an.LIQ, r=600)
                p.callout(ev["i"], dfx.Close.iloc[ev["i"]], "Band width at local minimum\n= squeeze", dx=4, color=an.LIQ)
                p.arrow(ev["i"] + 1, dfx.Close.iloc[ev["i"]], min(ev["i"] + 9, p.w1 - 2),
                        dfx.Close.iloc[min(ev["i"] + 9, len(dfx) - 1)], color=col, lw=3.0)
            plans.append(plan(dsn, ev["i"], "Bollinger Band Squeeze", IND, draw, L["BB_SQ"],
                              overlays=["bb"], score=ev["score"]))
    for dsn in ["GOOG_D", "SUPOR_D"]:
        df = ds.load(dsn)
        mid, up, lo = ind.bollinger(df.Close)
        cands = []
        run = 0
        for i in range(25, len(df) - 10):
            if df.Close.iloc[i] > mid.iloc[i] and df.High.iloc[i] >= up.iloc[i] * 0.995:
                run += 1
                if run >= 5:
                    cands.append(dict(i=i, score=float(run)))
            else:
                run = 0
        for ev in take(cands, dsn, 1, min_gap=40):
            def draw(p, ev=ev, dfx=df):
                p.callout(ev["i"], dfx.High.iloc[ev["i"]], "Walking the band:\ntrend strength, not 'overbought'", dx=-14, color=an.UP)
            plans.append(plan(dsn, ev["i"], "Bollinger Band Walk", IND, draw, L["BB_RIDE"],
                              overlays=["bb"], score=ev["score"]))
    for dsn in ["EURUSD_4H", "ASML_D"]:
        df = ds.load(dsn)
        mid, up, lo = ind.bollinger(df.Close)
        a, _, _ = ind.adx(df)
        cands = []
        for i in range(30, len(df) - 10):
            if a.iloc[i] < 18 and (df.Low.iloc[i] <= lo.iloc[i] or df.High.iloc[i] >= up.iloc[i]):
                back = abs(df.Close.iloc[min(i + 6, len(df) - 1)] - mid.iloc[i]) < abs(df.Close.iloc[i] - mid.iloc[i])
                if back:
                    side = "bull" if df.Low.iloc[i] <= lo.iloc[i] else "bear"
                    cands.append(dict(i=i, score=float(20 - a.iloc[i]), side=side))
        for ev in take(cands, dsn, 1, min_gap=30):
            def draw(p, ev=ev, dfx=df):
                col = an.UP if ev["side"] == "bull" else an.DOWN
                px = dfx.Low.iloc[ev["i"]] if ev["side"] == "bull" else dfx.High.iloc[ev["i"]]
                p.mark(ev["i"], px, color=col)
                p.callout(ev["i"], px, "Low-ADX regime: band touch\nfades back to the mean", dx=4,
                          dy_frac=-0.09 if ev["side"] == "bull" else 0.09, color=col)
            plans.append(plan(dsn, ev["i"], "Bollinger Mean Reversion", IND, draw, L["BB_REV"],
                              overlays=["bb"], panels=["adx"], score=ev["score"]))

    # VWAP (4, intraday only)
    df = ds.load("EURUSD_1H")
    vw = ind.vwap_session(df)
    cands_b, cands_r = [], []
    for i in range(24, len(df) - 8):
        if df.index[i].hour < 8 or df.index[i].hour > 18:
            continue
        d = (df.Low.iloc[i] - vw.iloc[i]) / vw.iloc[i]
        u = (df.High.iloc[i] - vw.iloc[i]) / vw.iloc[i]
        if abs(d) < 0.0004 and df.Close.iloc[i] > vw.iloc[i] and df.Close.iloc[min(i + 4, len(df) - 1)] > df.Close.iloc[i]:
            cands_b.append(dict(i=i, score=float(df.Close.iloc[min(i + 4, len(df) - 1)] - df.Close.iloc[i]) * 1e4, side="bull"))
        if abs(u) < 0.0004 and df.Close.iloc[i] < vw.iloc[i] and df.Close.iloc[min(i + 4, len(df) - 1)] < df.Close.iloc[i]:
            cands_r.append(dict(i=i, score=float(df.Close.iloc[i] - df.Close.iloc[min(i + 4, len(df) - 1)]) * 1e4, side="bear"))
    for evs, nm in [(take(cands_b, "EURUSD_1H", 2, min_gap=30), "VWAP Bounce (support)"),
                    (take(cands_r, "EURUSD_1H", 2, min_gap=30), "VWAP Rejection (resistance)")]:
        for ev in evs:
            def draw(p, ev=ev, dfx=df):
                col = an.UP if ev["side"] == "bull" else an.DOWN
                px = dfx.Low.iloc[ev["i"]] if ev["side"] == "bull" else dfx.High.iloc[ev["i"]]
                p.mark(ev["i"], px, color=col)
                p.callout(ev["i"], px, "Reaction at session VWAP", dx=4,
                          dy_frac=-0.08 if ev["side"] == "bull" else 0.08, color=col)
            plans.append(plan("EURUSD_1H", ev["i"], nm, IND, draw, L["VWAP"],
                              overlays=["vwap"], before=30, after=20, score=ev["score"]))

    # Ichimoku (3)
    for dsn, n in [("GOOG_D", 2), ("EURUSD_4H", 1)]:
        df = ds.load(dsn)
        conv, base, sa, sb, lag = ind.ichimoku(df)
        cands = []
        for i in range(60, len(df) - 15):
            above = df.Close.iloc[i] > max(sa.iloc[i], sb.iloc[i]) if not np.isnan(sa.iloc[i]) else False
            cross = conv.iloc[i - 1] < base.iloc[i - 1] and conv.iloc[i] > base.iloc[i]
            if above and cross:
                move = (df.Close.iloc[min(i + 12, len(df) - 1)] - df.Close.iloc[i]) / df.Close.iloc[i]
                cands.append(dict(i=i, score=float(move * 100), side="bull"))
            below = df.Close.iloc[i] < min(sa.iloc[i], sb.iloc[i]) if not np.isnan(sa.iloc[i]) else False
            crossd = conv.iloc[i - 1] > base.iloc[i - 1] and conv.iloc[i] < base.iloc[i]
            if below and crossd:
                move = (df.Close.iloc[i] - df.Close.iloc[min(i + 12, len(df) - 1)]) / df.Close.iloc[i]
                cands.append(dict(i=i, score=float(move * 100), side="bear"))
        for ev in take(cands, dsn, n, min_gap=35):
            def draw(p, ev=ev, dfx=df):
                col = an.UP if ev["side"] == "bull" else an.DOWN
                p.mark(ev["i"], dfx.Close.iloc[ev["i"]], color=col)
                p.callout(ev["i"], dfx.Close.iloc[ev["i"]],
                          f"TK cross {'above' if ev['side']=='bull' else 'below'} the Kumo", dx=5, color=col)
            nm = f"Ichimoku TK Cross ({ev['side']})"
            plans.append(plan(dsn, ev["i"], nm, IND, draw, L["ICHI"], overlays=["ichimoku"],
                              before=80, after=40, score=ev["score"]))

    # PSAR flips (2)
    for dsn, n in [("GOOG_D", 1), ("EURUSD_4H", 1)]:
        df = ds.load(dsn)
        ps = ind.psar(df)
        cands = []
        for i in range(30, len(df) - 12):
            was_above = ps.iloc[i - 1] > df.Close.iloc[i - 1]
            now_below = ps.iloc[i] < df.Close.iloc[i]
            if was_above and now_below:
                move = (df.Close.iloc[min(i + 10, len(df) - 1)] - df.Close.iloc[i]) / df.Close.iloc[i]
                cands.append(dict(i=i, score=float(move * 100), side="bull"))
            if (not was_above) and (not now_below):
                pass
        for ev in take(cands, dsn, n, min_gap=30):
            def draw(p, ev=ev, dfx=df):
                p.mark(ev["i"], dfx.Close.iloc[ev["i"]], color=an.UP)
                p.callout(ev["i"], dfx.Close.iloc[ev["i"]], "SAR flip: dots switch sides,\ntrail begins", dx=5, color=an.UP)
            plans.append(plan(dsn, ev["i"], "Parabolic SAR Flip", IND, draw, L["PSAR"],
                              overlays=["psar"], score=ev["score"]))

    # Stochastic (2)
    for dsn, n in [("EURUSD_4H", 1), ("ASML_D", 1)]:
        df = ds.load(dsn)
        k, d = ind.stochastic(df)
        cands = []
        for i in range(25, len(df) - 8):
            if np.isnan(k.iloc[i - 1]) or np.isnan(d.iloc[i - 1]):
                continue
            if k.iloc[i - 1] < d.iloc[i - 1] and k.iloc[i] > d.iloc[i] and k.iloc[i] < 25:
                cands.append(dict(i=i, score=float(25 - k.iloc[i]), side="bull"))
            if k.iloc[i - 1] > d.iloc[i - 1] and k.iloc[i] < d.iloc[i] and k.iloc[i] > 75:
                cands.append(dict(i=i, score=float(k.iloc[i] - 75), side="bear"))
        for ev in take(cands, dsn, n, min_gap=25):
            def draw(p, ev=ev, dfx=df):
                col = an.UP if ev["side"] == "bull" else an.DOWN
                p.mark(ev["i"], dfx.Close.iloc[ev["i"]], color=col)
                ax = p.panel_axes.get("stoch")
                if ax:
                    ax.axhline(80, color=an.DOWN, lw=1.2, ls="--")
                    ax.axhline(20, color=an.UP, lw=1.2, ls="--")
                    ax.axvline(p.x(ev["i"]), color=col, lw=1.6, ls="--")
            nm = f"Stochastic Cross ({'oversold' if ev['side']=='bull' else 'overbought'})"
            plans.append(plan(dsn, ev["i"], nm, IND, draw, L["STOCH"], panels=["stoch"], score=ev["score"]))

    # ADX trend (2), ATR regime (2), OBV (2), CCI (2), CMF (1), Supertrend (2)
    for dsn in ["GOOG_D", "EURUSD_4H"]:
        df = ds.load(dsn)
        a, pdi, mdi = ind.adx(df)
        cands = [dict(i=i, score=float(a.iloc[i]), side="bull" if pdi.iloc[i] > mdi.iloc[i] else "bear")
                 for i in range(40, len(df) - 10)
                 if not np.isnan(a.iloc[i]) and a.iloc[i - 5] < 22 and a.iloc[i] > 30]
        for ev in take(cands, dsn, 1, min_gap=40):
            def draw(p, ev=ev, dfx=df):
                col = an.UP if ev["side"] == "bull" else an.DOWN
                p.callout(ev["i"], dfx.Close.iloc[ev["i"]], "ADX pushes through 25-30:\ntrend certified", dx=-14, color=col)
                ax = p.panel_axes.get("adx")
                if ax:
                    ax.axhline(25, color=an.MUTED, lw=1.2, ls="--")
            plans.append(plan(dsn, ev["i"], "ADX Trend Confirmation", IND, draw, L["ADX"],
                              panels=["adx"], score=ev["score"]))
    for dsn in ["GOOG_D", "EURUSD_1H"]:
        df = ds.load(dsn)
        a = ind.atr(df)
        cands = [dict(i=i, score=float(a.iloc[i] / a.iloc[i - 15]))
                 for i in range(40, len(df) - 10) if a.iloc[i] > 1.8 * a.iloc[i - 15]]
        for ev in take(cands, dsn, 1, min_gap=40):
            def draw(p, ev=ev, dfx=df):
                p.callout(ev["i"], dfx.Close.iloc[ev["i"]],
                          f"ATR ×{ev['score']:.1f} in 15 bars —\nhalve size, widen stops", dx=-14, color=an.LIQ)
            plans.append(plan(dsn, ev["i"], "ATR Volatility Regime Shift", IND, draw, L["ATR"],
                              panels=["atr"], score=ev["score"]))
    for dsn in ["GOOG_D", "SUPOR_D"]:
        df = ds.load(dsn)
        o = ind.obv(df)
        zz_o = det.zigzag(df, 6)
        cands = []
        for i in range(40, len(df) - 12):
            win_o = o.iloc[i - 25 : i]
            if o.iloc[i] == win_o.max() and df.Close.iloc[i] < df.Close.iloc[i - 25 : i].max():
                cands.append(dict(i=i, score=1.0, side="bull"))
        for ev in take(cands, dsn, 1, min_gap=40):
            def draw(p, ev=ev, dfx=df):
                p.callout(ev["i"], dfx.Close.iloc[ev["i"]], "OBV leads price to new highs:\naccumulation confirmed", dx=-14, color=an.UP)
            plans.append(plan(dsn, ev["i"], "OBV Accumulation Signal", IND, draw, L["OBV"],
                              panels=["obv"], score=ev["score"]))
    for dsn in ["EURUSD_4H", "GOOG_D"]:
        df = ds.load(dsn)
        c = ind.cci(df)
        cands = []
        for i in range(30, len(df) - 8):
            if c.iloc[i - 1] < -100 <= c.iloc[i]:
                cands.append(dict(i=i, score=float(-c.iloc[i - 1]), side="bull"))
            if c.iloc[i - 1] > 100 >= c.iloc[i]:
                cands.append(dict(i=i, score=float(c.iloc[i - 1]), side="bear"))
        for ev in take(cands, dsn, 1, min_gap=30):
            def draw(p, ev=ev, dfx=df):
                col = an.UP if ev["side"] == "bull" else an.DOWN
                p.mark(ev["i"], dfx.Close.iloc[ev["i"]], color=col)
                ax = p.panel_axes.get("cci")
                if ax:
                    ax.axhline(100, color=an.DOWN, lw=1.2, ls="--")
                    ax.axhline(-100, color=an.UP, lw=1.2, ls="--")
            plans.append(plan(dsn, ev["i"], "CCI Extreme Re-entry", IND, draw, L["CCI"],
                              panels=["cci"], score=ev["score"]))
    df = ds.load("GOOG_D")
    cm = ind.cmf(df)
    cands = []
    for i in range(40, len(df) - 12):
        seg = df.Close.iloc[i - 10 : i + 1]
        if seg.iloc[-1] < seg.iloc[0] and cm.iloc[i] > 0.08:
            cands.append(dict(i=i, score=float(cm.iloc[i] * 100)))
    for ev in take(cands, "GOOG_D", 1, min_gap=40):
        def draw(p, ev=ev, dfx=df):
            p.callout(ev["i"], dfx.Close.iloc[ev["i"]], "Price falls, CMF stays positive:\nbuying under weakness", dx=-14, color=an.UP)
        plans.append(plan("GOOG_D", ev["i"], "Chaikin Money Flow Divergence", IND, draw, L["CMF"],
                          panels=["cmf"], score=ev["score"]))
    for dsn in ["GOOG_D", "EURUSD_4H"]:
        df = ds.load(dsn)
        st, dirn = ind.supertrend(df)
        cands = []
        for i in range(30, len(df) - 12):
            if dirn.iloc[i - 1] == -1 and dirn.iloc[i] == 1:
                move = (df.Close.iloc[min(i + 10, len(df) - 1)] - df.Close.iloc[i]) / df.Close.iloc[i]
                cands.append(dict(i=i, score=float(move * 100), side="bull"))
        for ev in take(cands, dsn, 1, min_gap=35):
            def draw(p, ev=ev, dfx=df):
                p.mark(ev["i"], dfx.Close.iloc[ev["i"]], color=an.UP)
                p.callout(ev["i"], dfx.Close.iloc[ev["i"]], "Supertrend flips long —\nline becomes the trail", dx=5, color=an.UP)
            plans.append(plan(dsn, ev["i"], "Supertrend Flip", IND, draw, L["ST"],
                              overlays=["supertrend"], score=ev["score"]))

    # Volume profile (3) + volume climax (2)
    for dsn, n in [("GOOG_D", 2), ("EURUSD_1H", 1)]:
        df = ds.load(dsn)
        evs = det.rectangle_range(df)
        for ev in take(evs, dsn, n, min_gap=40):
            def draw(p, ev=ev, dfx=df):
                from .indicators import volume_profile
                prof = volume_profile(dfx.iloc[p.w0 : p.w1])
                p.volume_profile(prof)
                p.callout(ev["i"], prof["poc"], "POC: price with most\ntraded volume (fair value)", dx=-16, color=an.GOLD)
            plans.append(plan(dsn, ev["i"], "Volume Profile: POC / VAH / VAL", IND, draw, L["VP"],
                              before=55, after=25, score=ev["score"]))
    for dsn in ["GOOG_D", "SUPOR_D"]:
        df = ds.load(dsn)
        cands = []
        for i in range(30, len(df) - 10):
            vol_win = df.Volume.iloc[i - 25 : i]
            if df.Volume.iloc[i] > 2.8 * vol_win.mean() and df.Low.iloc[i] == df.Low.iloc[i - 12 : i + 1].min():
                rec = df.Close.iloc[min(i + 6, len(df) - 1)] > df.Close.iloc[i]
                if rec:
                    cands.append(dict(i=i, score=float(df.Volume.iloc[i] / vol_win.mean())))
        for ev in take(cands, dsn, 1, min_gap=40):
            def draw(p, ev=ev, dfx=df):
                p.mark(ev["i"], dfx.Low.iloc[ev["i"]], color=an.LIQ, r=700)
                p.callout(ev["i"], dfx.Low.iloc[ev["i"]], f"Volume climax ×{ev['score']:.1f} average:\ncapitulation at the low",
                          dx=4, dy_frac=-0.1, color=an.LIQ)
            plans.append(plan(dsn, ev["i"], "Volume Climax / Capitulation", IND, draw, L["VC"], score=ev["score"]))

    return plans
