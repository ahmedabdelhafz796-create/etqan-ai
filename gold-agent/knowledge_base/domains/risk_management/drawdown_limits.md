# Maximum Drawdown Circuit Breaker — Emergency Capital Preservation

## Executive Summary

The maximum drawdown circuit breaker monitors account equity against the highest watermark (peak equity). When drawdown reaches 15-20%, the system escalates to Emergency state, closes all positions, and halts execution until manual recovery.

**Rule**: Drawdown ≥ 15-20% from peak → EMERGENCY state, close all positions, halt execution

---

## Drawdown Definition

```
Drawdown % = (Peak Equity - Current Equity) / Peak Equity × 100

Example:
  Peak Equity (highest balance ever): $10,000
  Current Equity: $8,500
  Drawdown: ($10,000 - $8,500) / $10,000 × 100 = 15%
  
Trigger: Drawdown >= 15% → Emergency escalation
```

---

## Why Drawdown Limits Exist

### Problem: Psychological Breakdown

```
Historical Pattern:
  - Small losses compound
  - After 10% drawdown: Trader's decision quality degrades
  - After 15% drawdown: Emotional trading begins (desperation)
  - After 20% drawdown: System abandonment likely (stop following rules)
  
Research Source: Schwager, Jack D., "Market Wizards" (1989)
                 Multiple trader interviews show degradation above 15-20%

Solution: Automated circuit breaker
          Remove emotional decision-making
          Force-close all positions
          Require manual review before resuming
```

### Problem: Compounding Losses

```
Drawdown Effect:
  10% loss requires 11.1% gain to recover
  15% loss requires 17.6% gain to recover
  20% loss requires 25% gain to recover
  
Time to Recovery:
  With 1% win rate, 15% drawdown takes 30+ trades to recover
  With 55% win rate (good system), still 15-20 trades
  Time = 3-4 weeks of daily trading

Worst Case:
  Large drawdown → Desperation trading → Larger loss
  
Solution: Circuit breaker prevents cascading drawdowns
```

---

## Drawdown Monitoring

### Real-time Tracking

```python
def track_drawdown(current_equity: float, peak_equity: float):
    """
    Calculate current drawdown from peak.
    """
    if current_equity > peak_equity:
        peak_equity = current_equity  # New peak, reset watermark
    
    drawdown_pct = (peak_equity - current_equity) / peak_equity * 100
    
    if drawdown_pct >= 15.0:
        # EMERGENCY: Breaker triggered
        escalate_to_emergency_state()
        close_all_positions()
        halt_execution()
        return "EMERGENCY", drawdown_pct
    
    elif drawdown_pct >= 12.0:
        # WARNING: Approaching breaker
        log_warning(f"Drawdown {drawdown_pct:.1f}% (approaching 15% limit)")
        reduce_position_sizes()
        return "WARNING", drawdown_pct
    
    else:
        # OK: Normal operation
        return "OK", drawdown_pct

# Example:
# Peak: $10,000
# After losing trades: $8,300
# Drawdown: 17% → Exceeds 15% trigger → EMERGENCY
```

---

## Emergency State Actions

### Immediate (Automatic)

```
1. Close All Positions
   - Market order to close every open position
   - No stop-loss used (market close regardless of price)
   - Record close price for audit trail
   
2. Halt Execution
   - Execution module disabled
   - No new trades can be entered
   - Even if signal is STRONG BUY, no execution
   
3. Trigger Alert
   - Send urgent notification (email, SMS, dashboard)
   - Log timestamp and reason: "Drawdown {X}% >= 15% circuit breaker"
   - Record peak equity and current equity
```

### Manual Recovery Required

```
What Trader Must Do:
  1. Review what went wrong (system analysis)
  2. Verify signals are still working (backtest)
  3. Check macro environment (has regime changed?)
  4. Plan revised strategy (if needed)
  5. Explicitly re-enable execution in config
  
No Automatic Exit: Unlike daily loss limit (resets UTC 00:00)
                  Drawdown circuit breaker requires manual intervention
                  Forces conscious decision to resume trading
```

---

## Drawdown Levels and Trader Psychology

### 5-10% Drawdown (Normal)

```
Psychological State: Slight concern, but confident
Action: Continue trading normally
Confidence: Unaffected
Decision Quality: Normal

Frequency: 1x per 5-10 days (normal variation)
Recovery Time: 1-2 days with 55% win rate
```

### 10-15% Drawdown (Serious)

```
Psychological State: Concerned, questioning system
Action: Reduce position sizes, avoid high-risk setups
Confidence: Reduced 20-30%
Decision Quality: Slightly degraded (more conservative)

Frequency: 1x per 20-30 days
Recovery Time: 3-5 days with 55% win rate
Warning: Circuit breaker warning triggered (12% level)
```

### 15-20% Drawdown (Crisis)

```
Psychological State: Panic, revenge trading urge
Action: SYSTEM FORCES HALT (circuit breaker triggered)
Confidence: Severely degraded
Decision Quality: Poor (emotional override)

Frequency: 1x per 50-100 days (if system working)
Recovery Time: 7-10 days (if system is actually sound)
Danger: Without circuit breaker, losses often continue to 30-50%
```

### 20%+ Drawdown (Catastrophe)

```
Psychological State: System failure assumed, panic selling
Action: (Only if circuit breaker disabled) Abandon system entirely
Confidence: Zero
Decision Quality: Irrational

Historical Outcome: Many retail traders blow up entire accounts
                   Drawdown reaches 50-100%

Circuit Breaker Benefit: Caps damage at ~20%, allows recovery
```

---

## Recovery After Circuit Breaker Trigger

### Step 1: Analysis (24-48 hours)

```
Questions to Answer:
  1. What caused the drawdown? (Market event? System error? Bad luck?)
  2. Is the system still valid? (Backtest recent results)
  3. Has market regime changed? (Macro analysis)
  4. Is this normal variance or system failure?

Example A (Normal Variance):
  - 5 consecutive losing trades (happens statistically ~8% of time)
  - System still working correctly
  - Just bad luck for 2 days
  → Safe to resume after analysis
  
Example B (System Failure):
  - Signals stopped working (backtest shows loss of edge)
  - New market regime not accounted for
  - System architecture broken
  → Do NOT resume, fix system first
```

### Step 2: Confidence Check

```
Before Resuming:
  Backtest last 20 trades:
    Expected: 11 wins, 9 losses (55% win rate)
    Actual: _____ (check results)
  
  If confidence >= 60%:
    → Safe to resume, system still working
  
  If confidence < 60%:
    → Stop, do not resume, investigate system
```

### Step 3: Restart (Explicit)

```
To Resume Trading:
  1. Trader must explicitly enable execution (config change)
  2. Start with REDUCED position sizes (0.5% instead of 1% risk)
  3. Monitor first 10 trades closely
  4. Gradually return to normal sizing after 10 wins
  
  Prevents: Emotional over-correction or under-confidence
```

---

## Circuit Breaker vs. Daily Loss Limit

| Aspect | Daily Loss (5%) | Drawdown CB (15-20%) |
|---|---|---|
| **Trigger** | Single day, cumulative loss | From peak equity |
| **Reset** | Automatic, UTC 00:00 | Manual recovery only |
| **Duration** | 15-24 hours | Until explicitly re-enabled |
| **Severity** | Moderate | Severe (full emergency) |
| **Frequency** | 1x per 20 days | 1x per 50-100 days |
| **Action** | Halt new trades | Close ALL, halt execution |

---

## References

- Van Tharp, "Trade Your Way to Financial Freedom" (2007)
- Schwager, Jack D., "Market Wizards" (1989)
- Taleb, Nassim, "Fooled by Randomness" (2001) — Drawdown mathematics
