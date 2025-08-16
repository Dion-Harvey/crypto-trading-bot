# 🤖 Crypto Trading Bot - 24/7 AWS EC2 Deployment Guide

## 🚀 Overview
This guide sets up your crypto trading bot for continuous 24/7 operation on AWS EC2 with automatic restart, monitoring, and maintenance.

## 📋 Prerequisites
- AWS EC2 instance (t3.micro or larger recommended)
- Ubuntu 20.04+ LTS
- Bot code uploaded to `/home/ubuntu/crypto-trading-bot/crypto-trading-bot/`
- Python 3.8+ installed
- Binance API credentials configured

## 🔧 Quick Setup

### 1. Upload Files to EC2
```bash
# Upload your bot files to EC2 (from your local machine)
scp -i your-key.pem -r crypto-trading-bot ubuntu@your-ec2-ip:~/
```

### 2. Run Setup Script
```bash
# Connect to EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Navigate to bot directory
cd crypto-trading-bot/crypto-trading-bot

# Make setup script executable and run it
chmod +x setup_ec2_24_7.sh
./setup_ec2_24_7.sh
```

## 🎯 What Gets Configured

### 📦 Systemd Service
- **Service Name**: `crypto-trading-bot`
- **Auto-start**: Enabled on boot
- **Auto-restart**: Yes, with 30-second delay
- **Resource Limits**: 1GB RAM, 80% CPU
- **Security**: Sandboxed environment

### 📊 Monitoring & Logging
- **Daemon Logs**: `daemon.log` (automatic rotation)
- **Trading Logs**: `bot_log.txt`
- **Performance Monitoring**: Every 15 minutes via cron
- **Log Rotation**: Daily, keep 30 days

### 💾 Backup System
- **Automatic Backups**: Daily at 2 AM
- **What's Backed Up**: Config files, state files, logs
- **Retention**: Last 10 backups kept
- **Location**: `backups/` directory

### 🔄 Maintenance Scripts
- **Monitor**: `./monitor_bot.sh` - Check bot status
- **Backup**: `./backup_bot_data.sh` - Manual backup
- **Update**: `./update_bot.sh` - Safe bot updates

## 🎮 Daily Operations

### ✅ Check Bot Status
```bash
# Quick status check
./monitor_bot.sh

# Detailed service status
sudo systemctl status crypto-trading-bot

# Live log monitoring
tail -f daemon.log
```

### 🔄 Control Bot Service
```bash
# Start bot
sudo systemctl start crypto-trading-bot

# Stop bot
sudo systemctl stop crypto-trading-bot

# Restart bot
sudo systemctl restart crypto-trading-bot

# View recent logs
journalctl -u crypto-trading-bot -f
```

### 📊 Performance Monitoring
```bash
# Check recent trading performance
grep "TRADING PERFORMANCE" daemon.log | tail -5

# View recent trades
grep -E "(BUY|SELL) EXECUTED" bot_log.txt | tail -10

# Check portfolio status
grep "Portfolio" daemon.log | tail -3
```

## 🛡️ Security & Safety Features

### 🔒 Automatic Safeguards
- **Rate Limiting**: Max 10 restarts per hour
- **Resource Limits**: Memory and CPU capped
- **Graceful Shutdown**: 60-second timeout for clean stops
- **Error Recovery**: Automatic restart on crashes

### 💰 Risk Management
- **Stop Loss**: 3% (configured in bot)
- **Take Profit**: 8% (configured in bot)
- **Daily Loss Limit**: $5.00
- **Position Sizing**: 35% of portfolio max

### 📝 Audit Trail
- **All Trades Logged**: Complete transaction history
- **System Events**: Start/stop/restart events tracked
- **Error Logging**: Detailed error messages and stack traces
- **Performance Metrics**: Real-time P&L tracking

## 🔧 Troubleshooting

### ❌ Bot Won't Start
```bash
# Check service status
sudo systemctl status crypto-trading-bot

# Check recent logs
journalctl -u crypto-trading-bot --since "10 minutes ago"

# Verify bot files
ls -la /home/ubuntu/crypto-trading-bot/crypto-trading-bot/

# Test bot manually
cd /home/ubuntu/crypto-trading-bot/crypto-trading-bot
source .venv/bin/activate
python bot.py
```

### 🔄 Bot Keeps Restarting
```bash
# Check restart count
grep "Restarting" daemon.log | tail -10

# Look for error patterns
grep -i error daemon.log | tail -5

# Check API connectivity
python -c "import ccxt; print('API test:', ccxt.binanceus().fetch_ticker('BTC/USDC')['last'])"
```

### 📡 Network Issues
```bash
# Test internet connectivity
ping -c 4 google.com

# Test Binance API
curl -s "https://api.binance.us/api/v3/ticker/price?symbol=BTCUSDC"

# Check firewall (if needed)
sudo ufw status
```

## 📈 Performance Optimization

### 🚀 EC2 Instance Recommendations
- **Minimum**: t3.micro (1 vCPU, 1GB RAM) - $8.47/month
- **Recommended**: t3.small (2 vCPU, 2GB RAM) - $16.94/month
- **High-frequency**: t3.medium (2 vCPU, 4GB RAM) - $33.89/month

### ⚡ Bot Configuration
- **Loop Interval**: 30 seconds (fast response)
- **Trade Cooldown**: 5 minutes (prevents overtrading)
- **Multi-timeframe**: 1m + 5m analysis
- **Price Detection**: Spike/trend analysis

### 💾 Storage Requirements
- **Minimum**: 8GB (logs, backups, OS)
- **Recommended**: 20GB (room for growth)
- **Log Retention**: 30 days automatic cleanup

## 🔄 Updates & Maintenance

### 📥 Updating Bot Code
```bash
# Safe update process
./update_bot.sh

# Upload new files (from local machine)
scp -i your-key.pem -r updated-files ubuntu@your-ec2-ip:~/crypto-trading-bot/crypto-trading-bot/

# Restart service
sudo systemctl start crypto-trading-bot
```

### 🧹 Maintenance Tasks
```bash
# Manual backup
./backup_bot_data.sh

# Clean old logs (if needed)
find . -name "*.log.*" -mtime +30 -delete

# Check disk usage
df -h .

# Update system packages (monthly)
sudo apt update && sudo apt upgrade
```

## 🎯 Key Benefits

### ✅ 24/7 Operation
- Automatic startup on EC2 reboot
- Continuous monitoring and restart
- No manual intervention required

### 📊 Professional Monitoring
- Real-time performance tracking
- Automated error detection
- Historical data preservation

### 🛡️ Risk Management
- Built-in stop losses and take profits
- Daily loss limits
- Position size controls

### 💰 Cost Effective
- AWS Free Tier eligible (t3.micro)
- Automatic resource management
- Minimal maintenance overhead

## 🆘 Emergency Procedures

### 🚨 Stop All Trading Immediately
```bash
# Stop the service
sudo systemctl stop crypto-trading-bot

# Verify it's stopped
sudo systemctl status crypto-trading-bot

# Manual market order (if needed)
python -c "
import ccxt
exchange = ccxt.binanceus({'apiKey': 'your_key', 'secret': 'your_secret'})
balance = exchange.fetch_balance()
if balance['BTC']['free'] > 0:
    exchange.create_market_order('BTC/USDC', 'sell', balance['BTC']['free'])
    print('Emergency sell executed')
"
```

### 📞 Contact & Support
- **Logs Location**: `/home/ubuntu/crypto-trading-bot/crypto-trading-bot/`
- **Service Name**: `crypto-trading-bot`
- **Monitor Command**: `./monitor_bot.sh`

---

## 🚀 Your bot is now running 24/7 on AWS EC2!

### Quick Status Check:
```bash
./monitor_bot.sh
```

### Live Trading Monitor:
```bash
tail -f daemon.log | grep -E "(TRADING PERFORMANCE|BUY|SELL)"
```

**💡 Pro Tip**: Bookmark this guide and keep the monitor command handy for quick status checks!
