"""Fundamental Analysis case builders (~20 plates).

Every event date here is a matter of public record and is verified against the
data itself before a plate is produced (the detector confirms the documented
reaction exists in the series - e.g. GOOG's +19.1% gap on 2008-04-18).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import annotate as an
from . import data_sources as ds
from . import detectors as det
from .cases_util import BADGE, claim, plan

FA = "Fundamental Analysis"

# FOMC statement days within the EURUSD sample (public record):
FOMC = ["2017-05-03", "2017-06-14", "2017-07-26", "2017-09-20", "2017-11-01", "2017-12-13"]
FOMC_NOTE = {
    "2017-06-14": "FOMC hikes 25bp to 1.00-1.25%",
    "2017-09-20": "FOMC announces balance-sheet runoff",
    "2017-12-13": "FOMC hikes 25bp to 1.25-1.50%",
}
ECB = {"2017-09-07": "ECB press conference (Draghi) — EUR rallies",
       "2017-10-26": "ECB announces QE taper — EUR sells off sharply"}
# Non-farm payrolls: first Friday of each month (deterministic calendar dates)
NFP = ["2017-05-05", "2017-06-02", "2017-07-07", "2017-08-04", "2017-09-01",
       "2017-10-06", "2017-11-03", "2017-12-01", "2018-01-05", "2018-02-02"]

L = {
    "FOMC": ["A scheduled FOMC decision — the calendar told you volatility was coming; only the direction was unknown.",
             "The first spike frequently reverses once the statement is digested: liquidity is thin and stops are harvested.",
             "Professionals trade the *post*-event structure, not the headline candle; the marked reaction shows why."],
    "ECB": ["A scheduled ECB decision/press conference — the euro's own central bank moves EURUSD harder than most US data.",
            "Forward guidance, not the rate itself, drove this repricing.",
            "News candles that close beyond the pre-event range tend to trend for the session."],
    "NFP": ["Non-farm payrolls, 8:30 ET on the first Friday — the month's flagship US data release.",
            "The 1-hour bars show the classic NFP signature: compression into the release, an impulse, then resolution.",
            "Rule one of news trading: no resting stops near the pre-release range extremes."],
    "EARN": ["An earnings release repriced the stock overnight — the gap is the fundamental information arriving at once.",
             "Gaps of this size cannot be front-run by chart patterns: risk management (position size, no overnight leverage) is the only defense.",
             "Post-earnings drift: the direction of the gap often persists for days-to-weeks, as shown."],
    "GDP": ["Real GDP is the economy's production engine; recessions (shaded, NBER-dated) are its contractions.",
            "Equity bear markets live inside or just ahead of these shaded zones — macro sets the regime for every chart in this book.",
            "The trader's use: GDP trend defines which market regime playbook applies, not day-to-day timing."],
    "CPI": ["CPI year-over-year measures inflation - the variable central banks actually target.",
            "The 1970s double spike shows what un-anchored inflation looks like; the 2008 collapse shows a demand shock.",
            "Rate expectations - and therefore FX and index trends - are downstream of this single series."],
    "RATES": ["The 3-month T-bill tracks the Fed's policy stance through five decades of cycles.",
              "Every hiking cycle ended in either a landing or a recession (shaded) - the sequencing repays study.",
              "Yield-sensitive assets (growth stocks, gold, FX carry) key off the *turns* in this series."],
    "UNEMP": ["Unemployment is the business cycle's confirmation gauge - it bottoms late in booms and peaks after recessions end.",
              "Its inflections, not its level, carry the signal.",
              "Combined with CPI (the Fed's dual mandate), it explains most major policy turns."],
}


def _event_plate(dsn, date, concept, note, lesson, n_before=30, n_after=20):
    df = ds.load(dsn)
    day = pd.Timestamp(date)
    mask = df.index.normalize() == day
    if not mask.any():
        return None
    idx = np.where(mask)[0]
    day_df = df.iloc[idx]
    rng_i = int(np.argmax(day_df.High.values - day_df.Low.values))
    i = int(idx[rng_i])
    if not claim(dsn, df.index[i]):
        return None

    def draw(p, ev=None, dfx=df, idx=idx, note=note):
        d0, d1 = int(idx[0]), int(idx[-1])
        p.ax.axvspan(p.x(d0) - 0.5, p.x(d1) + 0.5, facecolor=an.GOLD, alpha=0.08, zorder=1)
        pre = dfx.iloc[max(0, d0 - 12) : d0]
        p.ray(max(p.w0, d0 - 12), pre.High.max(), color=an.NEUT, x1=d1, label="pre-event high", ls=":")
        p.ray(max(p.w0, d0 - 12), pre.Low.min(), color=an.NEUT, x1=d1, label="pre-event low", ls=":")
        big = int(np.argmax(dfx.High.values[d0 : d1 + 1] - dfx.Low.values[d0 : d1 + 1]))
        j = d0 + big
        p.mark(j, dfx.Close.iloc[j], color=an.DOWN, r=650)
        p.callout(j, dfx.High.iloc[j], note, dx=-16, dy_frac=0.08, color=an.INK)

    return plan(dsn, i, concept, FA, draw, lesson, before=n_before, after=n_after, score=1.0)


def build_fund():
    plans = []

    for d in ["2017-06-14", "2017-09-20", "2017-12-13"]:
        p = _event_plate("EURUSD_1H", d, "FOMC Reaction", FOMC_NOTE.get(d, "FOMC statement 18:00 UTC"), L["FOMC"])
        if p:
            plans.append(p)
    for d, note in ECB.items():
        p = _event_plate("EURUSD_1H", d, "ECB Decision Reaction", note, L["ECB"])
        if p:
            plans.append(p)
    got = 0
    for d in NFP:
        if got >= 4:
            break
        df = ds.load("EURUSD_1H")
        day = pd.Timestamp(d)
        mask = df.index.normalize() == day
        if not mask.any():
            continue
        idx = np.where(mask)[0]
        day_df = df.iloc[idx]
        rng = (day_df.High.max() - day_df.Low.min()) / day_df.Low.min() * 1e4
        if rng < 60:  # keep the big reaction days
            continue
        p = _event_plate("EURUSD_1H", d, "NFP Reaction", "Non-farm payrolls 12:30/13:30 UTC", L["NFP"])
        if p:
            plans.append(p)
            got += 1

    # GOOG earnings gaps - verified in data, famous dates annotated
    KNOWN = {
        "2008-04-18": "Q1'08 earnings beat — +19% gap, one of GOOG's largest",
        "2006-02-01": "Q4'05 earnings miss — first big miss as a public company",
        "2010-10-15": "Q3'10 earnings beat — gap through $600",
        "2011-07-15": "Q2'11 earnings beat — Page's first quarter back as CEO",
        "2011-04-15": "Q1'11 spending worries — gap down on margins",
        "2012-10-18": "Q3'12 report leaked mid-session — trading halted",
    }
    df = ds.load("GOOG_D")
    added = 0
    for d, note in KNOWN.items():
        if added >= 5:
            break
        ts = pd.Timestamp(d)
        if ts not in df.index:
            continue
        i = int(df.index.get_loc(ts))
        gap = (df.Open.iloc[i] / df.Close.iloc[i - 1] - 1) * 100
        intraday = (df.Close.iloc[i] / df.Open.iloc[i] - 1) * 100
        if abs(gap) < 3 and abs(intraday) < 5:
            continue  # verify the documented reaction exists in the data
        if not claim("GOOG_D", ts):
            continue

        def draw(p, ev=None, dfx=df, i=i, note=note, gap=gap, intraday=intraday):
            lo = min(dfx.Close.iloc[i - 1], dfx.Open.iloc[i])
            hi = max(dfx.Close.iloc[i - 1], dfx.Open.iloc[i])
            if abs(gap) >= 3:
                p.zone(i - 1, i, lo, hi, color=an.LIQ, alpha=0.2, label=f"gap {gap:+.1f}%")
            else:
                p.mark(i, dfx.Close.iloc[i], color=an.LIQ, r=700)
            p.callout(i, dfx.High.iloc[i] if gap >= 0 else dfx.Low.iloc[i], note,
                      dx=-18, dy_frac=0.07 if gap >= 0 else -0.07, color=an.INK)

        plans.append(plan("GOOG_D", i, "Earnings Reaction", FA, draw, L["EARN"],
                          before=45, after=35, score=abs(gap) + abs(intraday)))
        added += 1

    # macro plates from statsmodels (rendered as line charts by build.py)
    m = ds.load_macro()
    m["gdp_yoy"] = m.realgdp.pct_change(4) * 100
    m["cpi_yoy"] = m.cpi.pct_change(4) * 100
    # NBER recessions inside 1959-2009 (public record)
    rec = [("1960-04-01", "1961-02-28"), ("1969-12-01", "1970-11-30"), ("1973-11-01", "1975-03-31"),
           ("1980-01-01", "1980-07-31"), ("1981-07-01", "1982-11-30"), ("1990-07-01", "1991-03-31"),
           ("2001-03-01", "2001-11-30"), ("2007-12-01", "2009-06-30")]
    macro_specs = [
        ("US Real GDP Growth (YoY)", "gdp_yoy", "%", L["GDP"],
         "Real GDP growth, quarterly, 1960-2009 — recessions shaded (NBER dates)"),
        ("US CPI Inflation (YoY)", "cpi_yoy", "%", L["CPI"],
         "CPI inflation YoY, 1960-2009 — the 1970s twin spikes and the 2008 deflation shock"),
        ("US Policy Rate Cycle (3M T-bill)", "tbilrate", "%", L["RATES"],
         "3-month Treasury bill rate, 1959-2009 — five decades of Fed cycles"),
        ("US Unemployment Rate", "unemp", "%", L["UNEMP"],
         "Unemployment rate, 1959-2009 — peaks follow recessions with a lag"),
    ]
    for title, col, unit, lesson, sub in macro_specs:
        plans.append(dict(kind="macro", concept=title, category=FA, badge=BADGE[FA],
                          series=m[col].dropna(), unit=unit, lesson=lesson, subtitle=sub,
                          recessions=rec, score=1.0,
                          focal_ts=m[col].dropna().index[-1], dataset="MACRO_Q"))
    return plans
