# 🚀 MANUAL AWS DEPLOYMENT GUIDE - SWITCHING OPTIMIZATION

## Step-by-Step Upload Process

### 1. UPLOAD CORE FILES (Run these commands one by one)

```bash
# Navigate to your project directory
cd "C:\Users\miste\Documents\crypto-trading-bot\crypto-trading-bot"

# Upload the main bot file with switching optimizations
scp -i "C:\Users\miste\Documents\cryptobot-key.pem" -o StrictHostKeyChecking=no bot.py ubuntu@3.135.216.32:/home/ubuntu/crypto-trading-bot/bot.py

# Upload the enhanced multi-crypto monitor
scp -i "C:\Users\miste\Documents\cryptobot-key.pem" -o StrictHostKeyChecking=no multi_crypto_monitor.py ubuntu@3.135.216.32:/home/ubuntu/crypto-trading-bot/multi_crypto_monitor.py

# Upload the configuration with supported pairs
scp -i "C:\Users\miste\Documents\cryptobot-key.pem" -o StrictHostKeyChecking=no enhanced_config.json ubuntu@3.135.216.32:/home/ubuntu/crypto-trading-bot/enhanced_config.json

# Upload the optimization documentation
scp -i "C:\Users\miste\Documents\cryptobot-key.pem" -o StrictHostKeyChecking=no SWITCHING_OPTIMIZATION_COMPLETE.md ubuntu@3.135.216.32:/home/ubuntu/crypto-trading-bot/SWITCHING_OPTIMIZATION_COMPLETE.md
```

### 2. RESTART THE BOT ON AWS

```bash
# Connect to your EC2 instance
ssh -i "C:\Users\miste\Documents\cryptobot-key.pem" ubuntu@3.135.216.32

# Once connected, run these commands:
cd /home/ubuntu/crypto-trading-bot

# Stop any running bot
pkill -f "python.*bot.py" || true

# Start the optimized bot
nohup python3 bot.py > bot_output.log 2>&1 &

# Check if it's running
ps aux | grep bot.py

# View the logs
tail -f bot_output.log
```

### 3. QUICK VERIFICATION COMMANDS

```bash
# Check bot status
ssh -i "C:\Users\miste\Documents\cryptobot-key.pem" ubuntu@3.135.216.32 "cd /home/ubuntu/crypto-trading-bot && ps aux | grep bot.py"

# View recent logs
ssh -i "C:\Users\miste\Documents\cryptobot-key.pem" ubuntu@3.135.216.32 "cd /home/ubuntu/crypto-trading-bot && tail -20 bot_output.log"
```

---

## 🎯 WHAT'S BEEN OPTIMIZED

The files you're uploading contain these critical improvements for catching HBAR +5.83% and XLM +6.40% moves:

### ✅ Bot.py Changes:
- **Aggressive switching thresholds**: 0.65→0.45 (-31%), 0.85→0.50 (-41%)
- **Direct percentage detection**: 5%+ moves trigger immediate switching
- **Emergency override**: Lowered from 90% to 80% score threshold

### ✅ Multi_crypto_monitor.py Changes:
- **Ultra-aggressive spike detection**: 5%+ moves forced to 85%+ scores
- **Ultra-low thresholds**: 1% minimum detection (was 5%)
- **Forced score enhancement**: Guarantees high scores for momentum moves

### ✅ Enhanced_config.json:
- **Confirmed pairs**: XLM/USDT and HBAR/USDT in supported list
- **Current trading**: SUI/USDT (will switch when opportunities arise)

---

## 🚨 MONITORING AFTER DEPLOYMENT

Once uploaded, monitor for these log messages indicating the optimizations are working:

```
🚨 STRONG MOVE: HBAR/USDT +5.83% - FORCING 85%+ score
🚀 EMERGENCY SPIKE DETECTED: XLM/USDT score 0.850+
🔄 CRYPTO SWITCH: Switching to higher-performing asset
```

The bot will now immediately detect and switch to any 5%+ moves in supported pairs!
