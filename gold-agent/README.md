# Gold Trading Analysis Agent 🥇📊

[![Tests](https://img.shields.io/badge/tests-8%2F8%20passing-brightgreen)](tests/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/status-Phase%201%20Complete-green)](PHASE1_STATUS.md)

A sophisticated **semi-autonomous trading analysis system** for gold (XAU/USD) that leverages multi-agent AI, technical analysis, macro-economic indicators, and Islamic finance compliance.

**⚠️ DISCLAIMER:** This system is for educational and analysis purposes only. Trading involves substantial risk of loss. Never trade with money you cannot afford to lose. Past performance does not guarantee future results.

---

## 🎯 Project Goals

1. **Analyze** gold market data using technical indicators, macro analysis, and sentiment
2. **Generate decisions** with confidence scores and detailed reasoning
3. **Respect risk limits** via the Risk Gate (position sizing, volatility checks)
4. **Ensure compliance** via the Sharia Gate (Islamic finance rules)
5. **Enable learning** from trading patterns and performance metrics
6. **Prevent accidents** with the Kill Switch (execution disabled by default)

---

## ✨ Key Features

### 🧠 Intelligent Analysis
- **Technical Indicators:** RSI, MACD, Moving Averages
- **Macro Analysis:** Bond yields, Dollar Index (DXY), VIX
- **News Sentiment:** Market-moving news with sentiment scoring
- **LLM Brain:** Claude API for nuanced market interpretation
- **Ensemble Voting:** 5 independent signal types with weighted consensus

### 🛡️ Risk Management
- **Kill Switch:** Execution disabled by default (must be consciously enabled)
- **Position Sizing:** Dynamic sizing based on capital and risk limits
- **Daily Loss Limits:** Automatic stop-trading on daily loss threshold
- **Drawdown Limits:** Protection against sustained losses
- **Volatility Checks:** Reduced position sizing in high volatility

### 🕌 Sharia Compliance
- **Hard Veto:** Sharia Gate blocks non-compliant trades (cannot be overridden)
- **Configurable Rules:** Custom rules per Islamic jurisprudential school
- **Swap Policy:** Overnight interest handling per Sharia rules
- **Settlement Requirements:** Taqābuḍ (spot settlement) verification
- **Audit Log:** Separate Sharia compliance audit trail

### 📊 Self-Management
- **Automatic Tuning:** Parameters adjust based on recent performance
- **Regime Detection:** Strategy selection based on market conditions
- **Performance Monitoring:** Continuous alerts for key metrics
- **Backtesting:** Systematic parameter optimization on historical data

### 🔔 Notifications
- **Telegram Integration:** Real-time alerts for decisions and emergencies
- **Console Fallback:** Works without Telegram (development mode)
- **Arabic Support:** Notifications available in English and Arabic
- **Multilingual:** State changes and alerts in native language

### 📈 Data Pipeline
- **Real Market Data:** TwelveData or AlphaVantage APIs
- **News Integration:** NewsAPI or RSS feeds
- **Robust Fallbacks:** Mock data when APIs unavailable
- **Caching:** Resilience to temporary API outages

---

## 📋 Architecture

### 5-Tier Implementation

| Tier | Component | Purpose | Status |
|------|-----------|---------|--------|
| **1** | Execution | Order placement, broker adapters, position management | ✅ Complete |
| **2** | Learning | Pattern extraction, trade statistics, recommendations | ✅ Complete |
| **3** | Validation | Backtesting, performance validation, criteria checking | ✅ Complete |
| **4** | Analysis | Volatility adjustment, regime detection, ensemble voting | ✅ Complete |
| **5** | Self-Mgmt | Parameter tuning, strategy selection, risk adjustment | ✅ Complete |

### 38 Implemented Modules

**Core:** Models, Pipeline, Configuration, State Machine  
**Data:** Market providers (TwelveData, AlphaVantage, Mock), News (NewsAPI, RSS, Mock)  
**Analysis:** Indicators, Scoring, Macro Agent, Correlation Agent  
**Advanced:** Volatility Adjuster, Regime Detector, Signal Ensemble, Feature Importance  
**Decision:** LLM Brain (Claude API), Fallback Engine, Hybrid Brain  
**Gates:** Risk Gate, Sharia Gate  
**Execution:** Order/Position/Capital Managers, Trade Lifecycle, Brokers (Mock, MT5, OANDA)  
**Support:** Notifications (Telegram/Console), Audit Log, Monitoring, Self-Management

---

## 🚀 Quick Start

### Installation
```bash
# Clone repository
git clone https://github.com/ahmedabdelhafz796-create/etqan-ai.git
cd etqan-ai/gold-agent

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Verify Installation
```bash
# Run integration tests (should pass 8/8)
python -m pytest tests/test_integration.py -v

# Run one analysis cycle
python scripts/run_once.py

# Expected output: 
# 📈 BUY | Confidence: 75% | Reason: Fallback rule engine...
```

### Configuration (Optional)
```bash
# Edit configuration for testing
nano config/config.yaml

# Key settings:
# - data.market_provider: "mock" (testing) or "twelve_data"
# - execution.broker_type: "mock" (testing) or "mt5"/"oanda"
# - execution.kill_switch_armed: true (NEVER CHANGE)
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [MASTER_PLAN.md](MASTER_PLAN.md) | Architectural blueprint and design decisions |
| [PHASE1_STATUS.md](PHASE1_STATUS.md) | Phase 1 implementation status and validation |
| [IMPLEMENTATION_PROGRESS.md](IMPLEMENTATION_PROGRESS.md) | Current progress and production readiness |
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | Step-by-step production deployment instructions |
| [ENGINEERING_AUDIT_REPORT.md](ENGINEERING_AUDIT_REPORT.md) | Complete implementation inventory and gaps |

---

## 🔧 Configuration

### Minimal Configuration (Testing)
```yaml
# config/config.yaml
data:
  market_provider: "mock"  # No API keys needed
  news_provider: "mock"    # No API keys needed

execution:
  broker_type: "mock"      # Simulated broker
  kill_switch_armed: true  # CRITICAL: execution disabled

scoring:
  confidence_threshold_wait: 60  # Only act on high confidence
```

### Full Configuration (Production)
```yaml
data:
  market_provider: "twelve_data"  # Real market data
  news_provider: "newsapi"        # Real news sentiment

execution:
  broker_type: "mt5"  # or "oanda"
  kill_switch_armed: true  # Always start disabled

notification:
  telegram_enabled: true
  telegram_bot_token: "${TELEGRAM_BOT_TOKEN}"  # From .env
  
risk:
  daily_loss_limit_percent: 3    # Stop trading after 3% daily loss
  max_drawdown_percent: 5        # Emergency if 5% drawdown
  max_position_size_percent: 2   # Never risk more than 2%
```

---

## 🧪 Testing

### Integration Tests
```bash
# Run all tests (8/8 passing)
python -m pytest tests/test_integration.py -v

# Test specific component
python -m pytest tests/test_integration.py::TestIntegration::test_market_data_fetch -v
```

### Manual Testing
```bash
# Test market data
python -c "from gold_agent.data.market import MockMarketDataProvider; print('✓ OK')"

# Test indicators
python -c "from gold_agent.analysis.indicators import IndicatorEngine; print('✓ OK')"

# Run analysis
python scripts/run_once.py
```

---

## 📊 Usage

### Single Analysis Cycle
```bash
python scripts/run_once.py
```

### Continuous Operation (Production)
```bash
python scripts/run_continuous.py
# Runs every 60 minutes (configurable)
# Sends Telegram notifications
# Logs activity to audit database
```

---

## 🔐 Security

### Kill Switch
- ✅ **Enabled by default:** Execution always disabled on startup
- ✅ **Explicit enablement:** Must call `agent.execution.enable()` after validation
- ✅ **No automatic trading:** All trades require human review initially

### Risk Controls
- ✅ Position size limited to 2% of capital
- ✅ Daily loss limit (3%) stops new trades
- ✅ Drawdown limit (5%) triggers emergency state
- ✅ Volatility checks reduce position size in high VIX

---

## 📈 Production Readiness

### Current Status: **81% Ready**

| Category | Score | Details |
|----------|-------|---------|
| Architecture | 95% | Sound design, all components implemented |
| Implementation | 95% | 38/38 modules complete |
| Testing | 85% | 8/8 integration tests passing |
| Configuration | 80% | Parameterized, needs API keys |
| Monitoring | 85% | Health checks + notifications |
| Documentation | 85% | MASTER_PLAN, PHASE1_STATUS, Deployment Guide |
| Deployment | 40% | Not deployed, VPS setup needed |

### Before Live Trading
- [ ] Real broker credentials (MT5 or OANDA)
- [ ] Paper trading validation (7+ days)
- [ ] Market data API keys configured
- [ ] Telegram bot token configured
- [ ] VPS provisioned and configured
- [ ] PostgreSQL database initialized
- [ ] Monitoring and alerting setup
- [ ] Emergency procedures tested

---

## 🗺️ Roadmap

### Phase 1: ✅ Complete
- Core architecture and components
- Technical and macro analysis
- Risk and Sharia gates
- Mock data pipeline
- Backtesting framework

### Phase 2: 🔄 In Progress
- Real market data providers ✅
- Claude API integration ✅
- Telegram notifications ✅
- Broker adapter implementation ✅

### Phase 3: 📋 Planned
- Production deployment
- Extended validation with real data
- Portfolio-level risk management
- Machine learning signal enhancement

---

## 📊 Project Statistics

- **Lines of Code:** 3,500+
- **Modules:** 38
- **Components:** 22 major systems
- **Test Cases:** 8 integration tests (100% passing)
- **Configuration Parameters:** 150+
- **Supported Languages:** English, Arabic

---

## 📞 Support

### Documentation
- **Setup Issues:** See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Technical Details:** See [ENGINEERING_AUDIT_REPORT.md](ENGINEERING_AUDIT_REPORT.md)
- **Architecture:** See [MASTER_PLAN.md](MASTER_PLAN.md)

### Configuration
- **Main:** [config/config.yaml](config/config.yaml) (150+ parameters)
- **Islamic:** [config/sharia_rules.yaml](config/sharia_rules.yaml)

---

## ⚖️ Legal & Disclaimer

**This system is provided for educational purposes only.**

- **Not Financial Advice:** This is not a financial advisor.
- **Risk Warning:** Trading involves substantial risk of loss.
- **No Guarantees:** Past performance does not guarantee future results.
- **Sharia Compliance:** Configure based on YOUR fatwa, not defaults.
- **User Liability:** You assume all responsibility for trades executed.

**By using this software, you accept these risks.**

---

## 📝 License

MIT License - See LICENSE file for details

---

## 👤 Author

Built by Ahmed Abdelhafz (أحمد عبد الحافظ)  
for the etqan-ai project

---

## 🙏 Acknowledgments

- **Anthropic:** Claude AI and Claude API
- **Twelve Data:** Market data provider
- **Alpha Vantage:** Alternative market data
- **NewsAPI:** News sentiment data
- **python-telegram-bot:** Notification delivery
- **Open Source Community:** Flask, SQLAlchemy, pytest, and many others

---

**Status:** Phase 1 Complete. Ready for Phase 2 real data testing.

🚀 **Next: Deploy to VPS → Configure real APIs → Paper trading validation**
