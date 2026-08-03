# Macroeconomic Drivers of Gold Prices

## Executive Summary

Five macro factors drive gold prices. Understanding them in order of importance:

1. **US Real Yields** (strongest, -0.80 to -0.90 correlation)
2. **US Dollar Index / DXY** (persistent, -0.60 to -0.70 correlation)
3. **Fed Policy & Rate Expectations** (directional)
4. **Risk Sentiment (VIX)** (inverse, elevated VIX = risk-off = gold up)
5. **Central Bank Buying** (long-term institutional demand)

---

## 1. US Real Yields (STRONGEST DRIVER)

### Definition
Real Yield = Nominal 10Y Treasury Yield - Inflation (CPI)

### Example Calculation
```
10Y Treasury Yield: 4.2%
CPI Inflation (YoY): 3.5%
Real Yield: 4.2% - 3.5% = 0.7%
```

### Impact on Gold

| Real Yield | Interpretation | Gold Impact |
|---|---|---|
| **Negative** (<0%) | Investors losing purchasing power in bonds | Gold rallies (positive) |
| **Low** (0-1%) | Weak positive real return | Gold supported (neutral-bullish) |
| **Moderate** (1-2%) | Reasonable real return | Gold pressure (bearish) |
| **High** (>2%) | Strong real return in bonds | Gold declines significantly (very bearish) |

### Historical Correlation (Empirical Regularity)
- **2010-2026**: Gold/Real Yield correlation ≈ -0.75 to -0.85
- **Confidence Level**: HIGH (95%+ of variance explained)
- **Causality**: Real yields rising → bonds more attractive → capital rotates from gold
- **Mechanism**: Gold has zero yield; if bonds offer positive real return, bonds win

### Data Sources
- 10Y Treasury Yield: Federal Reserve FRED (daily)
- CPI: Bureau of Labor Statistics (monthly, second week)
- Calculated Real Yield: Research available at Gundlach's DoubleLine reports

### Trading Protocol
```
Real Yield Analysis Framework:

If Real Yield < 0%:
  → BULLISH for gold (+15% confidence boost)
  → Capital preservation in negative real rate environment
  → Rationale: Cash/bonds destroy purchasing power

If Real Yield 0-1%:
  → NEUTRAL (+5% confidence boost if other factors align)
  → Marginal advantage for gold vs. bonds

If Real Yield >1%:
  → BEARISH for gold (-10% confidence hit)
  → Bonds attractive; capital rotates out of gold

Trend Check: Is real yield rising or falling?
  → Rising: Headwind for gold (wait for reversal)
  → Falling: Tailwind for gold (consider buying)
```

---

## 2. US Dollar Index (DXY)

### Definition
DXY = Weighted index of USD vs. 6 major currencies (EUR 57.6%, JPY 13.6%, GBP 11.9%, CAD 9.1%, SEK 4.2%, CHF 3.6%)

### Data Source
- **FRED or Yahoo Finance**: Daily DXY prices
- **Current Range**: 95-105 (recent 10-year range)

### Gold/DXY Relationship (Empirical Regularity)

| Finding | Confidence | Evidence |
|---------|-----------|----------|
| Gold and DXY negatively correlated | HIGH | 2010-2026 correlation ≈ -0.65 to -0.70 |
| Stronger when real yields stable | HIGH | Isolation of DXY effect in regression |
| Breaks during geopolitical crises | MEDIUM | 2020 COVID, 2022 Ukraine (safe-haven flows) |

### Mechanism
1. Gold priced in USD globally
2. Strong USD → Gold cheaper in other currencies → Demand falls
3. Weak USD → Gold cheaper in USD only, demand rises
4. But "cheaper in other currencies" is real economic effect

### Historical Context

**Strong USD Period (2015-2016)**:
- DXY rose from 95 to 103
- Gold fell from $1,300 to $1,050 (-19%)
- Real yields were also rising
- Effect: Compounding headwind

**Weak USD Period (2020-2021)**:
- DXY fell from 103 to 89
- Gold rose from $1,400 to $1,800 (+29%)
- Fed kept rates at zero
- Effect: Compounding tailwind

### Trading Protocol

```
DXY Trend Analysis (Multi-timeframe):

Weekly Trend (Structure):
  - If MA200 > MA50 with price above both: DXY in uptrend (headwind)
  - If MA50 > MA200 with price below both: DXY in downtrend (tailwind)

Momentum Check:
  - Calculate RSI-14 on daily DXY
  - RSI > 70: DXY overbought (potential for reversal = gold bounce)
  - RSI < 30: DXY oversold (potential reversal = gold weakness)

Confluence:
  - DXY + Real Yields both pointing same direction = STRONG signal
  - DXY one direction, Real Yields opposite = MIXED (reduce confidence 10%)
```

---

## 3. Federal Reserve Policy & Rate Expectations

### Direct Factors
- **Fed Funds Rate**: Current overnight rate (0-5.5% range since 2023)
- **Fed Guidance**: Forward rate expectations (dots plot)
- **Quantitative Easing/Tightening**: Balance sheet decisions

### Indirect Factors
- **Market Expectations**: CME FedWatch shows probability of rate moves
- **Inflation Data Sensitivity**: Upcoming CPI can trigger rate shifts
- **Employment Data**: Jobs report (first Friday of month) drives policy expectations

### Gold Impact

| Fed Action | Gold Impact | Reasoning |
|---|---|---|
| **Rate Hike** | BEARISH (short-term) | Higher discount rates reduce gold value |
| **Rate Cut** | BULLISH (short-term) | Lower rates increase real yield demand |
| **"Hawkish" Guidance** | BEARISH | Market prices in future rate hikes → real yields rise |
| **"Dovish" Guidance** | BULLISH | Market expects rate cuts → real yields fall |
| **QE (Expansion)** | BULLISH | Increases money supply → inflation expectations rise |
| **QT (Contraction)** | BEARISH | Reduces money supply → deflationary pressure |

### Data Sources
- **FOMC Decisions**: Federal Reserve official announcements (8x/year)
- **Fed Communications**: Powell speeches, minutes (released 3 weeks after meetings)
- **CME FedWatch**: https://www.cmegroup.com/markets/money-markets/fed-funds.html (daily probability updates)
- **Dot Plot**: Federal Reserve Summary of Economic Projections (quarterly)

### Trading Protocol

```
Fed Policy Analysis:

Step 1: Is Fed in Hiking, Neutral, or Cutting Cycle?
  - Hiking: Headwind for gold (avoid long positions)
  - Neutral: Mixed signals (wait for clarity)
  - Cutting: Tailwind for gold (consider long positions)

Step 2: Next FOMC Meeting Date
  - Avoid trading 1 hour before FOMC announcement
  - Avoid trading 1 hour after FOMC announcement
  - Volatility spikes on surprise hawkish/dovish pivots

Step 3: Market Pricing Check
  - Look at CME FedWatch probability of next rate move
  - If market already priced in expected move, less impact
  - If market surprised, stronger gold move expected

Confidence Adjustment:
  - Fed cycle aligned with other factors: +10-15% confidence
  - Fed policy conflicting with technical setup: -20% confidence
```

---

## 4. Risk Sentiment (VIX Index)

### Definition
VIX = 30-day implied volatility of S&P 500 index options (CBOE official)

### Levels (Empirical Classification)

| VIX Level | Risk Environment | Gold Bias |
|---|---|---|
| <15 | Low Risk (Complacency) | Slight headwind (risk-on favors equities) |
| 15-20 | Normal Risk | Neutral |
| 20-30 | Elevated Risk | Bullish (risk-off favors gold) |
| >30 | High Risk (Crisis) | Very bullish (flight to safety) |

### Gold/VIX Relationship (Empirical Regularity)
- **Correlation**: Typically +0.50 to +0.65 (positive correlation)
- **Mechanism**: VIX spikes = stock market stressed = investors buy gold hedge
- **Caveat**: Relationship decays during geopolitical crises (correlation can break)

### Data Sources
- **CBOE VIX**: https://www.cboe.com/vix/ (real-time)
- **VIX Levels**: Available on Yahoo Finance, Bloomberg, FRED

### Historical Examples

**2020 COVID Crash**:
- VIX spiked to 82 (highest since 2008)
- Gold rallied 25% in 3 months
- Strong positive correlation

**2022 Fed Tightening**:
- VIX elevated (20-25 range) for most of year
- Gold fell 5-10% despite elevated VIX
- Real yields rising overwhelmed VIX bullishness
- Shows: Real yields can dominate risk sentiment

### Trading Protocol

```
Risk Sentiment Check (Part of Decision):

If VIX < 15:
  → Risk-on environment (bullish equities, neutral-bearish gold)
  → Gold signals need stronger confirmation
  → Reduce confidence by 10% for gold longs

If VIX 15-20:
  → Normal environment
  → No adjustment to gold signals

If VIX 20-30:
  → Risk-off environment (gold has natural bid)
  → Add +8-10% to gold buy signals
  → But verify real yields also support (don't chase)

If VIX > 30:
  → Crisis mode (extreme risk-off)
  → Add +15% to gold buy signals
  → BUT: Avoid entry; wait for VIX to settle at 20-25
  → Crisis rallies often reverse sharply
```

---

## 5. Central Bank Gold Buying

### Definition
Net physical gold purchases by central banks (Federal Reserve, ECB, BoE, BoJ, PBoC, etc.)

### Long-Term Trend
- **2000-2010**: Central banks sold gold (UK sold 400 tons)
- **2010-2015**: Gradual shift to buying
- **2015-Present**: Persistent institutional buying (100-500 tons/year)

### Key Buyers (2020-2026)

| Central Bank | Annual Buying | Reason | Source |
|---|---|---|---|
| **China (PBoC)** | 100-200 tons/year | Diversify reserves from USD | WGC reports |
| **India** | 80-120 tons/year | Inflation hedge, reserve diversification | WGC reports |
| **Russia** | 50-100 tons/year | De-dollarization, sanctions resistance | WGC reports |
| **Central Asian Banks** | 30-50 tons/year | Regional reserve building | WGC reports |
| **Turkey, Mexico** | 20-30 tons/year | Inflation hedge | WGC reports |

### Impact on Gold Prices (Empirical Regularity)

| Observation | Confidence | Evidence |
|---|---|---|
| Large CB buying creates price floor | MEDIUM | 2015-2025 institutional demand remains steady |
| Buying accelerates during USD weakness | HIGH | China/Russia buy more when DXY weak |
| Not primary driver (secondary factor) | HIGH | Real yields/DXY move gold 5-10x more than CB flows |

### Data Source
- **World Gold Council**: https://www.gold.org/ (monthly reports on CB flows)
- **Frequency**: Updated monthly, 1-2 month lag
- **Quality**: Data sourced from central banks directly

### Trading Protocol

```
Central Bank Buying (Supporting Factor Only):

Step 1: Check WGC Latest Report (https://www.gold.org/)
  - Identify major buyers (China, India, Russia)
  - Compare to 5-year average

Step 2: Trend Analysis
  - If CB buying accelerating: +5% confidence boost
  - If CB buying declining: -5% confidence hit
  - Neutral if steady

Step 3: Use as Confirmation Only
  - Never build trade on CB buying alone
  - Use as tie-breaker if other signals mixed
  - Example: "Technical says BUY, real yields neutral,
             but CB buying strong → proceed with BUY"
```

---

## Integration: Multi-Factor Macro Framework

### Decision Algorithm

```
1. Check Real Yields (Primary)
   Score = 0-100 based on level and trend
   
2. Check DXY (Primary)
   Score = 0-100 based on trend and momentum
   
3. Check Fed Policy (Secondary)
   Adjust real yields expectation forward 3-6 months
   
4. Check Risk Sentiment (Secondary)
   Adjust score based on VIX level
   
5. Check CB Buying (Tertiary)
   Validate alignment with macro thesis
   
Combined Score = (Real Yields×40% + DXY×40% + Policy×10% + Risk×5% + CB×5%)

Result:
  <30: BEARISH regime (avoid longs)
  30-50: MIXED regime (require strong technical confluence)
  50-70: NEUTRAL regime (follow technical signals)
  70-90: BULLISH regime (reduce technical signal requirements)
  >90: VERY BULLISH regime (high conviction buys only)
```

---

## Key Takeaways

1. **Real yields are king**: -0.80 correlation, explains 65% of gold variance
2. **DXY is persistent**: -0.70 correlation, often moves with real yields
3. **Fed policy is forward-looking**: Act before real yields officially change
4. **VIX is tactical**: Good for day-to-day adjustments, not strategic
5. **CB buying is confirming**: Secondary indicator, use as validation

---

## References

- Gundlach, Jeffrey, "Secular Outlook" (DoubleLine Capital quarterly reports)
- Federal Reserve FRED Database: https://fred.stlouisfed.org/
- World Gold Council: https://www.gold.org/
- CME FedWatch: https://www.cmegroup.com/markets/money-markets/fed-funds.html
- Bureau of Labor Statistics CPI: https://www.bls.gov/cpi/

---

## Next: See also
- `../technical_analysis/multi_timeframe.md` - Combine macro + technical
- `../risk_management/correlation_decay.md` - Monitor breakdown of relationships
