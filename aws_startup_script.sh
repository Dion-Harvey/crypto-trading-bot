#!/bin/bash
# 🚀 AWS TRADING BOT STARTUP SCRIPT
# =================================
# Run this script to start the enhanced trading bot on AWS

echo "🚀 STARTING ENHANCED CRYPTO TRADING BOT ON AWS..."
echo "=" * 60

# Navigate to bot directory
cd ~/cryptobot/crypto-trading-bot

# Activate virtual environment
echo "🐍 Activating Python virtual environment..."
source venv/bin/activate

# Check system status first
echo "📊 Checking system status..."
python3 check_multipair_status.py

echo ""
echo "🎯 SYSTEM READY!"
echo "Choose an option:"
echo "1. 🚀 Start Multi-Pair Trading System"
echo "2. 🧹 Run Emergency Order Cleanup"
echo "3. 🔍 Check System Status Only"
echo "4. 🛠️  Run Fix Verification"

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "🚀 Starting multi-pair trading system..."
        python3 start_multipair_system.py
        ;;
    2)
        echo "🧹 Running emergency order cleanup..."
        python3 emergency_order_cleanup.py
        ;;
    3)
        echo "📊 System status check complete (already shown above)"
        ;;
    4)
        echo "🛠️ Running fix verification..."
        python3 fix_verification.py
        ;;
    *)
        echo "❌ Invalid choice. Please run script again."
        ;;
esac

echo ""
echo "✅ Script completed!"
