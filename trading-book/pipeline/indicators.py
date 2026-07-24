"""Standard technical indicators computed on the real OHLCV series.

Plain pandas implementations of the textbook formulas - every value is a
deterministic function of the real historical prices.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def sma(s: pd.Series, n: int) -> pd.Series:
    return s.rolling(n).mean()


def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()


def rsi(close: pd.Series, n: int = 14) -> pd.Series:
    d = close.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rs = up / dn.replace(0, np.nan)
    return 100 - 100 / (1 + rs)


def macd(close: pd.Series, fast: int = 12, slow: int = 26, sig: int = 9):
    line = ema(close, fast) - ema(close, slow)
    signal = ema(line, sig)
    return line, signal, line - signal


def bollinger(close: pd.Series, n: int = 20, k: float = 2.0):
    mid = sma(close, n)
    sd = close.rolling(n).std(ddof=0)
    return mid, mid + k * sd, mid - k * sd


def true_range(df: pd.DataFrame) -> pd.Series:
    pc = df.Close.shift()
    return pd.concat([df.High - df.Low, (df.High - pc).abs(), (df.Low - pc).abs()], axis=1).max(axis=1)


def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    return true_range(df).ewm(alpha=1 / n, adjust=False).mean()


def adx(df: pd.DataFrame, n: int = 14):
    up = df.High.diff()
    dn = -df.Low.diff()
    plus_dm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=df.index)
    minus_dm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=df.index)
    tr = true_range(df).ewm(alpha=1 / n, adjust=False).mean()
    pdi = 100 * plus_dm.ewm(alpha=1 / n, adjust=False).mean() / tr
    mdi = 100 * minus_dm.ewm(alpha=1 / n, adjust=False).mean() / tr
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi).replace(0, np.nan)
    return dx.ewm(alpha=1 / n, adjust=False).mean(), pdi, mdi


def stochastic(df: pd.DataFrame, n: int = 14, d: int = 3):
    ll = df.Low.rolling(n).min()
    hh = df.High.rolling(n).max()
    k = 100 * (df.Close - ll) / (hh - ll)
    return k.rolling(d).mean(), k.rolling(d).mean().rolling(d).mean()


def obv(df: pd.DataFrame) -> pd.Series:
    return (np.sign(df.Close.diff()).fillna(0) * df.Volume).cumsum()


def cci(df: pd.DataFrame, n: int = 20) -> pd.Series:
    tp = (df.High + df.Low + df.Close) / 3
    ma = tp.rolling(n).mean()
    md = (tp - ma).abs().rolling(n).mean()
    return (tp - ma) / (0.015 * md)


def cmf(df: pd.DataFrame, n: int = 20) -> pd.Series:
    mfm = ((df.Close - df.Low) - (df.High - df.Close)) / (df.High - df.Low).replace(0, np.nan)
    mfv = mfm * df.Volume
    return mfv.rolling(n).sum() / df.Volume.rolling(n).sum()


def vwap_session(df: pd.DataFrame) -> pd.Series:
    """Session-anchored VWAP (anchor = each UTC day) for intraday data."""
    tp = (df.High + df.Low + df.Close) / 3
    day = df.index.normalize()
    pv = (tp * df.Volume).groupby(day).cumsum()
    vv = df.Volume.groupby(day).cumsum()
    return pv / vv


def psar(df: pd.DataFrame, af0: float = 0.02, af_max: float = 0.2) -> pd.Series:
    high, low = df.High.values, df.Low.values
    n = len(df)
    out = np.full(n, np.nan)
    bull = True
    af = af0
    ep = high[0]
    sar = low[0]
    for i in range(1, n):
        sar = sar + af * (ep - sar)
        if bull:
            sar = min(sar, low[i - 1], low[i - 2] if i > 1 else low[i - 1])
            if low[i] < sar:
                bull, sar, ep, af = False, ep, low[i], af0
            elif high[i] > ep:
                ep, af = high[i], min(af + af0, af_max)
        else:
            sar = max(sar, high[i - 1], high[i - 2] if i > 1 else high[i - 1])
            if high[i] > sar:
                bull, sar, ep, af = True, ep, high[i], af0
            elif low[i] < ep:
                ep, af = low[i], min(af + af0, af_max)
        out[i] = sar
    return pd.Series(out, index=df.index)


def ichimoku(df: pd.DataFrame):
    conv = (df.High.rolling(9).max() + df.Low.rolling(9).min()) / 2
    base = (df.High.rolling(26).max() + df.Low.rolling(26).min()) / 2
    span_a = ((conv + base) / 2).shift(26)
    span_b = ((df.High.rolling(52).max() + df.Low.rolling(52).min()) / 2).shift(26)
    lagging = df.Close.shift(-26)
    return conv, base, span_a, span_b, lagging


def supertrend(df: pd.DataFrame, n: int = 10, mult: float = 3.0):
    a = atr(df, n)
    mid = (df.High + df.Low) / 2
    ub, lb = mid + mult * a, mid - mult * a
    st = pd.Series(np.nan, index=df.index)
    dirn = pd.Series(1, index=df.index)
    for i in range(1, len(df)):
        prev = st.iloc[i - 1]
        if np.isnan(prev):
            st.iloc[i] = lb.iloc[i]
            continue
        if dirn.iloc[i - 1] == 1:
            st.iloc[i] = max(lb.iloc[i], prev) if df.Close.iloc[i] > prev else ub.iloc[i]
            dirn.iloc[i] = 1 if df.Close.iloc[i] > prev else -1
        else:
            st.iloc[i] = min(ub.iloc[i], prev) if df.Close.iloc[i] < prev else lb.iloc[i]
            dirn.iloc[i] = -1 if df.Close.iloc[i] < prev else 1
    return st, dirn


def volume_profile(df: pd.DataFrame, bins: int = 40):
    """Volume-at-price histogram with POC / VAH / VAL (70% value area)."""
    lo, hi = df.Low.min(), df.High.max()
    edges = np.linspace(lo, hi, bins + 1)
    vol = np.zeros(bins)
    for _, r in df.iterrows():
        lo_i = np.searchsorted(edges, r.Low, "right") - 1
        hi_i = max(lo_i, np.searchsorted(edges, r.High, "left") - 1)
        span = max(hi_i - lo_i + 1, 1)
        vol[max(lo_i, 0) : min(hi_i + 1, bins)] += r.Volume / span
    poc_i = int(vol.argmax())
    total = vol.sum()
    inc = {poc_i}
    lo_i, hi_i = poc_i, poc_i
    while vol[list(inc)].sum() < 0.70 * total and (lo_i > 0 or hi_i < bins - 1):
        below = vol[lo_i - 1] if lo_i > 0 else -1
        above = vol[hi_i + 1] if hi_i < bins - 1 else -1
        if above >= below:
            hi_i += 1
            inc.add(hi_i)
        else:
            lo_i -= 1
            inc.add(lo_i)
    centers = (edges[:-1] + edges[1:]) / 2
    return dict(edges=edges, centers=centers, volume=vol, poc=centers[poc_i], vah=centers[hi_i], val=centers[lo_i])
