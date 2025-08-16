#!/bin/bash
# AWS API Key Fix Script (Bash version)
# This script connects to AWS and updates the config.py with working API keys

echo "🔧 Fixing AWS API Key Issues..."

# AWS server details
AWS_USER="ubuntu"
AWS_HOST="3.135.216.32"
AWS_PATH="~/crypto-trading-bot/"

echo "📤 Connecting to AWS to fix API keys..."

# Method 1: Try with default SSH key
if [ -f ~/.ssh/id_rsa ]; then
    echo "🔑 Using default SSH key..."
    ssh -i ~/.ssh/id_rsa $AWS_USER@$AWS_HOST << 'EOF'
        cd ~/crypto-trading-bot/
        echo "📝 Backing up current config..."
        cp config.py config.py.backup.$(date +%Y%m%d_%H%M%S)
        
        echo "🔧 Updating config.py with working API keys..."
        cat > config.py << 'CONFIG_EOF'
# config.py
# Place your Binance API credentials here. Do NOT commit this file to version control!

BINANCE_API_KEY = "bN4mjzb1pIfmRZCit0zjqxACIv1JszpbPDi3Zlhbh1961qsFgvwio6UWzIyUwQND"
BINANCE_API_SECRET = "Rq5p1qTSwq4qmb8xgb7kdKHZGlPVvIaiakF5jiu43dknp0nGg17jDLtuIwZ1cWza"

CONFIG_EOF
        
        echo "✅ Config updated! Testing connection..."
        python3 connection_test.py
        
        echo "🔄 Stopping any running bot processes..."
        pkill -f "python.*bot.py" || true
        
        echo "✅ AWS API key fix complete!"
EOF

else
    echo "❌ No SSH key found. Please use manual method below."
    echo ""
    echo "🔧 MANUAL FIX INSTRUCTIONS:"
    echo "=========================="
    echo "1. SSH into your AWS instance:"
    echo "   ssh -i your-key.pem ubuntu@3.135.216.32"
    echo ""
    echo "2. Navigate to bot directory:"
    echo "   cd ~/crypto-trading-bot/"
    echo ""
    echo "3. Backup current config:"
    echo "   cp config.py config.py.backup"
    echo ""
    echo "4. Edit config.py:"
    echo "   nano config.py"
    echo ""
    echo "5. Replace with working API keys:"
    echo "   BINANCE_API_KEY = \"bN4mjzb1pIfmRZCit0zjqxACIv1JszpbPDi3Zlhbh1961qsFgvwio6UWzIyUwQND\""
    echo "   BINANCE_API_SECRET = \"Rq5p1qTSwq4qmb8xgb7kdKHZGlPVvIaiakF5jiu43dknp0nGg17jDLtuIwZ1cWza\""
    echo ""
    echo "6. Save and exit (Ctrl+X, Y, Enter)"
    echo ""
    echo "7. Test connection:"
    echo "   python3 connection_test.py"
    echo ""
    echo "8. Stop old bot processes:"
    echo "   pkill -f 'python.*bot.py'"
fi
