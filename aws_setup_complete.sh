#!/bin/bash
# Complete AWS Environment Setup Script
# Run this on your AWS instance to fix all issues

echo "🚀 AWS Trading Bot Environment Setup"
echo "===================================="

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and pip if not already installed
echo "🐍 Installing Python and pip..."
sudo apt install -y python3 python3-pip python3-venv

# Install required Python packages
echo "📚 Installing Python dependencies..."
pip3 install --user ccxt>=3.0.0
pip3 install --user pandas>=1.5.0
pip3 install --user numpy>=1.24.0
pip3 install --user scipy>=1.10.0
pip3 install --user scikit-learn>=1.3.0
pip3 install --user python-dotenv>=1.0.0
pip3 install --user requests>=2.31.0

# Alternative: Install from requirements.txt if available
if [ -f "requirements.txt" ]; then
    echo "📋 Installing from requirements.txt..."
    pip3 install --user -r requirements.txt
fi

# Update config.py with working API keys
echo "🔧 Updating config.py with working API keys..."
cat > config.py << 'EOF'
# config.py
# Place your Binance API credentials here. Do NOT commit this file to version control!

BINANCE_API_KEY = "bN4mjzb1pIfmRZCit0zjqxACIv1JszpbPDi3Zlhbh1961qsFgvwio6UWzIyUwQND"
BINANCE_API_SECRET = "Rq5p1qTSwq4qmb8xgb7kdKHZGlPVvIaiakF5jiu43dknp0nGg17jDLtuIwZ1cWza"

EOF

echo "✅ Config.py updated with working API keys"

# Test the connection
echo "🧪 Testing API connection..."
python3 connection_test.py

# Stop any running bot processes
echo "🔄 Stopping any old bot processes..."
pkill -f "python.*bot.py" || true

echo ""
echo "✅ AWS Environment Setup Complete!"
echo "🎯 Your bot should now work properly on AWS"
echo ""
echo "📝 Next steps:"
echo "1. The API connection test should have passed"
echo "2. You can now run: python3 bot.py"
echo "3. Or run in background: nohup python3 bot.py > bot.log 2>&1 &"
echo ""
