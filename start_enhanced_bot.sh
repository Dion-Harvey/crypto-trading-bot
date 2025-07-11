#!/bin/bash
# Enhanced Trading Bot Startup Script
# This script activates the virtual environment and starts the bot

echo "🚀 Starting Enhanced Crypto Trading Bot..."
echo "📍 Location: $(pwd)"
echo "🕐 Time: $(date)"

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source crypto_bot_env/bin/activate

# Check if enhanced configuration exists
if [ ! -f "enhanced_config.json" ]; then
    echo "❌ Error: enhanced_config.json not found!"
    exit 1
fi

# Verify dependencies
echo "🔍 Verifying dependencies..."
python3 -c "import ccxt, pandas, numpy; print('✅ All dependencies available')"

# Test enhanced detection system
echo "🧪 Testing enhanced detection system..."
python3 -c "from price_jump_detector import get_price_jump_detector; print('✅ Enhanced detection system ready')"

# Start the bot
echo "🚀 Starting enhanced trading bot..."
echo "📊 Enhanced features:"
echo "   - Multi-timeframe price jump detection"
echo "   - Sustained trend tracking"
echo "   - Momentum analysis"
echo "   - Smart cooldown override"
echo "   - MA7/MA25 crossover priority"
echo ""
echo "💡 To stop the bot, press Ctrl+C"
echo ""

# Run the bot
python3 bot.py
