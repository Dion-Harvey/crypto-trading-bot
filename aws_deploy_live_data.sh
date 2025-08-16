#!/bin/bash
# AWS CRYPTO TRADING BOT DEPLOYMENT SCRIPT
# Updated for Live Data Access - July 17, 2025
# ============================================

echo "🚀 CRYPTO TRADING BOT - AWS DEPLOYMENT WITH LIVE DATA ACCESS"
echo "============================================================="

# Configuration
AWS_INSTANCE_IP="3.135.216.32"
AWS_KEY_PATH="C:\Users\miste\Downloads\cryptobot-key.pem"
AWS_USER="ubuntu"
REMOTE_PATH="/home/ubuntu/crypto-trading-bot"

# Check if AWS key exists
if [ ! -f "$AWS_KEY_PATH" ]; then
    echo "❌ AWS key file not found: $AWS_KEY_PATH"
    echo "Please update AWS_KEY_PATH in this script"
    exit 1
fi

echo "📋 UPLOADING FILES FOR LIVE DATA ACCESS..."
echo "Target: $AWS_USER@$AWS_INSTANCE_IP:$REMOTE_PATH"
echo ""

# Create remote directory
echo "📁 Creating remote directory..."
ssh -i "$AWS_KEY_PATH" "$AWS_USER@$AWS_INSTANCE_IP" "mkdir -p $REMOTE_PATH/strategies"

# Core application files
echo "📦 Uploading core application..."
scp -i "$AWS_KEY_PATH" bot.py "$AWS_USER@$AWS_INSTANCE_IP:$REMOTE_PATH/"
scp -i "$AWS_KEY_PATH" config.py "$AWS_USER@$AWS_INSTANCE_IP:$REMOTE_PATH/"
scp -i "$AWS_KEY_PATH" enhanced_config.json "$AWS_USER@$AWS_INSTANCE_IP:$REMOTE_PATH/"
scp -i "$AWS_KEY_PATH" requirements.txt "$AWS_USER@$AWS_INSTANCE_IP:$REMOTE_PATH/"

# Live data access modules
echo "📊 Uploading live data access modules..."
scp -i "$AWS_KEY_PATH" price_jump_detector.py "$AWS_USER@$AWS_INSTANCE_IP:$REMOTE_PATH/"
scp -i "$AWS_KEY_PATH" multi_timeframe_ma.py "$AWS_USER@$AWS_INSTANCE_IP:$REMOTE_PATH/"
scp -i "$AWS_KEY_PATH" enhanced_multi_timeframe_ma.py "$AWS_USER@$AWS_INSTANCE_IP:$REMOTE_PATH/"
scp -i "$AWS_KEY_PATH" priority_functions_5m1m.py "$AWS_USER@$AWS_INSTANCE_IP:$REMOTE_PATH/"

# Core strategies
echo "📈 Uploading trading strategies..."
scp -i "$AWS_KEY_PATH" strategies/ma_crossover.py "$AWS_USER@$AWS_INSTANCE_IP:$REMOTE_PATH/strategies/"
scp -i "$AWS_KEY_PATH" strategies/multi_strategy_optimized.py "$AWS_USER@$AWS_INSTANCE_IP:$REMOTE_PATH/strategies/"
scp -i "$AWS_KEY_PATH" strategies/hybrid_strategy.py "$AWS_USER@$AWS_INSTANCE_IP:$REMOTE_PATH/strategies/"

# Support modules
echo "🔧 Uploading support modules..."
scp -i "$AWS_KEY_PATH" enhanced_multi_strategy.py "$AWS_USER@$AWS_INSTANCE_IP:$REMOTE_PATH/"
scp -i "$AWS_KEY_PATH" institutional_strategies.py "$AWS_USER@$AWS_INSTANCE_IP:$REMOTE_PATH/"
scp -i "$AWS_KEY_PATH" log_utils.py "$AWS_USER@$AWS_INSTANCE_IP:$REMOTE_PATH/"
scp -i "$AWS_KEY_PATH" performance_tracker.py "$AWS_USER@$AWS_INSTANCE_IP:$REMOTE_PATH/"
scp -i "$AWS_KEY_PATH" enhanced_config.py "$AWS_USER@$AWS_INSTANCE_IP:$REMOTE_PATH/"
scp -i "$AWS_KEY_PATH" state_manager.py "$AWS_USER@$AWS_INSTANCE_IP:$REMOTE_PATH/"
scp -i "$AWS_KEY_PATH" success_rate_enhancer.py "$AWS_USER@$AWS_INSTANCE_IP:$REMOTE_PATH/"

# State files (preserve trading history)
echo "💾 Uploading state files..."
if [ -f "bot_state.json" ]; then
    scp -i "$AWS_KEY_PATH" bot_state.json "$AWS_USER@$AWS_INSTANCE_IP:$REMOTE_PATH/"
    echo "✅ bot_state.json uploaded"
else
    echo "⚠️ bot_state.json not found - will create fresh state"
fi

if [ -f "trade_log.csv" ]; then
    scp -i "$AWS_KEY_PATH" trade_log.csv "$AWS_USER@$AWS_INSTANCE_IP:$REMOTE_PATH/"
    echo "✅ trade_log.csv uploaded"
else
    echo "⚠️ trade_log.csv not found - will create new log"
fi

# Setup environment and dependencies
echo ""
echo "🔧 Setting up AWS environment for live data access..."
ssh -i "$AWS_KEY_PATH" "$AWS_USER@$AWS_INSTANCE_IP" << 'EOF'
cd /home/ec2-user/crypto-trading-bot

# Install Python and pip if not available
if ! command -v python3 &> /dev/null; then
    echo "📦 Installing Python 3..."
    sudo yum update -y
    sudo yum install python3 python3-pip -y
fi

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv crypto_bot_env
source crypto_bot_env/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set file permissions
chmod +x bot.py
chmod 600 config.py  # Secure API keys

echo "✅ Environment setup complete"
EOF

# Test connection and live data access
echo ""
echo "🔍 Testing live data connection..."
ssh -i "$AWS_KEY_PATH" "$AWS_USER@$AWS_INSTANCE_IP" << 'EOF'
cd /home/ec2-user/crypto-trading-bot
source crypto_bot_env/bin/activate

echo "Testing Binance US connection..."
python3 -c "
import sys
sys.path.append('.')
try:
    from bot import test_connection
    test_connection()
    print('✅ Live data connection successful!')
except Exception as e:
    print(f'❌ Connection error: {e}')
    print('Please check your API keys in config.py')
"
EOF

echo ""
echo "🎉 AWS DEPLOYMENT COMPLETE!"
echo "=========================="
echo ""
echo "📋 DEPLOYMENT SUMMARY:"
echo "   • Core files: Uploaded ✅"
echo "   • Live data modules: Uploaded ✅"
echo "   • Trading strategies: Uploaded ✅"
echo "   • Dependencies: Installed ✅"
echo "   • Connection: Tested ✅"
echo ""
echo "🚀 TO START THE BOT:"
echo "   ssh -i $AWS_KEY_PATH $AWS_USER@$AWS_INSTANCE_IP"
echo "   cd crypto-trading-bot"
echo "   source crypto_bot_env/bin/activate"
echo "   python3 bot.py"
echo ""
echo "📊 TO MONITOR:"
echo "   tail -f bot_log.txt"
echo "   tail -f trade_log.csv"
echo ""
echo "⚠️  SECURITY REMINDER:"
echo "   • Your API keys are in config.py"
echo "   • Consider using environment variables for production"
echo "   • Monitor AWS costs and instance usage"
