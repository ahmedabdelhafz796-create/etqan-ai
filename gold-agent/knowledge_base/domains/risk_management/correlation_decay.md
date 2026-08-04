# Correlation Decay — Detecting Broken Relationships

## Executive Summary

Historical correlations between gold and macro drivers (real yields, DXY, VIX) can break down during market regime changes, crises, or shifts in institutional flows. Detecting correlation decay is critical for identifying when macro models need revision.

**Monitoring Rule**: When historical correlation shifts >0.30 from baseline, flag as potential regime shift and reduce confidence in macro signals.

---

## Normal Gold Correlations (Baseline)

### Gold vs. Real Yields

```
Historical Correlation: -0.75 to -0.85
Confidence Interval: 95%

Interpretation:
  - Strong inverse relationship
  - Rising real yields → Gold falls
  - Falling real yields → Gold rises
  - This relationship holds >95% of the time

When Baseline: Use real yields as primary macro driver
When Breaks: Something structural has changed (rare)
```

### Gold vs. DXY (US Dollar Index)

```
Historical Correlation: -0.65 to -0.70
Confidence Interval: 95%

Interpretation:
  - Persistent negative relationship
  - Strong dollar → Gold falls
  - Weak dollar → Gold rises
  - Less strong than real yields, but consistent

When Baseline: Use DXY trend for secondary confirmation
When Breaks: KB should note breakdown reason
```

### Gold vs. VIX (Risk Sentiment)

```
Historical Correlation: +0.55 to +0.65
Confidence Interval: 90%

Interpretation:
  - Positive relationship (both respond to risk-off)
  - Rising VIX → Gold typically rises
  - Falling VIX → Gold typically falls
  - Weaker than real yields or DXY correlations

When Baseline: Use VIX as tertiary confirmation
When Breaks: Institutional flows may be overwhelmed
```

---

## Detecting Correlation Decay

### Calculation Method

```python
def calculate_rolling_correlation(asset1_returns: list, 
                                   asset2_returns: list, 
                                   window: int = 30):
    """
    Calculate rolling correlation (e.g., 30-day window).
    
    Steps:
      1. Calculate daily returns for both assets
      2. For each day, correlate last 30 days of returns
      3. Track correlation over time
      4. Identify shifts from baseline
    """
    correlations = []
    for i in range(window, len(asset1_returns)):
        subset1 = asset1_returns[i-window:i]
        subset2 = asset2_returns[i-window:i]
        corr = pearson_correlation(subset1, subset2)
        correlations.append(corr)
    
    return correlations

# Example:
# Baseline gold/real-yield correlation: -0.75
# Current 30-day correlation: -0.35
# Shift: -0.35 - (-0.75) = +0.40 (MASSIVE DECAY)
# Action: FLAG AS REGIME SHIFT, reduce macro confidence
```

### Alert Thresholds

```
Monitoring Alert:
  
  If |Correlation_Current - Correlation_Baseline| > 0.30:
    → Alert: "CORRELATION DECAY DETECTED"
    → Reason: Historical relationship broken
    → Action: Reduce confidence, investigate cause
  
  Example Gold/Real Yields:
    Baseline: -0.75
    Current: -0.45
    Decay: |-0.45 - (-0.75)| = 0.30 → ALERT TRIGGERED
```

---

## Causes of Correlation Decay

### Cause 1: Geopolitical Crisis (Safe-Haven Flows)

```
Example: 2020 COVID Crash
  Normal: Gold + Real Yields correlation = -0.75
  During Crisis: Gold + Real Yields correlation = +0.30
  
Reason:
  Both gold and bonds rally as flight-to-safety (dual safe-havens)
  Breaks normal inverse relationship
  
Duration: 2-4 weeks typically
Severity: Extreme (0.30+ shift)

Trading Implication:
  → Ignore real yields during crisis
  → Focus on technical signals only
  → Expect volatility even with macro support
```

### Cause 2: Central Bank Gold Buying Surge

```
Example: 2024-2025 CB buying accelerated
  Normal: DXY/Gold correlation = -0.70
  With CB buying: DXY/Gold correlation = -0.40
  
Reason:
  Institutional demand (CB buying) overwhelms currency effect
  Gold rises despite strong dollar
  
Duration: Weeks to months
Severity: Moderate (0.30+ shift)

Trading Implication:
  → DXY weakness still bullish, but strength no longer bearish
  → Gold supported regardless of DXY direction
  → Look for other drivers (CB buying flows, geopolitics)
```

### Cause 3: Fed Policy Regime Shift

```
Example: 2022 Pivot to Aggressive Hiking
  Normal: Rate cut expectations support gold
  During Pivot: Real yields spike faster than expected
             Gold correlation breaks
  
Reason:
  Market repricing is so rapid that normal lag disappears
  Real yields jump 200+ basis points
  Gold can't keep up with negative correlation
  
Duration: Days to weeks
Severity: Extreme initially (2+ shift), normalizes quickly

Trading Implication:
  → Macro signals temporarily unreliable
  → Position sizes should be reduced
  → Wait for market to digest before resume normal trading
```

### Cause 4: Inflation Surprise (Dual Response)

```
Example: CPI prints hot unexpectedly
  Normal: CPI up → Real yields up → Gold down (normal correlation)
  Surprise Case: CPI up AND DXY falls (competing effects)
  
Reason:
  Market expects Fed rate cuts sooner than expected
  Real yields actually fall (lower expected rates, higher CPI)
  DXY falls (dovish pivot)
  Gold rallies (dual benefit)
  
Duration: Hours to days (single event)
Severity: Temporary (event-driven)

Trading Implication:
  → Prepare for volatility around CPI releases
  → After CPI, correlation should normalize
  → Don't trade 1 hour before/after events
```

---

## Response Protocol When Correlation Decays

### Step 1: Identify the Decay

```
Check Weekly:
  1. Calculate 30-day rolling correlation (gold vs. real yields, DXY, VIX)
  2. Compare to baseline (-0.75, -0.70, +0.60)
  3. If any shift > 0.30, flag as "Correlation Decay Alert"
  
Log Example:
  Date: Aug 3, 2026
  Gold/Real Yields: -0.45 (baseline -0.75) → Decay -0.30 ✓ ALERT
  Gold/DXY: -0.68 (baseline -0.68) → Decay 0.00 ✓ NORMAL
  Gold/VIX: +0.58 (baseline +0.60) → Decay -0.02 ✓ NORMAL
```

### Step 2: Investigate Cause

```
Questions:
  1. Recent geopolitical events? (check news)
  2. Recent CB gold flows? (check World Gold Council report)
  3. Fed policy announcement? (check FOMC communications)
  4. Inflation surprise? (check CPI release)
  5. VIX spike? (check volatility index)

Once Cause Identified:
  → Document in KB
  → Estimate duration of decay
  → Plan when to resume normal correlation trading
```

### Step 3: Adjust Trading Protocol

```
Temporary Adjustments (During Correlation Decay):

1. Reduce Macro Confidence Adjustments
   Normal: +15% for bullish real yields, -15% for bearish
   During Decay: +5% for bullish, -5% for bearish
   Reason: Correlation broken, macro signal less reliable

2. Require Stronger Technical Confluence
   Normal: ≥3/5 indicators aligned = BUY signal
   During Decay: Require ≥4/5 indicators
   Reason: Technical signals more reliable than macro

3. Reduce Position Sizes
   Normal: 1% risk per trade
   During Decay: 0.5% risk per trade
   Reason: Volatility and directional uncertainty higher

4. Increase Hold-Time Monitoring
   Normal: 24-hour max hold
   During Decay: 4-hour max hold
   Reason: Overnight gaps more likely, close positions earlier
```

### Step 4: Resume Normal Trading

```
When to Restore Normal Protocol:

Criteria:
  1. Correlation has returned to within 0.15 of baseline
     (e.g., -0.75 ± 0.15 = range -0.90 to -0.60)
  2. The cause of decay has resolved
     (e.g., geopolitical crisis passed, CB buying normalized)
  3. Market behavior reverts to historical patterns
     (e.g., 10+ days at normalized correlation)

Example:
  Decay identified: Aug 1 (correlation -0.45)
  Cause: COVID-like crisis (geopolitical)
  Recovery: Aug 15 (correlation -0.72, back to baseline)
  Duration: 14 days
  
  Action: Aug 15, resume normal macro adjustments
          Increase position sizes back to 1%
          Revert to ≥3/5 confluence requirement
```

---

## References

- World Gold Council, "Gold Demand Trends" (quarterly correlations)
- Gundlach, Jeffrey, "Secular Outlook" (DoubleLine Capital)
- Markowitz, Harry, "Portfolio Selection," Journal of Finance (1952) — Correlation theory
- Taleb, Nassim, "The Black Swan" (2007) — Extreme events and correlation breakdown
