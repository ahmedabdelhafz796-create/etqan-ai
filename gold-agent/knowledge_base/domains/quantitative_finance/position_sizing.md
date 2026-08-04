# Position Sizing — Theory and Practice

## Executive Summary

Position sizing is the single most important decision in professional trading. It determines risk per trade, maximum portfolio heat, and recovery time from drawdowns. Incorrect position sizing can bankrupt an account even with a winning strategy.

**Core Principle**: Never risk more than you can afford to lose on a single trade.

---

## Historical Context: The Evolution of Position Sizing

### Pre-1980s Era: Ad-Hoc Sizing
- Traders used gut feel and account intuition
- "Risk what feels comfortable" mentality
- Resulted in catastrophic drawdowns and blowups
- No systematic approach

### 1980s: Van Tharp Systematization
- **Source**: Van Tharp, "Trade Your Way to Financial Freedom" (2007)
- Introduced fixed-fractional method
- Formula: Position Size = (Account Risk $) / (Entry Price - Stop Loss Price)
- Revolutionized position sizing with mathematical rigor
- Key insight: Risk is known, position size is derived

### 1990s-2000s: Academic Research
- **Source**: Ralph Vince, "Portfolio Management Formulas" (1990)
- Kelly Criterion brought to trading from gambling theory
- Modern Portfolio Theory applied to single-trade sizing
- Risk metrics formalized: VaR, Expected Shortfall

### 2010s-Present: Adaptive Sizing
- Dynamic adjustment based on volatility (ATR-based sizing)
- Regime-adaptive position sizing
- Machine learning optimization (academic research, not practical)
- Consensus: Fixed-fractional Van Tharp remains industry standard

---

## The Van Tharp Method (Industry Standard)

### Formula

```
Position Size = (Account Risk $) / (Entry Price - Stop Loss Price)

Where:
  Account Risk $ = Starting Capital × Risk Per Trade %
  Entry Price - Stop Loss Price = Price Risk per Unit
```

### Example Calculation

```
Starting Capital: $10,000
Risk Per Trade: 1% (PRIMARY default)
Entry Price: $2,050 (gold XAU/USD)
Stop Loss Price: $2,040

Account Risk $ = $10,000 × 0.01 = $100
Price Risk per Unit = $2,050 - $2,040 = $10
Position Size = $100 / $10 = 10 units

Maximum Loss if SL hit = 10 units × $10 = $100 (exactly 1% of account)
```

### Key Properties

1. **Directional**: Entry determines direction (BUY if entry > SL, SELL if entry < SL)
2. **Risk-Defined**: Maximum loss is known before entry (exactly Account Risk $)
3. **Scalable**: Works regardless of account size
4. **Immutable**: Risk amount is fixed, position size adjusts to market conditions

### Why Van Tharp Over Others

| Method | Pros | Cons | Industry Use |
|---|---|---|---|
| **Van Tharp (Fixed-Fractional)** | Simple, proven, industry standard, risk defined | Requires accurate SL placement | 95%+ professional traders |
| **Kelly Criterion** | Mathematically optimal (asymptotically) | Requires win % and payoff ratio, extremely aggressive in practice | Academic, backtesting only |
| **Volatility-Adjusted (ATR)** | Adapts to market volatility | Complex calculation, requires indicator | ~5% professional traders |
| **Percentage-of-Equity** | Simple to calculate | Risk unknown, can exceed account on slippage | Retail traders, dangerous |

---

## The Fixed Baseline Principle (Capital Preservation)

### Problem: House Money Effect

When using current equity for position sizing:
```
Scenario A (after wins):
  Peak Equity: $15,000
  Risk 2% = $300 per trade (position sizes balloon)
  One bad trade and 2% of $15K can wipe out $3K of gains

Scenario B (after losses):
  Current Equity: $8,000
  Risk 2% = $160 per trade (position sizes shrink)
  Psychological pressure to "revenge trade"
```

This violates Van Tharp's core principle: **consistent position sizing regardless of current equity state**.

### Solution: Use Initial Capital as Baseline

```
Position Size = (INITIAL Starting Capital × Risk%) / (Entry - SL)

Properties:
  - Position sizes remain constant through win/loss streaks
  - Prevents psychological bias (revenge trading, overleveraging after wins)
  - Aligns with capital preservation philosophy
  - Follows Van Tharp's original recommendation for consistency
```

### Mathematical Proof (Why It Works)

```
Initial Capital: $10,000
Risk Per Trade: 1% = $100

After 3 winning trades of +2% each:
  Equity: $10,600
  Position Size STILL = $100 / price_diff (same as day 1)
  → Avoids overconfidence → Reduces drawdown risk

After 3 losing trades of -1% each:
  Equity: $9,700
  Position Size STILL = $100 / price_diff (same as day 1)
  → Maintains discipline → Prevents revenge trading

Result: Consistent risk regardless of equity state
```

---

## Risk Per Trade: Default vs. Emergency Ceiling

### Recommended Allocation

```
PRIMARY Default: 1% per trade
  - Used 95%+ of the time
  - Allows account to survive 100+ consecutive 1% losses before ruin
  - Mathematical safety margin
  - Source: Van Tharp empirical recommendation

EMERGENCY Ceiling: 2% per trade
  - Reserved for exceptional setups (rare)
  - Only used when edge is mathematically proven
  - Should almost never be reached in practice
  - Source: Professional trader consensus

ABSOLUTE MAXIMUM: 5% per trade (theoretical cap)
  - Only in extreme situations (position being forced closed by broker)
  - Violates Van Tharp method if used voluntarily
  - Indicates system has failed
```

### Risk of Ruin Calculation

```
Probability of Account Ruin = (1 - edge)^n

Where:
  edge = Win % - Loss %
  n = number of consecutive losses at which capital depleted

Example: 1% risk per trade, 50% win rate, 1:1 risk/reward
  edge = 50% - 50% = 0% (no edge)
  Probability of ruin at 100 consecutive losses = ~100% (obvious)
  
Example: 1% risk per trade, 55% win rate, 1:2 risk/reward
  edge = 55% - (45% × 2) = 55% - 90% = -35% (negative edge!)
  Conclusion: Risk management cannot overcome bad strategy

Conclusion: Position sizing fixes RISK, not WIN RATE. Strategy determines profitability.
```

---

## Position Sizing Constraints (Immutable Rules)

### Rule 1: Maximum Position Size Cannot Exceed Account Margin

```python
max_position_size = available_margin / price
# If using 2% risk and 10:1 margin available:
# Position size = $100 / price_diff (Van Tharp)
# Margin required = position_size × price / margin_multiple
# MUST verify position size is tradeable with available margin
```

### Rule 2: Position Size Must Be Positive and Deterministic

```python
if price_diff <= 0:
    raise ValueError("Stop loss must be below entry price for longs")
if risk_per_trade_pct <= 0:
    raise ValueError("Risk must be positive")
# Position size must be > 0 and must not involve borrowing (Sharia rule)
```

### Rule 3: Consecutive Positions Cannot Exceed Account Heat Limit

```
Maximum Account Heat = Sum of all open position risks
Rule: Max heat typically 5-10% of account across all open positions
Example: If 5 positions open, 1% risk each = 5% total heat (acceptable)
If 10 positions open, 1% risk each = 10% total heat (at limit)
If 12 positions open, 1% risk each = 12% total heat (VIOLATION, close oldest)
```

---

## Integration with Capital Preservation

### Daily Loss Limit Integration

```
If Daily Loss Limit = 5% of account:
  Each 1% risk trade can hit stop loss 5 times before halting

If Daily Loss Limit = 2.5% of account:
  Each 1% risk trade can hit stop loss 2-3 times before halting
  
Rule: Position sizing (1% per trade) must be coordinated with daily limit
If daily limit = 5% and risk = 1%, you can take 5 trades before halt
If daily limit = 5% and risk = 2%, you can take 2-3 trades before halt
```

### Drawdown Recovery Calculation

```
After 10% drawdown with 1% risk per trade:
  Recovery trades needed = 10% / (1% × 1.01) ≈ 10 winning trades
  If win rate = 55%, expected trades to 10 wins ≈ 18 trades
  Time to recovery = 18 trades × 1 trade/day ≈ 3 weeks

After 10% drawdown with 2% risk per trade:
  Recovery trades needed = 10% / (2% × 1.01) ≈ 5 winning trades
  If win rate = 55%, expected trades to 5 wins ≈ 9 trades
  Time to recovery = 9 trades × 1 trade/day ≈ 9 days

Observation: Higher risk enables faster recovery but at higher cost if wrong
Professional consensus: 1% risk for consistency, psychological stability, longevity
```

---

## References

- Van Tharp, "Trade Your Way to Financial Freedom" (2007) — definitive text on position sizing
- Vince, Ralph, "Portfolio Management Formulas" (1990) — optimal f and Kelly integration
- Taleb, Nassim, "Dynamic Hedging" (1997) — risk management mathematics
- Harris, Larry, "Trading and Exchanges" (2003) — market microstructure foundations
- Miller, Bill, "On Bluffing in Poker and Trading" (2009) — Kelly Criterion practical application
