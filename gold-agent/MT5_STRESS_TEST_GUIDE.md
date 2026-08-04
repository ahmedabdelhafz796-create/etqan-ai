# MT5 Connection Reliability Stress Test Guide

## Purpose

Before deploying the gold-agent trading system to live trading, we need to verify that the MT5 broker connection is reliable under stress conditions. This guide walks you through stress-testing the connection with 1000 cycles to measure:

1. **Real success rate** (not optimistic assumptions)
2. **Failure patterns** (clustering by symbol, time, or error type)
3. **Retry logic effectiveness** (does exponential backoff actually work?)
4. **Response time characteristics** (latency under load)
5. **Actionable recommendations** (is the system production-ready?)

---

## Setup: Get Exness Demo Credentials

### Step 1: Create Free Exness Demo Account

1. Visit: https://www.exness.com/
2. Click **"Create Account"** → **"Demo Trading"**
3. Choose **MT5 Platform**
4. Fill in your email
5. Check your email for MT5 account details

You'll receive:
- **Login Number**: (e.g., 123456789)
- **Password**: (e.g., YourPassword)
- **Server**: (e.g., ExnessMT5-Demo or ExnessMT5)

### Step 2: Create `.env` File

Create a file named `.env` in the gold-agent project root:

```bash
# In: gold-agent/.env
MT5_LOGIN=123456789
MT5_PASSWORD=YourPassword
MT5_SERVER=ExnessMT5-Demo
```

**IMPORTANT**: 
- Keep this file private (already in `.gitignore`)
- Never commit `.env` to git
- This is test/demo capital, not production

---

## Installation: Dependencies

Ensure MetaTrader5 Python library is installed:

```bash
pip install MetaTrader5
```

Verify it works:

```bash
python -c "import MetaTrader5; print('✓ MetaTrader5 installed')"
```

---

## Run the Stress Test

### Option A: Quick Test (100 cycles)

```bash
cd gold-agent
python scripts/mt5_connection_stress_test.py --cycles 100 --mode query
```

**Expected time**: ~2-5 minutes  
**Good for**: Quick validation before committing to full 1000-cycle test

### Option B: Full Reliability Test (1000 cycles)

#### Mode 1: Query Mode (Recommended)

Single connection, 1000 sequential queries (faster, tests query reliability):

```bash
python scripts/mt5_connection_stress_test.py --cycles 1000 --mode query
```

**Expected time**: ~15-30 minutes  
**Tests**: Query reliability after connection established

#### Mode 2: Connect Mode (Stricter)

1000 separate connect/disconnect cycles (slower, tests connection establishment):

```bash
python scripts/mt5_connection_stress_test.py --cycles 1000 --mode connect
```

**Expected time**: ~30-60 minutes  
**Tests**: Connection robustness under repeated connect/disconnect stress

### Example Output

```
===== STRESS TEST RESULTS =====
Total Tests: 1000
Successful: 998
Failed: 2
Success Rate: 99.80%

Response Time (successful only):
  Average: 125.43ms
  Min: 45.22ms
  Max: 2341.10ms

Failed Tests Analysis:
  Symbol AAPL not found: 1 occurrences
  Connection timeout: 1 occurrences

Failure Clustering Analysis:
  By Symbol:
    AAPL: 1 failures
    (others): 0 failures
  By Position:
    First 100 cycles: 0 failures
    Middle cycles: 0 failures
    Last 100 cycles: 2 failures

RELIABILITY VERDICT:
  ✅ EXCELLENT: 99.80% success rate
  Acceptable for live trading (very high reliability)
```

---

## Interpret Results

### Success Rate Thresholds

| Rate | Verdict | Status |
|---|---|---|
| ≥ 99.5% | ✅ Excellent | Approved for live trading |
| ≥ 99.0% | ✅ Good | Generally acceptable |
| ≥ 95.0% | ⚠️  Acceptable | Monitor closely; investigate patterns |
| < 95.0% | ❌ Poor | NOT acceptable; needs investigation |

### Common Issues & Fixes

#### Issue 1: Symbol Not Found (AAPL/MSFT)

**Error**: `Symbol AAPL not found`

**Cause**: Exness demo may not have all symbols

**Fix**: 
```python
# Edit test_symbols in mt5_connection_stress_test.py (line ~95)
self.test_symbols = [
    "XAUUSD",  # Always available (gold)
    "EURUSD",  # Always available (forex)
    "GBPUSD",  # Always available (forex)
    # Remove MSFT/AAPL if not in your demo
]
```

#### Issue 2: Authentication Failure

**Error**: `Connection failed: Invalid account or password`

**Fix**:
1. Double-check credentials in `.env`
2. Verify you copied server name exactly (case-sensitive)
3. Verify account is "MT5 Demo", not "WebTrader"

#### Issue 3: Connection Timeout

**Error**: `Connection timeout` or `Network unreachable`

**Cause**: Network issue or MT5 server unavailable

**Fix**:
1. Check your internet connection
2. Try manually connecting via MT5 terminal (if installed)
3. Check Exness status: https://www.exness.com/status

#### Issue 4: High Failure Rate (>5%)

**Action**: Run cluster analysis

```python
# Look for patterns:
# 1. By time: Are failures clustered at start/middle/end?
#    → May indicate connection warmup or saturation
# 2. By symbol: Do certain symbols fail more?
#    → May indicate symbol availability or data issues
# 3. By error: Do specific errors repeat?
#    → May indicate recoverable vs. permanent issues

# If failures cluster at END, connection may be saturating
# → Reduce batch size or add delays between queries
```

---

## After Stress Test: Next Steps

### If Success Rate ≥ 99%

✅ **PASS**: Connection is reliable enough for live trading

**Next**: Proceed to Phase 2 — Execute 5-10 real demo trades (with full audit logging) to verify:
1. Order execution works
2. Settlement happens correctly
3. Sharia gate blocks appropriately
4. Audit trail is captured

### If Success Rate 95-99%

⚠️ **CONDITIONAL PASS**: Acceptable but monitor

**Action**:
1. Identify failure patterns from cluster analysis
2. If failures are random/scattered: Proceed with caution, monitor live
3. If failures cluster (e.g., always symbol X): Investigate root cause
4. Consider reducing batch size or adding retry logic

### If Success Rate < 95%

❌ **FAIL**: Connection not reliable enough

**Action**:
1. Fix the underlying issue (credentials, network, symbol availability)
2. Re-run 100-cycle test to validate fix
3. If success rate improves: Run full 1000-cycle test again
4. If success rate doesn't improve: Investigate with Exness support

---

## Logging Output

### File: `logs/mt5_stress_test_TIMESTAMP.csv`

Detailed CSV log with every test result:

```
cycle_number,timestamp,mode,symbol,success,response_time_ms,error_message,...
1,2026-08-04T12:00:00.123456,query,XAUUSD,True,125.43,,True,...
2,2026-08-04T12:00:01.456789,query,EURUSD,True,118.22,,True,...
3,2026-08-04T12:00:02.789012,query,GBPUSD,True,145.67,,True,...
...
```

**Useful for**:
- Detailed failure analysis
- Latency trending
- Time-series pattern detection

---

## Automation: Run on Schedule

### Background Testing

To run stress test in background and get results periodically:

```bash
# Run every day at 2 AM
0 2 * * * cd /path/to/gold-agent && \
  python scripts/mt5_connection_stress_test.py --cycles 100 >> logs/daily_test.log 2>&1
```

---

## Final Checklist

Before proceeding to live trading:

- [ ] Created `.env` with MT5 credentials
- [ ] Ran stress test (minimum 100 cycles, recommended 1000)
- [ ] Success rate ≥ 99% (or acceptable pattern explanation)
- [ ] Reviewed failure clustering (no concerning patterns)
- [ ] Retry logic triggered correctly (if any failures)
- [ ] Saved CSV log for audit trail
- [ ] Ready to proceed to Phase 2 (demo trades)

---

## Support

If issues arise:

1. **Check `.env`**: Verify credentials match Exness email exactly
2. **Check network**: Ping Exness servers (if possible in your environment)
3. **Check symbol availability**: Try XAUUSD + EURUSD (always available)
4. **Review logs**: Look at CSV for patterns
5. **Exness support**: Contact Exness if account/server issues

---

**Next Phase**: Once stress test passes, execute 5-10 real demo trades with full audit logging.

**Timeline**: Connection stress test → Demo trades → Live signal verification → Production activation
