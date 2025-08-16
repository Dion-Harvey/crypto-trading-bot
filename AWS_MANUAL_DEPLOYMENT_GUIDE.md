# 🚀 MANUAL AWS DEPLOYMENT GUIDE - PHASE 3 WEEK 2
# ===================================================
# Step-by-step manual deployment for Pattern Recognition AI
# Target: ubuntu@3.135.216.32 (AWS EC2)

# STEP 1: Upload Pattern Recognition AI file
scp pattern_recognition_ai.py ubuntu@3.135.216.32:~/crypto-trading-bot/

# STEP 2: Upload updated bot.py (with Pattern AI integration)
scp bot.py ubuntu@3.135.216.32:~/crypto-trading-bot/

# STEP 3: Upload updated requirements.txt (with new dependencies)
scp requirements.txt ubuntu@3.135.216.32:~/crypto-trading-bot/

# STEP 4: Connect to AWS and install dependencies
ssh ubuntu@3.135.216.32

# STEP 5: Navigate to project directory
cd ~/crypto-trading-bot

# STEP 6: Install new AI dependencies
pip3 install opencv-python-headless>=4.8.0
pip3 install scikit-learn>=1.3.0
pip3 install scipy>=1.10.0
pip3 install tensorflow-cpu>=2.15.0

# STEP 7: Stop existing bot
pkill -f 'python.*bot.py' || true

# STEP 8: Start bot with new Pattern Recognition AI
nohup python3 bot.py > bot_output.log 2>&1 &

# STEP 9: Verify bot is running
ps aux | grep 'python.*bot.py' | grep -v grep

# STEP 10: Check logs
tail -f bot_output.log

# ✅ DEPLOYMENT COMPLETE!
# 🧠 LSTM AI (Week 1): Active
# 🎯 Pattern Recognition AI (Week 2): Active
