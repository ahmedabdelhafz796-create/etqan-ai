# MACD (Moving Average Convergence Divergence) — Momentum Indicator

## Executive Summary

MACD measures momentum by comparing two exponential moving averages. It consists of the MACD line, signal line, and histogram, helping traders identify trend changes and momentum shifts.

**Formula**:
- MACD Line: 12-period EMA minus 26-period EMA
- Signal Line: 9-period EMA of MACD line
- Histogram: MACD line minus signal line

---

## MACD Components

### The MACD Line

```
MACD = EMA-12 - EMA-26

Where:
  EMA-12: 12-period exponential moving average (faster, more responsive)
  EMA-26: 26-period exponential moving average (slower, smoothed)

Interpretation:
  MACD > 0: Bullish (short-term average above long-term)
  MACD < 0: Bearish (short-term average below long-term)
  MACD rising: Momentum increasing (bullish)
  MACD falling: Momentum decreasing (bearish)
```

### The Signal Line (9-period EMA)

```
Signal Line = 9-period EMA of MACD

Purpose: Smooth the MACD for clearer signals

Interpretation:
  MACD > Signal: Bullish momentum (uptrend)
  MACD < Signal: Bearish momentum (downtrend)
  MACD crossing above Signal: BULLISH crossover (buy signal)
  MACD crossing below Signal: BEARISH crossover (sell signal)
```

### The Histogram

```
Histogram = MACD - Signal Line

Purpose: Visual representation of momentum strength

Interpretation:
  Positive histogram + rising: Bullish (momentum strengthening)
  Positive histogram + falling: Weakening (uptrend fading)
  Negative histogram + falling: Bearish (momentum strengthening)
  Negative histogram + rising: Weakening (downtrend fading)
```

---

## MACD Trading Signals

### Crossover Signals

```
Signal 1: MACD Crosses Above Signal Line
  Trigger: MACD (t-1) < Signal (t-1), MACD (t) > Signal (t)
  Interpretation: BULLISH momentum reversal
  Use: Entry confirmation for BUY signals
  
Signal 2: MACD Crosses Below Signal Line
  Trigger: MACD (t-1) > Signal (t-1), MACD (t) < Signal (t)
  Interpretation: BEARISH momentum reversal
  Use: Entry confirmation for SELL signals or exit BUY positions
```

### Histogram Patterns

```
Pattern: Positive histogram, rising
  → Bullish momentum strengthening
  → Confirm uptrend, continue buying
  
Pattern: Positive histogram, falling
  → Bullish momentum weakening
  → Caution, watch for crossover to bearish
  
Pattern: Negative histogram, falling
  → Bearish momentum strengthening
  → Confirm downtrend, avoid buying
  
Pattern: Negative histogram, rising
  → Bearish momentum weakening
  → Caution, watch for crossover to bullish
```

---

## MACD Confluence in Multi-timeframe Analysis

### Bullish Alignment (3/5 confluence)

```
Scenario: All three timeframes show bullish MACD
  Weekly MACD:  > Signal (positive histogram)
  Daily MACD:   > Signal (positive histogram)
  H4 MACD:      > Signal (positive histogram)
  
Signal: STRONG BULLISH CONFLUENCE
Entry: BUY signal confirmed
Confidence: Base 60% + 5% bonus = 65%
```

### Bearish Misalignment (confluence failure)

```
Scenario: Timeframes conflict
  Weekly MACD:  > Signal (bullish)
  Daily MACD:   < Signal (bearish)
  H4 MACD:      > Signal (bullish)
  
Signal: CONFLICTING (2 bullish, 1 bearish out of 3)
Entry: WAIT for alignment
Recommendation: Require additional technical confirmation
```

---

## Limitations and Best Practices

### Limitation 1: Lagging Indicator

```
MACD is momentum-based, not leading

Problem: MACD confirms trends but signals reversals late
  Price has often moved significantly before MACD crossover
  
Solution: Combine MACD with other indicators (RSI, support/resistance)
```

### Limitation 2: Whipsaws in Choppy Markets

```
In range-bound markets, MACD generates false signals

Problem: Constant crossovers back/forth without trending
  Entry, stop hit, reverse, stop hit pattern
  
Solution: Check if price is above/below key moving averages first
          (Avoid entries unless price in clear trend)
```

---

## References

- Appel, Gerald, "Technical Analysis: Power Tools for Active Investors" (2005) — MACD original methodology
- Murphy, John J., "Technical Analysis of Financial Markets" (1999)
- Pring, Martin J., "Technical Analysis Explained" (2002)
