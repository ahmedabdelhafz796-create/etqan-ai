"""Algorithmic detection of trading setups in the real historical data.

Each detector scans a real OHLCV series and returns candidate events:
    dict(i=<focal integer index>, score=<quality>, **payload)
Nothing is drawn that was not found in the data - annotations mark actual
detected occurrences (gaps, sweeps, structure breaks, pattern geometry).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.signal import argrelextrema

from . import indicators as ind


# ---------------------------------------------------------------- swings

def swings(df: pd.DataFrame, order: int = 5):
    """Swing highs/lows as (index, price) arrays using local extrema."""
    hi = argrelextrema(df.High.values, np.greater_equal, order=order)[0]
    lo = argrelextrema(df.Low.values, np.less_equal, order=order)[0]
    # collapse plateaus
    hi = [i for k, i in enumerate(hi) if k == 0 or i - hi[k - 1] > order // 2]
    lo = [i for k, i in enumerate(lo) if k == 0 or i - lo[k - 1] > order // 2]
    return np.array(hi, dtype=int), np.array(lo, dtype=int)


def zigzag(df: pd.DataFrame, order: int = 5):
    """Alternating swing sequence [(i, price, 'H'|'L'), ...]."""
    hi, lo = swings(df, order)
    pts = [(int(i), float(df.High.iloc[i]), "H") for i in hi] + [(int(i), float(df.Low.iloc[i]), "L") for i in lo]
    pts.sort()
    out = []
    for p in pts:
        if out and out[-1][2] == p[2]:
            if (p[2] == "H" and p[1] >= out[-1][1]) or (p[2] == "L" and p[1] <= out[-1][1]):
                out[-1] = p
        else:
            out.append(p)
    return out


def _rng(df, i, n=100):
    seg = df.iloc[max(0, i - n) : i + 1]
    return float(seg.High.max() - seg.Low.min()) or 1e-9


# ---------------------------------------------------------------- SMC

def fvg(df, min_frac=0.15):
    """3-candle fair value gaps; size relative to ATR filters noise."""
    a = ind.atr(df).values
    out = []
    H, L = df.High.values, df.Low.values
    for i in range(2, len(df) - 5):
        if np.isnan(a[i]) or a[i] == 0:
            continue
        gap_up = L[i] - H[i - 2]
        gap_dn = L[i - 2] - H[i]
        if gap_up > min_frac * a[i]:
            out.append(dict(i=i - 1, score=gap_up / a[i], side="bull", top=L[i], bot=H[i - 2]))
        if gap_dn > min_frac * a[i]:
            out.append(dict(i=i - 1, score=gap_dn / a[i], side="bear", top=L[i - 2], bot=H[i]))
    return out


def displacement(df, mult=2.2):
    a = ind.atr(df).values
    body = (df.Close - df.Open).values
    out = []
    for i in range(20, len(df) - 5):
        if abs(body[i]) > mult * a[i]:
            out.append(dict(i=i, score=abs(body[i]) / a[i], side="bull" if body[i] > 0 else "bear"))
    return out


def order_block(df, disp_mult=1.8):
    """Last opposite candle before a displacement leg."""
    a = ind.atr(df).values
    C, O, H, L = df.Close.values, df.Open.values, df.High.values, df.Low.values
    out = []
    for i in range(20, len(df) - 10):
        move = C[i + 2] - C[i]  # 3-bar leg after candidate
        if C[i] < O[i] and move > disp_mult * a[i]:  # bearish candle then strong rally
            out.append(dict(i=i, score=move / a[i], side="bull", top=H[i], bot=L[i]))
        if C[i] > O[i] and -move > disp_mult * a[i]:
            out.append(dict(i=i, score=-move / a[i], side="bear", top=H[i], bot=L[i]))
    return out


def structure_events(df, order=6):
    """BOS and CHoCH from the zigzag swing sequence."""
    zz = zigzag(df, order)
    out = []
    trend = 0  # 1 up, -1 down
    for k in range(2, len(zz)):
        i, p, t = zz[k]
        pi, pp, pt = zz[k - 2]  # previous same-type swing
        if t == "H":
            if p > pp:
                kind = "BOS" if trend >= 0 else "CHOCH"
                out.append(dict(i=i, score=(p - pp) / _rng(df, i), kind=kind, side="bull",
                                level=pp, level_i=pi, zz_k=k))
                trend = 1
        else:
            if p < pp:
                kind = "BOS" if trend <= 0 else "CHOCH"
                out.append(dict(i=i, score=(pp - p) / _rng(df, i), kind=kind, side="bear",
                                level=pp, level_i=pi, zz_k=k))
                trend = -1
    return out


def equal_levels(df, order=5, tol_frac=0.0012, kind="H"):
    """Equal highs (kind='H') or equal lows resting liquidity."""
    hi, lo = swings(df, order)
    idx = hi if kind == "H" else lo
    px = df.High.values if kind == "H" else df.Low.values
    out = []
    for a_k in range(len(idx) - 1):
        for b_k in range(a_k + 1, min(a_k + 4, len(idx))):
            i1, i2 = idx[a_k], idx[b_k]
            if i2 - i1 < order or i2 - i1 > 60:
                continue
            p1, p2 = px[i1], px[i2]
            if abs(p1 - p2) <= tol_frac * p1:
                out.append(dict(i=int(i2), score=1 - abs(p1 - p2) / (tol_frac * p1),
                                i1=int(i1), i2=int(i2), level=float((p1 + p2) / 2), kind=kind))
    return out


def sweep(df, order=5, lookback=40):
    """Liquidity sweep: wick beyond a prior swing level, close back inside, reversal."""
    hi, lo = swings(df, order)
    H, L, C = df.High.values, df.Low.values, df.Close.values
    out = []
    for i in range(order, len(df) - 6):
        for s in hi[(hi < i - 1) & (hi > i - lookback)]:
            lvl = H[s]
            if H[i] > lvl and C[i] < lvl and C[i + 3] < C[i]:  # swept highs, rejected
                out.append(dict(i=i, score=(H[i] - lvl) / _rng(df, i) + (C[i] - C[i + 3]) / _rng(df, i),
                                side="bear", level=float(lvl), level_i=int(s)))
                break
        for s in lo[(lo < i - 1) & (lo > i - lookback)]:
            lvl = L[s]
            if L[i] < lvl and C[i] > lvl and C[i + 3] > C[i]:
                out.append(dict(i=i, score=(lvl - L[i]) / _rng(df, i) + (C[i + 3] - C[i]) / _rng(df, i),
                                side="bull", level=float(lvl), level_i=int(s)))
                break
    return out


# ---------------------------------------------------------------- candles

def engulfing(df):
    O, C = df.Open.values, df.Close.values
    a = ind.atr(df).values
    out = []
    for i in range(15, len(df) - 5):
        b0, b1 = C[i - 1] - O[i - 1], C[i] - O[i]
        if b0 < 0 < b1 and O[i] <= C[i - 1] and C[i] >= O[i - 1] and abs(b1) > 0.8 * a[i]:
            out.append(dict(i=i, score=abs(b1) / a[i], side="bull"))
        if b1 < 0 < b0 and O[i] >= C[i - 1] and C[i] <= O[i - 1] and abs(b1) > 0.8 * a[i]:
            out.append(dict(i=i, score=abs(b1) / a[i], side="bear"))
    return out


def pin_bar(df):
    O, C, H, L = df.Open.values, df.Close.values, df.High.values, df.Low.values
    a = ind.atr(df).values
    out = []
    for i in range(15, len(df) - 5):
        rng = H[i] - L[i]
        if rng < 0.8 * a[i] or rng == 0:
            continue
        body = abs(C[i] - O[i])
        up_w = H[i] - max(O[i], C[i])
        dn_w = min(O[i], C[i]) - L[i]
        if dn_w > 2 * body and dn_w > 0.6 * rng:
            out.append(dict(i=i, score=dn_w / rng * rng / a[i], side="bull"))
        if up_w > 2 * body and up_w > 0.6 * rng:
            out.append(dict(i=i, score=up_w / rng * rng / a[i], side="bear"))
    return out


def inside_bar(df):
    H, L = df.High.values, df.Low.values
    out = []
    for i in range(15, len(df) - 5):
        if H[i] < H[i - 1] and L[i] > L[i - 1]:
            brk = 1 if H[i + 1] > H[i - 1] else (-1 if L[i + 1] < L[i - 1] else 0)
            out.append(dict(i=i, score=(H[i - 1] - L[i - 1]) / _rng(df, i) + abs(brk),
                            mother_hi=float(H[i - 1]), mother_lo=float(L[i - 1]), brk=brk))
    return out


def outside_bar(df):
    H, L, C, O = df.High.values, df.Low.values, df.Close.values, df.Open.values
    a = ind.atr(df).values
    out = []
    for i in range(15, len(df) - 5):
        if H[i] > H[i - 1] and L[i] < L[i - 1] and (H[i] - L[i]) > 1.4 * a[i]:
            out.append(dict(i=i, score=(H[i] - L[i]) / a[i], side="bull" if C[i] > O[i] else "bear"))
    return out


def gaps(df, min_pct=3.0):
    C, O = df.Close.values, df.Open.values
    out = []
    for i in range(1, len(df) - 5):
        g = (O[i] / C[i - 1] - 1) * 100
        if abs(g) >= min_pct:
            out.append(dict(i=i, score=abs(g), pct=float(g), side="bull" if g > 0 else "bear"))
    return out


# ---------------------------------------------------------------- classical patterns

def double_extreme(df, order=7, tol=0.015, kind="top"):
    zz = zigzag(df, order)
    out = []
    for k in range(4, len(zz)):
        a, b, c = zz[k - 4], zz[k - 3], zz[k - 2]
        d = zz[k - 1] if k - 1 < len(zz) else None
        want = "H" if kind == "top" else "L"
        if a[2] == want and c[2] == want and b[2] != want:
            if abs(a[1] - c[1]) <= tol * a[1] and c[0] - a[0] >= 2 * order:
                neck = b[1]
                # confirmation: price beyond neckline after c
                seg = df.iloc[c[0] : min(c[0] + 40, len(df))]
                conf = None
                if kind == "top":
                    br = seg[seg.Close < neck]
                else:
                    br = seg[seg.Close > neck]
                if len(br):
                    conf = int(df.index.get_loc(br.index[0]))
                    out.append(dict(i=conf, score=1 - abs(a[1] - c[1]) / (tol * a[1]) + abs(a[1] - neck) / _rng(df, c[0]),
                                    p1=a, p2=c, neck=float(neck), neck_i=int(b[0]), kind=kind))
    return out


def head_shoulders(df, order=7, tol=0.06):
    zz = zigzag(df, order)
    out = []
    for k in range(6, len(zz)):
        s = zz[k - 6 : k + 1]
        if [p[2] for p in s[:5]] == ["H", "L", "H", "L", "H"]:
            l_s, t1, head, t2, r_s = s[0], s[1], s[2], s[3], s[4]
            inv = False
        elif [p[2] for p in s[:5]] == ["L", "H", "L", "H", "L"]:
            l_s, t1, head, t2, r_s = s[0], s[1], s[2], s[3], s[4]
            inv = True
        else:
            continue
        if not inv:
            if not (head[1] > l_s[1] and head[1] > r_s[1] and abs(l_s[1] - r_s[1]) < tol * head[1]):
                continue
        else:
            if not (head[1] < l_s[1] and head[1] < r_s[1] and abs(l_s[1] - r_s[1]) < tol * abs(head[1])):
                continue
        neck = (t1[1] + t2[1]) / 2
        seg = df.iloc[r_s[0] : min(r_s[0] + 50, len(df))]
        br = seg[seg.Close < neck] if not inv else seg[seg.Close > neck]
        if len(br):
            conf = int(df.index.get_loc(br.index[0]))
            amp = abs(head[1] - neck) / _rng(df, conf)
            out.append(dict(i=conf, score=amp + (1 - abs(l_s[1] - r_s[1]) / (tol * abs(head[1]))),
                            pts=[l_s, t1, head, t2, r_s], neck=float(neck), inv=inv))
    return out


def trend_channel(df, win=60, min_r2=0.75):
    """Linear regression channels over rolling windows; picks clean trends."""
    out = []
    C = df.Close.values
    x = np.arange(win)
    for i in range(win, len(df) - 10, win // 3):
        y = C[i - win : i]
        A = np.vstack([x, np.ones(win)]).T
        (m, b), res, *_ = np.linalg.lstsq(A, y, rcond=None)
        pred = m * x + b
        ss_res = ((y - pred) ** 2).sum()
        ss_tot = ((y - y.mean()) ** 2).sum() or 1e-9
        r2 = 1 - ss_res / ss_tot
        if r2 > min_r2:
            resid = y - pred
            out.append(dict(i=i - 1, score=r2, start=i - win, m=float(m), b=float(b),
                            up=float(resid.max()), dn=float(resid.min()),
                            side="bull" if m > 0 else "bear"))
    return out


def triangle(df, order=6, win=70):
    """Converging swing trendlines (symmetrical/ascending/descending)."""
    out = []
    for end in range(win, len(df) - 10, win // 3):
        seg = df.iloc[end - win : end]
        hi, lo = swings(seg, order)
        if len(hi) < 3 or len(lo) < 3:
            continue
        hx, hy = hi[-3:], seg.High.values[hi[-3:]]
        lx, ly = lo[-3:], seg.Low.values[lo[-3:]]
        mh = np.polyfit(hx, hy, 1)[0]
        ml = np.polyfit(lx, ly, 1)[0]
        scale = seg.Close.mean()
        mh_n, ml_n = mh / scale * 1000, ml / scale * 1000
        if mh_n < -0.3 and ml_n > 0.3:
            kind = "symmetrical"
        elif abs(mh_n) < 0.25 and ml_n > 0.4:
            kind = "ascending"
        elif mh_n < -0.4 and abs(ml_n) < 0.25:
            kind = "descending"
        else:
            continue
        out.append(dict(i=end - 1, score=abs(mh_n - ml_n), start=end - win, kind=kind,
                        h_pts=[(int(end - win + i), float(v)) for i, v in zip(hx, hy)],
                        l_pts=[(int(end - win + i), float(v)) for i, v in zip(lx, ly)]))
    return out


def flag(df, pole_mult=3.5, cons_win=10):
    """Sharp pole then tight drifting consolidation."""
    a = ind.atr(df).values
    C = df.Close.values
    out = []
    for i in range(25, len(df) - cons_win - 5):
        pole = C[i] - C[i - 5]
        if abs(pole) < pole_mult * a[i]:
            continue
        cons = df.iloc[i + 1 : i + 1 + cons_win]
        width = cons.High.max() - cons.Low.min()
        drift = cons.Close.iloc[-1] - cons.Close.iloc[0]
        if width < 0.45 * abs(pole) and np.sign(drift) != np.sign(pole):
            out.append(dict(i=i + cons_win, score=abs(pole) / a[i] * (0.45 - width / abs(pole)),
                            pole_start=i - 5, pole_end=i, cons_end=i + cons_win,
                            side="bull" if pole > 0 else "bear"))
    return out


def wedge(df, order=5, win=60):
    """Rising/falling wedge: both lines same direction, converging."""
    out = []
    for end in range(win, len(df) - 10, win // 3):
        seg = df.iloc[end - win : end]
        hi, lo = swings(seg, order)
        if len(hi) < 3 or len(lo) < 3:
            continue
        hx, hy = hi[-3:], seg.High.values[hi[-3:]]
        lx, ly = lo[-3:], seg.Low.values[lo[-3:]]
        mh = np.polyfit(hx, hy, 1)[0]
        ml = np.polyfit(lx, ly, 1)[0]
        scale = seg.Close.mean() / 1000
        if mh > 0.3 * scale and ml > 0.3 * scale and ml > mh * 1.4:
            kind = "rising"
        elif mh < -0.3 * scale and ml < -0.3 * scale and mh < ml * 1.4:
            kind = "falling"
        else:
            continue
        out.append(dict(i=end - 1, score=abs(ml - mh) / scale, start=end - win, kind=kind,
                        h_pts=[(int(end - win + i), float(v)) for i, v in zip(hx, hy)],
                        l_pts=[(int(end - win + i), float(v)) for i, v in zip(lx, ly)]))
    return out


def rectangle_range(df, win=40, tol=0.25):
    """Sideways range: flat top/bottom relative to height."""
    out = []
    a = ind.atr(df).values
    for end in range(win + 20, len(df) - 10, win // 2):
        seg = df.iloc[end - win : end]
        hi, lo = swings(seg, 4)
        if len(hi) < 2 or len(lo) < 2:
            continue
        tops = seg.High.values[hi]
        bots = seg.Low.values[lo]
        height = seg.High.max() - seg.Low.min()
        if height < 3 * a[end]:
            continue
        if tops.std() < tol * height and bots.std() < tol * height and (tops.mean() - bots.mean()) > 0.5 * height:
            out.append(dict(i=end - 1, score=1 / (tops.std() + bots.std() + 1e-9) * height,
                            start=end - win, top=float(tops.mean()), bot=float(bots.mean())))
    return out


def cup_handle(df, win=90):
    """Rounded base then small handle near the rim."""
    C = df.Close.values
    out = []
    for end in range(win + 20, len(df) - 15, 10):
        seg = C[end - win : end]
        x = np.arange(win)
        coef = np.polyfit(x, seg, 2)
        pred = np.polyval(coef, x)
        r2 = 1 - ((seg - pred) ** 2).sum() / (((seg - seg.mean()) ** 2).sum() or 1e-9)
        if coef[0] > 0 and r2 > 0.55:  # upward parabola = rounded bottom
            rim = max(seg[0], seg[-1])
            depth = rim - seg.min()
            handle = df.iloc[end : end + 12]
            if len(handle) and handle.Low.min() > rim - 0.4 * depth and handle.High.max() < rim * 1.03:
                out.append(dict(i=end + len(handle) - 1, score=r2 * depth / _rng(df, end),
                                start=end - win, rim=float(rim), cup_end=end, r2=r2))
    return out


# ---------------------------------------------------------------- Wyckoff

def spring_upthrust(df, win=45, kind="spring"):
    """False break out of a trading range then reclaim (Wyckoff spring / upthrust)."""
    out = []
    for end in range(win + 10, len(df) - 12, 5):
        seg = df.iloc[end - win : end]
        top, bot = seg.High.quantile(0.92), seg.Low.quantile(0.08)
        height = top - bot
        if height / seg.Close.mean() < 0.02:
            continue
        i = end  # candidate break bar
        bar = df.iloc[i]
        after = df.iloc[i + 1 : i + 10]
        if kind == "spring" and bar.Low < bot - 0.1 * height and bar.Close > bot - 0.15 * height and after.Close.max() > bot + 0.4 * height:
            out.append(dict(i=i, score=(bot - bar.Low) / height + (after.Close.max() - bot) / height,
                            start=end - win, top=float(top), bot=float(bot)))
        if kind == "upthrust" and bar.High > top + 0.1 * height and bar.Close < top + 0.15 * height and after.Close.min() < top - 0.4 * height:
            out.append(dict(i=i, score=(bar.High - top) / height + (top - after.Close.min()) / height,
                            start=end - win, top=float(top), bot=float(bot)))
    return out


# ---------------------------------------------------------------- indicator events

def rsi_divergence(df, order=6):
    r = ind.rsi(df.Close)
    zz = zigzag(df, order)
    out = []
    lows = [p for p in zz if p[2] == "L"]
    highs = [p for p in zz if p[2] == "H"]
    for k in range(1, len(lows)):
        (i1, p1, _), (i2, p2, _) = lows[k - 1], lows[k]
        if i2 - i1 < 5 or i2 - i1 > 60 or np.isnan(r.iloc[i1]) or np.isnan(r.iloc[i2]):
            continue
        if p2 < p1 and r.iloc[i2] > r.iloc[i1] + 2 and r.iloc[i2] < 45:
            out.append(dict(i=i2, score=(r.iloc[i2] - r.iloc[i1]) + (p1 - p2) / _rng(df, i2) * 20,
                            side="bull", i1=i1, i2=i2, p1=p1, p2=p2, r1=float(r.iloc[i1]), r2=float(r.iloc[i2])))
    for k in range(1, len(highs)):
        (i1, p1, _), (i2, p2, _) = highs[k - 1], highs[k]
        if i2 - i1 < 5 or i2 - i1 > 60 or np.isnan(r.iloc[i1]) or np.isnan(r.iloc[i2]):
            continue
        if p2 > p1 and r.iloc[i2] < r.iloc[i1] - 2 and r.iloc[i2] > 55:
            out.append(dict(i=i2, score=(r.iloc[i1] - r.iloc[i2]) + (p2 - p1) / _rng(df, i2) * 20,
                            side="bear", i1=i1, i2=i2, p1=p1, p2=p2, r1=float(r.iloc[i1]), r2=float(r.iloc[i2])))
    return out


def macd_cross(df):
    line, sig, hist = ind.macd(df.Close)
    out = []
    for i in range(30, len(df) - 10):
        if np.isnan(line.iloc[i - 1]):
            continue
        prev, cur = line.iloc[i - 1] - sig.iloc[i - 1], line.iloc[i] - sig.iloc[i]
        move = abs(df.Close.iloc[min(i + 8, len(df) - 1)] - df.Close.iloc[i]) / _rng(df, i)
        if prev < 0 < cur:
            out.append(dict(i=i, score=move + abs(line.iloc[i]) / (df.Close.iloc[i] * 0.01), side="bull"))
        if prev > 0 > cur:
            out.append(dict(i=i, score=move + abs(line.iloc[i]) / (df.Close.iloc[i] * 0.01), side="bear"))
    return out


def ma_cross(df, fast=50, slow=200):
    f, s = ind.sma(df.Close, fast), ind.sma(df.Close, slow)
    out = []
    for i in range(slow + 1, len(df) - 5):
        if np.isnan(s.iloc[i - 1]):
            continue
        prev, cur = f.iloc[i - 1] - s.iloc[i - 1], f.iloc[i] - s.iloc[i]
        if prev < 0 < cur:
            out.append(dict(i=i, score=1.0, side="bull"))
        if prev > 0 > cur:
            out.append(dict(i=i, score=1.0, side="bear"))
    return out


def bb_squeeze(df, n=20):
    mid, up, lo = ind.bollinger(df.Close, n)
    width = (up - lo) / mid
    out = []
    for i in range(n + 30, len(df) - 15):
        w = width.iloc[i]
        if np.isnan(w):
            continue
        if w == width.iloc[i - 30 : i + 1].min():
            brk = df.Close.iloc[i + 10] - df.Close.iloc[i]
            out.append(dict(i=i, score=abs(brk) / _rng(df, i) / (w + 1e-9) * 0.1,
                            side="bull" if brk > 0 else "bear"))
    return out
