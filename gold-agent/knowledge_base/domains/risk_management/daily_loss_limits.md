# Daily Loss Limits — Immutable Capital Preservation Rule

## Executive Summary

The daily loss limit is a hard stop that halts all new trading when cumulative losses reach 5% of account equity in a single day. This rule is code-enforced and cannot be disabled—it protects against catastrophic loss days and psychological breakdown.

**Rule**: Daily Loss ≥ 5% → HALT all new trades until UTC 00:00 reset

---

## Why Daily Limits Exist

### Problem 1: Catastrophic Loss Days

```
Historical Pattern:
  - Bad macro news → Market gaps down
  - Stop-loss gets hit multiple times
  - Trader panic → revenge trading
  - Result: 10-20% loss in single day

Example (Hypothetical Gold Trader):
  Start Day Equity: $10,000
  Trade 1: Loss -$300
  Trade 2: Loss -$200
  Trade 3: Loss -$150 (already hit $650 = 6.5% loss)
  
  Without daily limit: Trader likely continues trading, accumulates -$1,500+
  With daily limit: Forced stop at $500 loss, protects remaining capital

Source: Schwager, Jack D., "Market Wizards" (1989) — trader interviews show pattern
```

### Problem 2: Revenge Trading

```
Psychological Trap:
  After losing 2-3 trades, trader feels pressure to "get even"
  Starts taking larger positions
  Lowers quality standards for entries
  Results in larger losses
  
Solution: Daily limit removes decision-making
          "System says stop, I stop"
          Emotion overrides prevented by rules
```

---

## Daily Loss Limit Mechanics

### Calculation

```python
def check_daily_loss_limit(current_equity: float, initial_daily_equity: float):
    """
    Check if daily loss exceeds 5% limit.
    
    daily_loss_amount = Initial Daily Equity - Current Equity
    daily_loss_pct = (daily_loss_amount / initial_daily_equity) * 100
    
    if daily_loss_pct >= 5.0%:
        HALT all new trades
    """
    daily_loss = initial_daily_equity - current_equity
    daily_loss_pct = (daily_loss / initial_daily_equity) * 100
    
    if daily_loss_pct >= 5.0:
        return False, f"Daily limit breached: {daily_loss_pct:.1f}% loss"
    else:
        return True, f"Daily loss OK: {daily_loss_pct:.1f}% (limit: 5.0%)"

# Example:
# Start of day: $10,000 equity
# After 3 losing trades: $9,500 equity
# Daily loss: $500 = 5.0% → LIMIT TRIGGERED
```

### Reset Timing

```
Reset Schedule: UTC 00:00 (midnight UTC)
  - When UTC day rolls over, counter resets to $0
  - Allows new trades starting UTC 00:00
  - Transparent and unambiguous
  
Timezone Consideration:
  All times in UTC (never affected by daylight savings)
  Traders in different timezones get reset at same absolute time
  
Example:
  New York (EDT): 8 PM Aug 3 → Reset at 4 AM Aug 4
  London (BST):   1 AM Aug 4 → Reset at 4 AM Aug 4
  Tokyo (JST):    1 PM Aug 4 → Reset at 4 AM Aug 4
  
All traders reset simultaneously at UTC 00:00
```

---

## Daily Loss Limit in Practice

### Scenario 1: Normal Trading Day (No Breach)

```
Aug 3, 2026 UTC:
  00:00: Start with $10,000
  06:00: Trade 1 closed, P&L -$100 → Equity $9,900 (loss 1.0%)
  08:00: Trade 2 closed, P&L +$200 → Equity $10,100 (loss -1.0%, net +$100)
  12:00: Trade 3 closed, P&L -$50 → Equity $10,050 (loss 0.5%)
  16:00: Trade 4 closed, P&L +$150 → Equity $10,200 (loss -2.0%, net +$200)
  
  Daily Cumulative Loss: MAX(-$100) = $100
  Daily Loss %: 1.0% (well below 5% limit)
  
  Status: ✓ TRADING ALLOWED (cumulative loss < 5%)
```

### Scenario 2: Bad Day (Breach Occurs)

```
Aug 3, 2026 UTC:
  08:00: Trade 1 closed, P&L -$500 → Loss 5.0%
  09:00: Check daily limit → BREACHED (5.0% >= 5.0%)
  
  Status: ✗ TRADING HALTED
  Message: "Daily loss limit breached. No new trades until reset at 00:00."
  
  Equity: $9,500 remaining
  Halt Duration: 15 hours (until UTC 00:00)
  
  What Trader Does:
    - Close existing positions (optional)
    - Stop ALL new trade entries
    - Review what went wrong
    - Prepare for next day with reset
```

### Scenario 3: Recovery Attempt (Limit Prevents Revenge)

```
Aug 3 (Bad Day):
  09:00: Trade 1 Loss -$500 → Daily loss 5.0% → LIMIT TRIGGERED
  09:05: Trader wants to revenge trade to "get even"
  09:05: System BLOCKS new trade entry
  
  Without System Rule: Trader enters 2 more trades
                      Both stop out for -$250 each
                      Daily loss now -$1,000 (10%)
  
  With System Rule: No new trades allowed
                   Daily loss capped at -$500 (5%)
                   Remaining capital: $9,500 (protected)
  
  Result: System rule saved $500 of capital
```

---

## Daily Loss Limit vs. Other Risk Rules

### Comparison Table

| Rule | Trigger | Action | Recovery |
|---|---|---|---|
| **Daily Loss** | 5% loss in single day | Halt new trades | Reset UTC 00:00 |
| **Drawdown CB** | 15-20% loss from peak | Emergency state | Manual recovery only |
| **Consecutive Loss** | 3-4 losing trades in row | Pause new trades | 1 winning trade or manual override |
| **Position Hold-time** | 24 hours elapsed | Force close position | Close occurs automatically |

---

## Psychology Behind the 5% Threshold

```
Why 5% Specifically?

1. Statistical Basis:
   - If risk per trade = 1%, can lose 5 consecutive trades before hitting limit
   - Probability of 5 consecutive losses (55% win rate) = ~8%
   - Frequency: Approximately 1x per 12-15 days
   
2. Psychological Viability:
   - 5% loss is noticeable but not catastrophic
   - Trader still functional (not in crisis mentality)
   - Allows rational review of what went wrong
   - Can restart next day with full focus
   
3. Capital Preservation:
   - 5% limit prevents domino effect of revenge trading
   - After 1-2 bad days, account still intact
   - 20 losing days at 5% each = 64% final equity
   - Survivable drawdown (can recover with discipline)

Source: Van Tharp, "Trade Your Way to Financial Freedom" (2007)
        Professional traders consensus: 5-10% daily halt threshold
```

---

## Implementation Notes

### What Happens When Limit is Breached

```python
def on_daily_loss_breach():
    """
    Actions when daily loss limit exceeded.
    """
    # Immediate actions
    halt_new_trade_signals = True
    log_event("DAILY_LOSS_LIMIT_BREACHED")
    send_alert("Daily loss limit reached 5%. No new trades until reset.")
    
    # Optional trader actions
    # - Close existing positions (optional, trader's choice)
    # - Review the day's trades
    # - Prepare next-day strategy
    
    # Automatic reset
    schedule_daily_reset_check()  # Fires at UTC 00:00
```

---

## References

- Van Tharp, "Trade Your Way to Financial Freedom" (2007)
- Schwager, Jack D., "Market Wizards" (1989)
- Taleb, Nassim, "Fooled by Randomness" (2001) — Daily volatility patterns
