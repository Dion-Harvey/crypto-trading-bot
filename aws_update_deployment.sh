#!/bin/bash

# AWS Update Script - Crypto Trading Bot
# Updates AWS deployment with latest working configuration
# Date: July 12, 2025

echo "🚀 CRYPTO TRADING BOT - AWS UPDATE DEPLOYMENT"
echo "=============================================="
echo "📅 Update Date: $(date)"
echo "🎯 Updating with latest working configuration..."
echo ""

# AWS Instance details
AWS_USER="ubuntu"
AWS_IP="3.135.216.32"
AWS_KEY_PATH="~/crypto-bot-key.pem"
REMOTE_DIR="~/crypto-trading-bot"
LOCAL_DIR="."

echo "🔧 STEP 1: Backing up current AWS configuration..."
ssh -i $AWS_KEY_PATH $AWS_USER@$AWS_IP "cd $REMOTE_DIR && cp enhanced_config.json enhanced_config.json.backup_$(date +%Y%m%d_%H%M%S)"

echo "✅ STEP 2: Uploading latest working configuration..."
# Upload the working enhanced_config.json
scp -i $AWS_KEY_PATH enhanced_config.json $AWS_USER@$AWS_IP:$REMOTE_DIR/

echo "✅ STEP 3: Uploading enhanced_config.py with API support..."
# Upload the enhanced config handler with get_api_config method
scp -i $AWS_KEY_PATH enhanced_config.py $AWS_USER@$AWS_IP:$REMOTE_DIR/

echo "✅ STEP 4: Uploading recovery tools..."
# Upload the recovery and diagnostic tools
scp -i $AWS_KEY_PATH bot_recovery.py $AWS_USER@$AWS_IP:$REMOTE_DIR/
scp -i $AWS_KEY_PATH diagnostic_report.py $AWS_USER@$AWS_IP:$REMOTE_DIR/

echo "✅ STEP 5: Uploading startup script..."
# Upload the working startup script
scp -i $AWS_KEY_PATH start_bot.bat $AWS_USER@$AWS_IP:$REMOTE_DIR/start_bot.sh

echo "🔧 STEP 6: Installing missing dependencies on AWS..."
ssh -i $AWS_KEY_PATH $AWS_USER@$AWS_IP "cd $REMOTE_DIR && python3 -m pip install scipy python-dotenv --user"

echo "🔧 STEP 7: Setting up virtual environment on AWS..."
ssh -i $AWS_KEY_PATH $AWS_USER@$AWS_IP "
cd $REMOTE_DIR
# Create virtual environment if it doesn't exist
if [ ! -d '.venv' ]; then
    python3 -m venv .venv
fi
# Activate and install dependencies
source .venv/bin/activate
pip install --upgrade pip
pip install ccxt pandas numpy scipy python-dotenv
"

echo "⚙️ STEP 8: Configuring API keys on AWS..."
echo "⚠️  IMPORTANT: You need to manually update API keys on AWS!"
echo "📝 Run this command to edit the config on AWS:"
echo "   ssh -i $AWS_KEY_PATH $AWS_USER@$AWS_IP"
echo "   cd $REMOTE_DIR && nano enhanced_config.json"
echo "   Update the api_keys section with your credentials"
echo ""

echo "🧪 STEP 9: Testing bot functionality on AWS..."
ssh -i $AWS_KEY_PATH $AWS_USER@$AWS_IP "
cd $REMOTE_DIR
source .venv/bin/activate
python3 -c 'print(\"Testing import...\"); import enhanced_config; config = enhanced_config.BotConfig(); print(\"Config validation:\", config.validate_config())'
"

echo "🎯 STEP 10: Creating AWS startup script..."
ssh -i $AWS_KEY_PATH $AWS_USER@$AWS_IP "
cd $REMOTE_DIR
cat > start_bot_aws.sh << 'EOF'
#!/bin/bash
echo '🚀 Starting Crypto Trading Bot on AWS...'
cd ~/crypto-trading-bot
source .venv/bin/activate
echo '✅ Virtual environment activated'
python3 bot.py
EOF
chmod +x start_bot_aws.sh
"

echo ""
echo "✅ AWS UPDATE COMPLETED!"
echo "========================"
echo "🎯 Your AWS deployment has been updated with:"
echo "   ✅ Latest working enhanced_config.json"
echo "   ✅ Enhanced config handler with API support"
echo "   ✅ Recovery and diagnostic tools"
echo "   ✅ Virtual environment with all dependencies"
echo "   ✅ AWS startup script (start_bot_aws.sh)"
echo ""
echo "🔑 NEXT STEPS:"
echo "1. SSH to AWS: ssh -i $AWS_KEY_PATH $AWS_USER@$AWS_IP"
echo "2. Edit config: cd $REMOTE_DIR && nano enhanced_config.json"
echo "3. Add your API keys to the api_keys section"
echo "4. Start bot: ./start_bot_aws.sh"
echo ""
echo "📊 To monitor the bot:"
echo "   - Use screen/tmux for persistent sessions"
echo "   - Monitor logs: tail -f bot_log.txt"
echo "   - Press Ctrl+C to stop safely"
echo ""
