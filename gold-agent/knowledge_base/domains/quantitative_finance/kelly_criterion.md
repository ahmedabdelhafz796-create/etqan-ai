# Kelly Criterion — Theory, Application, and Limitations

## Executive Summary

The Kelly Criterion is a mathematical formula that calculates the optimal bet size to maximize long-term wealth growth. While theoretically optimal asymptotically (infinite time horizon), it is too aggressive for practical trading and should only be used diagnostically in this system.

**Formula**: Kelly % = (Win % × Avg Win - Loss % × Avg Loss) / Avg Win

**Practical Rule**: Never use full Kelly. Use at most Quarter-Kelly (1/4) for sizing, and only after backtesting 100+ trades.

---

## Historical Origins

### The Gambling Roots (1956)

**Source**: Kelly Jr., J.L., "A New Interpretation of Information Rate," Bell System Technical Journal (1956)

Kelly developed this formula for optimal bet sizing in roulette and blackjack, where:
- Payoff ratios are known
- Win probabilities are fixed
- No slippage or market microstructure

### Application to Trading (1990s)

**Source**: Vince, Ralph, "Portfolio Management Formulas" (1990)

Adaptation to trading with modifications:
- Substituted expected payoff ratio
- Incorporated historical win/loss statistics
- Acknowledged practical constraints (leverage limits, transaction costs)

**Key Finding**: Kelly works well in mathematical theory, but produces bankruptcies in practice due to:
- Estimation error (win rate and payoff ratio are never known exactly)
- Variance in real-world outcomes
- Psychological inability to withstand drawdowns

---

## The Kelly Formula Explained

### Basic Form

```
Kelly % = (P × B - Q) / B

Where:
  P = Probability of winning (as decimal, 0.0-1.0)
  Q = Probability of losing (1 - P)
  B = Ratio of win size to loss size (Avg Win / Avg Loss)
  Kelly % = Fraction of capital to risk (as decimal, 0.0-1.0)
```

### Practical Trading Form

```
Kelly % = (Win % × Avg Win $ - Loss % × Avg Loss $) / Avg Win $

Example:
  Historical data from 100 trades:
  - 55 winning trades, 45 losing trades
  - Average win: $150 per trade
  - Average loss: $100 per trade
  
  Kelly % = (0.55 × $150 - 0.45 × $100) / $150
          = ($82.50 - $45.00) / $150
          = $37.50 / $150
          = 0.25 = 25%
          
Interpretation: Kelly suggests risking 25% of capital per trade
              (DANGEROUS in practice, would require 4+ consecutive losses to ruin)
```

---

## Kelly vs. Van Tharp: Practical Comparison

| Aspect | Kelly Criterion | Van Tharp (1-2%) |
|---|---|---|
| **Theory** | Mathematically optimal (asymptotic) | Heuristic, empirically proven |
| **Typical Output** | 15-40% of capital per trade | 1-2% of capital per trade |
| **Drawdown Tolerance** | 30-50% drawdowns | 5-15% drawdowns |
| **Psychological Feasibility** | Extremely difficult | Sustainable |
| **Recovery from Drawdown** | Faster but requires discipline | Slower but stable |
| **Estimation Error Sensitivity** | EXTREME (20% error in win % = 4x position sizing error) | MODERATE (20% error = 20% sizing error) |
| **Professional Use** | Diagnostic only, portfolio level | Daily trading standard |
| **Recommended Practice** | Calculate after 100+ trades for diagnostics | Use 1% default for all trades |

---

## Why Kelly Fails in Trading Practice

### Reason 1: Win Rate Estimation Error

```
Problem: Win rate is estimated, not known

Example:
  Estimated win rate: 60% (from 50 trades)
  Actual win rate: 50% (true parameter)
  
  Kelly calculation (wrong):
    Kelly % = (0.60 × $150 - 0.40 × $100) / $150 = 23%
    Suggested position: Risk $2,300 per trade (on $10K account!)
  
  Reality (true):
    Kelly % = (0.50 × $150 - 0.50 × $100) / $150 = 3.3%
    Suggested position: Risk $330 per trade (much smaller)
  
  Result: Over-leveraged by 7x due to estimation error
          → Account ruin likely within 20 trades
```

**Source**: Thorp, Edward O., "The Mathematics of Gambling" (1985) — documented this estimation problem

### Reason 2: Payoff Ratio Variability

```
Problem: Payoff ratio varies trade to trade (not constant)

Example (Gold Trading):
  Trade A: Win $200, Stop Loss $50 = 4:1 payoff ratio
  Trade B: Win $100, Stop Loss $50 = 2:1 payoff ratio
  Trade C: Win $300, Stop Loss $75 = 4:1 payoff ratio
  Average: 3.3:1
  
  Kelly uses average payoff (3.3:1), but actual varies (2:1 to 4:1)
  → Position sizes don't match actual outcome distribution
  → Risk management misaligned
```

### Reason 3: Asymptotic Property (Infinite Time Horizon)

```
Mathematical Theorem: Kelly is optimal only as n → infinity

Practical Problem: We don't trade infinitely many times
  Traders retire, accounts close, markets change
  Finite time horizon means Kelly's advantages disappear
  → Van Tharp (fixed-fractional) actually better for finite horizons
  
Source: Markowitz, Harry, "Portfolio Selection" (1952)
        Proved Kelly optimal only asymptotically
```

### Reason 4: Drawdown Magnitude (Psychological Ceiling)

```
Kelly typical drawdown (55% win rate, 1.5:1 payoff): 30-50%
Van Tharp typical drawdown (55% win rate, 1.5:1 payoff): 5-15%

Problem: Humans cannot psychologically sustain 50% drawdowns
  Decision quality degrades when equity down 30%
  Temptation to deviate from system increases
  Revenge trading replaces disciplined execution
  
Professional Observation: Drawdowns >20% correlate with system abandonment
Source: Schwager, Jack D., "Market Wizards" (1989) — trader interviews
```

---

## Kelly Diagnostic Use Case (This System)

### When to Calculate Kelly (Informational Only)

```python
def calculate_kelly_diagnostic():
    """
    Calculate Kelly as diagnostic tool after 100+ trades.
    
    Purpose: Understand theoretical optimal sizing vs. conservative Van Tharp
    Action: Never change position sizing based on Kelly calculation
    Interpretation: Kelly % indicates edge strength:
      - Kelly < 1%: No edge (system is break-even or losing)
      - Kelly 1-5%: Weak edge (use 1% Van Tharp)
      - Kelly 5-15%: Moderate edge (use 1% Van Tharp, Kelly diagnostic shows edge)
      - Kelly > 15%: Strong edge (use 1-2% Van Tharp, consider increasing to 1.5%)
    """
    wins = [t for t in trades if t.pnl > 0]
    losses = [t for t in trades if t.pnl < 0]
    
    win_pct = len(wins) / len(trades)
    loss_pct = len(losses) / len(trades)
    avg_win = sum([t.pnl for t in wins]) / len(wins)
    avg_loss = sum([abs(t.pnl) for t in losses]) / len(losses)
    
    kelly = (win_pct * avg_win - loss_pct * avg_loss) / avg_win
    
    return {
        "kelly_percent": kelly * 100,
        "interpretation": interpret_kelly(kelly),
        "action": "DIAGNOSTIC ONLY - Do NOT use for position sizing",
        "position_sizing_recommendation": "Maintain Van Tharp 1% default"
    }
```

### Interpreting Kelly Diagnostics

```
Scenario A: Kelly = 0.5% (calculated)
  Message: "System is barely profitable"
  Action: Continue with 1% Van Tharp (conservative)
  Implication: Edge is weak, continue research

Scenario B: Kelly = 8% (calculated)
  Message: "System has legitimate edge"
  Action: Continue with 1% Van Tharp (remains safe)
  Implication: If 100+ trades confirm, system is working as intended
  
Scenario C: Kelly = 25% (calculated)
  Message: "System shows exceptional edge (rare)"
  Action: Continue with 1% Van Tharp for daily trading
          Research increasing to 1.5% after backtesting 200+ more trades
  Implication: Investigate why edge is so strong (likely overfitting)
```

---

## Fractional Kelly (Practical Compromise)

### Quarter-Kelly Strategy

```
Rather than using full Kelly, use Kelly / 4

Rationale: Reduces drawdowns to psychological tolerance levels

Example:
  Calculated Kelly: 25%
  Quarter Kelly: 25% / 4 = 6.25%
  
  Trade sizing: Risk 6.25% per trade
  Expected drawdown: 15-20% (vs. 50%+ for full Kelly)
  Recovery time: Faster than 1% Van Tharp
  
Challenge: Requires proof of edge (100+ historical trades minimum)
Recommendation: Stick with Van Tharp 1% until system proves itself
```

### When Quarter-Kelly Might Be Considered

```
Criteria (ALL must be met):
  1. System has 200+ historical trades in backtesting
  2. Win rate stable across different market conditions
  3. Payoff ratio consistent (variance < 30% around mean)
  4. Estimated Kelly >= 10% (indicates strong edge)
  5. Forward testing on paper trading >= 50 trades
  6. Psychological comfort with 20%+ drawdowns
  7. Capital available to recover from drawdown

Example:
  After 300+ backtested trades + 75 paper trades:
  - Win rate: 60% (consistent)
  - Avg win: $150, Avg loss: $75
  - Kelly = 30%
  - Quarter Kelly = 7.5%
  
  Consider: Increasing from 1% to 2% risk (under Van Tharp cap)
           (NOT using 7.5%, but acknowledging edge strength)
```

---

## Conclusion: Kelly in This System

**Decision**: Kelly is calculated and reported as diagnostic.
- **Used For**: Understanding system edge strength after 100+ trades
- **NOT Used For**: Position sizing or daily trading decisions
- **Default Remains**: Van Tharp fixed-fractional 1% per trade
- **Immutable Cap**: 2% per trade, emergency use only

This conservative approach trades slightly slower recovery for much higher probability of system survival and sustainable trading psychology.

---

## References

- Kelly Jr., J.L., "A New Interpretation of Information Rate," Bell System Technical Journal (1956)
- Vince, Ralph, "Portfolio Management Formulas" (1990)
- Thorp, Edward O., "The Mathematics of Gambling" (1985)
- Markowitz, Harry, "Portfolio Selection," Journal of Finance (1952)
- Schwager, Jack D., "Market Wizards" (1989)
- Taleb, Nassim, "Fooled by Randomness" (2001) — critique of Kelly in trading
