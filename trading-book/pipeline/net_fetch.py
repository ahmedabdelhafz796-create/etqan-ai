"""Network fetchers for full multi-market coverage.

These are ready-to-use once the environment's egress policy allows the hosts
below (they were tested and denied in the build sandbox: HTTP CONNECT 403).
Allow-list needed: api.binance.com, data.binance.vision, query1.finance.yahoo.com,
stooq.com — or run on any unrestricted machine.

Usage:
    from pipeline.net_fetch import binance_klines, yahoo_chart, stooq_daily
    btc = binance_klines("BTCUSDT", "4h", limit=1000)

Each fetcher returns a standard OHLCV DataFrame indexed by UTC timestamp, ready
to drop into data_sources.load() so the existing detectors/renderers produce
the full 27-market catalog with no other changes.
"""

from __future__ import annotations

import time

import pandas as pd
import requests

UA = {"User-Agent": "Mozilla/5.0 (trading-book pipeline)"}


def binance_klines(symbol: str, interval: str, limit: int = 1000,
                   end_ms: int | None = None) -> pd.DataFrame:
    """Spot klines from Binance's public REST API (no key required)."""
    params = dict(symbol=symbol, interval=interval, limit=limit)
    if end_ms:
        params["endTime"] = end_ms
    r = requests.get("https://api.binance.com/api/v3/klines", params=params, headers=UA, timeout=30)
    r.raise_for_status()
    rows = r.json()
    df = pd.DataFrame(rows, columns=["t", "Open", "High", "Low", "Close", "Volume",
                                     "ct", "qv", "n", "tb", "tq", "x"])
    df.index = pd.to_datetime(df.t, unit="ms", utc=True)
    return df[["Open", "High", "Low", "Close", "Volume"]].astype(float)


def binance_klines_range(symbol: str, interval: str, start: str, end: str) -> pd.DataFrame:
    """Paginate klines across an arbitrary historical range."""
    start_ms = int(pd.Timestamp(start, tz="UTC").timestamp() * 1000)
    end_ms = int(pd.Timestamp(end, tz="UTC").timestamp() * 1000)
    out = []
    cur = end_ms
    while cur > start_ms:
        chunk = binance_klines(symbol, interval, limit=1000, end_ms=cur)
        if chunk.empty:
            break
        out.append(chunk)
        cur = int(chunk.index[0].timestamp() * 1000) - 1
        time.sleep(0.25)  # public rate limit courtesy
    df = pd.concat(out).sort_index()
    return df[~df.index.duplicated()].loc[start:end]


def yahoo_chart(symbol: str, interval: str = "1d", range_: str = "10y") -> pd.DataFrame:
    """Yahoo Finance v8 chart API (indices ^GSPC ^IXIC ^DJI ^GDAXI ^N225,
    futures GC=F SI=F CL=F NG=F, FX EURUSD=X, stocks AAPL MSFT TSLA NVDA AMZN META GOOGL)."""
    r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
                     params=dict(interval=interval, range=range_), headers=UA, timeout=30)
    r.raise_for_status()
    res = r.json()["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    df = pd.DataFrame(dict(Open=q["open"], High=q["high"], Low=q["low"],
                           Close=q["close"], Volume=q["volume"]),
                      index=pd.to_datetime(res["timestamp"], unit="s", utc=True))
    return df.dropna()


def stooq_daily(symbol: str) -> pd.DataFrame:
    """Full daily history CSV from stooq.com (e.g. 'aapl.us', 'eurusd', '^spx')."""
    r = requests.get(f"https://stooq.com/q/d/l/?s={symbol}&i=d", headers=UA, timeout=30)
    r.raise_for_status()
    from io import StringIO

    df = pd.read_csv(StringIO(r.text), parse_dates=["Date"], index_col="Date")
    return df[["Open", "High", "Low", "Close", "Volume"]]
