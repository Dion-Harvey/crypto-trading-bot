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

if [ ! -f .env ]; then
    echo "🔧 Creating .env placeholder (edit with real keys)..."
    cat > .env <<'ENVEOF'
BINANCE_API_KEY=REPLACE_ME
BINANCE_API_SECRET=REPLACE_ME
GEMINI_API_KEY=REPLACE_ME
ENVEOF
    chmod 600 .env
    echo "✅ .env created (place real keys, never commit)"
else
    echo "ℹ️ .env already exists - leaving in place"
fi

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
