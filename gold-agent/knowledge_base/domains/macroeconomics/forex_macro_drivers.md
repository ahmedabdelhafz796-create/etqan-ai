# Forex Macro Drivers — Multi-Pair Analysis

**Scope**: Major currency pairs (EUR/USD, GBP/USD, USD/JPY, AUD/USD, etc.)  
**Market Hours**: 24-hour market, overlapping sessions (Tokyo → London → New York)  
**Tradability per Sharia**: Spot-only, swap-free accounts required (zero overnight interest)  

## Core Macro Drivers for Forex

Unlike gold (driven primarily by real yields and DXY), forex pairs respond to diverging central bank policies, interest rate differentials, and risk sentiment.

### Driver 1: Interest Rate Differential (Rate Differential Driver)

**Definition**: (Yield of Country A) - (Yield of Country B)

**Impact on Currency Pair**:
- Rising rate differential favors the high-yield currency
- Falling rate differential favors the low-yield currency
- Traders deploy "carry trades" to capture rate differential

**Example — EUR/USD**:
- ECB (European Central Bank) holds rates at 4.0%
- Fed (US Federal Reserve) holds rates at 5.5%
- Differential: USD yields 1.5% more than EUR
- Effect: USD strengthens, EUR weakens → EUR/USD falls
- Trader expectation: Earn 1.5% differential by borrowing EUR, lending USD

**Real Trade Impact** (Actual):
- Historical correlation: Rate differential ≈ 0.75 with currency move direction
- Effect magnitude: +50 bps differential shift typically → 2-3% currency revaluation over 3-6 months
- Timing: Immediate on rate announcement; sustained over differential persistence period

**Sharia Compliance Note**: Carry trades earn from rate differential, NOT from overnight interest swaps. Clean trades exist in swap-free accounts.

### Driver 2: Relative Economic Growth (Growth Differential)

**Indicator**: GDP growth rate differential between countries

**Impact**:
- Faster-growing economy attracts investment, strengthens currency
- Slower-growing economy sees capital outflow, weakens currency

**Example — AUD/USD**:
- Australia GDP growth: 3.5% (YoY)
- US GDP growth: 2.1% (YoY)
- Growth differential: AUD +1.4% advantage
- Effect: AUD strengthens on capital inflow expectations
- Historical correlation: GDP differential ≈ 0.60 with currency direction

**Data Source**: IMF World Economic Outlook, national statistical agencies (monthly/quarterly updates)

### Driver 3: Inflation Differential

**Definition**: (Inflation Rate of Country A) - (Inflation Rate of Country B)

**Impact**:
- Higher inflation weakens currency (purchasing power erosion)
- Lower inflation strengthens currency
- Central banks respond with rate hikes, compounding effect

**Example — GBP/USD**:
- UK CPI: 4.0% (YoY)
- US CPI: 3.1% (YoY)
- Inflation differential: GBP +0.9% disadvantage
- Effect: GBP weakens, USD strengthens → GBP/USD falls
- Mechanism: BoE (Bank of England) may raise rates faster to combat inflation, but markets price in negative real returns → GBP sells off initially, recovers if BoE follows through

**Timing**: CPI releases drive intraday volatility (±1-2% moves common); sustained trend over weeks if inflation gap persists

### Driver 4: Risk Sentiment (Risk-On/Risk-Off)

**Definition**: Market appetite for risky assets vs. safe-haven flows

**Safe-Haven Currencies**: USD (primary), JPY (secondary)
**Risk Currencies**: AUD, NZD, GBP (commodity-linked or high-yield, sell-off in risk-off)

**Mechanism**:
- **Risk-On**: Investors buy emerging market assets, commodity currencies (AUD), high-yield pairs (GBP) → AUD/USD rises, GBP/USD rises
- **Risk-Off**: Investors flee to safety → USD strengthens, JPY strengthens → AUD/USD falls, GBP/USD falls

**Indicator**: VIX level
- VIX < 15 = Low fear, risk-on (buy AUD, NZD, GBP)
- VIX 15-25 = Neutral
- VIX > 25 = High fear, risk-off (buy USD, JPY, sell commodity currencies)

**Real Impact** (Actual):
- Correlation: VIX ≈ -0.65 with AUD/USD (risk-off → AUD sells)
- Magnitude: VIX spike from 15 → 30 typically → 3-5% AUD/USD retracement in 24-48 hours

### Driver 5: Central Bank Policy & Guidance

**Triggers**:
- Interest rate decisions (8x yearly for most central banks)
- Forward guidance (hawkish = rate hikes expected, bearish for currency; dovish = rate cuts expected, bullish for currency)
- Quantitative easing/tightening announcements
- Actual balance sheet changes (M2 money supply growth)

**Example — USD Strength (2023-2024)**:
- Fed held rates at 5.5% longest; other central banks cut rates
- Market pricing: USD will outperform due to rate differential
- Result: USD Index rose from 101 → 105 (+4%)
- Pair impact: EUR/USD fell 1.05 → 0.98 (-6.7%)

**Sharia Consideration**: Rate decisions are NOT Haram, but overnight interest swaps ARE. Trade the rate differential (clean) via swap-free accounts only.

### Driver 6: Capital Flows & Foreign Direct Investment (FDI)

**Indicator**: Current account, FDI inflows, portfolio investment flows

**Mechanism**:
- Large FDI inflow to country A strengthens currency A (investment requires buying local currency)
- Large capital outflow from country A weakens currency A

**Example — AUD/USD (Iron Ore Prices)**:
- Australian exports: Iron ore, coal, wheat (commodity exports)
- When iron ore prices rise → Australia expects higher export revenues → FDI inflows increase
- Result: AUD strengthens
- Historical correlation: Iron ore price ≈ 0.70 with AUD/USD

**Timing**: Quarterly FDI data (lagging indicator); daily impact from forward guidance on expected FDI (leading)

### Driver 7: Trade Balance & Current Account

**Definition**: Exports - Imports (trade balance); broader measure including services/investment income (current account)

**Impact**:
- Persistent trade surplus strengthens currency (export demand requires foreign buyers to buy domestic currency)
- Persistent trade deficit weakens currency

**Example — US Current Account**:
- US current account: -3% of GDP (persistent deficit)
- Impact: Long-term USD weakness (structural headwind)
- BUT: Short-term strength if interest rates compensate (USD yield advantage)

**Timing**: Trade data released monthly (lagging 1-2 months); market prices expectations continuously

## Forex-Specific Risk: Geopolitical Events

Unlike gold (benefit from risk-off), forex pairs face directional uncertainty from geopolitical shocks:

**Risk-Off (Strengthens JPY, USD)**:
- War/conflict escalation
- Sanctions announcement
- Supply chain disruptions

**Risk-On (Strengthens commodity currencies AUD, NZD)**:
- Peace agreement
- Sanctions removal
- Resolution of trade disputes

**Timing**: Hours to days of elevated volatility; cross-pair correlations shift unpredictably

**Trading Protocol**: Avoid 1-2 hours before/after major geopolitical announcements per news/event protocol.

## Multi-Pair Correlation Tracking

**Developed Market Pairs** (EUR/USD, GBP/USD, AUD/USD):
- Correlation between pairs ≈ 0.70-0.85 (they move together often)
- Rationale: All developed economies influenced by global risk sentiment

**Carry Trade Pairs** (High-yield currency pairs like AUD/USD):
- Correlation with VIX ≈ -0.65
- Rise during risk-on (VIX low), fall during risk-off (VIX high)

**Safe-Haven Pairs** (USD/JPY):
- Correlation with VIX ≈ +0.60 (rises during risk-off)
- Inverse to equity markets ≈ -0.70

**Implementation**: Track rolling 60-day correlations; detect when historical relationships break (indicates regime shift).

## Sharia Compliance in Forex Trading

### Swap-Free Requirement
- Must trade on swap-free account (zero overnight interest)
- Carry trade profit comes from rate differential, NOT interest swaps
- Verification: Broker API shows swap_long = 0.0, swap_short = 0.0

### T+2 Settlement Compliance
- Forex market typically T+2 settlement (2 days after trade)
- Taqabud requirement: T+0 or T+2 maximum per AAOIFI Sharia Standard
- Verification: Broker specifies "T+2 spot settlement" (acceptable)

### No Leverage Constraint
- Personal capital only; no margin loans
- Account leverage must be 1.0 (no margining)
- Can trade multiple pairs simultaneously on personal capital only

## Sample Forex Macro Analysis

### Example: EUR/USD Bullish Scenario

**Macro Inputs**:
- ECB rate hold at 4.0% (hawkish guidance for potential hikes)
- US inflation falling (CPI 3.1% → 2.9%), Fed expected to cut in Q3
- Risk sentiment: VIX 14 (low, risk-on)
- EUR growth: +2.2%, US growth: +1.8% (EUR outperforming)

**Regime Classification**: BULLISH_ALIGNED
- Rate differential expected to compress (USD yield advantage narrowing)
- Growth differential favors EUR
- Risk-on sentiment neutral (not negative for developed market pairs)

**Technical Confluence** (H4 timeframe):
- EUR/USD at 1.1050, MA-50 at 1.0980, MA-200 at 1.0850
- RSI-14: 52% (neutral, not overbought)
- MACD: Positive histogram, signal above zero

**Decision**: BUY with 70% confidence
- Macro alignment: +15% adjustment
- Technical confluence: 4/4 indicators (MA structure, RSI neutral, MACD bullish)
- Risk: 1% of capital ($100 on $10K account)
- Entry: 1.1050 market, Stop: 1.1000 (50 pips), Target: 1.1150 (100 pips)
- Risk/Reward: 1:2 (favorable)

**KB References**:
- KB/macroeconomics/forex_macro_drivers.md (rate differential, growth differential)
- KB/technical_analysis/multi_timeframe.md (confluence rule)
- KB/decision_protocols/news_event_protocol.md (no imminent events)

---

## Citations

- Federal Reserve Economic Data (FRED) — Interest rate and inflation data
- IMF World Economic Outlook (October 2023 & April 2024)
- Bank for International Settlements (BIS) — Quarterly review on forex markets
- Martin Aloisi, "FX Trading Strategies" (2022) — Carry trade mechanics, correlation analysis
- Reuters/Bloomberg — Central bank policy tracker and guidance timeline
