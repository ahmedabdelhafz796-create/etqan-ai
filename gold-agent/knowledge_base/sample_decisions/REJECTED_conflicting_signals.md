# REJECTED TRADE DECISION EXAMPLE 2
## Gold BUY Signal Rejected Due to Conflicting Macro + Daily Loss Limit

**Date**: 2026-08-04 09:15 UTC  
**Decision**: WAIT / REJECT BUY Signal  
**Confidence**: 35% (below 50% WAIT threshold)  
**Status**: REJECTED (multiple blocking criteria)

---

## Decision Summary

```
Signal Suggested: BUY XAU/USD
Recommendation: WAIT (DO NOT TRADE)

Rejection Reasons (in priority order):
  1. Daily loss limit already 80% consumed (blocking)
  2. Macro signals conflicting (reducing confidence)
  3. Technical signals weak (insufficient confluence)
  4. FOMC decision imminent (24 hours away)

Confidence: 35% (below 50% WAIT threshold)
```

---

## Macro Analysis (Step 1-5)

### 1. Real Yields Assessment
```
Data:
  10Y Treasury Yield: 4.1%
  CPI (YoY): 3.6%
  Real Yield: 0.5%

Trend:
  One week ago: Real yield was 0.7%
  Rising 20 basis points over 5 trading days
  Direction: RISING (bearish for gold)

KB Reference: gold_macro_drivers.md
  "Rising real yields = headwind for gold"

Score: 45 (BEARISH-NEUTRAL)
Reasoning: Real yields ticking up, reducing gold's appeal
```

### 2. DXY Assessment
```
Data:
  Weekly Price: 101.8
  MA-200 (weekly): 102.1
  MA-50 (weekly): 101.5
  RSI-14 (daily): 62

Trend:
  Price bounced off MA50 and now consolidating
  Structure: Price recovering from weakness
  Direction: STABILIZING/REBOUNDING (mixed signal)

KB Reference: gold_macro_drivers.md
  "DXY stabilizing = mixed for gold"

Score: 50 (NEUTRAL)
Reasoning: DXY has stopped falling, now consolidating
```

### 3. Fed Policy Assessment
```
Data:
  Days to FOMC: 1 day (CRITICAL - decision tomorrow at 18:00 UTC)
  Current Rate: 5.25-5.50%
  CME FedWatch Probabilities:
    - Hold: 70%
    - Hike: 20%
    - Cut: 10%
  Powell Tone: Hawkish (speech 2 days ago emphasized inflation risks)

Direction: POTENTIAL HAWKISH SURPRISE

KB Reference: gold_macro_drivers.md
  "Policy shift can dominate all other factors"

KB Reference: decision_protocols/macro_decision_framework.md
  "Avoid trading within 2 days of FOMC"
  "Currently 1 day away = MANDATORY AVOID"

Score: 25 (VERY BEARISH due to risk)
Reasoning: FOMC decision in <24 hours, rate hike probability 20% (not negligible)
```

### 4. Risk Sentiment (VIX) Assessment
```
Data:
  VIX Current: 12.5
  VIX One week ago: 14.8
  Trend: Declining (risk appetite rising)

Environment: LOW RISK / Very complacent

KB Reference: gold_macro_drivers.md
  "VIX < 15 = headwind for gold"
  "VIX < 12 = extreme risk-on bias"

Score: -20 (STRONG HEADWIND)
Reasoning: Risk-on environment, equities favored, gold under pressure
```

### 5. Macro Regime Classification

```
Score Summary:
  Real Yields: 45 (Rising, bearish-neutral)
  DXY: 50 (Neutral, stabilizing)
  Fed Policy: 25 (CRITICAL - FOMC tomorrow)
  VIX: -20 (Strong headwind)

Factor Count:
  Bullish Factors: 0
  Neutral Factors: 2 (DXY, partly real yields)
  Bearish Factors: 2 (FOMC risk, VIX headwind)

Classification: CONFLICTING / BEARISH

KB Reference: macro_decision_framework.md
  "0 bullish factors, 2 bearish = CONFLICTING regime at best"
  "FOMC within 2 days = MANDATORY AVOID per protocol"

Macro Confidence Adjustment: -30% (not -15%)
Reasoning: FOMC imminent is automatic override, regardless of other factors
```

---

## Technical Analysis (Step 6)

### Daily/Weekly Structure (Risk Framework)
```
Gold Weekly (XAU/USD):
  Price: $2,335
  MA-200 (weekly): $2,310
  MA-50 (weekly): $2,340
  Interpretation: Price below MA50, slightly above MA200
  Status: JUST FELL BELOW SUPPORT (weak)
  Score: -1

Gold Daily (XAU/USD):
  Price: $2,333
  MA-50 (daily): $2,342
  Interpretation: Price below MA50 = downtrend momentum
  Status: BROKEN SUPPORT (negative)
  Score: -1

KB Reference: technical_analysis/multi_timeframe.md
  "Price breaking below MA50 = loss of short-term bullish structure"
```

### H4 Confirmation
```
Gold H4:
  RSI-14: 65 (approaching overbought at 70)
  MACD: Histogram positive but weakening (signal line not far below)
  MA-50 (H4): $2,341 (price at $2,333, below it)
  Interpretation: Momentum fading, RSI approaching overbought territory
  Status: WEAKENING (not bullish)
  Score: 0 (mixed, not supportive)

KB Reference: technical_analysis/multi_timeframe.md
  "RSI >65 = approaching overbought, caution"
  "MACD histogram weakening = momentum fading"
```

### Entry Timing (M15/M5)
```
Gold M15:
  RSI-14: 68 (overbought zone, approaching 70)
  Price: Below H4 MA-50, facing resistance
  Interpretation: Momentum is extremely overextended at short-term timeframe
  Status: ENTRY RISK IS EXCESSIVE (likely reversal)
  Score: -2 (strong negative)

Confluence Count: 1/5 indicators aligned (only MACD slightly positive)

KB Reference: multi_timeframe.md
  "M15 RSI > 65 = entry risk high, wait for pullback"
  "1/5 = INSUFFICIENT confluence, WAIT signal"
```

### Technical Signal
```
Indicators Aligned: 1/5 (BELOW threshold of ≥3)
Signal: WAIT (REJECTED)

Reasoning:
  ✗ Weekly structure weak (price below MA50 support)
  ✗ Daily momentum broken (below MA50)
  ✗ H4 momentum fading (histogram weakening)
  ✗ M15 severely overbought (RSI at 68)
  ? MACD still positive (only supportive indicator)

Final: Only 1/5 indicators = INSUFFICIENT confluence

KB Reference: macro_decision_framework.md
  "<3 indicators = WAIT signal, do not trade"
```

---

## Capital Preservation Check (BLOCKING FACTOR)

### Daily Loss Limit
```
Equity at Start of Day: $10,000
Current Time: 09:15 UTC
Daily Loss So Far:

Trade 1 (07:30 UTC): Loss -$400 (gold SELL position stopped out)
Trade 2 (08:45 UTC): Loss -$100 (missed stop, partial execution)
Total Daily Loss: -$500
Daily Loss Percentage: 5.0% of $10,000 equity

Daily Limit: 5.0% (per config)
Current Status: AT THE LIMIT

New Trade Scenario:
If this BUY position's SL at $2,320 is hit:
  Max Loss: $200 (20 units × $10)
  Total Daily Loss Would Be: $500 + $200 = $700 (7.0% of equity)

Status: EXCEEDS DAILY LIMIT

KB Reference: capital_preservation.py
  "Once daily loss reaches 5%, halt all new trades"
  "Current daily loss = 5.0%, new trade would breach 7%"

Action: BLOCK THIS TRADE (daily limit active)
```

### Drawdown Circuit Breaker
```
Peak Equity: $10,000
Current Equity: $9,500 (after today's losses)
Drawdown: 5.0%
Limit: 15.0%

Status: OK (5% < 15% limit)
Note: Breaker not triggered, but we're early in session and losing
Caution: If two more -$300 losses, would trigger emergency stop

KB Reference: capital_preservation.py
  "Drawdown limit 15%, currently 5%"
```

---

## Final Decision Integration (Step 7)

### Calculation

```
Technical Signal: WAIT (1/5 confluence, insufficient)
Technical Confidence: 35% (well below WAIT threshold)

Macro Regime: CONFLICTING/BEARISH (FOMC imminent is override)
Macro Adjustment: -30% (FOMC override, MANDATORY AVOID)

Capital Preservation Check: BLOCKED (daily loss limit at 5%)

Final Decision: WAIT / REJECT

Reasoning Chain:
  1. FOMC decision in 24 hours (immediate override)
  2. Daily loss limit already 5% (cannot add more risk)
  3. Technical confluence insufficient (1/5)
  4. Macro conflicting (bearish signals outweigh neutral)
  5. VIX headwind active
  
No Path to Approval: Recommendation fails at 3 independent levels
```

### Multiple Rejection Criteria

```
BLOCKING CRITERIA (any one alone would reject):
  ✗ 1. FOMC within 2 days (protocol violation)
  ✗ 2. Daily loss limit breached (capital rule)
  ✗ 3. Technical confluence <3 (signal rule)
  ✗ 4. Macro conflicting + bearish (regime rule)

All four rejection criteria are active simultaneously.
This is a STRONG REJECT, not borderline.
```

---

## KB References (Complete)

1. **Macro Analysis**:
   - gold_macro_drivers.md (real yields rising, VIX headwind)
   - macro_decision_framework.md (FOMC protocol override)
   - Federal Reserve FRED (real yield data)
   - CME FedWatch (FOMC probability)

2. **Technical Analysis**:
   - technical_analysis/multi_timeframe.md (confluence <3 = WAIT)
   - technical_analysis/rsi_theory.md (RSI >68 = overbought)
   - technical_analysis/macd_theory.md (histogram weakening)

3. **Capital Preservation**:
   - capital_preservation.py (daily loss limit 5%)
   - decision_protocols/risk_protocol.md (daily halts)

4. **Decision Protocol**:
   - macro_decision_framework.md (FOMC avoidance)
   - decision_protocols/event_protocol.md ("avoid 1hr before/after events")

5. **Experts/Standards**:
   - John Murphy: Technical analysis confluence rules
   - Van Tharp: Position sizing (not relevant here as trade rejected)
   - Van Tharp: Capital preservation philosophy

---

## Why This Rejection is Correct

### If We Ignored the FOMC Rule...
"But macro is only slightly negative, technical could work out..."

**Problem**: FOMC decision tomorrow could move gold 2-3% in either direction.
Even if we're right on entry (unlikely given 1/5 confluence), FOMC surprise could wipe out.
*Source: macro_decision_framework.md - FOMC events cause 2-5% moves*

### If We Ignored the Daily Loss Limit...
"But we've learned from today's losses, this trade is different..."

**Problem**: Emotions after losses lead to over-trading and revenge trading.
Capital preservation rules protect against this psychological trap.
*Source: van_tharp_method.md - mechanical rules remove emotional bias*

### If We Ignored the Technical Confluence...
"But the macro setup is so good, technical will catch up..."

**Problem**: Macro takes time to play out. Short-term technical structure is bearish.
Trading against technical setup = fighting market short-term momentum.
*Source: technical_analysis/multi_timeframe.md - confluence = higher probability*

### Confidence Calculation
```
Base Technical: 35% (from 1/5 confluence)
Macro Adjustment: -30% (from FOMC override)
Capital Adjustment: -20% (from daily loss limit)
Final: 35% - 30% - 20% = -15%

Clamped to 0% (confidence cannot go negative)
Reported: WAIT (do not trade)
```

---

## Recommended Action

### Immediate (Today)
```
1. Stop trading until daily reset at UTC 00:00 (9 hours from now)
2. Analyze why today started with -$500 loss (review morning trades)
3. Wait for FOMC decision tomorrow (18:00 UTC)
4. After FOMC clarity, reassess macro regime
```

### After FOMC (Tomorrow)
```
1. If FOMC Hikes: Gold likely down, reassess all bullish signals
2. If FOMC Holds: Back to neutral, macro conflicting signals remain
3. If FOMC Cuts: Positive surprise, gold could rally (new entry opportunity)
4. Regardless: Wait for technical structure to recover (price back above MA50)
```

### Next Valid Entry Opportunity
```
Requirements for ACCEPT:
  1. Daily loss counter reset (new UTC day)
  2. FOMC decision announced and market digested (36+ hours from now)
  3. Technical confluence ≥3/5 (currently 1/5, need price to recover or indicators reset)
  4. Macro regime BULLISH_ALIGNED (currently conflicting/bearish)
  
Earliest: 2026-08-05 14:00 UTC (after FOMC digestion)
```

---

## Trade Outcome (If We Had Ignored Rules)

*Hypothetical: "What if we took this trade anyway?"*

Scenario A (FOMC Hikes):
- Position opened at $2,333
- FOMC surprise hike announcement → gold drops 2% → $2,286
- Stop loss at $2,320 likely triggered with slippage
- Realized Loss: -$300 to -$400
- Daily Loss Total: $800 (would exceed 5% limit, violate capital rule)

Scenario B (FOMC Cuts):
- Position opened at $2,333
- FOMC surprise cut → gold rallies 2% → $2,381
- Take profit at $2,370 might get partial fill
- Realized Win: +$200 to +$300
- BUT: Position taken in highest VIX headwind with no confluence
- Right trade for wrong reasons (luck, not skill)

**Lesson**: Rejection protecting capital is the correct choice, even if scenario B was possible.

---

## Next Steps

1. Monitor FOMC decision tomorrow (18:00 UTC)
2. Post-FOMC analysis (markets need 1-2 hours to digest)
3. Reassess macro signals at 20:00 UTC tomorrow
4. If technical setup improves after FOMC clarity, new entry opportunity
5. Record this decision rejection in audit database for learning
