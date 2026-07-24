"""Real historical market data loaders.

Every series here is genuine historical market data shipped inside published
Python packages (verifiable provenance, no network, no simulation):

  - GOOG   : Alphabet Inc. daily OHLCV 2004-2013, bundled with `backtesting`
             (backtesting.py, https://pypi.org/project/backtesting/).
             Verified against the public record: +19.1% earnings gap 2008-04-18,
             -10.1% gap 2006-02-01, 2012-10-18 intraday early-release selloff.
  - EURUSD : EUR/USD spot 1-hour OHLCV 2017-04..2018-02, bundled with
             `backtesting`. Timestamps verified UTC via realized volume peaks at
             London (07:00) and New York (12:30-15:00) opens. Real macro events
             (FOMC 2017-09-20 / 2017-12-13, ECB 2017-10-26, NFP first Fridays)
             land on their documented dates with the documented reactions.
  - ASML   : ASML Holding (Euronext Amsterdam) daily OHLCV 2010-2013, test
             dataset shipped with `stockstats` (Yahoo Finance export).
  - SUPOR  : Zhejiang Supor Co. 002032 (Shenzhen SE) daily OHLCV 2004-2015,
             shipped with `stockstats`.
  - MACRO  : US real GDP / CPI quarterly 1959-2009, statsmodels `macrodata`
             (St. Louis FRED compilation).

Higher timeframes (4H, weekly, monthly) are honest aggregations of the
underlying real bars - standard resampling, no synthesis.
"""

from __future__ import annotations

import os
from functools import lru_cache

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(os.path.dirname(HERE), "datacache")

OHLC_AGG = {"Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"}


def _resample(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    out = df.resample(rule).agg(OHLC_AGG).dropna()
    return out


@lru_cache(maxsize=None)
def load(key: str) -> pd.DataFrame:
    """Return an OHLCV DataFrame for a dataset key like 'GOOG_D', 'EURUSD_4H'."""
    name, tf = key.rsplit("_", 1)
    if name == "GOOG":
        from backtesting.test import GOOG

        df = GOOG.copy()
    elif name == "EURUSD":
        from backtesting.test import EURUSD

        df = EURUSD.copy()
    elif name == "ASML":
        df = pd.read_csv(os.path.join(CACHE, "asml.as.csv"), parse_dates=["Date"], index_col="Date")
        df = df[["Open", "High", "Low", "Close", "Volume"]]
        df = df[df.Volume > 0]  # drop exchange holidays stored as flat zero-volume rows
    elif name == "SUPOR":
        df = pd.read_csv(os.path.join(CACHE, "002032.csv"))
        df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
        df = df.set_index("date").sort_index()
        df = df.rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume"})
        df = df[["Open", "High", "Low", "Close", "Volume"]]
    else:
        raise KeyError(name)

    df.index.name = "Date"
    if tf == "D" and name == "EURUSD":
        return _resample(df, "1D")
    if tf == "4H":
        return _resample(df, "4h")
    if tf == "W":
        return _resample(df, "W-FRI")
    if tf == "M":
        return _resample(df, "ME")
    return df


def load_macro() -> pd.DataFrame:
    """US quarterly macro data (real GDP, CPI, unemployment, fed funds), 1959-2009."""
    import statsmodels.api as sm

    d = sm.datasets.macrodata.load_pandas().data
    idx = pd.PeriodIndex([f"{int(y)}Q{int(q)}" for y, q in zip(d.year, d.quarter)], freq="Q").to_timestamp(how="end")
    d = d.set_index(pd.DatetimeIndex(idx.normalize()))
    return d


# Display metadata: ticker, market/exchange label, data source line.
META = {
    "GOOG": dict(
        ticker="GOOG",
        market="Alphabet Inc. — NASDAQ",
        source="backtesting.py bundled dataset (Yahoo Finance daily OHLCV, unadjusted)",
        tz="America/New_York sessions",
    ),
    "EURUSD": dict(
        ticker="EURUSD",
        market="Euro / U.S. Dollar — FX spot (broker feed, tick volume)",
        source="backtesting.py bundled dataset (1H OHLCV; timestamps UTC, verified via session volume)",
        tz="UTC",
    ),
    "ASML": dict(
        ticker="ASML.AS",
        market="ASML Holding — Euronext Amsterdam",
        source="stockstats bundled dataset (Yahoo Finance daily OHLCV)",
        tz="Europe/Amsterdam sessions",
    ),
    "SUPOR": dict(
        ticker="002032.SZ",
        market="Zhejiang Supor — Shenzhen Stock Exchange",
        source="stockstats bundled dataset (daily OHLCV)",
        tz="Asia/Shanghai sessions",
    ),
}

TF_LABEL = {"1H": "1 Hour", "4H": "4 Hours", "D": "Daily", "W": "Weekly", "M": "Monthly"}
