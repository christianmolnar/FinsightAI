# Configuration Setup Guide

## Overview

The autonomous trader uses a **hybrid configuration approach**:
- **YAML file** (`trading_config.yaml`) - Trading parameters, committed to git
- **.env file** - Secrets (API keys), **NEVER committed to git**

This keeps your secrets safe while allowing version control of trading parameters.

---

## Quick Setup (5 minutes)

### Step 1: Copy the .env template
```bash
cd backend
cp .env.example .env
```

### Step 2: Get your Alpaca API keys

1. Go to https://alpaca.markets/
2. Sign up (free for paper trading)
3. Navigate to "Your API Keys" section
4. Generate **Paper Trading** keys (not live keys!)
5. Copy the API Key and Secret Key

### Step 3: Edit your .env file

```bash
nano .env  # or use your favorite editor
```

Add your Alpaca paper trading keys:
```bash
ALPACA_PAPER_API_KEY=PKxxxxxxxxxxxxxxxxxxxxx
ALPACA_PAPER_SECRET_KEY=yyyyyyyyyyyyyyyyyyyyyyyy
```

**IMPORTANT**: 
- Use PAPER keys, not LIVE keys
- NEVER commit this file to git
- `.gitignore` already protects it

### Step 4: Test configuration loading

```bash
cd backend
python config/config_loader.py
```

You should see:
```
Configuration loaded successfully!
Paper trading: True
Position size: 10.0%
Max positions: 5
Alpaca credentials loaded: True
```

---

## Configuration Files

### 1. `config/trading_config.yaml` ✅ Safe to commit

Contains all trading parameters:
- Position sizing
- Risk limits
- Entry/exit rules
- Technical filters
- Strategy parameters

**You can edit this file** and commit changes to git.

### 2. `backend/.env` ❌ NEVER commit

Contains secrets:
- API keys
- Database passwords
- Notification credentials

**This file is in `.gitignore`** - it will never be committed.

### 3. `backend/.env.example` ✅ Safe to commit

Template showing what secrets are needed. Contains NO actual secrets.

---

## Usage in Code

### Import configuration
```python
from config.config_loader import config

# Access trading parameters
position_size = config.trading.position_size_pct  # 0.10 (10%)
max_positions = config.risk.max_positions  # 5
profit_target = config.trading.profit_target_pct  # 12.0

# Access secrets (from .env)
api_key, secret_key = config.get_alpaca_credentials()

# Check environment
if config.trading.paper_trading:
    print("Running in PAPER TRADING mode")
```

### Modify trading parameters
Edit `config/trading_config.yaml`:
```yaml
trading:
  position_size_pct: 0.05  # Change from 10% to 5%
  profit_target_pct: 15  # Change from 12% to 15%
```

Configuration reloads automatically when you restart the bot.

---

## Parameter Reference

### Key Trading Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `position_size_pct` | 0.10 | 0.01-0.25 | Percentage of portfolio per trade |
| `max_positions` | 5 | 1-10 | Maximum open positions |
| `profit_target_pct` | 12 | 5-25 | Take profit percentage |
| `stop_loss_pct` | 5 | 3-10 | Stop loss percentage |
| `min_confidence` | 75 | 50-95 | Minimum signal confidence |

### Risk Management

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `daily_loss_limit_pct` | 3 | 1-5 | Daily loss before pause |
| `max_drawdown_pct` | 15 | 5-25 | Max drawdown before pause |
| `consecutive_loss_limit` | 5 | 3-10 | Consecutive losses before pause |
| `vix_threshold` | 25 | 15-40 | VIX level to reduce positions |
| `min_cash_reserve` | 1000 | 500-5000 | Minimum cash to keep |

---

## Security Best Practices

### ✅ DO:
- Use paper trading keys initially
- Keep `.env` file local only
- Use `.env.example` as template
- Commit `trading_config.yaml` changes
- Review config before deploying

### ❌ DON'T:
- Commit `.env` file
- Share API keys in chat/email
- Use live trading keys in development
- Hard-code secrets in Python files
- Push secrets to GitHub

---

## Environment Variables Reference

### Required (Paper Trading)
```bash
ALPACA_PAPER_API_KEY=your_paper_key
ALPACA_PAPER_SECRET_KEY=your_paper_secret
DATABASE_URL=postgresql://user:pass@localhost:5432/finsight_db
```

### Optional (Notifications)
```bash
# Email alerts
EMAIL_ENABLED=true
EMAIL_FROM=alerts@yourdomain.com
EMAIL_TO=your_email@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Slack alerts
SLACK_ENABLED=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# SMS alerts (Twilio)
SMS_ENABLED=true
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_FROM_NUMBER=+1234567890
TWILIO_TO_NUMBER=+1234567890
```

---

## Troubleshooting

### "Configuration error: Alpaca credentials not found"
- Check `.env` file exists in `backend/` directory
- Verify keys are correctly set (no spaces, quotes)
- Run `python config/config_loader.py` to test

### "ValueError: Strategy weights must sum to 1.0"
- Edit `trading_config.yaml`
- Check `scanner.strategy_weights` section
- Ensure weights add up to 1.0 (e.g., 0.35 + 0.30 + 0.20 + 0.15 = 1.0)

### "Position size too high"
- Edit `trading_config.yaml`
- Set `position_size_pct` between 0.01 and 0.25
- Start conservative (0.05 = 5%)

---

## Next Steps

1. ✅ Setup complete? → Proceed to Phase 1: Position Sizing
2. Need help? → Check error messages in logs
3. Want to customize? → Edit `trading_config.yaml`

**Ready to build!** 🚀
