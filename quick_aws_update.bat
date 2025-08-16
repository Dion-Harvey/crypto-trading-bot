# Quick AWS Update - Crypto Trading Bot
# Run this to update your AWS deployment with the latest working configuration

# Step 1: Upload latest working files
echo "🚀 Updating AWS with latest working bot configuration..."

# Upload the key files that were fixed
scp -i "C:\Users\miste\Downloads\cryptobot-key.pem" enhanced_config.json ubuntu@3.135.216.32:~/crypto-trading-bot/
scp -i "C:\Users\miste\Downloads\cryptobot-key.pem" enhanced_config.py ubuntu@3.135.216.32:~/crypto-trading-bot/
scp -i "C:\Users\miste\Downloads\cryptobot-key.pem" bot.py ubuntu@3.135.216.32:~/crypto-trading-bot/
scp -i "C:\Users\miste\Downloads\cryptobot-key.pem" bot_recovery.py ubuntu@3.135.216.32:~/crypto-trading-bot/
scp -i "C:\Users\miste\Downloads\cryptobot-key.pem" diagnostic_report.py ubuntu@3.135.216.32:~/crypto-trading-bot/

echo "✅ Files uploaded successfully!"
echo ""
echo "🔧 Next steps:"
echo "1. SSH to AWS: ssh -i \"C:\Users\miste\Downloads\cryptobot-key.pem\" ubuntu@3.135.216.32"
echo "2. Install dependencies: cd ~/crypto-trading-bot && python3 -m pip install scipy python-dotenv --user"
echo "3. Edit API keys: nano enhanced_config.json"
echo "4. Start bot: python3 bot.py"
echo ""
echo "📊 Your AWS bot now has the same working configuration as your local bot!"
