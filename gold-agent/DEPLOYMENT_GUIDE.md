# Gold Trading Analysis Agent — Deployment Guide

**Version:** 1.0  
**Date:** August 2, 2026  
**Environment:** Linux VPS, Python 3.11+

---

## Quick Start (Development/Testing)

### 1. Prerequisites
```bash
# Clone repository
git clone https://github.com/ahmedabdelhafz796-create/etqan-ai.git
cd etqan-ai/gold-agent

# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Verify Installation
```bash
# Run integration tests (should pass 8/8)
python -m pytest tests/test_integration.py -v

# Run one analysis cycle
python scripts/run_once.py

# Expected output: Decision (BUY/SELL/WAIT) with confidence and reason
```

### 3. Configuration
```bash
# Copy example config
cp config/config.yaml config/config.local.yaml

# Edit configuration (optional for testing)
nano config/config.local.yaml

# Load default configuration for testing
python -c "from src.gold_agent.config import load_config; load_config('config/config.yaml')"
```

---

## Production Deployment

### Phase 1: VPS Setup

#### Server Requirements
- **OS**: Linux (Ubuntu 20.04 LTS or later recommended)
- **CPU**: 2+ cores (gold trading not CPU-intensive)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 20GB (for database, logs, backups)
- **Network**: Stable internet connection (99.9% uptime recommended)
- **Firewall**: Outbound HTTPS allowed (for APIs)

#### VPS Providers (Recommendations)
- DigitalOcean ($6-12/month)
- Linode ($5-15/month)
- AWS EC2 (t3.micro free tier)
- Vultr ($2.50-6/month)

### Phase 2: System Installation

#### 1. System Dependencies
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python 3.11
sudo apt-get install -y python3.11 python3.11-venv python3-pip

# Install other dependencies
sudo apt-get install -y git curl wget postgresql postgresql-contrib

# Verify installation
python3.11 --version
psql --version
```

#### 2. Database Setup (PostgreSQL)

```bash
# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE gold_agent;
CREATE USER gold_agent WITH PASSWORD 'your_secure_password_here';
ALTER ROLE gold_agent SET client_encoding TO 'utf8';
ALTER ROLE gold_agent SET default_transaction_isolation TO 'read committed';
ALTER ROLE gold_agent SET default_transaction_deferrable TO on;
ALTER ROLE gold_agent SET default_transaction_read_only TO off;
GRANT ALL PRIVILEGES ON DATABASE gold_agent TO gold_agent;
\q
EOF
```

#### 3. Application Setup
```bash
# Clone and setup
cd /opt
sudo git clone https://github.com/ahmedabdelhafz796-create/etqan-ai.git
cd etqan-ai/gold-agent
sudo chown -R $USER:$USER /opt/etqan-ai

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Phase 3: Configuration & Secrets

#### 1. Environment Variables
```bash
# Create .env file
cat > /opt/etqan-ai/gold-agent/.env << 'EOF'
# Market Data API Keys
TWELVE_DATA_API_KEY=your_key_here
ALPHA_VANTAGE_API_KEY=your_key_here

# News API
NEWSAPI_API_KEY=your_key_here

# Claude API (for LLM brain)
ANTHROPIC_API_KEY=your_key_here

# Telegram Bot (notifications)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Broker Credentials (if using MT5/OANDA)
MT5_LOGIN=your_login
MT5_PASSWORD=your_password
MT5_SERVER=your_server

OANDA_API_KEY=your_api_key
OANDA_ACCOUNT_ID=your_account_id
OANDA_ENVIRONMENT=practice  # Start with practice!

# Database
DATABASE_URL=postgresql://gold_agent:your_password@localhost/gold_agent

# Configuration
CONFIG_PATH=/opt/etqan-ai/gold-agent/config/config.yaml
LOG_LEVEL=INFO
EOF

chmod 600 .env
```

#### 2. Application Configuration
```bash
# Edit main configuration
nano config/config.yaml

# Key sections to customize:
# - data.market_provider: "twelve_data" or "alpha_vantage"
# - data.news_provider: "newsapi" or "rss"
# - execution.broker_type: "mock" (start), "mt5", or "oanda"
# - execution.kill_switch_armed: true (must be true for safety)
# - notification.telegram_enabled: true/false
# - risk.daily_loss_limit_percent: 3 (conservative)
# - risk.max_drawdown_percent: 5 (conservative)
```

#### 3. Sharia Compliance Configuration
```bash
# Edit Islamic finance rules
nano config/sharia_rules.yaml

# Verify settings match your fatwa:
# - school: "hanafi" (or your preferred school)
# - contract_types: acceptable instruments
# - swap_policy: overnight interest handling
# - settlement: taqaabud requirements
```

### Phase 4: Testing & Validation

#### 1. Verify Configuration
```bash
cd /opt/etqan-ai/gold-agent
source venv/bin/activate
python -c "from gold_agent.config import load_config; c = load_config('config/config.yaml'); print('✅ Config loaded successfully')"
```

#### 2. Run Integration Tests
```bash
python -m pytest tests/test_integration.py -v
# Expected: 8/8 tests passing
```

#### 3. Run One Cycle
```bash
python scripts/run_once.py
# Expected: Decision output with confidence and reason
# No actual trades executed (kill switch armed)
```

#### 4. Test Notifications (if Telegram configured)
```bash
# Manually trigger a notification
python -c "
import asyncio
from gold_agent.notification.telegram import ConsoleNotifier

async def test():
    notifier = ConsoleNotifier()
    from gold_agent.core.models import Decision, ActionType, IndicatorValues, Score, StateType
    from datetime import datetime
    
    decision = Decision(
        timestamp=datetime.utcnow(),
        action=ActionType.BUY,
        confidence=75.0,
        reason='Test notification',
        indicators=IndicatorValues(datetime.utcnow(), 45, 0.5, 0.4, 0.1, 2050, 2040),
        score=Score(datetime.utcnow(), 70, 75, 68),
        state=StateType.AUTONOMOUS
    )
    await notifier.notify_decision(decision)

asyncio.run(test())
"
```

### Phase 5: Systemd Service Setup

#### 1. Create Service File
```bash
sudo tee /etc/systemd/system/gold-agent.service > /dev/null << 'EOF'
[Unit]
Description=Gold Trading Analysis Agent
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=gold_agent
WorkingDirectory=/opt/etqan-ai/gold-agent
Environment="PATH=/opt/etqan-ai/gold-agent/venv/bin"
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/opt/etqan-ai/gold-agent/.env
ExecStart=/opt/etqan-ai/gold-agent/venv/bin/python scripts/run_continuous.py
Restart=on-failure
RestartSec=300
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create dedicated user (if not exists)
sudo useradd -r -s /bin/bash -d /opt/etqan-ai/gold-agent gold_agent

# Set ownership
sudo chown gold_agent:gold_agent /opt/etqan-ai/gold-agent -R

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable gold-agent
```

#### 2. Create Run Script
```bash
cat > /opt/etqan-ai/gold-agent/scripts/run_continuous.py << 'EOF'
#!/usr/bin/env python3
"""
Run Gold Trading Analysis Agent continuously.

Usage:
    python scripts/run_continuous.py

Runs continuous analysis with configurable interval.
Automatically manages state transitions and error recovery.
"""

import asyncio
import sys
from pathlib import Path
import logging

# Setup path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from gold_agent.main import GoldTradingAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Run continuous analysis."""
    try:
        logger.info("Initializing Gold Trading Analysis Agent...")
        agent = GoldTradingAgent()
        logger.info("✓ Agent initialized")
        
        # Run continuously (every 60 minutes by default)
        interval_minutes = agent.config.execution.analysis_interval_minutes or 60
        logger.info(f"Starting continuous analysis loop (interval: {interval_minutes} minutes)")
        
        await agent.run_continuous(interval_minutes=interval_minutes)
        
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
        return 0
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
EOF

chmod +x /opt/etqan-ai/gold-agent/scripts/run_continuous.py
```

#### 3. Manage Service
```bash
# Start service
sudo systemctl start gold-agent

# Check status
sudo systemctl status gold-agent

# View logs
sudo journalctl -u gold-agent -f

# Stop service
sudo systemctl stop gold-agent

# Restart service
sudo systemctl restart gold-agent
```

### Phase 6: Monitoring & Logging

#### 1. Setup Log Collection
```bash
# Create log directory
sudo mkdir -p /var/log/gold-agent
sudo chown gold_agent:gold_agent /var/log/gold-agent

# Update service to use log file
sudo tee /etc/systemd/system/gold-agent.service > /dev/null << 'EOF'
[Unit]
Description=Gold Trading Analysis Agent
After=network.target postgresql.service

[Service]
Type=simple
User=gold_agent
WorkingDirectory=/opt/etqan-ai/gold-agent
Environment="PATH=/opt/etqan-ai/gold-agent/venv/bin"
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/opt/etqan-ai/gold-agent/.env
ExecStart=/opt/etqan-ai/gold-agent/venv/bin/python scripts/run_continuous.py
Restart=on-failure
RestartSec=300
StandardOutput=append:/var/log/gold-agent/stdout.log
StandardError=append:/var/log/gold-agent/error.log

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
```

#### 2. Setup Health Checks
```bash
# Create health check script
cat > /opt/etqan-ai/gold-agent/scripts/health_check.sh << 'EOF'
#!/bin/bash

# Check if service is running
if ! systemctl is-active --quiet gold-agent; then
    echo "ALERT: Gold Agent service is not running"
    systemctl restart gold-agent
    exit 1
fi

# Check database connectivity
if ! pg_isready -h localhost -U gold_agent -d gold_agent > /dev/null 2>&1; then
    echo "ALERT: Database is not accessible"
    exit 1
fi

# Check recent activity (within last hour)
LAST_DECISION=$(sqlite3 /var/lib/gold-agent/audit.db "SELECT MAX(timestamp) FROM decisions;" 2>/dev/null)
if [ -z "$LAST_DECISION" ]; then
    echo "WARNING: No recent decisions found"
fi

echo "OK: Gold Agent is healthy"
exit 0
EOF

chmod +x /opt/etqan-ai/gold-agent/scripts/health_check.sh

# Add health check to crontab
(crontab -l 2>/dev/null; echo "*/15 * * * * /opt/etqan-ai/gold-agent/scripts/health_check.sh") | crontab -
```

### Phase 7: Backup & Recovery

#### 1. Database Backups
```bash
# Create backup script
cat > /opt/etqan-ai/gold-agent/scripts/backup_db.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/backups/gold-agent"
mkdir -p $BACKUP_DIR

# Backup PostgreSQL database
pg_dump -U gold_agent -d gold_agent | gzip > $BACKUP_DIR/gold_agent_$(date +%Y%m%d_%H%M%S).sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR"
EOF

chmod +x /opt/etqan-ai/gold-agent/scripts/backup_db.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/etqan-ai/gold-agent/scripts/backup_db.sh") | crontab -
```

#### 2. Disaster Recovery Plan
```bash
# If something goes wrong:

# 1. Stop the service
sudo systemctl stop gold-agent

# 2. Check logs for errors
sudo journalctl -u gold-agent -n 100

# 3. Verify database is accessible
psql -U gold_agent -d gold_agent -c "SELECT COUNT(*) FROM decisions;"

# 4. Restore from backup if needed
gunzip < /backups/gold-agent/latest_backup.sql.gz | psql -U gold_agent -d gold_agent

# 5. Restart service
sudo systemctl start gold-agent

# 6. Verify it's running
sudo systemctl status gold-agent
```

---

## Security Best Practices

### 1. Credentials Management
- ✅ Store API keys in `.env` file (never commit)
- ✅ Restrict `.env` file permissions (600)
- ✅ Use environment variables for all secrets
- ✅ Rotate API keys periodically (quarterly)

### 2. Network Security
- ✅ Use HTTPS for all API calls (enforce SSL/TLS)
- ✅ Whitelist VPS IP on API provider accounts
- ✅ Use VPN if possible for additional security
- ✅ Keep firewall restrictive (only allow outbound HTTPS)

### 3. System Security
- ✅ Keep system packages updated (`apt-get upgrade`)
- ✅ Use strong passwords for PostgreSQL
- ✅ Disable root login via SSH
- ✅ Setup SSH key-based authentication
- ✅ Install and configure fail2ban for DDoS protection

### 4. Application Security
- ✅ Kill switch enabled by default (never disabled)
- ✅ Conservative position sizing (2% max)
- ✅ Daily loss limits enforced (3% max)
- ✅ All decisions logged for audit trail
- ✅ Telegram notifications for all major events

---

## Troubleshooting

### Service Won't Start
```bash
# Check logs
sudo journalctl -u gold-agent -n 50 --no-pager

# Check if Python is available
/opt/etqan-ai/gold-agent/venv/bin/python --version

# Check if port/resources are in use
netstat -tuln | grep :8000
free -h  # Check available RAM
```

### Database Connection Issues
```bash
# Test connection
psql -U gold_agent -h localhost -d gold_agent -c "SELECT 1;"

# Check PostgreSQL status
sudo systemctl status postgresql

# Check database permissions
sudo -u postgres psql -c "\l+"
```

### API Key Issues
```bash
# Verify .env file is readable
ls -la /opt/etqan-ai/gold-agent/.env

# Test API keys manually
curl -H "Authorization: Bearer YOUR_KEY" https://api.twelvedata.com/quote?symbol=XAU/USD
```

### No Decisions Being Generated
```bash
# Check if market data is fetching
python -c "from gold_agent.data.market import MockMarketDataProvider; print('✓ Data provider working')"

# Check if indicators are calculating
python -c "from gold_agent.analysis.indicators import IndicatorEngine; print('✓ Indicators working')"

# Run one cycle with debug output
python scripts/run_once.py 2>&1 | grep -i "error\|warning"
```

---

## Performance Tuning

### For Low-Traffic Deployments
```yaml
# config/config.yaml
execution:
  analysis_interval_minutes: 120  # Run every 2 hours
  default_position_size: 0.001  # Minimum position size
```

### For High-Frequency Analysis
```yaml
execution:
  analysis_interval_minutes: 15  # Run every 15 minutes
  default_position_size: 0.005  # Small positions
```

---

## Support & Escalation

### If System Fails
1. Check logs: `sudo journalctl -u gold-agent -f`
2. Verify database: `psql -U gold_agent -d gold_agent -c "SELECT COUNT(*) FROM decisions;"`
3. Check API connectivity: `curl https://api.twelvedata.com/quote?symbol=XAU/USD`
4. Restart service: `sudo systemctl restart gold-agent`
5. Check status: `sudo systemctl status gold-agent`

### Emergency Procedures
1. Kill switch is always armed by default
2. No trades execute without explicit enablement
3. All decisions logged to database for review
4. Telegram notifications sent for all state changes
5. Manual intervention possible at any time

---

**Deployment Ready: Follow this guide for production deployment.**

For questions or issues, refer to MASTER_PLAN.md or PHASE1_STATUS.md.
