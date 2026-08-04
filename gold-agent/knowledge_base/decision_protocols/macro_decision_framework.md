# Macro Decision Framework — How to Use the Knowledge Base

## Purpose
This document shows HOW the knowledge base is actually used in real trading decisions. Every decision cites sources and follows a structured reasoning chain.

---

## Step 1: Real Yields Assessment

### Input Data
- Get 10Y Treasury Yield from Federal Reserve FRED
- Get CPI from BLS (latest monthly release)
- Calculate Real Yield = Nominal - Inflation

### Assessment

```python
real_yield = 10y_treasury_yield - cpi_yoy

if real_yield < 0:
    yield_score = 85  # Very bullish
    reasoning = "Negative real yields = capital loses in bonds (KB: gold_macro_drivers.md)"
elif 0 <= real_yield < 1:
    yield_score = 65  # Bullish
    reasoning = "Weak positive yields = gold supported (KB: gold_macro_drivers.md)"
elif 1 <= real_yield < 2:
    yield_score = 40  # Neutral/Bearish
    reasoning = "Moderate yields = bonds competitive (KB: gold_macro_drivers.md)"
else:
    yield_score = 20  # Very bearish
    reasoning = "Strong positive yields = bonds very attractive (KB: gold_macro_drivers.md)"

# Also check trend
if current_real_yield < prev_week_real_yield:
    yield_score += 10  # Rising trend adds bullish bias
```

### Example Entry
```
Timestamp: 2026-08-03 14:00 UTC
10Y Treasury Yield: 4.2%
CPI (YoY): 3.5%
Real Yield: 0.7%

Assessment:
  Level: WEAK POSITIVE (0.7%)
  Trend: Falling (was 1.1% one week ago)
  Score: 65 + 10 = 75 (BULLISH)
  
Reasoning: Real yields falling = tailwind for gold
KB References:
  - gold_macro_drivers.md: "Real Yield < 1% = Bullish"
  - gold_macro_drivers.md: "Trend falling = tailwind"
```

---

## Step 2: DXY Assessment

### Input Data
- Get daily/weekly DXY prices
- Calculate MA-50 and MA-200
- Calculate RSI-14

### Assessment

```python
dxy_weekly_price = get_dxy_close('weekly')
dxy_ma200 = get_moving_average(dxy, 200, 'weekly')
dxy_ma50 = get_moving_average(dxy, 50, 'weekly')
dxy_rsi14 = calculate_rsi(dxy, 14, 'daily')

if dxy_weekly_price < dxy_ma50 < dxy_ma200:
    dxy_score = 75  # Clear downtrend (bullish for gold)
    reason = "Weekly price < MA50 < MA200 = downtrend"
elif dxy_ma50 < dxy_ma200 and dxy_weekly_price > dxy_ma50:
    dxy_score = 60  # Downtrend but testing resistance
    reason = "Price above MA50 but structure bearish"
elif dxy_weekly_price > dxy_ma200:
    dxy_score = 30  # Uptrend (bearish for gold)
    reason = "Weekly price > MA200 = uptrend"
else:
    dxy_score = 50  # Consolidation
    reason = "DXY consolidating, no clear trend"

# RSI divergence check
if dxy_rsi14 > 70:
    dxy_score -= 10  # Overbought, potential reversal
    
return dxy_score, reason
```

### Example Entry
```
Timestamp: 2026-08-03 14:00 UTC
DXY Weekly Price: 101.2
DXY MA-50 (weekly): 101.5
DXY MA-200 (weekly): 102.1
DXY RSI-14 (daily): 58

Assessment:
  Price < MA50: YES (101.2 < 101.5)
  Structure: DOWNTREND (price below both MAs)
  Score: 75 (BULLISH for gold)
  
Reasoning: DXY in clear downtrend = tailwind for gold
KB References:
  - gold_macro_drivers.md: "DXY downtrend = tailwind"
  - technical_analysis/multi_timeframe.md: "Price < MA50 < MA200 = downtrend confirmed"
```

---

## Step 3: Fed Policy Assessment

### Input Data
- Days until next FOMC meeting
- Current Fed Funds Target Rate
- Market expectations (CME FedWatch)
- Latest Powell communications

### Assessment

```python
days_to_fomc = calculate_days_until_next_fomc()
if days_to_fomc < 2:
    policy_score = "AVOID"  # Too risky, next policy decision imminent
    return policy_score, "FOMC within 2 days, avoid positions"

# Probability of rate move
fed_prob_hike = get_cme_fedwatch_probability('hike')
fed_prob_cut = get_cme_fedwatch_probability('cut')
fed_prob_hold = get_cme_fedwatch_probability('hold')

if fed_prob_hike > 60:
    policy_score = 25  # Bearish (market expects hikes)
    reason = f"Market pricing {fed_prob_hike}% probability of rate hike"
elif fed_prob_cut > 60:
    policy_score = 75  # Bullish (market expects cuts)
    reason = f"Market pricing {fed_prob_cut}% probability of rate cut"
else:
    policy_score = 50  # Neutral hold expected
    reason = "Market expects Fed to hold, no clear bias"
    
return policy_score, reason
```

### Example Entry
```
Timestamp: 2026-08-03 14:00 UTC
Next FOMC: August 15 (12 days away)
Fed Funds Rate: 5.25-5.50%
CME FedWatch Probabilities:
  - Hike: 15%
  - Hold: 75%
  - Cut: 10%
Current Powell Tone: "Neutral" (inflation still above target)

Assessment:
  Next Meeting: >2 days (safe to trade)
  Market Expectation: HOLD (75% probability)
  Score: 50 (NEUTRAL)
  
Reasoning: Market expects Fed to hold steady
KB References:
  - gold_macro_drivers.md: "Policy neutral = no directional bias"
  - decision_protocols: "Avoid FOMC within 2 days"
```

---

## Step 4: Risk Sentiment (VIX) Assessment

### Input Data
- Current VIX level
- VIX trend (rising/falling)

### Assessment

```python
vix_current = get_vix_close()

if vix_current < 15:
    risk_score = -15  # Risk-on, headwind for gold
    reason = "VIX low = complacency, equities favored"
elif 15 <= vix_current < 20:
    risk_score = 0  # Neutral
    reason = "Normal risk environment"
elif 20 <= vix_current < 30:
    risk_score = +10  # Risk-off tailwind
    reason = "Elevated risk = flight to safety = gold support"
else:  # >30
    risk_score = +20  # Crisis mode
    reason = "High VIX = crisis, extreme risk-off bias"
    
return risk_score, reason
```

### Example Entry
```
Timestamp: 2026-08-03 14:00 UTC
VIX Current: 14.8
VIX Trend: Stable (was 14.5 one week ago)

Assessment:
  Level: LOW (<15)
  Trend: Stable
  Score: -15 (HEADWIND for gold)
  
Reasoning: Risk-on environment favors equities over gold
KB References:
  - gold_macro_drivers.md: "VIX < 15 = slight headwind"
```

---

## Step 5: Combine Macro Regime

### Regime Classification Algorithm

```python
def classify_macro_regime(real_yield_score, dxy_score, policy_score, vix_score):
    """
    Classify into one of three regimes based on factor alignment.
    """
    
    # Count how many factors point to each direction
    bullish_factors = 0
    bearish_factors = 0
    
    for score in [real_yield_score, dxy_score, policy_score, vix_score]:
        if score > 60:
            bullish_factors += 1
        elif score < 40:
            bearish_factors += 1
    
    if bullish_factors >= 3:
        regime = "BULLISH_ALIGNED"
        confidence_adj = +20  # Add 20% to technical signals
        reasoning = "Macro aligned bullish (3+ factors)"
    elif bearish_factors >= 3:
        regime = "BEARISH_ALIGNED"
        confidence_adj = +20  # Strong bearish technical only
        reasoning = "Macro aligned bearish (3+ factors)"
    else:
        regime = "CONFLICTING"
        confidence_adj = -15  # Reduce confidence, need stronger technical
        reasoning = "Macro signals conflicting, require strong technical"
    
    return regime, confidence_adj, reasoning
```

### Example Entry
```
Macro Scores Summary:
  Real Yields: 75 (Bullish)
  DXY: 75 (Bullish)
  Fed Policy: 50 (Neutral)
  VIX: -15 (Headwind)

Regime Classification:
  Bullish Factors: 2 (real yields, DXY)
  Bearish Factors: 1 (VIX headwind)
  Neutral Factors: 1 (policy)
  
Classification: MIXED (2 bullish, but not 3+)
Regime: CONFLICTING
Confidence Adjustment: -15%

Reasoning: Real yields and DXY bullish, but VIX headwind and policy neutral
means market is not fully aligned. Require stronger technical confirmation.
KB References:
  - macro_decision_framework.md: "CONFLICTING regime = reduce confidence 15%"
```

---

## Step 6: Technical Confluence Check

(Reference from `../technical_analysis/multi_timeframe.md`)

### Input Data
- Daily/Weekly structure (MA-200, MA-50)
- H4 confirmation (RSI, MACD)
- M15/M5 entry timing

### Assessment

```python
confluence_count = 0

# Weekly structure
if gold_weekly_price > gold_weekly_ma200:
    confluence_count += 1
    
# Daily support
if gold_daily_price > gold_daily_ma50:
    confluence_count += 1
    
# H4 RSI not overbought
if 30 < gold_h4_rsi < 70:
    confluence_count += 1
    
# H4 MACD positive
if gold_h4_macd_histogram > 0:
    confluence_count += 1
    
# M15 entry timing
if gold_m15_rsi < 50:  # Not overextended
    confluence_count += 1

if confluence_count >= 3:
    tech_signal = "BUY"
    tech_confidence = 60 + (confluence_count * 5)  # Base 60% + bonus
else:
    tech_signal = "WAIT"
    tech_confidence = 40
    
return tech_signal, tech_confidence, confluence_count
```

---

## Step 7: Final Decision Integration

### Algorithm

```python
def final_decision():
    # Get macro regime
    macro_regime, macro_adj, macro_reason = classify_macro_regime(...)
    
    # Get technical signal
    tech_signal, tech_base_conf, confluence = get_technical_signal()
    
    # Combine
    if tech_signal == "WAIT":
        return {
            "action": "WAIT",
            "confidence": 0,
            "reason": f"Technical: Insufficient confluence ({confluence}/5 indicators)",
            "kb_refs": ["technical_analysis/multi_timeframe.md: ≥3 required"]
        }
    
    # Calculate final confidence
    final_confidence = tech_base_conf + macro_adj
    final_confidence = max(0, min(100, final_confidence))  # Clamp 0-100
    
    return {
        "action": tech_signal,
        "confidence": final_confidence,
        "macro_regime": macro_regime,
        "reasoning_chain": [
            f"Macro Regime: {macro_regime} ({macro_reason})",
            f"Technical Signal: {tech_signal} ({confluence}/5 confluence)",
            f"Base Confidence: {tech_base_conf}%",
            f"Macro Adjustment: {macro_adj:+.0f}%",
            f"Final Confidence: {final_confidence}%"
        ],
        "kb_references": [
            "gold_macro_drivers.md",
            "technical_analysis/multi_timeframe.md",
            "decision_protocols/macro_decision_framework.md",
        ]
    }
```

---

## Full Example: ACCEPTED TRADE DECISION

See `../sample_decisions/ACCEPTED_bullish_alignment.md`

---

## Full Example: REJECTED TRADE DECISION

See `../sample_decisions/REJECTED_conflicting_signals.md`

---

## References

- Van Tharp, "Trade Your Way to Financial Freedom" (2007)
- John Murphy, "Technical Analysis of Financial Markets" (1999)
- Federal Reserve FRED: https://fred.stlouisfed.org/
- CME FedWatch: https://www.cmegroup.com/markets/money-markets/fed-funds.html
- World Gold Council: https://www.gold.org/
