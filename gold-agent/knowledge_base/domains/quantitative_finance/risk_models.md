# Risk Models — VaR, Expected Shortfall, Sharpe Ratio

## Executive Summary

Risk models quantify potential losses and performance consistency. In this trading system, risk models serve as diagnostic tools—the primary risk management remains capital preservation rules (daily loss limit, drawdown circuit breaker, position sizing).

**Three Key Models**:
1. **Value at Risk (VaR)**: Probability of losing more than X amount
2. **Expected Shortfall (ES)**: Expected loss when worst-case scenarios occur
3. **Sharpe Ratio**: Risk-adjusted return metric

---

## Value at Risk (VaR)

### Definition

VaR answers: "What is the maximum loss I can expect with X% confidence over Y days?"

```
VaR(95%, 1 day) = The maximum loss likely to occur 95% of the time
                = 5th percentile of returns distribution
                = "Worst day in 20 days"
```

### Historical Calculation (Empirical Method)

```python
def calculate_var_empirical(returns: list, confidence_level: float = 0.95):
    """
    Calculate VaR using historical return distribution.
    
    Args:
        returns: List of daily return percentages
        confidence_level: Confidence (0.95 = 95% confidence)
    
    Returns:
        VaR value (negative = loss)
    """
    sorted_returns = sorted(returns)
    var_index = int(len(returns) * (1 - confidence_level))
    return sorted_returns[var_index]  # 5th percentile for 95% confidence

# Example:
# Last 100 days of gold returns: [-0.5%, +0.3%, -1.2%, +0.8%, ...]
# Sorted (worst first): [-3.5%, -2.8%, -2.1%, -1.9%, -1.7%, ...]
# VaR(95%, 1 day) = sorted_returns[5] = -1.7%
# Interpretation: "95% of the time, daily loss <= 1.7%"
```

### VaR in This System

**Application**: Verify that daily loss limit (5%) is aligned with VaR:

```
Account: $10,000
Daily Loss Limit: 5% = $500 maximum loss per day

VaR(95%, 1 day) = -1.7% = $170 max expected daily loss (95% confidence)
VaR(90%, 1 day) = -2.3% = $230 max expected daily loss (90% confidence)
VaR(99%, 1 day) = -3.8% = $380 max expected daily loss (99% confidence)

Observation: Daily loss limit (5%) > VaR(99%) (3.8%)
→ System is conservative, protects against tail events
→ Halts trading 1x per 100 days on average (when worst day occurs)
```

### Limitations of VaR

```
Problem 1: Doesn't tell you how bad worst case is
  VaR(95%) = -1.7%, but doesn't answer: "If worst happens, how much worse?"
  
Problem 2: Based on historical distribution (assumes past = future)
  Gold returned -1.7% on worst day in past year
  But next worst day could be -5% (market regime change)
  
Problem 3: Ignores tail risk (extremely rare but catastrophic events)
  Example: Flash crash, geopolitical crisis, exchange halted
  VaR doesn't quantify these

Solution: Use Expected Shortfall for tail risk, AND maintain firm daily limits
```

---

## Expected Shortfall (ES) / Conditional VaR

### Definition

ES answers: "When the worst X% of days occur, what is my average loss?"

```
ES(95%) = Average loss across worst 5% of days
        = Expected loss conditional on being in tail
        = VaR + "how much worse than VaR"
```

### Calculation

```python
def calculate_expected_shortfall(returns: list, confidence_level: float = 0.95):
    """
    Calculate ES (average of all returns worse than VaR).
    """
    sorted_returns = sorted(returns)
    var_index = int(len(returns) * (1 - confidence_level))
    tail_returns = sorted_returns[:var_index]  # All returns worse than VaR
    return sum(tail_returns) / len(tail_returns)

# Example:
# VaR(95%, 1 day) = -1.7%
# Worst 5 days: [-3.5%, -2.8%, -2.1%, -1.9%, -1.7%]
# ES(95%) = (-3.5 - 2.8 - 2.1 - 1.9 - 1.7) / 5 = -2.4%
# Interpretation: "When a worst-day occurs, average loss is -2.4% (worse than -1.7% VaR)"
```

### ES Insight for Capital Preservation

```
Daily Loss Limit = 5%
ES(95%, 1 day) = -2.4%
Ratio = 5% / 2.4% = 2.08x buffer

Interpretation: On worst days (which occur ~1x/month), the system can tolerate
                2x the worst-expected loss before triggering daily halt
                
Implication: Daily halt triggers approximately:
              - 1x per 100 days for normal market days (VaR breach)
              - 1x per 500 days for tail risk days (ES breach)
```

---

## Sharpe Ratio

### Definition

Sharpe Ratio measures return per unit of risk (risk-adjusted performance).

```
Sharpe Ratio = (Average Return - Risk-Free Rate) / Standard Deviation

Example:
  System Average Return: 0.15% per day = 3.75% per month (annualized ~45%)
  Standard Deviation: 1.2% per day (volatility)
  Risk-Free Rate: 0.02% per day (10-year Treasury) = 5% annualized
  
  Sharpe = (0.15% - 0.02%) / 1.2% = 0.108
  
Interpretation: For every unit of risk taken, system generates 0.108 units of return
                (higher is better; >1.0 is exceptional)
```

### Interpreting Sharpe Ratios

| Sharpe Ratio | Assessment | Typical Trader |
|---|---|---|
| < 0.5 | Poor (return insufficient for risk) | ~80% of retail traders |
| 0.5-1.0 | Acceptable | ~15% of professional traders |
| 1.0-2.0 | Good (professionally viable) | ~4% of traders |
| 2.0-3.0 | Excellent (rare) | ~0.8% of traders |
| > 3.0 | Exceptional (nearly impossible) | ~0.1% of traders, or overfitted |

### Sharpe Ratio in This System

**Diagnostic Use**: After 100+ trades, calculate Sharpe to assess system quality:

```python
def calculate_sharpe_ratio(trades_pnl: list, risk_free_rate_daily: float = 0.0002):
    """
    Calculate Sharpe ratio from trade P&L history.
    
    risk_free_rate_daily: 10-year Treasury / 252 trading days
                          ~5% annual = ~0.02% daily
    """
    avg_daily_return = sum(trades_pnl) / len(trades_pnl)
    std_dev = calculate_std_dev(trades_pnl)
    
    sharpe = (avg_daily_return - risk_free_rate_daily) / std_dev
    return sharpe
```

**Interpretation Guidance**:

```
After 100 live trades:
  Sharpe = 0.3 → System underperforming, research needed
  Sharpe = 0.8 → System acceptable, viable for trading
  Sharpe = 1.5 → System good, profitable and consistent
  Sharpe = 2.5 → Exceptional, investigate for overfitting
```

---

## Calmar Ratio (Return / Max Drawdown)

### Definition

Calmar Ratio = Annual Return / Maximum Drawdown

```
Example:
  Annual Return: 45%
  Maximum Drawdown: 12%
  Calmar = 45% / 12% = 3.75
  
Interpretation: System returns 3.75x the maximum drawdown annually
                (higher is better; >2.0 is professional quality)
```

### Application in This System

**Verification After 6 Months**:

```
Cumulative P&L: +$2,450 (on $10,000 account) = +24.5%
Maximum Drawdown: -$800 (8% from peak) 
Calmar = 24.5% / 8% = 3.06

Assessment: Calmar 3.06 indicates system is professionally viable
            Return is 3x the drawdown (excellent risk-adjusted performance)
            
Threshold: Calmar > 1.0 for viable system
           Calmar > 2.0 for professional quality
           Calmar < 0.5 signals system needs revision
```

---

## Sortino Ratio (Return / Downside Deviation)

### Definition

Sortino improves on Sharpe by only penalizing downside volatility (not upside).

```
Sortino = (Average Return - Risk-Free Rate) / Downside Deviation Only

Where:
  Downside Deviation = Standard Deviation of negative returns only
  
Example:
  System has 10 days: [+1.2%, +0.8%, -0.5%, +1.0%, -0.3%, +0.9%, -0.8%, +1.1%, +0.7%, +0.6%]
  
  Sharpe uses std dev of all 10 days
  Sortino uses std dev of only 3 negative days (the -0.5%, -0.3%, -0.8%)
  
  Result: Sortino typically > Sharpe (because negative days are smaller swing)
```

### Sortino in Trading

**Insight**: Gold trading typically has:
- Many small wins (+0.5% to +1.5% per winning trade)
- Few large losses (-1.0% to -2.0% on stop-out trades)
- Asymmetric distribution (skewed positive)

Sortino Ratio is more appropriate than Sharpe for such systems.

---

## Integration: Risk Models in This System

### Diagnostic Checks (Performed Monthly)

```python
def monthly_risk_model_check(trades: list, capital: float):
    """
    Monthly diagnostic check of system risk metrics.
    Purpose: Verify capital preservation rules are working as designed
    """
    var_95 = calculate_var_empirical(get_daily_returns(trades), 0.95)
    es_95 = calculate_expected_shortfall(get_daily_returns(trades), 0.95)
    sharpe = calculate_sharpe_ratio(get_daily_pnl(trades))
    sortino = calculate_sortino_ratio(get_daily_pnl(trades))
    calmar = calculate_calmar(get_cumulative_return(trades), get_max_drawdown(trades))
    
    # Verify alignment with capital rules
    daily_loss_limit = capital * 0.05  # 5% = $500 on $10K
    
    print(f"VaR(95%): {var_95:.2%} (limit: 5.0%)")
    print(f"ES(95%):  {es_95:.2%} (limit: 5.0%)")
    print(f"Sharpe:   {sharpe:.2f} (target: >0.8)")
    print(f"Sortino:  {sortino:.2f} (target: >1.0)")
    print(f"Calmar:   {calmar:.2f} (target: >1.0)")
    
    # Alerts
    if abs(var_95) > 0.05:
        logger.warning(f"VaR breach: {var_95:.2%} > 5.0% limit")
    if sharpe < 0.5:
        logger.warning(f"Sharpe ratio low: {sharpe:.2f} (system may not be profitable)")
    if calmar < 0.5:
        logger.error(f"Calmar critical: {calmar:.2f} (system in drawdown phase)")
```

### Monthly Report Example

```
=== RISK MODELS REPORT — Month 1 ===

Value at Risk (VaR):
  VaR(95%, 1 day): -1.8% (within 5% daily limit)
  VaR(99%, 1 day): -3.2% (within emergency margin)
  Assessment: ✓ PASS — Downside risk within expectations

Expected Shortfall (ES):
  ES(95%, 1 day):  -2.4% (average worst-day loss)
  Assessment: ✓ PASS — Tail risk acceptable

Sharpe Ratio: 0.85 (monthly, 21 trading days)
  Interpretation: ✓ ACCEPTABLE — Return sufficient for risk taken
  Benchmark: Professional traders = 0.8-1.5

Sortino Ratio: 1.12 (monthly, downside volatility only)
  Interpretation: ✓ GOOD — Upside outpacing downside
  Benchmark: Professional traders = 1.0-2.0

Calmar Ratio: 2.4 (monthly return / max drawdown)
  Interpretation: ✓ EXCELLENT — Return 2.4x max drawdown
  Benchmark: Professional traders = 1.5-3.0

Overall Assessment: SYSTEM PERFORMING AS DESIGNED
  - Daily loss limit (5%) provides sufficient margin
  - Risk-adjusted returns (Sharpe, Sortino) within professional range
  - Return/drawdown (Calmar) demonstrates quality risk management
  
Next Review: 2026-09-03 (month 2)
```

---

## References

- Markowitz, Harry, "Portfolio Selection," Journal of Finance (1952)
- Jorion, Philippe, "Value at Risk" (2006) — definitive VaR reference
- Dowd, Kevin, "Measuring Market Risk" (2007) — ES and tail risk
- Sharpe, William F., "The Sharpe Ratio," Journal of Portfolio Management (1994)
- Sortino, Frank, "The Sortino Ratio," Pensions & Investments (2001)
- Young, Robert R., "Managing Investment Portfolios Using Value-at-Risk" (2009)
