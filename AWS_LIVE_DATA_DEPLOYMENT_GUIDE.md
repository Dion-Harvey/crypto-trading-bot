🎯 CRYPTO TRADING BOT - AWS LIVE DATA DEPLOYMENT CHECKLIST
===========================================================
Updated: July 17, 2025

📋 CRITICAL FILES FOR LIVE DATA ACCESS
=====================================

✅ MUST-HAVE CORE FILES (15 files):
----------------------------------
1. bot.py                           # Main trading application
2. config.py                        # API keys and basic config
3. enhanced_config.json              # Advanced trading parameters
4. requirements.txt                  # Python dependencies (updated)

5. price_jump_detector.py            # Real-time price movement detection
6. multi_timeframe_ma.py             # Multi-timeframe MA analysis
7. enhanced_multi_timeframe_ma.py    # Enhanced timeframe analysis
8. priority_functions_5m1m.py       # Priority signal management

9. strategies/ma_crossover.py        # Core MA crossover strategy
10. strategies/multi_strategy_optimized.py  # Multi-strategy optimization
11. strategies/hybrid_strategy.py    # Hybrid trading approach

12. enhanced_multi_strategy.py       # Enhanced strategy coordination
13. institutional_strategies.py     # Institutional-grade algorithms
14. log_utils.py                    # Logging and performance tracking
15. performance_tracker.py          # Trade performance analysis
16. enhanced_config.py              # Configuration management
17. state_manager.py                # Trading state persistence
18. success_rate_enhancer.py        # Success rate optimization

📊 OPTIONAL STATE FILES (preserve trading history):
--------------------------------------------------
• bot_state.json                   # Current bot state
• trade_log.csv                    # Trading history
• performance_report.csv           # Performance analytics

🚀 DEPLOYMENT METHODS
====================

METHOD 1: Automated Script (Recommended)
----------------------------------------
Windows PowerShell:
   > .\aws_deploy_live_data.ps1

Linux/Mac Bash:
   $ chmod +x aws_deploy_live_data.sh
   $ ./aws_deploy_live_data.sh

METHOD 2: Manual SCP Upload
---------------------------
# Update these values first:
AWS_INSTANCE_IP="your-ec2-ip-here"
AWS_KEY_PATH="your-key.pem"  
AWS_USER="ec2-user"

# Core files
scp -i your-key.pem bot.py config.py enhanced_config.json requirements.txt ec2-user@your-ip:/home/ec2-user/crypto-trading-bot/

# Live data modules
scp -i your-key.pem price_jump_detector.py multi_timeframe_ma.py enhanced_multi_timeframe_ma.py priority_functions_5m1m.py ec2-user@your-ip:/home/ec2-user/crypto-trading-bot/

# Strategies
scp -i your-key.pem strategies/*.py ec2-user@your-ip:/home/ec2-user/crypto-trading-bot/strategies/

# Support modules
scp -i your-key.pem enhanced_multi_strategy.py institutional_strategies.py log_utils.py performance_tracker.py enhanced_config.py state_manager.py success_rate_enhancer.py ec2-user@your-ip:/home/ec2-user/crypto-trading-bot/

🔧 AWS SETUP COMMANDS
=====================

1. CREATE DIRECTORY STRUCTURE:
   ssh -i your-key.pem ec2-user@your-ip "mkdir -p /home/ec2-user/crypto-trading-bot/strategies"

2. SETUP PYTHON ENVIRONMENT:
   ssh -i your-key.pem ec2-user@your-ip
   cd crypto-trading-bot
   python3 -m venv crypto_bot_env
   source crypto_bot_env/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt

3. SET PERMISSIONS:
   chmod +x bot.py
   chmod 600 config.py  # Secure API keys

4. TEST LIVE DATA CONNECTION:
   python3 -c "from bot import test_connection; test_connection()"

🚀 START TRADING BOT
===================

START BOT:
   cd crypto-trading-bot
   source crypto_bot_env/bin/activate
   python3 bot.py

RUN IN BACKGROUND:
   nohup python3 bot.py > bot_output.log 2>&1 &

MONITOR LOGS:
   tail -f bot_output.log
   tail -f trade_log.csv
   tail -f bot_log.txt

STOP BOT:
   pkill -f "python3 bot.py"

📊 LIVE DATA VERIFICATION
=========================

After deployment, verify these capabilities:

✅ Real-time price feeds from Binance US
✅ 1-minute and 1-hour OHLCV data
✅ Order book access (bid/ask spreads)
✅ Multi-timeframe MA calculations
✅ Price jump detection (spike/short/medium/long)
✅ Volume analysis and confirmation
✅ RSI, MACD, Bollinger Bands
✅ Progressive profit taking
✅ Risk management and stop losses

🔍 TROUBLESHOOTING
==================

CONNECTION ISSUES:
• Check API keys in config.py
• Verify Binance US API permissions
• Ensure stable internet connection
• Check firewall/security group settings

DEPENDENCY ISSUES:
• Update pip: pip install --upgrade pip
• Install scipy: pip install scipy numpy
• Clear cache: pip cache purge

PERMISSION ISSUES:
• Set file permissions: chmod +x bot.py
• Check user ownership: chown ec2-user:ec2-user *

MEMORY ISSUES:
• Monitor with: htop or top
• Check swap: free -h
• Restart if needed: sudo reboot

⚠️  SECURITY CHECKLIST
======================

✅ API keys secured in config.py (chmod 600)
✅ Consider environment variables for production
✅ Monitor AWS costs and usage
✅ Set up CloudWatch alarms
✅ Regular backups of trade_log.csv
✅ Monitor bot logs for errors
✅ Test with small amounts first

📈 EXPECTED PERFORMANCE
======================

With live data access, the bot should achieve:
• 30-second analysis loops
• MA7/MA25 crossover detection within 1-2 minutes
• Price jump detection for 0.5%+ moves
• Multi-layer trading (Layer 1: MA crossover, Layer 2: Scalping, Layer 3: Range-bound)
• 2.5% daily profit target
• Advanced risk management and stop losses

🎉 DEPLOYMENT COMPLETE!
=======================

Your AWS bot now has full live data access for optimal trading performance.
Monitor the logs and adjust parameters as needed.

For support, check the bot logs and trading performance reports.
