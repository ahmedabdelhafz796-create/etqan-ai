# Multi-timeframe Technical Analysis — Confluence Framework

## Executive Summary

Trading on multiple timeframes simultaneously increases signal reliability. This system uses 4 timeframes: Weekly (trend), Daily (structure), H4 (confirmation), and M15 (entry timing).

**Core Rule**: ≥3 indicators aligned across timeframes = BUY/SELL signal. <3 indicators = WAIT.

---

## Timeframe Hierarchy

### Weekly (Primary Trend)

```
Purpose: Identify long-term direction
Typical Move: $50-200 over 1-2 weeks
Indicators:
  - MA-200 (long-term support/resistance)
  - Price position (above/below MA)
  - Basic structure (uptrend, downtrend, consolidation)

Signal Strength: Most important (defines macro bias)
```

### Daily (Intermediate Trend)

```
Purpose: Confirm weekly bias, identify pullbacks
Typical Move: $15-50 per day
Indicators:
  - MA-50 (short-term support)
  - Price position (above/below MA-50)
  - Daily momentum (closing prices, support/resistance)

Signal Strength: Filters weekly signal (confirms or questions)
```

### H4 (Tactical Confirmation)

```
Purpose: Verify momentum before entry
Typical Move: $5-20 per 4-hour candle
Indicators:
  - RSI-14 (momentum, not overbought/oversold)
  - MACD (histogram positive/negative)
  - MA-50 (support level)

Signal Strength: Confirms daily signal or warns of divergence
```

### M15/M5 (Entry Timing)

```
Purpose: Precise entry point execution
Typical Move: $1-5 per 15-minute candle
Indicators:
  - RSI-14 (<50 for longs, entry not overextended)
  - MACD crossover (exact entry confirmation)
  - Support/resistance (key levels)

Signal Strength: Tactical only (does not override higher timeframes)
```

---

## Confluence Rules (5 Indicators Total)

### Indicator 1: Weekly Structure (MA-200)

```
Gold Weekly:
  If Price > MA-200: Uptrend structure, +1 confluence
  If Price < MA-200: Downtrend structure, -1 confluence (SELL setup)
  If Price near MA-200: Consolidation, 0 confluence (neutral)

Bullish Example: Gold $2,350, MA-200 $2,310 → Price above = +1
Bearish Example: Gold $1,950, MA-200 $2,020 → Price below = -1 (avoid BUY)
```

### Indicator 2: Daily Momentum (MA-50)

```
Gold Daily:
  If Price > MA-50: Daily bullish, +1 confluence
  If Price < MA-50: Daily bearish, -1 confluence (avoid BUY)
  
Bullish Example: Gold $2,335, MA-50 $2,330 → Price above = +1
Bearish Example: Gold $2,320, MA-50 $2,330 → Price below = -1
```

### Indicator 3: H4 RSI (Momentum Check)

```
Gold H4 RSI-14:
  If 30 < RSI < 70: Healthy momentum, +1 confluence
  If RSI > 70: Overbought (reversal risk), 0 confluence (caution)
  If RSI < 30: Oversold (dead weight), 0 confluence (weak)

Bullish Example: Gold H4 RSI = 55 → In healthy zone = +1
Overbought Risk: Gold H4 RSI = 74 → Approaching overbought = 0
```

### Indicator 4: H4 MACD (Trend Confirmation)

```
Gold H4 MACD:
  If MACD > Signal AND Histogram > 0: Bullish, +1 confluence
  If MACD < Signal OR Histogram < 0: Bearish, -1 confluence
  If MACD near Signal: Transition, 0 confluence (neutral)

Bullish Example: MACD 15, Signal 12, Histogram +3 → Bullish = +1
Bearish Example: MACD 8, Signal 12, Histogram -4 → Bearish = -1
```

### Indicator 5: M15 Entry Timing (RSI)

```
Gold M15 RSI-14:
  If RSI < 50: Entry not overextended, +1 confluence (good entry)
  If 50 < RSI < 65: Entry neutral, 0 confluence
  If RSI > 65: Entry overextended, -1 confluence (wait for pullback)

Good Entry: M15 RSI = 42 → Early uptrend = +1
Bad Entry: M15 RSI = 72 → Momentum exhausted = -1 (likely reversal)
```

---

## Confluence Scoring System

### BUY Signal (Bullish Confluence)

```
Confluence Calculation:
  Weekly structure:     +1 (price above MA-200)
  Daily momentum:       +1 (price above MA-50)
  H4 RSI:              +1 (RSI 30-70 range)
  H4 MACD:             +1 (MACD > Signal)
  M15 entry timing:    +1 (RSI < 50)
  
  Total: 5/5 indicators aligned
  Signal: BUY (maximum confidence)
  
Minimum Requirement: ≥3 indicators aligned
  3/5 = 60% base confidence + macro adjustment
  4/5 = 70% base confidence + macro adjustment
  5/5 = 80% base confidence + macro adjustment
```

### WAIT Signal (Insufficient Confluence)

```
Confluence Calculation:
  Weekly structure:     +1 (price above MA-200)
  Daily momentum:       -1 (price below MA-50) → CONFLICT
  H4 RSI:              0 (RSI at 72, overbought)
  H4 MACD:             +1 (MACD > Signal)
  M15 entry timing:    -1 (RSI at 68, overextended)
  
  Total: 2/5 indicators aligned (1 positive, 2 negative)
  Signal: WAIT / DO NOT TRADE (insufficient confluence)
  Recommendation: Wait for daily structure to recover above MA-50
```

---

## Multi-timeframe Divergence Detection

### Higher Timeframe Bias vs. Lower Timeframe Signal

```
Scenario A: Weekly Bullish, Daily Bearish
  Weekly: Price > MA-200, RSI > 50 (clear uptrend)
  Daily:  Price < MA-50, RSI < 30 (weak, oversold)
  
  Interpretation:
    Major trend is up (weekly)
    Minor pullback occurring (daily)
    Probability: Bounce/reversal of daily downtrend likely
    
  Action: Wait for daily to recover above MA-50
          Then enter BUY when daily RSI recovers to 40-50 range
          Entry will have strong weekly support below it

Scenario B: Weekly Bearish, Daily Bullish
  Weekly: Price < MA-200, RSI < 50 (downtrend)
  Daily:  Price > MA-50, RSI > 60 (strong momentum)
  
  Interpretation:
    Major trend is down (weekly)
    Minor bounce occurring (daily)
    Probability: Bounce is countertrend, will fail
    
  Action: Avoid BUY entries
          If must trade, only SELL into the bounce
          Use daily bounce as opportunity to short (against weekly bias)
```

---

## Entry Rules (Consolidated)

### Minimum Confluence for Entry

```
Trading Rules:
  1. Weekly structure aligned (price above/below key MA)
  2. Daily structure aligned (price above/below MA-50)
  3. H4 RSI not overbought/oversold (30-70 range)
  4. H4 MACD trending in signal direction
  5. M15 entry not overextended (RSI < 65 for longs)
  
Minimum: 3 of 5 rules met
Preferred: 4+ of 5 rules met
Strong Setup: All 5 rules aligned
```

---

## References

- Murphy, John J., "Technical Analysis of Financial Markets" (1999) — Definitive multi-timeframe methodology
- Elder, Alexander, "Come Into My Trading Room" (2002) — Elder-Ray indicator, multi-timeframe application
- Nison, Steve, "Japanese Candlestick Charting Techniques" (2001)
