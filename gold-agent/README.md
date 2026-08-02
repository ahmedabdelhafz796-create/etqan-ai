# Gold Trading Analysis Agent (GTAA)

A **semi-automated, human-supervised** system for analyzing gold market data and producing trading decisions with confidence percentages and explanations.

**Status:** Phase 1 Development (Milestone 1: Alerts-Only System)  
**Language:** English (code), Arabic (alerts, Sharia compliance)  
**Architecture:** Modular Monolith (single operator, no DevOps team)

---

## Quick Start

### Prerequisites
- Python 3.11+
- pip or conda

### Installation

```bash
# 1. Clone repository and navigate to project
cd gold-agent

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys (optional for mock mode)

# 5. Configure application
# config/config.yaml — weights, thresholds, schedule
# config/sharia_rules.yaml — Islamic compliance rules
```

### Run (Offline, No Keys Required)

```bash
# Run complete pipeline once with mock data
python scripts/run_once.py

# Expected output:
# - Decision: BUY/SELL/WAIT
# - Confidence: X%
# - Reason: explanation
# - Audit log: saved to database
```

### Run Tests

```bash
# Unit + integration tests (offline, no keys)
pytest -v

# With coverage report
pytest --cov=src
```

---

## Project Structure

```
gold-agent/
├── MASTER_PLAN.md              # Architecture & decisions (§1-19)
├── BLUEPRINT.md                # Production architecture details
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template

config/
├── config.yaml                 # Main configuration (weights, thresholds)
└── sharia_rules.yaml           # Islamic compliance rules (user-editable)

src/gold_agent/
├── main.py                     # Entry point
├── config.py                   # Config loading & validation
├── state_machine.py            # 4-state FSM (Autonomous/Safe/Emergency/Recovery)
│
├── core/
│   ├── models.py               # Data models (Price, News, Decision, etc.)
│   └── pipeline.py             # Main data→decision pipeline
│
├── data/
│   ├── market.py               # Market data (XAU/USD, DXY, VIX)
│   └── news.py                 # News aggregation (NewsAPI/RSS)
│
├── analysis/
│   ├── indicators.py           # RSI, MACD, Moving Averages
│   └── scoring.py              # Weighted scoring system
│
├── brain/
│   └── llm_brain.py            # Claude API → confidence % + reason
│
├── decision/
│   └── decision_engine.py      # Decision logic (WAIT if confidence < threshold)
│
├── risk/
│   └── risk_gate.py            # Risk veto (position sizing, drawdown limits)
│
├── sharia/
│   └── sharia_gate.py          # Sharia Hard Veto (Islamic compliance)
│
├── notification/
│   └── telegram.py             # Telegram alerts (+ console fallback)
│
├── execution/
│   └── placeholder.py          # Disabled by default; Phase 4
│
├── audit/
│   └── db.py                   # SQLite audit log (every decision/verdict)
│
├── monitoring/
│   └── health.py               # Data health + agent performance tracking
│
└── backtesting/
    └── backtester.py           # Walk-forward backtesting (Phase 3)

scripts/
├── run_once.py                 # One-shot pipeline (no schedule)
└── run_backtest.py             # Backtesting runner (Phase 3)

tests/
└── [unit + integration tests]  # Offline, no API keys required
```

---

## How It Works

### Data Flow (§6 MASTER_PLAN)

```
Market Data (XAU/USD, DXY)  ─┐
News (NewsAPI/RSS)           ├─→ Indicators (RSI/MACD/MA)
                              │
                         Scoring (weighted)
                              │
                         ┌────┴────┐
                         │          │
                 Confidence < 50%?  ┌─ LLM Brain (Claude API)
                   │ YES → WAIT        │
                   │ NO  → merge scores
                         │
                    Risk Gate ────┐
                    (veto)        │
                         │        │
                  Sharia Gate ────┴─→ Telegram Alert
                   (Hard Veto)         │
                                  Audit Log ✓
```

### Decision Output

For each analysis:

```json
{
  "action": "BUY",
  "confidence": 72,
  "reason": "RSI oversold (28) + MACD bullish crossover + 50/200 MA aligned. News sentiment mixed. Risk gate passed. Sharia gate passed.",
  "timestamp": "2026-08-02T09:00:00Z",
  "indicators": {
    "rsi": 28,
    "macd": "bullish",
    "ma_short": 2050,
    "ma_long": 2045
  }
}
```

### State Machine (§5.1 MASTER_PLAN)

Four operational states with event-driven transitions:

| State | Behavior | Exit |
|-------|----------|------|
| **Autonomous** | Normal operation; decisions acted on | Escalation event |
| **Safe Mode** | New trades blocked; existing managed | Manual review OK |
| **Emergency** | All trades stopped; human alerted | Manual recovery only |
| **Manual Recovery** | Full stop; waits for human approval | Manual approval required |

Escalation triggers:
- Data quality < 95% → Safe Mode
- Model conflict (confidence divergence) → Safe Mode
- Drawdown > 15% → Emergency
- Connection loss > 5 min → Emergency
- VIX spike > 30% → Emergency

### Kill Switch

**100% required.** Execution module:
- OFF by default
- Requires explicit activation after testing
- Armed (stopping trades) when not tested
- Respects all risk limits

---

## Configuration

### Main Config (`config/config.yaml`)

Key sections:

```yaml
indicators:
  rsi.period: 14
  macd: 12/26/9
  moving_averages: 50/200

scoring:
  weights:
    rsi: 0.30
    macd: 0.35
    moving_average: 0.35
  confidence_threshold_act: 65

risk_gate:
  max_drawdown_percent: 5
  max_position_size_percent: 2
  market_volatility_limit_vix: 40

sharia:
  school: "hanafi"  # Configurable per user's fatwa
  rules_file: "config/sharia_rules.yaml"

state_machine:
  initial_state: "autonomous"
  # Define transition rules with thresholds
```

### Sharia Rules (`config/sharia_rules.yaml`)

User-editable Islamic compliance rules:

- **Contract Type:** Spot/forward only (no futures/options/CFDs)
- **Overnight Interest:** Zero swap charges
- **Leverage:** 1:1 max (no leverage allowed)
- **Borrowing:** Prohibited
- **Taqābuḍ:** Spot settlement required
- **Audit:** Sharia-specific logging

Default: **Hanafi** school. Replace with your Sharia scholar's fatwa.

---

## Phase Roadmap

| Phase | Duration | Contents | Output |
|-------|----------|----------|--------|
| **1 (Current)** | 1-2 weeks | Data agents · Indicators · Scoring · Decisions | Alerts only; no execution |
| **2** | ~1 month | LLM brain (Claude API) · Macro analysis · Correlation | Confidence % + reason |
| **3** | 2+ months | Self-learning · Backtesting · Risk models | Performance metrics + strategy refinement |
| **4** | Optional | Execution · Broker integration · Auto-trading | Live trading (after months of alerts) |

---

## Day-One Requirements (§11 MASTER_PLAN)

To run with live data:

1. **Anthropic API Key** — Claude API access
2. **Claude Pro** — Required for development
3. **Market Data** — Twelve Data OR Alpha Vantage
4. **News** — NewsAPI OR RSS
5. **Telegram** — Bot token + chat ID
6. **GitHub** — Already available

---

## Testing

### Unit Tests (Offline)

```bash
pytest tests/ -v
```

Tests cover:
- Indicator calculations (RSI, MACD, MA)
- Scoring logic (weighted, aggregation)
- Decision engine (threshold, WAIT condition)
- Risk gate (position sizing, drawdown)
- Sharia gate (rule enforcement)
- State machine (transitions, escalations)
- Audit logging (database writes)

### Integration Tests

```bash
python scripts/run_once.py
```

Verifies:
- Full pipeline execution (data → decision)
- WAIT correctly emitted when confidence < threshold
- Risk gate veto blocks decision
- Sharia gate hard veto blocks decision
- Audit log written
- Telegram alert (or console fallback)
- State machine transitions on demand

---

## Deployment

### Local (Phase 1-2)

```bash
python scripts/run_once.py  # Manual trigger
```

Or scheduled:

```bash
# Edit config.yaml: deployment.schedule_cron = "0 9 * * *"
# Run via cron/task scheduler on your machine
```

### GitHub Actions (Phase 2+)

```bash
# Enable in config.yaml: deployment.github_actions.enabled = true
# Workflow file: .github/workflows/gold-agent.yml
# Runs on schedule or webhook
```

### VPS (Phase 3+)

- PostgreSQL instead of SQLite
- Permanent uptime
- Better monitoring

---

## Disclaimer

⚠️ **IMPORTANT**

1. **This is NOT financial advice.** Decisions are yours; Claude is a tool only.
2. **Never trade with capital you can't afford to lose.**
3. **Test thoroughly** before enabling execution.
4. **Sharia compliance is YOUR responsibility.** Consult your Sharia scholar.
5. **No system is 100% accurate.** Even Citadel & Renaissance lose trades.
6. **Kill switch is MANDATORY.** Execution OFF by default.

---

## References

- **MASTER_PLAN.md** — Architecture decisions (§1-19)
- **BLUEPRINT.md** — Detailed production design
- **config.yaml** — Runtime configuration
- **config/sharia_rules.yaml** — Islamic compliance rules

---

## Support

For issues, questions, or contributions:
- See MASTER_PLAN.md for design rationale
- Check config files for tuning parameters
- Run tests to verify functionality
- Review audit logs for decision explanations

---

**Last Updated:** August 2, 2026  
**Version:** Phase 1 - Milestone 1 (Alerts-Only)  
**Maintained by:** Gold Trading Analysis Agent Team
