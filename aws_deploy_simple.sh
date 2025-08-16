#!/bin/bash
# 🚀 SIMPLE AWS DEPLOYMENT - PHASE 3 WEEK 2
# No complex loops or timeouts - just direct commands

echo "🚀 Uploading Pattern Recognition AI to AWS..."

# Upload key files
scp pattern_recognition_ai.py ubuntu@3.135.216.32:~/crypto-trading-bot/ &
scp bot.py ubuntu@3.135.216.32:~/crypto-trading-bot/ &
scp requirements.txt ubuntu@3.135.216.32:~/crypto-trading-bot/ &

wait

echo "📦 Installing dependencies and restarting bot..."

# One SSH session with all commands
ssh ubuntu@3.135.216.32 << 'EOF'
cd ~/crypto-trading-bot
pip3 install opencv-python-headless scikit-learn scipy tensorflow-cpu --quiet
pkill -f 'python.*bot.py' || true
sleep 2
nohup python3 bot.py > bot_output.log 2>&1 &
sleep 1
ps aux | grep 'python.*bot.py' | grep -v grep
echo "✅ Pattern Recognition AI deployment complete!"
EOF

echo "🎯 Deployment finished! Bot running with dual AI system."
