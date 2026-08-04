# RSI (Relative Strength Index) — Theory and Application

## Executive Summary

The Relative Strength Index (RSI) measures momentum on a scale of 0-100. Developed by J. Welles Wilder Jr. in 1978, RSI identifies overbought (>70) and oversold (<30) conditions, helping traders identify potential reversals.

**Application in This System**: RSI is one of 5 confluence indicators. Combined with MACD, moving averages, and multi-timeframe analysis, RSI helps confirm trading signals.

---

## RSI Formula

```
RSI = 100 - (100 / (1 + RS))

Where:
  RS = Average Gain over N periods / Average Loss over N periods
  N = Typically 14 (RSI-14)

Calculation Steps:
  1. Calculate gains and losses for each period
  2. Average gains and losses over N periods
  3. Calculate RS (ratio)
  4. Convert to 0-100 scale
  
Result: RSI ranges 0-100
        RSI = 50: Neutral (equal ups/downs)
        RSI > 50: More ups than downs (bullish momentum)
        RSI < 50: More downs than ups (bearish momentum)
```

---

## RSI Zones and Interpretations

| RSI Level | Interpretation | Trading Signal |
|---|---|---|
| < 30 | Oversold (extreme low) | Potential reversal up / BUY setup |
| 30-50 | Declining momentum | Bearish bias / WAIT for reversal |
| 50-70 | Rising momentum | Bullish bias / BUY confirmation |
| > 70 | Overbought (extreme high) | Potential reversal down / SELL setup |

---

## Application: Multi-timeframe RSI Analysis

### Weekly RSI (Trend Confirmation)

```
Gold Weekly RSI-14:
  > 70: Overextended rally (caution, pullback risk)
  50-70: Healthy uptrend
  30-50: Weak uptrend or consolidation
  < 30: Oversold (potential bottom forming)

Trading Use:
  Weekly RSI > 70: Don't chase, wait for pullback
  Weekly RSI < 30: Accumulation opportunity
```

### Daily RSI (Entry Timing)

```
Gold Daily RSI-14:
  > 70: Daily overbought (entry risk if weekly bullish)
  50-70: Daily bullish momentum
  30-50: Daily range-bound or consolidating
  < 30: Daily oversold (potential bounce)

Trading Use:
  Daily RSI 30-50 with weekly RSI > 50: WAIT for recovery
  Daily RSI > 70 with weekly RSI > 50: ENTER on confirmation (not overbought yet)
```

### H4 RSI (Confluence Check)

```
Gold H4 RSI-14:
  Purpose: Verify H4 momentum aligns with daily trend
  
  Bullish Alignment:
    Weekly RSI > 50 + Daily RSI > 50 + H4 RSI > 50 = 3/5 confluence
    
  Bearish Misalignment:
    Weekly RSI > 50 + Daily RSI > 50 + H4 RSI < 50 = Conflict
    → Suggests H4 pullback incoming
    → Wait for H4 to reverse before entry
```

---

## RSI Divergence (Advanced)

### Bullish Divergence (Reversal Signal)

```
Setup:
  Price makes new LOW
  RSI makes HIGHER LOW
  
Interpretation:
  Price selling off, but momentum weakening
  Suggests reversal up likely
  
Example (Gold):
  Price: $2,040 (new low)
  RSI-14: 28 (but previous low was 22)
  Signal: BULLISH DIVERGENCE → Expect bounce
  
Source: Wilder's RSI, "New Concepts in Technical Trading Systems" (1978)
```

### Bearish Divergence (Reversal Signal)

```
Setup:
  Price makes new HIGH
  RSI makes LOWER HIGH
  
Interpretation:
  Price rallying, but momentum weakening
  Suggests reversal down likely
  
Example (Gold):
  Price: $2,380 (new high)
  RSI-14: 72 (but previous high was 78)
  Signal: BEARISH DIVERGENCE → Expect pullback
```

---

## References

- Wilder, J. Welles Jr., "New Concepts in Technical Trading Systems" (1978) — Original RSI paper
- Wilder, J. Welles Jr., "The Adam Theory of Markets" (1989)
- Murphy, John J., "Technical Analysis of Financial Markets" (1999)
