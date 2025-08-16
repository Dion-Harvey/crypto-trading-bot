#!/bin/bash

# AWS Enhanced Dip Detection Deployment Script
# Updates AWS with the latest enhanced dip detection system
# Date: July 23, 2025

echo "🚀 DEPLOYING ENHANCED DIP DETECTION TO AWS"
echo "============================================="
echo "📅 Deployment Date: $(date)"
echo "🎯 Fixing peak-buying behavior with enhanced dip detection..."
echo ""

# AWS Instance details
AWS_USER="ubuntu"
AWS_IP="3.135.216.32"
AWS_KEY_PATH="~/crypto-bot-key.pem"
REMOTE_DIR="~/crypto-trading-bot"
LOCAL_DIR="."

echo "🔧 STEP 1: Backing up current AWS bot.py..."
ssh -i $AWS_KEY_PATH $AWS_USER@$AWS_IP "cd $REMOTE_DIR && cp bot.py bot.py.backup_$(date +%Y%m%d_%H%M%S)"

echo "🔧 STEP 2: Backing up current AWS enhanced_config.json..."
ssh -i $AWS_KEY_PATH $AWS_USER@$AWS_IP "cd $REMOTE_DIR && cp enhanced_config.json enhanced_config.json.backup_$(date +%Y%m%d_%H%M%S)"

echo "✅ STEP 3: Uploading enhanced bot.py with dip detection..."
# Upload the updated bot.py with enhanced dip detection
scp -i $AWS_KEY_PATH bot.py $AWS_USER@$AWS_IP:$REMOTE_DIR/

echo "✅ STEP 4: Uploading optimized enhanced_config.json..."
# Upload the optimized configuration with dip-specific parameters
scp -i $AWS_KEY_PATH enhanced_config.json $AWS_USER@$AWS_IP:$REMOTE_DIR/

echo "✅ STEP 5: Uploading enhanced_config.py handler..."
# Ensure the config handler supports dip detection parameters
scp -i $AWS_KEY_PATH enhanced_config.py $AWS_USER@$AWS_IP:$REMOTE_DIR/

echo "✅ STEP 6: Uploading test scripts for verification..."
# Upload our dip detection test scripts
scp -i $AWS_KEY_PATH dip_test.py $AWS_USER@$AWS_IP:$REMOTE_DIR/
scp -i $AWS_KEY_PATH bot_signal_test.py $AWS_USER@$AWS_IP:$REMOTE_DIR/

echo "🔧 STEP 7: Verifying enhanced dip detection on AWS..."
ssh -i $AWS_KEY_PATH $AWS_USER@$AWS_IP "
cd $REMOTE_DIR
echo '📊 Testing enhanced dip detection on AWS...'
python3 dip_test.py | head -20
echo ''
echo '🎯 Testing bot signal function on AWS...'
python3 bot_signal_test.py | head -15
"

echo "🔧 STEP 8: Restarting bot with enhanced dip detection..."
ssh -i $AWS_KEY_PATH $AWS_USER@$AWS_IP "
cd $REMOTE_DIR
echo '🛑 Stopping current bot...'
sudo systemctl stop crypto-trading-bot.service 2>/dev/null || pkill -f bot.py
sleep 3
echo '🚀 Starting bot with enhanced dip detection...'
sudo systemctl start crypto-trading-bot.service 2>/dev/null || nohup python3 bot.py > bot.log 2>&1 &
sleep 5
echo '📊 Bot status:'
sudo systemctl status crypto-trading-bot.service --no-pager -l | head -10 2>/dev/null || ps aux | grep bot.py | grep -v grep
"

echo ""
echo "🎉 ENHANCED DIP DETECTION DEPLOYMENT COMPLETE!"
echo "=============================================="
echo "✅ Deployed Changes:"
echo "   • Enhanced detect_ma_crossover_signals() function"
echo "   • Multi-tier dip detection (enhanced/RSI/moderate)"
echo "   • Dynamic confidence reduction for dip signals"
echo "   • Peak avoidance logic to prevent peak-buying"
echo "   • Optimized configuration with dip-specific parameters"
echo ""
echo "🎯 Expected Behavior:"
echo "   • Bot will now BUY DIPS instead of peaks"
echo "   • Enhanced dip detection with 0.45-0.65 confidence"
echo "   • Moderate dip opportunities at 0.45 confidence"
echo "   • RSI oversold confirmation for stronger signals"
echo ""
echo "📊 Monitor logs for: 'MODERATE DIP DETECTED!' and 'Enhanced dip buying'"
echo "📱 AWS Bot Status: systemctl status crypto-trading-bot.service"
