"""Shared machinery for building the 300-case catalog from detected events."""

from __future__ import annotations

import numpy as np

from . import data_sources as ds
from . import detectors as det

# Category badge colors (fixed identity per category - never cycled)
BADGE = {
    "Smart Money Concepts": "#1F2937",
    "ICT": "#7C3AED",
    "Price Action": "#0F766E",
    "Technical Analysis": "#1D4ED8",
    "Indicators": "#B7791F",
    "Wyckoff": "#C2410C",
    "Elliott Wave": "#0F172A",
    "Fibonacci": "#8B5E12",
    "Fundamental Analysis": "#047857",
}

CAT_ORDER = list(BADGE)

_used = set()  # global (dataset-base, date) dedupe across the whole book


def reset_used():
    _used.clear()


def claim(dataset: str, ts) -> bool:
    key = (dataset.rsplit("_", 1)[0], ts.date())
    if key in _used:
        return False
    _used.add(key)
    return True


def window(df, i, before=70, after=45):
    w0 = max(0, i - before)
    w1 = min(len(df), i + after)
    return w0, w1


def plan(dataset, i, concept, category, draw, lesson, overlays=None, panels=None,
         before=70, after=45, score=0.0, ev=None):
    df = ds.load(dataset)
    w0, w1 = window(df, i, before, after)
    return dict(dataset=dataset, focal_i=i, focal_ts=df.index[i], w0=w0, w1=w1,
                concept=concept, category=category, draw=draw, lesson=lesson,
                overlays=overlays or [], panels=panels or [], score=score,
                badge=BADGE[category], ev=ev)


def take(events, dataset, n, min_gap=8, score_key="score"):
    """Pick top-n events by score with date dedupe and index spacing."""
    df = ds.load(dataset)
    out, taken_i = [], []
    for e in sorted(events, key=lambda e: -e[score_key]):
        i = e["i"]
        if i < 30 or i > len(df) - 12:
            continue
        if any(abs(i - j) < min_gap for j in taken_i):
            continue
        if not claim(dataset, df.index[i]):
            continue
        out.append(e)
        taken_i.append(i)
        if len(out) == n:
            break
    return out


def trade_from(entry, sl, side, rs=(1, 2, 3)):
    risk = abs(entry - sl)
    sgn = 1 if side == "bull" else -1
    return entry, sl, [entry + sgn * risk * r for r in rs]


def swing_leg(df, i, order=6, direction=None):
    """Most recent completed swing (lo_i, lo_p, hi_i, hi_p) before bar i."""
    zz = det.zigzag(df.iloc[max(0, i - 120): i + 1], order)
    if len(zz) < 2:
        return None
    off = max(0, i - 120)
    a, b = zz[-2], zz[-1]
    if a[2] == "L":
        return (a[0] + off, a[1], b[0] + off, b[1])
    return (b[0] + off, b[1], a[0] + off, a[1])
