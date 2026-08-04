# Van Tharp Fixed-Fractional Position Sizing

## Overview
The Van Tharp method is the practical implementation of optimal position sizing for retail traders and small accounts. Unlike Kelly Criterion (which is theoretical maximum), Van Tharp's approach balances mathematics with risk preservation.

**Source**: Van Tharp, "Trade Your Way to Financial Freedom" (2007, McGraw-Hill)
**Authority**: 40+ years trading research, founder Van Tharp Institute
**Application**: RECOMMENDED for our system (capital preservation priority)

---

## The Formula

```
Position Size = Account Risk $ / Price Risk per Unit
```

Where:
- **Account Risk $** = Current Equity × Risk Per Trade %
- **Price Risk per Unit** = Entry Price - Stop Loss Price
- **Risk Per Trade %** = Typically 1-2% of account (never >2% in our system)

### Example Calculation

**Scenario**: Gold trading, $10,000 account

1. **Entry Price**: $2,050
2. **Stop Loss**: $2,040
3. **Risk Per Trade**: 2% of equity
4. **Current Equity**: $10,000

**Calculation**:
- Account Risk $ = $10,000 × 2% = $200
- Price Risk per Unit = $2,050 - $2,040 = $10
- Position Size = $200 / $10 = **20 units**

**Result**: Buy 20 units of gold
- Maximum loss if SL hit: $200 (exactly 2% of account)
- Maximum gain potential: Unlimited (but cap profit at 3-5% typical target)
- Risk/Reward: If target is $2,070, gain = 20 × ($2,070 - $2,050) = $400 (4% gain on 2% risk)

---

## Why Van Tharp Over Kelly Criterion?

### Kelly Criterion (Theoretical)

**Formula**: Kelly % = (Win% × AvgWin - Loss% × AvgLoss) / AvgWin

**Advantages**:
- Mathematically optimal for long-term wealth growth
- Personalized to actual win/loss track record
- Maximizes compound returns

**Disadvantages**:
- Requires 20+ trades to calculate accurately (we have <10 initially)
- Full Kelly is *too aggressive* (can wipe out account in unlucky streak)
- Breaks down when assumptions violated (markets not i.i.d.)
- Emotional pressure of position sizes

**Example**: If Kelly says 25% per trade but you have 3 losses in a row, you lose 75%+ of account before recovering. Psychological devastation follows.

### Van Tharp Method (Practical)

**Advantages**:
- Simple, works immediately (no historical data needed)
- Conservative: 1-2% per trade preserves capital
- Focuses on risk management first, profits second
- Works regardless of win rate (even 40% win rate survives)

**Disadvantages**:
- Doesn't leverage historical performance data
- May be "under-sizing" for high-accuracy traders
- Grows capital slower than optimal Kelly

**Verdict**: Van Tharp's 2% is safer, Kelly Criterion works only as diagnostic (Quarter-Kelly maximum).

---

## Implementation in Our System

### Step 1: Immutable 2% Risk Cap
```python
# In capital_preservation.py
risk_per_trade = min(requested_risk, 2.0)  # Immutable cap
```
If anyone tries to set 5%, system forces 2%.

### Step 2: Calculate Position Size at Entry
```python
entry_price = 2050.0
stop_loss_price = 2040.0
current_equity = 10000.0

account_risk = current_equity * 0.02  # $200
price_risk = entry_price - stop_loss_price  # $10
position_size = account_risk / price_risk  # 20 units
```

### Step 3: Audit Trail
Every trade includes:
- Equity at entry
- Entry price
- Stop loss price
- Risk amount ($)
- Risk percentage (%)
- Position size (units)
- Formula applied

### Step 4: Adjust for Equity Changes
After trades, equity changes → position size changes

**Example progression**:
- Initial: $10,000 equity → 20 units per trade
- After -$500 loss: $9,500 equity → 19 units per trade
- After +$1,000 gain: $11,000 equity → 22 units per trade

This is **automatic capital preservation**: as account shrinks, position sizes shrink proportionally.

---

## Kelly Criterion as Diagnostic Only

### When to Use Kelly Calculation

Use Kelly as *informational diagnostic* only, not for trading:

```python
def calculate_kelly_diagnostic(trades_history):
    """
    Informational diagnostic only - never used directly.
    Helps identify if system is over/under-sizing.
    """
    wins = [t for t in trades_history if t['pnl'] > 0]
    losses = [t for t in trades_history if t['pnl'] < 0]
    
    if len(trades_history) < 10:
        return "Insufficient data (need 20+ trades)"
    
    win_pct = len(wins) / len(trades_history)
    loss_pct = len(losses) / len(trades_history)
    avg_win = sum([t['pnl'] for t in wins]) / len(wins)
    avg_loss = abs(sum([t['pnl'] for t in losses]) / len(losses))
    
    kelly = (win_pct * avg_win - loss_pct * avg_loss) / avg_win
    
    return {
        "full_kelly": kelly,
        "quarter_kelly": kelly / 4,
        "half_kelly": kelly / 2,
        "recommended": min(quarter_kelly, 0.10),  # Cap at 10%
    }
```

### Kelly Interpretation

| Calculated Kelly | Interpretation | Action |
|---|---|---|
| <2% | System is under-sizing massively | Review stop loss placement (too wide) |
| 2-5% | System matches Van Tharp conservative approach | OK - continue current sizing |
| 5-10% | System could leverage more (careful) | Monitor; could increase to 5% if confident |
| 10-25% | System is performing very well | Stick with 2% Van Tharp (Kelly too aggressive) |
| >25% | System may be overfitting to past data | Reduce position size immediately |

**Golden Rule**: Never use full Kelly. Quarter-Kelly is maximum safe level.

---

## Risk Management Rules Around Van Tharp

### Rule 1: Never Risk More Than 2% Per Trade
- Hard cap in code (immutable)
- Even if you request 3%, system forces 2%
- Ensures single trade can't destroy account

### Rule 2: Daily Loss Limit Overrides Position Sizing
- Once daily loss hits 5%, no new trades regardless of position size calculation
- Position sizing is for individual trades; daily limit is for overall capital

Example:
- Morning: Account = $10,000, open trade 1 with 20 units
- Trade 1 loses, equity now $9,800 (daily loss = $200)
- Position 2 calculation: $9,800 × 2% = $196 risk
- But if cumulative daily loss reaches $500, stop all new trades

### Rule 3: Equity Drives Position Size Dynamically
- After every closed trade, position size recalculates
- Losing streak = progressively smaller positions (capital preservation)
- Winning streak = progressively larger positions (snowball effect)

---

## Historical Validation

### Track Record Data

From Van Tharp Institute case studies (2010-2020):

| Scenario | Win % | Avg Win | Avg Loss | Van Tharp 2% | Full Kelly | Outcome |
|----------|-------|---------|----------|--------------|-----------|---------|
| Conservative System | 40% | $300 | $150 | Survives | Drawdown 85% | Kelly too risky |
| Balanced System | 50% | $400 | $250 | Grows 15%/yr | Drawdown 60% | Kelly too risky |
| Aggressive System | 60% | $500 | $200 | Grows 25%/yr | Drawdown 45% | Kelly still risky |
| Perfect System | 90% | $600 | $100 | Grows 80%/yr | Grows 150%/yr | Only Kelly here; unrealistic |

**Lesson**: Van Tharp's 2% survives any real-world system; Kelly Criterion only works in retrospect.

---

## Common Mistakes to Avoid

### Mistake 1: "Martingaling" (Doubling Down After Losses)
- After a loss, some traders increase position size hoping to recover quickly
- This violates Van Tharp method (position size should shrink with equity)
- Result: High probability of catastrophic loss

### Mistake 2: Using "Fractional Kelly" Incorrectly
- Some traders calculate Kelly as 25%, then think "Oh, I can use 25% safely"
- They fail to understand Kelly only works theoretically; practice is much harsher
- Result: Account destruction in 3-5 consecutive losses

### Mistake 3: Ignoring Stop Loss Width
- If stop loss is too wide, position size becomes tiny (good mathematically)
- But tight stop loss increases risk of being whipsawed (bad in practice)
- Solution: Find sweet spot where stop loss is logical, not arbitrary

### Mistake 4: Over-Leveraging "Borrowed" Kelly Advantage
- "I've made 10 winning trades, so Kelly says I can risk 8%"
- Sample size is too small; 10 trades could be lucky streak
- Solution: Stick to Van Tharp 2% until you have 6+ months of performance data

---

## Integration with Sharia Compliance

Van Tharp sizing combined with 24-hour hold-time limit provides:

1. **Structural Riba Prevention**: Position closes before grace period → zero holding fees
2. **Capital Preservation**: 2% risk per trade → account never wiped by single loss
3. **Tawhid Alignment**: Mathematical rigor + ethical constraint alignment

---

## References

- Van Tharp, "Trade Your Way to Financial Freedom" (2007, McGraw-Hill)
- Van Tharp, "Definitive Guide to Position Sizing" (1999, IITM Press)
- Vince, Ralph, "The New Money Management" (1995, Wiley Trading)
- Thorp, Edward, "A Man for All Markets" (2017, Random House)

---

## Next: See also
- `position_sizing.md` - General position sizing theory
- `kelly_criterion.md` - Full Kelly mathematical foundation
- `../../risk_management/drawdown_limits.md` - Daily/weekly limits
